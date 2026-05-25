# -*- coding: utf-8 -*-
from odoo import models, fields, api
import requests
from datetime import datetime

class RedlmcTenantMetrics(models.Model):
    _name = 'redlmc.tenant.metrics'
    _description = 'Metricas de Tenant SaaS'
    _order = 'fecha desc'

    tenant_id = fields.Many2one('res.partner', string='Cliente/Tenant', domain=[('is_saas_client', '=', True)])
    fecha = fields.Datetime(string='Fecha de medición', default=fields.Datetime.now)
    active_users = fields.Integer(string='Usuarios activos 24h')
    invoices_count = fields.Integer(string='Nº Facturas')
    contacts_count = fields.Integer(string='Nº Contactos')
    db_size_mb = fields.Float(string='Tamaño DB (MB)')
    odoo_version = fields.Char(string='Versión Odoo')
    status = fields.Selection([('ok', '🟢 OK'), ('error', '🔴 Error'), ('unreachable', '⚪ Inaccesible')], string="Estado", default='ok')
    raw_response = fields.Text(string='Respuesta cruda JSON')

    @api.model
    def pull_all_tenant_metrics(self):
        tenants = self.env['res.partner'].search([('is_saas_client', '=', True), ('license_status', '=', 'activo')])
        for tenant in tenants:
            self._pull_metrics_from_tenant(tenant)

    def _pull_metrics_from_tenant(self, tenant):
        if not tenant.instance_url:
            self._create_error_metric(tenant, "Sin URL de instancia")
            return
            
        url = f"{tenant.instance_url.rstrip('/')}/redlmc/metrics"
        headers = {'Authorization': f"Bearer {tenant.tenant_id}"}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.create({
                    'tenant_id': tenant.id,
                    'fecha': fields.Datetime.now(),
                    'active_users': data.get('active_users', 0),
                    'invoices_count': data.get('invoices_count', 0),
                    'contacts_count': data.get('contacts_count', 0),
                    'db_size_mb': data.get('db_size_mb', 0.0),
                    'odoo_version': data.get('odoo_version', ''),
                    'status': 'ok',
                    'raw_response': response.text
                })
            else:
                self._create_error_metric(tenant, f"HTTP {response.status_code}")
        except Exception as e:
            self._create_error_metric(tenant, str(e), status='unreachable')

    def _create_error_metric(self, tenant, error_msg, status='error'):
        self.create({
            'tenant_id': tenant.id,
            'fecha': fields.Datetime.now(),
            'status': status,
            'raw_response': error_msg
        })
