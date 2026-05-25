# -*- coding: utf-8 -*-
{
    'name': 'PromocionesRed · API Gateway',
    'version': '18.0.1.1.0',  # Enterprise-ready
    'summary': 'API REST (Headless) para conectar Odoo con la Pasarela de Pago React y Web Externa.',
    'author': 'PromocionesRed.com',
    'category': 'Tools',
    'depends': ['base', 'promocionesred_core_models'],
    'data': [
        'security/api_security.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

