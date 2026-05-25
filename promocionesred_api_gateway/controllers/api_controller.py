import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class PremiosRedApiGateway(http.Controller):
    
    def _check_api_key(self):
        """Validador simple Headless para proteger la API REST sin sesión de Odoo."""
        auth_header = request.httprequest.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '')
        
        # Recupera la llave validada alojada en Preferencias / Config Parameters
        master_token = request.env['ir.config_parameter'].sudo().get_param('premiosred.api_master_key')
        
        if not master_token:
            _logger.error("No se ha configurado 'premiosred.api_master_key' en Odoo")
            return False
            
        return token == master_token

    def _http_response(self, data, status_code=200):
        # Permite conexiones CORS desde el React Front-end
        headers = [
            ('Content-Type', 'application/json'),
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'POST, GET, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        ]
        return request.make_response(json.dumps(data), headers=headers, status=status_code)

    @http.route('/api/v1/leads', type='http', auth='none', methods=['POST', 'OPTIONS'], csrf=False)
    def web_create_lead(self, **kwargs):
        """Endpoint expuesto: Atrapa envíos de formularios del React Frontend."""
        
        # CORS Preflight check
        if request.httprequest.method == 'OPTIONS':
            return self._http_response({})

        # Seguridad
        if not self._check_api_key():
            return self._http_response({'status': 'error', 'message': 'Unauthorized (Bearer Token invalido)'}, 401)
            
        try:
            payload = json.loads(request.httprequest.data)
            
            # Garantizar Odoo Multi-Empresa: Determinar el tenant (empresa) operativo desde el payload
            tenant_prefix = payload.get('tenant_slug', 'REDROYAL') # Ej: REDROYAL, PROMOSMEX
            Company = request.env['res.company'].with_user(1)
            target_company = Company.search([('name', 'ilike', tenant_prefix)], limit=1)
            company_id = target_company.id if target_company else Company.search([], limit=1).id

            # Map de JSON a columnas Odoo (Core Models)
            lead_vals = {
                'name': payload.get('name', 'Lead desde Web'),
                'email_from': payload.get('email', ''),
                'phone': payload.get('phone', ''),
                'description': payload.get('notes', ''),
                'company_id': company_id,
                'user_id': False,
                # Campos extendidos desde types.ts a través de core_models
                'pr_encrypted_id': payload.get('encrypted_id', ''),
                'pr_portal_type': payload.get('portal_type', 'direct')
            }
            
            # Inserción con SU (SuperUser) dado que auth='none' rompe seguridad estricta
            new_lead = request.env['crm.lead'].with_user(1).with_company(company_id).create(lead_vals)
            
            return self._http_response({
                'status': 'success', 
                'odoo_id': new_lead.id,
                'message': 'Lead ingresado a Odoo correctamente.'
            })
            
        except Exception as e:
            _logger.exception("Error procesando lead vía webhook API:")
            return self._http_response({'status': 'error', 'message': str(e)}, 500)

    @http.route('/api/v1/payments/webhook', type='http', auth='none', methods=['POST', 'OPTIONS'], csrf=False)
    def web_process_payment(self, **kwargs):
        """Endpoint expuesto: Recibe eventos de pago confirmados (Checkout) desde la pasarela externa."""
        
        # CORS Preflight
        if request.httprequest.method == 'OPTIONS':
            return self._http_response({})

        # Seguridad Base
        if not self._check_api_key():
            return self._http_response({'status': 'error', 'message': 'Unauthorized'}, 401)
            
        try:
            payload = json.loads(request.httprequest.data)
            
            # Destructurar Payload según interfaz de 'types.ts' Payment
            provider = payload.get('provider', 'Stripe')
            reference = payload.get('provider_reference', 'N/A')
            amount = float(payload.get('amount', 0.0))
            email = payload.get('user_email')
            
            # Garantizar Odoo Multi-Empresa: Determinar el tenant (empresa) operativo desde el payload
            tenant_prefix = payload.get('tenant_slug', 'REDROYAL') # Ej: REDROYAL, PROMOSMEX
            Company = request.env['res.company'].with_user(1)
            target_company = Company.search([('name', 'ilike', tenant_prefix)], limit=1)
            company_id = target_company.id if target_company else Company.search([], limit=1).id

            # 1. Buscar a la empresa (partner)
            Partner = request.env['res.partner'].with_user(1).with_company(company_id)
            partner = Partner.search([('email', '=', email), ('company_id', 'in', [False, company_id])], limit=1)
            
            if not partner:
                # Si pagó pero no existe en Odoo aún, creamos el "Shell" del Partner (Company o Client)
                partner = Partner.create({
                    'name': payload.get('user_name', f'Membresía Activa {email}'),
                    'email': email,
                    'pr_role': 'client', # Mejor dejarlo genérico si es compra web
                    'company_id': company_id
                })
                
            # 1.1. CIERRE DE BUCLE: Recuperar el "Lead" del Paso 1 y marcarlo como ganado.
            Lead = request.env['crm.lead'].with_user(1).with_company(company_id)
            abandoned_lead = Lead.search([('email_from', '=', email), ('company_id', '=', company_id)], limit=1)
            if abandoned_lead:
                abandoned_lead.write({
                    'partner_id': partner.id,
                    'description': abandoned_lead.description + f'\n\n[SISTEMA]: El usuario recuperó el carrito y completó el pago ({reference}).' if abandoned_lead.description else f'El usuario completó el pago ({reference}).'
                })
                try:
                    abandoned_lead.action_set_won() # Lo marcamos como "Venta Ganada" en el embudo
                except Exception:
                    pass # Evita fallos si el CRM no está configurado igual
                    
            # 2. Generar el registro contable nativo (Factura de Venta / account.move)
            Move = request.env['account.move'].with_user(1).with_company(company_id)
            invoice = Move.create({
                'move_type': 'out_invoice',
                'partner_id': partner.id,
                'ref': f"Pago Web Ext: {provider} - {reference}",
                'company_id': company_id,
                'invoice_line_ids': [(0, 0, {
                    'name': payload.get('pack_name', 'Pack Digital / Membresía PremiosRed'),
                    'quantity': 1,
                    'price_unit': amount,
                })]
            })
            
            # 3. Asentar la factura automáticamente si viaja con bandera Paid
            if payload.get('status') == 'paid':
                invoice.action_post()
            
            _logger.info(f"💰 PAGO EXTERNO PROCESADO: {reference} por {amount} EUR. Factura: {invoice.id}")
            
            return self._http_response({
                'status': 'success', 
                'invoice_id': invoice.id,
                'invoice_name': invoice.name,
                'message': 'Transacción contable guardada y automatizada en Odoo.'
            })
            
        except Exception as e:
            _logger.exception("Error procesando Webhook de Pagos Web:")
            return self._http_response({'status': 'error', 'message': str(e)}, 500)

    @http.route('/api/v1/carteles', type='http', auth='none', methods=['GET', 'OPTIONS'], csrf=False)
    def web_get_carteles(self, **kwargs):
        """Endpoint expuesto: Permite a la Web Externa (React) descargar los carteles diseñados en Odoo."""
        
        if request.httprequest.method == 'OPTIONS':
            return self._http_response({})

        if not self._check_api_key():
            return self._http_response({'status': 'error', 'message': 'Unauthorized'}, 401)
            
        try:
            # Buscar carteles que el administrador haya marcado como 'Listos para imprimir'
            Cartel = request.env['cc.cartel.design'].sudo()
            designs = Cartel.search([('state', '=', 'ready')])
            
            payload = []
            for d in designs:
                payload.append({
                    'id': d.id,
                    'name': d.name,
                    'active_format': d.active_format,
                    # Devolver el JSON ensamblado para que React lo parsee nativamente
                    'design_state': json.loads(d.design_json) if d.design_json else {},
                    'updated_at': d.write_date.isoformat()
                })
                
            return self._http_response({'status': 'success', 'data': payload})
            
        except Exception as e:
            _logger.exception("Error obteniendo carteles desde API:")
            return self._http_response({'status': 'error', 'message': str(e)}, 500)
