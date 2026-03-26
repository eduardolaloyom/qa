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

---

## Checklist de exploración por página

1. **¿Carga?** — < 3 segundos, sin errores
2. **¿Se ve bien?** — Layout, branding del cliente, sin elementos rotos
3. **¿Datos correctos?** — Productos, precios, nombres presentes
4. **¿Funciona?** — Botones, links, formularios
5. **¿Consola limpia?** — DevTools sin errores rojos
6. **¿Es usable?** — Feedback, mensajes claros, navegación intuitiva
