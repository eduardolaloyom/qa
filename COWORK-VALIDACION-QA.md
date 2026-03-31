# QA: Validación de Flujos Usuario en Codelpa y Surtiventas

**Objetivo:** Probar que la app funciona end-to-end Y que las variables de configuración se comportan correctamente en cada cliente.

**Duración:** ~60 min (30 min Codelpa + 30 min Surtiventas)

---

## 🔑 Variables Críticas por Cliente

### Codelpa (beta-codelpa.solopide.me)
- `purchaseOrderEnabled: true` → Campo OC debe existir
- `disableCommerceEdit: true` → Perfil comercio NO editable (bloqueado)
- `editAddress: false` → Dirección NO editable en checkout
- `hasAllDistributionCenters: true` → Stock multicentro (ver centros)
- `enableOrderApproval: true` → UI para aprobar órdenes
- `enableSellerDiscount: true` → Campo descuento visible

### Surtiventas (surtiventas.solopide.me)
- `purchaseOrderEnabled: false` → Campo OC NO debe existir
- `disableCommerceEdit: false` → Perfil comercio SÍ editable
- `editAddress: true` → Dirección SÍ editable en checkout
- `hasSingleDistributionCenter: true` → Stock single center (sin multicentro)
- `enableOrderApproval: false` → NO hay UI de aprobación
- `enableSellerDiscount: true` → Campo descuento visible

---

## 📋 Flujos a Ejecutar

### FLUJO 1: Compra Simple (validar variables base)

**Aplica:** Ambos clientes
**Variables:** `enableCoupons`, `hasStockEnabled`, `purchaseOrderEnabled`, `editAddress`
**Tiempo:** 10 min

#### Pasos:
1. Login con credenciales
2. Ve a `/products` (catálogo)
3. **Busca producto, haz click en "Agregar"**
4. Ve a `/cart`
5. **¿Ves un campo "Orden de Compra" o "OC"?**
   - **Codelpa:** DEBE existir (purchaseOrderEnabled=true) → Anota ubicación
   - **Surtiventas:** NO debe existir (purchaseOrderEnabled=false)
6. Agrega 2-3 productos más
7. **¿Hay campo "Cupón"?** (ambos deben tenerlo)
8. Haz click en "Confirmar pedido"
9. ¿Aparece formulario con dirección? Verifica:
   - **Codelpa:** Dirección está locked/readonly (editAddress=false)
   - **Surtiventas:** Dirección está editable (editAddress=true) → intenta cambiarla
10. Confirma el pedido
11. ¿Ves número de orden?

**Validar:**
```
[CLIENTE] FLUJO 1: Compra Simple

✓ Login exitoso
✓ Productos cargan con precio
✓ Campo OC:
  - Codelpa: ✓/❌ Existe → ubicación: [dónde]
  - Surtiventas: ✓/❌ NO existe (correcto)
✓ Campo cupón: ✓/❌ Existe
✓ Dirección en checkout:
  - Codelpa: ✓/❌ Locked/readonly (correcto)
  - Surtiventas: ✓/❌ Editable (correcto) → cambié a: [dirección nueva]
✓ Orden confirmada con número: [número]
```

---

### FLUJO 2: Descuentos y Stock

**Aplica:** Ambos clientes
**Variables:** `enableSellerDiscount`, `hasStockEnabled`, `limitAddingByStock`
**Tiempo:** 10 min

#### Pasos:
1. Login
2. Ve a `/products`
3. **¿Ves indicador de stock en tarjetas?** (ej: "Stock: 100", "Disponible: Ilimitado")
   - Si SÍ: Anota qué dice exactamente
   - Si NO: Anota "Sin indicador visible"
4. Agrega 1 producto al carrito
5. Ve a `/cart`
6. **¿Hay campo de "Descuento" o "Descuento %"?** (ambos deben tenerlo)
   - Si SÍ: Intenta agregar 10% descuento
   - Verifica que el total baja correctamente
7. Intenta agregar cantidad muy grande (ej: 100 unidades)
   - ¿El sistema permite?
   - ¿Cambió el precio unitario? (step pricing)
8. Intenta confirmar
   - ¿Hay alerta de monto mínimo?
   - ¿Se bloquea el checkout?

**Validar:**
```
[CLIENTE] FLUJO 2: Descuentos y Stock

✓ Stock visible en tarjetas: ✓/❌
  Texto que dice: "[texto exacto]"
✓ Campo descuento: ✓/❌ Existe
  - Si SÍ → apliqué 10% → total bajó: ✓/❌
✓ Cantidad grande (100 unidades):
  - Permitió: ✓/❌
  - Precio cambió (step pricing): ✓/❌
✓ Validación monto mínimo:
  - Alerta apareció: ✓/❌
  - Monto mínimo es: [monto]
```

---

### FLUJO 3: Perfil Comercio y Restricciones

**Aplica:** Ambos clientes (diferente por cliente)
**Variables:** `disableCommerceEdit`, `editAddress`, `pendingDocuments`
**Tiempo:** 5 min

#### Pasos:
1. Login
2. **Busca perfil de comercio:** prueba estas rutas:
   - `/profile`
   - `/account`
   - `/settings`
   - `/commerce`
   - O busca en menú (avatar, engranaje, etc.)
3. Cuando encuentres: **intenta editar campos (nombre, email, dirección, etc.)**
   - **Codelpa:** Campos deben estar LOCKED/READONLY (disableCommerceEdit=true)
   - **Surtiventas:** Campos deben estar EDITABLES (disableCommerceEdit=false)
4. **¿Hay notificación de "Documentos pendientes"?** (si aplica)

**Validar:**
```
[CLIENTE] FLUJO 3: Perfil Comercio

✓ Perfil ubicado en: [ruta]
✓ Campos de nombre/email/dirección:
  - Codelpa: ✓/❌ Locked/readonly (correcto)
  - Surtiventas: ✓/❌ Editables (correcto) → cambié nombre a: [nuevo nombre]
✓ Documentos pendientes:
  - Aparece notificación: ✓/❌
  - Si SÍ: count = [número]
```

---

### FLUJO 4: Stock y Distribución

**Aplica:** Ambos clientes (diferente por cliente)
**Variables:** `hasStockEnabled`, `hasAllDistributionCenters` (Codelpa) vs `hasSingleDistributionCenter` (Surtiventas)
**Tiempo:** 5 min

#### Pasos:
1. Login
2. Ve a `/products`
3. Mira una tarjeta de producto
4. **¿Ves botón "Ver stock", "Centros", "Distribución", o similar?**
   - Si SÍ: Haz click
   - **Codelpa:** Debe mostrar MÚLTIPLES centros (multicentro)
   - **Surtiventas:** NO debe haber botón (single center)
5. Screenshot del modal o lista de centros

**Validar:**
```
[CLIENTE] FLUJO 4: Stock y Distribución

✓ Stock visible: ✓/❌
✓ Botón "Ver stock/centros": ✓/❌
  - Codelpa: ✓/❌ Existe (multicentro) → centros: [nombres]
  - Surtiventas: ✓/❌ NO existe (single center, correcto)
```

---

### FLUJO 5: Órdenes y Aprobación

**Aplica:** Ambos clientes (diferente por cliente)
**Variables:** `enableOrderApproval`
**Tiempo:** 5 min

#### Pasos:
1. Login
2. Ve a `/orders` (historial de pedidos)
3. **¿Ves tabla con órdenes?**
   - ¿Cuál es el estado más común? (ej: "processing", "pending", "approved")
   - Enumera todos los estados que ves
4. **¿Hay botón "Aprobar", "Approve", "Validar" en alguna orden?**
   - **Codelpa:** Debe haber (enableOrderApproval=true)
   - **Surtiventas:** NO debe haber (enableOrderApproval=false)
5. Haz click en una orden para ver detalles
6. ¿Se ven items, precio total, fecha?

**Validar:**
```
[CLIENTE] FLUJO 5: Órdenes

✓ Órdenes cargadas: ✓/❌
✓ Estados encontrados: [lista de estados]
✓ Botón de aprobación:
  - Codelpa: ✓/❌ Existe (correcto) → ubicación: [dónde]
  - Surtiventas: ✓/❌ NO existe (correcto)
✓ Detalles orden visible: ✓/❌
```

---

### FLUJO 6: Promociones y Cupones (BONUS)

**Aplica:** Ambos clientes
**Variables:** `enableCoupons`, `useNewPromotions`
**Tiempo:** 5 min

#### Pasos:
1. Login
2. Ve a `/products`
3. **¿Ves badges de "Promoción", "Oferta", "%OFF"?** (Surtiventas las tiene, Codelpa no)
4. Agrega producto a carrito
5. Ve a `/cart`
6. **Ingresa un cupón** (pide a alguien si hay uno activo)
   - ¿Se aplica?
   - ¿El descuento aparece?
7. Si no tienes cupón válido, anota "No hay cupones activos en este momento"

**Validar:**
```
[CLIENTE] FLUJO 6: Promociones/Cupones

✓ Promociones visibles: ✓/❌
  - Codelpa: [cantidad encontrada]
  - Surtiventas: [cantidad encontrada]
✓ Cupón ingresado: [cupón]
  - Aplicó correctamente: ✓/❌
  - Descuento aparece: [monto] ✓/❌
```

---

## 📸 Entrega Final

Cuando termines, comparte:

### Por cliente (Codelpa + Surtiventas):
1. **Resumen por flujo** — ✓/❌ de cada validación
2. **Screenshots** — mínimo 1 por flujo (12+ total)
3. **Ubicaciones exactas** — rutas, labels, selectores si es posible
4. **Problemas encontrados** — cualquier comportamiento inesperado

### Formato de respuesta:

```markdown
## CODELPA (beta-codelpa.solopide.me)

### FLUJO 1: Compra Simple ✓
- Login exitoso ✓
- Productos cargan ✓
- Campo OC visible: ✓ (ubicación: justo antes de confirmar pedido)
- Cupón visible: ✓
- Dirección locked: ✓
- Orden confirmada: ✓ (OC-12345)
- [Screenshot 1]

### FLUJO 2: Descuentos y Stock ✓
- Stock visible: ✓ ("Stock: 150 unidades")
- Campo descuento: ✓
- Descuento aplicado: ✓ (bajó de $50k a $45k)
- Cantidad grande (100): ✓ Permitió
- Step pricing: ✓ Precio cambió
- Monto mínimo: ⚠️ $200k (NO permitió confirmar)
- [Screenshot 2]

[... continúa FLUJO 3, 4, 5, 6 con mismo formato ...]

## SURTIVENTAS (surtiventas.solopide.me)

### FLUJO 1: Compra Simple ✓
- Login exitoso ✓
- Productos cargan ✓
- Campo OC: ❌ NO existe (correcto — purchaseOrderEnabled=false)
- Cupón visible: ✓
- Dirección EDITABLE: ✓ (cambié a "Calle Nueva 123")
- Orden confirmada: ✓ (SV-67890)
- [Screenshot 1]

[... continúa FLUJO 2-6 ...]

## PROBLEMAS ENCONTRADOS

### Codelpa
- El monto mínimo no permite confirmar con $100k (requiere $200k)
- El botón de aprobación está grayed out (pero existe)

### Surtiventas
- Las promociones no cargan en el catálogo (pero flag=true)
- Campo descuento deshabilitado para este usuario
```

---

## ✅ Checklist

Antes de terminar:

- [ ] **CODELPA:**
  - [ ] Flujo 1: Compra + OC + dirección locked
  - [ ] Flujo 2: Stock + descuento
  - [ ] Flujo 3: Perfil locked
  - [ ] Flujo 4: Multicentro (Ver stock)
  - [ ] Flujo 5: Aprobación visible
  - [ ] Flujo 6: Cupones

- [ ] **SURTIVENTAS:**
  - [ ] Flujo 1: Compra sin OC + dirección editable
  - [ ] Flujo 2: Stock + descuento
  - [ ] Flujo 3: Perfil editable
  - [ ] Flujo 4: Single center (sin botón)
  - [ ] Flujo 5: Sin aprobación
  - [ ] Flujo 6: Cupones/promociones

---

## 🎯 Qué validamos en cada flujo

| Flujo | Codelpa | Surtiventas | Objetivo |
|-------|---------|-------------|----------|
| 1. Compra | OC + locked dir | Sin OC + editable dir | Permisos de compra y datos |
| 2. Descuentos | Stock + descuento | Stock + descuento | Descuentos y validaciones |
| 3. Perfil | Locked campos | Editable campos | Restricciones por config |
| 4. Stock | Multicentro | Single center | Distribución según config |
| 5. Órdenes | Aprobación ✓ | Aprobación ✗ | Flujos distintos por cliente |
| 6. Cupones | Cupones | Cupones + promociones | Descuentos y ofertas |

---

## 💡 Notas Importantes

- **Estos NO son tests técnicos** — son pruebas reales que simulas como usuario
- **Las variables importan** — cada flujo valida que la configuración funciona
- **Las diferencias entre clientes son ESPERADAS** — Codelpa y Surtiventas tienen configs diferentes
- **Si algo no funciona** — reporta exactamente qué esperabas vs qué pasó
- **Si encuentras un bug** — toma screenshot y anota paso a paso

---

## 📞 ¿Dudas?

- ¿No encuentras una ruta? → Busca en el menú, avatar, o settings
- ¿Un campo está bloqueado? → Eso PODRÍA ser correcto según la config
- ¿Se quedó cargando? → Espera 10-15 segundos y reintenta
- ¿Algo roto? → Reporta con screenshot
