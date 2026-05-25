# -*- coding: utf-8 -*-
import json
from datetime import datetime
from odoo import http, release, fields
from odoo.http import request, Response

class RedlmcMetricsController(http.Controller):

    def _validate_token(self, token):
        # En MVP, podríamos tener un token fijo en ir.config_parameter
        # Para el agente, el token que autoriza las llamadas entrantes
        expected_token = request.env['ir.config_parameter'].sudo().get_param('redlmc_tenant.token', 'DEV-TOKEN')
        return token == expected_token

    def _get_tenant_id(self):
        return request.env['ir.config_parameter'].sudo().get_param('redlmc_tenant.id', 'UNKNOWN-TENANT')

    def _count_active_users_24h(self):
        # Cuenta de sesiones recientes (simplificado)
        return request.env['res.users'].sudo().search_count([('log_ids.create_date', '>=', fields.Datetime.now())]) # aproximado
        
    def _count_invoices(self):
        return request.env['account.move'].sudo().search_count([('move_type', 'in', ['out_invoice', 'in_invoice'])])

    def _count_contacts(self):
        return request.env['res.partner'].sudo().search_count([('active', '=', True)])

    def _get_db_size(self):
        # Requeriría queries crudas, devolveremos 0 por seguridad en MVP
        request.env.cr.execute("SELECT pg_database_size(current_database())")
        size_bytes = request.env.cr.fetchone()[0]
        return round(size_bytes / (1024 * 1024), 2) if size_bytes else 0.0

    @http.route('/redlmc/metrics', auth='none', methods=['GET'], csrf=False)
    def get_metrics(self, **kwargs):
        token = request.httprequest.headers.get('Authorization', '').replace('Bearer ', '')
        if not self._validate_token(token):
            return Response('Unauthorized', status=401)

        metrics = {
            'tenant_id': self._get_tenant_id(),
            'timestamp': datetime.now().isoformat(),
            'invoices_count': self._count_invoices(),
            'contacts_count': self._count_contacts(),
            'odoo_version': release.version,
            'db_size_mb': self._get_db_size(),
            'status': 'ok'
        }
        return Response(json.dumps(metrics), content_type='application/json')
