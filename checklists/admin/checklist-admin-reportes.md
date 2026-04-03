# Checklist Admin — Reportes y Configuración de Tienda

**Fuente:** Funcionalidad Admin YOM — reportes, configuración, branding  
**Cuándo ejecutar:** Post-deploy, onboarding cliente nuevo, cambios de configuración  
**Plataforma:** admin.youorder.me → secciones Configuración y Reportes

---

## Configuración de Tienda (Store Config)

| ID | Caso | Cómo validar | Estado |
|----|------|--------------|--------|
| ADM-STR-01 | Configurar logo de tienda | Subir imagen logo → verificar que aparece en header del B2B del cliente | PENDIENTE |
| ADM-STR-02 | Configurar favicon | Subir favicon → aparecer en tab del browser en B2B | PENDIENTE |
| ADM-STR-03 | Configurar colores de marca | Cambiar color primario → B2B refleja el nuevo color en botones y header | PENDIENTE |
| ADM-STR-04 | Activar/desactivar métodos de pago | Habilitar Khipu → aparece opción "Pagar con Khipu" en checkout B2B | PENDIENTE |
| ADM-STR-05 | Configurar fechas de entrega | Agregar fechas de entrega → aparecen en selector de fecha en carrito B2B | PENDIENTE |
| ADM-STR-06 | Configurar monto mínimo de pedido | Establecer monto mínimo → B2B bloquea checkout si total es menor | PENDIENTE |
| ADM-STR-07 | Habilitar facturas en B2B | Activar "Mostrar facturas en B2B" → aparece sección de facturas en historial de pedidos | PENDIENTE |
| ADM-STR-08 | Deshabilitar campo de observaciones | Activar "Deshabilitar observaciones" → campo notas desaparece en carrito B2B | PENDIENTE |

---

## Gestión de Banners

| ID | Caso | Cómo validar | Estado |
|----|------|--------------|--------|
| ADM-STR-10 | Crear banner con imagen | Subir imagen, definir URL destino → banner visible en B2B header/hero | PENDIENTE |
| ADM-STR-11 | Activar/desactivar banner | Desactivar banner → desaparece en B2B sin necesidad de eliminarlo | PENDIENTE |
| ADM-STR-12 | Banner con rango de fechas | Configurar fechas inicio/fin → banner solo visible en ese período | PENDIENTE |
| ADM-STR-13 | Múltiples banners con orden | Crear 3 banners → se muestran en el orden configurado en B2B | PENDIENTE |
| ADM-STR-14 | Banner con enlace externo | URL destino apunta a sitio externo → link abre correctamente | PENDIENTE |

---

## Gestión de Promociones

| ID | Caso | Cómo validar | Estado |
|----|------|--------------|--------|
| ADM-STR-20 | Crear promoción de catálogo | Definir % descuento para producto → precio descontado visible en B2B catálogo | PENDIENTE |
| ADM-STR-21 | Crear promoción por volumen | Configurar escalas de descuento → B2B muestra descuento al seleccionar cantidad correcta | PENDIENTE |
| ADM-STR-22 | Activar/desactivar promoción | Desactivar promoción activa → precio vuelve a normal en B2B | PENDIENTE |
| ADM-STR-23 | Promoción con fechas | Configurar inicio y fin → solo activa en ese período | PENDIENTE |
| ADM-STR-24 | Crear cupón de descuento | Definir código y % descuento → cupón funciona en carrito B2B | PENDIENTE |
| ADM-STR-25 | Cupón de uso único | Crear cupón de uso único → después del primer uso, no aplica | PENDIENTE |

---

## Reportes y Analytics

| ID | Caso | Cómo validar | Estado |
|----|------|--------------|--------|
| ADM-RPT-01 | Ver dashboard de ventas | Acceder a sección Reportes → gráficos de ventas con datos del período | PENDIENTE |
| ADM-RPT-02 | Filtrar reporte por período | Cambiar rango de fechas → datos actualizan para el período seleccionado | PENDIENTE |
| ADM-RPT-03 | Ver top productos vendidos | Lista de productos más vendidos con montos | PENDIENTE |
| ADM-RPT-04 | Ver top comercios compradores | Lista de comercios con mayor volumen de compra | PENDIENTE |
| ADM-RPT-05 | Exportar reporte a CSV/Excel | Botón exportar → archivo descarga con datos del período | PENDIENTE |
| ADM-RPT-06 | Reporte de pedidos pendientes | Filtrar pedidos PENDIENTE → lista con detalle de cada uno | PENDIENTE |

---

## Gestión de Comercios

| ID | Caso | Cómo validar | Estado |
|----|------|--------------|--------|
| ADM-STR-30 | Invitar nuevo comercio | Enviar invitación por email → comercio recibe email con acceso | PENDIENTE |
| ADM-STR-31 | Activar/desactivar comercio | Desactivar comercio activo → no puede hacer login en B2B | PENDIENTE |
| ADM-STR-32 | Bloquear comercio por crédito | Marcar comercio como BLOQUEADO → en B2B ve mensaje de acceso restringido | PENDIENTE |
| ADM-STR-33 | Ver historial de pedidos de un comercio | En detalle del comercio → historial de todas sus órdenes | PENDIENTE |
| ADM-STR-34 | Asignar segmento a comercio | Cambiar segmento → precios del comercio actualizan según nuevo segmento | PENDIENTE |

---

## Notas de Escalamiento

Si cambio de configuración no se refleja en B2B → P1, puede ser caché no invalidada.  
Si promoción aparece con monto incorrecto → P1, revisar cálculo en checklist-pricing-engine.md.  
Si datos de reportes no coinciden con pedidos → P2, posible lag en agregación.

**Post-mortem relacionado:** Ninguno registrado actualmente.
