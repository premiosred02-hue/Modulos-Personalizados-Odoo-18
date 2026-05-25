# -*- coding: utf-8 -*-
{
    'name': 'PromocionesRed.com Dashboard ADM',
    'version': '18.0.2.2.0',  # Enterprise-ready
    'summary': 'Panel de gestión de leads, red de colaboradores y finanzas para PromocionesRed.com.',
    'author': 'PromocionesRed.com / Arqvi Dev',
    'category': 'Custom',
    'description': """
        Dashboard administrativo completo para PromocionesRed.com.
        Migrado desde React.js + Supabase a Odoo 18 nativo.

        Módulos funcionales:
        - Dashboard de KPIs (Total Leads, Conversión, Sponsors, Fondo de Garantía)
        - Pipeline de Leads con edición inline
        - Formulario de registro de nuevos leads (Empresas / Colaboradores / Personas)
        - Red de colaboradores COL/SUB con vista jerárquica
        - Generador de QR por colaborador
        - Email Marketing con tracking de aperturas y clics
        - Finanzas: regla 55/45
        - Gestión Legal y Auditoría
        - SEC-OPS: Usuarios y Logs de auditoría (usa el sistema de usuarios de Odoo)
    """,
    'depends': ['web', 'base', 'mail', 'crm', 'promocionesred_core_models'],
    'data': [
        'security/ir.model.access.csv',
        'views/actions.xml',
        'views/menus.xml',
        'views/qr_verify_portal.xml',
        'data/demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # ── Fuentes (debe ir PRIMERO para que @import funcione) ───
            'promocionesred_dashboard/static/src/fonts.css',
            # ── Estilos ──────────────────────────────────────────────
            'promocionesred_dashboard/static/src/app.css',
            'promocionesred_dashboard/static/src/components/onboarding.css',
            'promocionesred_dashboard/static/src/cupones.css',
            # ── Templates XML (DEBEN ir antes que el JS) ─────────────
            'promocionesred_dashboard/static/src/components/Dashboard.xml',
            'promocionesred_dashboard/static/src/components/LeadForm.xml',
            'promocionesred_dashboard/static/src/components/NetworkView.xml',
            'promocionesred_dashboard/static/src/components/MyQRView.xml',
            'promocionesred_dashboard/static/src/components/EmailManager.xml',
            'promocionesred_dashboard/static/src/components/FinanceView.xml',
            'promocionesred_dashboard/static/src/components/LegalView.xml',
            'promocionesred_dashboard/static/src/components/AuditView.xml',
            'promocionesred_dashboard/static/src/components/SecurityView.xml',
            'promocionesred_dashboard/static/src/components/OnboardingView.xml',
            'promocionesred_dashboard/static/src/components/EmpresasView.xml',
            'promocionesred_dashboard/static/src/components/CuponesView.xml',
            'promocionesred_dashboard/static/src/components/PromotoresView.xml',
            'promocionesred_dashboard/static/src/components/PacksView.xml',
            'promocionesred_dashboard/static/src/app.xml',
            # ── JavaScript (va DESPUÉS del XML) ──────────────────────
            'promocionesred_dashboard/static/src/components/Dashboard.js',
            'promocionesred_dashboard/static/src/components/LeadForm.js',
            'promocionesred_dashboard/static/src/components/NetworkView.js',
            'promocionesred_dashboard/static/src/components/MyQRView.js',
            'promocionesred_dashboard/static/src/components/EmailManager.js',
            'promocionesred_dashboard/static/src/components/FinanceView.js',
            'promocionesred_dashboard/static/src/components/LegalView.js',
            'promocionesred_dashboard/static/src/components/AuditView.js',
            'promocionesred_dashboard/static/src/components/SecurityView.js',
            'promocionesred_dashboard/static/src/components/OnboardingView.js',
            'promocionesred_dashboard/static/src/components/EmpresasView.js',
            'promocionesred_dashboard/static/src/components/CuponesView.js',
            'promocionesred_dashboard/static/src/components/PromotoresView.js',
            'promocionesred_dashboard/static/src/components/PacksView.js',
            'promocionesred_dashboard/static/src/app.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
