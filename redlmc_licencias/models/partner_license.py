# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResPartnerLicense(models.Model):
    _inherit = 'res.partner'

    # Datos de la Licencia SaaS
    is_saas_client = fields.Boolean(string="Es Cliente SaaS", default=False)
    tenant_id = fields.Char(string="Tenant ID", help="Ejemplo: TENANT-001")
    license_type = fields.Selection([
        ('saas_dedicada', 'SaaS Dedicada'),
        ('white_label', 'White Label'),
        ('intragrupo', 'Intragrupo'),
    ], string="Tipo de Licencia", default='saas_dedicada')
    instance_url = fields.Char(string="URL de Instancia", help="Ejemplo: erp.cliente.com")
    instance_port = fields.Integer(string="Puerto Asignado", help="Ejemplo: 8001")
    license_start_date = fields.Date(string="Fecha Inicio")
    license_renewal_date = fields.Date(string="Próxima Renovación")
    license_status = fields.Selection([
        ('activo', '🟢 Activo'),
        ('suspendido', '🟡 Suspendido'),
        ('cancelado', '🔴 Cancelado'),
    ], string="Estado de Licencia", default='activo', tracking=True)

    @api.onchange('license_status')
    def _onchange_license_status(self):
        # Aquí se podrían añadir automatizaciones si el estado cambia (ej. Tags)
        pass
