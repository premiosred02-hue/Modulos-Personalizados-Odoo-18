# -*- coding: utf-8 -*-
{
    'name': 'REDLMC — Partners: Licencias SaaS y Sub-colaboradores',
    'version': '18.0.1.4.0',  # Enterprise-ready
    'summary': (
        'Gestión completa del grupo REDLMC/PremiosRed en Odoo: '
        '5 roles de actor (COL/SUB/CCP/COM/ASE), exclusión automática del sorteo, '
        'zona geográfica + URL QR, comisiones AML, Licencias SaaS con pestaña '
        'en formulario de empresa (equivalente a Ramas) y Sub-colaboradores COL→SUB.'
    ),
    'description': """
        Extiende res.partner con dos secciones propias del modelo
        de negocio REDLMC SL / PremiosRed:

        1. LICENCIAS SAAS
           - Activar/desactivar condición de cliente con licencia
           - Tipo de licencia, código de tenant, vigencia, cuota mensual
           - Generación de API Key segura (token_urlsafe 40 chars)
           - Estado: Borrador / Activa / Suspendida / Expirada

        2. SUB-COLABORADORES (solo visible si el contacto es Empresa)
           - Marcar al partner como COL (punto de venta)
           - Lista editable de SUBs vinculados con NIF, IBAN,
             tipo fiscal, % comisión y estado
           - Base para el Modelo 111 (retenciones IRPF autónomos)

        Ref. modelo negocio: SKILL-GRUPO-EMPRESARIAL.md §3
        Split comisiones: 45% pool actores — SUB recibe 25% de ese pool

        NOTA Enterprise v18:
        - Compatible con web_enterprise (vistas mejoradas de contactos)
        - Compatible con contacts_enterprise si está instalado
    """,
    'author': 'REDLMC SL',
    'website': 'https://redlmc.com',
    'category': 'Customizations',
    'license': 'LGPL-3',
    'depends': ['base', 'contacts', 'mail', 'redlmc_es_labels'],
    'data': [
        'security/ir.model.access.csv',
        'data/redlmc_roles_data.xml',
        'views/res_partner_views.xml',
        'views/res_company_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}

