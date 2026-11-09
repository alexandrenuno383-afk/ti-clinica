from django.core.management.base import BaseCommand
from django_redis import get_redis_connection

from accounts.cache import CACHE_TTL, cache_key, render_user
from accounts.models import User


class Command(BaseCommand):
    help = "Carrega no Redis os utilizadores 1..N (conjunto quente)."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=1000)

    def handle(self, *args, **opts):
        n = opts["count"]
        redis = get_redis_connection("default")
        pipe = redis.pipeline()
        for user in User.objects.filter(pk__lte=n).order_by("pk"):
            pipe.set(cache_key(user.pk), render_user(user), ex=CACHE_TTL)
        pipe.execute()
        self.stdout.write(f"{n} utilizadores quentes carregados")
