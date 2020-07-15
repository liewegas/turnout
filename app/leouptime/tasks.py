from celery import shared_task


@shared_task(queue="uptime")
def check_uptime_group(slug):
    from .uptime import check_group

    check_group(slug)


@shared_task(queue="uptime")
def check_uptime():
    from .uptime import MONITORS

    for slug in MONITORS.keys():
        check_uptime_group.delay(slug)


@shared_task(queue="uptime")
def tweet_uptime():
    from .uptime import tweet_all_sites

    tweet_all_sites()


@shared_task(queue="uptime")
def check_proxies():
    from .proxy import check_proxies

    check_proxies()
