# PromocionesRed Core Models (Traducción Headless de `types.ts`)

Este módulo funciona como la "Fuente de Verdad" de todo el ecosistema PremiosRed en su arquitectura Odoo-como-Backend.
No contiene código frontal (XML/OWL de Dashboards), solamente amplía el ORM PostgreSQL base para alinear las clases nativas de Odoo con las Interfaces mapeadas en React (TypeScript).

## Estructura de Intercomunicación
- `ResPartner` (res.partner) abarca los roles `UserRole` del `types.ts`.
- `CrmLead` (crm.lead) incluye los rastreadores QR (`scan_count`, `encrypted_id`).

Esta encapsulación permite desarrollar integraciones por API sin que una caída del Dashboard administrativo o de la app en React comprometa los datos relacionales.
