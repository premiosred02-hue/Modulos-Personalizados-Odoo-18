# -*- coding: utf-8 -*-
{
    'name': "REDLMC SaaS Monitor Central",
    'summary': "Monitorización central de instancias SaaS",
    'description': """
        Módulo maestro para la instancia de REDLMC SL. Recibe telemetría
        desde los Tenant Agents instalados en clientes, monitorea el estado 
        de salud (uptime) y dispara alertas de licenciamiento.

        Compatible con Odoo 18 Enterprise.
    """,
    'author': "REDLMC SL",
    'website': "https://www.promocionesred.com",
    'category': 'Technical',
    'version': '18.0.1.2.0',  # Enterprise-ready · v1.2: cron activado, dep explícita partner_ext
    'depends': ['base', 'mail', 'redlmc_licencias', 'redlmc_partner_ext'],
    'data': [
        'security/ir.model.access.csv',
        'views/metrics_views.xml',
        'data/ir_cron.xml',           # Cron de telemetría: pull diario de métricas de tenants
    ],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
}

