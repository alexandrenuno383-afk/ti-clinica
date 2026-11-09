import random
from datetime import datetime, timedelta, timezone

from django.core.management.base import BaseCommand
from django.db import connection

from accounts.models import User

FIRST = [
    "Ana", "João", "Maria", "Pedro", "Inês", "Rui", "Sofia", "Tiago",
    "Marta", "Nuno", "Carla", "Miguel", "Beatriz", "André", "Rita", "Paulo",
]
LAST = [
    "Silva", "Santos", "Ferreira", "Pereira", "Oliveira", "Costa", "Rodrigues",
    "Martins", "Sousa", "Fernandes", "Gonçalves", "Lopes", "Ribeiro", "Alves",
]


class Command(BaseCommand):
    help = "Gera N utilizadores sintéticos determinísticos (IDs 1..N)."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=10000)

    def handle(self, *args, **opts):
        n = opts["count"]
        if n < 1:
            raise ValueError("--count tem de ser pelo menos 1")

        rng = random.Random(42)
        joined = datetime(2020, 1, 1, tzinfo=timezone.utc)
        users = []
        for i in range(1, n + 1):
            first = rng.choice(FIRST)
            last = rng.choice(LAST)
            user = User(
                username=f"user{i:05d}",
                first_name=first,
                last_name=last,
                email=f"user{i:05d}@example.test",
                password="!",  # password inutilizável; este estudo não testa login
                is_staff=False,
                is_active=True,
                is_superuser=False,
                last_login=None,
                date_joined=joined + timedelta(seconds=i),
            )
            users.append(user)

        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "accounts_user" RESTART IDENTITY CASCADE')
        User.objects.bulk_create(users, batch_size=1000)
        self.stdout.write(self.style.SUCCESS(f"{n} utilizadores criados"))
