# -*- coding: utf-8 -*-
from odoo import api, fields, models
import secrets

class RedlmcStore(models.Model):
    """
    Representa una tienda o sucursal física de un Colaborador (COL).
    Un COL puede tener varias tiendas, cada una con su propio personal (SUBs)
    y sus propios carteles QR físicos instalados.
    """
    _name = 'redlmc.store'
    _description = 'Tienda o Sucursal física del COL'
    _order = 'name'

    name = fields.Char(string='Nombre de la Tienda', required=True, help="Ej: Kiosko Centro, Papelería Norte")
    col_id = fields.Many2one(
        'res.partner', 
        string='Empresa Colaboradora (COL)', 
        required=True, 
        domain="[('is_company', '=', True), ('redlmc_is_col', '=', True)]",
        ondelete='cascade'
    )
    
    # Dirección
    street = fields.Char(string='Calle')
    city = fields.Char(string='Ciudad')
    zip = fields.Char(string='Código Postal', size=5)
    
    # Relaciones
    sub_ids = fields.One2many('redlmc.col.sub', 'store_id', string='Personal (SUBs)')
    cartel_ids = fields.One2many('redlmc.qr.cartel', 'store_id', string='Carteles QR')

    # Estadísticas básicas
    cartel_count = fields.Integer(string='Nº de Carteles', compute='_compute_counts')
    sub_count = fields.Integer(string='Nº de Empleados (SUB)', compute='_compute_counts')

    @api.depends('cartel_ids', 'sub_ids')
    def _compute_counts(self):
        for record in self:
            record.cartel_count = len(record.cartel_ids)
            record.sub_count = len(record.sub_ids)


class RedlmcQrCartel(models.Model):
    """
    Representa un Cartel QR físico impreso y colocado en una Tienda.
    Permite trazar exactamente de qué cartel de qué tienda viene el escaneo.
    """
    _name = 'redlmc.qr.cartel'
    _description = 'Cartel QR Físico en Tienda'
    _order = 'name'

    name = fields.Char(string='Ubicación del Cartel', required=True, help="Ej: Escaparate principal, Mostrador caja")
    store_id = fields.Many2one('redlmc.store', string='Tienda (Sucursal)', required=True, ondelete='cascade')
    col_id = fields.Many2one('res.partner', string='COL', related='store_id.col_id', store=True)
    
    qr_code_uid = fields.Char(string='UID del QR', required=True, copy=False, readonly=True, default=lambda self: self._generate_uid())
    qr_url = fields.Char(string='URL del Cartel', compute='_compute_qr_url', store=True)
    
    active = fields.Boolean(default=True, string='Activo')

    @api.model
    def _generate_uid(self):
        # Genera un identificador único corto para el QR (ej: QR-8A3B2F)
        return f"QR-{secrets.token_hex(3).upper()}"

    @api.depends('qr_code_uid')
    def _compute_qr_url(self):
        for rec in self:
            if rec.qr_code_uid:
                rec.qr_url = f"https://premiosred.com/qr/{rec.qr_code_uid}"
            else:
                rec.qr_url = False
