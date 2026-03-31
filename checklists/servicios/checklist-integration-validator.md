# Checklist QA — Integration Validator (Lambda)

> Fuente: [Integration Validator — Notion](https://www.notion.so/320d8139ba4e80cc80d9c413e092ab2e)
> Componente: Lambda AWS que valida datos de integraciones antes de publicar
> Fecha creación: 2026-03-27

---

## Contexto

El Integration Validator es una Lambda orquestada desde el Admin Backend. Valida que archivos CSV/JSON/Excel de integraciones cumplan con estructura y tipos requeridos antes de publicarse en producción. Pipeline de 6 pasos: parse → classify → load rules → extract → load to DataFrame → validate.

---

## 1. Validación por archivo

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| IV-01 | CSV válido con todas las columnas requeridas | `status: success`, `details: []` | PENDIENTE |
| IV-02 | CSV con columna requerida faltante | `status: error`, detalle "Missing required column: X" | PENDIENTE |
| IV-03 | CSV con tipo incorrecto (texto en columna number) | Error en filas específicas con "invalid type" | PENDIENTE |
| IV-04 | CSV con valores NULL en columna not-null | Error indicando "contains NULL in required column" | PENDIENTE |
| IV-05 | CSV con IDs duplicados | Error indicando duplicados | PENDIENTE |
| IV-06 | Excel válido (primera hoja) | Validación exitosa | PENDIENTE |
| IV-07 | JSON array válido | Validación exitosa | PENDIENTE |
| IV-08 | Archivo >256KB se chunquea automáticamente | Chunks se procesan y unen correctamente | PENDIENTE |
| IV-09 | Archivo vacío | Error 400 descriptivo | PENDIENTE |
| IV-10 | Formato no soportado (ej: PDF) | Error 400 "formato no soportado" | PENDIENTE |

---

## 2. Validación por URL

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| IV-20 | URL de API que retorna JSON válido | Validación exitosa | PENDIENTE |
| IV-21 | URL que retorna 404 | Error controlado | PENDIENTE |
| IV-22 | URL con timeout (>30s) | Error de timeout, no queda colgado | PENDIENTE |
| IV-23 | URL que retorna archivo >50MB | Rechazado por tamaño | PENDIENTE |
| IV-24 | URL con headers personalizados | Headers se pasan correctamente al request | PENDIENTE |

---

## 3. Encodings y formatos

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| IV-30 | CSV en UTF-8 | Parseado correctamente | PENDIENTE |
| IV-31 | CSV en UTF-8 con BOM (utf-8-sig) | Parseado correctamente | PENDIENTE |
| IV-32 | CSV en Latin-1 (caracteres acentuados) | Parseado correctamente | PENDIENTE |
| IV-33 | CSV en CP1252 (Windows) | Parseado correctamente | PENDIENTE |
| IV-34 | JSON con campos anidados | Se expanden (ej: `locations_0_city`) | PENDIENTE |

---

## 4. Acceso y autenticación

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| IV-40 | Acceso con guest token desde yom-api | Lambda acepta y procesa | PENDIENTE |
| IV-41 | Acceso con login normal de Admin | Lambda acepta y procesa | PENDIENTE |
| IV-42 | Request sin JWT al Gateway | Rechazado antes de llegar a Lambda | PENDIENTE |
| IV-43 | JWT expirado | Rechazado por Gateway | PENDIENTE |

---

## 5. Respuestas y edge cases

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| IV-50 | Validación exitosa retorna columnas usadas y no usadas | `columns_used`, `columns_not_used`, `possible_columns` presentes | PENDIENTE |
| IV-51 | Integration type inexistente | Error "IntegrationNotFoundError" (400) | PENDIENTE |
| IV-52 | Rules override parcial | Deep-merge con rules base, override tiene precedencia | PENDIENTE |
| IV-53 | Base64 inválido en archivo | Error 400 descriptivo | PENDIENTE |
