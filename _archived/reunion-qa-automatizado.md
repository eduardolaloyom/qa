# Reunión QA Automatizado — Resultados

**Objetivo:** Entender el estado actual del equipo Tech y alinear cómo implementar tests automáticos en YOM.
**Asistentes:** Rodrigo (APP), Diego C (B2B), Lalo
**Fecha:** 25-03-2026
**Contexto:** Tenemos un documento con 7 flujos críticos y ~80 casos de prueba listos. Necesitamos saber qué existe hoy para decidir cómo avanzar.

---

## Bloque 1 — Estado actual

### Tests existentes

| Pregunta | APP (Rodrigo) | B2B (Diego) |
|---|---|---|
| ¿Tienen tests hoy? | No | Sí, pocos. Tests unitarios/componentes en GitHub Actions |
| ¿Qué librería usan? | Ninguna activa | GitHub Actions (unit tests de componentes) |
| ¿Tienen unit tests? | Se intentaron, fallaron (2h, caros, no detectaban bugs reales) | Sí, pocos. Diego los está expandiendo para cubrir más lógica |
| ¿Tienen integration tests? | No | No |
| ¿Tienen E2E? | No | Cypress instalado pero **roto** tras actualizar el front. Tenía solo: login, agregar carrito, borrar carrito |
| ¿Los tests corren en cada PR? | No | Sí (GitHub Actions) + Code Quality de GitHub (revisa redundancia/código, no funcionalidad) |

### Problema E2E del B2B (Diego)

- La página es lenta → tests dan **timeout** (esperan 5 seg max)
- Rendimiento varía por horario — mañanas más lentas (caché frío, nadie usa el front)
- Diego tenía **retry x4** configurado, pero igual fallaba
- E2E se demoraba **media hora** completo pegado a producción
- Tras actualizar versiones del front, Cypress se rompió y no lo ha podido retomar

### CI/CD

| Pregunta | APP | B2B |
|---|---|---|
| ¿CI/CD? | Nada automático | GitHub Actions (tests) + deploy automático |
| ¿Qué corre en pipeline? | Nada | Tests unitarios de código + Code Quality en PRs |
| ¿Staging? | No. Prueban en dev → prod con clientes específicos (Surtiventas, Softies, 5K, Éxito) | No formal. **tienda.yom.ai** funciona como staging informal (no productivo) |
| ¿Deploy a producción? | Play Store Internal Testing → producción. Rollback: 4h-2 días | Deploy automático. Rollback en 2 min. Deploy total ~30 min (incluye invalidar caché navegador) |

---

## Bloque 2 — Stack técnico

| Componente | Lo que asumía | Respuesta real |
|---|---|---|
| Backend | Node.js / Express | Mismo backend para B2B y APP (yom-api). Tiene sus propios tests (hooks, órdenes) |
| **B2B (tienda)** | Next.js / React | **Next.js** confirmado por Diego. 2 versiones: **nuevo** (clientes nuevos) y **antiguo** (tecnología obsoleta) |
| **Admin** | Next.js / React | Existe admin nuevo y antiguo. Diego dio acceso al nuevo |
| APP mobile | React Native | **React Native + Expo SDK 53 + TypeScript**. Java legacy como submodule Android (`yom-sales`) para Realm/SessionBridge. Sin testIDs en componentes RN |
| Base de datos | MongoDB | MongoDB (backend) + Realm (BD local offline en APP) |
| ORM / Driver | Mongoose o nativo | No se confirmó directamente |
| ¿Monorepo o repos separados? | No sabía | Repos separados. B2B tiene su repo. APP: `app-mobile` + `jumpsales` (submódulo Java) |
| API versión | REST v2 (api.youorder.me) | Confirmado. APP sincroniza 99% vía sync, 1% en línea |
| **Infra subdominios** | No sabía | **AWS Route 53** maneja subdominios (ej: soprole.youorder.me) |
| **Repo adicional** | No sabía | Existe repo `cloud-architecture` relevante para entender infra |

### Config por cliente (B2B)

- **Todo viene de MongoDB** — no hay ifs hardcodeados tipo `if soprole`
- Dominio → MongoDB → configuración del cliente
- Si hay problemas de datos/precios, por lo general **no es el B2B** sino la integración/backend
- Existe guía en Notion para activación de nuevo cliente B2B

### B2B nuevo vs antiguo

- **Nuevo**: para clientes que entran ahora. Tiene variantes, pagos por equipo, más features
- **Antiguo**: tecnología obsoleta, lento, no tiene features nuevas. No vale la pena testear

---

## Bloque 3 — Dolor y prioridades

### Bugs en producción

| Pregunta | APP (Rodrigo) | B2B (Diego) |
|---|---|---|
| ¿Bugs recurrentes? | Componentes visuales, interacciones, promociones | Prueban con un cliente y **rompen otro** sin darse cuenta |
| ¿Detectables con test? | Sí, con E2E/humo (no unit tests) | Sí — necesitan forma automática de verificar múltiples clientes |
| ¿Qué tan graves? | Riesgo alto (rollback lento Play Store) | Se arreglan rápido, no tan graves (rollback 2 min) |
| ¿Miedo a tocar? | APP en general por rollback | No tanto — pero romper un cliente al tocar otro es el riesgo |

### Áreas críticas

| Área | APP | B2B |
|---|---|---|
| Precios / Overrides / Escalas | 98% problemas de integración, no APP | Problemas de datos vienen de integración, no del front |
| Inyección al ERP | APP crea pedido, backend maneja | yom-api tiene tests propios para esto |
| Sync de datos | Crítico — si falla, datos desactualizados | No aplica igual — B2B lee directo |
| Promociones / Descuentos | Lo que más problemas trae | Depende de la integración |
| Login / Auth | Estable (ya en RN) | No se reportaron problemas |
| Carro de compras | Pendiente detallar | E2E viejo tenía agregar/borrar carrito |
| Config por cliente | Email → cliente → config → Realm | Dominio → MongoDB → config. Todo dinámico |
| **Stock** | Número de stock (actualiza cantidad) | Estado de stock (binario: hay/no hay). Depende de cómo integre el cliente |

### Detección de problemas

| Pregunta | APP | B2B |
|---|---|---|
| ¿Cómo detectan fallos en prod? | Manual, sin alertas automáticas | Manual. No hay monitoreo de que un cliente se rompió |
| ¿Monitoreo/alertas? | No | No |
| ¿Tiempo de detección? | Variable, alguien tiene que reportar | Variable, alguien tiene que reportar |

---

## Bloque 4 — Proceso de trabajo

| Pregunta | APP | B2B |
|---|---|---|
| Flujo de cambio | Desarrollo → Internal Testing (Play Store) → producción | Desarrollo → PR con Code Quality → merge → deploy automático |
| Code review | No detallado | Code Quality de GitHub (no funcional, solo código) |
| Feature flags | Variables en MongoDB | Variables en MongoDB |
| Config por cliente | Email → MongoDB → Realm | Dominio → MongoDB |
| Multi-tenant | Sí, una app para todos | Sí, un deploy para todos. Dominio determina tenant |

---

## Bloque 5 — Viabilidad y acuerdos

### Documento qa-master-prompt.md

- No se alcanzó a mostrar en ninguna de las dos reuniones
- Se reenfocó a entender el estado actual primero
- Pendiente: mostrar y validar con el equipo

### Decisiones tomadas

| Tema | Rodrigo (APP) | Diego (B2B) |
|---|---|---|
| ¿Qué tipo de tests primero? | Tests de humo con emulador, NO unit tests | E2E (reemplazar Cypress roto) + seguir expandiendo unit tests |
| ¿Herramientas? | Por definir (emulador Android) | Cypress existente o migrar a otra herramienta |
| ¿Usan Claude Code? | Sí, el equipo lo usa. Linear se implementa con CC | Sí |
| ¿Tiempo asignado? | No definido | No definido |
| ¿Plazo? | No definido | No definido |

### Accesos entregados por Diego

- **tienda.yom.ai** — cuenta de comercio (para navegar como cliente)
- **Admin B2B nuevo** — cuenta de administrador (para gestionar productos, config)
- **Repo B2B nuevo** — acceso al código fuente
- **Repo cloud-architecture** — pendiente revisar

### Próximos pasos acordados

- [x] Reunión con Rodrigo (APP) — 25/03 mañana
- [x] Reunión con Diego (B2B) — 25/03 tarde
- [ ] Explorar tienda.yom.ai con cuentas de admin y comercio
- [ ] Revisar repo B2B nuevo (estructura, tests existentes, Cypress roto)
- [ ] Revisar repo `cloud-architecture`
- [ ] Revisar guía Notion de activación nuevo cliente B2B
- [ ] Armar propuesta de plan QA B2B y enviar a Diego — semana del 31/03
- [ ] Siguiente checkpoint con Diego — semana del 31/03

---

## Clientes con B2B + APP

| Cliente | B2B | APP | Nota |
|---|---|---|---|
| Codelpa | Sí | Sí | Stock funciona distinto entre ambos |
| Caren | Próximamente | Próximamente | En proceso de configuración |

---

## Glosario rápido

| Término | Qué es |
|---|---|
| **Unit test** | Prueba una función aislada. Rápido (~ms). Ej: "calcular precio con override" |
| **Integration test** | Prueba componentes conectados (API + DB). Ej: "crear orden vía API" |
| **E2E test** | Prueba flujo completo en browser. Ej: "login → comprar → ver historial" |
| **Jest / Vitest** | Librerías para correr tests (como Excel es a planillas) |
| **Playwright** | Robot que abre Chrome y hace clicks como usuario real |
| **Cypress** | Similar a Playwright, es lo que Diego tenía instalado en B2B (actualmente roto) |
| **CI/CD** | Pipeline automático: corre tests en cada PR / deploy |
| **Fixture** | Datos falsos de prueba (comercio inventado, productos inventados) |
| **Mock** | Imitación de un servicio externo (simular ERP sin depender del cliente) |
| **Coverage** | % del código que está cubierto por tests |
| **Regression** | Bug que reaparece después de haber sido arreglado |
| **Staging** | Ambiente de prueba idéntico a producción pero sin datos reales |
| **Feature flag** | Interruptor para activar/desactivar funcionalidad por cliente |
| **Tenant** | Configuración específica de un cliente en sistema multi-tenant |
| **Route 53** | Servicio de AWS que maneja DNS/subdominios (ej: soprole.youorder.me) |
| **Code Quality** | Herramienta de GitHub que revisa calidad de código (no funcionalidad) |

---

*Documento actualizado post-reuniones — 25-03-2026*
