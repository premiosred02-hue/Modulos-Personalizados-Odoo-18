# promocionesred_dashboard

Módulo Odoo 18 — Panel administrativo unificado de **PremiosRed / REDROYAL SL**.

## Descripción

Dashboard administrativo completo migrado desde React.js + Supabase a **Odoo 18 nativo** con Owl Framework.

## Módulos funcionales

| Sección | Descripción |
|---|---|
| 📊 Dashboard | KPIs globales, métricas en tiempo real |
| 🎯 Leads/CRM | Pipeline RBAC (ADM/COL/SUB), notas, etapas |
| 🌐 Red | Jerarquía COL/SUB/SPP con árbol visual |
| 📱 QR | Generador SHA-256, portal `/verify/`, API REST |
| 💰 Finanzas | Modelo 55/45, break-even, costes, bancos, fiscal |
| 📧 Email | Campañas con tracking de aperturas |
| ⚖️ Legal | Contratos por actor (COL/SUB/SPP/COM/ASE) |
| 🔍 Auditoría | Log de acciones por usuario |
| 🔐 Seguridad | Gestión de accesos y roles |
| 🚀 Onboarding | Formularios de alta por tipo de actor |
| 🏢 Empresas | CRUD de empresas colaboradoras |
| 🎫 Cupones | Gestión del ciclo de vida de cupones |
| 📦 Packs | Configuración de packs digitales |
| 👥 Promotores | Gestión de promotores comerciales |

## Stack técnico

- **Odoo 18** — Community Edition
- **Owl Framework** — Componentes reactivos (XML + JS)
- **Python HTTP Controllers** — API REST pública `/api/qr/`
- **QWeb** — Templates públicas (portal de validación QR)
- **SHA-256** — Tokens de identificación seguros

## Instalación

```bash
# Copiar a extra-addons de Odoo
cp -r promocionesred_dashboard /path/to/odoo/extra-addons/

# En Odoo: Ajustes → Activar modo desarrollador → Actualizar lista de módulos → Instalar
```

## Estructura

```
promocionesred_dashboard/
├── __manifest__.py
├── __init__.py
├── controllers/
│   └── verify.py          # API REST + Portal público
├── models/
│   ├── actor.py
│   ├── lead.py
│   └── ...
├── views/
│   ├── actions.xml
│   ├── menus.xml
│   └── qr_verify_portal.xml
├── security/
│   └── ir.model.access.csv
├── data/
│   └── demo_data.xml
└── static/src/
    ├── app.js             # Componente raíz Owl
    ├── app.xml
    ├── app.css            # Sistema de diseño
    └── components/
        ├── Dashboard.*
        ├── LeadForm.*     # CRM Pipeline
        ├── MyQRView.*     # QR Management
        ├── FinanceView.*  # Centro Financiero
        └── ...
```

## Licencia

Propietario — REDLMC SL / REDROYAL SL. Todos los derechos reservados.
