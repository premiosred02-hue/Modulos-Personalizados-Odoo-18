# 🤖 redlmc_ai_assistant — Gemini Ultra × Odoo 18 Enterprise

> **Empresa:** REDLMC SL (B26946525) · **Versión:** 18.0.1.1.0  
> **Requiere:** Odoo 18 **Enterprise** · Google Workspace Ultra · API Key Gemini  
> **Ref. Vault:** `80.20 SISTEMA-GESTION-DOCUMENTAL-ODOO.md`

---

## ¿Qué hace este módulo?

Integra **Gemini AI (Google Workspace Ultra)** con Odoo 18 Enterprise de forma nativa.

| Funcionalidad | Dónde en Odoo | Estado |
|---|---|---|
| 🤖 Clasificador automático de facturas | Contabilidad → Facturas proveedor → botón "Analizar con IA" | ✅ v1.0 |
| 🚨 Alertas fiscales automáticas | Cron diario → email al ADM | ✅ v1.0 |
| ⚙️ Configuración segura API Key | Ajustes → REDLMC AI | ✅ v1.0 |
| 🔗 Endpoint JSON-RPC para frontend | `/redlmc/ai/ask` | ✅ v1.0 |
| 💬 Widget chat AI en chatter | OWL component (próxima versión) | 🚧 v1.1 |
| 📄 Generador de contratos | Ventas → Contratos (próxima versión) | 🚧 v1.2 |

---

## Instalación

### 1. Copiar el módulo al addons_path

```powershell
# Desde la raíz de 03_HERRAMIENTAS-Y-CODIGO:
# El módulo ya está en esta carpeta. Solo hay que registrar el path.
# Ver: odoo-redlmc-dev/config/odoo.conf → addons_path
```

### 2. Instalar en Odoo

```powershell
# Desarrollo local:
docker exec odoo-redlmc-dev odoo -d odoo_redlmc_v2 -i redlmc_ai_assistant --stop-after-init

# Producción Hetzner:
docker exec odoo-redlmc-prod odoo -d odoo_redlmc_prod -i redlmc_ai_assistant --stop-after-init
```

### 3. Configurar la API Key

```
Odoo → Ajustes → 🤖 REDLMC AI → Gemini API Key → [pegar tu clave]
```

**Obtener API Key gratuita:**  
→ https://aistudio.google.com/app/apikey  
→ Selecciona tu proyecto "REDLMC-Odoo-Integration" en Google Cloud  
→ Copia la clave (empieza por `AIza...`)

---

## Estructura del módulo

```
redlmc_ai_assistant/
│
├── __manifest__.py              ← Metadatos del módulo
├── __init__.py                  ← Entry point
│
├── models/
│   ├── gemini_service.py        ← ⭐ Servicio core Gemini (punto central)
│   ├── res_config_settings.py   ← Configuración en Ajustes de Odoo
│   └── ai_invoice_classifier.py ← Clasificador de facturas (hereda account.move)
│
├── controllers/
│   └── main.py                  ← Endpoints HTTP (/redlmc/ai/ask, /ping)
│
├── views/
│   ├── res_config_settings_views.xml  ← UI en Ajustes
│   ├── ai_assistant_views.xml         ← Botón + pestaña en facturas
│   └── menus.xml                      ← Sin menús propios
│
├── data/
│   └── cron_data.xml            ← Cron alertas fiscales (diario 8:00)
│
├── security/
│   └── ir.model.access.csv      ← ACL del servicio Gemini
│
└── static/src/components/       ← (v1.1) Widget OWL para chat en chatter
    ├── AiChatWidget.xml
    ├── AiChatWidget.js
    └── AiChatWidget.css
```

---

## Seguridad

| Aspecto | Implementación |
|---|---|
| **API Key** | Almacenada en `ir.config_parameter` (cifrada en BD). Nunca en código fuente. |
| **Timeout** | 30 segundos por llamada. Si supera → UserError. |
| **Reintentos** | 2 reintentos automáticos en errores 5xx de Google. |
| **Rate limiting** | Controlado por Google (Workspace Ultra: ilimitado para APIs de Workspace). |
| **Logs** | Errores registrados en `_logger` de Odoo (nunca la API Key). |
| **Acceso** | Solo usuarios internos (`base.group_user`) pueden llamar al servicio. |
| **.gitignore** | Nunca commitear `*.json`, `*.key`, `.env`, secrets/. Ver `.gitignore`. |

---

## Uso — Clasificador de Facturas

1. Ve a **Contabilidad → Proveedores → Facturas**
2. Abre una factura de proveedor
3. Adjunta el **PDF** de la factura (botón 📎)
4. Pulsa **🤖 Analizar con IA**
5. Gemini extrae: proveedor, importe, fecha, concepto, IVA
6. Si confianza ≥ 80% → los campos se rellenan automáticamente
7. Revisa los datos → **Confirmar factura**

---

## Uso — Alertas Fiscales

El cron se ejecuta automáticamente cada día a las 8:00.  
Se activa desde: **Ajustes → REDLMC AI → Alertas fiscales automáticas ✅**

Para probar manualmente:
```
Odoo → Ajustes → Técnico → Acciones programadas → REDLMC AI — Alertas Fiscales → Ejecutar manualmente
```

---

## Changelog

| Versión | Fecha | Cambios |
|---|---|---|
| 18.0.1.1.0 | 2026-05-25 | Migración a Enterprise, README actualizado |
| 18.0.1.0.0 | 2026-05-08 | v1.0 inicial: servicio Gemini + clasificador facturas + alertas fiscales |

---

## Roadmap

- **v1.1** Widget OWL de chat en el chatter de cualquier registro Odoo
- **v1.2** Generador de contratos desde plantillas + datos del registro
- **v1.3** Sync Drive → Odoo: subir PDF a carpeta Drive → vendor.bill automático
- **v2.0** Multi-empresa: soporte REDLMC + REDROYAL en una sola instancia

---

*REDLMC SL · NIF B26946525 · redlmc_ai_assistant v18.0.1.0.0 · 2026-05-08*
