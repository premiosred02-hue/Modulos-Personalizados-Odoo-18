# -*- coding: utf-8 -*-
{
    'name': "REDLMC Tenant Agent",
    'summary': "Agente de telemetría para instancias SaaS",
    'description': """
        Módulo cliente (agente) para instalar en las instancias Odoo de los clientes.
        Se encarga de recopilar métricas de uso y enviarlas a la instancia central
        (REDLMC SaaS Monitor) para su control y facturación.

        Compatible con Odoo 18 Enterprise y Community.
    """,
    'author': "REDLMC SL",
    'website': "https://www.promocionesred.com",
    'category': 'Technical',
    'version': '18.0.1.1.0',  # Enterprise-ready
    'depends': ['base'],
    'data': [
        # 'security/ir.model.access.csv',
        # 'data/ir_cron.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
}

