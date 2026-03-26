"""
checklist-generator.py

Genera un checklist de QA completo para un cliente YOM.
No solo lista features — genera casos de prueba concretos,
validaciones de datos, edge cases y escenarios de negocio.

Uso:
  python checklist-generator.py --cliente Soprole
  python checklist-generator.py --cliente Bidfood --output QA/Bidfood/checklist.md
  python checklist-generator.py --list-clientes

Requiere:
  - CSV de features en la ruta configurada
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# ─────────────────────────────────────────────
# Rutas a CSVs
# ─────────────────────────────────────────────

_BASE = Path(__file__).parent.parent  # qa/ root
FEATURES_CSV = _BASE / "data" / "features-clientes-2026.csv"
FEATURES_CSV_ALL = _BASE / "data" / "features-clientes-2026.csv"
QA_MATRIX_JSON = _BASE / "data" / "qa-matrix.json"

# ─────────────────────────────────────────────
# Base de conocimiento de pruebas por feature
# Cada entrada: (feature_name, list[TestCase])
# TestCase = (herramienta, descripción_prueba, tipo)
# tipo: "funcional" | "datos" | "edge" | "integración" | "visual" | "negocio"
# ─────────────────────────────────────────────

TEST_CASES: Dict[str, List[Tuple[str, str, str]]] = {
    # ── VENTA CORE ──
    "Catálogo": [
        ("B2B", "Abrir catálogo: productos visibles con nombre, precio e imagen", "funcional"),
        ("B2B", "Navegar por categorías: cada categoría muestra productos relevantes", "funcional"),
        ("B2B", "Producto sin imagen: muestra placeholder, no quiebra layout", "edge"),
        ("B2B", "Catálogo con +500 productos: scroll fluido, paginación/infinite scroll funciona", "edge"),
        ("APP", "Catálogo filtra por portafolio del vendedor (si configurado)", "negocio"),
        ("APP", "Catálogo funciona offline (muestra última sincronización)", "edge"),
        ("Admin", "Productos en Admin coinciden con lo que muestra B2B", "datos"),
    ],
    "Crear pedido": [
        ("B2B", "Flujo completo: catálogo → producto → carro → checkout → confirmación", "funcional"),
        ("B2B", "Pedido con 1 solo producto: se crea correctamente", "funcional"),
        ("B2B", "Pedido con 20+ productos: todos aparecen en resumen y confirmación", "edge"),
        ("B2B", "Pedido con cantidad 0 o negativa: no permite crear", "edge"),
        ("B2B", "Doble click en 'crear pedido': no genera pedido duplicado", "edge"),
        ("B2B", "Pedido aparece en historial inmediatamente después de crear", "funcional"),
        ("APP", "Crear pedido desde tomador: seleccionar comercio → productos → confirmar", "funcional"),
        ("APP", "Crear pedido offline: se encola y envía al recuperar conexión", "edge"),
    ],
    "Carro de compras": [
        ("B2B", "Agregar producto: carro actualiza contador y total", "funcional"),
        ("B2B", "Modificar cantidad: total recalcula correctamente", "funcional"),
        ("B2B", "Eliminar producto del carro: se remueve y total actualiza", "funcional"),
        ("B2B", "Carro vacío: mensaje descriptivo, no pantalla en blanco", "edge"),
        ("B2B", "Carro con producto sin stock: muestra aviso (si stock integrado)", "edge"),
        ("B2B", "Carro persiste al navegar entre páginas", "funcional"),
        ("B2B", "Carro persiste al cerrar y reabrir sesión", "edge"),
    ],
    "Búsqueda de productos": [
        ("B2B", "Buscar por nombre exacto: producto aparece primero", "funcional"),
        ("B2B", "Buscar por SKU: producto encontrado", "funcional"),
        ("B2B", "Buscar término parcial: resultados relevantes", "funcional"),
        ("B2B", "Buscar término inexistente: mensaje 'sin resultados', no error", "edge"),
        ("B2B", "Buscar con caracteres especiales (ñ, tildes): funciona correctamente", "edge"),
        ("APP", "Búsqueda en APP retorna mismos resultados que B2B", "datos"),
    ],
    "Historial de pedidos": [
        ("B2B", "Lista muestra pedidos del comercio logueado", "funcional"),
        ("B2B", "Detalle de pedido: items, cantidades, precios, total correcto", "funcional"),
        ("B2B", "Pedido recién creado aparece al tope de la lista", "funcional"),
        ("APP", "Historial en APP coincide con B2B para el mismo comercio", "datos"),
    ],
    "Seguimiento de pedidos": [
        ("B2B", "Estado del pedido visible (pendiente/confirmado/despachado/etc)", "funcional"),
        ("B2B", "Estado se actualiza cuando cambia en el ERP", "integración"),
        ("B2B", "Detalle incluye: total, facturas, notas de crédito, fecha creación", "funcional"),
    ],
    "Listas de precio": [
        ("B2B", "Comercio del segmento A ve precios del segmento A", "negocio"),
        ("B2B", "Comercio del segmento B ve precios diferentes al segmento A", "negocio"),
        ("B2B", "Precio en detalle de producto = precio en carro = precio en pedido", "datos"),
        ("Admin", "Overrides aplicados por segmento visibles en Admin", "datos"),
    ],
    "Precios brutos o neto": [
        ("B2B", "Si config=neto: precios sin impuesto en todo el flujo", "negocio"),
        ("B2B", "Si config=bruto: precios con impuesto en todo el flujo", "negocio"),
        ("B2B", "Total del carro calcula correctamente según formato de precio", "funcional"),
        ("B2B", "Formato de precio consistente en: catálogo, detalle, carro, pedido", "datos"),
    ],
    "Precio futuro": [
        ("B2B", "Precio cambia según fecha de despacho seleccionada", "funcional"),
        ("B2B", "API /cart/products?deliveryDate= retorna precio correcto", "integración"),
        ("B2B", "Variable enablePriceOracle activa en BD", "integración"),
    ],
    "Agregar fecha despacho": [
        ("B2B", "Calendario aparece en checkout", "funcional"),
        ("B2B", "Solo fechas disponibles son seleccionables (deliveryDays del comercio)", "negocio"),
        ("B2B", "Fecha seleccionada se refleja en el pedido creado", "funcional"),
        ("APP", "Variable enableAskDeliveryDate activa → calendario en observaciones", "integración"),
        ("APP", "Fecha seleccionada viaja con el pedido", "funcional"),
    ],
    "Agregar observaciones": [
        ("B2B", "Campo de observaciones visible en checkout", "funcional"),
        ("B2B", "Texto ingresado aparece en detalle del pedido", "funcional"),
        ("B2B", "Observación con caracteres especiales (ñ, tildes, emojis): se guarda", "edge"),
        ("APP", "Observaciones desde APP visibles en Admin", "datos"),
    ],
    "Mínimos de compra (productos)": [
        ("B2B", "Producto con MinUnit=6: no permite agregar menos de 6", "negocio"),
        ("B2B", "Mensaje claro cuando se intenta comprar menos del mínimo", "funcional"),
        ("B2B", "Producto sin mínimo: permite agregar desde 1", "edge"),
    ],
    "Máximos de compra (items)": [
        ("APP", "No permite agregar más del máximo configurado", "negocio"),
        ("APP", "Mensaje claro cuando se alcanza el máximo", "funcional"),
    ],
    "Labels en productos": [
        ("B2B", "Productos con new=true muestran etiqueta 'Nuevo'", "funcional"),
        ("B2B", "Productos con featured=true muestran etiqueta 'Destacado'", "funcional"),
        ("B2B", "Productos sin labels: no muestran etiqueta vacía", "edge"),
    ],
    "Cambios de formato": [
        ("APP", "Producto con múltiples formatos: selector visible (pack/unidad/caja)", "funcional"),
        ("APP", "Cambiar formato actualiza precio y cantidad", "funcional"),
        ("APP", "Formato seleccionado se refleja en el pedido", "datos"),
    ],
    "Detalle del producto": [
        ("APP", "Muestra: nombre, descripción, precio, imagen, especificaciones", "funcional"),
        ("APP", "Producto sin imagen: muestra placeholder", "edge"),
        ("APP", "Producto sin descripción: no muestra campo vacío", "edge"),
    ],
    "Visualización de stock": [
        ("APP", "Stock visible en producto (si integrado)", "funcional"),
        ("APP", "Stock 0: indicador visual claro", "funcional"),
        ("APP", "Stock actualizado (comparar con fuente del cliente)", "datos"),
    ],
    "Edición de store": [
        ("B2B", "Logo del cliente visible en header", "visual"),
        ("B2B", "Colores del cliente aplicados (primario, secundario)", "visual"),
        ("B2B", "Favicon del cliente en pestaña del browser", "visual"),
        ("Admin", "Tienda → personalización refleja lo que se ve en B2B", "datos"),
    ],
    "Favicon": [
        ("B2B", "Favicon del cliente visible en pestaña del browser", "visual"),
        ("B2B", "No es el favicon genérico de YOM", "visual"),
    ],
    "Funcionamiento offline": [
        ("APP", "Desactivar internet: app no crashea", "funcional"),
        ("APP", "Catálogo disponible offline (última sincronización)", "funcional"),
        ("APP", "Crear pedido offline: se encola", "funcional"),
        ("APP", "Reactivar internet: pedidos encolados se envían", "funcional"),
        ("APP", "Indicador visual de modo offline", "funcional"),
    ],
    "Re-hacer un pedido anterior": [
        ("APP", "Botón 'repetir pedido' visible en historial", "funcional"),
        ("APP", "Productos del pedido anterior se agregan al carro", "funcional"),
        ("APP", "Producto descontinuado en pedido anterior: mensaje claro", "edge"),
    ],
    "Compartir el pedido": [
        ("APP", "Botón compartir visible en detalle de pedido", "funcional"),
        ("APP", "Compartir genera link o contenido legible", "funcional"),
    ],
    "Compartir la sugerencia": [
        ("APP", "Botón compartir en sugerencia de productos", "funcional"),
        ("APP", "Contenido compartido incluye productos sugeridos", "funcional"),
    ],
    "Transferencia de pedidos": [
        ("B2B", "Pedido creado en B2B visible en APP", "funcional"),
        ("APP", "Pedido transferido muestra datos correctos", "datos"),
    ],
    "Visibilidad y acceso al catálogo": [
        ("B2B", "Usuario verificado: ve catálogo completo", "negocio"),
        ("B2B", "Usuario no verificado: acceso según config del cliente", "negocio"),
    ],
    "Lista categorías": [
        ("B2B", "Categorías visibles en navegación", "funcional"),
        ("B2B", "Cada categoría tiene productos asignados", "datos"),
        ("B2B", "No hay categorías vacías visibles", "edge"),
    ],
    "Filtros de productos": [
        ("APP", "Filtros disponibles y funcionales", "funcional"),
        ("APP", "Filtro por categoría: muestra solo productos de esa categoría", "funcional"),
        ("APP", "Combinar filtros: resultados coherentes", "edge"),
        ("APP", "Limpiar filtros: vuelve a mostrar todo", "funcional"),
    ],
    "Filtros de comercios": [
        ("APP", "Filtrar comercios por criterio", "funcional"),
        ("APP", "Resultado de filtro coherente con datos", "datos"),
    ],
    "Limitación productos": [
        ("B2B", "Producto con límite: no permite exceder máximo de unidades", "negocio"),
        ("APP", "Mensaje claro al alcanzar el límite", "funcional"),
    ],
    "Escalones obligados": [
        ("B2B", "Producto con escalón=6: solo permite comprar en múltiplos de 6", "negocio"),
        ("B2B", "Intentar cantidad no múltiplo: corrige o muestra error", "edge"),
    ],
    "Descuentos manuales": [
        ("APP", "Vendedor puede aplicar descuento manual", "funcional"),
        ("APP", "Descuento se refleja en total del pedido", "funcional"),
        ("APP", "Descuento respeta límite máximo (si configurado)", "negocio"),
    ],
    "Impuestos para productos": [
        ("B2B", "Impuestos calculados correctamente según config", "funcional"),
        ("B2B", "Desglose de impuestos visible (si aplica)", "funcional"),
    ],
    "Precio despacho": [
        ("APP", "Costo de despacho visible en resumen de pedido", "funcional"),
        ("APP", "Costo se suma al total correctamente", "funcional"),
    ],
    "Precio unitario": [
        ("APP", "Precio por unidad visible en detalle", "funcional"),
        ("APP", "Precio unitario correcto al cambiar formato", "datos"),
    ],
    "Gestión de pedidos": [
        ("B2B", "Lista de pedidos completa", "funcional"),
        ("Admin", "Pedidos visibles con detalle completo", "funcional"),
        ("Admin", "Filtrar pedidos por fecha, estado, comercio", "funcional"),
    ],
    "Separación de marcas": [
        ("APP", "Vendedor ve solo la marca asignada", "negocio"),
        ("APP", "Productos de otra marca no aparecen", "negocio"),
    ],
    "Selección de método de pago": [
        ("B2B", "Métodos de pago configurados visibles en checkout", "funcional"),
        ("B2B", "Seleccionar método diferente: pedido se crea con método correcto", "funcional"),
    ],

    # ── MARKETING ──
    "Banners": [
        ("B2B", "Banners visibles en home o posición configurada", "funcional"),
        ("B2B", "Imagen del banner carga correctamente", "visual"),
        ("B2B", "Click en banner: navega a URL configurada", "funcional"),
        ("B2B", "Banner sin URL: click no genera error", "edge"),
        ("Admin", "Banner creado en Admin aparece en B2B", "datos"),
    ],
    "Minibanners": [
        ("B2B", "Minibanners visibles en posición correcta", "visual"),
        ("B2B", "No se superponen con otros elementos", "visual"),
    ],
    "Anuncio": [
        ("B2B", "Anuncio visible al usuario", "funcional"),
        ("B2B", "Contenido del anuncio correcto", "datos"),
        ("Admin", "Anuncio creado en Admin aparece en B2B", "datos"),
    ],
    "Notificaciones y alertas": [
        ("B2B", "Notificaciones sobre estado de pedidos llegan", "funcional"),
        ("APP", "Alertas de facturas/pedidos visibles", "funcional"),
    ],
    "Notificaciones push": [
        ("B2B", "Mensaje push creado en Admin llega al usuario B2B", "funcional"),
        ("Admin", "Crear notificación push: formulario funcional", "funcional"),
        ("Admin", "Segmentar destinatarios: funciona", "funcional"),
    ],
    "Notificaciones push app": [
        ("APP", "Push notification llega al dispositivo", "funcional"),
        ("APP", "Tap en notificación: abre sección correcta de la app", "funcional"),
    ],
    "FAQ": [
        ("B2B", "Sección FAQ visible y accesible", "funcional"),
        ("B2B", "Contenido relevante al cliente (no genérico de otro)", "datos"),
        ("B2B", "Links dentro de FAQ funcionan", "funcional"),
    ],
    "Cupón de descuento": [
        ("B2B", "Campo para ingresar cupón visible en checkout", "funcional"),
        ("B2B", "Cupón válido: descuento se aplica al total", "funcional"),
        ("B2B", "Cupón inválido: mensaje de error claro", "edge"),
        ("B2B", "Cupón expirado: mensaje de error claro", "edge"),
        ("B2B", "Cupón ya usado (si uso único): rechazado", "edge"),
        ("Admin", "Crear cupón: fecha inicio, fin, tipo descuento, monto", "funcional"),
    ],

    # ── RECOMENDACIONES ──
    "Canasta base": [
        ("B2B", "Sección de sugerencias visible (si comercio tiene historial)", "funcional"),
        ("B2B", "Sugerencias coherentes (productos que el comercio suele comprar)", "negocio"),
        ("B2B", "Agregar sugerencia al carro: funciona", "funcional"),
        ("B2B", "Comercio nuevo (cold start): muestra productos populares", "negocio"),
        ("APP", "Canasta base visible con mismos productos que B2B", "datos"),
        ("APP", "Cantidad sugerida entre MINSIZE y MAXSIZE", "negocio"),
    ],
    "Canasta Estratégica: General": [
        ("B2B", "Sugerencias estratégicas visibles", "funcional"),
        ("B2B", "Productos sugeridos alineados con estrategia comercial del cliente", "negocio"),
        ("APP", "Mismas sugerencias que en B2B", "datos"),
    ],
    "Canasta Estratégica: Exploración": [
        ("B2B", "Productos de comercios similares sugeridos", "funcional"),
        ("B2B", "Productos sugeridos NO son los que el comercio ya compra", "negocio"),
        ("APP", "Sugerencias de exploración visibles", "funcional"),
    ],
    "Canasta Estratégica: Foco": [
        ("B2B", "SKUs estratégicos priorizados en sugerencias", "negocio"),
        ("B2B", "SKUs provienen del SAF del cliente", "datos"),
        ("APP", "Mismos SKUs de foco que en B2B", "datos"),
    ],
    "Canasta Estratégica: Innovación": [
        ("B2B", "Productos innovadores sugeridos", "funcional"),
        ("APP", "Productos de innovación visibles", "funcional"),
    ],
    "Promociones de catálogo": [
        ("B2B", "Producto con promoción: precio original tachado + precio promocional", "funcional"),
        ("B2B", "Descuento se refleja en carro y pedido", "funcional"),
        ("B2B", "Promoción expirada: precio vuelve a normal", "edge"),
        ("APP", "Misma promoción visible en APP", "datos"),
        ("Admin", "Crear promoción de catálogo: funcional", "funcional"),
    ],
    "Descuentos por volumen": [
        ("B2B", "Escalas de volumen visibles en producto", "funcional"),
        ("B2B", "Comprar 10 unidades (escala 1): descuento X% aplicado", "negocio"),
        ("B2B", "Comprar 50 unidades (escala 2): descuento Y% mayor aplicado", "negocio"),
        ("B2B", "Cantidad justo debajo del umbral: NO aplica descuento", "edge"),
        ("B2B", "Total del carro refleja descuento por volumen correctamente", "funcional"),
        ("APP", "Descuentos por volumen funcionan igual que en B2B", "datos"),
    ],
    "Promociones personalizadas": [
        ("B2B", "Promos específicas para el comercio visible", "funcional"),
        ("B2B", "Comercio diferente: ve promos diferentes", "negocio"),
    ],
    "Inyección de recomendaciones": [
        ("APP", "Sugerencias aparecen durante flujo de compra", "funcional"),
        ("APP", "Sugerencia se puede agregar al pedido actual", "funcional"),
    ],
    "Combos": [
        ("B2B", "Combo visible con productos que lo componen", "funcional"),
        ("B2B", "Precio del combo < suma de productos individuales", "negocio"),
        ("B2B", "Agregar combo al carro: todos los productos del combo agregados", "funcional"),
        ("APP", "Combo funciona igual que en B2B", "datos"),
    ],
    "Packs de productos": [
        ("B2B", "Pack visible con descuento aplicado", "funcional"),
        ("B2B", "Agregar pack al carro: precio correcto", "funcional"),
    ],

    # ── FINTECH ──
    "Estado crediticio": [
        ("B2B", "Comercio OK: puede comprar normalmente", "negocio"),
        ("B2B", "Comercio en alerta: aviso visible pero puede comprar", "negocio"),
        ("B2B", "Comercio bloqueado: NO puede crear pedido", "negocio"),
        ("APP", "Estado crediticio visible en datos del comercio", "funcional"),
        ("APP", "Comercio bloqueado: vendedor ve indicador claro", "funcional"),
    ],
    "Cobranza y facturación": [
        ("APP", "Documentos de cobranza visibles para el comercio", "funcional"),
        ("APP", "Facturas con datos correctos (monto, fecha, estado)", "datos"),
    ],
    "Historial de pagos": [
        ("APP", "Lista de facturas y pagos del comercio", "funcional"),
        ("APP", "Detalle de cada documento: monto, fecha, estado", "funcional"),
        ("APP", "Datos coinciden con fuente del cliente (PendingDocuments)", "datos"),
    ],
    "Recaudación diaria": [
        ("APP", "Resumen del día visible: total cobrado, total pendiente", "funcional"),
        ("APP", "Datos actualizados (no de días anteriores)", "datos"),
    ],
    "Bloqueo": [
        ("APP", "Comercio bloqueado: acción de venta restringida", "negocio"),
        ("APP", "Indicador visual de bloqueo", "funcional"),
    ],
    "Redirección a pago de facturas": [
        ("B2B", "Link a plataforma de pago del cliente visible", "funcional"),
        ("B2B", "Click: redirige correctamente (no 404)", "funcional"),
        ("APP", "Mismo link funcional en APP", "funcional"),
    ],
    "Justificaciones": [
        ("APP", "Campo de justificación visible cuando aplica", "funcional"),
        ("APP", "Justificación se guarda correctamente", "funcional"),
    ],
    "Documentos manuales": [
        ("APP", "Crear documento manual: formulario funcional", "funcional"),
        ("APP", "Documento creado aparece en historial", "funcional"),
    ],

    # ── EJECUCIÓN DEL PUNTO ──
    "Ruta del día": [
        ("APP", "Ruta asignada visible con comercios en orden", "funcional"),
        ("APP", "Comercios de la ruta corresponden al vendedor", "negocio"),
        ("APP", "Navegar entre comercios de la ruta: fluido", "funcional"),
    ],
    "Georreferencia": [
        ("APP", "Mapa muestra comercios geolocalizados", "funcional"),
        ("APP", "Ubicación de comercios es correcta (no en el mar)", "datos"),
        ("APP", "Permisos de ubicación: solicita correctamente", "funcional"),
    ],
    "Registro de visitas": [
        ("APP", "Registrar visita: formulario funcional", "funcional"),
        ("APP", "Encuesta de visita: preguntas configuradas", "funcional"),
        ("APP", "Visita registrada aparece en historial", "funcional"),
    ],
    "Gestión de tareas": [
        ("APP", "Tareas del vendedor visibles", "funcional"),
        ("APP", "Completar tarea: estado actualiza", "funcional"),
        ("Admin", "Tareas creadas en Admin visibles en APP", "datos"),
    ],
    "Visualización de datos comercio": [
        ("APP", "Datos del comercio completos: contacto, dirección, crédito", "funcional"),
        ("APP", "Ticket promedio, último pedido, formas de pago visibles", "funcional"),
        ("APP", "Datos coinciden con fuente del cliente", "datos"),
    ],

    # ── AUTH ──
    "Log in B2B": [
        ("B2B", "Login con credenciales válidas: accede al catálogo", "funcional"),
        ("B2B", "Login con credenciales inválidas: mensaje de error claro", "edge"),
        ("B2B", "Login con campo vacío: validación de formulario", "edge"),
    ],
    "Log in App": [
        ("APP", "Login con credenciales de vendedor: accede a la app", "funcional"),
        ("APP", "Login con credenciales inválidas: mensaje claro", "edge"),
    ],
    "Cambio de contraseña": [
        ("B2B", "Flujo 'olvidé contraseña': email llega", "funcional"),
        ("B2B", "Link de reset funciona y permite cambiar", "funcional"),
        ("B2B", "Nueva contraseña: login exitoso", "funcional"),
        ("APP", "Mismo flujo funcional en APP", "funcional"),
    ],
    "Creación de cuentas": [
        ("APP", "Método de registro disponible según config del cliente", "funcional"),
        ("APP", "Registro completo: cuenta activa", "funcional"),
        ("APP", "Registro con datos inválidos: validación", "edge"),
    ],

    # ── INTEGRACIONES ──
    "Inyectar pedido": [
        ("B2B", "Crear pedido → llega al ERP del cliente", "integración"),
        ("B2B", "Tiempo de confirmación dentro del SLA configurado", "integración"),
        ("B2B", "Error de ERP: mensaje descriptivo al usuario (no crash)", "edge"),
        ("B2B", "Timeout de ERP: pedido queda en estado pendiente", "edge"),
        ("APP", "Inyección desde APP funciona igual", "integración"),
    ],
    "Estados de orden según ERP": [
        ("B2B", "Estado cambia en ERP → se refleja en B2B", "integración"),
        ("B2B", "Tiempo de actualización razonable", "integración"),
        ("APP", "Mismos estados visibles en APP", "datos"),
        ("Admin", "Estados visibles en Admin", "datos"),
    ],
    "Jobs de integración": [
        ("Admin", "CronJobs configurados según requerimiento del cliente", "integración"),
        ("Admin", "Última ejecución exitosa (verificar con Analytics)", "integración"),
        ("Admin", "Horarios de ejecución correctos según ventana acordada", "integración"),
    ],
    "Sincronización de sistemas": [
        ("APP", "Datos se actualizan después de cada sync", "integración"),
        ("APP", "Último sync visible o inferible (datos frescos)", "funcional"),
    ],
    "Integración con Google Analytics": [
        ("Admin", "GA tracking activo (verificar en DevTools → Network)", "integración"),
        ("B2B", "Eventos de navegación se registran en GA", "integración"),
    ],

    # ── ADMIN ──
    "Lista de comercios": [
        ("Admin", "Lista completa de comercios del cliente", "funcional"),
        ("Admin", "Invitar, activar, bloquear comercio: funcional", "funcional"),
    ],
    "Gestión comercial": [
        ("Admin", "Dashboard de gestión de ventas visible", "funcional"),
        ("Admin", "Datos coherentes con pedidos reales", "datos"),
    ],
    "Dashboards": [
        ("Admin", "Metabase dashboards accesibles", "funcional"),
        ("Admin", "Datos actualizados (no de hace semanas)", "datos"),
    ],
    "Pedido Sugerido": [
        ("Admin", "Dashboard de pedido sugerido accesible en Metabase", "funcional"),
        ("Admin", "Métricas del modelo de sugerencias visibles", "datos"),
    ],

    # ── OTROS ──
    "Contacto": [
        ("B2B", "Información de contacto del comercio visible", "funcional"),
        ("B2B", "Datos de contacto correctos", "datos"),
    ],
    "Soporte": [
        ("APP", "Sección de soporte accesible", "funcional"),
        ("APP", "Canal de soporte funcional (chat/email/teléfono)", "funcional"),
    ],
    "Bloqueo de carro en casos de precios anómalos": [
        ("B2B", "Producto con precio < $50: no se puede agregar al carro", "negocio"),
        ("B2B", "Mensaje claro de por qué está bloqueado", "funcional"),
        ("APP", "Mismo bloqueo funcional en APP", "funcional"),
    ],
    "Límite de descuento": [
        ("APP", "Descuento no excede el límite configurado", "negocio"),
        ("APP", "Intentar exceder: mensaje o corrección automática", "funcional"),
    ],
    "Ticket promedio": [
        ("APP", "Ticket promedio visible en datos del comercio", "funcional"),
        ("APP", "Valor coherente con historial de compras", "datos"),
    ],
    "Exportación de datos": [
        ("APP", "Exportar datos: archivo generado", "funcional"),
        ("APP", "Datos exportados completos y correctos", "datos"),
    ],
    "Impresión": [
        ("APP", "Conectar impresora: funcional", "funcional"),
        ("APP", "Imprimir recibo: formato correcto", "funcional"),
    ],
    "Registros de visitas": [
        ("APP", "Listado de visitas anteriores visible", "funcional"),
        ("APP", "Detalle de visita con datos de encuesta", "funcional"),
    ],
    "Resumen de venta": [
        ("APP", "Resumen de ventas del período visible", "funcional"),
        ("APP", "Datos coinciden con pedidos reales", "datos"),
    ],
    "Historial de facturas": [
        ("B2B", "Historial de facturas visible", "funcional"),
        ("APP", "Mismas facturas visibles en APP", "datos"),
    ],
    "Compra mínima": [
        ("B2B", "Pedido por debajo del mínimo: no permite crear", "negocio"),
        ("B2B", "Mensaje claro con el monto mínimo", "funcional"),
    ],
    "Método de pago": [
        ("B2B", "Métodos de pago del cliente configurados y visibles", "funcional"),
    ],
    "Ordenar": [
        ("APP", "Ordenar por precio ascendente: funciona", "funcional"),
        ("APP", "Ordenar por nombre: funciona", "funcional"),
        ("APP", "Cambiar criterio de orden: lista se actualiza", "funcional"),
    ],
    "Regalos": [
        ("APP", "Productos de regalo visibles cuando aplica", "funcional"),
        ("APP", "Regalo se agrega al pedido correctamente", "funcional"),
    ],
    # ── P1: PAGOS Y COBRANZA (nuevos) ──
    "Módulo de pagos": [
        ("B2B", "Sección de pagos visible en menú lateral cuando habilitado", "funcional"),
        ("B2B", "Pagos deshabilitados: sección oculta, rutas devuelven 403", "funcional"),
        ("B2B", "Nuevo módulo de pagos renderiza correctamente", "funcional"),
        ("B2B", "Pago requiere monto completo: pago parcial muestra error", "negocio"),
        ("B2B", "Pago externo: redirect a pasarela, callback correcto", "integración"),
        ("B2B", "Validar pago desde admin: pago cambia a APPROVED", "funcional"),
    ],
    "Notas de crédito": [
        ("Admin", "Generar nota de crédito vinculada a factura", "funcional"),
        ("B2B", "NC visible para comercio en historial", "funcional"),
    ],
    # ── P2: GESTION DE COMERCIOS (nuevos) ──
    "Edición de comercios": [
        ("B2B", "Edición deshabilitada: campos no editables", "funcional"),
        ("B2B", "Edición de dirección: campos editables en checkout, cambio se guarda", "funcional"),
        ("B2B", "Tipo de recibo oculto: selector no visible en checkout", "funcional"),
    ],
    "Alerta de cliente bloqueado": [
        ("B2B", "Comercio bloqueado: popup con alerta HTML personalizada", "funcional"),
        ("B2B", "Comercio no bloqueado: sin popup", "funcional"),
    ],
    # ── P3: PACKAGING Y UNIDADES (nuevos) ──
    "Packaging y empaque": [
        ("B2B", "Info empaque oculta cuando hidePackagingInformationB2B=true", "funcional"),
        ("B2B", "Info empaque single item oculta cuando configurado", "funcional"),
        ("B2B", "Multi-unidad: selector visible, cálculo correcto por unidad", "funcional"),
        ("B2B", "Monto usa unidades en packaging cuando configurado", "negocio"),
        ("B2B", "Info de peso visible en tarjeta y checkout cuando weightInfo=true", "funcional"),
    ],
    # ── P4: POLITICAS DE ORDEN (nuevos) ──
    "Políticas de crédito y deuda": [
        ("B2B", "Bloqueo por deuda vencida: orden bloqueada con mensaje", "negocio"),
        ("B2B", "Retención por deuda: orden retenida, no bloqueada", "negocio"),
        ("B2B", "Status crédito excedido: orden toma status configurado", "negocio"),
        ("B2B", "Orden de compra: campo OC visible y se guarda", "funcional"),
        ("B2B", "Última orden en detalle de compra como referencia rápida", "funcional"),
    ],
    # ── P5: HOOKS E INTEGRACIONES (nuevos) ──
    "Hooks de integración": [
        ("B2B", "Hook de stock: consulta vía hook externo, respuesta integrada", "integración"),
        ("B2B", "Hook de documentos pendientes: obtenidos vía hook", "integración"),
        ("B2B", "Hook de semáforo: actualización correcta vía hook", "integración"),
        ("APP", "Código de transporte: campo visible, se envía al ERP", "integración"),
    ],
    # ── P6: UI Y EXPERIENCIA (nuevos) ──
    "Home y experiencia": [
        ("B2B", "Home habilitado: página con banners/contenido al entrar", "funcional"),
        ("B2B", "Hora estimada de entrega oculta cuando configurado", "funcional"),
        ("B2B", "Footer personalizado: HTML custom renderiza correctamente", "visual"),
        ("B2B", "Botones beta visibles y funcionales cuando habilitado", "funcional"),
        ("B2B", "Texto personalizado en botón confirmar carro", "visual"),
        ("APP", "Filtro de no venta: lista filtra correctamente", "funcional"),
        ("Admin", "Límite de descuento visible cuando configurado", "funcional"),
    ],
}


# ─────────────────────────────────────────────
# Pruebas transversales (siempre se incluyen)
# ─────────────────────────────────────────────

CROSS_CUTTING_TESTS = {
    "Datos y catálogo": [
        ("B2B", "Cantidad total de productos coincide con fuente del cliente (±5%)", "datos"),
        ("B2B", "Revisar 10 productos al azar: nombre, precio e imagen correctos", "datos"),
        ("B2B", "Precios en B2B = precios en fuente del cliente (verificar 5+)", "datos"),
        ("B2B", "Categorías: estructura lógica, no hay vacías", "datos"),
        ("APP", "Catálogo en APP coincide con B2B (mismos productos y precios)", "datos"),
        ("Admin", "Cantidad de productos en Admin = B2B", "datos"),
    ],
    "Consistencia cross-platform": [
        ("B2B+APP", "Precio del mismo producto: igual en B2B y APP", "datos"),
        ("B2B+APP", "Pedido creado en B2B: visible en APP y Admin", "datos"),
        ("B2B+APP", "Pedido creado en APP: visible en B2B y Admin", "datos"),
        ("B2B+APP", "Promoción activa: se aplica tanto en B2B como APP", "datos"),
        ("B2B+APP", "Estado crediticio: consistente entre plataformas", "datos"),
    ],
    "Consola y errores": [
        ("B2B", "Home: abrir DevTools → Console → sin errores rojos", "funcional"),
        ("B2B", "Catálogo: sin errores en consola", "funcional"),
        ("B2B", "Checkout: sin errores en consola", "funcional"),
        ("B2B", "Network: sin requests fallidos (4xx/5xx) en flujo normal", "funcional"),
    ],
    "Performance": [
        ("B2B", "Home carga en < 3 segundos", "funcional"),
        ("B2B", "Catálogo carga en < 3 segundos", "funcional"),
        ("B2B", "Búsqueda responde en < 1 segundo", "funcional"),
        ("B2B", "Agregar al carro responde en < 500ms", "funcional"),
        ("APP", "App abre en < 5 segundos", "funcional"),
    ],
    "UX básica": [
        ("B2B", "Textos en español (no inglés ni placeholders)", "visual"),
        ("B2B", "Mensajes de error descriptivos (no códigos técnicos)", "funcional"),
        ("B2B", "Feedback visual al agregar producto al carro", "funcional"),
        ("B2B", "Confirmación antes de enviar pedido", "funcional"),
        ("B2B", "Navegación intuitiva: siempre se puede volver atrás", "funcional"),
    ],
}


# ─────────────────────────────────────────────
# CSV loading
# ─────────────────────────────────────────────

def load_features(csv_path: Path) -> List[Dict[str, str]]:
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_all_features(csv_path: Path) -> Dict[str, Dict[str, str]]:
    """Carga el CSV completo indexado por Feature name."""
    rows = load_features(csv_path)
    return {r.get("Feature", "").strip(): r for r in rows if r.get("Feature", "").strip()}


def get_all_clients(features: List[Dict[str, str]]) -> Set[str]:
    clients: Set[str] = set()
    for row in features:
        raw = row.get("Cliente", "")
        if raw and raw.strip().lower() != "todos":
            for c in raw.split(","):
                c = c.strip()
                if c:
                    clients.add(c)
    return clients


def get_client_features(features: List[Dict[str, str]], client: str) -> List[Dict[str, str]]:
    client_lower = client.lower()
    result = []
    for row in features:
        raw_client = row.get("Cliente", "").strip()
        feature_name = row.get("Feature", "").strip()
        if not feature_name:
            continue
        if "(deprecad" in feature_name.lower():
            continue

        if not raw_client or raw_client.lower() == "todos":
            result.append(row)
        else:
            for c in raw_client.split(","):
                if c.strip().lower() == client_lower:
                    result.append(row)
                    break
    return result


# ─────────────────────────────────────────────
# Checklist generation
# ─────────────────────────────────────────────

TIPO_EMOJI = {
    "funcional": "⚙️",
    "datos": "📊",
    "edge": "🔀",
    "integración": "🔗",
    "visual": "🎨",
    "negocio": "💼",
}


def generate_checklist(
    client: str,
    client_features: List[Dict[str, str]],
    all_features_data: Optional[Dict[str, Dict[str, str]]] = None,
) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    feature_names = {f.get("Feature", "").strip() for f in client_features}

    # Clasificar features por herramienta
    b2b_features = [f for f in client_features if "B2B" in f.get("Herramientas", "")]
    app_features = [f for f in client_features if "APP" in f.get("Herramientas", "")]
    admin_features = [f for f in client_features if "Admin" in f.get("Herramientas", "")]
    integration_features = [f for f in client_features
                           if f.get("Req. Integración", "").strip().lower() in ("yes", "sí")]

    # Contar pruebas
    total_tests = 0
    for fname in feature_names:
        if fname in TEST_CASES:
            total_tests += len(TEST_CASES[fname])
    for tests in CROSS_CUTTING_TESTS.values():
        total_tests += len(tests)

    lines = [
        f"# QA Checklist — {client}",
        f"**Fecha:** {today}  ",
        f"**Features activas:** {len(client_features)} ({len(b2b_features)} B2B, {len(app_features)} APP, {len(admin_features)} Admin)  ",
        f"**Requieren integración:** {len(integration_features)}  ",
        f"**Casos de prueba:** {total_tests}",
        "",
        "**Tipos de prueba:**  ",
        "⚙️ Funcional — ¿funciona? · 📊 Datos — ¿datos correctos? · 🔀 Edge case — ¿qué pasa si...? · 🔗 Integración — ¿ERP conectado? · 🎨 Visual — ¿se ve bien? · 💼 Regla de negocio — ¿lógica comercial correcta?",
        "",
        "---",
        "",
    ]

    # ── PRE-VUELO ──
    lines.extend([
        "## 1. Pre-vuelo",
        "",
        "| # | Verificación | Cómo validar | ✓ |",
        "|---|---|---|---|",
        "| 1 | Catálogo cargado | Admin → Productos: hay productos del cliente | ☐ |",
        "| 2 | Categorías configuradas | B2B → Navegación: categorías visibles | ☐ |",
        f"| 3 | Precios correctos | Comparar 5 productos con fuente del cliente | ☐ |",
        "| 4 | Branding aplicado | B2B: logo, colores, favicon del cliente | ☐ |",
        "| 5 | Usuarios de prueba | Tener credenciales: comercio + admin + vendedor | ☐ |",
        f"| 6 | Integraciones activas | Confirmar con Analytics — {len(integration_features)} features requieren integración | ☐ |",
        "| 7 | Variables de entorno | Confirmar con Tech que están configuradas | ☐ |",
        "| 8 | `externalAccess` + `verificationconfigs` | MongoDB: `yom-stores.sites.externalAccess = true` y entrada en `yom-production.verificationconfigs` para ese site | ☐ |",
        "| 9 | `enableOrderApproval` | MongoDB: `yom-stores.sites.enableOrderApproval` coincide con lo acordado con el cliente | ☐ |",
        "| 10 | `contactMailingList` | MongoDB: `yom-stores.sites.contactMailingList` tiene al menos un email válido | ☐ |",
        "| 11 | `salesterms` (monto mínimo + días despacho) | MongoDB: `yom-stores.sites.salesterms.order.minTotalPrice` y `delivery.daysOfWeek` correctos según cliente | ☐ |",
        "",
    ])

    # ── PRE-VUELO ERP (solo si el cliente tiene integración) ──
    if integration_features:
        counter = 12
        erp_rows = [
            ("`createOrderHook` configurado", "MongoDB: `yom-api.customers` → `integrationHooks.createOrderHook` tiene URL válida"),
            ("Variables de entorno ERP", "Confirmar con Tech que `{CLIENTE}_URL` y `{CLIENTE}_X_AUTH_TOKEN` están en `environment/index.js`"),
            ("Cronjob de reintento en k8s", "Confirmar con Tech que existe entrada en `k8s/production-ti/values.yaml` para el cliente"),
            ("`customStatusId` correcto (si aplica)", "Confirmar si el cliente requiere estado personalizado para filtrar órdenes en cronjob"),
            ("`updateDeliveryDate` seteado", "Confirmar con Tech si el cliente requiere actualización automática de fecha de entrega (true/false)"),
            ("Secrets de k8s para cronjob", "Confirmar con Tech que `clientId` y `clientSecret` están creados para el nuevo cliente"),
        ]
        lines.append("**Pre-vuelo ERP** (cliente con integración activa):")
        lines.append("")
        lines.append("| # | Verificación | Cómo validar | ✓ |")
        lines.append("|---|---|---|---|")
        for label, how in erp_rows:
            lines.append(f"| {counter} | {label} | {how} | ☐ |")
            counter += 1
        lines.append("")

    # ── ACCESOS ──
    lines.extend([
        "---",
        "",
        "## 2. Accesos",
        "",
        "| # | Test | Herramienta | Pasos | ✓ |",
        "|---|---|---|---|---|",
    ])

    access_tests = [
        ("Login B2B", "B2B", f"Ir a {client.lower()}.youorder.me → credenciales comercio"),
        ("Login Admin", "Admin", "Ir a admin.youorder.me → credenciales admin"),
        ("Login APP", "APP", "Abrir app → credenciales vendedor"),
    ]
    if "Cambio de contraseña" in feature_names:
        access_tests.append(("Cambio de contraseña", "B2B", "Flujo 'olvidé mi contraseña' → email → reset"))
    if "Creación de cuentas" in feature_names:
        access_tests.append(("Registro de comercio", "B2B/APP", "Flujo de registro según método del cliente"))

    for i, (name, tool, steps) in enumerate(access_tests, 1):
        lines.append(f"| {i} | {name} | {tool} | {steps} | ☐ |")
    lines.append("")

    # ── FLUJOS CORE ──
    lines.extend([
        "---",
        "",
        "## 3. Flujos core",
        "",
        "### 3.1 Flujo de compra B2B",
        "",
        "```",
        "Catálogo → Seleccionar producto → Agregar al carro → Revisar carro → Crear pedido → Confirmación",
        "```",
        "",
        "| # | Paso | Qué verificar | ✓ |",
        "|---|---|---|---|",
        "| 1 | Catálogo | Productos visibles, navegables, con precio | ☐ |",
        "| 2 | Detalle producto | Precio, descripción, imagen, botón agregar | ☐ |",
        "| 3 | Agregar al carro | Feedback visual, contador actualiza | ☐ |",
        "| 4 | Carro de compras | Items, cantidades, precios, total correcto | ☐ |",
        "| 5 | Modificar carro | Cambiar cantidad, eliminar item, total recalcula | ☐ |",
        "| 6 | Crear pedido | Botón funciona, no permite doble click | ☐ |",
        "| 7 | Confirmación | Resumen del pedido, número de orden | ☐ |",
        "| 8 | Historial | Pedido aparece en lista con estado correcto | ☐ |",
        "",
        "### 3.2 Flujo de compra APP",
        "",
        "| # | Paso | Qué verificar | ✓ |",
        "|---|---|---|---|",
        "| 1 | Seleccionar comercio | Lista visible, se puede elegir | ☐ |",
        "| 2 | Tomador de pedidos | Catálogo del comercio carga | ☐ |",
        "| 3 | Agregar productos | Cantidad, feedback visual | ☐ |",
        "| 4 | Confirmar pedido | Resumen correcto, confirmación | ☐ |",
        "| 5 | Historial | Pedido aparece con estado | ☐ |",
        "",
    ])

    # ── FEATURES CON CASOS DE PRUEBA ──
    lines.extend([
        "---",
        "",
        "## 4. Features del cliente — Casos de prueba",
        "",
    ])

    # Agrupar por categoría de producto
    categories: Dict[str, List[Dict[str, str]]] = {}
    for f in client_features:
        producto = f.get("Producto", "").strip()
        if not producto:
            producto = "Otros"
        primary = producto.split(",")[0].strip()
        categories.setdefault(primary, []).append(f)

    cat_order = ["Venta", "Marketing", "Recomendaciones", "Fintech",
                 "Ejecución del punto", "Retención", "Otros"]

    seen = set()
    for cat in cat_order:
        if cat not in categories:
            continue
        seen.add(cat)
        feats_in_cat = sorted(categories[cat], key=lambda x: x.get("Feature", ""))

        # Solo incluir categoría si hay al menos 1 feature con test cases
        has_tests = any(f.get("Feature", "").strip() in TEST_CASES for f in feats_in_cat)

        lines.append(f"### {cat}")
        lines.append("")

        for f in feats_in_cat:
            fname = f.get("Feature", "").strip()
            tools = f.get("Herramientas", "").strip() or "—"
            req_int = f.get("Req. Integración", "").strip()
            has_int = req_int.lower() in ("yes", "sí")

            # Obtener detalle de integración del CSV completo
            int_detail = ""
            if has_int and all_features_data and fname in all_features_data:
                raw_req = all_features_data[fname].get("Req. Integración", "").strip()
                if raw_req and raw_req.lower() not in ("yes", "sí", "no"):
                    # Primera línea significativa
                    for line in raw_req.split("\n"):
                        line = line.strip()
                        if line and line.lower() not in ("yes", "sí"):
                            int_detail = line[:120]
                            break

            int_tag = " 🔗" if has_int else ""
            lines.append(f"#### {fname} ({tools}){int_tag}")
            lines.append("")

            if int_detail:
                lines.append(f"> Integración: {int_detail}")
                lines.append("")

            if fname in TEST_CASES:
                lines.append("| # | Herramienta | Caso de prueba | Tipo | ✓ |")
                lines.append("|---|---|---|---|---|")
                for i, (tool, desc, tipo) in enumerate(TEST_CASES[fname], 1):
                    emoji = TIPO_EMOJI.get(tipo, "")
                    lines.append(f"| {i} | {tool} | {desc} | {emoji} {tipo} | ☐ |")
            else:
                # Feature sin test cases predefinidos — generar checklist básico
                lines.append("| # | Herramienta | Caso de prueba | Tipo | ✓ |")
                lines.append("|---|---|---|---|---|")
                lines.append(f"| 1 | {tools} | Feature visible y accesible | ⚙️ funcional | ☐ |")
                lines.append(f"| 2 | {tools} | Funcionalidad principal opera correctamente | ⚙️ funcional | ☐ |")
                if has_int:
                    lines.append(f"| 3 | {tools} | Datos de integración presentes y actualizados | 🔗 integración | ☐ |")

            lines.append("")

    # Categorías no previstas
    for cat, feats in categories.items():
        if cat not in seen:
            lines.append(f"### {cat}")
            lines.append("")
            for f in sorted(feats, key=lambda x: x.get("Feature", "")):
                fname = f.get("Feature", "").strip()
                tools = f.get("Herramientas", "").strip() or "—"
                lines.append(f"#### {fname} ({tools})")
                lines.append("")
                if fname in TEST_CASES:
                    lines.append("| # | Herramienta | Caso de prueba | Tipo | ✓ |")
                    lines.append("|---|---|---|---|---|")
                    for i, (tool, desc, tipo) in enumerate(TEST_CASES[fname], 1):
                        emoji = TIPO_EMOJI.get(tipo, "")
                        lines.append(f"| {i} | {tool} | {desc} | {emoji} {tipo} | ☐ |")
                else:
                    lines.append("| # | Herramienta | Caso de prueba | Tipo | ✓ |")
                    lines.append("|---|---|---|---|---|")
                    lines.append(f"| 1 | {tools} | Feature visible y accesible | ⚙️ funcional | ☐ |")
                    lines.append(f"| 2 | {tools} | Funcionalidad principal opera correctamente | ⚙️ funcional | ☐ |")
                lines.append("")

    # ── INTEGRACIONES ──
    if integration_features:
        lines.extend([
            "---",
            "",
            "## 5. Integraciones",
            "",
        ])

        # Inyección de pedidos (siempre crítica)
        if "Inyectar pedido" in feature_names:
            lines.extend([
                "### Inyección de pedidos al ERP",
                "",
                "| # | Test | Esperado | ✓ |",
                "|---|---|---|---|",
                "| 1 | Crear pedido en B2B | Pedido se crea en YOM | ☐ |",
                "| 2 | Pedido llega al ERP | Confirmar con cliente o logs | ☐ |",
                "| 3 | Tiempo de confirmación | Dentro del SLA configurado | ☐ |",
                "| 4 | Error de ERP | Mensaje descriptivo, no crash | ☐ |",
                "| 5 | Timeout de ERP | Pedido queda pendiente, no se pierde | ☐ |",
                "",
            ])

        lines.extend([
            "### Sincronización de datos",
            "",
            "| Integración | Dirección | Último sync OK | Datos correctos | ✓ |",
            "|---|---|---|---|---|",
            "| Productos/Catálogo | Cliente → YOM | ☐ | ☐ | ☐ |",
            "| Precios/Overrides | Cliente → YOM | ☐ | ☐ | ☐ |",
        ])
        if "Visualización de stock" in feature_names:
            lines.append("| Stock | Cliente → YOM | ☐ | ☐ | ☐ |")
        if "Estados de orden según ERP" in feature_names:
            lines.append("| Estados de orden | ERP → YOM | ☐ | ☐ | ☐ |")
        if any(f.get("Feature", "").strip() in ("Historial de pagos", "Cobranza y facturación", "Recaudación diaria")
               for f in client_features):
            lines.append("| Facturas/Pagos | ERP → YOM | ☐ | ☐ | ☐ |")
        if "Estado crediticio" in feature_names:
            lines.append("| Crédito comercios | Cliente → YOM | ☐ | ☐ | ☐ |")

        lines.extend([
            "",
            "### CronJobs",
            "",
            "| Verificación | Estado | ✓ |",
            "|---|---|---|",
            "| Jobs configurados (confirmar con Analytics) | | ☐ |",
            "| Última ejecución exitosa | | ☐ |",
            "| Horarios según ventana del cliente | | ☐ |",
            "| Sin errores en últimas 48h | | ☐ |",
            "",
        ])

    # ── PRUEBAS TRANSVERSALES ──
    lines.extend([
        "---",
        "",
        "## 6. Pruebas transversales",
        "",
    ])

    for section_name, tests in CROSS_CUTTING_TESTS.items():
        lines.append(f"### {section_name}")
        lines.append("")
        lines.append("| # | Herramienta | Prueba | ✓ |")
        lines.append("|---|---|---|---|")
        for i, (tool, desc, _tipo) in enumerate(tests, 1):
            lines.append(f"| {i} | {tool} | {desc} | ☐ |")
        lines.append("")

    # ── VEREDICTO ──
    lines.extend([
        "---",
        "",
        "## 7. Veredicto — Gate de Rollout",
        "",
        "### Issues encontrados",
        "",
        "| ID | Severidad | Herramienta | Feature | Descripción | Escalado a | Estado |",
        "|---|---|---|---|---|---|---|",
        f"| {client}-QA-001 | | | | | | |",
        f"| {client}-QA-002 | | | | | | |",
        f"| {client}-QA-003 | | | | | | |",
        "",
        "### Criterios de salida",
        "",
        "| Criterio | Obligatorio | Cumple | Notas |",
        "|---|---|---|---|",
        "| Zero issues Critical abiertos | Sí | ☐ | |",
        "| Zero issues High sin plan de resolución | Sí | ☐ | |",
        "| Flujo de compra B2B funcional | Sí | ☐ | |",
        "| Flujo de compra APP funcional | Sí | ☐ | |",
    ])
    if "Inyectar pedido" in feature_names:
        lines.append("| Inyección pedidos ERP funcional | Sí | ☐ | |")
    lines.extend([
        "| Catálogo con datos del cliente | Sí | ☐ | |",
        "| Health Score >= 80% | Sí | ☐ | Score: ___ |",
        "",
        "### Health Score",
        "",
        "| Categoría | Peso | Score (0-100) | Ponderado |",
        "|---|---|---|---|",
        "| Flujos core | 30% | | |",
        "| Datos y catálogo | 20% | | |",
        "| Integraciones | 20% | | |",
        "| Features del cliente | 15% | | |",
        "| UX y visual | 10% | | |",
        "| Performance | 5% | | |",
        "| **TOTAL** | **100%** | | **___** |",
        "",
        "### Veredicto final",
        "",
        "☐ **LISTO** — Todos los criterios obligatorios cumplidos, Health Score >= 80%  ",
        "☐ **LISTO CON CONDICIONES** — Criterios cumplidos, issues Medium pendientes  ",
        "☐ **NO APTO** — Algún criterio obligatorio no cumplido  ",
        "",
        "**Condiciones (si aplica):**",
        "1. ",
        "2. ",
        "",
        "**Próximos pasos:**",
        "",
        "| Acción | Responsable | Plazo |",
        "|---|---|---|",
        "| | | |",
        "",
        "---",
        "",
        f"*Generado: {today} | Cliente: {client} | Casos de prueba: {total_tests}*",
    ])

    return "\n".join(lines)


# ─────────────────────────────────────────────
# MongoDB source: variable → feature mapping
# ─────────────────────────────────────────────

# Variables with inverted logic (feature active when value is False)
INVERTED_VARIABLES = {
    "disableObservationInput",
    "disableManualDiscount",
    "disablePayments",
    "disableWrongPrices",
    "disableCart",
    "disableCommerceEdit",
    "disableShowEstimatedDeliveryHour",
}

# Mapping: feature name → list of variables that indicate the feature is active
FEATURE_TO_VARIABLES: Dict[str, List[str]] = {
    "Agregar fecha despacho": ["enableAskDeliveryDate"],
    "Agregar observaciones": ["disableObservationInput"],
    "Bloqueo": ["blockedClientAlert.enableBlockedClientAlert"],
    "Bloqueo de carro en casos de precios anómalos": ["wrongPrices.block", "disableWrongPrices"],
    "Botones de acceso configurables (deprecado)": ["enableBetaButtons"],
    "Cambio de contraseña": ["mobileAccess.passwordDisabled"],
    "Cambios de formato": ["enableChooseSaleUnit", "hasMultiUnitEnabled"],
    "Canasta base": ["filterGroupedSuggestionsBy", "productList.enableSuggestionByCategories"],
    "Canasta Estratégica: Exploración": ["productList.enableSuggestionByCategories"],
    "Cobranza y facturación": ["enablePaymentsCollection", "enablePayments", "enablePaymentDocumentsB2B", "pendingDocuments"],
    "Compra mínima": ["showMinOne"],
    "Creación de cuentas": ["commerce.enableCreateCommerce"],
    "Cupón de descuento": ["enableCoupons"],
    "Descuentos manuales": ["enableSellerDiscount", "disableManualDiscount"],
    "Descuentos por volumen": ["useNewPromotions"],
    "Documentos manuales": ["pendingDocuments", "enablePaymentDocumentsB2B"],
    "Estado crediticio": ["enableCreditStateMessage", "hooks.updateTrafficLightHook"],
    "Estados de orden según ERP": ["enableOrderValidation", "hooks.shippingHook"],
    "FAQ": ["footerCustomContent.useFooterCustomContent"],
    "Filtros de comercios": ["hasNoSaleFilter"],
    "Funcionamiento offline": ["synchronization.enableBackgroundSync", "synchronization.enableBackgroundSendOrders"],
    "Georreferencia": ["useMobileGps"],
    "Gestión de pedidos": ["enableMassiveOrderSend", "enableOrderApproval", "ordersRequireAuthorization"],
    "Gestión de tareas": ["enableTask"],
    "Historial de facturas": ["enableInvoicesList", "enablePaymentDocumentsB2B"],
    "Historial de pagos": ["enablePayments", "enablePaymentsCollection"],
    "Impresión": ["hasVoucherPrinterEnabled"],
    "Impuestos para productos": ["includeTaxRateInPrices", "taxes.useTaxRate"],
    "Inyectar pedido": ["hooks.shippingHook"],
    "Justificaciones": ["enableDialogNoSellReason"],
    "Limitación productos": ["limitAddingByStock"],
    "Límite de descuento": ["enableSellerDiscount", "adminConfiguration.showDiscountLimitAdmin"],
    "Lista categorías": ["showEmptyCategories"],
    "Lista de comercios": ["commerce.enableCreateCommerce", "disableCommerceEdit"],
    "Listas de precio": ["useMongoPricing", "mustHaveOverride"],
    "Log in App": ["mobileAccess.passwordDisabled"],
    "Log in B2B": ["anonymousAccess", "externalAccess"],
    "Método de pago": ["enablePayments", "disablePayments", "payment.enableNewPaymentModule"],
    "Notificaciones y alertas": ["blockedClientAlert.enableBlockedClientAlert"],
    "Pedido Sugerido": ["filterGroupedSuggestionsBy", "productList.enableSuggestionByCategories"],
    "Precio despacho": ["hooks.shippingHook", "disableShowEstimatedDeliveryHour"],
    "Precio futuro": ["enablePriceOracle"],
    "Precio unitario": ["weightInfo"],
    "Precios brutos o neto": ["includeTaxRateInPrices", "taxes.useTaxRate"],
    "Promociones de catálogo": ["useNewPromotions"],
    "Promociones personalizadas": ["useNewPromotions"],
    "Re-hacer un pedido anterior": ["shoppingDetail.lastOrder"],
    "Recaudación diaria": ["enablePaymentsCollection"],
    "Redirección a pago de facturas": ["enablePayments", "payment.externalPayment", "enablePaymentDocumentsB2B"],
    "Registros de visitas": ["enableTask"],
    "Selección de método de pago": ["enablePayments", "disablePayments", "hideReceiptType", "payment.enableNewPaymentModule"],
    "Sincronización de sistemas": ["synchronization.enableBackgroundSync", "synchronization.enableBackgroundSendOrders", "synchronization.enableSyncImages"],
    "Transferencia de pedidos": ["enableMassiveOrderSend"],
    "Visibilidad y acceso al catálogo": ["anonymousAccess", "anonymousHideCart", "anonymousHidePrice", "externalAccess"],
    "Visualización de datos comercio": ["enableCreditStateMessage"],
    "Visualización de stock": ["hasStockEnabled", "hooks.stockHook"],
    # New P1-P6 features
    "Módulo de pagos": ["enablePayments", "disablePayments", "payment.enableNewPaymentModule", "payment.requiresFullPayment", "payment.externalPayment", "validatePaymentFromAdmin"],
    "Notas de crédito": ["enableCreditNotes"],
    "Edición de comercios": ["disableCommerceEdit", "editAddress", "hideReceiptType"],
    "Alerta de cliente bloqueado": ["blockedClientAlert.enableBlockedClientAlert"],
    "Packaging y empaque": ["packagingInformation.hidePackagingInformationB2B", "hasMultiUnitEnabled", "packaging.amountUsesUnits", "weightInfo"],
    "Políticas de crédito y deuda": ["orderPolicy.overdueDebtConfiguration.blockSettings.enabled", "orderPolicy.retainCreditBlockedCommerces", "purchaseOrderEnabled", "shoppingDetail.lastOrder"],
    "Hooks de integración": ["hooks.stockHook", "hooks.getPendingDocumentsHook", "hooks.updateTrafficLightHook", "hasTransportCode"],
    "Home y experiencia": ["enableHome", "disableShowEstimatedDeliveryHour", "footerCustomContent.useFooterCustomContent", "enableBetaButtons", "confirmCartText", "hasNoSaleFilter"],
}

# Base features (always active, no variable check needed)
BASE_FEATURES = [
    "Catálogo", "Crear pedido", "Carro de compras", "Búsqueda de productos",
    "Historial de pedidos", "Seguimiento de pedidos", "Detalle del producto",
    "Filtros de productos", "Ordenar", "Contacto", "Soporte",
]


def is_variable_active(var_name: str, value: Any) -> bool:
    """Check if a variable's value means the feature is active."""
    if var_name in INVERTED_VARIABLES:
        if isinstance(value, bool):
            return not value
        return not value

    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() not in ("", "false", "0", "no", "null", "none", "[]")
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, list):
        return len(value) > 0
    if value is None:
        return False
    return bool(value)


def load_from_mongo_matrix(json_path: Path, client_name: str) -> Optional[List[Dict[str, str]]]:
    """
    Load client features from qa-matrix.json (generated by mongo-extractor.py).
    Returns a list of feature dicts compatible with the CSV format.
    """
    if not json_path.exists():
        return None

    with open(json_path, "r", encoding="utf-8") as f:
        matrix = json.load(f)

    # Find the client in the matrix
    client_data = None
    client_lower = client_name.lower()
    for _key, data in matrix.get("clients", {}).items():
        if client_lower in data.get("name", "").lower() or client_lower in data.get("domain", "").lower():
            client_data = data
            break

    if not client_data:
        return None

    variables = client_data.get("variables", {})

    # Determine active features
    active_features: List[Dict[str, str]] = []

    # Add base features (always active)
    for fname in BASE_FEATURES:
        active_features.append({
            "Feature": fname,
            "Herramientas": "B2B, APP",
            "Producto": "Venta",
            "Cliente": client_name,
            "Req. Integración": "",
        })

    # Check variable-based features
    for fname, var_list in FEATURE_TO_VARIABLES.items():
        if not var_list:
            # No variables = base feature, already added
            continue

        # Feature is active if ANY mapped variable is active
        is_active = any(
            is_variable_active(var_name, variables.get(var_name))
            for var_name in var_list
            if var_name in variables
        )

        if is_active:
            # Determine herramientas from test cases
            tools_set: Set[str] = set()
            if fname in TEST_CASES:
                for tool, _desc, _tipo in TEST_CASES[fname]:
                    tools_set.add(tool)
            herramientas = ", ".join(sorted(tools_set)) if tools_set else "B2B"

            active_features.append({
                "Feature": fname,
                "Herramientas": herramientas,
                "Producto": "Venta",
                "Cliente": client_name,
                "Req. Integración": "Sí" if any(v.startswith("hooks.") for v in var_list) else "",
            })

    return active_features


def list_mongo_clients(json_path: Path) -> None:
    """List all clients available in qa-matrix.json."""
    if not json_path.exists():
        print(f"Error: No se encontró {json_path}", file=sys.stderr)
        print("Ejecuta primero: python data/mongo-extractor.py", file=sys.stderr)
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        matrix = json.load(f)

    print(f"Clientes en qa-matrix.json (extraído: {matrix.get('extractedAt', '?')}):\n")
    for _key, data in sorted(matrix.get("clients", {}).items(), key=lambda x: x[1]["name"]):
        tc = data.get("testCount", {})
        print(f"  {data['name']:25s} {data['domain']:35s} {tc.get('total', 0)} tests")
    print(f"\nTotal: {len(matrix.get('clients', {}))} clientes")


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="Genera checklist de QA completo por cliente YOM."
    )
    ap.add_argument("--cliente", help="Nombre del cliente (ej: Soprole, Bidfood)")
    ap.add_argument("--output", "-o", help="Ruta de salida (default: stdout)")
    ap.add_argument("--csv", help="Ruta al CSV de features (override default)")
    ap.add_argument("--source", choices=["csv", "mongo"], default="csv",
                    help="Fuente de datos: csv (default) o mongo (lee qa-matrix.json)")
    ap.add_argument("--list-clientes", action="store_true", help="Lista todos los clientes")

    args = ap.parse_args()

    # MongoDB source
    if args.source == "mongo":
        if args.list_clientes:
            list_mongo_clients(QA_MATRIX_JSON)
            return

        if not args.cliente:
            print("Error: --cliente requerido. Usa --list-clientes para ver opciones.", file=sys.stderr)
            sys.exit(1)

        client_features = load_from_mongo_matrix(QA_MATRIX_JSON, args.cliente)
        if client_features is None:
            print(f"Error: Cliente '{args.cliente}' no encontrado en {QA_MATRIX_JSON}", file=sys.stderr)
            print("Ejecuta primero: python data/mongo-extractor.py", file=sys.stderr)
            sys.exit(1)

        checklist = generate_checklist(args.cliente, client_features)

        if args.output:
            out = Path(args.output)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(checklist, encoding="utf-8")
            print(f"Checklist generado: {out}")
            print(f"  Fuente: MongoDB (qa-matrix.json)")
            print(f"  Features: {len(client_features)}")
        else:
            print(checklist)
        return

    # CSV source (default)
    csv_path = Path(args.csv) if args.csv else FEATURES_CSV

    if not csv_path.exists():
        print(f"Error: No se encontró el CSV en {csv_path}", file=sys.stderr)
        sys.exit(1)

    features = load_features(csv_path)

    if args.list_clientes:
        clients = sorted(get_all_clients(features))
        print("Clientes disponibles:")
        for c in clients:
            count = len(get_client_features(features, c))
            print(f"  {c:20s} ({count} features)")
        print(f"\nTotal: {len(clients)} clientes")
        return

    if not args.cliente:
        print("Error: --cliente requerido. Usa --list-clientes para ver opciones.", file=sys.stderr)
        sys.exit(1)

    client_features = get_client_features(features, args.cliente)

    # Cargar CSV completo para detalles de integración
    all_data = None
    if FEATURES_CSV_ALL.exists():
        all_data = load_all_features(FEATURES_CSV_ALL)

    checklist = generate_checklist(args.cliente, client_features, all_data)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(checklist, encoding="utf-8")
        print(f"Checklist generado: {out}")
        print(f"  Features: {len(client_features)}")
    else:
        print(checklist)


if __name__ == "__main__":
    main()
