import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import connection

from clients.models import Client

FIRST = ["Ana", "João", "Maria", "Pedro", "Inês", "Rui", "Sofia", "Tiago", "Marta",
         "Nuno", "Carla", "Miguel", "Beatriz", "André", "Rita", "Paulo"]
LAST = ["Silva", "Santos", "Ferreira", "Pereira", "Oliveira", "Costa", "Rodrigues",
        "Martins", "Sousa", "Fernandes", "Gonçalves", "Lopes", "Ribeiro", "Alves"]
CITIES = ["Porto", "Vila Nova de Gaia", "Matosinhos", "Gondomar", "Maia", "Braga",
          "Lisboa", "Coimbra", "Aveiro", "Espinho"]
STREETS = ["Rua das Flores", "Avenida da República", "Rua do Souto",
           "Travessa do Carmo", "Rua Direita", "Avenida dos Aliados"]
WORDS = ["vacinação", "consulta", "cão", "gato", "desparasitação", "esterilização",
         "alergia", "check-up", "urgência", "microchip", "dieta", "seguimento"]


class Command(BaseCommand):
    help = "Gera N clientes sintéticos com seed fixa (IDs 1..N)."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=10000)

    def handle(self, *args, **opts):
        n = opts["count"]
        rng = random.Random(42)
        base = date(2018, 1, 1)
        with connection.cursor() as cur:
            cur.execute("TRUNCATE clients_client RESTART IDENTITY")
        items = [
            Client(
                name=f"{rng.choice(FIRST)} {rng.choice(LAST)} {rng.choice(LAST)}",
                email=f"cliente{i}@example.com",
                phone=f"9{rng.randint(10000000, 99999999)}",
                nif=str(rng.randint(100000000, 299999999)),
                city=rng.choice(CITIES),
                address=f"{rng.choice(STREETS)}, {rng.randint(1, 300)}",
                registered_at=base + timedelta(days=rng.randint(0, 2900)),
                notes=" ".join(rng.choices(WORDS, k=30)),
            )
            for i in range(1, n + 1)
        ]
        Client.objects.bulk_create(items, batch_size=1000)
        self.stdout.write(self.style.SUCCESS(f"{n} clientes criados"))
