# GitHub Pages Setup — QA Dashboard

## ✅ Configuración Completada

El dashboard de QA está configurado para publicarse automáticamente en GitHub Pages en cada push a `main`.

### 📍 URLs

- **Dashboard principal:** `https://{usuario}.github.io/qa`
- **Codelpa report:** `https://{usuario}.github.io/qa/codelpa/`
- **Surtiventas report:** `https://{usuario}.github.io/qa/surtiventas/`

### ⚙️ Cómo funciona

1. **Trigger:** Cada push a `main` o PR en rama `main`
2. **Tests:** GitHub Actions ejecuta Playwright E2E para Codelpa y Surtiventas en paralelo
3. **Reports:** Playwright genera HTML reports automáticamente
4. **Deploy:** Los reportes se publican a GitHub Pages

### 🔧 Configuración requerida en GitHub

Para que GitHub Pages funcione, debes:

1. **Ir a:** Settings → Pages (en la rama `main`)
2. **Build and deployment:**
   - Source: `GitHub Actions`
   - Workflow: `Playwright Tests → GitHub Pages`

```
Repo Settings → Pages → Source: GitHub Actions
```

3. **Esperar 1-2 min** a que GitHub desplegue la primera versión

### 📊 Estructura del Dashboard

```
public/
├── index.html              ← Dashboard principal
├── codelpa/
│   ├── index.html         ← Reporte Playwright (autogenerado)
│   ├── test-results.json  ← Data JSON
│   └── ...
└── surtiventas/
    ├── index.html         ← Reporte Playwright (autogenerado)
    ├── test-results.json  ← Data JSON
    └── ...
```

### 🚀 Ejecutar Localmente

Para ver los reportes sin push:

```bash
# Ejecutar tests
cd tests/e2e
npx playwright test --project=b2b b2b/codelpa.spec.ts

# Abrir reporte
npx playwright show-report
```

### 📈 Histórico de Reportes

El dashboard mantiene un histórico automático en `public/reports-history.json` con:
- Timestamp de cada ejecución
- Passed/Failed/Skipped counts
- Health score %
- URLs de reportes

Esto permite trackear la salud de los tests a lo largo del tiempo.

### ⚠️ Variables de entorno

El workflow usa estos envs para Codelpa/Surtiventas:

```yaml
# Codelpa
BASE_URL: https://beta-codelpa.solopide.me
ADMIN_URL: https://admin-codelpa.solopide.me

# Surtiventas
BASE_URL: https://surtiventas.solopide.me
ADMIN_URL: https://admin-surtiventas.solopide.me
```

Si cambian las URLs o credenciales, actualizar `.github/workflows/playwright.yml`

### 🔐 Secrets (si aplica)

Si necesitas agregar credenciales secretas:

```bash
# GitHub CLI
gh secret set CODELPA_PASSWORD --body "password"
```

Luego en el workflow:

```yaml
env:
  CODELPA_USER: ${{ secrets.CODELPA_USER }}
  CODELPA_PASS: ${{ secrets.CODELPA_PASSWORD }}
```

### 🐛 Debugging

Si los tests no se ejecutan:

1. **Revisar logs:** Actions → Workflow run → ver logs de cada job
2. **Errores comunes:**
   - Node version mismatch → actualizar `node-version` en workflow
   - Playwright cache issue → limpiar cache en GitHub Actions settings
   - Dependencies → ejecutar `npm ci` nuevamente

### 📝 Próximos pasos

- [ ] Configurar GitHub Pages en Settings → Pages (Source: GitHub Actions)
- [ ] Hacer push de cambios
- [ ] Esperar 1-2 min a que se depliegue
- [ ] Acceder a `https://{usuario}.github.io/qa`
- [ ] Compartir link con el equipo

---

**Dashboard está listo. Solo falta activar GitHub Pages en Settings.**
