# QA Checklist — Soprole
**Fecha:** 2026-03-25  
**Features activas:** 84 (39 B2B, 50 APP, 8 Admin)  
**Requieren integración:** 0  
**Casos de prueba:** 232

**Tipos de prueba:**  
⚙️ Funcional — ¿funciona? · 📊 Datos — ¿datos correctos? · 🔀 Edge case — ¿qué pasa si...? · 🔗 Integración — ¿ERP conectado? · 🎨 Visual — ¿se ve bien? · 💼 Regla de negocio — ¿lógica comercial correcta?

---

## 1. Pre-vuelo

| # | Verificación | Cómo validar | ✓ |
|---|---|---|---|
| 1 | Catálogo cargado | Admin → Productos: hay productos del cliente | ☐ |
| 2 | Categorías configuradas | B2B → Navegación: categorías visibles | ☐ |
| 3 | Precios correctos | Comparar 5 productos con fuente del cliente | ☐ |
| 4 | Branding aplicado | B2B: logo, colores, favicon del cliente | ☐ |
| 5 | Usuarios de prueba | Tener credenciales: comercio + admin + vendedor | ☐ |
| 6 | Integraciones activas | Confirmar con Analytics — 0 features requieren integración | ☐ |
| 7 | Variables de entorno | Confirmar con Tech que están configuradas | ☐ |

---

## 2. Accesos

| # | Test | Herramienta | Pasos | ✓ |
|---|---|---|---|---|
| 1 | Login B2B | B2B | Ir a soprole.youorder.me → credenciales comercio | ☐ |
| 2 | Login Admin | Admin | Ir a admin.youorder.me → credenciales admin | ☐ |
| 3 | Login APP | APP | Abrir app → credenciales vendedor | ☐ |
| 4 | Cambio de contraseña | B2B | Flujo 'olvidé mi contraseña' → email → reset | ☐ |

---

## 3. Flujos core

### 3.1 Flujo de compra B2B

```
Catálogo → Seleccionar producto → Agregar al carro → Revisar carro → Crear pedido → Confirmación
```

| # | Paso | Qué verificar | ✓ |
|---|---|---|---|
| 1 | Catálogo | Productos visibles, navegables, con precio | ☐ |
| 2 | Detalle producto | Precio, descripción, imagen, botón agregar | ☐ |
| 3 | Agregar al carro | Feedback visual, contador actualiza | ☐ |
| 4 | Carro de compras | Items, cantidades, precios, total correcto | ☐ |
| 5 | Modificar carro | Cambiar cantidad, eliminar item, total recalcula | ☐ |
| 6 | Crear pedido | Botón funciona, no permite doble click | ☐ |
| 7 | Confirmación | Resumen del pedido, número de orden | ☐ |
| 8 | Historial | Pedido aparece en lista con estado correcto | ☐ |

### 3.2 Flujo de compra APP

| # | Paso | Qué verificar | ✓ |
|---|---|---|---|
| 1 | Seleccionar comercio | Lista visible, se puede elegir | ☐ |
| 2 | Tomador de pedidos | Catálogo del comercio carga | ☐ |
| 3 | Agregar productos | Cantidad, feedback visual | ☐ |
| 4 | Confirmar pedido | Resumen correcto, confirmación | ☐ |
| 5 | Historial | Pedido aparece con estado | ☐ |

---

## 4. Features del cliente — Casos de prueba

### Venta

#### Agregar fecha despacho (APP, B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Calendario aparece en checkout | ⚙️ funcional | ☐ |
| 2 | B2B | Solo fechas disponibles son seleccionables (deliveryDays del comercio) | 💼 negocio | ☐ |
| 3 | B2B | Fecha seleccionada se refleja en el pedido creado | ⚙️ funcional | ☐ |
| 4 | APP | Variable enableAskDeliveryDate activa → calendario en observaciones | 🔗 integración | ☐ |
| 5 | APP | Fecha seleccionada viaja con el pedido | ⚙️ funcional | ☐ |

#### Búsqueda de comercios (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Feature visible y accesible | ⚙️ funcional | ☐ |
| 2 | APP | Funcionalidad principal opera correctamente | ⚙️ funcional | ☐ |

#### Búsqueda de productos (APP, B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Buscar por nombre exacto: producto aparece primero | ⚙️ funcional | ☐ |
| 2 | B2B | Buscar por SKU: producto encontrado | ⚙️ funcional | ☐ |
| 3 | B2B | Buscar término parcial: resultados relevantes | ⚙️ funcional | ☐ |
| 4 | B2B | Buscar término inexistente: mensaje 'sin resultados', no error | 🔀 edge | ☐ |
| 5 | B2B | Buscar con caracteres especiales (ñ, tildes): funciona correctamente | 🔀 edge | ☐ |
| 6 | APP | Búsqueda en APP retorna mismos resultados que B2B | 📊 datos | ☐ |

#### Carro de compras (B2B, APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Agregar producto: carro actualiza contador y total | ⚙️ funcional | ☐ |
| 2 | B2B | Modificar cantidad: total recalcula correctamente | ⚙️ funcional | ☐ |
| 3 | B2B | Eliminar producto del carro: se remueve y total actualiza | ⚙️ funcional | ☐ |
| 4 | B2B | Carro vacío: mensaje descriptivo, no pantalla en blanco | 🔀 edge | ☐ |
| 5 | B2B | Carro con producto sin stock: muestra aviso (si stock integrado) | 🔀 edge | ☐ |
| 6 | B2B | Carro persiste al navegar entre páginas | ⚙️ funcional | ☐ |
| 7 | B2B | Carro persiste al cerrar y reabrir sesión | 🔀 edge | ☐ |

#### Catálogo (B2B, APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Abrir catálogo: productos visibles con nombre, precio e imagen | ⚙️ funcional | ☐ |
| 2 | B2B | Navegar por categorías: cada categoría muestra productos relevantes | ⚙️ funcional | ☐ |
| 3 | B2B | Producto sin imagen: muestra placeholder, no quiebra layout | 🔀 edge | ☐ |
| 4 | B2B | Catálogo con +500 productos: scroll fluido, paginación/infinite scroll funciona | 🔀 edge | ☐ |
| 5 | APP | Catálogo filtra por portafolio del vendedor (si configurado) | 💼 negocio | ☐ |
| 6 | APP | Catálogo funciona offline (muestra última sincronización) | 🔀 edge | ☐ |
| 7 | Admin | Productos en Admin coinciden con lo que muestra B2B | 📊 datos | ☐ |

#### Compartir el pedido (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Botón compartir visible en detalle de pedido | ⚙️ funcional | ☐ |
| 2 | APP | Compartir genera link o contenido legible | ⚙️ funcional | ☐ |

#### Compartir la sugerencia (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Botón compartir en sugerencia de productos | ⚙️ funcional | ☐ |
| 2 | APP | Contenido compartido incluye productos sugeridos | ⚙️ funcional | ☐ |

#### Crear pedido (APP, B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Flujo completo: catálogo → producto → carro → checkout → confirmación | ⚙️ funcional | ☐ |
| 2 | B2B | Pedido con 1 solo producto: se crea correctamente | ⚙️ funcional | ☐ |
| 3 | B2B | Pedido con 20+ productos: todos aparecen en resumen y confirmación | 🔀 edge | ☐ |
| 4 | B2B | Pedido con cantidad 0 o negativa: no permite crear | 🔀 edge | ☐ |
| 5 | B2B | Doble click en 'crear pedido': no genera pedido duplicado | 🔀 edge | ☐ |
| 6 | B2B | Pedido aparece en historial inmediatamente después de crear | ⚙️ funcional | ☐ |
| 7 | APP | Crear pedido desde tomador: seleccionar comercio → productos → confirmar | ⚙️ funcional | ☐ |
| 8 | APP | Crear pedido offline: se encola y envía al recuperar conexión | 🔀 edge | ☐ |

#### Cupón de descuento (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Campo para ingresar cupón visible en checkout | ⚙️ funcional | ☐ |
| 2 | B2B | Cupón válido: descuento se aplica al total | ⚙️ funcional | ☐ |
| 3 | B2B | Cupón inválido: mensaje de error claro | 🔀 edge | ☐ |
| 4 | B2B | Cupón expirado: mensaje de error claro | 🔀 edge | ☐ |
| 5 | B2B | Cupón ya usado (si uso único): rechazado | 🔀 edge | ☐ |
| 6 | Admin | Crear cupón: fecha inicio, fin, tipo descuento, monto | ⚙️ funcional | ☐ |

#### Dashboards (Metabase)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | Admin | Metabase dashboards accesibles | ⚙️ funcional | ☐ |
| 2 | Admin | Datos actualizados (no de hace semanas) | 📊 datos | ☐ |

#### Detalle del producto (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Muestra: nombre, descripción, precio, imagen, especificaciones | ⚙️ funcional | ☐ |
| 2 | APP | Producto sin imagen: muestra placeholder | 🔀 edge | ☐ |
| 3 | APP | Producto sin descripción: no muestra campo vacío | 🔀 edge | ☐ |

#### Edición de store (B2B, Admin)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Logo del cliente visible en header | 🎨 visual | ☐ |
| 2 | B2B | Colores del cliente aplicados (primario, secundario) | 🎨 visual | ☐ |
| 3 | B2B | Favicon del cliente en pestaña del browser | 🎨 visual | ☐ |
| 4 | Admin | Tienda → personalización refleja lo que se ve en B2B | 📊 datos | ☐ |

#### Escalones obligados (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Producto con escalón=6: solo permite comprar en múltiplos de 6 | 💼 negocio | ☐ |
| 2 | B2B | Intentar cantidad no múltiplo: corrige o muestra error | 🔀 edge | ☐ |

#### Exportación de datos (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Exportar datos: archivo generado | ⚙️ funcional | ☐ |
| 2 | APP | Datos exportados completos y correctos | 📊 datos | ☐ |

#### FAQ (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Sección FAQ visible y accesible | ⚙️ funcional | ☐ |
| 2 | B2B | Contenido relevante al cliente (no genérico de otro) | 📊 datos | ☐ |
| 3 | B2B | Links dentro de FAQ funcionan | ⚙️ funcional | ☐ |

#### Favicon (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Favicon del cliente visible en pestaña del browser | 🎨 visual | ☐ |
| 2 | B2B | No es el favicon genérico de YOM | 🎨 visual | ☐ |

#### Filtros de productos (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Filtros disponibles y funcionales | ⚙️ funcional | ☐ |
| 2 | APP | Filtro por categoría: muestra solo productos de esa categoría | ⚙️ funcional | ☐ |
| 3 | APP | Combinar filtros: resultados coherentes | 🔀 edge | ☐ |
| 4 | APP | Limpiar filtros: vuelve a mostrar todo | ⚙️ funcional | ☐ |

#### Funcionamiento offline (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Desactivar internet: app no crashea | ⚙️ funcional | ☐ |
| 2 | APP | Catálogo disponible offline (última sincronización) | ⚙️ funcional | ☐ |
| 3 | APP | Crear pedido offline: se encola | ⚙️ funcional | ☐ |
| 4 | APP | Reactivar internet: pedidos encolados se envían | ⚙️ funcional | ☐ |
| 5 | APP | Indicador visual de modo offline | ⚙️ funcional | ☐ |

#### Gestión comercial (Admin)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | Admin | Dashboard de gestión de ventas visible | ⚙️ funcional | ☐ |
| 2 | Admin | Datos coherentes con pedidos reales | 📊 datos | ☐ |

#### Historial de pedidos (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Lista muestra pedidos del comercio logueado | ⚙️ funcional | ☐ |
| 2 | B2B | Detalle de pedido: items, cantidades, precios, total correcto | ⚙️ funcional | ☐ |
| 3 | B2B | Pedido recién creado aparece al tope de la lista | ⚙️ funcional | ☐ |
| 4 | APP | Historial en APP coincide con B2B para el mismo comercio | 📊 datos | ☐ |

#### Integración con Google Analytics (Admin)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | Admin | GA tracking activo (verificar en DevTools → Network) | 🔗 integración | ☐ |
| 2 | B2B | Eventos de navegación se registran en GA | 🔗 integración | ☐ |

#### Labels en productos (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Productos con new=true muestran etiqueta 'Nuevo' | ⚙️ funcional | ☐ |
| 2 | B2B | Productos con featured=true muestran etiqueta 'Destacado' | ⚙️ funcional | ☐ |
| 3 | B2B | Productos sin labels: no muestran etiqueta vacía | 🔀 edge | ☐ |

#### List view (admin) (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Feature visible y accesible | ⚙️ funcional | ☐ |
| 2 | APP | Funcionalidad principal opera correctamente | ⚙️ funcional | ☐ |

#### Lista categorías (APP, B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Categorías visibles en navegación | ⚙️ funcional | ☐ |
| 2 | B2B | Cada categoría tiene productos asignados | 📊 datos | ☐ |
| 3 | B2B | No hay categorías vacías visibles | 🔀 edge | ☐ |

#### Listas de precio (B2B, APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Comercio del segmento A ve precios del segmento A | 💼 negocio | ☐ |
| 2 | B2B | Comercio del segmento B ve precios diferentes al segmento A | 💼 negocio | ☐ |
| 3 | B2B | Precio en detalle de producto = precio en carro = precio en pedido | 📊 datos | ☐ |
| 4 | Admin | Overrides aplicados por segmento visibles en Admin | 📊 datos | ☐ |

#### Log in B2B (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Login con credenciales válidas: accede al catálogo | ⚙️ funcional | ☐ |
| 2 | B2B | Login con credenciales inválidas: mensaje de error claro | 🔀 edge | ☐ |
| 3 | B2B | Login con campo vacío: validación de formulario | 🔀 edge | ☐ |

#### Mínimos de compra (productos) (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Producto con MinUnit=6: no permite agregar menos de 6 | 💼 negocio | ☐ |
| 2 | B2B | Mensaje claro cuando se intenta comprar menos del mínimo | ⚙️ funcional | ☐ |
| 3 | B2B | Producto sin mínimo: permite agregar desde 1 | 🔀 edge | ☐ |

#### Notificaciones push app (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Push notification llega al dispositivo | ⚙️ funcional | ☐ |
| 2 | APP | Tap en notificación: abre sección correcta de la app | ⚙️ funcional | ☐ |

#### Ordenar (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Ordenar por precio ascendente: funciona | ⚙️ funcional | ☐ |
| 2 | APP | Ordenar por nombre: funciona | ⚙️ funcional | ☐ |
| 3 | APP | Cambiar criterio de orden: lista se actualiza | ⚙️ funcional | ☐ |

#### Packs de productos (APP, B2B, Admin)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Pack visible con descuento aplicado | ⚙️ funcional | ☐ |
| 2 | B2B | Agregar pack al carro: precio correcto | ⚙️ funcional | ☐ |

#### Precio futuro (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Precio cambia según fecha de despacho seleccionada | ⚙️ funcional | ☐ |
| 2 | B2B | API /cart/products?deliveryDate= retorna precio correcto | 🔗 integración | ☐ |
| 3 | B2B | Variable enablePriceOracle activa en BD | 🔗 integración | ☐ |

#### Precio unitario (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Precio por unidad visible en detalle | ⚙️ funcional | ☐ |
| 2 | APP | Precio unitario correcto al cambiar formato | 📊 datos | ☐ |

#### Precios brutos o neto (B2B, APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Si config=neto: precios sin impuesto en todo el flujo | 💼 negocio | ☐ |
| 2 | B2B | Si config=bruto: precios con impuesto en todo el flujo | 💼 negocio | ☐ |
| 3 | B2B | Total del carro calcula correctamente según formato de precio | ⚙️ funcional | ☐ |
| 4 | B2B | Formato de precio consistente en: catálogo, detalle, carro, pedido | 📊 datos | ☐ |

#### Regalos (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Productos de regalo visibles cuando aplica | ⚙️ funcional | ☐ |
| 2 | APP | Regalo se agrega al pedido correctamente | ⚙️ funcional | ☐ |

#### Resumen de venta (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Resumen de ventas del período visible | ⚙️ funcional | ☐ |
| 2 | APP | Datos coinciden con pedidos reales | 📊 datos | ☐ |

#### Separación de marcas (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Vendedor ve solo la marca asignada | 💼 negocio | ☐ |
| 2 | APP | Productos de otra marca no aparecen | 💼 negocio | ☐ |

#### Ticket promedio (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Ticket promedio visible en datos del comercio | ⚙️ funcional | ☐ |
| 2 | APP | Valor coherente con historial de compras | 📊 datos | ☐ |

#### Tomador de pedidos (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Feature visible y accesible | ⚙️ funcional | ☐ |
| 2 | APP | Funcionalidad principal opera correctamente | ⚙️ funcional | ☐ |

#### Transferencia de pedidos (B2B, APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Pedido creado en B2B visible en APP | ⚙️ funcional | ☐ |
| 2 | APP | Pedido transferido muestra datos correctos | 📊 datos | ☐ |

#### Visibilidad y acceso al catálogo (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Usuario verificado: ve catálogo completo | 💼 negocio | ☐ |
| 2 | B2B | Usuario no verificado: acceso según config del cliente | 💼 negocio | ☐ |

#### Vista de catálogo post-registro (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Feature visible y accesible | ⚙️ funcional | ☐ |
| 2 | B2B | Funcionalidad principal opera correctamente | ⚙️ funcional | ☐ |

### Marketing

#### Anuncio (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Anuncio visible al usuario | ⚙️ funcional | ☐ |
| 2 | B2B | Contenido del anuncio correcto | 📊 datos | ☐ |
| 3 | Admin | Anuncio creado en Admin aparece en B2B | 📊 datos | ☐ |

#### Banners (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Banners visibles en home o posición configurada | ⚙️ funcional | ☐ |
| 2 | B2B | Imagen del banner carga correctamente | 🎨 visual | ☐ |
| 3 | B2B | Click en banner: navega a URL configurada | ⚙️ funcional | ☐ |
| 4 | B2B | Banner sin URL: click no genera error | 🔀 edge | ☐ |
| 5 | Admin | Banner creado en Admin aparece en B2B | 📊 datos | ☐ |

#### Notificaciones push (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Mensaje push creado en Admin llega al usuario B2B | ⚙️ funcional | ☐ |
| 2 | Admin | Crear notificación push: formulario funcional | ⚙️ funcional | ☐ |
| 3 | Admin | Segmentar destinatarios: funciona | ⚙️ funcional | ☐ |

#### Notificaciones y alertas (B2B, APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Notificaciones sobre estado de pedidos llegan | ⚙️ funcional | ☐ |
| 2 | APP | Alertas de facturas/pedidos visibles | ⚙️ funcional | ☐ |

### Recomendaciones

#### Canasta Estratégica: Exploración (B2B, APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Productos de comercios similares sugeridos | ⚙️ funcional | ☐ |
| 2 | B2B | Productos sugeridos NO son los que el comercio ya compra | 💼 negocio | ☐ |
| 3 | APP | Sugerencias de exploración visibles | ⚙️ funcional | ☐ |

#### Canasta Estratégica: Foco (B2B, APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | SKUs estratégicos priorizados en sugerencias | 💼 negocio | ☐ |
| 2 | B2B | SKUs provienen del SAF del cliente | 📊 datos | ☐ |
| 3 | APP | Mismos SKUs de foco que en B2B | 📊 datos | ☐ |

#### Canasta Estratégica: General (B2B, APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Sugerencias estratégicas visibles | ⚙️ funcional | ☐ |
| 2 | B2B | Productos sugeridos alineados con estrategia comercial del cliente | 💼 negocio | ☐ |
| 3 | APP | Mismas sugerencias que en B2B | 📊 datos | ☐ |

#### Canasta Estratégica: Innovación (APP, B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Productos innovadores sugeridos | ⚙️ funcional | ☐ |
| 2 | APP | Productos de innovación visibles | ⚙️ funcional | ☐ |

#### Canasta base (B2B, APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Sección de sugerencias visible (si comercio tiene historial) | ⚙️ funcional | ☐ |
| 2 | B2B | Sugerencias coherentes (productos que el comercio suele comprar) | 💼 negocio | ☐ |
| 3 | B2B | Agregar sugerencia al carro: funciona | ⚙️ funcional | ☐ |
| 4 | B2B | Comercio nuevo (cold start): muestra productos populares | 💼 negocio | ☐ |
| 5 | APP | Canasta base visible con mismos productos que B2B | 📊 datos | ☐ |
| 6 | APP | Cantidad sugerida entre MINSIZE y MAXSIZE | 💼 negocio | ☐ |

#### Combos (B2B, APP, Admin)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Combo visible con productos que lo componen | ⚙️ funcional | ☐ |
| 2 | B2B | Precio del combo < suma de productos individuales | 💼 negocio | ☐ |
| 3 | B2B | Agregar combo al carro: todos los productos del combo agregados | ⚙️ funcional | ☐ |
| 4 | APP | Combo funciona igual que en B2B | 📊 datos | ☐ |

#### Inyección de recomendaciones (—)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Sugerencias aparecen durante flujo de compra | ⚙️ funcional | ☐ |
| 2 | APP | Sugerencia se puede agregar al pedido actual | ⚙️ funcional | ☐ |

#### Pedido Sugerido (Metabase)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | Admin | Dashboard de pedido sugerido accesible en Metabase | ⚙️ funcional | ☐ |
| 2 | Admin | Métricas del modelo de sugerencias visibles | 📊 datos | ☐ |

### Fintech

#### Cobranza y facturación (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Documentos de cobranza visibles para el comercio | ⚙️ funcional | ☐ |
| 2 | APP | Facturas con datos correctos (monto, fecha, estado) | 📊 datos | ☐ |

#### Documentos manuales (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Crear documento manual: formulario funcional | ⚙️ funcional | ☐ |
| 2 | APP | Documento creado aparece en historial | ⚙️ funcional | ☐ |

#### Historial de pagos (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Lista de facturas y pagos del comercio | ⚙️ funcional | ☐ |
| 2 | APP | Detalle de cada documento: monto, fecha, estado | ⚙️ funcional | ☐ |
| 3 | APP | Datos coinciden con fuente del cliente (PendingDocuments) | 📊 datos | ☐ |

#### Justificaciones (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Campo de justificación visible cuando aplica | ⚙️ funcional | ☐ |
| 2 | APP | Justificación se guarda correctamente | ⚙️ funcional | ☐ |

#### Redirección a pago de facturas (B2B, APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Link a plataforma de pago del cliente visible | ⚙️ funcional | ☐ |
| 2 | B2B | Click: redirige correctamente (no 404) | ⚙️ funcional | ☐ |
| 3 | APP | Mismo link funcional en APP | ⚙️ funcional | ☐ |

### Ejecución del punto

#### Bloqueo (APP, Admin)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Comercio bloqueado: acción de venta restringida | 💼 negocio | ☐ |
| 2 | APP | Indicador visual de bloqueo | ⚙️ funcional | ☐ |

#### Configuraciones (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Feature visible y accesible | ⚙️ funcional | ☐ |
| 2 | APP | Funcionalidad principal opera correctamente | ⚙️ funcional | ☐ |

#### Soporte (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Sección de soporte accesible | ⚙️ funcional | ☐ |
| 2 | APP | Canal de soporte funcional (chat/email/teléfono) | ⚙️ funcional | ☐ |

#### Soporte (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Sección de soporte accesible | ⚙️ funcional | ☐ |
| 2 | APP | Canal de soporte funcional (chat/email/teléfono) | ⚙️ funcional | ☐ |

### Retención

#### Acciones automáticas (—)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | — | Feature visible y accesible | ⚙️ funcional | ☐ |
| 2 | — | Funcionalidad principal opera correctamente | ⚙️ funcional | ☐ |

#### Clientes (Admin)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | Admin | Feature visible y accesible | ⚙️ funcional | ☐ |
| 2 | Admin | Funcionalidad principal opera correctamente | ⚙️ funcional | ☐ |

#### Estado de retención (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Feature visible y accesible | ⚙️ funcional | ☐ |
| 2 | APP | Funcionalidad principal opera correctamente | ⚙️ funcional | ☐ |

#### Priorización de visitas y acción (—)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | — | Feature visible y accesible | ⚙️ funcional | ☐ |
| 2 | — | Funcionalidad principal opera correctamente | ⚙️ funcional | ☐ |

#### Registro de visita (—)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | — | Feature visible y accesible | ⚙️ funcional | ☐ |
| 2 | — | Funcionalidad principal opera correctamente | ⚙️ funcional | ☐ |

### Otros

#### Bloqueo de carro en casos de precios anómalos (B2B, APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Producto con precio < $50: no se puede agregar al carro | 💼 negocio | ☐ |
| 2 | B2B | Mensaje claro de por qué está bloqueado | ⚙️ funcional | ☐ |
| 3 | APP | Mismo bloqueo funcional en APP | ⚙️ funcional | ☐ |

#### Cambio de contraseña (APP, B2B, Admin)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Flujo 'olvidé contraseña': email llega | ⚙️ funcional | ☐ |
| 2 | B2B | Link de reset funciona y permite cambiar | ⚙️ funcional | ☐ |
| 3 | B2B | Nueva contraseña: login exitoso | ⚙️ funcional | ☐ |
| 4 | APP | Mismo flujo funcional en APP | ⚙️ funcional | ☐ |

#### Compra mínima (—)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Pedido por debajo del mínimo: no permite crear | 💼 negocio | ☐ |
| 2 | B2B | Mensaje claro con el monto mínimo | ⚙️ funcional | ☐ |

#### Contacto (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Información de contacto del comercio visible | ⚙️ funcional | ☐ |
| 2 | B2B | Datos de contacto correctos | 📊 datos | ☐ |

#### Creación de roles para administradores (—)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | — | Feature visible y accesible | ⚙️ funcional | ☐ |
| 2 | — | Funcionalidad principal opera correctamente | ⚙️ funcional | ☐ |

#### Gestión de administradores (—)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | — | Feature visible y accesible | ⚙️ funcional | ☐ |
| 2 | — | Funcionalidad principal opera correctamente | ⚙️ funcional | ☐ |

#### Gestión de pedidos (B2B, APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Lista de pedidos completa | ⚙️ funcional | ☐ |
| 2 | Admin | Pedidos visibles con detalle completo | ⚙️ funcional | ☐ |
| 3 | Admin | Filtrar pedidos por fecha, estado, comercio | ⚙️ funcional | ☐ |

#### Historial de facturas (B2B, APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Historial de facturas visible | ⚙️ funcional | ☐ |
| 2 | APP | Mismas facturas visibles en APP | 📊 datos | ☐ |

#### Icons (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Feature visible y accesible | ⚙️ funcional | ☐ |
| 2 | B2B | Funcionalidad principal opera correctamente | ⚙️ funcional | ☐ |

#### Impuestos para productos (—)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Impuestos calculados correctamente según config | ⚙️ funcional | ☐ |
| 2 | B2B | Desglose de impuestos visible (si aplica) | ⚙️ funcional | ☐ |

#### Jobs de integración (—)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | Admin | CronJobs configurados según requerimiento del cliente | 🔗 integración | ☐ |
| 2 | Admin | Última ejecución exitosa (verificar con Analytics) | 🔗 integración | ☐ |
| 3 | Admin | Horarios de ejecución correctos según ventana acordada | 🔗 integración | ☐ |

#### Log in App (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Login con credenciales de vendedor: accede a la app | ⚙️ funcional | ☐ |
| 2 | APP | Login con credenciales inválidas: mensaje claro | 🔀 edge | ☐ |

#### Minibanners (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Minibanners visibles en posición correcta | 🎨 visual | ☐ |
| 2 | B2B | No se superponen con otros elementos | 🎨 visual | ☐ |

#### Método de pago (—)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Métodos de pago del cliente configurados y visibles | ⚙️ funcional | ☐ |

#### Prompt Analytics (—)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | — | Feature visible y accesible | ⚙️ funcional | ☐ |
| 2 | — | Funcionalidad principal opera correctamente | ⚙️ funcional | ☐ |

#### Ruta del día (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Ruta asignada visible con comercios en orden | ⚙️ funcional | ☐ |
| 2 | APP | Comercios de la ruta corresponden al vendedor | 💼 negocio | ☐ |
| 3 | APP | Navegar entre comercios de la ruta: fluido | ⚙️ funcional | ☐ |

#### Selección de método de pago (—)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Métodos de pago configurados visibles en checkout | ⚙️ funcional | ☐ |
| 2 | B2B | Seleccionar método diferente: pedido se crea con método correcto | ⚙️ funcional | ☐ |

---

## 6. Pruebas transversales

### Datos y catálogo

| # | Herramienta | Prueba | ✓ |
|---|---|---|---|
| 1 | B2B | Cantidad total de productos coincide con fuente del cliente (±5%) | ☐ |
| 2 | B2B | Revisar 10 productos al azar: nombre, precio e imagen correctos | ☐ |
| 3 | B2B | Precios en B2B = precios en fuente del cliente (verificar 5+) | ☐ |
| 4 | B2B | Categorías: estructura lógica, no hay vacías | ☐ |
| 5 | APP | Catálogo en APP coincide con B2B (mismos productos y precios) | ☐ |
| 6 | Admin | Cantidad de productos en Admin = B2B | ☐ |

### Consistencia cross-platform

| # | Herramienta | Prueba | ✓ |
|---|---|---|---|
| 1 | B2B+APP | Precio del mismo producto: igual en B2B y APP | ☐ |
| 2 | B2B+APP | Pedido creado en B2B: visible en APP y Admin | ☐ |
| 3 | B2B+APP | Pedido creado en APP: visible en B2B y Admin | ☐ |
| 4 | B2B+APP | Promoción activa: se aplica tanto en B2B como APP | ☐ |
| 5 | B2B+APP | Estado crediticio: consistente entre plataformas | ☐ |

### Consola y errores

| # | Herramienta | Prueba | ✓ |
|---|---|---|---|
| 1 | B2B | Home: abrir DevTools → Console → sin errores rojos | ☐ |
| 2 | B2B | Catálogo: sin errores en consola | ☐ |
| 3 | B2B | Checkout: sin errores en consola | ☐ |
| 4 | B2B | Network: sin requests fallidos (4xx/5xx) en flujo normal | ☐ |

### Performance

| # | Herramienta | Prueba | ✓ |
|---|---|---|---|
| 1 | B2B | Home carga en < 3 segundos | ☐ |
| 2 | B2B | Catálogo carga en < 3 segundos | ☐ |
| 3 | B2B | Búsqueda responde en < 1 segundo | ☐ |
| 4 | B2B | Agregar al carro responde en < 500ms | ☐ |
| 5 | APP | App abre en < 5 segundos | ☐ |

### UX básica

| # | Herramienta | Prueba | ✓ |
|---|---|---|---|
| 1 | B2B | Textos en español (no inglés ni placeholders) | ☐ |
| 2 | B2B | Mensajes de error descriptivos (no códigos técnicos) | ☐ |
| 3 | B2B | Feedback visual al agregar producto al carro | ☐ |
| 4 | B2B | Confirmación antes de enviar pedido | ☐ |
| 5 | B2B | Navegación intuitiva: siempre se puede volver atrás | ☐ |

---

## 7. Veredicto — Gate de Rollout

### Issues encontrados

| ID | Severidad | Herramienta | Feature | Descripción | Escalado a | Estado |
|---|---|---|---|---|---|---|
| Soprole-QA-001 | | | | | | |
| Soprole-QA-002 | | | | | | |
| Soprole-QA-003 | | | | | | |

### Criterios de salida

| Criterio | Obligatorio | Cumple | Notas |
|---|---|---|---|
| Zero issues Critical abiertos | Sí | ☐ | |
| Zero issues High sin plan de resolución | Sí | ☐ | |
| Flujo de compra B2B funcional | Sí | ☐ | |
| Flujo de compra APP funcional | Sí | ☐ | |
| Catálogo con datos del cliente | Sí | ☐ | |
| Health Score >= 80% | Sí | ☐ | Score: ___ |

### Health Score

| Categoría | Peso | Score (0-100) | Ponderado |
|---|---|---|---|
| Flujos core | 30% | | |
| Datos y catálogo | 20% | | |
| Integraciones | 20% | | |
| Features del cliente | 15% | | |
| UX y visual | 10% | | |
| Performance | 5% | | |
| **TOTAL** | **100%** | | **___** |

### Veredicto final

☐ **LISTO** — Todos los criterios obligatorios cumplidos, Health Score >= 80%  
☐ **LISTO CON CONDICIONES** — Criterios cumplidos, issues Medium pendientes  
☐ **NO APTO** — Algún criterio obligatorio no cumplido  

**Condiciones (si aplica):**
1. 
2. 

**Próximos pasos:**

| Acción | Responsable | Plazo |
|---|---|---|
| | | |

---

*Generado: 2026-03-25 | Cliente: Soprole | Casos de prueba: 232*