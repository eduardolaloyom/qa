# Cleanup Repo

Limpia el repositorio QA de artefactos, archivos obsoletos y basura acumulada. Dos modos: rutinario (rápido, seguro) o profundo (auditoría completa con confirmación).

## Usage

```
/cleanup-repo
/cleanup-repo deep
```

## Pasos

### 1. Adoptar rol
Adoptar el rol `repo-cleanup-specialist` (ver `ai-specs/.agents/repo-cleanup-specialist.md`).

### 2. Modo rutinario (default)

Correr el script de limpieza automática:

```bash
bash tools/cleanup-repo.sh
```

Reportar el resultado:

```
🧹 Cleanup rutinario — {FECHA}

{output del script}

✓ Completado en {tiempo}s
```

Si no hubo cambios → responder "✅ Repo limpio — nada que eliminar."

Terminar aquí salvo que se pase `deep`.

### 3. Modo profundo (`/cleanup-repo deep`)

#### 3a. Limpieza rutinaria primero
Correr `bash tools/cleanup-repo.sh` igual que el modo default.

#### 3b. Auditoría de archivos raíz
Listar todos los `.md` en la raíz y verificar si están referenciados en `CLAUDE.md` como documentos activos. Candidatos a eliminar: los que no aparecen en CLAUDE.md y tienen más de 30 días sin modificarse.

#### 3c. Auditoría de ai-specs
Verificar que todos los agentes en `ai-specs/.agents/` y comandos en `ai-specs/.commands/` son QA-específicos. Candidatos a eliminar: cualquiera que no tenga relación con QA, Playwright, Maestro, o reportes.

#### 3d. Auditoría de public/
Verificar que todos los `.html` y `.json` en `public/` (raíz) están referenciados en `public/manifest.json` o son usados por el dashboard (`public/index.html`). Candidatos: archivos staging-*, accionables.html, grouped-report.html, weekly-status.json, etc.

#### 3e. Auditoría de data/
Verificar que no hay matrices de clientes separadas (`qa-matrix-{cliente}.json`) que sean redundantes con `qa-matrix.json` o `qa-matrix-staging.json`.

#### 3f. Auditoría de QA/
Listar carpetas vacías o con solo logs sin reporte asociado.

#### 3g. Presentar lista y confirmar

```
🔍 Auditoría profunda — {FECHA}

Candidatos a eliminar:

| Archivo | Razón | Riesgo |
|---------|-------|--------|
| {path} | {razón} | bajo/medio |
| ...

¿Eliminar todos? (sí / seleccionar / cancelar)
```

Esperar confirmación antes de `git rm`.

#### 3h. Ejecutar eliminaciones y commit

```bash
git rm {archivos confirmados}
git commit -m "chore: deep cleanup {FECHA} — {N} archivos obsoletos"
git push
```

### 4. Resumen final

```
─────────────────────────────────────────
Cleanup completado — {FECHA}

Rutinario:
  ✓ {N} .DS_Store eliminados
  ✓ test-results/ limpiado
  ✓ {N} screenshots > 30 días eliminados

Profundo (si aplica):
  ✓ {N} archivos obsoletos eliminados
  ✓ Commit: chore: {descripción}

Repo size antes: {X} archivos tracked
Repo size ahora: {Y} archivos tracked
─────────────────────────────────────────
```

## Reglas

- **Nunca eliminar** archivos en `QA/` con contenido, `public/qa-reports/`, `public/app-reports/`, `tests/e2e/`, `tools/`, `_archived/`
- **Siempre confirmar** en modo `deep` antes de `git rm`
- **Commit inmediato** después de cada limpieza con cambios tracked
- Si `git push` falla → `git pull --rebase` y reintentar

## Archivos clave

- `tools/cleanup-repo.sh` — script de limpieza rutinaria
- `public/manifest.json` — reportes activos en dashboard
- `CLAUDE.md` — documentos activos del repo
- `ai-specs/.agents/repo-cleanup-specialist.md` — rol a adoptar
