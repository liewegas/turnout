import random
import datetime
import logging

import sentry_sdk
import tweepy
from django.conf import settings
from selenium import webdriver
from selenium.common.exceptions import (
    RemoteDriverServerException,
    SessionNotCreatedException,
)

from common import enums
from common.apm import tracer
from election.models import StateInformation

from .models import Proxy, Site, SiteCheck

MONITORS = {
    "external_tool_polling_place": "Polling Place Lookup",
    "external_tool_ovr": "Online Voter Registration",
    "external_tool_verify_status": "Voter Registration Status Verifier",
    "external_tool_vbm_application": "Absentee Ballot Request",
    "external_tool_absentee_ballot_tracker": "Absentee Ballot Tracker",
}

# as downtime crosses each of these thresholds, we tweet (again)
TWEET_DOWNTIME_THRESHOLDS = [600, 3600, 6 * 3600, 24 * 3600, 7 * 24 * 3600]


logger = logging.getLogger("integration")


class NoProxyError(Exception):
    pass


@tracer.wrap()
def check_group(slug):
    drivers = get_drivers()
    if not drivers:
        logger.error("No active proxies")
        sentry_sdk.capture_exception(NoProxyError("No active proxies"))

    logger.info(f"Checking group {slug}")
    items = [i for i in StateInformation.objects.filter(field_type__slug=slug)]
    random.shuffle(items)
    for item in items:
        # some values are blank
        if not item.text:
            continue

        desc = f"{item.state_id} {MONITORS[slug]}"

        site, _ = Site.objects.get_or_create(description=desc, url=item.text,)

        check_site(drivers, site)


@tracer.wrap()
def check_site(drivers, site):
    # first try primary proxy
    check = check_site_with(drivers[0][0], drivers[0][1], site)
    if not check.state_up:
        # try another proxy
        check2 = check_site_with(drivers[1][0], drivers[1][1], site)

        if check2.state_up:
            # new proxy is fine; ignore the failure
            check.ignore = True
            check.save()

            check3 = check_site_with(drivers[0][0], drivers[0][1], site)
            if check3.state_up:
                # call it intermittent; stick with original proxy
                check = check3
            else:
                # we've burned the proxy
                logger.info(f"We've burned proxy {drivers[0][1]}")
                drivers[0][1].failure_count += 1
                drivers[0][1].state = enums.ProxyState.BURNED
                drivers[0][1].save()

                check = check2

    if site.state_up != check.state_up:
        site.state_up = check.state_up
        site.state_changed_at = check.created_at
        if check.state_up:
            site.last_went_up_at = check.created_at
        else:
            site.last_went_down_at = check.created_at

    site.calc_uptimes()
    site.save()


@tracer.wrap()
def check_site_with(driver, proxy, site):
    logger.debug(f"Checking {site.url} with {proxy}")
    error = None
    before = datetime.datetime.utcnow()
    try:
        driver.get(site.url)
        up = True
    except SessionNotCreatedException as e:
        raise e
    except RemoteDriverServerException as e:
        raise e
    except Exception as e:
        if "establishing a connection" in str(e):
            raise e
        if "marionette" in str(e):
            raise e
        up = False
        error = str(e)
    after = datetime.datetime.utcnow()
    dur = after - before

    # the trick is determining if this loaded the real page or some sort of error/404 page.
    for item in ["404", "not found"]:
        if item in driver.title.lower():
            up = False
            error = f"'{item}' in page title"

    REQUIRED_STRINGS = [
        "vote",
        "Vote",
        "Poll",
        "poll",
        "Absentee",
        "Please enable JavaScript to view the page content.",  # for CT
        "application/pdf",  # for WY
    ]
    have_any = False
    for item in REQUIRED_STRINGS:
        if item in driver.page_source:
            have_any = True
    if not have_any:
        up = False
        error = f"Cannot find any of {REQUIRED_STRINGS} not in page content"
        logger.info(driver.page_source)

    check = SiteCheck.objects.create(
        site=site,
        state_up=up,
        load_time=dur.total_seconds(),
        error=error,
        proxy=proxy,
        ignore=False,
    )

    logger.info(
        f"up={up}: {site.description} {site.url} ({error}) duration {dur} proxy {proxy}"
    )
    return check


def get_drivers():
    drivers = []

    for proxy in Proxy.objects.filter(state=enums.ProxyStatus.UP).order_by(
        "failure_count", "created_at"
    )[:2]:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f"--proxy-server=socks5://{proxy.proxy}")
        drivers.append(
            (
                webdriver.Remote(
                    command_executor="http://selenium:4444/wd/hub",
                    desired_capabilities=webdriver.DesiredCapabilities.CHROME,
                    options=chrome_options,
                ),
                proxy,
            )
        )

    return drivers


@tracer.wrap()
def check_all():
    for slug in MONITORS.keys():
        check_group(slug)


def tweet(message):
    auth = tweepy.OAuthHandler(
        settings.UPTIME_TWITTER_CONSUMER_KEY, settings.UPTIME_TWITTER_CONSUMER_SECRET
    )
    auth.set_access_token(
        settings.UPTIME_TWITTER_ACCESS_TOKEN,
        settings.UPTIME_TWITTER_ACCESS_TOKEN_SECRET,
    )

    # Create API object
    api = tweepy.API(auth)

    # Create a tweet
    logger.info(f"Tweet: {message}")
    api.update_status(message)


def to_pretty_timedelta(n):
    if n < datetime.timedelta(seconds=120):
        return str(int(n.total_seconds())) + "s"
    if n < datetime.timedelta(minutes=120):
        return str(int(n.total_seconds() // 60)) + "m"
    if n < datetime.timedelta(hours=48):
        return str(int(n.total_seconds() // 3600)) + "h"
    if n < datetime.timedelta(days=14):
        return str(int(n.total_seconds() // (24 * 3600))) + "d"
    if n < datetime.timedelta(days=7 * 12):
        return str(int(n.total_seconds() // (24 * 3600 * 7))) + "w"
    if n < datetime.timedelta(days=365 * 2):
        return str(int(n.total_seconds() // (24 * 3600 * 30))) + "M"
    return str(int(n.total_seconds() // (24 * 3600 * 365))) + "y"


@tracer.wrap()
def tweet_site_status(site):
    message = None
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

    if site.state_up:
        if (
            site.last_tweet_at
            and site.last_went_down_at
            and site.last_went_up_at
            and site.last_tweet_at > site.last_went_down_at
            and site.last_tweet_at < site.last_went_up_at
        ):
            message = f"{site.description} is now back up"
    elif site.state_changed_at:
        # complain about being down after crossing several thresholds
        for seconds in TWEET_DOWNTIME_THRESHOLDS:
            cutoff = site.state_changed_at + datetime.timedelta(seconds=seconds)
            if now > cutoff and (not site.last_tweet_at or site.last_tweet_at < cutoff):
                actual_delta = now - site.state_changed_at
                logger.info(
                    f"cutoff {cutoff} {seconds} change at {site.state_changed_at} tweet_at {site.last_tweet_at}"
                )
                message = f"{site.description} has been down for {to_pretty_timedelta(actual_delta)}"
                break

    if message:
        uptimes = []
        for period, v in {
            "day": (24 * 3600, site.uptime_day),
            "week": (7 * 24 * 3600, site.uptime_week),
            "month": (30 * 24 * 3600, site.uptime_month),
            "quarter": (91 * 24 * 3600, site.uptime_quarter),
        }.items():
            seconds, uptime = v
            if uptime and uptime < 1.0:
                down_seconds = (1.0 - uptime) * seconds
                uptimes.append(
                    f"{to_pretty_timedelta(datetime.timedelta(seconds=down_seconds))} over last {period} ({'%.3f' % (uptime*100)}% uptime)"
                )
        if uptimes:
            message += ". Overall, down " + ", ".join(uptimes)
        message += " " + site.url
        logger.info(message)
        site.last_tweet_at = now
        site.save()
        tweet(message)


@tracer.wrap()
def tweet_all_sites():
    for site in Site.objects.all():
        tweet_site_status(site)
