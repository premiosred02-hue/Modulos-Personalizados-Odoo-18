# -*- coding: utf-8 -*-
{
    'name': 'REDLMC - Gestión de Suplidos',
    'version': '18.0.1.1.0',  # Enterprise-ready (corregido formato de versión)
    'category': 'Accounting/Localizations',
    'summary': 'Añade la gestión visual de Suplidos en las facturas y separa la Base Imponible Real.',
    'description': """
        Este módulo permite marcar líneas de factura como 'Suplidos' para que 
        se calculen y visualicen por separado de la Base Imponible general en la factura.
        Ideal para Notarías, Gestorías y despachos en España.

        Compatible con Odoo 18 Enterprise (account nativo).
    """,
    'author': 'Antigravity / REDLMC',
    'depends': ['account'],
    'data': [
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

