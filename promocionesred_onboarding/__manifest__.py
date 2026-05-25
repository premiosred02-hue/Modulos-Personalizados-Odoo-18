{
    'name': 'PremiosRed Onboarding de Actores (KYB)',
    'version': '18.0.1.1.0',  # Enterprise-ready
    'category': 'Sales',
    'summary': 'Wizard KYB y Onboarding Digital para Actores de PremiosRed',
    'description': """
        Digitaliza los formularios de alta para COL, SUB, CCP, COM y ASE.
        - Gestión de KYB y documentación de actores.
        - Wizard de onboarding por pasos.
        - Sistema de validación (NIF, IBAN).
        - Kill Switch de campaña integrado.

        NOTA Enterprise v18:
        - portal: compatible con portal_enterprise si está disponible.
        - Puede integrarse con sign (firma digital) de Enterprise.
    """,
    'author': 'Antigravity AI / REDLMC SL',
    'website': 'https://premiosred.com',
    'depends': ['redlmc_partner_ext', 'mail', 'portal'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'views/res_partner_kyb_views.xml',
        'views/onboarding_wizard_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
}

