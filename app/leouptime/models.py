from django.db import models

from common import enums
from common.fields import TurnoutEnumField
from common.utils.models import TimestampModel, UUIDModel


class Site(UUIDModel, TimestampModel):
    url = models.TextField(null=True)
    description = models.TextField(null=True)
    state_up = models.BooleanField(null=True)
    state_changed_at = models.DateTimeField(null=True)
    last_went_down_at = models.DateTimeField(null=True)
    last_went_up_at = models.DateTimeField(null=True)
    last_tweet_at = models.DateTimeField(null=True)
    uptime_day = models.FloatField(null=True)
    uptime_week = models.FloatField(null=True)
    uptime_month = models.FloatField(null=True)
    uptime_quarter = models.FloatField(null=True)

    class Meta:
        ordering = ["-modified_at"]

    def calc_uptimes(self):
        r = self.do_calc_uptime(
            [3600 * 24, 3600 * 24 * 7, 3600 * 24 * 30, 3600 * 24 * 90]
        )
        #        print(r)
        (self.uptime_day, self.uptime_week, self.uptime_month, self.uptime_quarter) = r

    def do_calc_uptime(self, cutoffs):
        now = None
        last = None
        total_up = 0
        total_down = 0
        cutoff = 0
        r = []
        for check in SiteCheck.objects.filter(site=self).order_by("-created_at"):
            ts = check.created_at.timestamp()
            if not last:
                now = ts
                cutoff = now - cutoffs.pop(0)
            else:
                assert cutoff < last
                while ts < cutoff:
                    tup = total_up
                    tdn = total_down
                    if check.state_up:
                        tup += last - cutoff
                    else:
                        tdn += last - cutoff
                    #                    print('cutoff %d  tup %d, tdn %d,  sum %d' % (cutoff, tup, tdn, tup+tdn))
                    assert tup + tdn == now - cutoff
                    r.append(float(tup) / float(tup + tdn))
                    if not cutoffs:
                        return r
                    cutoff = now - cutoffs.pop(0)
                if check.state_up:
                    total_up += last - ts
                else:
                    total_down += last - ts
            #                print('cutoff %s  tup %d, tdn %d' % (cutoff, total_up, total_down))
            last = ts

        # we assume up for pre-history
        assert cutoff < last
        while True:
            total_up += last - cutoff
            last = cutoff
            r.append(float(total_up) / float(total_up + total_down))
            if not cutoffs:
                return r
            cutoff = now - cutoffs.pop(0)


class SiteCheck(TimestampModel):
    site = models.ForeignKey("Site", null=True, on_delete=models.CASCADE)
    state_up = models.BooleanField(null=True)
    ignore = models.BooleanField(null=True)
    load_time = models.FloatField(null=True)
    error = models.TextField(null=True)
    proxy = models.ForeignKey("Proxy", null=True, on_delete=models.CASCADE)


class Proxy(TimestampModel):
    proxy = models.TextField(primary_key=True)
    description = models.TextField(null=True)
    state = TurnoutEnumField(enums.ProxyStatus, null=True)
    failure_count = models.IntegerField(null=True)
