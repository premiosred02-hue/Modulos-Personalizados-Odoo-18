# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request, Response
import base64

_logger = logging.getLogger(__name__)

class RedlmcApiOnboarding(http.Controller):

    @http.route('/api/v1/onboarding/register', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False, cors='*')
    def register_actor(self, **post):
        """
        Recibe los datos del formulario de Next.js (multipart/form-data)
        Crea un contacto (res.partner) en estado "draft/pending".
        """
        if request.httprequest.method == 'OPTIONS':
            return Response(status=200)

        try:
            # 1. Extraer campos de texto
            actor_type = post.get('actor_type')
            name = post.get('name')
            nif = post.get('nif')
            email = post.get('email')
            phone = post.get('phone')
            iban = post.get('iban')
            
            if not all([actor_type, name, nif, email]):
                return self._json_response({'error': 'Faltan campos obligatorios (actor_type, name, nif, email)'}, 400)

            # Validar que el rol exista
            role = request.env['redlmc.actor.role'].sudo().search([('code', '=', actor_type)], limit=1)
            if not role:
                return self._json_response({'error': f'Rol {actor_type} no válido.'}, 400)

            # Validar duplicados por NIF o Email (opcional, pero buena práctica)
            exist = request.env['res.partner'].sudo().search(['|', ('vat', '=', nif), ('email', '=', email)], limit=1)
            if exist:
                return self._json_response({'error': 'Ya existe un usuario con ese NIF o Email.'}, 409)

            # Generar Código
            from datetime import date
            seq_code = f'premiosred.actor.{actor_type}'
            seq = request.env['ir.sequence'].sudo().next_by_code(seq_code)
            if not seq:
                seq = '000001'
            actor_code = f'{actor_type.upper()}-{date.today().strftime("%Y%m%d")}-{seq}'

            # 2. Crear Partner en Odoo
            vals = {
                'name': name,
                'vat': nif,
                'email': email,
                'phone': phone,
                'redlmc_actor_role_id': role.id,
                'redlmc_actor_code': actor_code,
                'redlmc_actor_state': 'pending', # Requiere validación manual
                'redlmc_kyb_estado': 'pendiente',
                'redlmc_iban': iban,
            }

            partner = request.env['res.partner'].sudo().create(vals)

            # 3. Procesar Archivos (Archivos PDF/JPG adjuntos)
            # Ejemplo: doc_dni, doc_cif
            files_map = {
                'doc_dni': 'DNI_Documento.pdf',
                'doc_cif': 'CIF_Documento.pdf',
                'doc_contract': 'Contrato_Firmado.pdf'
            }

            for file_field, file_name in files_map.items():
                if file_field in request.httprequest.files:
                    file_obj = request.httprequest.files[file_field]
                    file_data = file_obj.read()
                    
                    if file_data:
                        # Crear adjunto
                        attachment = request.env['ir.attachment'].sudo().create({
                            'name': f"{actor_code}_{file_name}",
                            'type': 'binary',
                            'datas': base64.b64encode(file_data),
                            'res_model': 'res.partner',
                            'res_id': partner.id,
                        })
                        
                        # Asignar a campo específico según lógica KYB si es necesario
                        if file_field == 'doc_dni':
                            partner.sudo().write({'redlmc_kyb_dni_front': attachment.id})
                        elif file_field == 'doc_cif':
                            partner.sudo().write({'redlmc_kyb_cif': attachment.id})
                        elif file_field == 'doc_contract':
                            partner.sudo().write({'redlmc_kyb_contrato': attachment.id})

            # Retornar éxito
            return self._json_response({
                'status': 'success',
                'message': 'Registro completado. Pendiente de revisión por administración.',
                'actor_code': actor_code
            }, 201)

        except Exception as e:
            _logger.error("Error en API Onboarding: %s", str(e))
            return self._json_response({'error': str(e)}, 500)

    def _json_response(self, payload, status_code):
        return Response(
            json.dumps(payload),
            status=status_code,
            content_type='application/json'
        )
