# -*- coding: utf-8 -*-
"""
res_config_settings.py — Configuración del módulo en Ajustes de Odoo
=====================================================================
Añade la sección "REDLMC AI" al menú de Ajustes de Odoo para configurar
la API Key de Gemini de forma segura (almacenada en ir.config_parameter).
"""
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # ── Campo de configuración visible en Ajustes ──────────────────────────
    redlmc_gemini_api_key = fields.Char(
        string='Gemini API Key',
        help=(
            'Clave de API de Google Gemini (Google AI Studio).\n'
            'Obtener en: https://aistudio.google.com/app/apikey\n'
            'Se almacena cifrada en la base de datos de Odoo.\n'
            '⚠️ NUNCA la compartas ni la incluyas en código fuente.'
        ),
        config_parameter='redlmc.gemini_api_key',
    )

    redlmc_gemini_model = fields.Selection(
        string='Modelo Gemini',
        selection=[
            ('gemini-1.5-pro',   'Gemini 1.5 Pro (recomendado)'),
            ('gemini-1.5-flash', 'Gemini 1.5 Flash (más rápido, menor coste)'),
            ('gemini-1.0-pro',          'Gemini 1.0 Pro (legacy)'),
        ],
        default='gemini-1.5-pro',
        config_parameter='redlmc.gemini_model',
        help='Modelo de Gemini a usar. Pro es más preciso; Flash es más rápido.',
    )

    redlmc_gemini_max_tokens = fields.Integer(
        string='Máx. tokens por respuesta',
        default=2048,
        config_parameter='redlmc.gemini_max_tokens',
        help='Límite de tokens por llamada. Valor recomendado: 2048.',
    )

    redlmc_ai_invoice_auto = fields.Boolean(
        string='Clasificación automática de facturas',
        default=False,
        config_parameter='redlmc.ai_invoice_auto',
        help=(
            'Si está activo, Gemini analizará automáticamente los PDFs adjuntos '
            'en facturas de proveedor y sugerirá cuenta contable y datos de línea.'
        ),
    )

    redlmc_ai_fiscal_alerts = fields.Boolean(
        string='Alertas fiscales automáticas',
        default=True,
        config_parameter='redlmc.ai_fiscal_alerts',
        help=(
            'Envía recordatorios por email generados por Gemini '
            '7 días antes de cada obligación fiscal (Mod. 036, 685, 303, 111...).'
        ),
    )

    redlmc_ai_alert_email = fields.Char(
        string='Email de alertas fiscales',
        config_parameter='redlmc.ai_alert_email',
        help='Email donde se enviarán las alertas fiscales generadas por Gemini.',
    )
