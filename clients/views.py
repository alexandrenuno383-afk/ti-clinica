from django.http import HttpResponse
from django_redis import get_redis_connection
from rest_framework.generics import RetrieveAPIView

from .cache import CACHE_TTL, cache_key, render_client
from .models import Client
from .serializers import ClientSerializer


class ClientDetailDirect(RetrieveAPIView):
    """Variante A: leitura direta do PostgreSQL via ORM."""
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


def client_detail_cached(request, pk):
    """Variante B: cache-aside em Redis com o JSON já serializado."""
    redis = get_redis_connection("default")
    key = cache_key(pk)

    body = redis.get(key)
    if body is not None:  # acerto
        return HttpResponse(body, content_type="application/json")

    # falha: PostgreSQL + serialização + SET
    try:
        client = Client.objects.get(pk=pk)
    except Client.DoesNotExist:
        return HttpResponse(b'{"detail":"Not found."}', status=404,
                            content_type="application/json")
    body = render_client(client)
    redis.set(key, body, ex=CACHE_TTL)
    return HttpResponse(body, content_type="application/json")
