from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    pr_role = fields.Selection([
        ('super-admin', 'Super Admin'),
        ('company-admin', 'Company Admin (Empresa)'),
        ('promoter-admin', 'Promoter Admin (Subcamarero)'),
        ('client', 'Cliente Final')
    ], string="PremiosRed Role", default='client', help="Rol principal del ecosistema PremiosRed")
    
    pr_is_promoter = fields.Boolean("Es Promotor Activo", default=False)
    pr_commission_pct = fields.Float("Porcentaje Comisión", default=0.0)
    pr_entity_id = fields.Char("ID Entidad Vinculada", help="Enlace criptográfico entre Empresa y Promotor")
