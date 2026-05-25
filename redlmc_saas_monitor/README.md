# REDLMC — SaaS Monitor Central (`redlmc_saas_monitor`)

> **Módulo:** `redlmc_saas_monitor`
> **Versión:** 18.0.1.1.0
> **Licencia:** OPL-1 *(Uso interno exclusivo REDLMC SL)*
> **Autor:** REDLMC SL / Arqvi Dev
> **Entorno:** ✅ Odoo 18 Enterprise

---

## Descripción

Panel de **monitorización centralizado** para todos los tenants SaaS gestionados por REDLMC SL. Proporciona visibilidad en tiempo real del estado de salud de cada instancia Odoo desplegada, métricas de uso, alertas de disponibilidad y gestión del ciclo de vida de las instancias.

Diseñado para el equipo técnico de REDLMC como **centro de operaciones** multi-tenant.

---

## Funcionalidades

| Funcionalidad | Descripción |
|---|---|
| 🖥️ **Dashboard multi-tenant** | Estado en tiempo real de todas las instancias |
| ✅ **Health Check** | Ping periódico a cada tenant para verificar disponibilidad |
| 📊 **Métricas de uso** | Usuarios activos, transacciones, storage usado |
| 🚨 **Alertas** | Notificación cuando un tenant cae o supera umbrales |
| 📅 **Historial de uptime** | Registro de disponibilidad histórica por tenant |
| 🔄 **Cron de monitoreo** | Ejecución automática cada N minutos |

---

## Estructura del Módulo

```
redlmc_saas_monitor/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── saas_tenant.py             # Modelo de tenant monitoreado
│   ├── saas_health_check.py       # Registro de health checks
│   └── saas_alert.py              # Alertas y notificaciones
├── views/
│   ├── saas_tenant_views.xml
│   ├── saas_monitor_dashboard.xml
│   └── menus.xml
├── data/
│   └── cron_monitor.xml           # Cron de health check (cada 5 min)
└── security/
    └── ir.model.access.csv
```

---

## Dependencias

```python
'depends': ['base', 'mail', 'redlmc_es_labels', 'redlmc_partner_ext']
```

---

## Modelo: `saas.tenant`

| Campo | Tipo | Descripción |
|---|---|---|
| `name` | Char | Nombre del tenant |
| `url` | Char | URL base del tenant |
| `estado` | Selection | activo / suspendido / error / inactivo |
| `ultimo_check` | Datetime | Último health check exitoso |
| `uptime_pct` | Float | % uptime de los últimos 30 días |
| `partner_id` | Many2one | Cliente asociado en `res.partner` |

---

## Configuración

1. **Añadir tenants**: SaaS Monitor → Tenants → Nuevo
2. **Intervalo de check**: Ajustes → REDLMC → Monitor → Cada N minutos
3. **Destinatarios de alerta**: Lista de correos para notificaciones de caída

---

## Compatibilidad Enterprise 18

| Característica | Estado |
|---|---|
| Dashboard Enterprise (`spreadsheet_dashboard`) | 🔄 Evaluando integración |
| Notificaciones push Enterprise | ✅ Via `mail.message` |

---

## Notas de Licencia

> ⚠️ **OPL-1**: Módulo propietario de REDLMC SL. Prohibida su redistribución o copia sin autorización escrita.

---

## Historial de Versiones

| Versión | Cambio |
|---|---|
| `18.0.1.1.0` | Migración a Enterprise, sin cambios funcionales |
| `18.0.1.0.0` | Versión inicial Community |
