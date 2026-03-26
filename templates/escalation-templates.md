# Templates de Escalamiento — QA YOM

> Copiar, rellenar campos entre {}, enviar por Slack.

---

## Bug de código → Tech (Rodrigo / Diego C)

**Canal:** `#tech`

```
Bug QA — {CLIENTE}

Severidad: {Critical/High/Medium}
Herramienta: {B2B/APP/Admin}
Feature: {nombre del feature}

Qué pasa:
{descripción del problema}

Pasos para reproducir:
1. Ir a {url}
2. {acción}
3. {resultado inesperado}

Esperado: {lo que debería pasar}
Actual: {lo que pasa}

URL: {slug}.youorder.me{/ruta}
Screenshot: [adjunto]

ID: {CLIENTE}-QA-{NUM}
Bloquea rollout: {Sí/No}
```

---

## Datos incorrectos → Analytics (Diego F / Nicole)

**Canal:** `#datos`

```
Issue de datos QA — {CLIENTE}

Tipo: {Productos faltantes / Precios incorrectos / Sync desactualizado / Categorías mal mapeadas}

Detalle:
{descripción}

Ejemplo:
- Producto: {nombre o SKU}
- En YOM: {lo que muestra}
- Esperado (fuente cliente): {lo que debería ser}

¿Último sync exitoso?: {fecha/hora si se sabe}

ID: {CLIENTE}-QA-{NUM}
Bloquea rollout: {Sí/No}
```

---

## Configuración → Tech (Rodrigo / Diego C)

**Canal:** `#tech`

```
Config QA — {CLIENTE}

Feature afectada: {nombre}
Tipo: {Variable de entorno / Feature flag / Config de store}

Qué falta o está mal:
{descripción}

Variable (si se conoce): {nombre}

ID: {CLIENTE}-QA-{NUM}
```

---

## Contenido del cliente → CS (Max) → Cliente

**Canal:** `#pem`

```
Contenido pendiente QA — {CLIENTE}

Necesitamos del cliente:
- [ ] {ej: Logo en alta resolución}
- [ ] {ej: Imágenes de productos}
- [ ] {ej: Textos para FAQ}

Contexto: Estamos en QA (Fase 8), esto es necesario para {completar branding / tener catálogo completo}.

Prioridad: {Alta — bloquea rollout / Media — recomendado}
```

---

## Integración ERP → Analytics + Tech

**Canal:** `#integraciones`

```
Issue integración QA — {CLIENTE}

Integración: {Inyección pedidos / Sync productos / Estados orden}
Método: {API / SFTP / Webhook / CronJob}

Problema:
{descripción}

Evidencia:
- Pedido ID: {id}
- ¿Llegó al ERP?: {Sí/No/Timeout}
- Error: {mensaje si hay}
- Hora: {timestamp}

ID: {CLIENTE}-QA-{NUM}
Bloquea rollout: Sí — sin inyección de pedidos no se puede operar
```

---

## Feature no disponible → Producto (Alejandro)

**Canal:** `#producto`

```
Feature request QA — {CLIENTE}

Feature: {nombre}
Situación: {qué existe hoy vs qué necesita el cliente}
¿En scope del contrato?: {Sí/No/No claro}
Impacto si no está para rollout: {descripción}

ID: {CLIENTE}-QA-{NUM}
```
