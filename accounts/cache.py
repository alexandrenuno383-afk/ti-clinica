from rest_framework.renderers import JSONRenderer

from .serializers import UserSerializer

CACHE_TTL = 300  # segundos; maior do que cada corrida


def cache_key(pk):
    return f"user:{pk}"


def render_user(user):
    """Devolve o mesmo JSON para A e B; credenciais nunca são serializadas."""
    return JSONRenderer().render(UserSerializer(user).data)
