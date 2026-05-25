from odoo import models, fields

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    pr_encrypted_id = fields.Char(
        string="ID Encriptado (BD Externa)", 
        help="Clave criptográfica única que enlaza con Leads y QRs gestionados desde el Frontend en React."
    )
    pr_scan_count = fields.Integer(
        string="Conteo de Escaneos", 
        default=0,
        help="Veces que el recurso visual asociado (Cartel/QR) ha sido escaneado."
    )
    pr_custom_label = fields.Char(string="Etiqueta Personalizada Frontend")
    pr_portal_type = fields.Selection([
        ('direct', 'Captación Directa'),
        ('qr', 'QR Promocional'),
        ('social', 'Redes Sociales')
    ], string="Fuente del Portal")
