# -*- coding: utf-8 -*-
"""
Modelo: pr.email.log
Equivalente a las tablas 'email_logs' y 'email_templates' de Supabase.
"""
from odoo import models, fields, api


class PrEmailLog(models.Model):
    _name = 'pr.email.log'
    _description = 'PromocionesRed.com Email Log'
    _order = 'sent_at desc'

    lead_id = fields.Many2one('pr.lead', string='Lead', ondelete='set null')
    recipient = fields.Char(string='Email Destinatario')
    name = fields.Char(string='Nombre Destinatario')
    category = fields.Char(string='Categoría')
    subject = fields.Char(string='Asunto')
    body = fields.Text(string='Cuerpo del Mensaje')
    sent_at = fields.Datetime(string='Enviado el', default=fields.Datetime.now)
    views = fields.Integer(string='Aperturas', default=0)
    clicks = fields.Integer(string='Clics', default=0)
    country = fields.Char(string='País de Apertura')
    last_action = fields.Char(string='Última Acción')


class PrEmailTemplate(models.Model):
    _name = 'pr.email.template'
    _description = 'PromocionesRed.com Email Template'
    _order = 'name asc'

    name = fields.Char(string='Nombre (Uso Interno)', required=True)
    subject = fields.Char(string='Asunto del Correo', required=True)
    body = fields.Text(string='Cuerpo del Mensaje', required=True)
