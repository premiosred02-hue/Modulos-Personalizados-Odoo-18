# -*- coding: utf-8 -*-
"""
Modelo: pr.network
Equivalente a la tabla 'network' de Supabase.
Gestiona la jerarquía de actores COL / CCP / SUB.
"""
from odoo import models, fields, api


class PrNetwork(models.Model):
    _name = 'pr.network'
    _description = 'PromocionesRed.com Network Actor'
    _order = 'name asc'

    name = fields.Char(string='Nombre del Actor', required=True)
    role = fields.Selection([
        ('2 COL', '2 COL - Colaborador'),
        ('2.2 CCP', '2.2 CCP - Central Partner'),
        ('2.6 SUB', '2.6 SUB - Sub-Colaborador'),
    ], string='Rol en la Red', default='2.6 SUB', required=True)

    parent_id = fields.Many2one('pr.network', string='Superior (Manager)', ondelete='set null')
    child_ids = fields.One2many('pr.network', 'parent_id', string='Sub-Colaboradores')

    status = fields.Selection([
        ('Active', 'Activo'),
        ('Pending', 'Pendiente de Auditoría'),
        ('Inactive', 'Inactivo'),
    ], string='Estado', default='Active')

    base_commission_pct = fields.Float(string='% Comisión Base', default=30.0)
    override_commission_pct = fields.Float(string='% Override', default=15.0)

    leads_count = fields.Integer(string='Leads Asignados', compute='_compute_leads_count')

    @api.depends()
    def _compute_leads_count(self):
        for rec in self:
            rec.leads_count = self.env['pr.lead'].search_count([('created_by_actor', '=', rec.id)])

    @api.model
    def get_network_json(self):
        """Devuelve la red completa como lista de dicts para el frontend JS."""
        records = self.search([])
        return [{
            'id': r.id,
            'name': r.name,
            'role': r.role,
            'parent_id': r.parent_id.id if r.parent_id else None,
            'status': r.status,
            'base_commission_pct': r.base_commission_pct,
            'override_commission_pct': r.override_commission_pct,
        } for r in records]
