# Selectores Playwright — B2B YOM

Guía de selectores y ejemplo de código Playwright basado en la exploración del repo YOMCL/b2b.

---

## Setup básico

```typescript
import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'https://dev.youorder.me';
const SLUG = process.env.SLUG || 'dev';

test.beforeEach(async ({ page }) => {
  await page.goto(`${BASE_URL}/auth/jwt/login`);
});
```

---

## 1. LOGIN

### Campos del formulario

```typescript
test('should login with valid credentials', async ({ page }) => {
  // Email input
  const emailInput = page.locator('input[name="email"]');
  await emailInput.fill('test@youorder.me');

  // Password input
  const passwordInput = page.locator('input[name="password"]');
  await passwordInput.fill('password123');

  // Toggle password visibility
  const togglePasswordButton = page.locator('button[class*="eye"]').first();
  await expect(togglePasswordButton).toBeVisible();

  // Submit button
  const submitButton = page.locator('button[type="submit"]');
  await submitButton.click();

  // Validar redirección a productos
  await expect(page).toHaveURL(/\/products/);
});

test('should show password toggle', async ({ page }) => {
  const passwordInput = page.locator('input[name="password"]');
  
  // Validar que es password type
  await expect(passwordInput).toHaveAttribute('type', 'password');
  
  // Click toggle
  const toggle = page.locator('button[class*="eye"]').first();
  await toggle.click();
  
  // Validar que cambió a text
  await expect(passwordInput).toHaveAttribute('type', 'text');
});

test('should show "recover password" link', async ({ page }) => {
  const recoverLink = page.locator('a[href*="/jwt/recover"]');
  await expect(recoverLink).toContainText('¿Olvidaste la contraseña?');
});

test('should show loading state during login', async ({ page }) => {
  await page.fill('input[name="email"]', 'test@youorder.me');
  await page.fill('input[name="password"]', 'password123');
  
  const submitButton = page.locator('button[type="submit"]');
  await submitButton.click();
  
  // Validar que el botón tiene atributo loading
  await expect(submitButton).toHaveAttribute('aria-busy', 'true');
});
```

---

## 2. CATÁLOGO/BÚSQUEDA

### Búsqueda de productos

```typescript
test('should search for products', async ({ page }) => {
  await page.goto(`${BASE_URL}/products`);

  // Searchbar input
  const searchInput = page.locator('input[placeholder="Buscar productos"]');
  await searchInput.fill('arroz');
  await searchInput.press('Enter');

  // Validar query param
  await expect(page).toHaveURL(/name=arroz/);

  // Validar que hay resultados
  const productCards = page.locator('[class*="StyledProductCard"]');
  await expect(productCards).not.toHaveCount(0);
});

test('should show search suggestions', async ({ page }) => {
  await page.goto(`${BASE_URL}/products`);

  const searchInput = page.locator('input[placeholder="Buscar productos"]');
  await searchInput.fill('ar');

  // Dropdown con sugerencias
  const dropdown = page.locator('ul[role="listbox"]');
  await expect(dropdown).toBeVisible();

  // Contar sugerencias
  const options = dropdown.locator('li');
  const count = await options.count();
  expect(count).toBeGreaterThan(0);
});

test('should search in category scope', async ({ page }) => {
  await page.goto(`${BASE_URL}/products?category=cereales`);

  const searchInput = page.locator('input[placeholder="Buscar productos"]');
  await searchInput.fill('arroz');

  // Verificar scope badge
  const scopeBadge = page.locator('[class*="scope-badge"]');
  await expect(scopeBadge).toContainText('cereales');

  await searchInput.press('Enter');
  await expect(page).toHaveURL(/category=cereales.*name=arroz/);
});
```

### Filtros

```typescript
test('should filter by category', async ({ page }) => {
  await page.goto(`${BASE_URL}/products`);

  // Abrir filtro de categorías
  const categoryFilter = page.locator('button:has-text("Categorías")');
  await categoryFilter.click();

  // Seleccionar categoría
  const categoryOption = page.locator('label:has-text("Granos")');
  await categoryOption.click();

  // Validar que URL tiene category param
  await expect(page).toHaveURL(/category=/);
});

test('should show product count', async ({ page }) => {
  await page.goto(`${BASE_URL}/products`);

  // En desktop: CatalogHeader
  const productCount = page.locator('text=/\\d+ productos encontrados/');
  await expect(productCount).toBeVisible();

  // En mobile: junto al filtro
  const mobileCount = page.locator('text=/productos encontrados/');
  await expect(mobileCount).toBeVisible();
});
```

---

## 3. PRODUCTO EN CATÁLOGO

### Agregar a carrito

```typescript
test('should add product to cart', async ({ page }) => {
  await page.goto(`${BASE_URL}/products`);

  // Buscar primer producto
  const firstProduct = page.locator('[class*="StyledProductCard"]').first();

  // Botón "Agregar"
  const addButton = firstProduct.locator('button[class*="add-new-product-to-cart-button"]');
  await expect(addButton).toContainText('Agregar');
  await addButton.click();

  // Validar que el botón ahora es +/-
  const incrementButton = firstProduct.locator('button[data-testid="add-to-cart"]');
  await expect(incrementButton).toBeVisible();

  // Validar que el carrito se actualiza
  const cartButton = page.locator('button[data-testid="side-cart-button"]');
  await expect(cartButton).toContainText(/\$.*\d+/);
});

test('should handle out of stock product', async ({ page }) => {
  await page.goto(`${BASE_URL}/products`);

  // Buscar producto sin stock
  const outOfStockProduct = page.locator('[class*="StyledProductCard"]').filter({ 
    has: page.locator('text=Sin stock') 
  }).first();

  const addButton = outOfStockProduct.locator('button[class*="add-new-product-to-cart-button"]');
  await expect(addButton).toContainText('Sin stock');
  await expect(addButton).toBeDisabled();
});

test('should show product with variants requires selection', async ({ page }) => {
  await page.goto(`${BASE_URL}/products`);

  // Producto con variantes
  const variantProduct = page.locator('[class*="StyledProductCard"]')
    .filter({ has: page.locator('text=Seleccionar') })
    .first();

  const selectButton = variantProduct.locator('button[class*="add-new-product-variant-to-cart-button"]');
  await expect(selectButton).toContainText('Seleccionar');
  await selectButton.click();

  // Abre modal
  const modal = page.locator('[data-testid="product-detail-modal"]');
  await expect(modal).toBeVisible();
});

test('should show pricing and minimum quantity', async ({ page }) => {
  await page.goto(`${BASE_URL}/products`);

  const productCard = page.locator('[class*="StyledProductCard"]').first();

  // Precio (typography bold 20-24px)
  const price = productCard.locator('text=/\$[\d,.]+/').first();
  await expect(price).toBeVisible();

  // Cantidad mínima
  const minQty = productCard.locator('text=/Mín:/');
  // Puede no estar visible si min = 1
  if (await minQty.isVisible()) {
    await expect(minQty).toContainText(/Mín:\s*\d+/);
  }
});

test('should increment/decrement quantity', async ({ page }) => {
  await page.goto(`${BASE_URL}/products`);

  // Agregar producto
  const addButton = page.locator('button[class*="add-new-product-to-cart-button"]').first();
  await addButton.click();

  const cartQtyInput = page.locator('input[data-testid="cart-quantity"]').first();
  await expect(cartQtyInput).toHaveValue('1');

  // Click increment
  const incrementBtn = page.locator('button[data-testid="add-to-cart"]').first();
  await incrementBtn.click();
  await expect(cartQtyInput).toHaveValue('2');

  // Click decrement
  const decrementBtn = page.locator('button[class*="decrement-to-cart-button"]').first();
  await decrementBtn.click();
  await expect(cartQtyInput).toHaveValue('1');
});

test('should manually edit quantity', async ({ page }) => {
  await page.goto(`${BASE_URL}/products`);

  // Agregar producto
  const addButton = page.locator('button[class*="add-new-product-to-cart-button"]').first();
  await addButton.click();

  const qtyInput = page.locator('input[data-testid="cart-quantity"]').first();
  
  // Borrar y escribir
  await qtyInput.fill('5');
  await qtyInput.blur();

  // Validar que se guardó
  await page.waitForTimeout(300); // esperar debounce
  await expect(qtyInput).toHaveValue('5');
});
```

---

## 4. CARRITO

### Abrir carrito

```typescript
test('should open side cart', async ({ page }) => {
  await page.goto(`${BASE_URL}/products`);

  // Agregar producto primero
  const addButton = page.locator('button[class*="add-new-product-to-cart-button"]').first();
  await addButton.click();

  // Click en botón carrito
  const cartButton = page.locator('button[data-testid="side-cart-button"]');
  await cartButton.click();

  // Validar que drawer se abre
  const drawer = page.locator('[class*="MuiDrawer-root"]');
  await expect(drawer).toBeVisible();

  // Validar encabezado
  await expect(drawer.locator('text=Carrito')).toBeVisible();
});

test('should show cart items in drawer', async ({ page }) => {
  await page.goto(`${BASE_URL}/products`);

  // Agregar 2 productos
  const addButtons = page.locator('button[class*="add-new-product-to-cart-button"]');
  await addButtons.nth(0).click();
  await addButtons.nth(1).click();

  // Abrir carrito
  const cartButton = page.locator('button[data-testid="side-cart-button"]');
  await cartButton.click();

  // Validar lista
  const cartList = page.locator('[data-testid="side-cart-list"]');
  await expect(cartList).toBeVisible();

  const items = cartList.locator('[class*="product-card"]');
  expect(await items.count()).toBe(2);
});

test('should show cart total price', async ({ page }) => {
  await page.goto(`${BASE_URL}/products`);

  const addButton = page.locator('button[class*="add-new-product-to-cart-button"]').first();
  await addButton.click();

  const cartButton = page.locator('button[data-testid="side-cart-button"]');
  
  // Validar que muestra precio
  const totalPrice = cartButton.locator('text=/\$[\d,.]+/');
  await expect(totalPrice).toBeVisible();
});
```

### Ir al carrito completo

```typescript
test('should navigate to full cart page', async ({ page }) => {
  await page.goto(`${BASE_URL}/products`);

  // Agregar producto
  const addButton = page.locator('button[class*="add-new-product-to-cart-button"]').first();
  await addButton.click();

  // Abrir drawer
  const cartButton = page.locator('button[data-testid="side-cart-button"]');
  await cartButton.click();

  // Click en "Ir al carrito"
  const goToCartButton = page.locator('button:has-text("Ir al carrito")');
  await goToCartButton.click();

  // Validar que está en /cart
  await expect(page).toHaveURL(/\/cart/);
});

test('should load cart page with products', async ({ page }) => {
  // Agregar producto via API o cookies
  // Para simplificar, asumiendo que ya hay un carrito
  
  await page.goto(`${BASE_URL}/cart`);

  // Validar header
  const header = page.locator('text=Carrito');
  await expect(header).toBeVisible();

  // Validar que hay productos
  const productRows = page.locator('[class*="product-card"]');
  expect(await productRows.count()).toBeGreaterThan(0);
});
```

---

## 5. CARRITO — CUPÓN

```typescript
test('should apply valid coupon', async ({ page }) => {
  await page.goto(`${BASE_URL}/cart`);

  // Input de cupón
  const couponInput = page.locator('input[placeholder="Ingresar cupón"]');
  await couponInput.fill('DESCUENTO10');

  // Botón aplicar
  const applyButton = page.locator('button:has-text("Aplicar")');
  await applyButton.click();

  // Validar check icon
  const checkIcon = page.locator('[class*="CheckCircleOutline"]');
  await expect(checkIcon).toBeVisible();
});

test('should show error for invalid coupon', async ({ page }) => {
  await page.goto(`${BASE_URL}/cart`);

  const couponInput = page.locator('input[placeholder="Ingresar cupón"]');
  await couponInput.fill('INVALIDO');

  const applyButton = page.locator('button:has-text("Aplicar")');
  await applyButton.click();

  // Validar mensaje de error
  const errorMsg = page.locator('[class*="MuiFormHelperText"]');
  await expect(errorMsg).toBeVisible();
  await expect(errorMsg).toContainText(/no válido|expirado|no existe/i);
});

test('should remove coupon', async ({ page }) => {
  await page.goto(`${BASE_URL}/cart`);

  // Aplicar cupón válido
  const couponInput = page.locator('input[placeholder="Ingresar cupón"]');
  await couponInput.fill('DESCUENTO10');
  const applyButton = page.locator('button:has-text("Aplicar")');
  await applyButton.click();

  // Esperar check icon
  await page.locator('[class*="CheckCircleOutline"]').waitFor();

  // Click en icono delete
  const deleteButton = page.locator('button[aria-label="Eliminar cupón"]');
  await deleteButton.click();

  // Validar que input está vacío
  await expect(couponInput).toHaveValue('');
});
```

---

## 6. CARRITO — OBSERVACIONES

```typescript
test('should add observations', async ({ page }) => {
  await page.goto(`${BASE_URL}/cart`);

  // Buscar textarea de observaciones
  const observationsInput = page.locator('textarea[placeholder*="notas especiales"]');
  
  // Puede no existir si disableObservationInput = true
  if (await observationsInput.isVisible()) {
    await observationsInput.fill('Sin picante, sin cebolla');
    await observationsInput.blur();

    // Validar que se guardó
    await expect(observationsInput).toHaveValue('Sin picante, sin cebolla');
  }
});

test('should show character count', async ({ page }) => {
  await page.goto(`${BASE_URL}/cart`);

  const observationsInput = page.locator('textarea[placeholder*="notas especiales"]');
  
  if (await observationsInput.isVisible()) {
    await observationsInput.fill('Esto es una prueba');

    // Buscar contador
    const charCount = page.locator('text=/Caracteres:/');
    await expect(charCount).toBeVisible();
  }
});
```

---

## 7. CHECKOUT

```typescript
test('should complete checkout', async ({ page }) => {
  // 1. Agregar producto
  await page.goto(`${BASE_URL}/products`);
  const addButton = page.locator('button[class*="add-new-product-to-cart-button"]').first();
  await addButton.click();

  // 2. Ir al carrito
  const cartButton = page.locator('button[data-testid="side-cart-button"]');
  await cartButton.click();
  const goToCartButton = page.locator('button:has-text("Ir al carrito")');
  await goToCartButton.click();

  // 3. Seleccionar dirección (si hay)
  const addressSelect = page.locator('select[name*="address"]');
  if (await addressSelect.isVisible()) {
    const options = addressSelect.locator('option');
    const optionCount = await options.count();
    if (optionCount > 1) {
      await addressSelect.selectOption({ index: 1 });
    }
  }

  // 4. Seleccionar fecha de entrega (si hay)
  const dateSelect = page.locator('select[name*="delivery"]');
  if (await dateSelect.isVisible()) {
    const options = dateSelect.locator('option');
    const optionCount = await options.count();
    if (optionCount > 1) {
      await dateSelect.selectOption({ index: 1 });
    }
  }

  // 5. Click checkout
  const checkoutButton = page.locator('button:has-text("Confirmar pedido")');
  await checkoutButton.click();

  // 6. Validar redirección a confirmación
  await expect(page).toHaveURL(/\/confirmation\/[a-f0-9-]+/);
  
  // 7. Validar que hay mensaje de éxito
  const successMsg = page.locator('text=/pedido|confirmación/i');
  await expect(successMsg).toBeVisible();
});

test('should validate minimum order total', async ({ page }) => {
  await page.goto(`${BASE_URL}/products`);

  // Agregar producto barato (simulado)
  const addButton = page.locator('button[class*="add-new-product-to-cart-button"]').first();
  await addButton.click();

  // Ir a carrito
  const cartButton = page.locator('button[data-testid="side-cart-button"]');
  await cartButton.click();
  const goToCartButton = page.locator('button:has-text("Ir al carrito")');
  await goToCartButton.click();

  // Botón checkout debería estar desabilitado o mostrar error
  const checkoutButton = page.locator('button:has-text("Confirmar pedido")');
  
  // Verificar que está disabled o muestra tooltip
  const isDisabled = await checkoutButton.isDisabled();
  expect(isDisabled || await page.locator('text=monto mínimo').isVisible()).toBeTruthy();
});

test('should show checkout loading state', async ({ page }) => {
  await page.goto(`${BASE_URL}/cart`);

  // Asumir que hay carrito válido
  const checkoutButton = page.locator('button:has-text("Confirmar pedido")');
  await checkoutButton.click();

  // Validar loading state
  await expect(checkoutButton).toHaveAttribute('aria-busy', 'true');
});
```

---

## 8. ACCESO ANÓNIMO

```typescript
test('should show products without login if anonymous access enabled', async ({ page }) => {
  // Asumir que SLUG tiene anonymousAccess = true
  await page.goto(`${BASE_URL}/products`);

  // Validar que no redirige a login
  await expect(page).toHaveURL(/\/products/);

  // Validar que hay productos
  const productCards = page.locator('[class*="StyledProductCard"]');
  expect(await productCards.count()).toBeGreaterThan(0);
});

test('should hide prices if anonymousHidePrice enabled', async ({ page }) => {
  // Asumir que SLUG tiene anonymousHidePrice = true
  await page.goto(`${BASE_URL}/products`);

  // No debería haber precios visibles
  const prices = page.locator('text=/\$[\d,.]+/');
  expect(await prices.count()).toBe(0);
});

test('should hide cart if anonymousHideCart enabled', async ({ page }) => {
  // Asumir que SLUG tiene anonymousHideCart = true
  await page.goto(`${BASE_URL}/products`);

  // Botón agregar no debería ser visible
  const addButtons = page.locator('button[class*="add-new-product-to-cart-button"]');
  expect(await addButtons.count()).toBe(0);
});

test('should require login if anonymous access disabled', async ({ page }) => {
  // Asumir que SLUG tiene anonymousAccess = false
  await page.goto(`${BASE_URL}/products`);

  // Validar que redirige a login
  await expect(page).toHaveURL(/\/auth\/jwt\/login/);
});
```

---

## 9. HELPERS Y UTILITIES

```typescript
// lib/test-helpers.ts

export async function loginAsUser(page: Page, email: string, password: string) {
  await page.goto(`${process.env.BASE_URL}/auth/jwt/login`);
  
  await page.fill('input[name="email"]', email);
  await page.fill('input[name="password"]', password);
  await page.click('button[type="submit"]');
  
  // Esperar redirección
  await page.waitForURL(/\/products/);
}

export async function addProductToCart(page: Page, index: number = 0) {
  const addButton = page.locator('button[class*="add-new-product-to-cart-button"]').nth(index);
  await addButton.click();
  
  // Esperar que aparezca el input de cantidad
  const qtyInput = page.locator('input[data-testid="cart-quantity"]').nth(index);
  await qtyInput.waitFor();
}

export async function goToCart(page: Page) {
  const cartButton = page.locator('button[data-testid="side-cart-button"]');
  await cartButton.click();
  
  const goToCartButton = page.locator('button:has-text("Ir al carrito")');
  await goToCartButton.click();
  
  await page.waitForURL(/\/cart/);
}

export async function applyCoupon(page: Page, code: string) {
  const couponInput = page.locator('input[placeholder="Ingresar cupón"]');
  await couponInput.fill(code);
  
  const applyButton = page.locator('button:has-text("Aplicar")');
  await applyButton.click();
  
  // Esperar validación
  await page.locator('[class*="CheckCircleOutline"]').waitFor({ timeout: 5000 });
}

export async function checkout(page: Page) {
  const checkoutButton = page.locator('button:has-text("Confirmar pedido")');
  await checkoutButton.click();
  
  // Esperar redirección a confirmación
  await page.waitForURL(/\/confirmation/);
}
```

---

## Notas importantes

1. **Placeholders exactos**: Usa `placeholder="Buscar productos"`, `placeholder="Ingresar cupón"`, etc.
2. **Nombres de input**: `name="email"`, `name="password"` en login
3. **Data-testid específicos**: `data-testid="cart-quantity"`, `data-testid="side-cart-button"`, etc.
4. **Clases dinámicas**: Algunos selectores usan `[class*="..."]` porque MUI genera clases únicas
5. **Multi-tenant**: Siempre usar `BASE_URL` con SLUG en variables de ambiente
6. **Waits**: Agregar `waitForTimeout()` después de clicks que disparan debounce (300ms)
7. **Async/await**: Material-UI es async, siempre esperar con `.waitFor()`

