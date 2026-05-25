# -*- coding: utf-8 -*-
# ── PREMIOSRED — Modelo pr.pack (Catálogo de packs) ──────────────────────
# Pack único activo 2026: PTK (Pack General 6€)
# Vault: 40.01 PACKS-Y-PREMIOS
from odoo import models, fields, api


PACK_STATUS = [
    ('active',   'Activo'),
    ('inactive', 'Inactivo'),
    ('future',   'Campaña futura'),
]


class PrPack(models.Model):
    _name = 'pr.pack'
    _description = 'Pack PremiosRed (catálogo de productos)'
    _order = 'pack_status asc, price asc'
    _rec_name = 'name'

    # ── Identificación ──────────────────────────────────────────────────────
    name         = fields.Char('Nombre del pack', required=True)   # 'PTK Pack General'
    code         = fields.Char('Código', required=True)            # 'PTK'
    description  = fields.Text('Descripción')
    pack_status  = fields.Selection(PACK_STATUS, 'Estado', default='active', required=True)

    # ── Precios y distribución ───────────────────────────────────────────────
    price        = fields.Float('PVP (€)', digits=(10, 2), required=True)
    donation_pct = fields.Float('% Donación solidaria', digits=(5, 2), default=2.0)
    # Donación por unidad = price * donation_pct / 100
    donation_per_unit = fields.Float(
        'Donación por unidad (€)',
        compute='_compute_donation',
        store=True,
        digits=(10, 4)
    )

    # ── Campaña ─────────────────────────────────────────────────────────────
    campaign_year = fields.Integer('Año campaña', default=lambda self: fields.Date.today().year)
    launch_date   = fields.Date('Fecha de lanzamiento')
    end_date      = fields.Date('Fecha de fin')

    # ── Sorteo vinculado ─────────────────────────────────────────────────────
    sorteo_ref    = fields.Char('Referencia del sorteo')

    # ── KPIs computed ───────────────────────────────────────────────────────
    total_sold = fields.Integer(
        'Unidades vendidas',
        compute='_compute_stats',
        store=False
    )
    total_revenue = fields.Float(
        'Ingresos totales (€)',
        compute='_compute_stats',
        store=False,
        digits=(12, 2)
    )
    total_donations = fields.Float(
        'Total donaciones (€)',
        compute='_compute_stats',
        store=False,
        digits=(12, 2)
    )

    @api.depends('price', 'donation_pct')
    def _compute_donation(self):
        for r in self:
            r.donation_per_unit = r.price * (r.donation_pct / 100.0)

    @api.depends('cupon_ids')
    def _compute_stats(self):
        for r in self:
            cupones = r.cupon_ids
            sold = len(cupones.filtered(lambda c: c.status in ('used', 'available')))
            r.total_sold = sold
            r.total_revenue = sold * r.price
            r.total_donations = sold * r.donation_per_unit

    cupon_ids = fields.One2many('pr.cupon', 'pack_id', 'Cupones emitidos')

    @api.model
    def get_packs_data(self):
        """Devuelve catálogo de packs para PacksView. Llamado desde JS."""
        packs = self.search([])
        result = []
        for p in packs:
            result.append({
                'id': p.id,
                'name': p.name,
                'code': p.code,
                'price': p.price,
                'donation_pct': p.donation_pct,
                'donation_per_unit': p.donation_per_unit,
                'pack_status': p.pack_status,
                'campaign_year': p.campaign_year,
                'launch_date': p.launch_date.isoformat() if p.launch_date else '',
                'sorteo_ref': p.sorteo_ref or '',
                'total_sold': p.total_sold,
                'total_revenue': p.total_revenue,
                'total_donations': p.total_donations,
            })
        return result
