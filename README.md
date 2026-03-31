# QA — YOM

Suite de QA para la plataforma YOM: B2B, APP mobile y Admin.

Cubre testing automatizado (Playwright E2E, Maestro mobile), generación de checklists por cliente desde MongoDB, y proceso operacional de puesta en marcha.

## Documentos clave

| Documento | Para quién | Contenido |
|-----------|-----------|-----------|
| [GUIA-OPERACIONAL-QA.md](GUIA-OPERACIONAL-QA.md) | **QA + Devs** | Qué, cuándo, quién y cómo se aplica cada artefacto |
| [checklists/INDICE.md](checklists/INDICE.md) | **QA + Devs** | Mapa completo: checklist → test automatizado → cobertura |
| [qa-master-prompt.md](qa-master-prompt.md) | **QA** | Casos de prueba madre (~80 casos), fixtures, esquemas |
| [playbook-qa-cliente-nuevo.md](playbook-qa-cliente-nuevo.md) | **QA** | Paso a paso para onboarding de cliente nuevo |
| [plan-qa-b2b.md](plan-qa-b2b.md) | **Devs** | Estrategia QA B2B (3 capas) |
| [qa-app-strategy.md](qa-app-strategy.md) | **QA** | Estrategia QA APP mobile |

## Estructura

```
qa/
├── checklists/                    # Checklists QA organizadas por categoría
│   ├── INDICE.md                  # Mapa maestro: checklist → test → cobertura
│   ├── regresion/                 # Basadas en post-mortems (incidentes reales)
│   ├── deuda-tecnica/             # Basadas en deuda técnica (Notion)
│   ├── servicios/                 # Backend: ERP, Khipu, Validator, Webhooks
│   └── funcional/                 # Producto: pricing, carrito, GA4, app
│
├── tests/
│   ├── e2e/                       # Playwright — E2E browser (B2B + Admin)
│   │   ├── b2b/                   # 13 specs: login, cart, coupons, pricing, etc.
│   │   ├── admin/                 # 2 specs: login, orders
│   │   ├── fixtures/              # Auth helper
│   │   └── playwright.config.ts
│   └── app/                       # Maestro — APP mobile Android
│       ├── flows/                 # 10 flows: login, pedido, pagos, concurrencia
│       └── config/                # Env config
│
├── data/                          # Datos de clientes y config
├── tools/                         # Scripts: extractor, generador, orquestador
├── templates/                     # Templates de reporte y escalamiento
├── references/                    # Taxonomía de issues
├── QA/                            # Resultados por cliente y fecha
│
├── GUIA-OPERACIONAL-QA.md         # Guía operacional (quién hace qué, cuándo)
├── plan-qa-b2b.md                 # Estrategia QA B2B (3 capas)
├── qa-app-strategy.md             # Estrategia QA APP mobile
├── qa-master-prompt.md            # Documento madre: ~80 casos
├── playbook-qa-cliente-nuevo.md   # Paso a paso onboarding cliente nuevo
└── SKILL.md                       # Flujo operacional QA PeM
```

## Setup

### Requisitos

- Python 3.9+
- Node.js 20+
- MongoDB access (para `mongo-extractor.py`)
- Android Studio (para Maestro — opcional)

### Credenciales

```bash
# Root — MongoDB (para extractor)
cp .env.example .env
# Completar con credenciales reales

# Playwright — B2B
cp tests/e2e/.env.example tests/e2e/.env
# Completar con credenciales del comercio

# Maestro — APP
cp tests/app/config/env.example.yaml tests/app/config/env.yaml
# Completar con credenciales del vendedor
```

### Playwright (E2E B2B)

```bash
cd tests/e2e
npm install
npx playwright install chromium
npx playwright test
```

### Maestro (APP mobile)

```bash
# Instalar Maestro
curl -Ls "https://get.maestro.mobile.dev" | bash

# Correr flows
cd tests/app
maestro test flows/
```

## Uso

### QA completo de un cliente

```bash
./tools/run-qa.sh Soprole
```

Esto ejecuta: extrae config de MongoDB → genera checklist → corre Playwright.

### Generar checklist manual

```bash
python3 tools/checklist-generator.py --cliente Soprole -o QA/Soprole/2026-03-26/checklist.md
```

### Correr solo Playwright

```bash
cd tests/e2e
npx playwright test                    # Todos los tests
npx playwright test b2b/login.spec.ts  # Solo login
npx playwright test --headed           # Con browser visible
npx playwright show-report             # Ver reporte HTML
```

## Proceso QA cliente nuevo

Ver [playbook-qa-cliente-nuevo.md](playbook-qa-cliente-nuevo.md) para el paso a paso completo:

1. Generar checklist con `checklist-generator.py`
2. Correr Playwright (B2B automatizado)
3. Explorar B2B con Cowork (validación visual)
4. Testear APP en dispositivo
5. Documentar y escalar issues
6. Veredicto: LISTO / CON CONDICIONES / NO APTO

## Escalamiento de issues

| Tipo | Equipo | Canal Slack |
|---|---|---|
| Bug de código | Tech (Rodrigo/Diego C) | `#tech` |
| Datos incorrectos | Analytics (Diego F/Nicole) | `#datos` |
| Configuración | Tech | `#tech` |
| Integración ERP | Analytics + Tech | `#integraciones` |
| Contenido del cliente | CS (Max) → Cliente | `#pem` |

Templates en [templates/escalation-templates.md](templates/escalation-templates.md).

## Documentos clave

| Documento | Contenido |
|---|---|
| [qa-master-prompt.md](qa-master-prompt.md) | Casos de prueba Tier 1-3, fixtures, esquemas de datos, reglas |
| [plan-qa-b2b.md](plan-qa-b2b.md) | Estrategia 3 capas: E2E + unit tests + Cowork |
| [qa-app-strategy.md](qa-app-strategy.md) | Estrategia APP: smoke tests → dispositivo físico → monitoreo |
| [casos-prioritarios-diego.md](casos-prioritarios-diego.md) | 29 casos priorizados para hooks y servicios del B2B |
| [reporte-exploracion-repos.md](reporte-exploracion-repos.md) | Stack real de cada repo (APP, B2B, API) |
