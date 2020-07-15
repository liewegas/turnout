from django.contrib import admin

from . import models


@admin.register(models.Proxy)
class ProxyAdmin(admin.ModelAdmin):
    list_display = (
        "proxy",
        "description",
        "state",
        "failure_count",
        "modified_at",
        "created_at",
    )


@admin.register(models.Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = (
        "description",
        "url",
        "state_up",
        "state_changed_at",
        "last_went_down_at",
        "last_went_up_at",
        "last_tweet_at",
        "uptime_day",
        "uptime_week",
        "uptime_month",
        "uptime_quarter",
    )
