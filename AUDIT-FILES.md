# Auditoría: Archivos Necesarios vs Opcionales

## Status Actual
- **10 archivos modificados/creados**
- **6 NECESARIOS** (fix del login timeout)
- **4 OPCIONALES** (automation + validation avanzada)

---

## ✅ NECESARIOS (Sin estos, los tests no funcionan)

| Archivo | Motivo | Cambio |
|---------|--------|--------|
| `tests/e2e/fixtures/login.ts` | **CRÍTICO** - Helper con selectores robusos (.or fallbacks) | Nuevo |
| `tests/e2e/fixtures/auth.ts` | Usa loginHelper en vez de getByLabel directo | Modificado |
| `tests/e2e/b2b/codelpa.spec.ts` | Usa loginHelper en lugar de login() local | Modificado |
| `tests/e2e/b2b/surtiventas.spec.ts` | Usa loginHelper en lugar de login() local | Modificado |
| `tests/e2e/b2b/config-validation.spec.ts` | Usa loginHelper en lugar de loginIfNeeded() local | Modificado |
| `tests/e2e/b2b/login.spec.ts` | Usa loginHelper en 4 ocurrencias inline | Modificado |

**Razón:** Sin login.ts con fallbacks, todos los tests fallan con timeout (getByLabel('Correo') no existe en todos los formularios).

---

## 🟡 OPCIONALES (Fase 2: automation + enrichment de tests)

| Archivo | Propósito | Impacto si NO se usa |
|---------|-----------|-------------------|
| `tools/sync-clients.py` | Auto-genera clients.ts desde qa-matrix.json | clients.ts sigue sendo manual/hardcodeado |
| `data/mongo-extractor.py` | Agrega yom-promotions + b2b-marketing | No extrae coupons/banners (solo variables ahora) |
| `tests/e2e/b2b/mongo-data.spec.ts` | Valida datos reales de Mongo en tests | No existe validación de datos reales (solo config) |
| `.env.example` | Documenta URIs por database | Documentación clara (no afecta tests) |

**Razón:** Estos archivos son para enriquecer el pipeline, pero los tests corren sin ellos (aunque sin validación de datos reales de Mongo).

---

## Recomendación

**Ahora:** Ejecutar tests con archivos NECESARIOS para ver:
- ✅ Login funciona (loginHelper con fallbacks)
- ✅ config-validation.spec.ts detecta feature flags
- ✅ Cualquier otro bug de frontend

**Después (Fase 2):** Activar opcionales cuando MongoDB URIs estén listos:
1. Extender mongo-extractor.py para full data extraction
2. Ejecutar sync-clients.py para auto-generar clients.ts
3. Ejecutar mongo-data.spec.ts para validar datos reales

---

## Verificación Rápida

```bash
# 1. Compilar todos los tests
cd tests/e2e && npx playwright test --list --reporter=list

# 2. Ejecutar config-validation (12 tests, 2 clientes x 6 flags)
npx playwright test config-validation.spec.ts

# 3. Ejecutar login tests (C1-01, C1-02, etc.)
npx playwright test login.spec.ts

# 4. Ver qué falla y por qué
# (credenciales, network, frontend bugs)
```

