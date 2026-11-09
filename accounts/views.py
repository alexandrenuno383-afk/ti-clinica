from django.http import HttpResponse
from django_redis import get_redis_connection
from rest_framework.generics import RetrieveAPIView

from .cache import CACHE_TTL, cache_key, render_user
from .models import User
from .serializers import UserSerializer


class UserDetailDirect(RetrieveAPIView):
    """Variante A: leitura direta do PostgreSQL via ORM."""

    queryset = User.objects.all()
    serializer_class = UserSerializer


def user_detail_cached(request, pk):
    """Variante B: cache-aside em Redis com o JSON já serializado."""
    redis = get_redis_connection("default")
    key = cache_key(pk)
    body = redis.get(key)
    if body is not None:
        return HttpResponse(body, content_type="application/json")

    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return HttpResponse(
            b'{"detail":"Not found."}',
            status=404,
            content_type="application/json",
        )
    body = render_user(user)
    redis.set(key, body, ex=CACHE_TTL)
    return HttpResponse(body, content_type="application/json")
