from django.core.management.base import BaseCommand
from django_redis import get_redis_connection

from clients.cache import CACHE_TTL, cache_key, render_client
from clients.models import Client


class Command(BaseCommand):
    help = "Carrega no Redis os clientes 1..N (conjunto quente)."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=1000)

    def handle(self, *args, **opts):
        n = opts["count"]
        redis = get_redis_connection("default")
        pipe = redis.pipeline()
        for client in Client.objects.filter(pk__lte=n):
            pipe.set(cache_key(client.pk), render_client(client), ex=CACHE_TTL)
        pipe.execute()
        self.stdout.write(f"{n} clientes quentes carregados")
