# REDLMC — OCR Local (`redlmc_ocr_local`)

> **Módulo:** `redlmc_ocr_local`
> **Versión:** 18.0.1.1.0
> **Licencia:** LGPL-3
> **Autor:** REDLMC SL / Arqvi Dev
> **Entorno:** ✅ Odoo 18 Enterprise

---

## Descripción

Extrae datos de **facturas recibidas en PDF** usando OCR local (sin enviar datos a servidores externos). Procesa los PDFs adjuntos en `account.move` para identificar automáticamente proveedor, número de factura, importe, fecha e impuestos, pre-rellenando el asiento contable.

Alternativa **100% privada y RGPD-compliant** al OCR de Odoo IAP (que envía documentos a servidores Odoo.com).

---

## Funcionalidades

| Funcionalidad | Descripción |
|---|---|
| 📄 **Extracción de PDF** | Lee texto de PDFs adjuntos en facturas recibidas |
| 🏷️ **Detección de Proveedor** | Identifica el proveedor por NIF/CIF o nombre |
| 💰 **Importes automáticos** | Extrae base, IVA y total |
| 📅 **Fecha de factura** | Detecta fecha de emisión del documento |
| 🔢 **Número de factura** | Extrae referencia del proveedor |
| ✅ **Sin dependencia cloud** | 100% local, sin envío de datos externos |

---

## Estructura del Módulo

```
redlmc_ocr_local/
├── __manifest__.py
├── __init__.py
├── models/
│   └── account_move.py        # Extensión con métodos OCR
├── wizard/
│   └── ocr_wizard.py          # Asistente de procesamiento manual
└── views/
    └── account_move_views.xml  # Botón "Procesar OCR" en facturas
```

---

## Dependencias Python

```python
# Requeridas en el contenedor Docker:
# pip install pypdf2 pdfplumber
external_dependencies = {'python': ['pypdf2', 'pdfplumber']}
```

> ⚠️ Si el módulo falla al procesar PDFs, ejecutar en el contenedor:
> ```bash
> docker exec odoo_18_enterprise_test pip install pypdf2 pdfplumber
> ```

---

## Dependencias Odoo

```python
'depends': ['account', 'mail']
```

---

## Uso

1. Abrir una factura de proveedor
2. Adjuntar el PDF de la factura original
3. Hacer clic en **"Procesar OCR"**
4. Revisar y confirmar los datos extraídos

---

## Compatibilidad Enterprise 18

| Característica | Estado |
|---|---|
| `account.move` Enterprise | ✅ Compatible |
| Adjuntos `ir.attachment` | ✅ Compatible |
| Sin dependencia de `account_edi` | ✅ Funciona sin módulos EDI |

---

## Limitaciones

- Solo procesa PDFs con texto seleccionable (no imágenes escaneadas sin OCR previo)
- Para PDFs escaneados, se requiere `tesseract` instalado en el contenedor

---

## Historial de Versiones

| Versión | Cambio |
|---|---|
| `18.0.1.1.0` | Migración a Enterprise, sin cambios funcionales |
| `18.0.1.0.0` | Versión inicial Community |
