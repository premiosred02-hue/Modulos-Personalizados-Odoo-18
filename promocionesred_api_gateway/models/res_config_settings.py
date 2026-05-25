from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pr_api_master_key = fields.Char(
        string='Master API Key (React to Odoo)',
        config_parameter='premiosred.api_master_key',
        help="Introduce el token se seguridad estático que el Frontend en React utilizará en su header de autorización (Bearer Token)."
    )
