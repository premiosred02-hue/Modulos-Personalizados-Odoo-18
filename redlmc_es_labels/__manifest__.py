# -*- coding: utf-8 -*-
{
    'name': 'REDLMC — Etiquetas España + Branding Login',
    'version': '18.0.1.4.0',
    'summary': 'Adapta los términos "Individuo" y "Compañía" a la terminología legal española',
    'description': """
        Sustituye las etiquetas genéricas del campo Tipo de Contacto:
        - "Individuo"  →  "Persona Física"
        - "Compañía"   →  "Empresa"

        Válido para proveedores, clientes y cualquier contacto en res.partner.
        Desarrollado para REDLMC SL y aplicado también a PremiosRed/REDROYAL SL.

        NOTA Enterprise v18:
        - Eliminadas dependencias OCA (om_account_*) no disponibles en Enterprise.
        - Enterprise incluye account_accountant, account_asset de forma nativa.
        - Compatible con Odoo 18 Enterprise sin módulos de terceros adicionales.
    """,
    'author': 'REDLMC SL',
    'website': 'https://redlmc.com',
    'category': 'Localization',
    'license': 'LGPL-3',
    # Enterprise: las OCA (om_account_*) se reemplazan por módulos nativos de Enterprise
    'depends': ['base', 'contacts', 'account'],
    'post_init_hook': '_post_init_hook',
    'data': [
        'views/account_menu_es.xml',
        'templates/login_branding.xml',
    ],
    'assets': {
        # CSS del login: se carga via web.assets_frontend (bundle de páginas públicas)
        'web.assets_frontend': [
            'redlmc_es_labels/static/src/css/login_branding.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
