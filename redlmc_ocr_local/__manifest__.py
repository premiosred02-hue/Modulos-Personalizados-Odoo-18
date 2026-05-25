# -*- coding: utf-8 -*-
{
    'name': 'REDLMC OCR Local — Extracción sin IA',
    'version': '18.0.1.1.0',  # Enterprise-ready
    'summary': 'Extracción de texto puro de facturas PDF sin usar APIs externas (Gemini) usando PyPDF2 nativo.',
    'author': 'REDLMC SL',
    'category': 'Accounting',
    'depends': ['account', 'redlmc_ai_assistant'],
    'data': [
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

