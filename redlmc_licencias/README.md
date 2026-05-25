# REDLMC — Licencias y Royalties (`redlmc_licencias`)

> **Módulo:** `redlmc_licencias`
> **Versión:** 18.0.1.1.0
> **Licencia:** OPL-1 *(Uso interno exclusivo REDLMC SL)*
> **Autor:** REDLMC SL / Arqvi Dev
> **Entorno:** ✅ Odoo 18 Enterprise

---

## Descripción

Sistema de **gestión de licencias de software y royalties** para REDLMC SL. Controla el ciclo de vida de licencias emitidas a clientes, vencimientos, renovaciones automáticas y el cálculo de royalties asociados.

Integra con `redlmc_partner_ext` para el perfil SaaS del contacto y con contabilidad para la facturación automática de renovaciones.

---

## Funcionalidades

| Funcionalidad | Descripción |
|---|---|
| 🔑 **Gestión de Licencias** | CRUD completo de licencias por cliente/producto |
| 📅 **Control de Vencimientos** | Alertas automáticas 30/15/7 días antes |
| 🔄 **Renovaciones Automáticas** | Cron de renovación con generación de factura |
| 💵 **Cálculo de Royalties** | Porcentaje sobre ventas de cada licenciado |
| 📊 **Dashboard de Licencias** | Vista resumen del estado de todas las licencias |
| 📧 **Emails automáticos** | Notificaciones de vencimiento y renovación |

---

## Estructura del Módulo

```
redlmc_licencias/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── redlmc_licencia.py         # Modelo principal de licencia
│   ├── redlmc_royalty.py          # Modelo de royalties
│   └── res_partner.py             # Extensión partner (campo licencias)
├── views/
│   ├── licencia_views.xml
│   ├── royalty_views.xml
│   └── menus.xml
├── data/
│   └── cron_data.xml              # Cron de vencimientos y renovaciones
├── report/
│   └── licencia_report.xml        # Informe PDF de licencia
└── security/
    └── ir.model.access.csv
```

---

## Dependencias

```python
'depends': ['base', 'mail', 'account', 'redlmc_es_labels', 'redlmc_partner_ext']
```

---

## Estados de Licencia

```
Borrador → Activa → Por Vencer → Vencida
                  ↓
              Renovada → Activa
```

---

## Configuración

1. **Tipos de licencia**: Ajustes → REDLMC → Tipos de Licencia
2. **Porcentaje royalty**: Por producto/categoría
3. **Periodo de aviso**: Configurable por tipo (30 días por defecto)

---

## Compatibilidad Enterprise 18

| Característica | Estado |
|---|---|
| Facturación automática Enterprise | ✅ Integrado |
| Informes PDF (`ir.actions.report`) | ✅ Compatible |
| Accesos por grupos de seguridad | ✅ Implementado |

---

## Notas de Licencia

> ⚠️ **OPL-1**: Módulo propietario de REDLMC SL. Prohibida su distribución o copia sin autorización escrita.

---

## Historial de Versiones

| Versión | Cambio |
|---|---|
| `18.0.1.1.0` | Migración a Enterprise, adaptado a módulos nativos |
| `18.0.1.0.0` | Versión inicial Community |
