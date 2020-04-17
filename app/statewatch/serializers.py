from rest_framework import serializers
from statewatch.models import Site, Check


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = [
            'guid', 'name', 'url',
            'last_check', 'last_up', 'last_down', 'last_change',
            'uptime_hour', 'uptime_day', 'uptime_week', 'uptime_30', 'uptime_90',
        ]

class SiteDowntimeSerializer(serializers.Serializer):
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    duration = serializers.DurationField()
    duration_seconds = serializers.IntegerField()

class CheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Check
        fields = [
            'id', 'guid', 'timestamp', 'data', 'data_unfiltered', 'tries', 'etag',
        ]

