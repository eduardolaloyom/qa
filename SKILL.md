# Flujo de QA — Puesta en Marcha YOM

> Proceso operacional para validar que un cliente está listo para Rollout.
> Fase 8 del proceso PeM.

---

## Visión general

```
ANTES DE QA                          QA (este documento)                    DESPUÉS DE QA
─────────────                        ──────────────────                     ───────────────
✅ Levantamiento                     1. Pre-vuelo                           ✅ Capacitaciones
✅ Entrega de datos                  2. Accesos                             ✅ Rollout
✅ Kick Off                          3. Datos y catálogo
✅ Integraciones                     4. Flujos core
✅ Cuadratura                        5. Features del cliente
✅ Desarrollos                       6. Integraciones en vivo
✅ Configuraciones                   7. Triage y escalamiento
                                     8. Re-test y cierre
                                     9. Veredicto → Gate de Rollout
```

## Cómo ejecutar QA para un cliente

### Paso 1: Generar checklist

```bash
python3 qa/checklist-generator.py --cliente {NOMBRE} -o QA/{NOMBRE}/{FECHA}/checklist.md
```

Esto genera un checklist con **casos de prueba reales** para cada feature del cliente:
- ⚙️ Funcional, 📊 Datos, 🔀 Edge cases, 🔗 Integración, 🎨 Visual, 💼 Reglas de negocio

### Paso 2: Ejecutar el checklist

Seguir el checklist generado sección por sección:
1. Pre-vuelo → confirmar que todo está en pie
2. Accesos → login en B2B, Admin, APP
3. Flujos core → compra completa en B2B y APP
4. Features → caso por caso con el checklist
5. Integraciones → inyección ERP, sync, CronJobs
6. Transversales → consola, performance, UX

### Paso 3: Documentar issues

Cada issue con: ID, severidad, screenshot, pasos para reproducir.
Usar la taxonomía de `qa/references/issue-taxonomy.md`.

### Paso 4: Escalar

Copiar template de `qa/templates/escalation-templates.md`, rellenar y enviar por Slack:
- Bug → Tech (Rodrigo/Diego C)
- Datos → Analytics (Diego F/Nicole)
- Config → Tech
- Contenido → CS (Max) → Cliente
- Integración → Analytics + Tech

### Paso 5: Veredicto

Completar el Gate de Rollout al final del checklist:
- **LISTO** → Capacitaciones → Rollout
- **CON CONDICIONES** → Plan de resolución documentado
- **NO APTO** → Volver a fases previas

---

## Clientes disponibles

```bash
python3 qa/checklist-generator.py --list-clientes
```

---

## Archivos del stack

| Archivo | Qué hace |
|---|---|
| `qa/checklist-generator.py` | Genera checklist completo por cliente (260+ casos de prueba) |
| `qa/references/issue-taxonomy.md` | Severidades, categorías, matriz de escalamiento |
| `qa/templates/escalation-templates.md` | Mensajes pre-armados para Slack por equipo |
| `qa/templates/qa-report-template.md` | Template de reporte final |
| `qa-only/SKILL.md` | Auditoría rápida (30 min, solo observar) |
