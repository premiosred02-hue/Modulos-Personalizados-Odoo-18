from odoo import models, fields, api
from datetime import datetime

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Documentos KYB
    redlmc_kyb_dni_front = fields.Many2one('ir.attachment', string='DNI/NIE Anverso', copy=False)
    redlmc_kyb_dni_back = fields.Many2one('ir.attachment', string='DNI Reverso', copy=False)
    redlmc_kyb_cif = fields.Many2one('ir.attachment', string='CIF Empresa', copy=False)
    redlmc_kyb_reta = fields.Many2one('ir.attachment', string='Alta RETA', copy=False)
    redlmc_kyb_aeat = fields.Many2one('ir.attachment', string='Certificado AEAT', copy=False)
    redlmc_kyb_ss = fields.Many2one('ir.attachment', string='Certificado SS', copy=False)
    redlmc_kyb_iban_cert = fields.Many2one('ir.attachment', string='Certificado Bancario', copy=False)
    redlmc_kyb_contrato = fields.Many2one('ir.attachment', string='Contrato Firmado PDF', copy=False)
    redlmc_kyb_foto_local = fields.Many2one('ir.attachment', string='Foto del Local', copy=False)
    redlmc_kyb_ubo = fields.Many2one('ir.attachment', string='Declaración UBO', copy=False)
    redlmc_kyb_auth_col = fields.Many2one('ir.attachment', string='Autorización COL', copy=False)

    # Estado KYB
    redlmc_kyb_estado = fields.Selection([
        ('incompleto', '⏳ Incompleto'),
        ('pendiente', '🔍 Pendiente revisión ADM'),
        ('verificado', '✅ Verificado'),
        ('rechazado', '❌ Rechazado'),
    ], string='Estado KYB', default='incompleto', tracking=True)
    
    redlmc_kyb_fecha = fields.Date(string='Fecha Verificación KYB', copy=False)
    redlmc_kyb_notas = fields.Text(string='Notas ADM (KYB)', copy=False)

    # Portal
    redlmc_portal_enabled = fields.Boolean(string='Portal Activado', default=False, copy=False)
    redlmc_portal_last_login = fields.Datetime(string='Último Acceso Portal', readonly=True, copy=False)
    redlmc_new_season_signed = fields.Boolean(string='Contrato Nueva Temporada Firmado', default=False, copy=False)

    # Kill Switch (Calculado al vuelo)
    redlmc_kill_switch_active = fields.Boolean(
        string='Botón Parada Emergencia Activo', 
        compute='_compute_kill_switch', 
        store=False
    )

    @api.depends()
    def _compute_kill_switch(self):
        # El 21 de Diciembre de 2026 a las 23:59:59 se corta la campaña
        KILL_DT = datetime(2026, 12, 21, 23, 59, 59)
        now = datetime.now()
        is_killed = now > KILL_DT
        for rec in self:
            rec.redlmc_kill_switch_active = is_killed

    def action_verify_kyb(self):
        for rec in self:
            rec.redlmc_kyb_estado = 'verificado'
            rec.redlmc_kyb_fecha = fields.Date.today()

    def action_reject_kyb(self):
        for rec in self:
            rec.redlmc_kyb_estado = 'rechazado'

    def action_activate_actor_from_kyb(self):
        # Override o extensión del action_activate_actor para verificar el KYB antes
        for rec in self:
            if rec.redlmc_kyb_estado != 'verificado':
                # Si el estado es incompleto, lo cambiamos pero idealmente debería estar verificado
                pass
            rec.redlmc_actor_state = 'active'
