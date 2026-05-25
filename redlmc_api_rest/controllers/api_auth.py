# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)

class RedlmcApiAuth(http.Controller):

    def _get_bearer_token(self):
        """Extracts Bearer token from the Authorization header."""
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        return auth_header.split(' ')[1]

    def _verify_actor_token(self):
        """Validates token and returns the partner record or raises an error."""
        token = self._get_bearer_token()
        if not token:
            return None, {'error': 'Missing or invalid Authorization header'}
        
        partner = request.env['res.partner'].sudo().search([
            ('redlmc_api_key', '=', token),
            ('active', '=', True)
        ], limit=1)

        if not partner:
            return None, {'error': 'Invalid Token'}

        if partner.redlmc_actor_status not in ['active', 'draft', 'pending']:
            return None, {'error': f'Actor account is not active. Current state: {partner.redlmc_actor_status}'}

        return partner, None

    @http.route('/api/v1/auth/me', type='http', auth='public', methods=['GET', 'OPTIONS'], csrf=False, cors='*')
    def get_me(self, **kwargs):
        """
        Endpoint for the Next.js portal to verify if a token is valid
        and get the actor's profile information.
        """
        if request.httprequest.method == 'OPTIONS':
            return Response(status=200)

        partner, error = self._verify_actor_token()
        
        if error:
            return Response(
                json.dumps(error),
                status=401,
                content_type='application/json'
            )

        # Build response payload
        data = {
            'id': partner.id,
            'name': partner.name,
            'email': partner.email,
            'actor_code': partner.redlmc_actor_code,
            'role_code': partner.redlmc_actor_role_id.code if partner.redlmc_actor_role_id else None,
            'role_name': partner.redlmc_actor_role_id.name if partner.redlmc_actor_role_id else None,
            'status': partner.redlmc_actor_status,
            'kyb_status': partner.redlmc_kyb_estado,
        }

        return Response(
            json.dumps({'status': 'success', 'data': data}),
            status=200,
            content_type='application/json'
        )

    @http.route('/api/v1/auth/login', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False, cors='*')
    def api_login(self, **kwargs):
        """
        Endpoint to authenticate users via username and password.
        Validates against redlmc_portal_username and redlmc_portal_password.
        """
        if request.httprequest.method == 'OPTIONS':
            return Response(status=200)

        try:
            body = json.loads(request.httprequest.data)
        except Exception:
            body = {}

        username = body.get('username')
        password = body.get('password')
        
        if not username or not password:
            return Response(json.dumps({'error': 'Usuario y clave son requeridos'}), status=400, content_type='application/json')

        # Buscar el partner con ese usuario y contraseña
        partner = request.env['res.partner'].sudo().search([
            ('redlmc_portal_username', '=', username),
            ('redlmc_portal_password', '=', password),
            ('active', '=', True)
        ], limit=1)

        if not partner:
            return Response(json.dumps({'error': 'Credenciales incorrectas o usuario no encontrado.'}), status=401, content_type='application/json')

        if partner.redlmc_actor_status not in ['active', 'draft', 'pending']:
            return Response(json.dumps({'error': f'Cuenta no activa. Estado actual: {partner.redlmc_actor_status}'}), status=403, content_type='application/json')

        # Generar API Key si no tiene una
        if not partner.redlmc_api_key:
            partner.action_generate_api_key()

        # Devolver el token (API Key) para que el frontend inicie sesión
        return Response(json.dumps({
            'status': 'success',
            'token': partner.redlmc_api_key,
            'message': 'Autenticación exitosa'
        }), status=200, content_type='application/json')
