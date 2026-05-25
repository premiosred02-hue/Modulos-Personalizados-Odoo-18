# Módulos Personalizados Odoo 18 Enterprise
> Módulos desarrollados para **PromocionesRed.com** sobre Odoo 18 Enterprise

## 📦 Módulos incluidos

### PromocionesRed Core
| Módulo | Descripción | Depende de |
|--------|-------------|------------|
| `promocionesred_core_models` | Modelos base (CRM, Contactos, Productos) | base, crm, sale, account |
| `promocionesred_dashboard` | Dashboard personalizado con métricas | web, base, mail, crm, core_models |
| `promocionesred_api_gateway` | Gateway API para integración React/TypeScript | base, core_models |
| `promocionesred_canva_cartel` | Editor de carteles publicitarios con QR | web, base |
| `promocionesred_onboarding` | Flujo de onboarding personalizado | redlmc_partner_ext, mail, portal |

### REDMLC
| Módulo | Descripción | Depende de |
|--------|-------------|------------|
| `redlmc_es_labels` | Etiquetas y localización española | base, contacts, account |
| `redlmc_partner_ext` | Extensión de contactos (roles, licencias, tiendas) | base, contacts, mail, redlmc_es_labels |
| `redlmc_licencias` | Gestión de licencias por empresa | base, sale, account, redlmc_partner_ext |
| `redlmc_saas_monitor` | Monitor de métricas SaaS multi-tenant | base, mail, redlmc_licencias |
| `redlmc_ai_assistant` | Asistente IA con Gemini para facturas | base, mail, account, web |
| `redlmc_ocr_local` | OCR local para facturas de proveedores | account, redlmc_ai_assistant |
| `redlmc_invoice_suplidos` | Gestión de facturas con suplidos | account |
| `redlmc_api_rest` | API REST para integración externa | base, redlmc_partner_ext |
| `redlmc_tenant_agent` | Agente de métricas por tenant | base |

## 🚀 Instalación

### Orden recomendado (por dependencias)
```
1. redlmc_es_labels
2. redlmc_partner_ext
3. redlmc_tenant_agent
4. redlmc_ai_assistant
5. redlmc_invoice_suplidos
6. redlmc_licencias
7. redlmc_ocr_local
8. redlmc_saas_monitor
9. redlmc_api_rest
10. promocionesred_core_models
11. promocionesred_dashboard
12. promocionesred_api_gateway
13. promocionesred_canva_cartel
14. promocionesred_onboarding
```

### Requisitos
- Odoo 18 Enterprise (`18.0+e`)
- PostgreSQL 16+
- Python 3.12+

### Copiar al servidor
```bash
git clone https://github.com/premiosred02-hue/Modulos-Personalizados-Odoo-18.git /mnt/custom-addons
```

Agregar al `odoo.conf`:
```ini
addons_path = ...,/mnt/custom-addons
```

## 📝 Errores conocidos y correcciones aplicadas

- Archivos Python guardados en **UTF-8 sin BOM** (compatible con Python 3.12+)
- Vistas XML con sintaxis **Odoo 18** (sin `attrs=` ni `states=`)
- Archivos de vista faltantes en `promocionesred_core_models` añadidos

## 🏢 Autor
**PromocionesRed.com** — Sistema de promociones y red de negocios
