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

`prepare.sh` aplica migrações, recria 10000 utilizadores sintéticos com seed fixa, limpa o
Redis lógico 1 e reinicia as estatísticas de `pg_stat_statements`. A seed usa passwords
inutilizáveis e endereços `example.test`; não são contas reais.

## Endpoints

- Direto: `GET /api/v1/users/{id}/`
- Cache-aside: `GET /api/v1/users-cached/{id}/`

IDs 1–1000 formam o conjunto quente. Os restantes IDs são usados uma única vez por corrida
como conjunto frio. O cache guarda o JSON já serializado durante 300 segundos.

## Corridas

```sh
bash bench/run_all.sh
```

O script executa 30 corridas: cinco repetições de cada combinação A/B e 0%, 80% e 99% de
acerto, à taxa configurada de 50 pedidos/s. A duração observada da corrida completa nesta
máquina é cerca de 3,5 horas (aproximadamente 7 minutos por corrida). A corrida curta
`REPS=1 MEASURE_S=30 WARMUP_S=5 bash bench/run_all.sh`, com seis combinações, demora cerca
de 4 minutos, sem contar a preparação dos containers.

Os resultados brutos ficam em `results/`; os dados usados na análise final estão em
`data/results-final.csv`.

## Ambiente de medição

Dados recolhidos nesta máquina:

- CPU: AMD Ryzen 5 5500U with Radeon Graphics; 6 núcleos físicos, 2 threads por núcleo.
- CPUs visíveis no WSL (`nproc`): 12.
- RAM visível (`free -h`): 5,5 GiB total.
- Distribuição WSL: Ubuntu 26.04.1 LTS; kernel `6.18.33.2-microsoft-standard-WSL2`.
- Windows: `wsl.exe --version` não ficou acessível neste terminal, por isso a versão do
  Windows não foi confirmada.
- Docker Client e Server: 29.8.1.
- Imagens: PostgreSQL 18.6 (`postgres:18.6`), Redis 8.10.3 (`redis:8.10.3`), k6 2.3.0
  (`grafana/k6:2.3.0`), Python 3.14.10 (base `python:3.14-slim`).
- Pacotes da aplicação: Django 6.1.3, djangorestframework 3.18.3, psycopg 3.3.8,
  django-redis 7.0.0 e Gunicorn 26.2.0. O `requirements.txt` fixa estas versões.
- Análise: Matplotlib 3.11.2, fixado separadamente em `requirements-analysis.txt`.

## Análise

Instala as dependências de análise fora do ambiente da aplicação e gera o resumo e figuras:

```sh
python3 -m venv .venv-analysis
. .venv-analysis/bin/activate
pip install -r requirements-analysis.txt
python3 bench/summarize.py
python3 bench/plot.py
```

Por omissão, ambos os scripts leem `data/results-final.csv`; também aceitam um CSV como
argumento. `summarize.py` mantém a tabela de p95, redução, IQR, acerto real e consultas SQL,
imprime média, desvio padrão amostral e mediana de p50, p95 e avg por variante/taxa, e grava
os valores em `data/summary.csv`. `plot.py` gera `figures/fig1_latencia.png` (p50 e p95 em
painéis lado a lado, barras A/B e desvio padrão) e `figures/fig2_sql.png` (consultas SQL por
pedido, A/B por taxa); ambas as figuras são gravadas a 300 dpi com fundo branco.

## Resultados

Média ± desvio padrão amostral, em milissegundos, calculados a partir das cinco repetições:

| Acerto | Variante | p50 (ms) | p95 (ms) |
|---:|:---:|---:|---:|
| 0% | A | 5,735 ± 0,116 | 7,290 ± 0,147 |
| 0% | B | 7,003 ± 0,028 | 8,918 ± 0,111 |
| 80% | A | 5,607 ± 0,211 | 7,363 ± 0,296 |
| 80% | B | 2,779 ± 0,041 | 7,522 ± 0,146 |
| 99% | A | 5,664 ± 0,130 | 7,310 ± 0,159 |
| 99% | B | 2,661 ± 0,051 | 3,935 ± 0,467 |

Hipótese **não confirmada**: a mediana da redução de p95 foi 48,5% a 99% de acerto (abaixo
do limiar de 50%) e −2,9% a 80% (abaixo de 50%). O critério mantém-se: confirmação exigiria
redução ≥ 50% a 99% e < 50% a 80%.

## Autores

- Tiago Ribeiro (A22607558)
- Nuno Alexandre (A22607462)
