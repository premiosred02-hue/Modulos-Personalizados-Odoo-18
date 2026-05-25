# -*- coding: utf-8 -*-
import base64
import logging
import re
from odoo import models, fields, _
from odoo.exceptions import UserError
import PyPDF2
from io import BytesIO

_logger = logging.getLogger(__name__)

class AccountMoveOcrLocal(models.Model):
    _inherit = 'account.move'

    ocr_local_text = fields.Text(string='Texto extraído (Local OCR)')

    def copy(self, default=None):
        default = dict(default or {})
        default['ocr_local_text'] = False
        return super().copy(default)

    def action_analyze_with_local_ocr(self):
        """
        Extrae texto de los adjuntos PDF usando PyPDF2 puro sin conectarse a internet.
        Luego intenta buscar la fecha, total e IVA usando expresiones regulares simples.
        """
        self.ensure_one()

        if self.move_type not in ('in_invoice', 'in_refund'):
            raise UserError(_("Esta función solo está disponible en facturas de proveedor."))

        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'account.move'),
            ('res_id', '=', self.id),
            ('mimetype', '=', 'application/pdf'),
        ], limit=1)

        if not attachments:
            raise UserError(_("No hay ningún PDF adjunto en esta factura."))

        attachment = attachments[0]
        pdf_data = base64.b64decode(attachment.datas)
        
        extracted_text = ""
        try:
            reader = PyPDF2.PdfReader(BytesIO(pdf_data))
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
        except Exception as e:
            raise UserError(_(f"Error al leer el PDF localmente: {str(e)}"))

        if not extracted_text.strip():
            raise UserError(_("No se pudo extraer texto. Es posible que el PDF sea una imagen escaneada."))

        # Intentar extraer Total (ej: Total: 100,50€ o Total 100.50)
        total_pattern = r'(?i)total[\s:]*([\d.,]+)'
        total_matches = re.findall(total_pattern, extracted_text)
        sug_total = total_matches[-1] if total_matches else "No encontrado"

        # Extraer NIF/CIF asegurando que limpia nombres concatenados (ej. "NIF:GONZALO LARGACHA LAMELA")
        nif_pattern = r'(?i)(?:NIF|CIF)[\s:]*([A-Z0-9]{9})'
        nif_match = re.search(nif_pattern, extracted_text)
        sug_nif = nif_match.group(1).upper() if nif_match else "No encontrado"

        # Extraer Número de Factura
        factura_pattern = r'(?i)(?:factura|fra\.?|nº|numero)[\s:]*([A-Z0-9\-\/]{4,15})'
        factura_match = re.search(factura_pattern, extracted_text)
        sug_factura = factura_match.group(1) if factura_match else "No encontrado"

        # Construir sugerencia
        sugerencia_local = f"Extracción Local Finalizada.\nTexto puro extraído ({len(extracted_text)} caracteres).\n\n"
        sugerencia_local += f"🔍 Búsqueda rápida:\n- Posible Total: {sug_total}\n- Posible NIF: {sug_nif}\n- Posible N.Factura: {sug_factura}\n"

        # Validación estricta del Total vs Odoo (amount_total)
        if sug_total != "No encontrado":
            try:
                # Normalizar 1.000,50 -> 1000.50 | 1000.50 -> 1000.50
                clean_str = sug_total.replace('.', '').replace(',', '.')
                if ',' not in sug_total and '.' in sug_total and sug_total.count('.') == 1:
                    clean_str = sug_total
                parsed_total = float(clean_str)
                
                # Si el total ya estaba ingresado en Odoo y difiere del PDF
                if self.amount_total > 0 and abs(parsed_total - self.amount_total) > 0.05:
                    sugerencia_local += f"\n⚠️ ALERTA: El Total extraído del PDF ({parsed_total:.2f}€) no coincide con el total registrado en Odoo ({self.amount_total:.2f}€)."
            except Exception:
                pass

        vals = {
            'ocr_local_text': extracted_text,
            'ai_suggestion': sugerencia_local,
            'ai_analyzed': True,
        }

        # Aplicar si encontró algo válido
        if sug_factura != "No encontrado":
            vals['ref'] = sug_factura
            # Corregir si el nombre principal lo había rellenado Odoo erróneamente con el nombre del proveedor
            if self.name and "LARGACHA" in self.name.upper():
                vals['name'] = sug_factura
        if sug_nif != "No encontrado" and not self.partner_id:
            partner = self.env['res.partner'].search([('vat', 'ilike', sug_nif)], limit=1)
            if partner:
                vals['partner_id'] = partner.id

        self.write(vals)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '📄 OCR Local',
                'message': 'Texto extraído sin IA. Revisa la sugerencia en la pestaña Análisis.',
                'type': 'success',
                'sticky': False,
            }
        }
