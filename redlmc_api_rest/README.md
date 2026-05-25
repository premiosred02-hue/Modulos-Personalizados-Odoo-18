# REDLMC — API REST (`redlmc_api_rest`)

> **Módulo:** `redlmc_api_rest`
> **Versión:** 18.0.1.1.0
> **Licencia:** LGPL-3
> **Autor:** REDLMC SL / Arqvi Dev
> **Entorno:** ✅ Odoo 18 Enterprise

---

## Descripción

Exposición de una **API REST segura** sobre Odoo 18 Enterprise para integración con sistemas externos (React Portal, Supabase, herramientas de terceros). Proporciona endpoints estandarizados con autenticación por API Key o JWT para acceder a datos críticos de negocio.

---

## Endpoints Disponibles

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/v1/partners` | Lista de contactos/clientes |
| `GET` | `/api/v1/leads` | Leads del CRM |
| `POST` | `/api/v1/leads` | Crear nuevo lead |
| `GET` | `/api/v1/invoices` | Facturas |
| `GET` | `/api/v1/products` | Catálogo de productos |
| `POST` | `/api/v1/webhook` | Receptor de webhooks externos |

---

## Autenticación

```http
Authorization: Bearer <API_KEY>
X-API-Key: <API_KEY>
```

La API Key se configura en: **Ajustes → REDLMC → API Keys**

---

## Estructura del Módulo

```
redlmc_api_rest/
├── __manifest__.py
├── __init__.py
├── controllers/
│   ├── main.py                # Controlador principal REST
│   └── auth.py                # Autenticación y validación
├── models/
│   └── api_key.py             # Modelo de API Keys
└── security/
    └── ir.model.access.csv
```

---

## Dependencias

```python
'depends': ['base', 'web', 'mail']
```

---

## Configuración

1. Instalar módulo
2. Crear API Key: Ajustes → REDLMC → API REST → Nueva Key
3. Asignar permisos por endpoint
4. Usar la key en cabeceras HTTP de las peticiones externas

---

## Integración con React Portal

```javascript
// Ejemplo de uso desde React
const response = await fetch('http://localhost:8002/api/v1/leads', {
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  }
});
```

---

## Compatibilidad Enterprise 18

| Característica | Estado |
|---|---|
| Controladores `http.Controller` | ✅ Compatible |
| Rate limiting | ✅ Implementado |
| CORS configurado | ✅ Habilitado para React |

---

## Historial de Versiones

| Versión | Cambio |
|---|---|
| `18.0.1.1.0` | Migración a Enterprise, endpoints actualizados |
| `18.0.1.0.0` | Versión inicial Community |
