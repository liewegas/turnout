from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from .models import Site, SiteCheck
from .serializers import SiteCheckSerializer, SiteDowntimeSerializer, SiteSerializer


@api_view(["GET"])
def api_root(request, format=None):
    return Response({"sites": reverse("site-list", request=request, format=format),})


class SiteList(generics.ListAPIView):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer


class SiteDownList(generics.ListAPIView):
    queryset = Site.objects.filter(state_up=False)
    serializer_class = SiteSerializer


class SiteDetail(generics.RetrieveAPIView):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer


class SiteChecks(APIView):
    def get(self, request, pk, format=None):
        checks = SiteCheck.objects.filter(site_id=pk)
        serializer = SiteCheckSerializer(checks, many=True)
        return Response(serializer.data)


class SiteDowntime(APIView):
    def get(self, request, pk, format=None):
        checks = SiteCheck.objects.filter(site_id=pk).order_by("created_at")
        start = None
        r = []
        for c in checks:
            if not c.state_up:
                if start is None:
                    start = c.created_at
            else:
                if start:
                    r.append(
                        {
                            "start": start,
                            "end": c.created_at,
                            "duration": c.created_at - start,
                            "duration_seconds": c.created_at.timestamp()
                            - start.timestamp(),
                        }
                    )
                    start = None
        serializer = SiteDowntimeSerializer(r, many=True)
        return Response(serializer.data)


class SiteCheckDetail(generics.RetrieveAPIView):
    queryset = SiteCheck.objects.all()
    serializer_class = SiteCheckSerializer
