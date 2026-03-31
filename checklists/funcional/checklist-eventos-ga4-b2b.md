# Checklist QA — Eventos GA4 del B2B

> Fuente: [[B2B] Eventos registrados](https://www.notion.so/2bdd8139ba4e80d0aeddc9f861d92b79)
> Total: 62 eventos GA4 en 16 categorías
> Fecha creación: 2026-03-27

---

## Contexto

El B2B tiene 62 eventos GA4 implementados. Podemos validar que los eventos se disparan correctamente interceptando las llamadas a GA4 en los tests E2E. Los más críticos son los del funnel de conversión.

---

## 1. Funnel de conversión (prioridad máxima)

> `cart_view` → `checkout_start` → `create_order` → `payment_success`

| # | Evento | Trigger | Dónde validar | Estado |
|---|--------|---------|--------------|--------|
| GA-01 | `cart_view` | Cargar página de carrito con items | `cart/view.tsx` | PENDIENTE |
| GA-02 | `checkout_start` | Click "Confirmar pedido" | `cart-create-base-button.tsx` | PENDIENTE |
| GA-03 | `create_order` | Orden creada exitosamente | `cart-create-base-button.tsx` | PENDIENTE |
| GA-04 | `payment_start` | Redirect a pasarela de pago | `payment/page.tsx` | PENDIENTE |
| GA-05 | `payment_success` | Página de confirmación carga | `confirmation/[uuid]/view.tsx` | PENDIENTE |
| GA-06 | `payment_failed` | Página de cancelación carga | `payment/cancel/page.tsx` | PENDIENTE |
| GA-07 | `cart_abandon` | 5 min sin comprar con items en carro | `cart/view.tsx` | PENDIENTE |

---

## 2. Carrito (12 eventos — alta prioridad)

| # | Evento | Trigger | Estado |
|---|--------|---------|--------|
| GA-10 | `add_product` | Agregar producto al carro | PENDIENTE |
| GA-11 | `remove_product` | Eliminar producto del carro | PENDIENTE |
| GA-12 | `modify_product` | Modificar producto (sin cambio packaging) | PENDIENTE |
| GA-13 | `cart_item_quantity_change` | Cambiar cantidad | PENDIENTE |
| GA-14 | `change_packaging` | Cambiar tipo de empaque | PENDIENTE |
| GA-15 | `clear_cart` | Vaciar carrito completo | PENDIENTE |
| GA-16 | `apply_coupon` | Aplicar cupón exitosamente | PENDIENTE |
| GA-17 | `open_pre_cart` | Abrir carrito lateral (drawer) | PENDIENTE |
| GA-18 | `cart_delivery_address_change` | Cambiar dirección de entrega | PENDIENTE |
| GA-19 | `cart_delivery_date_change` | Cambiar fecha de entrega | PENDIENTE |

---

## 3. Auth (7 eventos)

| # | Evento | Trigger | Estado |
|---|--------|---------|--------|
| GA-20 | `login_success` | Login exitoso | PENDIENTE |
| GA-21 | `register_success` | Registro exitoso | PENDIENTE |
| GA-22 | `logout` | Cerrar sesión | PENDIENTE |
| GA-23 | `start_login` | Click en "Iniciar sesión" | PENDIENTE |
| GA-24 | `social_login_attempt` | Login con Google/Facebook | PENDIENTE |

---

## 4. Catálogo (9 eventos)

| # | Evento | Trigger | Estado |
|---|--------|---------|--------|
| GA-30 | `search` | Búsqueda en catálogo | PENDIENTE |
| GA-31 | `search_no_results` | Búsqueda sin resultados | PENDIENTE |
| GA-32 | `filter_category` | Filtrar por categoría | PENDIENTE |
| GA-33 | `filter_featured` | Filtrar productos destacados | PENDIENTE |
| GA-34 | `filter_promotion` | Filtrar productos en promoción | PENDIENTE |
| GA-35 | `filter_suggestions` | Filtrar sugerencias | PENDIENTE |
| GA-36 | `pagination_change` | Cambiar de página | PENDIENTE |

---

## 5. Errores (3 eventos — regresión)

| # | Evento | Trigger | Estado |
|---|--------|---------|--------|
| GA-40 | `error_404` | Navegar a página inexistente | PENDIENTE |
| GA-41 | `error_500` | Error del servidor | PENDIENTE |
| GA-42 | `error_boundary_triggered` | ErrorBoundary captura error | PENDIENTE |

---

## Cómo validar en Playwright

Los eventos GA4 se pueden interceptar así:

```typescript
// Interceptar llamadas a GA4
const ga4Events: string[] = [];
page.on('request', (req) => {
  if (req.url().includes('google-analytics') || req.url().includes('gtag')) {
    ga4Events.push(req.url());
  }
});

// ... realizar acción ...

// Verificar que el evento se disparó
expect(ga4Events.some(url => url.includes('add_product'))).toBeTruthy();
```

---

## Notas

- Los eventos de vista usan `useRef` para dispararse una vez por sesión — verificar que no se disparen duplicados
- `cart_abandon` tiene delay de 5 min — difícil de testear en E2E, verificar con timer mock
- Los eventos de scroll usan milestones (25%, 50%, 75%, 90%, 100%)
