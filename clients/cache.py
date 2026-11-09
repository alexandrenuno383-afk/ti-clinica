from rest_framework.renderers import JSONRenderer

from .serializers import ClientSerializer

CACHE_TTL = 300  # segundos; maior do que cada corrida


def cache_key(pk):
    return f"client:{pk}"


def render_client(client):
    """JSON já serializado, igual ao que a variante A devolve."""
    return JSONRenderer().render(ClientSerializer(client).data)
