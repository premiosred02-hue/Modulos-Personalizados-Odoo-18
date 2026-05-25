# -*- coding: utf-8 -*-
from odoo import api, models, SUPERUSER_ID


def _post_init_hook(env):
    """
    Hook que se ejecuta tras la instalación/actualización del módulo.
    Actualiza directamente los registros ir_model_fields_selection
    para cambiar las etiquetas 'Individual'/'Company' por los términos
    legales españoles 'Persona Física'/'Empresa'.
    """
    # Buscar las opciones del campo company_type en res.partner
    Selection = env['ir.model.fields.selection']

    # Cambiar 'Individual' / 'Individuo' → 'Persona Física'
    person_sel = Selection.search([
        ('field_id.model', '=', 'res.partner'),
        ('field_id.name', '=', 'company_type'),
        ('value', '=', 'person'),
    ])
    if person_sel:
        person_sel.with_context(lang='es_ES').write({'name': 'Persona Física'})
        person_sel.write({'name': 'Persona Física'})

    # Cambiar 'Company' / 'Compañía' → 'Empresa'
    company_sel = Selection.search([
        ('field_id.model', '=', 'res.partner'),
        ('field_id.name', '=', 'company_type'),
        ('value', '=', 'company'),
    ])
    if company_sel:
        company_sel.with_context(lang='es_ES').write({'name': 'Empresa'})
        company_sel.write({'name': 'Empresa'})
