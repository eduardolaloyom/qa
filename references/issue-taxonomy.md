# Taxonomía de Issues — QA YOM

## Severidades

| Nivel | Definición | Respuesta | Bloquea rollout |
|---|---|---|---|
| **Critical** | Cliente no puede operar | Inmediato | Sí |
| **High** | Feature importante rota | Mismo día | Sí (sin plan) |
| **Medium** | Afecta experiencia, hay workaround | 48h | No |
| **Low** | Cosmético | Backlog | No |

### Ejemplos

**Critical:** Login roto, crear pedido falla, catálogo vacío, precios $0/NaN, app crashea, inyección ERP totalmente rota.

**High:** Búsqueda no retorna resultados, promociones no aplican, precios incorrectos, canasta base vacía, estado crediticio erróneo, sync desactualizado >24h.

**Medium:** Imágenes no cargan, categorías desordenadas, filtros fallan, banners con links rotos, labels no aparecen.

**Low:** Favicon faltante, placeholders visibles, espaciado inconsistente, FAQ genérica.

---

## Categorías y escalamiento

| Categoría | Señales | Escalar a | Canal |
|---|---|---|---|
| **Bug de código** | Error JS, crash, cálculo incorrecto | Tech (Rodrigo/Diego C) | `#tech` |
| **Datos** | Productos faltantes, precios incorrectos, categorías vacías | Analytics (Diego F/Nicole) | `#datos` |
| **Configuración** | Feature inactiva, variable faltante, flag off | Tech (Rodrigo/Diego C) | `#tech` |
| **Integración** | Pedido no llega a ERP, sync falla, timeout | Analytics + Tech | `#integraciones` |
| **Contenido** | Logo faltante, FAQ de otro cliente, imágenes genéricas | CS (Max) → Cliente | `#pem` |
| **Feature** | Funcionalidad requerida no existe | Producto (Alejandro) | `#producto` |
| **Consola/Errores** | Excepciones JS, requests 4xx/5xx, CORS, mixed content | Tech (Rodrigo/Diego C) | `#tech` |
| **Accesibilidad** | Alt text faltante, contraste insuficiente, keyboard nav rota | Tech + Producto | `#tech` |

---

## Detalle por categoría nueva

### Consola/Errores

Qué buscar en DevTools → Console y Network:

| Tipo | Qué es | Impacto |
|---|---|---|
| Excepciones JS no capturadas | `Uncaught TypeError`, `Cannot read property of undefined` | Funcionalidad rota silenciosamente |
| Requests fallidos (4xx/5xx) | API returns 500, imagen 404, recurso 403 | Datos faltantes o features rotas |
| Errores CORS | `Access-Control-Allow-Origin` bloqueado | Integraciones o APIs externas no cargan |
| Mixed content | Recursos HTTP en página HTTPS | Browsers bloquean, contenido no carga |
| Deprecation warnings | APIs del browser o librerías obsoletas | Funcionará hoy, romperá mañana |

### Accesibilidad

Verificaciones mínimas para B2B y APP:

| Verificación | Cómo validar | Ejemplo de fallo |
|---|---|---|
| Alt text en imágenes | Inspeccionar `<img>` — debe tener `alt` descriptivo | Imagen de producto sin alt, lector de pantalla dice "image" |
| Labels en formularios | Cada `<input>` debe tener `<label>` asociado | Campo de email sin label, lector no sabe qué llenar |
| Navegación por teclado | Tab por toda la página — todos los elementos interactivos deben ser alcanzables | Botón "Agregar al carrito" no recibe focus con Tab |
| Contraste de colores | Texto vs fondo debe tener ratio >= 4.5:1 (WCAG AA) | Texto gris claro sobre fondo blanco, ilegible |
| Focus visible | Al tabular, el elemento activo debe tener borde o highlight visible | Tab pasa por botones pero no se ve cuál está seleccionado |
| ARIA en componentes dinámicos | Modales, dropdowns, alerts deben tener `role` y `aria-*` correctos | Modal se abre pero lector de pantalla no lo anuncia |

---

## Checklist de exploración por página

1. **¿Carga?** — < 3 segundos, sin errores
2. **¿Se ve bien?** — Layout, branding del cliente, sin elementos rotos
3. **¿Datos correctos?** — Productos, precios, nombres presentes
4. **¿Funciona?** — Botones, links, formularios
5. **¿Consola limpia?** — DevTools → Console sin errores rojos, Network sin 4xx/5xx
6. **¿Es usable?** — Feedback, mensajes claros, navegación intuitiva
7. **¿Accesible?** — Tab navega todo, imágenes tienen alt, contraste legible, labels en inputs
