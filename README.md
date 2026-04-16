# QA — YOM

Suite de QA para la plataforma YOM (You Order Me): B2B web, APP mobile y Admin.

**Herramienta primaria: Cowork (claude.ai).** Playwright es regresión automatizada complementaria.

---

## Flujo completo de ejecución

```
1. Extraer config de MongoDB
   python3 data/mongo-extractor.py --full
   python3 tools/sync-clients.py
   → genera tests/e2e/fixtures/clients.ts (AUTO-GENERADO, no editar)

2. Sesión Cowork (claude.ai)
   → Pegar COWORK.md al inicio de la sesión
   → Ejecutar Modo A → B → C (si aplica) → D (si aplica)
   → Al final de cada modo: guardar HANDOFF

3. Guardar HANDOFF (Claude Code)
   "agrega modo {A/B/C/D} al archivo de sesión de {CLIENTE}"
   → escribe en QA/{CLIENTE}/{FECHA}/cowork-session.md

4. Generar reporte (Claude Code)
   /report-qa {CLIENTE} {FECHA}
   → genera QA/{CLIENTE}/{FECHA}/qa-report-{FECHA}.md
   → genera public/qa-reports/{CLIENTE}-{FECHA}.html
   → actualiza public/manifest.json
   → dashboard GitHub Pages se actualiza automáticamente

5. Playwright (opcional — regresión automatizada)
   cd tests/e2e
   npx playwright test --project={cliente} b2b/
   → resultado en playwright-report/index.html (local, no toca el dashboard)

6. Mejoras al proceso (si HANDOFF tiene Process improvements:)
   /qa-improve {CLIENTE} {FECHA}
   → propone tests de regresión, actualizaciones a COWORK.md, flags nuevos
```

---

## Herramientas y métricas

| Herramienta | Qué mide | Resultado |
|-------------|----------|-----------|
| **Cowork** (claude.ai) | Validación visual + flujos reales | Health Score 0–100 → dashboard |
| **Playwright** (terminal) | Regresión automatizada | % tests pasando → playwright-report/ |
| **Dashboard** (GitHub Pages) | Historial de reportes Cowork | Lee manifest.json |

> Cowork Health Score ≠ Playwright pass rate. Son métricas independientes.

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

## Comandos disponibles (Claude Code)

| Comando | Cuándo usarlo |
|---------|--------------|
| `/qa-plan-client {CLIENTE}` | Planificar QA completo para un cliente nuevo |
| `/run-playwright b2b` | Correr tests Playwright B2B y generar reporte |
| `/report-qa {CLIENTE} {FECHA}` | Generar reporte HTML desde sesión Cowork |
| `/qa-improve {CLIENTE} {FECHA}` | Aplicar mejoras al proceso sugeridas en la sesión |
| `/qa-coverage-analysis` | Ver gaps de cobertura por cliente |
| `/audit-maestro {FLOW}` | Auditar flow APP Maestro |

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
│   │   ├── b2b/                 # Specs: login, cart, prices, payment-documents...
│   │   ├── fixtures/            # clients.ts (AUTO-GENERADO), multi-client-auth.ts
│   │   └── playwright.config.ts
│   └── app/                     # Maestro flows APP Android
│       ├── flows/               # Flows por cliente
│       └── config/              # Config de ambiente
│
├── data/                        # mongo-extractor.py, qa-matrix.json, variables
├── tools/                       # run-qa.sh, sync-clients.py, checklist-generator.py
├── templates/                   # qa-report-template.md, escalation-templates.md
├── checklists/                  # Casos de prueba por categoría
├── QA/                          # Resultados: QA/{CLIENTE}/{FECHA}/
│
└── public/                      # Dashboard GitHub Pages
    ├── index.html               # Dashboard principal
    ├── manifest.json            # Índice unificado B2B + APP
    ├── qa-reports/              # HTML reports B2B
    └── app-reports/             # HTML reports APP
```

---

## Setup

### Requisitos

- Python 3.9+
- Node.js 20+
- MongoDB access (para `mongo-extractor.py`)
- Android Studio + Maestro (para APP — opcional)

### Credenciales

```bash
# Playwright — credenciales por cliente
cp tests/e2e/.env.example tests/e2e/.env
# Completar: BASTIEN_EMAIL, BASTIEN_PASSWORD, PRINORTE_EMAIL, etc.

# Maestro — APP
cp tests/app/config/config.example.yaml tests/app/config/config.yaml
```

### Instalar dependencias Playwright

```bash
cd tests/e2e
npm install
npx playwright install chromium
```

### Primer run Playwright

```bash
cd tests/e2e
npx playwright test b2b/login.spec.ts          # Solo login, todos los clientes
npx playwright test --project=bastien b2b/     # Solo Bastien, todos los specs B2B
npx playwright show-report                      # Ver reporte HTML
```

---

## Escalamiento de issues

| Severidad | Canal | Acción |
|-----------|-------|--------|
| P0 — flujo crítico roto | Slack `#engineering` | Escalar inmediatamente, detener QA |
| P1 — feature no funciona | Linear (etiqueta `qa`) | Crear ticket, continuar |
| P2/P3 — cosmético o menor | Reporte HTML | Anotar, no escalar |

Templates en [templates/escalation-templates.md](templates/escalation-templates.md).
