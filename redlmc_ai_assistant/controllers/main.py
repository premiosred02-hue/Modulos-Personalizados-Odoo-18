# -*- coding: utf-8 -*-
"""
main.py — Controlador HTTP para REDLMC AI Assistant
====================================================
Endpoint de prueba y webhook para futuras integraciones
(ej. Google Apps Script → Odoo).
"""
from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class RedlmcAiController(http.Controller):

    @http.route('/redlmc/ai/ping', type='json', auth='user', methods=['POST'])
    def ping(self, **kwargs):
        """
        Endpoint de prueba para verificar que el módulo está activo.
        curl -X POST http://localhost:8001/redlmc/ai/ping \
             -H "Content-Type: application/json" \
             -d '{"jsonrpc":"2.0","method":"call","params":{}}'
        """
        module = request.env['ir.module.module'].sudo().search(
            [('name', '=', 'redlmc_ai_assistant')], limit=1
        )
        return {
            'status': 'ok',
            'module': 'redlmc_ai_assistant',
            'version': module.installed_version if module else 'unknown',
            'gemini_configured': bool(
                request.env['ir.config_parameter'].sudo().get_param('redlmc.gemini_api_key')
            ),
            'gemini_model': request.env['ir.config_parameter'].sudo().get_param(
                'redlmc.gemini_model', 'gemini-1.5-pro'
            ),
        }

    @http.route('/redlmc/ai/ask', type='json', auth='user', methods=['POST'])
    def ask_gemini(self, prompt='', context='', **kwargs):
        """
        Endpoint JSON-RPC para llamar a Gemini desde el frontend OWL.
        Usado por el widget AiChatWidget.js en el chatter de Odoo.
        """
        if not prompt:
            return {'error': 'prompt is required'}

        try:
            gemini = request.env['redlmc.gemini.service']
            response = gemini.ask(prompt=prompt, system_context=context)
            return {'response': response, 'status': 'ok'}
        except Exception as e:
            _logger.error("Error en /redlmc/ai/ask: %s", str(e))
            return {'error': str(e), 'status': 'error'}
