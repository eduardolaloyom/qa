# Sync QA Data

Extrae datos de MongoDB y regenera el fixture `clients.ts`. Valida qué necesita re-extracción antes de correr tests.

## Usage

```
/sync-qa-data
/sync-qa-data staging
/sync-qa-data production
/sync-qa-data staging --client sonrie
```

## Pasos

### 1. Adoptar rol
Adoptar el rol `data-pipeline-specialist` (ver `ai-specs/.agents/data-pipeline-specialist.md`).

### 2. Evaluar si es necesario re-extraer

Verificar:
- Fecha de modificación de `data/qa-matrix-staging.json`
- Si tiene < 7 días Y no hay cambios de config conocidos → preguntar si igual quiere re-extraer

```
📦 Estado del pipeline QA

qa-matrix-staging.json: {N} días de antigüedad ({FECHA})
clients.ts: {N} días de antigüedad ({FECHA})
Clientes en fixture: {N}

¿Re-extraer? (sí / no — usar el existente)
```

Si respuesta es "no" → saltar al Step 4.

### 3. Extraer datos

**Staging (default o `staging`):**
```bash
python3 data/mongo-extractor.py --env staging --output data/qa-matrix-staging.json
```

**Producción (`production`):**
```bash
python3 data/mongo-extractor.py --env production
# → escribe data/qa-matrix.json (gitignored)
```

**Cliente específico (`--client {slug}`):**
```bash
python3 data/mongo-extractor.py --env staging --client {slug} --output data/qa-matrix-staging.json
```

Si el script falla → mostrar el error completo y detener. No continuar con datos corruptos.

### 4. Regenerar clients.ts

**Desde staging:**
```bash
python3 tools/sync-clients.py --input data/qa-matrix-staging.json
```

**Desde producción:**
```bash
python3 tools/sync-clients.py
```

Verificar que `tests/e2e/fixtures/clients.ts` fue actualizado (fecha de modificación).

### 5. Validar el fixture generado

Chequear:
- Que no hay credenciales hardcodeadas en `clients.ts`
- Que el número de clientes es razonable (similar al anterior)
- Que los KEY_ALIASES están correctos (`surtiventas`, `sonrie-prod`)

```bash
grep -c "baseURL" tests/e2e/fixtures/clients.ts  # contar clientes
grep -n "password\|secret\|token" tests/e2e/fixtures/clients.ts  # detectar creds
```

Si detecta credenciales hardcodeadas → **detener y alertar** — no commitear.

### 6. Commit del matrix (solo staging)

`qa-matrix-staging.json` se commitea. `qa-matrix.json` es gitignored.

```bash
git add data/qa-matrix-staging.json tests/e2e/fixtures/clients.ts
git commit -m "chore(data): sync qa-matrix-staging + regenerate clients.ts"
git push
```

### 7. Resumen

```
✅ Pipeline sincronizado — {FECHA}

Extracción: {staging|production}
Clientes extraídos: {N}
clients.ts actualizado: {N} clientes ({N} staging, {N} producción)
KEY_ALIASES aplicados: {lista}
Commit: chore(data): sync qa-matrix-staging + regenerate clients.ts

Próximo paso: /run-playwright b2b
```

## Reglas

- **Nunca editar `clients.ts` manualmente** — siempre regenerar vía este comando
- **No commitear `qa-matrix.json`** — es gitignored por contener datos de producción
- **Si el extractor falla** → no regenerar `clients.ts` con datos incompletos
- Si `clients.ts` tiene credenciales → alertar inmediatamente y no commitear

## Archivos clave

- `data/mongo-extractor.py` — extractor MongoDB
- `tools/sync-clients.py` — generador de clients.ts
- `data/qa-matrix-staging.json` — output staging (commiteado)
- `data/qa-matrix.json` — output producción (gitignored)
- `tests/e2e/fixtures/clients.ts` — fixture auto-generado
- `ai-specs/.agents/data-pipeline-specialist.md` — rol a adoptar
