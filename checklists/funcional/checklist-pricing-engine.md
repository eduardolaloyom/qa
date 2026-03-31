# Checklist QA — Motor de Pricing

> Fuente: [Pricing — Tech Wiki](https://www.notion.so/27b1bef354734c8aa97414ca9944cee8)
> Fecha creación: 2026-03-27

---

## Contexto

El pricing de YOM es un pipeline de 4 capas de descuento aplicadas en orden:
1. **Promotions legacy** → resultado en `pricingAfterDiscount.pricePerUnit`
2. **Cupones** → resultado en `fullPricing.discountedPricePerUnit`
3. **Promociones nuevas** → acumula en `discountedPricePerUnit`
4. **Descuento de vendedor** → acumula en `discountedPricePerUnit`

Luego se aplican impuestos → `finalPricePerUnit`

### Campos clave en la orden

| Campo | Nivel | Descripción |
|-------|-------|-------------|
| `pricingAfterDiscount.pricePerUnit` | Producto | Precio unitario post-promoción legacy |
| `fullPricing.discountedPricePerUnit` | Producto | Precio unitario con todos los descuentos (sin impuesto) |
| `fullPricing.finalPricePerUnit` | Producto | Precio final con descuentos + impuestos |
| `fullPricing.taxesApplied` | Producto | Mapa de códigos de impuestos y tasas |
| `pricing.netTotalPrice` | Orden | Total sin descuentos ni impuestos |
| `pricing.totalPrice` | Orden | Total con descuentos, sin impuestos |
| `pricing.discountedTotalPrice` | Orden | Total con descuentos, sin impuestos |
| `pricing.netTaxedTotalPrice` | Orden | Total sin descuentos, con impuestos |
| `pricing.finalTotalPrice` | Orden | **Total final** con todo aplicado |

---

## 1. Precio base (sin descuentos)

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| PRC-01 | Producto sin descuentos ni promociones | `netTotalPrice` = precio unitario × cantidad | PENDIENTE |
| PRC-02 | `netTotalPrice` = suma de `netPricePerUnit × qty` de todos los items | Cálculo correcto | PENDIENTE |
| PRC-03 | Producto con impuesto (IVA) | `finalPricePerUnit` = `pricePerUnit` × (1 + tasa) | PENDIENTE |

---

## 2. Pipeline de descuentos (orden importa)

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| PRC-10 | Solo promoción legacy activa | `pricePerUnit` ya tiene descuento, `discountedPricePerUnit` = `pricePerUnit` | PENDIENTE |
| PRC-11 | Promoción legacy + cupón | Cupón se calcula sobre `pricePerUnit` (ya descontado por promo) | PENDIENTE |
| PRC-12 | Promoción legacy + cupón + descuento vendedor | Se acumulan en cadena, no se suman porcentajes | PENDIENTE |
| PRC-13 | Solo cupón (sin promoción legacy) | `discountedPricePerUnit` = `pricePerUnit` × (1 - cupón%) | PENDIENTE |
| PRC-14 | Solo descuento de vendedor | `discountedPricePerUnit` refleja descuento del vendedor | PENDIENTE |
| PRC-15 | 100% descuento acumulado | `discountedPricePerUnit` = 0, `finalPricePerUnit` = 0 | PENDIENTE |
| PRC-16 | Descuento que supera el precio (>100%) | No debe generar precio negativo | PENDIENTE |

---

## 3. Impuestos

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| PRC-20 | `includeTaxRateInPrices = false` (neto) | Precios mostrados sin impuesto, impuesto visible aparte | PENDIENTE |
| PRC-21 | `includeTaxRateInPrices = true` (bruto) | Precios mostrados ya incluyen impuesto | PENDIENTE |
| PRC-22 | Impuesto se calcula sobre precio descontado | `finalPricePerUnit` = `discountedPricePerUnit` × (1 + tasa) | PENDIENTE |
| PRC-23 | `taxesApplied` contiene todos los impuestos aplicados | Mapa correcto con códigos y tasas | PENDIENTE |

---

## 4. Totales a nivel de orden

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| PRC-30 | `finalTotalPrice` = Σ(`finalPricePerUnit` × qty) | Suma correcta | PENDIENTE |
| PRC-31 | `totalPrice` con descuento vs sin descuento | `totalPrice` ≤ `netTotalPrice` | PENDIENTE |
| PRC-32 | `netTaxedTotalPrice` vs `finalTotalPrice` | `netTaxedTotalPrice` ≥ `finalTotalPrice` (sin descuento tiene más impuesto base) | PENDIENTE |
| PRC-33 | Orden con mezcla de productos con y sin descuento | Cada producto calcula independiente, total es la suma | PENDIENTE |

---

## 5. Segmentos y overrides (precios custom)

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| PRC-40 | Comercio en segmento con override de precio | Precio del override reemplaza precio base | PENDIENTE |
| PRC-41 | Comercio sin segmento usa precio base | Precio default del catálogo | PENDIENTE |
| PRC-42 | Override + promoción + cupón | Override como base, luego pipeline normal de descuentos | PENDIENTE |
| PRC-43 | Cambio de segmento del comercio | Precios se actualizan al nuevo segmento | PENDIENTE |
