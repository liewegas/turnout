import logging

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Region
from .serializers import RegionDetailSerializer, RegionNameSerializer

logger = logging.getLogger("official")


class StateRegionsViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    model = Region
    serializer_class = RegionNameSerializer

    def get_queryset(self):
        state_code = self.kwargs["state"]
        queryset = Region.visible.filter(state__code=state_code).order_by("name")

        county = self.request.query_params.get("county", None)
        if county:
            queryset = queryset.filter(county=county)

        municipality = self.request.query_params.get("municipality", None)
        if municipality:
            queryset = queryset.filter(municipality=municipality)

        return queryset


class RegionDetailViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    model = Region
    serializer_class = RegionDetailSerializer
    queryset = Region.objects.all()
    lookup_field = "external_id"


@api_view(["GET"])
def address_regions(request):
    regions, was_geocode_error = get_regions_for_address(
        street=request.query_params.get("address1", None),
        city=request.query_params.get("city", None),
        state=request.query_params.get("state", None),
        zipcode=request.query_params.get("zipcode", None),
    )

    if was_geocode_error:
        return Response("unable to geocode address", status=status.HTTP_400_BAD_REQUEST)

    serializer = RegionNameSerializer(regions, many=True)
    return Response(serializer.data)
