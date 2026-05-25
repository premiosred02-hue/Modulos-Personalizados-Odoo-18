# REDLMC Tenant Agent

**Agente de Telemetría para Odoo SaaS**

Este módulo es un componente fundamental de la arquitectura SaaS (Software as a Service) de REDLMC. Funciona como un agente silencioso ("headless") que se instala en todas las instancias satélite u operativas (Tenants), como por ejemplo PremiosRed u otras marcas de clientes.

## ¿Cómo Funciona?

El módulo no crea pantallas, menús, ni vistas gráficas para los usuarios del ERP. En su lugar, habilita un **Endpoint API** seguro y oculto.

### La Ruta de Conexión (Endpoint)
- **URL:** `http://[dominio-del-cliente]/redlmc/metrics`
- **Método:** `GET`
- **Autenticación:** Requiere un `Token Bearer` de seguridad.

### Datos Recopilados
Cuando el sistema central (REDLMC SaaS Monitor) consulta este Endpoint enviando la contraseña correcta, el agente responde instantáneamente con un objeto JSON en tiempo real:

1. **`tenant_id`**: Identificador único de la empresa o base de datos.
2. **`timestamp`**: Fecha y hora exacta de la consulta.
3. **`invoices_count`**: Cantidad de facturas emitidas y recibidas (para control de volumen).
4. **`contacts_count`**: Número de contactos activos (clientes/proveedores).
5. **`odoo_version`**: Versión exacta del código de Odoo instalada.
6. **`db_size_mb`**: Peso real de la base de datos en Megabytes.

## Configuración Técnica

Al instalar el módulo, funcionará con valores por defecto. Para configurarlo para producción, se deben añadir los siguientes **Parámetros del Sistema** en Odoo (Ajustes > Técnico > Parámetros del Sistema):

*   `redlmc_tenant.id`: (String) Asignar un ID identificador de la empresa (ej: `PREMIOSRED-01`). Por defecto es `UNKNOWN-TENANT`.
*   `redlmc_tenant.token`: (String) Contraseña o Token que debe coincidir con la petición de la API. Por defecto es `DEV-TOKEN`.

## Ejemplo de Demostración (Consola)

Puedes probarlo desde cualquier terminal en el servidor donde corre la instancia:

```bash
curl -X GET "http://localhost:8001/redlmc/metrics" \
     -H "Authorization: Bearer DEV-TOKEN"
```

**Respuesta Esperada:**
```json
{
  "tenant_id": "UNKNOWN-TENANT",
  "timestamp": "2026-05-14T19:05:59.573772",
  "invoices_count": 2,
  "contacts_count": 19,
  "odoo_version": "18.0-20260421",
  "db_size_mb": 87.72,
  "status": "ok"
}
```

## Arquitectura de Destino

Este módulo es pasivo. Solo responde cuando le preguntan.
El destino final es construir un "Panel de Control" (Dashboard en Next.js o en un Odoo Maestro) que haga `ping` diariamente a todas las bases de datos de clientes, recoja estas métricas, y permita a REDLMC SL facturar licencias, cobrar excesos de almacenamiento o monitorizar caídas sin tener que entrar manualmente a la base de datos de cada cliente.
