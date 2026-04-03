# Referencia Rápida — B2B UI Selectores

Basado en exploración de YOMCL/b2b (Next.js + MUI v5).

## Rutas clave

```
/auth/jwt/login          → Login page
/products                → Catálogo
/cart                    → Carrito
/confirmation/{uuid}     → Confirmación
```

## Selectores principales

### Login
```
input[name="email"]                    # Email
input[name="password"]                 # Password
button[type="submit"]                  # Iniciar sesión
a[href*="/jwt/recover"]                # Recuperar contraseña
```

### Catálogo
```
input[placeholder="Buscar productos"]  # Search
button[class*="add-new-product-to-cart-button"]  # Agregar
button[class*="add-new-product-variant-to-cart-button"]  # Seleccionar (variantes)
input[data-testid="cart-quantity"]     # Cantidad en carrito
button[data-testid="add-to-cart"]      # Increment
button[class*="decrement-to-cart-button"]  # Decrement
```

### Carrito
```
button[data-testid="side-cart-button"]  # Botón carrito header
div[data-testid="side-cart-list"]      # Lista de items
input[placeholder="Ingresar cupón"]    # Cupón
button:has-text("Aplicar")             # Aplicar cupón
button:has-text("Confirmar pedido")    # Checkout
textarea[placeholder*="notas especiales"]  # Observaciones
```

## Labels exactos (en español)

| Elemento | Texto |
|----------|-------|
| Email label | "Correo" |
| Password label | "Contraseña" |
| Recover link | "¿Olvidaste la contraseña?" |
| Login button | "Iniciar sesión" |
| Add button | "Agregar" |
| Select button | "Seleccionar" |
| Out of stock | "Sin stock" |
| Coupon label | "Ingresar cupón" |
| Apply button | "Aplicar" |
| Checkout button | "Confirmar pedido" |
| Go to cart | "Ir al carrito" |

## Componentes con data-testid

| Component | data-testid |
|-----------|------------|
| Catalog page | `catalog-page` |
| Cart quantity | `cart-quantity` |
| Add to cart (increment) | `add-to-cart` |
| Side cart button | `side-cart-button` |
| Side cart list | `side-cart-list` |
| Product detail modal | `product-detail-modal` |

## Clases CSS importantes

| Elemento | Clase contiene |
|----------|---|
| Product card | `StyledProductCard` |
| Add button (single) | `add-new-product-to-cart-button` |
| Add button (variant) | `add-new-product-variant-to-cart-button` |
| Increment button | `increment-to-cart-button` |
| Decrement button | `decrement-to-cart-button` |
| Eye toggle | `eye` o `solar-eye` |

## Parámetros de URL

```
/products?name=arroz&category=cereales&suggestions=1
```

- `name`: término de búsqueda
- `category`: categorías separadas por |
- `suggestions`: flag para mostrar recomendaciones
- Otros: custom filters del tenant

## Validaciones pre-checkout

```typescript
- isOrderValid: total >= minOrderTotal
- isBlocked: cuenta suspendida
- !commerce?.contact?.externalId: contacto no configurado
- isDeliveryDateLoading: esperando fechas
```

## Flags de acceso anónimo

De `useStore()`:
- `anonymousAccess`: permite ver sin login
- `anonymousHidePrice`: oculta precios si anónimo
- `anonymousHideCart`: oculta carrito si anónimo

## Flujo de compra típico

1. Login → `/auth/jwt/login`
2. Browse → `/products?name=...`
3. Add items → click agregar botones
4. Open cart → click side-cart-button
5. Review → `/cart`
6. Apply coupon → "Ingresar cupón" + "Aplicar"
7. Checkout → "Confirmar pedido"
8. Confirm → `/confirmation/{orderId}`

## Estructura de directorios clave

```
src/
├── app/(authenticated)/
│   ├── products/          → catálogo
│   ├── cart/              → carrito
│   └── confirmation/      → confirmación
├── components/
│   ├── sections/auth/     → login, registro
│   ├── cards/product/     → tarjetas producto
│   └── minimals/layouts/  → header, cart drawer
└── lib/
    ├── hooks/             → useCart, useAuth, useStore
    ├── contexts/          → CartContext, AuthContext
    └── services/          → cart, auth APIs
```

## Asertions comunes

```typescript
// URL
await expect(page).toHaveURL(/\/products/);
await expect(page).toHaveURL(/\/confirmation\/[a-f0-9-]+/);

// Visibilidad
await expect(element).toBeVisible();
await expect(element).toBeHidden();

// Estado
await expect(button).toBeDisabled();
await expect(input).toHaveValue('text');
await expect(button).toHaveAttribute('aria-busy', 'true');

// Contenido
await expect(element).toContainText('Agregar');
await expect(element).not.toHaveCount(0);
```

## Tips Playwright

1. Use `.locator()` en lugar de `.querySelector()`
2. Siempre `.waitFor()` para elementos async
3. MUI puede tener clases dinámicas → use `[class*="..."]`
4. Esperar debounce: `page.waitForTimeout(300)` después de input
5. Fill inputs: `input.fill()` + `input.blur()` para guardar
6. Click en texto: `button:has-text("Texto exacto")`

