# -*- coding: utf-8 -*-
{
    'name': 'REDLMC AI Assistant — Gemini Ultra',
    'version': '18.0.1.1.0',  # Enterprise-ready
    'summary': 'Integración Gemini AI (Google Workspace Ultra) en Odoo 18 Enterprise. Clasificación de facturas, asistente contable y alertas fiscales automáticas.',
    'author': 'REDLMC SL / Arqvi Dev',
    'category': 'Productivity',
    'description': """
REDLMC AI Assistant — Gemini Ultra Integration
===============================================

Módulo de integración entre Google Workspace Ultra (Gemini AI)
y Odoo 18 Enterprise.

Funcionalidades:
----------------
- Clasificación automática de facturas recibidas por Gmail
  (extrae proveedor, importe, fecha, concepto usando Gemini Vision)
- Asistente contable en el chatter de Odoo
  (pregunta en lenguaje natural sobre tu contabilidad)
- Alertas fiscales automáticas
  (recordatorios Modelo 036, 685, 303, 111 con contexto del negocio)
- Generación de borradores de contratos desde plantillas
  (rellena campos con datos del registro activo en Odoo)
- Resumen diario de actividad
  (cron nocturno: resume cambios del día y los envía al ADM)

Seguridad:
----------
- API Key almacenada en ir.config_parameter (cifrada en BD)
- Nunca en código fuente, nunca en Git
- Timeout máximo: 30s por llamada
- Rate limiting: máximo 60 llamadas/minuto por usuario

Configuración:
--------------
Ajustes → REDLMC AI → Gemini API Key
(obtener en: https://aistudio.google.com/app/apikey)

Ref. arquitectura: 80.20 SISTEMA-GESTION-DOCUMENTAL-ODOO.md
    """,
    'depends': [
        'base',
        'mail',
        'account',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/cron_data.xml',
        'views/ai_assistant_views.xml',
        'views/menus.xml',
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'redlmc_ai_assistant/static/src/components/AiChatWidget.xml',
    #         'redlmc_ai_assistant/static/src/components/AiChatWidget.js',
    #         'redlmc_ai_assistant/static/src/components/AiChatWidget.css',
    #     ],
    # },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': ['requests'],
    },
}
