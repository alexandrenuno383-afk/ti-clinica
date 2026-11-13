# Configuração partilhada pelos scripts de medição.
NET="${NET:-ti-clinica_default}"
K6_IMAGE="${K6_IMAGE:-grafana/k6:2.3.0}"

# Reserva de CPUs: 1 CPU para o k6, os restantes para web, db e redis.
N_CPUS=$(nproc)
if [ "$N_CPUS" -ge 4 ]; then
  K6_CPUS="${K6_CPUS:-0}"
  APP_CPUS="${APP_CPUS:-1-$((N_CPUS-1))}"
else
  echo "AVISO: só $N_CPUS CPUs; as medições ficam menos fiáveis." >&2
  K6_CPUS="${K6_CPUS:-0}"
  APP_CPUS="${APP_CPUS:-0-$((N_CPUS-1))}"
fi
