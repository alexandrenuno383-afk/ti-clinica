import http from 'k6/http';
import { check } from 'k6';
import exec from 'k6/execution';

const BASE = __ENV.BASE_URL || 'http://web:8000';
const VARIANT = __ENV.VARIANT || 'A';
const HIT = parseFloat(__ENV.HIT_RATE || '0.99');
const PHASE = __ENV.PHASE || 'measure';          // warmup | measure
const RATE = parseInt(__ENV.RATE || '50');
const WARMUP_S = parseInt(__ENV.WARMUP_S || '15');
const MEASURE_S = parseInt(__ENV.MEASURE_S || '120');

const HOT = 1000;                 // IDs 1..1000 (conjunto quente)
const TOTAL = 10000;
const COLD = TOTAL - HOT;         // IDs 1001..10000 (frios)

const DURATION = PHASE === 'warmup' ? WARMUP_S : MEASURE_S;
// A medição continua a numeração do aquecimento, para os IDs frios nunca se repetirem.
const OFFSET = PHASE === 'warmup' ? 0 : RATE * WARMUP_S;

if (RATE * (WARMUP_S + MEASURE_S) > COLD) {
  throw new Error('IDs frios insuficientes para esta duração/taxa');
}

const PATH = VARIANT === 'B' ? '/api/v1/users-cached/' : '/api/v1/users/';

export const options = {
  scenarios: {
    [PHASE]: {
      executor: 'constant-arrival-rate',
      rate: RATE,
      timeUnit: '1s',
      duration: `${DURATION}s`,
      preAllocatedVUs: 20,
      maxVUs: 100,
    },
  },
  summaryTrendStats: ['avg', 'med', 'p(90)', 'p(95)', 'p(99)', 'max'],
};

// Hash determinístico (finalizador do MurmurHash3) -> número em [0, 1).
// Dá a mesma sequência às duas variantes e em todas as repetições.
function rnd(k) {
  let t = (Math.imul(k + 1, 0x9e3779b1) ^ 0x85ebca6b) | 0;
  t = Math.imul(t ^ (t >>> 16), 0x85ebca6b);
  t = Math.imul(t ^ (t >>> 13), 0xc2b2ae35);
  t ^= t >>> 16;
  return (t >>> 0) / 4294967296;
}

export default function () {
  const n = OFFSET + exec.scenario.iterationInTest;
  let id;
  if (rnd(2 * n) < HIT) {
    id = 1 + Math.floor(rnd(2 * n + 1) * HOT);   // quente
  } else {
    id = HOT + 1 + n;                             // frio, único (n nunca se repete)
  }
  const res = http.get(`${BASE}${PATH}${id}/`);
  check(res, { 'status 200': (r) => r.status === 200 });
}
