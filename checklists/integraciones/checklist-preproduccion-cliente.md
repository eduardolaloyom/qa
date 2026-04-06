# Checklist Pre-producción — Integraciones de Cliente

> Aplica para: **cliente nuevo** (primera puesta en producción) y **re-validación** (cliente existente que vuelve al pipeline por deuda técnica o cambios mayores).
>
> Completar este checklist ANTES de iniciar QA funcional (Playwright, Cowork, Maestro).
> Si hay items BLOQUEADO → escalar y no avanzar.

---

## Cómo usar

| Estado | Significado |
|--------|-------------|
| ☐ | Pendiente de validar |
| ✓ | Validado y listo |
| N/A | No aplica para este cliente |
| BLOQUEADO | Falla crítica — no avanzar hasta resolver |

**Re-validación:** Items que no cambiaron pueden marcarse N/A con nota de fecha:
`N/A — validado 2026-03-15, sin cambios desde entonces`

---

## [1] Configuración MongoDB

> Dueño: **Tech** (Diego C / Rodrigo)

| # | Item | Estado | Notas |
|---|------|--------|-------|
| INT-01 | Sites configurado y activo en `yom-stores` | ☐ | |
| INT-02 | Salesterms activos en `yom-production` para este cliente | ☐ | |
| INT-03 | Config flags revisados y correctos (`anonymousAccess`, `enableOrderApproval`, `enableCoupons`, etc.) | ☐ | Usar `mongo-extractor.py` para extraer |
| INT-04 | Login path correcto configurado (`/login` vs `/auth/jwt/login`) | ☐ | Depende del cliente |
| INT-05 | Centro(s) de distribución activos | ☐ | |
| INT-06 | Hooks en customer configurados según flags activos | ☐ | `shippingHook`, `stockHook`, `cartShoppingHook`, etc. |
| INT-07 | Perfiles aprobadores definidos | ☐ | Solo si `enableOrderApproval: true` |
| INT-08 | Formulario de creación de comercios configurado | ☐ | Solo si `enableCreateCommerce: true` |

---

## [2] Catálogo y datos

> Dueño: **Analytics** (Diego F / Nicole)

| # | Item | Estado | Notas |
|---|------|--------|-------|
| INT-10 | Fotos de productos cargadas (sin imágenes rotas) | ☐ | |
| INT-11 | Productos activos con precio y stock | ☐ | Mínimo para poder testear un pedido completo |
| INT-12 | Categorías configuradas y visibles | ☐ | |
| INT-13 | Segmento base existe con todos los comercios asignados | ☐ | Prioridad alta (ej: 10000) |
| INT-14 | Overrides del segmento base con `enabled=false` por producto | ☐ | Evita que aparezcan precios trampa |
| INT-15 | Overrides de segmentos comerciales con `enabled=true` y precio real | ☐ | |
| INT-16 | Sin productos con precio trampa ($99.999) visibles en catálogo | ☐ | Indica override base sin segmento activo |
| INT-17 | Al menos un comercio de prueba activo y asignado a segmentos | ☐ | Para poder hacer QA funcional |

---

## [3] Acceso y usuarios

> Dueño: **Tech** (Diego C / Rodrigo)

| # | Item | Estado | Notas |
|---|------|--------|-------|
| INT-20 | Subdominio B2B activo con SSL (`https://{cliente}.youorder.me`) | ☐ | Abrir en browser, debe cargar sin error |
| INT-21 | Usuario vendedor creado (APP) | ☐ | Credenciales entregadas a QA |
| INT-22 | Usuario comercio creado (B2B) | ☐ | Credenciales entregadas a QA |
| INT-23 | Usuario admin creado | ☐ | Credenciales entregadas a QA |

---

## [4] Integraciones externas

> Dueño: **Tech + Analytics**
> *Completar solo si el cliente tiene ERP u otros servicios externos. Si no aplica, marcar toda la sección N/A.*

| # | Item | Estado | Notas |
|---|------|--------|-------|
| INT-30 | API del cliente responde (health check: `curl {api}/health → 200`) | ☐ | |
| INT-31 | Solo HTTPS — sin endpoints HTTP plano expuestos | ☐ | |
| INT-32 | Autenticación del hook activa (token/credenciales válidos) | ☐ | |
| INT-33 | IPs de YOM en whitelist del cliente (requests no bloqueados) | ☐ | |
| INT-34 | Endpoints requeridos disponibles: comercios, productos, stock, overrides, segmentos | ☐ | |
| INT-35 | Tiempo de respuesta < 100s con datos completos | ☐ | |
| INT-36 | Paginación implementada (`?page=1&limit=50`) | ☐ | |
| INT-37 | Filtro de fechas funcional (`?updated_from=YYYY-MM-DD`) | ☐ | |

---

## [5] Documentos tributarios

> Dueño: **Tech**
> *Completar solo si `enablePaymentDocumentsB2B`, `enableInvoicesList` o `enableCreditNotes` = true. Si no aplica, marcar toda la sección N/A.*

| # | Item | Estado | Notas |
|---|------|--------|-------|
| INT-40 | RUT y razón social configurados | ☐ | |
| INT-41 | Giro comercial definido | ☐ | |
| INT-42 | Tipo de documento configurado (boleta / factura) | ☐ | Según tipo de comercio |
| INT-43 | Notas de crédito habilitadas | ☐ | Solo si `enableCreditNotes: true` |

---

## [6] Gate de aprobación

> Completar luego de revisar todas las secciones anteriores.

| Sección | Estado | Items bloqueantes |
|---------|--------|-------------------|
| [1] Config MongoDB | | |
| [2] Catálogo y datos | | |
| [3] Acceso y usuarios | | |
| [4] Integraciones externas | | |
| [5] Documentos tributarios | | |

**Veredicto:**

| Estado | Condición | Acción |
|--------|-----------|--------|
| **LISTO** | Todos los items ✓ o N/A, cero BLOQUEADO | Avanzar a QA funcional (`playbook-qa-cliente-nuevo.md`) |
| **CON CONDICIONES** | Items ☐ no críticos, ningún BLOQUEADO | Avanzar con plan de resolución documentado |
| **BLOQUEADO** | Al menos un item en estado BLOQUEADO | No avanzar — escalar a dueño correspondiente |

**Fecha de validación:** _______________
**Validado por:** _______________
**Veredicto final:** _______________
