# PromocionesRed API Gateway (Web / React Connector)

Este submódulo expone la base de datos de Odoo a las aplicaciones externas escritas en React (Stripe Checkout UI, Website público de landing pages).

## Seguridad
- Auth Type: `none` y `public` (Bypassea cookies y sesiones lentas de Odoo).
- Token Validation: Obliga cabecera `Authorization: Bearer <TOKEN>`.
- Token se configura Odoo en: Ajustes -> Parámetros del Sistema -> `premiosred.api_master_key`.

## Endpoints Documentados
- `POST /api/v1/leads`: Recibe cargas útiles estandarizadas (JSON) heredadas de `LeadRecord` (`types.ts`) e inyecta sincrónicamente un lead en Odoo. Implementa CORS puro para funcionar sin proxy intermedio.
- `POST /api/v1/payments/webhook`: Recibe confirmaciones sólidas de pagos desde tu back-end web Node/React (cruzando pasarelas tipo Stripe/Redsys). Inyecta la contabilidad de manera nativa cruzando el valor de la interface `Payment` para generar el registro impositivo y factura de ingreso en Odoo de manera Zero-Touch.
