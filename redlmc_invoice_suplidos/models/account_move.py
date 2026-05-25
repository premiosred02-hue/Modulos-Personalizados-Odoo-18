from odoo import api, fields, models

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_suplido = fields.Boolean(
        string='Es Suplido', 
        default=False, 
        help="Marcar si esta línea es un suplido (gastos pagados por cuenta del cliente). No forma parte de la base imponible fiscal."
    )

class AccountMove(models.Model):
    _inherit = 'account.move'

    amount_suplidos = fields.Monetary(
        string='Total Suplidos', 
        compute='_compute_suplidos_redlmc', 
        store=True
    )
    amount_base_real = fields.Monetary(
        string='Base Imponible Real', 
        compute='_compute_suplidos_redlmc', 
        store=True,
        help="Importe Base estándar menos los Suplidos."
    )

    @api.depends('invoice_line_ids.price_subtotal', 'invoice_line_ids.is_suplido', 'amount_untaxed')
    def _compute_suplidos_redlmc(self):
        for move in self:
            suplidos = sum(line.price_subtotal for line in move.invoice_line_ids if line.is_suplido)
            move.amount_suplidos = suplidos
            move.amount_base_real = move.amount_untaxed - suplidos
