# -*- coding: utf-8 -*-
{
    'name': "REDLMC Licencias y Royalties",
    'summary': "Gestión de licencias SaaS y facturación de royalties",
    'description': """
        Módulo propio de REDLMC SL para la gestión automatizada de 
        licencias de software, control de clientes SaaS y 
        cálculo de royalties recurrentes.

        Compatible con Odoo 18 Enterprise.
    """,
    'author': "REDLMC SL",
    'website': "https://www.promocionesred.com",
    'category': 'Sales/Sales',
    'version': '18.0.1.2.0',
    'depends': ['base', 'sale_management', 'account', 'redlmc_partner_ext'],
    'data': [
        'security/ir.model.access.csv',
        'views/partner_views.xml',
        'views/menus.xml',
        'data/product_data.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
}
