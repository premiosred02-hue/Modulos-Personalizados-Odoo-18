# PromocionesRed — Onboarding (`promocionesred_onboarding`)

> **Módulo:** `promocionesred_onboarding`
> **Versión:** 18.0.1.1.0
> **Licencia:** OPL-1 *(Uso interno exclusivo REDLMC SL)*
> **Autor:** REDLMC SL / Arqvi Dev
> **Entorno:** ✅ Odoo 18 Enterprise

---

## Descripción

Módulo de **onboarding guiado** para nuevos clientes y usuarios de la plataforma PremiosRed. Define los pasos de bienvenida, tutoriales interactivos y listas de verificación de configuración inicial para que cada empresa pueda activar su entorno de forma autónoma.

Integra el sistema de **checklist nativo de Odoo Enterprise** con los flujos específicos de REDLMC.

---

## Funcionalidades

| Funcionalidad | Descripción |
|---|---|
| 📋 **Checklist de Bienvenida** | Pasos guiados para configuración inicial |
| 🎯 **Progreso por Empresa** | Seguimiento de avance por `res.company` |
| 📧 **Emails de Bienvenida** | Plantillas de correo automáticas al activar |
| 🔔 **Notificaciones** | Recordatorios para pasos pendientes |
| 🏢 **Multi-empresa** | Compatible con entornos multi-tenant |

---

## Estructura del Módulo

```
promocionesred_onboarding/
├── __manifest__.py
├── __init__.py
├── models/
│   └── onboarding_step.py     # Pasos personalizados de onboarding
├── data/
│   └── onboarding_data.xml    # Definición de pasos y configuración
├── views/
│   ├── onboarding_views.xml
│   └── menus.xml
└── security/
    └── ir.model.access.csv
```

---

## Dependencias

```python
'depends': ['base', 'mail', 'onboarding', 'redlmc_es_labels']
```

---

## Configuración

1. Módulo se activa automáticamente en la creación de nuevas bases de datos demo
2. Los pasos se gestionan en: Ajustes → PromocionesRed → Onboarding
3. El progreso es visible en el dashboard de cada empresa

---

## Compatibilidad Enterprise 18

| Característica | Estado |
|---|---|
| Módulo `onboarding` nativo Enterprise | ✅ Integrado |
| Multi-empresa | ✅ Compatible |
| `res.company` hooks | ✅ Compatible |

---

## Notas de Licencia

> ⚠️ **OPL-1**: Este módulo es de uso exclusivo interno de REDLMC SL. No redistribuir.

---

## Historial de Versiones

| Versión | Cambio |
|---|---|
| `18.0.1.1.0` | Migración a Enterprise, integración con módulo `onboarding` nativo |
| `18.0.1.0.0` | Versión inicial Community |
