# -*- coding: utf-8 -*-
{
    'name': 'PromocionesRed · Core Models (Headless DB)',
    'version': '18.0.1.1.0',  # Enterprise-ready
    'summary': 'Extiende los modelos base de Odoo (CRM, Contactos, Productos) para enlazar con el TypeScript de React (types.ts)',
    'author': 'PromocionesRed.com',
    'category': 'Sales',
    'depends': ['base', 'crm', 'sale_management', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_ext_views.xml',
        'views/crm_lead_ext_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
