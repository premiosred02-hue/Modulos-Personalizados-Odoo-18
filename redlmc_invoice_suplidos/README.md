# REDLMC — Gestión de Suplidos (`redlmc_invoice_suplidos`)

> **Módulo:** `redlmc_invoice_suplidos`
> **Versión:** 18.0.1.1.0
> **Licencia:** LGPL-3
> **Autor:** REDLMC SL / Arqvi Dev
> **Entorno:** ✅ Odoo 18 Enterprise

---

## Descripción

Implementa la gestión de **suplidos en facturas** conforme a la normativa fiscal española. Un suplido es un gasto pagado por cuenta del cliente que se repercute en la factura sin margen, y que tiene un tratamiento especial en el IVA (no genera base imponible propia).

Extiende el modelo `account.move` para identificar, calcular y mostrar líneas de suplidos con desglose diferenciado en el total de la factura.

---

## Funcionalidades

| Funcionalidad | Descripción |
|---|---|
| ✅ **Campo `is_suplido`** | Checkbox en cada línea de factura |
| 💰 **Cálculo automático** | Separa base imponible real de importes suplidos |
| 📊 **Totales desglosados** | Muestra `Base Real` y `Suplidos` antes del widget de totales |
| 🔒 **Solo visible si hay suplidos** | No "ensucia" facturas normales |

---

## Estructura del Módulo

```
redlmc_invoice_suplidos/
├── __manifest__.py
├── __init__.py
├── models/
│   └── account_move.py        # Extensión de account.move y account.move.line
└── views/
    └── account_move_views.xml  # Vista heredada: checkbox + totales desglosados
```

---

## Modelo: `account.move.line`

```python
is_suplido = fields.Boolean(string='Es Suplido', default=False)
```

## Modelo: `account.move`

```python
amount_suplidos = fields.Monetary(compute='_compute_suplidos', store=True)
amount_base_real = fields.Monetary(compute='_compute_suplidos', store=True)
```

---

## Dependencias

```python
'depends': ['account']
```

---

## Vista (Enterprise 18)

> **Corrección Enterprise**: El XPath usa `list` en lugar de `tree`, adaptado a la estructura de Odoo 18 Enterprise:

```xml
<!-- Enterprise 18: usa 'list' en lugar de 'tree' -->
<xpath expr="//field[@name='invoice_line_ids']/list/field[@name='name']" position="after">
    <field name="is_suplido" optional="show"/>
</xpath>
```

---

## Uso Práctico

1. Abrir una factura de cliente o proveedor
2. En las líneas, activar "Es Suplido" para las líneas que correspondan
3. Los totales mostrarán automáticamente el desglose:
   - **Base Real**: Subtotal sin suplidos
   - **Suplidos**: Importe total de líneas suplidas

---

## Normativa Española Aplicable

- Art. 78.3.3° LIVA: Los suplidos no forman parte de la base imponible del IVA
- Requisito: El gasto debe haberse pagado **en nombre y por cuenta del cliente**

---

## Historial de Versiones

| Versión | Cambio |
|---|---|
| `18.0.1.1.0` | Enterprise: XPath corregido `tree→list`, formato versión estandarizado |
| `18.0.0.1.0` | Versión inicial Community |
