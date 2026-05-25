# -*- coding: utf-8 -*-
"""
ai_invoice_classifier.py — Clasificador automático de facturas con Gemini
=========================================================================
Hereda account.move para añadir el botón "Analizar con IA" en facturas
de proveedor. Extrae datos del PDF adjunto y rellena los campos del formulario.
"""
import base64
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AiInvoiceClassifier(models.Model):
    _inherit = 'account.move'

    # ── Campos AI (solo en facturas de proveedor) ──────────────────────────
    ai_analyzed = fields.Boolean(
        string='Analizado por IA',
        default=False,
        help='Indica si Gemini ha analizado esta factura.'
    )
    ai_analysis_result = fields.Text(
        string='Resultado análisis IA',
        help='JSON con los datos extraídos por Gemini del documento adjunto.'
    )
    ai_confidence = fields.Float(
        string='Confianza IA (%)',
        digits=(3, 0),
        help='Nivel de confianza de Gemini en la extracción (0-100%).'
    )
    ai_suggestion = fields.Text(
        string='Sugerencia IA',
        help='Texto libre con la sugerencia de Gemini para esta factura.'
    )

    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'ai_analyzed': False,
            'ai_analysis_result': False,
            'ai_confidence': 0.0,
            'ai_suggestion': False,
        })
        return super().copy(default)

    # ── Acción: Analizar con IA ────────────────────────────────────────────
    def action_analyze_with_ai(self):
        """
        Analiza el PDF adjunto de la factura usando Gemini.
        Llamado desde el botón "🤖 Analizar con IA" en el formulario.
        """
        self.ensure_one()

        # Solo en facturas de proveedor
        if self.move_type not in ('in_invoice', 'in_refund'):
            raise UserError(_("Esta función solo está disponible en facturas de proveedor."))

        # Buscar adjuntos PDF
        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'account.move'),
            ('res_id', '=', self.id),
            ('mimetype', '=', 'application/pdf'),
        ], limit=1)

        if not attachments:
            raise UserError(_(
                "No hay ningún PDF adjunto en esta factura.\n"
                "Adjunta el PDF de la factura antes de analizar."
            ))

        # Extraer texto del PDF localmente (Local OCR)
        attachment = attachments[0]
        context_text = (
            f"Nombre del archivo: {attachment.name}\n"
            f"Tamaño: {attachment.file_size} bytes\n"
            f"Fecha de subida: {attachment.create_date}\n"
        )

        try:
            import PyPDF2
            from io import BytesIO
            pdf_data = base64.b64decode(attachment.datas)
            reader = PyPDF2.PdfReader(BytesIO(pdf_data))
            extracted_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
            if extracted_text.strip():
                context_text += "\n--- TEXTO EXTRAÍDO POR OCR LOCAL ---\n" + extracted_text
        except Exception as e:
            _logger.warning("Error al leer el PDF localmente: %s", str(e))

        if attachment.mimetype in ('text/xml', 'application/xml'):
            try:
                raw = base64.b64decode(attachment.datas).decode('utf-8', errors='ignore')
                context_text += f"\nContenido XML:\n{raw[:3000]}"
            except Exception:
                pass

        # Llamar a Gemini
        gemini = self.env['redlmc.gemini.service']
        try:
            result = gemini.analyze_document(
                text_content=context_text,
                task='extract_invoice_data'
            )
        except UserError:
            raise
        except Exception as e:
            raise UserError(_(f"Error al analizar con Gemini: {str(e)}"))

        # Guardar resultado
        if isinstance(result, dict):
            confidence = float(result.get('confianza', 1.0))
            self.write({
                'ai_analyzed': True,
                'ai_analysis_result': str(result),
                'ai_confidence': int(confidence * 100),
                'ai_suggestion': self._build_suggestion_text(result),
            })

            # Autocompletar campos si la confianza es alta (>80%)
            if confidence >= 0.8:
                self._apply_ai_suggestions(result)

            concepto = result.get('descripcion_general', result.get('concepto', 'Factura procesada'))
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '🤖 Gemini AI — Análisis completado',
                    'message': f"Confianza: {int(confidence * 100)}% | {concepto}",
                    'type': 'success' if confidence >= 0.8 else 'warning',
                    'sticky': False,
                }
            }
        else:
            # Gemini devolvió texto libre
            self.write({
                'ai_analyzed': True,
                'ai_suggestion': str(result),
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '🤖 Gemini AI',
                    'message': 'Análisis completado (ver campo Sugerencia IA)',
                    'type': 'info',
                }
            }

    def _build_suggestion_text(self, result):
        """Construye el texto de sugerencia legible para el usuario."""
        lines = []
        if result.get('proveedor'):
            lines.append(f"✅ Proveedor: {result['proveedor']}")
        if result.get('total'):
            lines.append(f"💶 Total: {result['total']:.2f}€")
            # Validación de descuadre contra Odoo
            if self.amount_total > 0 and abs(float(result['total']) - self.amount_total) > 0.05:
                lines.append(f"⚠️ ALERTA: El Total extraído del PDF ({float(result['total']):.2f}€) NO COINCIDE con el de Odoo ({self.amount_total:.2f}€). Revisa los suplidos o retenciones.")
        if result.get('fecha'):
            lines.append(f"📅 Fecha: {result['fecha']}")
        if result.get('descripcion_general'):
            lines.append(f"📝 Concepto: {result['descripcion_general']}")
        confianza = float(result.get('confianza', 1.0))
        lines.append(f"\n🎯 Confianza Gemini: {int(confianza * 100)}%")
        if confianza >= 0.8:
            lines.append("✅ Campos y líneas de factura aplicados automáticamente.")
        else:
            lines.append("⚠️ Confianza baja — revisa los datos manualmente.")
        return '\n'.join(lines)

    def _apply_ai_suggestions(self, result):
        """
        Aplica las sugerencias de Gemini al formulario de la factura.
        Crea/busca proveedor, completa cabecera y todas sus lineas.
        """
        vals = {}

        # Buscar o crear proveedor por nombre si no está ya asignado
        if not self.partner_id and result.get('proveedor'):
            partner = self.env['res.partner'].search([
                ('name', 'ilike', result['proveedor']),
                ('supplier_rank', '>', 0),
            ], limit=1)
            if partner:
                vals['partner_id'] = partner.id
            else:
                partner = self.env['res.partner'].create({
                    'name': result['proveedor'],
                    'supplier_rank': 1,
                    'is_company': True
                })
                vals['partner_id'] = partner.id

        # Fecha de factura
        if result.get('fecha') and not self.invoice_date:
            try:
                from datetime import datetime
                vals['invoice_date'] = datetime.strptime(result['fecha'], '%Y-%m-%d').date()
            except ValueError:
                pass

        # Referencia (número de factura)
        if result.get('n_factura') and not self.ref:
            vals['ref'] = result['n_factura']

        # Moneda
        moneda_code = result.get('moneda', 'EUR').upper()
        if moneda_code != 'EUR':
            currency = self.env['res.currency'].search([('name', '=', moneda_code)], limit=1)
            if currency:
                vals['currency_id'] = currency.id

        # Notas
        if result.get('notas'):
            vals['narration'] = result['notas']

        # Líneas de factura
        lineas = result.get('lineas', [])
        if lineas:
            invoice_lines = []
            for line in lineas:
                if line.get('nota'):
                    continue
                
                desc = line.get('descripcion', result.get('descripcion_general', 'Línea odoo'))
                precio = float(line.get('precio', 0.0))
                cantidad = float(line.get('cantidad', 1))
                descuento_pct = float(line.get('descuento_pct', 0.0))
                
                tax_ids_final = []
                es_suplido = bool(line.get('suplido')) or 'suplido' in desc.lower()
                es_isp = bool(line.get('isp'))
                
                if not es_suplido and not es_isp:
                    # Fix 4: búsqueda de impuestos robusta por tipo y signo
                    tax_map = [
                        # (campo_json, tipo_impuesto, es_retencion)
                        ('iva_pct',                'purchase', False),
                        ('irpf_pct',               'purchase', True),
                        ('retencion_alquiler_pct',  'purchase', True),
                        ('recargo_equiv_pct',        'purchase', False),
                    ]
                    for t_key, t_use, is_retention in tax_map:
                        val = line.get(t_key)
                        if val is None:
                            continue
                        val_float = float(val)
                        # Las retenciones en Odoo son negativas
                        amount_search = -val_float if is_retention else val_float
                        domain_tax = [
                            ('type_tax_use', '=', t_use),
                            ('amount', '=', amount_search),
                            ('price_include', '=', False),
                        ]
                        tax = self.env['account.tax'].search(domain_tax, limit=1)
                        if not tax:
                            # Fallback sin filtro de tipo_use
                            tax = self.env['account.tax'].search(
                                [('amount', '=', amount_search)], limit=1
                            )
                        if tax:
                            tax_ids_final.append(tax.id)
                elif es_isp:
                    tax = self.env['account.tax'].search([('type_tax_use', '=', 'purchase'), ('amount', '=', 0)], limit=1)
                    if tax: tax_ids_final.append(tax.id)
                
                line_vals = {
                    'name': desc,
                    'quantity': cantidad,
                    'price_unit': precio,
                }
                if descuento_pct:
                    line_vals['discount'] = descuento_pct
                if tax_ids_final:
                    line_vals['tax_ids'] = [(6, 0, tax_ids_final)]
                invoice_lines.append((0, 0, line_vals))
            
            if invoice_lines:
                vals['invoice_line_ids'] = [(5, 0, 0)] + invoice_lines

        if vals:
            self.write(vals)
            _logger.info("Gemini + OCR aplicó sugerencias a account.move id=%s", self.id)

    # ── Fix 6: Clasificación automática al adjuntar PDF ────────────────
    def _message_post_after_hook(self, message, msg_vals):
        """
        Hook de Odoo que se ejecuta tras cada adjunto en el chatter.
        Si redlmc.ai_invoice_auto está activo y se adjunta un PDF en
        una factura de proveedor borrador, lanza el análisis automáticamente.
        """
        res = super()._message_post_after_hook(message, msg_vals)
        if self.move_type not in ('in_invoice', 'in_refund'):
            return res
        if self.state != 'draft':
            return res
        auto = self.env['ir.config_parameter'].sudo().get_param(
            'redlmc.ai_invoice_auto', False
        )
        if not auto:
            return res
        # Verificar si hay algún attachment PDF en el mensaje recién creado
        has_pdf = any(
            att.mimetype == 'application/pdf'
            for att in message.attachment_ids
        )
        if has_pdf:
            try:
                self.action_analyze_with_ai()
            except Exception as e:
                _logger.warning(
                    "Auto-análisis IA falló en account.move id=%s: %s", self.id, e
                )
        return res
