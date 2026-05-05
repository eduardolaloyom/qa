# QA Scope Check

Lee el doc de alcance del cliente desde Google Drive y compara contra los tests existentes. Produce un gap report con features sin cobertura y sugiere tests nuevos.

## Uso

```
/qa-scope-check Caren
/qa-scope-check Cedisur
/qa-scope-check "PIL Andina"
```

## Pasos

1. **Buscar el doc de alcance en Google Drive**
   - Usar `mcp__claude_ai_Google_Drive__search_files` con query:
     `title contains 'Alcance' and title contains '{CLIENTE}' and title contains 'Yom'`
   - Si aparecen múltiples versiones (v1, v2, v3…) → tomar la de `modifiedTime` más reciente
   - Si no se encuentra → intentar búsqueda amplia: `fullText contains '{CLIENTE}' and fullText contains 'alcance'`
   - Si sigue sin encontrarse → indicar el nombre esperado del archivo y detener

2. **Leer el documento completo**
   - Usar `mcp__claude_ai_Google_Drive__read_file_content` con el `fileId` encontrado
   - Extraer tres secciones:
     - **Sección 3: Alcance Funcional — Features Existentes** → lista de features acordados
     - **Sección 4: Nuevos Desarrollos** → desarrollos custom que necesitan tests propios
     - **Sección 2.3: Webhooks** → eventos de integración que deben probarse

3. **Construir la lista de features del alcance**
   - Por cada sub-sección de la Sección 3 (Autenticación, Gestión de Comercios, Catálogo, Pedidos, etc.)
   - Extraer cada fila de feature con su descripción
   - Marcar los de Sección 4 como `custom` (desarrollos nuevos — mayor riesgo)
   - Output esperado: tabla `{Feature} | {Sección} | {Tipo: estándar/custom}`

4. **Escanear cobertura existente**
   - Leer `checklists/INDICE.md` → mapa de cobertura actual
   - Leer `tests/e2e/b2b/*.spec.ts` → specs B2B disponibles
   - Leer `tests/app/flows/` → flows Maestro del cliente (si existen)
   - Leer `qa-master-guide.md` Sección 6-8 → casos Tier 1-3 canónicos
   - Leer flags del cliente en `data/qa-matrix-staging.json` → para cruzar features con flags activos

5. **Cruzar alcance vs cobertura**
   Para cada feature del doc de alcance:
   - Buscar si existe test Playwright que lo cubra (por nombre de spec o comentario de caso ID)
   - Buscar si existe flow Maestro que lo cubra
   - Buscar si existe checklist que lo cubra
   - Buscar si existe caso en qa-master-guide.md (caso estándar cubierto automáticamente)
   - Clasificar: `✓ cubierto` / `⚠ solo manual` / `✗ sin cobertura` / `🆕 custom — sin test`

6. **Generar gap report**
   Output al console + guardar en `QA/{CLIENTE}/{DATE}/scope-gap-report.md`

## Output Format

```markdown
# Scope Gap Report — {CLIENTE} — {DATE}

**Doc de alcance:** Alcance_Implementacion_{CLIENTE}_Yom.docx (modificado: {fecha})

## Resumen
- Features en alcance: N
- Con cobertura automatizada: X (Y%)
- Solo cobertura manual/checklist: A
- Sin cobertura: B
- Desarrollos custom sin test: C

## Features con Cobertura ✓

| Feature | Sección | Test actual |
|---------|---------|-------------|
| Log In | Auth | login.spec.ts (C1-01) |
| Crear pedido | Pedidos | checkout.spec.ts (C2) |

## Gaps — Sin Cobertura Automatizada ✗

| Feature | Sección | Tipo | Acción sugerida |
|---------|---------|------|-----------------|
| Active Directory | Auth | estándar | Agregar spec: `auth-ad.spec.ts` (C1-06) |
| Manejo de leads | Comercios | estándar | Agregar a checklist manual si no es testeable vía B2B |
| [Feature custom] | Sección 4 | **custom** | Crear spec nuevo: `{feature}.spec.ts` |

## Desarrollos Custom — Alta Prioridad 🆕

Features de Sección 4 que son desarrollos nuevos y tienen mayor riesgo:

| Desarrollo | Descripción | Test sugerido |
|------------|-------------|---------------|
| [nombre] | [descripción] | spec: `{nombre}.spec.ts` + caso ID: {CLIENTE}-QA-{NNN} |

## Webhooks a Validar

| Evento | Cobertura actual | Acción |
|--------|-----------------|--------|
| order.created | checklist-webhooks.md | ✓ |
| payment.created | ✗ sin cobertura | Agregar a checklist-webhooks.md |

## Recomendaciones

**P0 — Crear antes del próximo ciclo QA:**
1. [feature sin cobertura crítico]

**P1 — Agregar esta semana:**
1. [feature importante sin test]

**P2 — Backlog:**
1. [feature menor o difícil de automatizar]
```

## Integración con otros comandos

- Este comando se ejecuta **al inicio de `/qa-plan-client {CLIENTE}`** para enriquecer el plan con gaps reales del alcance
- Los gaps detectados se agregan como sección extra en el plan generado
- Si hay desarrollos custom (Sección 4) sin test → el plan los marca como **P0 obligatorio**

## Documentos clave

- Google Drive: `Alcance_Implementacion_{CLIENTE}_Yom.docx`
- `checklists/INDICE.md` — índice de cobertura actual
- `qa-master-guide.md` — casos canónicos Tier 1-3
- `data/qa-matrix-staging.json` — flags activos del cliente
