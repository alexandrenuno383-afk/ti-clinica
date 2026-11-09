# Benchmark de cache-aside para utilizadores

Aplicação Django REST Framework com PostgreSQL, Redis e Gunicorn. O modelo de autenticação
principal é `accounts.User`, baseado no `AbstractUser` do Django e guardado em
`accounts_user`. A API de benchmark devolve os campos do estudo, exceto `password`.

## Preparação

Com Docker Compose disponível:

```sh
docker compose up -d --build
bash bench/prepare.sh
```

`prepare.sh` aplica migrações, recria os 10000 utilizadores sintéticos com seed fixa,
limpa o Redis lógico 1 e reinicia as estatísticas de `pg_stat_statements`. A seed usa
passwords inutilizáveis e endereços `example.test`; não são contas reais.

## Endpoints

- Direto: `GET /api/v1/users/{id}/`
- Cache-aside: `GET /api/v1/users-cached/{id}/`

IDs 1–1000 formam o conjunto quente. Os restantes IDs são usados uma única vez por corrida
como conjunto frio. O cache armazena o JSON já serializado durante 300 segundos.

## Corridas

```sh
bench/run_all.sh
python3 bench/summarize.py
```

São executadas cinco repetições de cada combinação A/B e 0%, 80% e 99%, à taxa configurada
de 50 pedidos/s, com 15 segundos de aquecimento e 120 segundos de medição. Os resultados
ficam em `results/`, ignorado pelo Git. Os ficheiros já existentes em `pilot/` são preservados.

O contador de consultas SQL considera `accounts_user`. A taxa de acerto efetiva é obtida
dos contadores Redis durante a janela de medição; por isso deve ser interpretada na corrida
da variante B, que é a única que consulta o Redis por pedido.
