import logging

from rest_framework import mixins, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apikey.auth import ApiKeyAuthentication, ApiKeyRequired

from .match import get_regions_for_address
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


class AddressRegionView(APIView):
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [ApiKeyRequired]

    def get(self, request, format=None):
        if not request.auth.subscriber.is_first_party:
            return Response(status=status.HTTP_403_FORBIDDEN)

        regions, was_geocode_error = get_regions_for_address(
            street=request.query_params.get("address1", None),
            city=request.query_params.get("city", None),
            state=request.query_params.get("state", None),
            zipcode=request.query_params.get("zipcode", None),
        )

        if was_geocode_error:
            return Response(
                {"error": "unable to geocode address"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = RegionDetailSerializer(regions, many=True)
        return Response({"regions": serializer.data, "error": None,})
