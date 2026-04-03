# Checklist Admin — Control de Acceso y Permisos

**Fuente:** Documentación de roles YOM (CLIENT_ADMIN, ADMIN)  
**Cuándo ejecutar:** Post-deploy, cambios en autenticación, onboarding cliente nuevo  
**Plataforma:** admin.youorder.me

---

## Autenticación Admin

| ID | Caso | Cómo validar | Estado |
|----|------|--------------|--------|
| ADM-ACC-01 | Login admin exitoso | Ingresar credenciales válidas → debe redirigir a /dashboard | PENDIENTE |
| ADM-ACC-02 | Login admin — credenciales inválidas | Ingresar password incorrecto → debe mostrar error 401, acceso denegado | PENDIENTE |
| ADM-ACC-03 | Acceso a ruta admin sin autenticación | Navegar directo a `/admin/dashboard` sin login → debe redirigir a login, no exponer datos | PENDIENTE |
| ADM-ACC-04 | Acceso admin con rol de comercio | Usar token/sesión de un COMMERCE (B2B) e intentar acceder al admin → debe mostrar 403 | PENDIENTE |
| ADM-ACC-05 | Sesión expira por inactividad | Dejar sesión 30+ min inactiva → al volver debe redirigir a login | PENDIENTE |
| ADM-ACC-06 | Logout exitoso | Click en "Cerrar sesión" → token invalida, redirige a login | PENDIENTE |
| ADM-ACC-07 | Multi-tenant isolation | Admin de cliente A no puede ver datos de cliente B | PENDIENTE |

---

## Control de Permisos por Rol

| ID | Caso | Cómo validar | Estado |
|----|------|--------------|--------|
| ADM-ACC-10 | ADMIN ve todas las opciones del panel | Ingresar como ADMIN → verificar acceso a productos, pedidos, comercios, config | PENDIENTE |
| ADM-ACC-11 | CLIENT_ADMIN ve solo su cliente | Ingresar como CLIENT_ADMIN → solo datos de su tenant visible | PENDIENTE |
| ADM-ACC-12 | Rol sin permisos de edición | Usuario con rol read-only no puede editar productos ni promociones | PENDIENTE |
| ADM-ACC-13 | Acceso a sección de configuración | Solo roles autorizados pueden editar configuración de tienda | PENDIENTE |

---

## Acceso Anónimo B2B (configurado desde Admin)

| ID | Caso | Cómo validar | Estado |
|----|------|--------------|--------|
| ADM-ACC-20 | Activar acceso anónimo | En Admin → Configuración → activar "Acceso anónimo" → guardar → verificar en B2B que catálogo es visible sin login | PENDIENTE |
| ADM-ACC-21 | Desactivar acceso anónimo | En Admin → desactivar "Acceso anónimo" → guardar → verificar que B2B redirige a login al intentar ver catálogo | PENDIENTE |
| ADM-ACC-22 | Ocultar precios para anónimos | Activar "Ocultar precios" → en B2B sin login, precios no visibles | PENDIENTE |
| ADM-ACC-23 | Ocultar carrito para anónimos | Activar "Ocultar carrito" → en B2B sin login, botones de carrito no visibles | PENDIENTE |

---

## Notas de Escalamiento

Si algún caso falla con P0 (acceso no autorizado, datos de otro tenant expuestos):
→ Escalar inmediatamente usando `templates/escalation-templates.md`

**Post-mortem relacionado:** Ninguno registrado actualmente. Documentar si ocurre incidente.
