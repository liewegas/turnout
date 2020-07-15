from rest_framework import serializers

from .models import Site, SiteCheck


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = [
            "uuid",
            "url",
            "description",
            "state_up",
            "state_changed_at",
            "last_went_down_at",
            "last_went_up_at",
            "last_tweet_at",
            "uptime_day",
            "uptime_week",
            "uptime_month",
            "uptime_quarter",
        ]


class SiteDowntimeSerializer(serializers.Serializer):
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    duration = serializers.DurationField()
    duration_seconds = serializers.IntegerField()


class SiteCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteCheck
        fields = [
            "site",
            "state_up",
            "ignore",
            "load_time",
            "error",
            "proxy",
            "created_at",
        ]
