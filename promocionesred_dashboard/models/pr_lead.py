# -*- coding: utf-8 -*-
"""
Modelo: pr.lead
Equivalente a la tabla 'leads' de Supabase.
Gestiona el pipeline de contactos: Empresas (SPP/PAT/AYT), Colaboradores (COL/CCP), Personas (SUB/CLI/EMP).
"""
from odoo import models, fields, api


class PrLead(models.Model):
    _name = 'pr.lead'
    _description = 'PromocionesRed.com Lead'
    _order = 'create_date desc'

    # ── Identidad ────────────────────────────────────────────────
    name = fields.Char(string='Nombre Comercial', required=True)
    legal_name = fields.Char(string='Razón Social')
    tax_id = fields.Char(string='CIF / NIF')

    # ── Tipo / Categoría ─────────────────────────────────────────
    lead_type = fields.Selection([
        ('SPP', 'Empresa - Main Sponsor (SPP)'),
        ('PAT', 'Empresa - Product Sponsor (PAT)'),
        ('AYT', 'Empresa - Town Hall B2G (AYT)'),
        ('COL', 'Colaborador (COL)'),
        ('CCP', 'Colaborador - Central Partner (CCP)'),
        ('SUB', 'Persona - Sub-Colaborador (SUB)'),
        ('CLI', 'Persona - Cliente Individual (CLI)'),
        ('EMP', 'Persona - Empleado (EMP)'),
    ], string='Tipo', default='SPP', required=True)

    # ── Pack Comercial (solo Empresas) ───────────────────────────
    pack = fields.Selection([
        ('N/A', 'N/A'),
        ('4.1 Apple', '4.1 Technology (Apple)'),
        ('4.2 Moda', '4.2 Fashion (Zara)'),
        ('4.4 RIU', '4.4 Travel (RIU)'),
    ], string='Pack Contratado', default='N/A')
    pack_price = fields.Float(string='Valor Contrato (€)', default=0.0)
    corporate_url = fields.Char(string='URL Corporativa')

    # ── Comisiones (solo Colaboradores) ─────────────────────────
    base_commission_pct = fields.Float(string='% Comisión Base', default=30.0)
    override_commission_pct = fields.Float(string='% Override (COL)', default=15.0)

    # ── Ubicación ────────────────────────────────────────────────
    address = fields.Char(string='Dirección')
    zip_code = fields.Char(string='Código Postal')
    city = fields.Char(string='Ciudad')
    province = fields.Char(string='Provincia')
    autonomy = fields.Char(string='Comunidad Autónoma')

    # ── Contacto ─────────────────────────────────────────────────
    email = fields.Char(string='Email')
    phone = fields.Char(string='Teléfono')

    # ── Estado ───────────────────────────────────────────────────
    status = fields.Selection([
        ('Enviado', 'Enviado'),
        ('En Negociación', 'En Negociación'),
        ('Contratado', 'Contratado'),
        ('cerrado', 'Cerrado'),
    ], string='Estado', default='Enviado', required=True)

    # ── Trazabilidad ─────────────────────────────────────────────
    created_by_actor = fields.Many2one('pr.network', string='Actor Origen (Red)')
    observation = fields.Text(string='Observaciones')

    # ── Campos calculados ────────────────────────────────────────
    type_label = fields.Char(string='Categoría (Label)', compute='_compute_type_label', store=False)

    @api.depends('lead_type')
    def _compute_type_label(self):
        mapping = {
            'SPP': 'Empresas (Sponsors)', 'PAT': 'Empresas (Sponsors)', 'AYT': 'Empresas (Sponsors)',
            'COL': 'Colaboradores (COL)', 'CCP': 'Colaboradores (COL)',
            'SUB': 'Empleados o Clientes', 'CLI': 'Empleados o Clientes', 'EMP': 'Empleados o Clientes',
        }
        for rec in self:
            rec.type_label = mapping.get(rec.lead_type, rec.lead_type)

    @api.model
    def get_dashboard_stats(self):
        """Método llamable desde JS para obtener KPIs del dashboard."""
        leads = self.search([])
        contratados = leads.filtered(lambda l: l.status == 'Contratado')
        total_revenue = sum(contratados.mapped('pack_price'))
        return {
            'total_leads': len(leads),
            'conversion_rate': round((len(contratados) / len(leads) * 100), 1) if leads else 0,
            'active_sponsors': len(contratados),
            'guarantee_fund': round(total_revenue * 0.10, 2),
            'total_revenue': total_revenue,
            'matrix_profit': round(total_revenue * 0.55, 2),
            'network_payout': round(total_revenue * 0.45, 2),
        }
