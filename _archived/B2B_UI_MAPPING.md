# Mapeo de UI B2B — YOMCL/b2b

## Stack técnico

| Componente | Tecnología |
|-----------|-----------|
| Framework | Next.js 14+ (App Router) |
| UI Library | Material-UI (MUI) v5 |
| Form Library | React Hook Form + MUI integration (RHFTextField) |
| Estado | React Hooks (useCart, useAuth, useStore, useSettings) |
| HTTP Client | Axios (custom interceptors, JWT auth) |
| Estilos | MUI `sx` prop + Styled Components |

---

## Routes (Paths)

Base: `https://{slug}.youorder.me`

| Página | Path | Descripción |
|--------|------|-------------|
| Login | `/auth/jwt/login` | Form email + password |
| Registro | `/auth/jwt/register` | Form name + email + password |
| Recuperar contraseña | `/auth/jwt/recover` | Email recovery |
| Reset password | `/auth/jwt/reset-password` | Cambiar contraseña |
| Home | `/` | Redirect a productos o cart |
| Catálogo/Productos | `/products` | Listado con filtros y búsqueda |
| Detalle producto | `/products/[uuid]` | Modal o página con variantes |
| Carrito | `/cart` | Review + coupon + checkout |
| Confirmación pedido | `/confirmation/[uuid]` | Receipt después de crear orden |
| Perfil | `/profile` | Datos usuario |
| Pedidos | `/orders` | Historial |
| Documentos | `/payment-documents` | Facturas, guías |
| Pagos Khipu | `/khipu-payments` | Estado de pagos |

---

## 1. LOGIN PAGE — `/auth/jwt/login`

### Componente Principal
**Archivo**: `src/components/sections/auth/views/auth-login-view.tsx`
**Componente Form**: `src/components/sections/auth/components/local-login-form.tsx`

### Campos y Selectores

| Campo | Selector | Label | Type | Validación |
|-------|----------|-------|------|-----------|
| Email | `input[name="email"]` | "Correo" | text | Required, valid email (RHF) |
| Contraseña | `input[name="password"]` | "Contraseña" | password/text | Required (toggleable) |
| Password toggle | `button[aria-label="toggle password"]` | N/A | icon button | Eye icon |
| Recuperar contraseña | `a[href*="/jwt/recover"]` | "¿Olvidaste la contraseña?" | link | - |
| Botón login | `button[type="submit"]` | "Iniciar sesión" | LoadingButton | - |

### Form Submit
- **Tipo**: Local JWT auth
- **Endpoint**: POST `/api/auth/jwt/login`
- **Estado de carga**: `loading` (visual en botón)
- **Validación**: React Hook Form con MUI TextField

### Alternativas de login
- **Google**: GoogleButton component
- **Facebook**: FacebookButton component

### Navegación
- Link a registro: `<NavigateToRegister />`
- Link a recuperar: `paths.auth.jwt.recover`

---

## 2. CATÁLOGO/PRODUCTOS — `/products`

### Componente Principal
**Archivo**: `src/app/(authenticated)/products/_components/view.tsx`
**Path en URL**: `/products?[query params]`

### Query Parameters
```
GET /products?
  name=<search-term>
  category=<tag1|tag2>
  suggestions=1
  [custom filters from useFilters()]
```

### Estructura de página

#### Header (Desktop)
- Componente: `CatalogHeader`
- Muestra: `{totalProducts} productos encontrados`

#### Navegación (Mobile)
- Componente: `CatalogFilterMobile` (collapsible)
- Botón: hamburger/filter icon

#### Filtros
- Componente: `CatalogFilter` (desktop) / `CatalogFilterMobile` (mobile)
- Tipos: 
  - `FeatureFilter` (atributos)
  - `CategoryFilter` (categorías)
  - `AdditionalFilters` (custom por cliente)

#### Búsqueda
- Componente: `Searchbar`
- Placeholder: `"Buscar productos"`
- Autocomplete: sí, con sugerencias
- Scopes: "Buscar en toda la tienda" / "Buscar en {categoria}"

#### Listado de productos
- Componente: `StyledProductsWrapper` (grid)
- Componente por item: `ProductCard`
- Loading: `LinearProgress`
- Sin resultados: `NoResults`

### Product Card Selectores

**Archivo**: `src/components/cards/product/catalog/product-card/product-card.tsx`

| Elemento | Selector | Descripción |
|----------|----------|-------------|
| Card wrapper | `div[class*="StyledProductCard"]` | Tarjeta del producto |
| Imagen hover | `img` con galería | Hover muestra imágenes |
| Nombre/SKU | `typography` | Nombre del producto |
| Precio actual | `typography` con fontSize 20-24px | Precio en MXN/CLP/etc |
| Precio anterior | `typography` strikethrough | Si hay descuento |
| Etiquetas | `ProductLabels` component | Ej: "Promoción", "Nuevo" |
| Cantidad mínima | `typography[variant="caption"]` | `Mín: {value} {unit}` |
| Botón agregar | `button[class*="add-new-product-to-cart-button"]` | "Agregar" o "Sin stock" |
| Botón agregar (variante) | `button[class*="add-new-product-variant-to-cart-button"]` | "Seleccionar" |
| Cantidad (en carrito) | `input[data-testid="cart-quantity"]` | TextField number |
| Decrement | `button[class*="decrement-to-cart-button"]` | Icon: Remove |
| Increment | `button[data-testid="add-to-cart"]` | Icon: Add |

### Precios y Promociones
- **Componente**: `Pricing`
- **Formato**: Moneda formateada con `useFormattedCurrency()`
- **Step pricing**: Si `product.pricing.steps.length > 0` → muestra `PromotionLabel`
- **Packaging**: Si tiene packaging, muestra unidad (ej: "caja", "paquete")

### Acceso anónimo
- Hook: `useAnonymousAccess()`
- Propiedades:
  - `canAccessCart`: booleano (depende de `anonymousHideCart`, `anonymousHidePrice`)
  - `canSeePrices`: booleano (depende de `anonymousHidePrice`)
  - `canAccessPages`: booleano

**Comportamiento**:
- Si anónimo + `anonymousHideCart` → oculta botones de carrito
- Si anónimo + `anonymousHidePrice` → oculta precios y carrito
- Configuración en `useStore()` → flags de config del tenant

---

## 3. CARRITO — `/cart`

### Componente Principal
**Archivo**: `src/app/(authenticated)/cart/_components/view.tsx`

### Secciones

#### a) Delivery (Envío)
- Componente: `CartDelivery`
- Campos:
  - `CartDeliverySelect`: Dropdown de direcciones (config del cliente)
  - `CartDeliveryDateSelect`: Picker de fechas de entrega
- Visible si:
  - `salesTerms?.delivery?.daysOfWeek?.length > 0` O
  - `addressList?.length > 0` O
  - `deliveryDates?.length > 0`

#### b) Productos en carrito
- Componente: `CartProducts`
- Cada item:
  - Imagen, nombre, SKU
  - Precio unitario
  - Cantidad (con +/- buttons)
  - Subtotal
  - Link a modal de detalle

#### c) Cupón/Descuento
- Componente: `CartCoupon`
- Input: "Ingresar cupón"
- Botón: "Aplicar"
- Validación: GET `/api/coupons/validate/{code}`
- Feedback: CheckCircleOutline si válido, error message si no

#### d) Observaciones
- Componente: `CartObservations`
- TextArea para notas especiales
- Deshabilitado si `disableObservationInput` en store

#### e) Resumen de precios
- Componente: `CartPricing`
- Muestra:
  - Subtotal
  - Descuentos (cupón, promociones)
  - Impuestos
  - Total final

#### f) Botones de pago
- `CartCreateOrderButton`: para pagos normales
  - Texto: "Confirmar pedido"
  - Valida: `isOrderValid`, `isBlocked`, shipping address, etc.
  
- `CartCreateKhipuButton`: para pagos Khipu
  - Texto: "Pagar con Khipu"

### Mini carrito (Drawer lateral)
**Archivo**: `src/components/minimals/layouts/common/cart-popover/`

| Componente | Descripción |
|-----------|-------------|
| `SideCartButton` | Botón en header con total y cantidad |
| `SideCartDrawer` | Drawer a la derecha |
| `SideCartHeader` | Encabezado: "Carrito ({count})" |
| `SideCartList` | Listado de items (scroll) |
| `SideCartFooter` | Botón "Ir al carrito" |

**Selectores**:
- Botón carrito: `button[data-testid="side-cart-button"]`
- Lista: `div[data-testid="side-cart-list"]`
- Drawer: `div[class*="MuiDrawer-root"]` (anchor="right")

---

## 4. CHECKOUT — POST `/cart`

### Flujo
1. Usuario en `/cart` completa:
   - Selecciona dirección de envío
   - Selecciona fecha de entrega
   - Opcionalmente aplica cupón
   - Opcionalmente agrega observaciones

2. Click en "Confirmar pedido" → `CartCreateBaseButton.handleClick()`

### Validaciones pre-checkout
```typescript
- !commerce?.contact?.externalId → error
- !isOrderValid (min order check) → error
- isBlocked (cuenta suspendida) → error
- isDeliveryDateLoading → disabled
```

### Request de orden
**POST** `POST /api/v1/orders` (legacyEndpoints.orders.create)

Payload:
```json
{
  "shippingAddress": { ShippingAddress },
  "observation": "string|null",
  "coupon": "string|null",
  "receiptType": "none"
}
```

Response:
```json
{
  "_id": "uuid"
}
```

### Redirección
- Success → `router.replace(/confirmation/{orderId})`
- Error → Toast con mensaje específico (accountNotVerified, blockedFromOrders, minTotalPrice, etc.)

---

## 5. BÚSQUEDA — Searchbar

**Archivo**: `src/components/minimals/layouts/common/searchbar/searchbar.tsx`

### Comportamiento
- Placeholder: `"Buscar productos"`
- Autocomplete con sugerencias
- On Enter o click botón búsqueda → ejecuta búsqueda
- Scope: "en toda la tienda" o "en {categoría}"

### Selectores
| Elemento | Selector |
|----------|----------|
| Input | `input[placeholder="Buscar productos"]` |
| Botón búsqueda | `button[aria-label*="search"]` |
| Dropdown | `ul[role="listbox"]` |
| Scope badge | `div[class*="scope-badge"]` |

### Integración
- Contexto: `useCatalogQuery()` → setName()
- Redirect: internamente actualiza query params de `/products`
- Analytics: logEvent('search', 'catalog', searchTerm)

---

## 6. NAVEGACIÓN

### Header Principal
**Ubicación**: Layout authenticated
**Componente**: `src/components/minimals/layouts/`

Elementos (desktop):
1. Logo (clickeable → home)
2. Searchbar (buscar productos)
3. Cart button (side cart)
4. User menu (perfil, logout)

Elementos (mobile):
1. Hamburger menu
2. Logo
3. Cart button
4. Searchbar colapsible

### Menú principal
- Inicio → `/`
- Productos → `/products`
- Pedidos → `/orders`
- Documentos → `/payment-documents`
- Perfil → `/profile`
- Logout → clear auth + redirect a login

### Categorías (Sidebar o Dropdown)
- Componente: `CategoryFilter` en catálogo
- Fetch de: `useCategories()`
- Tree structure: categorías con subcategorías

---

## 7. ACCESO ANÓNIMO (Multi-tenant config)

### Configuración por tenant
**Fuente**: `useStore()` hook
**Propiedades**:
```typescript
{
  anonymousAccess: boolean,        // ¿Permite ver sin login?
  anonymousHidePrice: boolean,     // ¿Oculta precios si anónimo?
  anonymousHideCart: boolean,      // ¿Oculta carrito si anónimo?
  themeStretch: boolean,           // Ancho max container
  disableObservationInput: boolean, // Deshabilita notas en cart
  payment: { ... },                // Config pagos
}
```

### Comportamiento
1. **anonymousAccess = true**
   - Permite ver catálogo sin login
   - Puede ver precios si `!anonymousHidePrice`
   - Puede acceder carrito si `!anonymousHideCart && !anonymousHidePrice`

2. **anonymousAccess = false**
   - Requiere login para ver catálogo
   - Redirect a `/auth/jwt/login` si no autenticado

3. **Guard**: `AnonymousAccessGuard` en auth/guard/

---

## 8. COMPONENTES CLAVE CON DATA-TESTID

| Component | data-testid | Ubicación |
|-----------|-------------|-----------|
| Catalog page | `catalog-page` | ProductsView |
| Cart quantity | `cart-quantity` | CartInteraction |
| Add to cart | `add-to-cart` | CartInteraction increment button |
| Side cart button | `side-cart-button` | SideCartButton |
| Side cart list | `side-cart-list` | SideCartList |
| Product detail modal | `product-detail-modal` | ProductDetailModal |

---

## 9. ELEMENTOS CON CLASES CSS

| Clase | Elemento | Ubicación |
|-------|----------|-----------|
| `add-new-product-to-cart-button` | Botón agregar (no en carrito) | AddToCartButton |
| `add-new-product-variant-to-cart-button` | Botón agregar con variante | AddToCartButton |
| `increment-to-cart-button` | Botón + cantidad | CartInteraction |
| `decrement-to-cart-button` | Botón - cantidad | CartInteraction |
| `cart-quantity-input` | Input cantidad en carrito | CartInteraction |

---

## 10. INPUTS Y LABELS EXACTOS

### Login Form
```html
<label>Correo</label>
<input type="text" name="email" placeholder="" />

<label>Contraseña</label>
<input type="password" name="password" placeholder="" />

<button type="submit">Iniciar sesión</button>
<a href="/auth/jwt/recover">¿Olvidaste la contraseña?</a>
```

### Carrito - Cupón
```html
<label>Ingresar cupón</label>
<input placeholder="Ingresar cupón" />
<button>Aplicar</button>

<!-- Si válido: -->
<svg>CheckCircleOutline</svg>

<!-- Si error: -->
<div class="MuiFormHelperText">{errorMessage}</div>
```

### Carrito - Observaciones
```html
<label>Observaciones (opcional)</label>
<textarea placeholder="Agregar notas especiales..." />
<span>Caracteres: {count}/500</span>
```

### Checkout
```html
<button type="submit" class="LoadingButton">
  Confirmar pedido
</button>
<!-- O -->
<button type="submit" class="LoadingButton">
  Pagar con Khipu
</button>
```

---

## 11. RUTAS RELATIVAS EN TESTS

Para construir URLs en Playwright:
```typescript
const BASE_URL = `https://${slug}.youorder.me`;

// Login
await page.goto(`${BASE_URL}/auth/jwt/login`);

// Catálogo
await page.goto(`${BASE_URL}/products`);
await page.goto(`${BASE_URL}/products?name=arroz`);

// Producto
await page.goto(`${BASE_URL}/products/${productUUID}`);

// Carrito
await page.goto(`${BASE_URL}/cart`);

// Confirmación
await page.goto(`${BASE_URL}/confirmation/${orderUUID}`);
```

---

## 12. OBSERVACIONES PARA QA

### Selectores a usar en Playwright

#### Campos de login
```typescript
// Email
await page.fill('input[name="email"]', 'test@youorder.me');

// Password
await page.fill('input[name="password"]', 'password123');

// Submit
await page.click('button[type="submit"]:has-text("Iniciar sesión")');
```

#### Producto en catálogo
```typescript
// Buscar producto
await page.fill('input[placeholder="Buscar productos"]', 'arroz');
await page.press('input[placeholder="Buscar productos"]', 'Enter');

// Agregar a carrito (si no está)
await page.click('button[class*="add-new-product-to-cart-button"]');

// Agregar cantidad (si ya está en carrito)
await page.click('button[data-testid="add-to-cart"]'); // increment
await page.click('button[class*="decrement-to-cart-button"]'); // decrement
```

#### Carrito
```typescript
// Abrir carrito
await page.click('button[data-testid="side-cart-button"]');

// Cupón
await page.fill('input[placeholder="Ingresar cupón"]', 'DESCUENTO10');
await page.click('button:has-text("Aplicar")');

// Observaciones
await page.fill('textarea[placeholder*="notas especiales"]', 'Sin hielo');

// Checkout
await page.click('button:has-text("Confirmar pedido")');
```

### Gaps encontrados

1. **No hay data-testid explícitos en formularios de auth** → usar name attributes
2. **Cupón no tiene data-testid** → usar label o placeholder
3. **Observaciones no tiene data-testid** → usar placeholder
4. **No hay validación visual clara de errores** → revisar aria-invalid o clases de error
5. **Acceso anónimo depende de flags en MongoDB** → verificar config antes de pruebas
6. **Redirecciones de checkout dependen de onSuccess callback** → puede haber race conditions

---

## Resumen para adaptar tests

**Rutas base**: `/auth/jwt/login`, `/products`, `/cart`, `/confirmation/[uuid]`

**Selectores clave**:
- Email: `input[name="email"]`
- Password: `input[name="password"]`
- Agregar: `button[class*="add-new-product-to-cart-button"]`
- Cart button: `button[data-testid="side-cart-button"]`
- Cupón: `input[placeholder="Ingresar cupón"]`
- Confirmar: `button:has-text("Confirmar pedido")`

**Multi-tenant**: Usar env var `BASE_URL` con slug dinámico

**Anónimo**: Revisar flags `anonymousAccess`, `anonymousHidePrice`, `anonymousHideCart` en config del tenant

