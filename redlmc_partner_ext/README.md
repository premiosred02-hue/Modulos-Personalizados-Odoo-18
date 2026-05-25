# REDLMC — Partners SaaS (`redlmc_partner_ext`)

> **Módulo:** `redlmc_partner_ext`
> **Versión:** 18.0.1.4.0
> **Licencia:** LGPL-3
> **Autor:** REDLMC SL / Arqvi Dev
> **Entorno:** ✅ Odoo 18 Enterprise

---

## Descripción

Extiende `res.partner` con un **perfil SaaS completo** para clientes y licenciatarios de la plataforma REDLMC/PremiosRed. Añade campos de identificación fiscal española, estado de verificación KYB (*Know Your Business*), datos de tenant y métricas de contrato SaaS.

---

## Funcionalidades

| Funcionalidad | Descripción |
|---|---|
| 🆔 **NIF/CIF español** | Campo validado para la identificación fiscal española |
| 🏢 **Tipo de empresa ES** | Persona Física / Empresa (integrado con `redlmc_es_labels`) |
| 🔍 **KYB Status** | Estados: Incompleto / Pendiente / Verificado / Rechazado |
| ☁️ **Datos de Tenant** | URL, plan, fecha de activación para clientes SaaS |
| 📊 **Métricas de Contrato** | MRR, licencias activas, estado de pago |
| 📋 **Pestaña REDLMC** | Grupo de campos dedicado en el formulario del partner |

---

## Estructura del Módulo

```
redlmc_partner_ext/
├── __manifest__.py
├── __init__.py
├── models/
│   └── res_partner.py             # Extensión principal de res.partner
├── views/
│   ├── res_partner_views.xml      # Pestaña "REDLMC SaaS" en formulario
│   └── menus.xml
├── security/
│   ├── redlmc_partner_security.xml
│   └── ir.model.access.csv
└── data/
    └── partner_ext_data.xml       # Valores por defecto
```

---

## Campos Añadidos a `res.partner`

| Campo | Tipo | Descripción |
|---|---|---|
| `redlmc_nif` | Char | NIF/CIF español (validado) |
| `redlmc_kyb_estado` | Selection | Estado verificación KYB |
| `redlmc_tenant_url` | Char | URL del tenant SaaS |
| `redlmc_plan` | Selection | Plan contratado (Basic/Pro/Enterprise) |
| `redlmc_mrr` | Monetary | Monthly Recurring Revenue |
| `redlmc_licencias_count` | Integer | Número de licencias activas |
| `redlmc_fecha_activacion` | Date | Fecha de activación del SaaS |

---

## Dependencias

```python
'depends': ['base', 'contacts', 'account', 'redlmc_es_labels']
```

---

## Estados KYB

```
Incompleto ⬅️ → Pendiente revisión ADM → Verificado ✅
                                        → Rechazado ❌
```

---

## Compatibilidad Enterprise 18

| Característica | Estado |
|---|---|
| `web_enterprise` — formulario mejorado | ✅ Compatible |
| Vista Kanban Enterprise de Contactos | ✅ Compatible |
| Grupos de seguridad granulares | ✅ Implementado |

---

## Historial de Versiones

| Versión | Cambio |
|---|---|
| `18.0.1.4.0` | Enterprise: añadida nota de compatibilidad `web_enterprise` |
| `18.0.1.3.0` | Añadido campo `redlmc_kyb_estado` con selección |
| `18.0.1.2.0` | Campos de métricas MRR añadidos |
| `18.0.1.0.0` | Versión inicial Community |
