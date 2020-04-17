from django.http import HttpResponse
from statewatch.models import Site, Check, Blob
from statewatch.serializers import SiteSerializer, SiteDowntimeSerializer, CheckSerializer
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse

import tempfile
import subprocess

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'sites': reverse('site-list', request=request, format=format),
    })

class SiteList(generics.ListAPIView):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer

class SiteDetail(generics.RetrieveAPIView):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer

class SiteChecks(APIView):
    def get(self, request, pk, format=None):
        checks = Check.objects.filter(guid__exact=pk)
        serializer = CheckSerializer(checks, many=True)
        return Response(serializer.data)

class SiteDowntime(APIView):
    def get(self, request, pk, format=None):
        checks = Check.objects.filter(guid__exact=pk).order_by('timestamp')
        start = None
        r = []
        for c in checks:
            if c.tries > 0:
                if start is None:
                    start = c.timestamp
            else:
                if start:
                    r.append({
                        'start': start,
                        'end': c.timestamp,
                        'duration': c.timestamp - start,
                        'duration_seconds': c.timestamp.timestamp() - start.timestamp(),
                    })
                    start = None
        serializer = SiteDowntimeSerializer(r, many=True)
        return Response(serializer.data)

class SiteChangesFiltered(APIView):
    def get(self, request, pk, format=None):
        checks = Check.objects.filter(guid__exact=pk).order_by('timestamp')
        last = None
        r = []
        for c in checks:
            if c.data is None:
                continue
            if last is None or last != c.data:
                r.append(c)
                last = c.data
        serializer = CheckSerializer(r, many=True)
        return Response(serializer.data)

class SiteChangesUnfiltered(APIView):
    def get(self, request, pk, format=None):
        checks = Check.objects.filter(guid__exact=pk).order_by('timestamp')
        last = None
        r = []
        for c in checks:
            if c.data_unfiltered is None:
                continue
            if last is None or last != c.data_unfiltered:
                r.append(c)
                last = c.data_unfiltered
        serializer = CheckSerializer(r, many=True)
        return Response(serializer.data)

class CheckDetail(generics.RetrieveAPIView):
    queryset = Check.objects.all()
    serializer_class = CheckSerializer

def get_blob(request, pk):
    blob = Blob.objects.get(pk=pk)
    return HttpResponse(blob.data, content_type='text/plain')

def diff_blob(request, a, b):
    a = Blob.objects.get(pk=a)
    b = Blob.objects.get(pk=b)

    af = tempfile.NamedTemporaryFile(mode='w')
    af.write(a.data)
    af.flush()
    bf = tempfile.NamedTemporaryFile(mode='w')
    bf.write(b.data)
    bf.flush()

    cmd = ['diff', '-u', af.name, bf.name]
    out = subprocess.run(cmd, check=False, stdout=subprocess.PIPE).stdout

    return HttpResponse(out, content_type='text/plain')
