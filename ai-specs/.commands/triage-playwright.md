# Triage Playwright

Analiza los fallos del último run de Playwright, corrobora cada uno y actúa: crea ticket en Linear, parchea el spec, o descarta.

## Usage

```
/triage-playwright
/triage-playwright 2026-04-16
/triage-playwright bastien
```

## Pasos

### 1. Adoptar rol
Adoptar el rol `playwright-failure-analyst` (ver `ai-specs/.agents/playwright-failure-analyst.md`).

### 2. Cargar resultados
- Si se pasa fecha → leer `public/history/{FECHA}.json`
- Si no → leer el archivo más reciente en `public/history/`
- Si se pasa cliente → filtrar `failure_groups` por ese cliente

Extraer:
- `failure_groups` → lista de fallos clasificados
- `stats`: total, passed, failed
- Fecha del run

Si no hay fallos (`failed == 0`) → responder "✅ Sin fallos en el último run de {FECHA}" y terminar.

### 3. Mostrar resumen inicial

```
🔍 Triage Playwright — {FECHA}
{total} tests · {passed} ✅ · {failed} ❌ · {flaky} ⚠️

Fallos a triagear:
1. [bug]      {razón} — {clientes afectados}
2. [ambiente] {razón} — {clientes afectados}
3. [flaky]    {razón} — {clientes afectados}
```

### 4. Triagear cada fallo (uno por uno)

Para cada grupo en `failure_groups` (orden: bug → ux → ambiente → flaky):

#### 4a. Mostrar contexto del fallo
```
─────────────────────────────────────────
Fallo {N}/{total}: [{CATEGORÍA}]
Razón: {reason}
Tests afectados: {count} ({tests[0]}, ...)
Clientes: {clients}
Acción sugerida: {action}
Screenshot: public/data/{screenshot si existe}
─────────────────────────────────────────
```

Si hay screenshot → mostrarlo con Read tool.

#### 4b. Decidir acción según categoría

**Si `bug` o `ux` (owner: dev):**
- Leer el spec afectado para confirmar que el test es correcto
- Si el test es correcto → proponer crear ticket Linear:
  ```
  Crear ticket Linear:
  Título: [QA] {razón corta} — {cliente}
  Descripción: {action} | Run: {fecha} | Tests: {lista}
  ¿Crear? (sí/no/skip)
  ```
- Si el test es incorrecto → ir a flujo "reescribir"

**Si `ambiente` (owner: qa):**
- Leer el spec afectado
- Identificar selector o timeout problemático
- Evaluar si el método es el problema o si hay una forma más robusta de validar lo mismo
- Proponer las opciones disponibles:
  ```
  Opciones para {test}:

  A) Parchear selector actual:
     - {línea actual}
     + {línea corregida}

  B) Método alternativo (más robusto):
     {descripción del método alternativo}
     Ej: interceptar /api/coupon en vez de buscar botón en UI

  C) Derivar a Cowork — feature visual que Playwright no captura bien

  ¿Qué hacemos? (a/b/c/skip)
  ```

**Si `flaky`:**
- Mostrar lista de tests flaky
- No crear ticket ni parchear
- Proponer annotation `.info()` para monitoreo:
  ```
  ⚠️ {count} tests flaky — pasaron en retry, no son bugs confirmados
  Monitorear en próximos runs. ¿Agregar annotation? (sí/no/skip)
  ```

#### 4c. Ejecutar acción aprobada
- **Crear ticket**: usar Linear API con `LINEAR_API_KEY` del `.env`
- **Parchear spec**: editar el archivo directamente con Edit tool
- **Skip**: pasar al siguiente fallo

### 5. Resumen final

```
─────────────────────────────────────────
Triage completado — {FECHA}

Acciones tomadas:
✓ Ticket Linear creado: {título} → {url}
✓ Spec parcheado: {archivo} — {descripción del cambio}
⏭ Saltado: {razón}
⚠️ Flaky monitoreados: {count}

Próximo paso: correr los tests parcheados para verificar
npx playwright test --grep "{tests parcheados}"
─────────────────────────────────────────
```

## Reglas

- **Máximo 1 ticket por grupo de fallo** — no crear duplicados por cada test del grupo
- **Buscar primero en Linear** si ya existe un ticket abierto para el mismo fallo antes de crear uno nuevo
- **No parchear specs flaky** — solo bugs confirmados (unexpected, no flaky)
- **Siempre leer el spec** antes de proponer un patch — no asumir qué hay que cambiar
- Si hay más de 5 fallos → priorizar los de categoría `bug` primero

## Archivos clave

- `public/history/` — resultados clasificados post-run
- `public/data/` — screenshots de fallos
- `tests/e2e/b2b/` — specs a parchear
- `ai-specs/.agents/playwright-failure-analyst.md` — rol a adoptar
