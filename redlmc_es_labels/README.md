# REDLMC — Etiquetas España (`redlmc_es_labels`)

> **Módulo:** `redlmc_es_labels`
> **Versión:** 18.0.1.3.0
> **Licencia:** LGPL-3
> **Autor:** REDLMC SL
> **Entorno:** ✅ Odoo 18 Enterprise

---

## Descripción

Adapta la terminología nativa de Odoo al **estándar legal español**, estableciendo los términos correctos para el tipo de contacto (`res.partner`):

| Término Odoo | Término España |
|---|---|
| "Individuo" | **Persona Física** |
| "Compañía" | **Empresa** |

Aplica a todos los módulos que usan `res.partner`: CRM, Contabilidad, Contactos, Ventas, etc.

---

## Funcionalidades

| Funcionalidad | Descripción |
|---|---|
| 🏷️ **Etiquetas legales ES** | Reemplaza términos anglosajones por terminología española |
| ⚡ **Post-init hook** | Se aplica automáticamente al instalar en datos existentes |
| 🔄 **Compatible con datos demo** | Actualiza registros existentes de `res.partner` |
| 📋 **Menús contables ES** | Renombra menús de contabilidad al español estándar |

---

## Estructura del Módulo

```
redlmc_es_labels/
├── __manifest__.py
├── __init__.py                  # Incluye _post_init_hook
├── hooks.py                     # Hook de post-instalación
└── views/
    └── account_menu_es.xml      # Renombrado de menús contables
```

---

## Dependencias

```python
# Enterprise-ready: sin dependencias OCA
'depends': ['base', 'contacts', 'account']
```

> ⚠️ **NOTA ENTERPRISE**: Las dependencias OCA (`om_account_*`, `accounting_pdf_reports`, etc.) han sido **eliminadas** — no existen en Odoo 18 Enterprise. El módulo usa exclusivamente módulos nativos de Odoo.

---

## Post-init Hook

Al instalar, el hook ejecuta automáticamente:

```python
def _post_init_hook(env):
    # Actualiza todos los partners existentes con las etiquetas correctas
    env['res.partner'].search([]).write({'company_type': ...})
```

---

## Menús Contables Españolizados

El archivo `account_menu_es.xml` renombra los menús nativos de `account`:

- Tablero, Clientes, Proveedores, Contabilidad
- Facturas, Facturas rectificativas, Pagos
- Asientos Contables, Plan Contable, Impuestos, Diarios
- Apuntes Contables, Apuntes Analíticos

---

## Historial de Versiones

| Versión | Cambio |
|---|---|
| `18.0.1.3.0` | Enterprise: eliminadas deps OCA, XML limpiado de referencias OCA |
| `18.0.1.2.0` | Versión Community con deps OCA |
| `18.0.1.1.0` | Versión inicial |
