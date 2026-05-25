# -*- coding: utf-8 -*-
{
    'name': 'PromocionesRed · Constructor de Carteles',
    'version': '18.0.1.1.0',  # Enterprise-ready
    'summary': 'Editor visual de carteles promocionales (tipo Canva) integrado en Odoo 18 Enterprise.',
    'author': 'PromocionesRed.com / Arqvi Dev',
    'category': 'Marketing',
    'description': """
        Constructor visual de carteles promocionales para PromocionesRed.com.

        Funcionalidades:
        - Editor tipo Canva integrado en Odoo 18 (OWL Framework)
        - Múltiples formatos: A4 V1/V2, Cuadrado 50x50, Banner 150x50, Poster 70x100
        - Sidebar de edición en tiempo real (contenido, packs, branding, legal)
        - Canvas interactivo con zoom, pan y borde de seguridad anticopia
        - Exportación a PDF via html2canvas + jsPDF
        - Generación de QR integrada (QRious.js nativo)
        - Estado persistido en Odoo (models: cc.cartel.design)
        - Vista de galería de diseños guardados
        - Modo impresión optimizado
    """,
    'depends': ['web', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/cartel_design_views.xml',
        'views/actions.xml',
        'views/menus.xml',
    ],
    'assets': {
        #
        # NOTA DE ARQUITECTURA:
        # Los assets del editor se cargan en web.assets_backend porque Odoo 18
        # no soporta bundles lazy personalizados en Client Actions (Community ni Enterprise).
        # Todo el CSS usa selectores scoped (.cc-main-wrapper y .cc-design-canvas)
        # para evitar contaminar la UI global de Odoo (incluyendo Enterprise).
        #
        'web.assets_backend': [
            # ── Librerías externas (bundleadas localmente, sin CDN en runtime) ──
            'promocionesred_canva_cartel/static/lib/html2canvas.min.js',
            'promocionesred_canva_cartel/static/lib/jspdf.umd.min.js',
            'promocionesred_canva_cartel/static/lib/qrious.min.js',

            # ── Estilos (scoped bajo .cc-main-wrapper y .cc-design-canvas) ────
            # El @import de Google Fonts fue ELIMINADO (bloqueaba el render de Odoo).
            # Se usa la fuente system-ui como fallback.
            'promocionesred_canva_cartel/static/src/css/editor.css',
            'promocionesred_canva_cartel/static/src/css/templates.css',

            # ── Templates OWL (XML debe ir ANTES del JS que los referencia) ────
            'promocionesred_canva_cartel/static/src/xml/CartelEditorView.xml',
            'promocionesred_canva_cartel/static/src/xml/CartelSidebar.xml',
            'promocionesred_canva_cartel/static/src/xml/TemplateA4V2.xml',
            'promocionesred_canva_cartel/static/src/xml/TemplateA4V1.xml',
            'promocionesred_canva_cartel/static/src/xml/TemplateSquare50.xml',
            'promocionesred_canva_cartel/static/src/xml/TemplateBanner150_50.xml',
            'promocionesred_canva_cartel/static/src/xml/TemplatePoster70_100.xml',

            # ── JavaScript OWL (después del XML) ──────────────────────────────
            # Orden de dependencias: data → sub-templates → sidebar → editor (root)
            'promocionesred_canva_cartel/static/src/js/cartel_data.js',
            'promocionesred_canva_cartel/static/src/js/TemplateA4V2.js',
            'promocionesred_canva_cartel/static/src/js/TemplateA4V1.js',
            'promocionesred_canva_cartel/static/src/js/TemplateSquare50.js',
            'promocionesred_canva_cartel/static/src/js/TemplateBanner150_50.js',
            'promocionesred_canva_cartel/static/src/js/TemplatePoster70_100.js',
            'promocionesred_canva_cartel/static/src/js/CartelSidebar.js',
            'promocionesred_canva_cartel/static/src/js/CartelEditorView.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
