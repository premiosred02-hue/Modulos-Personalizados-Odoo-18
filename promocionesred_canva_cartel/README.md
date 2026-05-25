# PromocionesRed — Constructor de Carteles (`promocionesred_canva_cartel`)

> **Módulo:** `promocionesred_canva_cartel`
> **Versión:** 18.0.1.1.0
> **Licencia:** LGPL-3
> **Autor:** REDLMC SL / Arqvi Dev
> **Entorno:** ✅ Odoo 18 Enterprise

---

## Descripción

Módulo de integración directa con la **API de Canva** para generar carteles promocionales desde Odoo, vinculados automáticamente a los leads del CRM y productos del catálogo.

Permite diseñar, generar y almacenar carteles de campaña (PremiosRed, REDROYAL, etc.) sin salir del ERP, con trazabilidad completa de cada pieza gráfica.

---

## Funcionalidades

| Funcionalidad | Descripción |
|---|---|
| 🎨 **Integración Canva API** | Genera carteles usando plantillas de Canva predefinidas |
| 📋 **Vinculación CRM** | Asocia cada cartel a un lead/oportunidad de CRM |
| 🏷️ **Catálogo de Plantillas** | Gestiona plantillas reutilizables por campaña |
| 📁 **Almacén de Carteles** | Historial completo de carteles generados |
| 🔗 **URL pública** | Genera enlace directo al cartel en Canva |

---

## Estructura del Módulo

```
promocionesred_canva_cartel/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── canva_template.py      # Modelo de plantillas Canva
│   └── canva_cartel.py        # Modelo de carteles generados
├── views/
│   ├── canva_template_views.xml
│   ├── canva_cartel_views.xml
│   └── menus.xml
├── security/
│   └── ir.model.access.csv
└── static/
    └── src/
        ├── components/        # Componentes OWL
        └── img/               # Iconos e imágenes
```

---

## Dependencias

```python
'depends': ['base', 'crm', 'web', 'mail']
```

---

## Configuración

1. **API Key de Canva**: Ajustes → PromocionesRed → Canva API Key
2. **Plantillas**: PromocionesRed → Carteles → Plantillas
3. **Generar cartel**: Desde un lead CRM → botón "Generar Cartel"

---

## Compatibilidad Enterprise 18

| Característica | Estado |
|---|---|
| `web.assets_backend` | ✅ Compatible |
| Vistas OWL | ✅ Compatible |
| CRM Enterprise | ✅ Compatible |

---

## Historial de Versiones

| Versión | Cambio |
|---|---|
| `18.0.1.1.0` | Migración a Enterprise, assets actualizados |
| `18.0.1.0.0` | Versión inicial Community |
