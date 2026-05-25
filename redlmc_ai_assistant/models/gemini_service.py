# -*- coding: utf-8 -*-
"""
gemini_service.py — Capa de abstracción para Google Gemini AI Ultra
====================================================================
Propósito:
    Servicio central que gestiona todas las llamadas a la API de Gemini.
    Todos los modelos del módulo deben llamar a este servicio, nunca
    directamente a la API.

Seguridad:
    - La API Key se lee SIEMPRE de ir.config_parameter
    - Nunca está en código fuente ni en variables de entorno del proceso
    - Timeout máximo configurable (por defecto 30s)
    - Manejo de errores con fallback graceful

Ref. arquitectura: 80.20 SISTEMA-GESTION-DOCUMENTAL-ODOO.md § B.3
"""
import json
import logging
import requests
from odoo import models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

# Configuración de seguridad por defecto
DEFAULT_GENERATION_CONFIG = {
    "temperature": 0.2,       # Bajo → respuestas precisas y deterministas
    "topP": 0.8,
    "topK": 40,
    "maxOutputTokens": 2048,
}

SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT",       "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_HATE_SPEECH",      "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT","threshold": "BLOCK_ONLY_HIGH"},
]


class GeminiService(models.AbstractModel):
    """
    Servicio abstracto de Gemini AI.
    No tiene tabla en base de datos — solo métodos de servicio.
    Se accede con: self.env['redlmc.gemini.service']
    """
    _name = 'redlmc.gemini.service'
    _description = 'REDLMC — Servicio de Integración Gemini AI (Google Workspace Ultra)'

    # ─────────────────────────────────────────────────────────────────
    # API PÚBLICA — Métodos a usar desde otros modelos
    # ─────────────────────────────────────────────────────────────────

    @api.model
    def ask(self, prompt, system_context='', temperature=None, max_tokens=None):
        """
        Llamada principal a Gemini. Punto de entrada único para todo el módulo.

        Args:
            prompt (str):          Pregunta o instrucción principal.
            system_context (str):  Contexto del sistema / rol del asistente.
            temperature (float):   Temperatura (0.0-1.0). None = usa default 0.2.
            max_tokens (int):      Máximo de tokens en la respuesta.

        Returns:
            str: Respuesta de Gemini.

        Raises:
            UserError: Si la API Key no está configurada.
            UserError: Si la llamada falla después de 2 reintentos.
        """
        api_key = self._get_api_key()

        generation_config = dict(DEFAULT_GENERATION_CONFIG)
        if temperature is not None:
            generation_config['temperature'] = temperature
        if max_tokens is not None:
            generation_config['maxOutputTokens'] = max_tokens

        # Construir el contenido del mensaje
        contents = []
        if system_context:
            contents.append({
                "role": "user",
                "parts": [{"text": f"[CONTEXTO DEL SISTEMA]\n{system_context}"}]
            })
            contents.append({
                "role": "model",
                "parts": [{"text": "Entendido. Actuaré según el contexto indicado."}]
            })

        contents.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })

        payload = {
            "contents": contents,
            "generationConfig": generation_config,
            "safetySettings": SAFETY_SETTINGS,
        }

        return self._call_api(api_key, payload)

    @api.model
    def analyze_document(self, text_content, task='classify'):
        """
        Analiza el texto extraído de un documento (factura, contrato, etc.).

        Args:
            text_content (str): Texto del documento.
            task (str): 'classify' | 'summarize' | 'extract_invoice_data'

        Returns:
            dict | str: Resultado estructurado según la tarea.
        """
        task_prompts = {
            'classify': (
                "Eres un asistente contable experto en fiscalidad española. "
                "Analiza el siguiente documento y devuelve un JSON con: "
                "{'tipo': 'factura|contrato|extracto|otro', "
                "'proveedor': 'nombre', 'importe': 0.00, 'fecha': 'YYYY-MM-DD', "
                "'concepto': 'descripción breve', 'cuenta_contable': '621|628|etc', "
                "'iva_tipo': 21|10|4|0, 'confianza': 0.0-1.0}. "
                "Solo devuelve el JSON, sin texto adicional."
            ),
            'summarize': (
                "Resume el siguiente documento en máximo 3 frases en español, "
                "indicando: tipo de documento, partes involucradas e importe si aplica."
            ),
            'extract_invoice_data': (
                "Actúa como OCR inteligente y analista contable certificado. "
                "Extrae los datos de la factura respetando esta estructura JSON universal: "
                "{'proveedor': '...', 'fecha': 'YYYY-MM-DD', 'n_factura': '...', "
                "'total': 0.00, 'moneda': 'EUR', 'descripcion_general': '...', "
                "'es_rectificativa': false, 'notas': '...', "
                "'lineas': [{'descripcion': '...', 'precio': 0.00, 'cantidad': 1, "
                "'descuento_pct': 0.0, 'iva_pct': 21.0, 'irpf_pct': 15.0, "
                "'retencion_alquiler_pct': 19.0, 'recargo_equiv_pct': 5.2, "
                "'isp': false, 'suplido': false, 'nota': false}]}. "
                "Aplica reglas: Todo exactamente como en el PDF. No inventes lineas. "
                "Si un precio ya incluye descuento, no pongas descuento_pct. "
                "Suplidos van con suplido: true sin IVA. ISP va con isp: true sin IVA. "
                "Redondeo max 0.05. Solo JSON válido, sin texto adicional."
            ),
        }

        system = task_prompts.get(task, task_prompts['classify'])
        response = self.ask(
            prompt=f"DOCUMENTO:\n\n{text_content}",
            system_context=system,
            temperature=0.1,   # Muy bajo para extracciones estructuradas
        )

        # Intentar parsear JSON si la tarea lo requiere
        if task in ('classify', 'extract_invoice_data'):
            try:
                # Limpiar posibles marcadores de código markdown
                clean = response.strip().lstrip('```json').lstrip('```').rstrip('```').strip()
                return json.loads(clean)
            except json.JSONDecodeError:
                _logger.warning("Gemini no devolvió JSON válido para task=%s. Raw: %s", task, response[:200])
                return response

        return response

    @api.model
    def get_fiscal_alert(self, model_name, deadline, amount, company_name='REDLMC SL'):
        """
        Genera el texto de una alerta fiscal personalizada.

        Args:
            model_name (str):   'Modelo 685' | 'Modelo 303' | etc.
            deadline (str):     Fecha límite en formato YYYY-MM-DD.
            amount (float):     Importe a pagar.
            company_name (str): Nombre de la empresa.

        Returns:
            str: Email/mensaje de alerta listo para enviar.
        """
        prompt = (
            f"Redacta un email de recordatorio fiscal URGENTE en español para {company_name}. "
            f"El asunto es la presentación del {model_name} con fecha límite {deadline} "
            f"por un importe de {amount:,.2f}€. "
            f"El email debe ser profesional, conciso (máximo 150 palabras) y terminar con "
            f"los pasos de acción inmediatos. Firma como 'Sistema Fiscal Automático — REDLMC SL'."
        )
        return self.ask(prompt=prompt, temperature=0.4)

    # ─────────────────────────────────────────────────────────────────
    # MÉTODOS PRIVADOS
    # ─────────────────────────────────────────────────────────────────

    @api.model
    def _get_api_key(self):
        """Lee la API Key de ir.config_parameter. Lanza UserError si no está."""
        api_key = self.env['ir.config_parameter'].sudo().get_param(
            'redlmc.gemini_api_key'
        )
        if not api_key or not api_key.strip():
            raise UserError(_(
                "La API Key de Gemini no está configurada.\n"
                "Ve a: Ajustes → REDLMC AI → Gemini API Key\n"
                "Obtén tu clave en: https://aistudio.google.com/app/apikey"
            ))
        return api_key.strip()

    @api.model
    def _call_api(self, api_key, payload, retries=2):
        """
        Realiza la llamada HTTP a la API de Gemini con reintentos.

        Args:
            api_key (str):   Clave de API.
            payload (dict):  Payload JSON completo.
            retries (int):   Número de reintentos en caso de error 5xx.

        Returns:
            str: Texto de la respuesta de Gemini.

        Raises:
            UserError: En caso de error irrecuperable.
        """
        # Leer modelo desde Ajustes → REDLMC AI → Modelo Gemini
        model_name = self.env['ir.config_parameter'].sudo().get_param(
            'redlmc.gemini_model', 'gemini-1.5-pro'
        )
        if not model_name or not model_name.strip():
            model_name = 'gemini-1.5-pro'
        model_name = model_name.strip()
        # Sanear tags -latest deprecados que causaban 404
        if model_name == 'gemini-1.5-pro-latest':
            model_name = 'gemini-1.5-pro'
        elif model_name == 'gemini-1.5-flash-latest':
            model_name = 'gemini-1.5-flash'

        # Fix 2: Leer max_tokens del setting real (no el hardcoded 2048)
        max_tokens = int(self.env['ir.config_parameter'].sudo().get_param(
            'redlmc.gemini_max_tokens', 2048
        ) or 2048)
        payload.setdefault('generationConfig', {})['maxOutputTokens'] = max_tokens

        url = f"{GEMINI_BASE_URL}/{model_name}:generateContent?key={api_key}"

        for attempt in range(retries + 1):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    timeout=30,
                    headers={"Content-Type": "application/json"},
                )

                if response.status_code == 200:
                    data = response.json()
                    try:
                        return data['candidates'][0]['content']['parts'][0]['text']
                    except (KeyError, IndexError) as e:
                        _logger.error("Respuesta Gemini inesperada: %s", data)
                        raise UserError(_("Respuesta de Gemini inesperada. Revisa los logs."))

                elif response.status_code == 400:
                    error_detail = response.json().get('error', {}).get('message', 'Error 400')
                    raise UserError(_(f"Error en la solicitud a Gemini: {error_detail}"))

                elif response.status_code == 403:
                    raise UserError(_(
                        "Error de autenticación con Gemini (403).\n"
                        "Verifica que la API Key es correcta y tiene acceso a 'Generative Language API'."
                    ))

                elif response.status_code == 429:
                    raise UserError(_(
                        "Límite de velocidad de Gemini superado (429).\n"
                        "Espera 1 minuto e inténtalo de nuevo."
                    ))

                elif response.status_code >= 500 and attempt < retries:
                    _logger.warning("Gemini API error %s (intento %d/%d). Reintentando...",
                                    response.status_code, attempt + 1, retries)
                    continue

                else:
                    raise UserError(_(f"Error HTTP {response.status_code} al llamar a Gemini."))

            except requests.Timeout:
                if attempt < retries:
                    _logger.warning("Timeout llamando a Gemini (intento %d/%d). Reintentando...",
                                    attempt + 1, retries)
                    continue
                raise UserError(_(
                    "Timeout al conectar con Gemini AI (>30s).\n"
                    "Comprueba la conexión a internet del servidor."
                ))

            except requests.RequestException as e:
                raise UserError(_(f"Error de red al llamar a Gemini: {str(e)}"))

        raise UserError(_("No se pudo conectar con Gemini AI después de varios intentos."))
