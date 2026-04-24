# QA — YOM

Suite de QA para la plataforma YOM (You Order Me): B2B web, APP mobile y Admin.

**Stack de QA:** Cowork (validación visual con IA) + Playwright (regresión automatizada) + Maestro (APP Android).

Dashboard público: [eduardolaloyom.github.io/qa](https://eduardolaloyom.github.io/qa)

---

## Qué es Cowork

Cowork es una sesión de Claude AI en [claude.ai](https://claude.ai) que actúa como QA humano: navega la app paso a paso, valida textos, flujos, banners y configuración de cada cliente. No es un test automatizado — es validación visual e interactiva guiada por el playbook `COWORK.md`.

Hay 4 modos de sesión:

| Modo | Qué hace |
|------|----------|
| **A — Configuración** | Valida que la config del cliente (precios, carrito, documentos) se refleje correctamente en la UI |
| **B — Flujo de compra** | Recorre catálogo → carrito → checkout → orden completa |
| **C — Features especiales** | Valida cupones, descuentos por volumen, pedidos mínimos, etc. (según cliente) |
| **D — Regresión manual** | Casos Tier 1 críticos que Playwright no puede cubrir (visuales, textos, UX) |

Al final de cada modo se genera un **HANDOFF** que Claude Code guarda en `QA/{CLIENTE}/{FECHA}/cowork-session.md`.

---

## Flujo completo de ejecución

```
1. Extraer config de MongoDB
   python3 data/mongo-extractor.py --env staging --output data/qa-matrix-staging.json
   python3 tools/sync-clients.py --input data/qa-matrix-staging.json
   → genera tests/e2e/fixtures/clients.ts (AUTO-GENERADO, no editar)

2. Playwright — regresión automatizada (obligatorio)
   cd tests/e2e
   npx playwright test --project=bastien b2b/
   → resultado en playwright-report/index.html

3. Publicar resultados al dashboard
   python3 tools/publish-results.py --date 2026-04-24 --client bastien
   → actualiza public/history/ y public/reports/
   → git push → GitHub Pages se actualiza

4. Sesión Cowork (claude.ai)
   → Abrir claude.ai → nueva sesión
   → Pegar contenido de COWORK.md al inicio
   → Ejecutar Modo A → B → C (si aplica) → D (si aplica)
   → Al final de cada modo: copiar bloque HANDOFF

5. Guardar HANDOFF en Claude Code
   "agrega modo {A/B/C/D} al archivo de sesión de {CLIENTE}"
   → escribe en QA/{CLIENTE}/{FECHA}/cowork-session.md

6. Generar reporte
   /report-qa {CLIENTE} {FECHA}
   → genera QA/{CLIENTE}/{FECHA}/qa-report-{FECHA}.md
   → genera public/qa-reports/{CLIENTE}-{FECHA}.html
   → actualiza public/manifest.json

7. Mejoras al proceso (opcional)
   /qa-improve {CLIENTE} {FECHA}
   → propone tests nuevos, actualiza COWORK.md, detecta flags nuevos
```

---

## Herramientas y métricas

| Herramienta | Qué mide | Resultado |
|-------------|----------|-----------|
| **Playwright** | Regresión E2E automatizada | Pass rate % por cliente → dashboard |
| **Cowork** (claude.ai) | Validación visual + flujos reales | Health Score 0–100 → dashboard |
| **Maestro** | Flujos APP Android | Health score APP → dashboard |

> Cowork Health Score ≠ Playwright pass rate. Son métricas complementarias, no equivalentes.

**Orden de prioridad al ejecutar QA:**
1. Playwright (detecta regresiones conocidas)
2. Cowork (valida lo que Playwright no ve: UI, textos, flujos multi-paso)
3. Maestro (APP mobile)

Si Playwright encuentra un P0 (auth roto, checkout imposible) → resolver antes de continuar con Cowork.

---

## Clientes activos

| Slug | Ambiente | URL |
|------|----------|-----|
| `bastien` | staging | bastien.solopide.me |
| `sonrie` | staging | sonrie.solopide.me |
| `codelpa` | staging | beta-codelpa.solopide.me |
| `surtiventas` | staging | surtiventas.solopide.me |
| `prinorte` | production | tienda.prinorte.cl |
| `caren` | production | caren.youorder.me |
| `soprole` | production | soprole.youorder.me |

Los slugs se usan en fixtures, variables de entorno, reportes y comandos. `clients.ts` se genera automáticamente desde MongoDB — nunca editar a mano.

---

## Contract tests

`tests/e2e/b2b/00-contract.spec.ts` valida la integridad de la config antes de cualquier test E2E:

- Todos los campos booleanos son `boolean` (no string ni number)
- `taxes.taxRate` está en `[0, 1]` — previene el bug donde MongoDB tiene `19` en vez de `0.19`
- Fixture tiene `name`, `baseURL` y `config`

Corre primero (prefijo `00-`) y falla rápido si la config está mal. Schema de referencia: `data/schemas/client-variables.schema.json`.

---

## Setup

### Requisitos

- Python 3.9+
- Node.js 20+
- Acceso a MongoDB staging (`solopide.me`) — credenciales en `.env`
- Android Studio + Maestro CLI (para APP — opcional)

### Credenciales

```bash
# Playwright — credenciales por cliente
cp tests/e2e/.env.example tests/e2e/.env
# Completar: BASTIEN_EMAIL, BASTIEN_PASSWORD, SONRIE_EMAIL, etc.

# Maestro — APP
cp tests/app/config/config.example.yaml tests/app/config/config.yaml
```

### Instalar dependencias Playwright

```bash
cd tests/e2e
npm install
npx playwright install chromium
```

### Primer run

```bash
cd tests/e2e
npx playwright test b2b/00-contract.spec.ts     # Contract tests — sin browser
npx playwright test b2b/login.spec.ts           # Solo login, todos los clientes
npx playwright test --project=bastien b2b/      # Bastien completo
npx playwright show-report                       # Abrir reporte HTML
```

---

## Comandos disponibles (Claude Code)

| Comando | Cuándo usarlo |
|---------|--------------|
| `/qa-plan-client {CLIENTE}` | Planificar QA completo para un cliente nuevo |
| `/run-playwright b2b` | Correr tests Playwright B2B y publicar al dashboard |
| `/triage-playwright` | Analizar fallos del último run y crear tickets Linear |
| `/report-qa {CLIENTE} {FECHA}` | Generar reporte HTML desde sesión Cowork |
| `/qa-improve {CLIENTE} {FECHA}` | Aplicar mejoras al proceso sugeridas en la sesión |
| `/qa-coverage-analysis` | Ver gaps de cobertura por cliente |
| `/qa-client-validation {CLIENTE} staging` | Suite completa: MongoDB → tests → reporte |

---

## Documentos clave

| Documento | Para quién | Contenido |
|-----------|-----------|-----------|
| [COWORK.md](COWORK.md) | QA (Cowork) | Playbook completo: modos A/B/C/D, HANDOFF, veredicto, escalamiento |
| [CLAUDE.md](CLAUDE.md) | Claude Code | Comandos disponibles, estructura del repo, reglas |
| [qa-master-guide.md](qa-master-guide.md) | QA | Casos Tier 1-3, fixtures, convenciones |
| [playbook-qa-cliente-nuevo.md](playbook-qa-cliente-nuevo.md) | QA | Onboarding completo para cliente nuevo (6 fases) |
| [B2B_REFERENCE.md](B2B_REFERENCE.md) | QA + Dev | Selectores UI B2B, componentes, código Playwright |
| [qa-app-strategy.md](qa-app-strategy.md) | QA | Estrategia APP mobile (Maestro) |
| [checklists/INDICE.md](checklists/INDICE.md) | QA | Mapa de cobertura: checklist → test → caso |

---

## Estructura del repo

```
qa/
├── COWORK.md                    # Playbook QA para Cowork (claude.ai)
├── CLAUDE.md                    # Instrucciones para Claude Code
│
├── ai-specs/
│   ├── .agents/                 # Roles IA (qa-coordinator, playwright-specialist...)
│   ├── .commands/               # Workflows (/report-qa, /run-playwright, /qa-improve...)
│   └── specs/                   # Standards QA, Maestro, Admin
│
├── tests/
│   ├── e2e/                     # Playwright B2B + Admin
│   │   ├── b2b/                 # Specs: login, cart, prices, checkout, coupons...
│   │   │   └── 00-contract.spec.ts  # Contract tests — corren primero
│   │   ├── fixtures/            # clients.ts (AUTO-GENERADO), multi-client-auth.ts
│   │   └── playwright.config.ts
│   └── app/                     # Maestro flows APP Android
│       ├── flows/               # Flows por cliente
│       └── config/              # Config de ambiente
│
├── data/
│   ├── mongo-extractor.py       # Extrae config desde MongoDB
│   ├── schemas/                 # JSON schemas para validación de config
│   └── qa-matrix-staging.json  # Config clientes staging (gitignored en prod)
│
├── tools/
│   ├── publish-results.py       # Publica resultados Playwright al dashboard
│   ├── sync-clients.py          # Genera clients.ts desde qa-matrix.json
│   └── evaluate-qa-listo.py     # Calcula estado LISTO/PENDIENTE/BLOQUEADO
│
├── templates/                   # qa-report-template.md, escalation-templates.md
├── checklists/                  # Casos de prueba por categoría
├── QA/                          # Resultados: QA/{CLIENTE}/{FECHA}/
│
└── public/                      # Dashboard GitHub Pages
    ├── index.html               # Dashboard principal
    ├── manifest.json            # Índice unificado Cowork + Maestro
    ├── history/                 # JSON histórico por fecha
    ├── reports/                 # HTML reports Playwright por cliente
    ├── qa-reports/              # HTML reports Cowork
    └── app-reports/             # HTML reports Maestro APP
```

---

## Escalamiento de issues

| Severidad | Canal | Acción |
|-----------|-------|--------|
| P0 — flujo crítico roto (auth, checkout) | Slack `#engineering` | Escalar inmediatamente, detener QA |
| P1 — feature no funciona | Linear (etiqueta `qa`) | Crear ticket, continuar |
| P2/P3 — cosmético o menor | Reporte HTML | Anotar, no escalar |

Templates en [templates/escalation-templates.md](templates/escalation-templates.md).
