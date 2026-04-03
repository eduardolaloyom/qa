# Referencia B2B — YOM UI, Selectores y Código Playwright

Documento único de referencia para testing de la tienda B2B (`{slug}.youorder.me`).  
Stack: **Next.js 14+ App Router + MUI v5**

---

## 1. Quick Reference

### Rutas clave

```
/auth/jwt/login          → Login
/products                → Catálogo
/cart                    → Carrito
/orders                  → Historial de pedidos
/confirmation/{uuid}     → Confirmación de pedido
/payment-documents       → Facturas / guías
/khipu-payments          → Pagos Khipu
/profile                 → Perfil de usuario
```

### Selectores principales

| Elemento | Selector |
|----------|----------|
| Email input | `input[name="email"]` |
| Password input | `input[name="password"]` |
| Submit login | `button[type="submit"]` |
| Recuperar contraseña | `a[href*="/jwt/recover"]` |
| Search input | `input[placeholder="Buscar productos"]` |
| Product card | `div[class*="StyledProductCard"]` |
| Botón agregar (simple) | `button[class*="add-new-product-to-cart-button"]` |
| Botón agregar (variante) | `button[class*="add-new-product-variant-to-cart-button"]` |
| Cantidad en carrito | `input[data-testid="cart-quantity"]` |
| Increment | `button[data-testid="add-to-cart"]` |
| Decrement | `button[class*="decrement-to-cart-button"]` |
| Side cart button | `button[data-testid="side-cart-button"]` |
| Side cart list | `div[data-testid="side-cart-list"]` |
| Cupón input | `input[placeholder="Ingresar cupón"]` o label "Ingresar cupón" |
| Aplicar cupón | `button:has-text("Aplicar")` |
| Confirmar pedido | `button:has-text("Confirmar pedido")` |
| Notas especiales | `textarea[placeholder*="notas especiales"]` |

### Labels exactos (en español)

| Elemento | Texto |
|----------|-------|
| Email label | "Correo" |
| Password label | "Contraseña" |
| Recover link | "¿Olvidaste la contraseña?" |
| Login button | "Iniciar sesión" |
| Add button | "Agregar" |
| Select button (variantes) | "Seleccionar" |
| Out of stock | "Sin stock" |
| Apply coupon | "Aplicar" |
| Checkout | "Confirmar pedido" |
| Go to cart | "Ir al carrito" |
| Khipu payment | "Pagar con Khipu" |

### Componentes con data-testid

| Component | data-testid |
|-----------|-------------|
| Catalog page | `catalog-page` |
| Cart quantity | `cart-quantity` |
| Add to cart (increment) | `add-to-cart` |
| Side cart button | `side-cart-button` |
| Side cart list | `side-cart-list` |
| Product detail modal | `product-detail-modal` |

---

## 2. Component Mapping (Arquitectura UI)

### Stack técnico

| Componente | Tecnología |
|-----------|-----------|
| Framework | Next.js 14+ (App Router) |
| UI Library | Material-UI (MUI) v5 |
| Form Library | React Hook Form + MUI integration (RHFTextField) |
| Estado | React Hooks (useCart, useAuth, useStore, useSettings) |
| HTTP Client | Axios (custom interceptors, JWT auth) |
| Estilos | MUI `sx` prop + Styled Components |

### Login — `/auth/jwt/login`

- **Archivo**: `src/components/sections/auth/views/auth-login-view.tsx`
- **Form**: `src/components/sections/auth/components/local-login-form.tsx`

| Campo | Selector | Label | Tipo |
|-------|----------|-------|------|
| Email | `input[name="email"]` | "Correo" | text, RHF |
| Contraseña | `input[name="password"]` | "Contraseña" | password/toggle |
| Toggle password | `button[aria-label="toggle password"]` | N/A | icon button |
| Recover link | `a[href*="/jwt/recover"]` | "¿Olvidaste la contraseña?" | link |
| Submit | `button[type="submit"]` | "Iniciar sesión" | LoadingButton |

Submit: POST `/api/auth/jwt/login`

### Catálogo — `/products`

- **Archivo**: `src/app/(authenticated)/products/_components/view.tsx`

Query params:
```
/products?name=<search>&category=<tag1|tag2>&suggestions=1&[custom-filters]
```

| Elemento | Componente | Selector |
|----------|-----------|---------|
| Search input | `Searchbar` | `input[placeholder="Buscar productos"]` |
| Filtros (desktop) | `CatalogFilter` | — |
| Filtros (mobile) | `CatalogFilterMobile` | — |
| Product card | `ProductCard` | `div[class*="StyledProductCard"]` |
| Sin resultados | `NoResults` | — |

**Product Card** (`src/components/cards/product/catalog/product-card/`):

| Elemento | Selector |
|----------|----------|
| Precio actual | `typography` con fontSize 20-24px |
| Precio tachado | `typography` strikethrough |
| Cantidad mínima | `typography[variant="caption"]` → `Mín: {value} {unit}` |
| Botón agregar | `button[class*="add-new-product-to-cart-button"]` |
| Botón variante | `button[class*="add-new-product-variant-to-cart-button"]` |
| Cantidad input | `input[data-testid="cart-quantity"]` |

### Carrito — `/cart`

- **Archivo**: `src/app/(authenticated)/cart/_components/view.tsx`

| Sección | Componente | Descripción |
|---------|-----------|-------------|
| Envío | `CartDelivery` | Dirección + fecha entrega |
| Productos | `CartProducts` | Lista con +/- qty |
| Cupón | `CartCoupon` | Input + validación GET `/api/coupons/validate/{code}` |
| Observaciones | `CartObservations` | TextArea (deshabilitado si `disableObservationInput`) |
| Resumen | `CartPricing` | Subtotal, descuentos, impuestos, total |
| Checkout | `CartCreateOrderButton` | "Confirmar pedido" |
| Khipu | `CartCreateKhipuButton` | "Pagar con Khipu" |

**Mini carrito (Drawer)**:
- Botón: `button[data-testid="side-cart-button"]`
- Lista: `div[data-testid="side-cart-list"]`
- Drawer: `div[class*="MuiDrawer-root"][anchor="right"]`

### Checkout — Validaciones pre-submit

```typescript
!commerce?.contact?.externalId    → error (externalId no configurado)
!isOrderValid (min order check)   → error (monto mínimo no alcanzado)
isBlocked                         → error (cuenta suspendida)
isDeliveryDateLoading             → disabled (esperando fechas)
```

Request POST `/api/v1/orders`:
```json
{
  "shippingAddress": { "ShippingAddress" },
  "observation": "string|null",
  "coupon": "string|null",
  "receiptType": "none"
}
```

Redirect éxito → `/confirmation/{orderId}`

### Acceso Anónimo (Multi-tenant config)

Hook: `useStore()` → `useAnonymousAccess()`

| Flag | Efecto |
|------|--------|
| `anonymousAccess: true` | Catálogo visible sin login |
| `anonymousHidePrice: true` | Precios ocultos si no autenticado |
| `anonymousHideCart: true` | Carrito oculto si no autenticado |
| `disableObservationInput: true` | Campo notas deshabilitado en carrito |

Guard: `AnonymousAccessGuard` en `auth/guard/`

### Navegación

**Header** (autenticado):
- Logo → home
- Searchbar
- Cart button (side cart)
- User menu (perfil, logout)

**Rutas menú**:
```
/           → Inicio (redirige a products)
/products   → Catálogo
/orders     → Historial
/payment-documents → Documentos
/profile    → Perfil
logout      → clear auth + redirect login
```

---

## 3. Código Playwright — Ejemplos

### Setup base

```typescript
import { test, expect } from '@playwright/test';
import { loginHelper } from '../fixtures/login';
import { clients } from '../fixtures/clients';

const client = clients.find(c => c.name === 'codelpa')!;
```

### Login

```typescript
test('should login with valid credentials', async ({ page }) => {
  await page.goto(`${client.baseUrl}/auth/jwt/login`);
  await page.fill('input[name="email"]', client.email);
  await page.fill('input[name="password"]', client.password);
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/\/products/);
});

test('should show loading state during login', async ({ page }) => {
  await page.fill('input[name="email"]', client.email);
  await page.fill('input[name="password"]', client.password);
  const submitButton = page.locator('button[type="submit"]');
  await submitButton.click();
  await expect(submitButton).toHaveAttribute('aria-busy', 'true');
});

test('should toggle password visibility', async ({ page }) => {
  const passwordInput = page.locator('input[name="password"]');
  await expect(passwordInput).toHaveAttribute('type', 'password');
  await page.locator('button[class*="eye"]').first().click();
  await expect(passwordInput).toHaveAttribute('type', 'text');
});
```

### Catálogo y búsqueda

```typescript
test('should search for products', async ({ page }) => {
  await loginHelper(page, client);
  await page.goto(`${client.baseUrl}/products`);

  const searchInput = page.locator('input[placeholder="Buscar productos"]');
  await searchInput.fill('arroz');
  await searchInput.press('Enter');

  await expect(page).toHaveURL(/name=arroz/);
  const cards = page.locator('[class*="StyledProductCard"]');
  await expect(cards).not.toHaveCount(0);
});

test('should filter by category', async ({ page }) => {
  await loginHelper(page, client);
  await page.goto(`${client.baseUrl}/products`);

  await page.locator('button:has-text("Categorías")').click();
  await page.locator('label:has-text("Granos")').click();
  await expect(page).toHaveURL(/category=/);
});
```

### Carrito y checkout

```typescript
test('should add product to cart', async ({ page }) => {
  await loginHelper(page, client);
  await page.goto(`${client.baseUrl}/products`);

  const addButton = page.locator('button[class*="add-new-product-to-cart-button"]').first();
  await addButton.click();

  const sideCart = page.locator('button[data-testid="side-cart-button"]');
  await expect(sideCart).toBeVisible();
});

test('should apply coupon', async ({ page }) => {
  await loginHelper(page, client);
  await page.goto(`${client.baseUrl}/cart`);

  await page.locator('input[placeholder="Ingresar cupón"]').fill('PROMO10');
  await page.locator('button:has-text("Aplicar")').click();

  // Validar feedback
  const feedback = page.locator('[class*="coupon-feedback"]');
  await expect(feedback).toBeVisible();
});

test('should complete checkout flow', async ({ page }) => {
  await loginHelper(page, client);
  // Agregar productos...
  await page.goto(`${client.baseUrl}/cart`);
  await page.locator('button:has-text("Confirmar pedido")').click();
  await expect(page).toHaveURL(/\/confirmation\/[a-f0-9-]+/);
});
```

### Assertions comunes

```typescript
// URL
await expect(page).toHaveURL(/\/products/);
await expect(page).toHaveURL(/\/confirmation\/[a-f0-9-]+/);

// Visibilidad
await expect(element).toBeVisible();
await expect(element).toBeHidden();

// Estado
await expect(button).toBeDisabled();
await expect(input).toHaveValue('texto esperado');
await expect(button).toHaveAttribute('aria-busy', 'true');

// Contenido
await expect(element).toContainText('Agregar');
await expect(element).not.toHaveCount(0);
```

### Tips MUI

1. Usar `.locator()` en lugar de `.querySelector()`
2. Siempre `.waitFor()` para elementos async
3. MUI tiene clases dinámicas → usar `[class*="..."]`
4. Después de inputs → `page.waitForTimeout(300)` para debounce
5. Fill + blur: `input.fill('value')` + `input.blur()` para guardar
6. Click en texto: `button:has-text("Texto exacto")`

---

## 4. Parámetros de URL

```
/products?name=arroz&category=cereales&suggestions=1
```

| Param | Tipo | Descripción |
|-------|------|-------------|
| `name` | string | Término de búsqueda |
| `category` | string \| `tag1\|tag2` | Categorías separadas por `\|` |
| `suggestions` | `1` | Mostrar recomendaciones |
| custom | varies | Filtros extra configurados por tenant |

---

## 5. Clases CSS importantes

| Clase | Elemento |
|-------|----------|
| `StyledProductCard` | Product card wrapper |
| `add-new-product-to-cart-button` | Botón agregar (producto sin variantes) |
| `add-new-product-variant-to-cart-button` | Botón agregar (con variante) |
| `increment-to-cart-button` | Botón + en carrito |
| `decrement-to-cart-button` | Botón - en carrito |
| `cart-quantity-input` | Input cantidad en carrito |
