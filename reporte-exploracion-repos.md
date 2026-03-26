# Reporte de Exploracion de Repos — YOM QA
> Fecha: 2026-03-25
> Repos: YOMCL/app-mobile, YOMCL/b2b

---

## Hallazgos clave (vs lo que se dijo en la reunion)

| Tema | Lo que se dijo | Lo que es realmente |
|---|---|---|
| **APP stack** | Java Android + RN solo login | **100% React Native + TypeScript + Expo** (con modulos nativos Java para Realm/Session) |
| **Tests APP** | No hay tests | **Si hay** — Jest + Testing Library configurados, CI corre tests en PRs |
| **Tests B2B** | Solo GitHub Actions (codigo) | **Jest + Cypress E2E** — Cypress corre cada 4h contra staging |
| **CI/CD APP** | Nada automatico | **Si tiene** — GH Actions: test + lint en PRs. EAS Build para deploys |
| **CI/CD B2B** | GitHub Actions | **Completo** — test + lint + Docker build + deploy a EKS (Kubernetes) |
| **Staging** | No hay staging | **Si existe** — `soprole.solopide.me` (Cypress E2E corre ahi) |
| **testIDs APP** | No se pregunto | **No existen** — Blocker para Maestro |

---

## APP Mobile (YOMCL/app-mobile)

### Stack
- React Native 0.79.5 + React 19 + Expo 53
- TypeScript (strict mode)
- Estado: Context API + Custom Hooks (no Redux)
- Offline: Realm via modulo nativo Java (`JavaRealmModule`)
- Auth: email/password + Microsoft OAuth, tokens en `SessionBridge` nativo

### Tests existentes
- **Jest** configurado con `@testing-library/react-native`
- Al menos 1 test: `TransportCodeScreen.test.tsx`
- Scripts: `npm test`, `npm run test:watch`, `npm run test:coverage`

### CI/CD
- `.github/workflows/ci.yml` — triggers en PR a production/staging
- Steps: checkout → Node 22 → install → **test** → **lint**
- EAS Build para generar APKs (development, staging, production)

### Archivos clave para QA
| Archivo | Proposito |
|---|---|
| `src/services/AuthService.ts` | Login (email/password + Microsoft) |
| `src/services/JavaRealmNativeService.ts` | Acceso a BD Realm offline |
| `src/hooks/useJavaRealmCart.ts` | Gestion de carrito offline |
| `src/contexts/JavaRealmContext.tsx` | State management principal |
| `src/screens/OrderTakerScreen/` | Pantalla de toma de pedido |
| `jest.config.js` | Configuracion Jest |
| `.github/workflows/ci.yml` | CI pipeline |

### Problema: Sin testIDs
Los componentes React Native **no tienen `testID` ni `accessibilityLabel`**. Esto significa:
- Maestro no puede usar selectores por ID
- Solo puede usar texto visible (`tapOn: {text: "..."}`) o posicion
- Los YAML actuales usan `id: "email-input"` que **no va a funcionar**
- **Accion requerida:** Pedir al equipo que agregue testIDs a componentes criticos

---

## B2B (YOMCL/b2b)

### Stack
- Next.js 16.1.6 + React 19 + TypeScript
- UI: Material UI (MUI) v7
- HTTP: Axios 1.12 con registry multi-instancia
- Data fetching: SWR
- Error tracking: Sentry
- Deploy: Docker → Amazon ECR → Kubernetes (EKS)

### Tests existentes
- **Jest** para unit/component tests (`src/__tests__/`)
- **Cypress 14.5** para E2E (`cypress/`)
- Testing Library (react + jest-dom + user-event)
- Cypress con reporters: mochawesome + allure

### CI/CD (3 workflows)

| Workflow | Trigger | Que hace |
|---|---|---|
| `test.yml` | PR a staging/production | TypeScript check + lint + Jest tests |
| `main.yml` | Push a staging/production | Docker build + push ECR + deploy K8s |
| `e2e-scheduled-tests.yml` | Cada 4 horas + manual | **Cypress E2E contra soprole.solopide.me** + notifica Slack si falla |

### Multi-tenant
- Backend devuelve JWT del sitio via `GET /sites/store`
- JWT contiene: logo, nombre, anonymousAccess, y toda la config
- Frontend decodifica y usa via `StoreContext` / `useStore()`
- No hay routing por dominio en Next.js — la config viene del API

### Archivos clave para QA
| Archivo | Proposito |
|---|---|
| `src/auth/context/jwt/` | Autenticacion JWT completa |
| `src/lib/contexts/store/` | Config multi-tenant del sitio |
| `src/lib/contexts/cart/` | Carrito de compras |
| `src/lib/services/` | Logica de negocio (auth, cart, catalog, orders) |
| `src/lib/utils/axios/` | HTTP client con refresh token |
| `cypress.config.ts` | Config Cypress E2E |
| `.github/workflows/` | CI/CD pipelines |
| `jest.config.cjs` | Config Jest |

---

## Backend API (YOMCL/yom-api)

### Stack
- Node.js + Express (JavaScript puro, 4.5MB)
- Mongoose (49 modelos) + MongoDB
- Moleculer (microservicios internos)
- ElasticSearch (busqueda y catalogo)
- JWT auth (15min access token, 365d refresh token)
- Deploy: Docker + Kubernetes

### Tests existentes
- **Mocha + Chai + Sinon + SuperTest**
- 47 archivos de test (.spec.js, .integration.js, .service.spec.js)
- Scripts: `npm test`, `npm run test:unit`, `npm run test:integration`, `npm run test:service`
- CI: Docker Compose ejecuta tests en PRs a production/staging

### Endpoints principales
| Endpoint | Metodo | Proposito |
|---|---|---|
| `/api/v2/auth/local` | POST | Login (email + password) |
| `/api/v2/sites/store` | GET | Config del sitio (JWT con variables) |
| `/api/v2/products` | GET | Catalogo de productos |
| `/api/v2/orders` | GET/POST | Listar/crear ordenes |
| `/api/v2/cart` | GET/POST/PUT/DELETE | Carrito de compras |
| `/api/v2/promotions` | GET | Promociones activas |
| `/api/v2/coupons/validate` | POST | Validar cupon |
| `/api/v2/commerces` | GET | Comercios del usuario |
| `/api/v2/segments` | GET | Segmentos |
| `/api/v2/erp-integration` | GET | Historial de integraciones ERP |
| `/hooks/{cliente}` | POST | Webhooks ERP por cliente |

### Pricing (como se calculan precios)
```
Precio base → Promocion (percentage/amount/fixedprice) → Cupon → Descuento vendedor → Impuestos
```
- 3 tipos de descuento: `percentage` (0.1 = 10%), `amount` (fijo), `fixedprice`
- Descuento por volumen via `steps: [{lowerLimit, discount}]`
- Impuestos: IVACL, ILACL
- Logica en: `server/api/v2/promotion/promotion.rules.js`

### ERP (inyeccion de pedidos)
- 12 integraciones especificas por cliente (surtiventas, codelpa, soprole, etc.)
- Cada una en `server/hooks/{cliente}/`
- Modelo `ErpIntegration` registra cada intento con: hookUrl, requestBody, responseStatus, isSuccess, processingTime
- Flujo: transformar orden → obtener token ERP → POST al ERP → registrar resultado

### Multi-tenant (como funciona)
1. Frontend envia header `Origin: https://cliente.youorder.me`
2. Middleware `checkDomain()` extrae dominio
3. Middleware `checkSiteToken()` valida JWT del sitio
4. `req.site` queda poblado con toda la config del cliente
5. Cada query a MongoDB filtra por `domain` o `customerId`

### Archivos clave para QA
| Archivo | Proposito |
|---|---|
| `server/auth/auth.service.js` | Middleware de auth (checkDomain, checkSiteToken, checkToken) |
| `server/api/v2/promotion/promotion.rules.js` | Calculo de precios y descuentos |
| `server/api/v2/order/order.model.js` | Schema de ordenes con pricing completo |
| `server/api/v2/product/product.model.js` | Schema de productos |
| `server/hooks/` | Integraciones ERP por cliente |
| `server/routes.js` | Todas las rutas de la API |
| `.github/workflows/test.yml` | CI pipeline |

---

## Respuestas a las 12 preguntas de qa-master-prompt.md

| # | Pregunta | Respuesta |
|---|---|---|
| 1 | Cuantos repos? | 3 principales: app-mobile (APP), b2b (tienda+admin), yom-api (backend) |
| 2 | Lenguaje backend? | **JavaScript (Node.js + Express + Mongoose + Moleculer)** |
| 3 | Framework B2B? | **Next.js 16 + React 19 + MUI** (no Angular) |
| 4 | Framework Admin? | **Mismo repo que B2B** (Next.js 16 + React 19) |
| 5 | Framework APP? | **React Native 0.79 + Expo 53 + TypeScript** (no Java) |
| 6 | Base de datos? | MongoDB (confirmado) + Realm (offline en APP) |
| 7 | Librerias de testing? | APP: Jest + Testing Library. B2B: Jest + Cypress + Testing Library |
| 8 | CI/CD? | APP: GH Actions (test+lint). B2B: GH Actions (test+lint+build+deploy+E2E scheduled) |
| 9 | Estructura API? | Express con 45+ rutas en `/api/v2/`. Productos, ordenes, cart, auth, promotions, coupons, commerces, segments, stock, etc. |
| 10 | Autenticacion? | JWT (15min access + 365d refresh). Middleware: checkDomain → checkSiteToken → checkToken. APP: email+Microsoft. B2B: email+Google+Facebook |
| 11 | Sistema de pagos? | Modelo `Payment` en yom-api. `payment.enableNewPaymentModule` en sites. Pagos por transferencia/credito (no tarjeta) |
| 12 | Integraciones ERP? | 12 integraciones especificas en `server/hooks/` (surtiventas, codelpa, soprole, etc.). Modelo `ErpIntegration` registra cada intento |

---

## Implicaciones para el plan de QA

### Lo que cambia

1. **Maestro YAML necesitan reescribirse** — no hay testIDs, los selectores por `id:` no funcionaran. Hay que usar selectores por texto.

2. **B2B ya tiene Cypress E2E corriendo** — no necesitamos Playwright. Mejor **extender los tests Cypress existentes** con los casos de C1-C6.

3. **APP ya tiene Jest corriendo en CI** — podemos agregar unit tests directamente al repo, no necesitamos setup desde cero.

4. **Staging existe** — `soprole.solopide.me` ya se usa para E2E. No necesitamos crear uno.

### Proximos pasos concretos

| Accion | Quien | Prioridad |
|---|---|---|
| Pedir acceso a repo backend y admin | Lalo → Rodrigo | Alta |
| Pedir que agreguen testIDs a componentes criticos de APP | Lalo → Rodrigo | Alta (blocker Maestro) |
| Revisar los tests Cypress existentes del B2B | Lalo | Media |
| Extender Cypress con casos C1-C3 (login, compra, precios) | Tech (Diego/Isaac) | Media |
| Agregar unit tests a APP para servicios criticos | Tech (Rodrigo) | Baja |
