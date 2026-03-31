# Checklist QA — Deuda Técnica General

> Fuente: [Deuda Técnica — Notion](https://www.notion.so/protocolodesoporte/Deuda-T-cnica-19ad8139ba4e8061bb86cfd8db6f46fe)
> Fecha creación: 2026-03-27

---

## 1. Condiciones de carrera — Hilo de background (App)

> Problema: La app salta entre hilo UI e hilo de fondo en una misma acción, causando race conditions y dificultando el debug.

| # | Caso | Cómo validar | Plataforma | Estado |
|---|------|-------------|-----------|--------|
| BG-01 | Sync mientras se toma pedido | Iniciar sync manual mientras se agrega producto al carro → no debe perder items | App | PENDIENTE |
| BG-02 | Navegación rápida durante carga | Cambiar de comercio mientras carga catálogo → no crash, datos correctos | App | PENDIENTE |
| BG-03 | Doble tap en confirmar pedido | Tap rápido doble en confirmar → solo 1 pedido creado | App | PENDIENTE |
| BG-04 | Pérdida de conexión durante operación de fondo | Desconectar WiFi mientras sync en progreso → app no queda en estado inconsistente | App | PENDIENTE |
| BG-05 | Múltiples acciones concurrentes | Agregar producto + buscar + scroll simultáneo → UI no se congela | App | PENDIENTE |
| BG-06 | Estado de UI después de operación de fondo | Completar sync → UI refleja datos actualizados sin necesidad de refresh manual | App | PENDIENTE |

---

## 2. Migración MongoDB (cuando se ejecute)

> Problema: Subir versión de MongoDB antes de agosto. Requiere regresión completa.

| # | Caso | Cómo validar | Plataforma | Estado |
|---|------|-------------|-----------|--------|
| MG-01 | Queries de catálogo funcionan post-upgrade | Buscar productos → resultados correctos, tiempos similares | Backend | PENDIENTE |
| MG-02 | Aggregations de reportes no se rompen | Generar reporte de ventas → datos cuadran con pre-migración | Backend | PENDIENTE |
| MG-03 | Índices existentes siguen funcionando | Consultas que usan índices → no hay full scans nuevos | Backend | PENDIENTE |
| MG-04 | Datos de comercios intactos | Comparar muestra de 10 comercios pre/post migración | Backend | PENDIENTE |
| MG-05 | Integraciones ERP siguen funcionando | Ejecutar sync de ERP → datos correctos | Backend | PENDIENTE |
| MG-06 | Backups restaurables en nueva versión | Tomar backup → restaurar en versión nueva → datos ok | Backend | PENDIENTE |

---

## 3. Upgrade Node.js en microservicios (cuando se ejecute)

| # | Caso | Cómo validar | Plataforma | Estado |
|---|------|-------------|-----------|--------|
| ND-01 | API health-check responde post-upgrade | GET `/api/health-check` → 200 OK | Backend | PENDIENTE |
| ND-02 | Dependencias nativas compilan correctamente | npm install sin errores en nueva versión de Node | Backend | PENDIENTE |
| ND-03 | Crypto/hashing sigue funcionando | Login → tokens se generan correctamente | Backend | PENDIENTE |
| ND-04 | Streams y buffers (uploads) funcionan | Subir imagen de producto → se almacena correctamente | Backend | PENDIENTE |
| ND-05 | Performance no degrada | Benchmark de endpoints principales → tiempos <= pre-upgrade | Backend | PENDIENTE |

---

## 4. Migración a SSR — Admin y B2B (cuando se ejecute)

| # | Caso | Cómo validar | Plataforma | Estado |
|---|------|-------------|-----------|--------|
| SSR-01 | Primera carga muestra contenido (no flash blanco) | Abrir página → contenido visible antes de JS hydrate | Admin/B2B | PENDIENTE |
| SSR-02 | SEO metadata presente en HTML fuente | View source → title, description, OG tags presentes | B2B | PENDIENTE |
| SSR-03 | Navegación client-side sigue funcionando | Click en links internos → no full reload | Admin/B2B | PENDIENTE |
| SSR-04 | Auth redirect funciona en SSR | Acceder a ruta protegida sin sesión → redirect a login sin flash | Admin/B2B | PENDIENTE |
| SSR-05 | Datos dinámicos se hidratan correctamente | Catálogo SSR → precios coinciden post-hydration | B2B | PENDIENTE |
| SSR-06 | E2E existentes siguen pasando post-migración | Correr suite completa Playwright → mismos resultados | Admin/B2B | PENDIENTE |
| SSR-07 | Performance mejora (LCP, TTFB) | Lighthouse pre/post → LCP y TTFB mejoran o se mantienen | Admin/B2B | PENDIENTE |

---

## Prioridades

| Prioridad | Items | Cuándo ejecutar |
|-----------|-------|----------------|
| **Ahora** | PAG-* (pagos) y BG-* (race conditions) | Se pueden testear sobre el código actual |
| **Al migrar** | MG-* (MongoDB), ND-* (Node.js) | Cuando el equipo ejecute la migración |
| **Al migrar** | SSR-* (Server Side Rendering) | Cuando Admin o B2B pasen a SSR |