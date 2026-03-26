# QA APP Mobile — Estrategia Ajustada
> Basado en reunión con Rodrigo Alliende — 2026-03-25

---

## CONTEXTO TÉCNICO CONFIRMADO

| Aspecto | Realidad |
|---|---|
| **Lenguaje** | Java (Android nativo) — grueso de la app. React Native — solo login hoy |
| **BD local** | Realm (offline-first). 99% datos vía sync, 1% en línea |
| **Backend** | Mismo que B2B (Node.js, MongoDB) |
| **Repos** | `app-mobile` (principal) + `jumpsales` (submódulo con código Java) |
| **Deploy** | Play Store → Internal Testing (grupo reducido) → Producción |
| **Rollback** | 4 horas a 2 días vía Play Store (vs 2 min en B2B) |
| **Config multi-tenant** | Email del usuario → identifica cliente → carga config desde MongoDB → Realm |

### Lo que NO funcionó antes
- **Tests unitarios:** Rodrigo los implementó, corrían 2 horas, eran caros, y no detectaban bugs reales
- **Razón:** Los bugs de la APP son en componentes visuales e interacciones, no en funciones aisladas
- **Decisión:** Descartar unit tests a corto plazo

### Lo que SÍ causa problemas
- Componentes visuales e interacciones (bugs principales)
- Promociones (más que precios base)
- Sync de datos: si backend manda data mala, APP la muestra tal cual (ej: Surtiventas/SFTP)
- 98% de problemas de precios/stock son de integración, no de la app

---

## ESTRATEGIA DE TESTING — 3 FASES

### Fase 1: Smoke Tests con Emulador (corto plazo)

**Objetivo:** Validar que los flujos críticos no se rompan antes de subir a Internal Testing.

**Herramienta sugerida:** [Maestro](https://maestro.mobile.dev/) o Appium con emulador Android.

**Cliente de prueba:** Crear un cliente en producción con datos fijos y consistentes:
- Productos siempre iguales (nombre, precio, stock)
- Comercios de prueba con config conocida
- Vendedor de prueba con comercios asignados

**Flujos a cubrir (prioridad):**

| # | Flujo | Qué valida | Criterio de éxito |
|---|---|---|---|
| 1 | **Login** | Ingreso con email → carga de config del cliente | Llega a pantalla principal con datos del cliente |
| 2 | **Sync inicial** | Descarga de datos tras login | Productos, precios y comercios visibles. Realm tiene datos |
| 3 | **Lista de comercios** | Vendedor ve sus comercios asignados | Comercios visibles, datos correctos |
| 4 | **Toma de pedido** | Agregar productos → confirmar pedido | Pedido creado, visible en historial |
| 5 | **Precios correctos** | Precio mostrado = precio esperado del cliente de prueba | Match exacto con datos fijos |
| 6 | **Promociones** | Descuento se aplica correctamente | Precio con promo = precio esperado |
| 7 | **Offline → Sync** | Crear pedido sin conexión → restaurar conexión | Pedido se sincroniza correctamente |

**Limitaciones conocidas del emulador:**
- Algunos bugs solo aparecen en dispositivo físico
- Cuando empiecen a haber demasiados falsos positivos de emulador → pasar a Fase 2

### Fase 2: Tests en Dispositivo Físico (mediano plazo)

**Objetivo:** Mayor confianza en los tests, eliminar falsos positivos del emulador.

**Opciones:**
1. **Celular físico conectado a CI** — Más barato, requiere hardware dedicado
2. **Servicio cloud de dispositivos** — Firebase Test Lab, BrowserStack, AWS Device Farm — Más caro pero escalable

**Mismos flujos de Fase 1**, pero ejecutados en dispositivos reales.

### Fase 3: Monitoreo Post-Deploy (paralelo)

**Objetivo:** Detectar problemas en producción antes de que los reporten los clientes.

| Qué monitorear | Cómo | Alerta |
|---|---|---|
| Crash rate | Firebase Crashlytics (si no lo tienen, implementar) | > X crashes/hora |
| Sync failures | Log de errores de sync en backend | Sync falla > 3 veces seguidas |
| Datos inconsistentes | Comparar precios Realm vs MongoDB para cliente de prueba | Diferencia detectada |
| Tiempo de sync | Medir duración de sync completo | > umbral definido |

---

## FLUJOS CRÍTICOS APP — AJUSTADOS

> Reemplazan los flujos V1 del qa-master-prompt.md para la APP.
> Se eliminaron los unit tests. Todo es smoke/integración/E2E con emulador o dispositivo.

### [APP-1] Login y Carga de Configuración

| ID | Caso | Acción en emulador | Resultado esperado |
|---|---|---|---|
| APP-1-01 | Login exitoso | Ingresar email y password del vendedor de prueba | Pantalla principal carga, datos del cliente visibles |
| APP-1-02 | Login con email inválido | Ingresar email que no existe | Mensaje de error, no crash |
| APP-1-03 | Login con password incorrecto | Ingresar password malo | Mensaje de error claro |
| APP-1-04 | Config del cliente se carga | Login exitoso → verificar config | Nombre del cliente, logo, productos del catálogo correctos |

### [APP-2] Sincronización de Datos

| ID | Caso | Acción en emulador | Resultado esperado |
|---|---|---|---|
| APP-2-01 | Sync inicial post-login | Login → esperar sync | Productos, precios, comercios cargados en Realm |
| APP-2-02 | Datos de productos correctos | Post-sync → navegar catálogo | Productos del cliente de prueba con precios esperados |
| APP-2-03 | Stock correcto | Post-sync → verificar stock | Stock matches con datos fijos del cliente de prueba |
| APP-2-04 | Sync manual (pull-to-refresh) | Forzar sync | Datos se actualizan sin error |
| APP-2-05 | Sync con conexión lenta | Throttle de red en emulador | Sync completa sin crash, puede demorar más |

### [APP-3] Navegación y Catálogo

| ID | Caso | Acción en emulador | Resultado esperado |
|---|---|---|---|
| APP-3-01 | Ver lista de comercios | Login como vendedor → ver comercios | Solo comercios asignados, datos correctos |
| APP-3-02 | Seleccionar comercio | Tap en comercio | Datos del comercio visibles, catálogo disponible |
| APP-3-03 | Ver catálogo de productos | Navegar catálogo | Productos con nombre, precio, imagen. Sin crashs |
| APP-3-04 | Buscar producto | Usar buscador | Resultados relevantes aparecen |
| APP-3-05 | Navegar categorías | Tap en categoría | Productos filtrados correctamente |

### [APP-4] Toma de Pedido

| ID | Caso | Acción en emulador | Resultado esperado |
|---|---|---|---|
| APP-4-01 | Agregar producto al carro | Seleccionar producto → agregar | Carro muestra producto, cantidad y total correcto |
| APP-4-02 | Modificar cantidad | Cambiar cantidad en carro | Total se recalcula |
| APP-4-03 | Eliminar producto del carro | Remover producto | Producto desaparece, total actualiza |
| APP-4-04 | Confirmar pedido | Carro válido → confirmar | Pedido creado, confirmación visible |
| APP-4-05 | Pedido aparece en historial | Post-confirmación → ir a historial | Pedido visible con estado correcto |
| APP-4-06 | Pedido con promoción | Producto con promo activa → agregar → confirmar | Precio descontado aplicado correctamente |

### [APP-5] Precios y Promociones

| ID | Caso | Acción en emulador | Resultado esperado |
|---|---|---|---|
| APP-5-01 | Precio base correcto | Ver producto del cliente de prueba | Precio = valor esperado (dato fijo) |
| APP-5-02 | Promoción activa visible | Producto con promo configurada | Descuento visible en catálogo y carro |
| APP-5-03 | Precio total del carro | Agregar múltiples productos | Total = suma correcta de precios individuales |
| APP-5-04 | Consistencia precio catálogo ↔ carro | Agregar producto → ver carro | Mismo precio en ambas vistas |

### [APP-6] Modo Offline

| ID | Caso | Acción en emulador | Resultado esperado |
|---|---|---|---|
| APP-6-01 | Navegar offline | Desactivar red → navegar catálogo | Datos de Realm visibles, app funcional |
| APP-6-02 | Crear pedido offline | Sin red → crear pedido completo | Pedido se guarda localmente |
| APP-6-03 | Sync post-offline | Restaurar red | Pedido offline se sincroniza al backend |
| APP-6-04 | No hay pérdida de datos | Offline → online → verificar | Todos los pedidos offline aparecen en historial |

### [APP-7] Cobranzas (registro contable)

| ID | Caso | Acción en emulador | Resultado esperado |
|---|---|---|---|
| APP-7-01 | Registrar cobranza | Ingresar monto de cobranza | Registro guardado correctamente |
| APP-7-02 | Ver historial de cobranzas | Navegar a cobranzas | Lista visible con montos y fechas |

> **Nota:** No involucra dinero real. Son registros contables que se pueden borrar sin impacto.

---

## CLIENTE DE PRUEBA — ESPECIFICACIÓN

Para que los tests de humo funcionen de forma determinista, se necesita un cliente en producción con datos fijos:

```
Nombre: test.youorder.me (o similar)
Productos: 10-20 productos con precios fijos y conocidos
Stock: siempre > 0 para todos los productos
Comercios: 3-5 comercios de prueba
Vendedor: 1 vendedor con todos los comercios asignados
Promociones: 1-2 promociones activas permanentes con descuento conocido
Config: Variables estándar, sin features experimentales
```

**Requisito crítico:** Los datos de este cliente NO deben modificarse por integraciones externas (sin sync con ERP real). Datos 100% controlados.

---

## QUÉ NO CUBRIR (POR AHORA)

| Área | Razón |
|---|---|
| Unit tests en Java/RN | Rodrigo los intentó, no funcionaron. Retomar cuando haya más RN |
| Tests de integración con ERP real | 98% de problemas de precios son de integración, pero eso se testea desde backend |
| Tests de pagos reales | No hay transferencias de dinero en la APP |
| Tests de rendimiento | Priorizar funcionalidad primero |
| Tests en iOS | No hay app iOS actualmente |

---

## PRÓXIMOS PASOS

- [ ] Definir con Rodrigo: ¿quién implementa los smoke tests? ¿Rodrigo? ¿Con apoyo?
- [ ] Crear el cliente de prueba en producción con datos fijos
- [ ] Elegir herramienta de automatización (Maestro vs Appium vs otra)
- [ ] Implementar los primeros 3 flujos (Login, Sync, Toma de pedido)
- [ ] Definir dónde corren los tests (CI local, GitHub Actions con emulador, otro)
- [ ] Reunión B2B con Diego para completar el cuadro (pendiente)

---

*Documento generado post-reunión QA Tests — 2026-03-25*
*Versión 1.0*
