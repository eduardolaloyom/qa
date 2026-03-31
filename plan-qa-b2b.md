# Plan QA B2B — YOM

**Fecha:** 25-03-2026
**Autor:** Lalo Jimenez
**Estado:** Borrador — pendiente validar con Diego (semana 31/03)

---

## Contexto

El B2B de YOM es una plataforma e-commerce multi-tenant en **Next.js** donde cada cliente accede vía subdominio (ej: `soprole.youorder.me`). La configuración por cliente viene 100% de MongoDB — no hay lógica hardcodeada por cliente.

### Problema principal
- Prueban con un cliente y **rompen otro sin darse cuenta**
- No hay forma automática de verificar múltiples clientes después de un cambio
- Los E2E existentes (Cypress) están **rotos** desde la última actualización del front
- Los unit tests tienen poca cobertura (Diego los está expandiendo)
- No hay monitoreo ni alertas de que algo se rompió en producción

### Qué existe hoy

| Capa | Estado |
|---|---|
| Unit tests / componentes | Pocos, en expansión. Corren en GitHub Actions |
| Code Quality (GitHub) | Activo en PRs. Revisa código, no funcionalidad |
| E2E (Cypress) | Corre cada 4h en CI contra soprole.solopide.me. Cobertura limitada (login + carrito). Problemas de timeout por lentitud del front |
| E2E (Playwright) | **Complementa Cypress**. 7 specs, 74 tests. Multi-cliente, precios, config validation. Corre manual desde este repo |
| Staging | No formal. tienda.yom.ai funciona como staging (no productivo) |
| Monitoreo producción | No existe |

> **Nota (27-03-2026):** Cypress es el E2E oficial en CI del repo B2B. Playwright lo complementa desde este repo QA con cobertura multi-cliente y validación de config. No se reemplaza Cypress — ambos conviven.

---

## Estrategia: 3 capas (Cowork primero)

> **Decisión (30-03-2026):** Cowork es la herramienta primaria de QA. Simula interacción humana real, valida que la config del cliente se vea correctamente. Playwright es complementario para regresión automatizada. Tests unitarios no son foco de QA — son dominio de Diego. Fuente: reunión QA con Diego.

### Capa 1 — E2E automatizado (complementar Cypress con Playwright)

**Objetivo:** Detectar que un cambio no rompe la funcionalidad en múltiples clientes.

**Herramienta:** Playwright (complementa Cypress existente en CI)
- Cypress corre cada 4h en CI del repo B2B → cobertura base de login + carrito
- Playwright corre desde este repo QA → cobertura multi-cliente, precios, config validation
- Mejor manejo de timeouts y reintentos nativos (resuelve el problema de lentitud)
- `auto-waiting` — espera automáticamente a que elementos estén listos, sin timeouts fijos de 5 seg

**Entorno de pruebas:** tienda.yom.ai (staging informal)

**Flujos iniciales (en orden de prioridad):**

| # | Flujo | Qué valida | Por qué primero |
|---|---|---|---|
| 1 | Login | Acceder con credenciales válidas, ver catálogo | Puerta de entrada. Si no funciona, nada más importa |
| 2 | Catálogo + búsqueda | Ver productos, filtrar, buscar | Validar que los datos de MongoDB se renderizan correctamente |
| 3 | Carrito | Agregar producto, modificar cantidad, eliminar | Diego ya tenía esto en Cypress — migrar a Playwright |
| 4 | Checkout / crear pedido | Completar flujo de compra | Flujo crítico de negocio |
| 5 | Precios | Verificar que precios mostrados coincidan con config | Es donde más se rompe según Rodrigo |

**Estrategia multi-cliente:**
- Ejecutar los mismos tests en **múltiples subdominios** (parametrizado)
- Empezar con tienda.yom.ai, luego agregar 1-2 clientes reales como validación
- Detecta automáticamente si un cambio rompe un cliente específico

**Configuración de timeouts (resolver problema actual):**
```
- Timeout por acción: 30 seg (no 5 seg como tenía Cypress)
- Retry por test: 2 intentos
- Ejecutar en horario de menor carga (tarde/noche) para evitar lentitud matutina
```

**Entregable:** Suite de Playwright con 5 flujos corriendo en GitHub Actions en cada PR.

---

### Capa 2 — Tests unitarios / componentes (complementar lo de Diego)

**Objetivo:** Mantener la lógica de negocio en el tiempo. "Declaración de intenciones" — si cambias algo, te avisa qué rompiste.

**Estado:** Diego ya está expandiendo cobertura. No intervenir demasiado aquí — es su dominio.

**Complemento desde QA:**
- Identificar los componentes/funciones críticas del `qa-master-prompt.md` que aplican a B2B
- Priorizar tests para lógica de precios, overrides, escalas
- Proponer casos de prueba específicos (datos de entrada + resultado esperado)

**Flujos del qa-master-prompt.md relevantes para B2B:**

| Flujo | Aplica a B2B | Tests |
|---|---|---|
| C1 — Login | Sí | 10 |
| C2 — Flujo de compra | Sí | 15 |
| C3 — Cálculo de precios | Sí (parcial, depende de integración) | 16 |
| C4 — Inyección al ERP | No directo (es backend/yom-api) | — |
| C5 — Canasta base | Sí | 8 |
| C6 — Sync de datos | No directo (B2B lee de MongoDB) | — |
| V1 — Vendedor APP | No (solo APP) | — |

**Entregable:** Lista de casos de prueba prioritarios para que Diego incorpore en sus unit tests.

---

### Capa 3 — QA operacional con Claude Cowork (PRIMARIA)

**Objetivo:** Validación funcional "como humano" usando IA. Es la capa principal: valida que lo que el equipo configura se vea y funcione correctamente desde la perspectiva del usuario.

**Cómo funciona:**
1. Cowork se conecta a tienda.yom.ai (o subdominio de cliente)
2. Ejecuta flujos funcionales como lo haría un usuario real
3. Valida contra la matriz de variables de MongoDB por cliente
4. Reporta diferencias, errores visuales, o funcionalidades rotas

**Ventajas sobre E2E puro:**
- Detecta problemas visuales (E2E solo valida DOM/datos)
- Puede verificar cosas que dependen de config específica del cliente
- No requiere escribir código — se configura con prompts
- Funciona en paralelo con desarrollo, sin bloquear PRs

**Flujos a validar:**
- Mismos 5 de Capa 1, pero con verificación visual
- Agregar: verificar que precios/productos coincidan con lo configurado en admin
- Agregar: verificar variantes, pagos por equipo, features específicos de clientes nuevos

**Entregable:** Skill de Cowork que ejecuta validación funcional de B2B por cliente.

---

## Orden de ejecución

| Fase | Qué | Quién | Cuándo |
|---|---|---|---|
| **Fase 0** | Explorar tienda.yom.ai, revisar repos, entender estructura | Lalo | Semana 25-28/03 |
| **Fase 1** | Capa 3 — QA con Cowork en tienda.yom.ai | Lalo | Semana 31/03 |
| **Fase 2** | Capa 1 — Playwright E2E (login + carrito, migrando de Cypress) | Lalo + Diego | Semana 07/04 |
| **Fase 3** | Capa 1 — Expandir E2E (checkout, precios, multi-cliente) | Lalo + Diego | Semana 14/04 |
| **Fase 4** | Capa 2 — Casos de prueba unitarios para Diego | Lalo (define) + Diego (implementa) | Continuo |

### Por qué Capa 3 antes que Capa 1

- No requiere tocar código ni repos — se puede hacer ya
- Genera valor inmediato (detecta problemas hoy)
- Sirve como exploración para entender los flujos antes de escribir E2E
- Los E2E requieren entender bien el repo y la estructura del front

---

## Dependencias y riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| tienda.yom.ai no tiene productos/datos suficientes | Tests no son realistas | Pedir a Diego que cargue datos representativos |
| Lentitud del front causa timeouts en E2E | Tests fallan intermitentemente | Playwright auto-waiting + timeouts de 30 seg + retry x2 |
| Config por cliente en MongoDB es compleja | Difícil parametrizar tests multi-cliente | Empezar con tienda.yom.ai, luego generalizar |
| Diego no tiene tiempo para apoyar E2E | Avance lento en Capa 1 | Lalo hace la mayor parte, Diego valida |
| B2B antiguo sigue activo | ¿Hay que testearlo? | No — foco solo en B2B nuevo. Antiguo está en sunset |

---

## Métricas de éxito

| Métrica | Hoy | Meta fase 2 | Meta fase 3 |
|---|---|---|---|
| Flujos E2E automatizados | 0 (Cypress roto) | 3 (login, catálogo, carrito) | 5 (+ checkout, precios) |
| Clientes validados por E2E | 0 | 1 (tienda.yom.ai) | 3 (+ 2 clientes reales) |
| Tiempo de detección de bug | Horas/días (manual) | Minutos (en PR) | Minutos (en PR) |
| Cobertura unit tests | Baja (Diego expandiendo) | +10 casos críticos | +20 casos críticos |
| QA funcional Cowork | No existe | 5 flujos por cliente | 5 flujos x N clientes |

---

## Siguiente paso inmediato

1. **Esta semana (25-28/03):** Explorar tienda.yom.ai con las cuentas de admin y comercio. Entender qué datos hay, qué flujos funcionan, qué se ve.
2. **Revisar repos:** B2B nuevo (código, tests de Diego, Cypress roto) + cloud-architecture.
3. **Semana 31/03:** Tener Cowork validando flujos en tienda.yom.ai + borrador de suite Playwright.
4. **Checkpoint con Diego:** Semana 31/03 — mostrar avance y validar plan.

---

*Plan QA B2B — Borrador v1 — 25-03-2026*
