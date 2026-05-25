# -*- coding: utf-8 -*-
from odoo import models, fields, api
import json


class CcCartelDesign(models.Model):
    """
    Modelo de persistencia para diseños de carteles.
    Almacena el estado JSON completo del editor (contenido, formato, UI).
    """
    _name = 'cc.cartel.design'
    _description = 'Diseño de Cartel Promocional'
    _order = 'write_date desc'

    name = fields.Char(
        string='Nombre del Diseño',
        required=True,
        default='Nuevo Cartel',
    )
    active_format = fields.Char(
        string='Formato Activo',
        default='a4_v2',
    )
    design_json = fields.Text(
        string='JSON del Diseño',
        help='Almacena el estado completo del editor en formato JSON.',
    )
    thumbnail = fields.Binary(
        string='Miniatura',
        attachment=True,
        help='Captura PNG del diseño para previsualización en galería.',
    )
    notes = fields.Text(
        string='Notas Internas',
    )
    state = fields.Selection(
        [
            ('draft', 'Borrador'),
            ('ready', 'Listo para Imprimir'),
            ('archived', 'Archivado'),
        ],
        string='Estado',
        default='draft',
    )

    # ── Campos relacionales para integración futura ──────────────────────
    user_id = fields.Many2one(
        'res.users',
        string='Creado por',
        default=lambda self: self.env.user,
        readonly=True,
    )

    @api.model
    def get_default_design(self):
        """Devuelve el JSON de diseño por defecto para un nuevo cartel."""
        default = {
            "active_format": "a4_v2",
            "formats": {
                "a4_v2": {"name": "A4 Vertical V2", "width": "210mm", "height": "297mm", "layout": "vertical-stack"},
                "a4_v1": {"name": "A4 Vertical V1", "width": "210mm", "height": "297mm", "layout": "compact-grid"},
                "square_50": {"name": "50x50 CM Cuadrado", "width": "500mm", "height": "500mm", "layout": "grid-2x2"},
                "banner_150_50": {"name": "Banner 150x50 CM", "width": "1500mm", "height": "500mm", "layout": "horizontal-banner"},
                "poster_70_100": {"name": "Poster 70x100 CM", "width": "700mm", "height": "1000mm", "layout": "large-format"},
            },
            "content": {
                "brand": "PremiosRed.com",
                "promo_title": "GRAN PROMOCIÓN DE PREMIOS EXCLUSIVOS",
                "promo_subtitle": "Y PARTICIPA EN EL SORTEO DE 20.000 €",
                "solidarity_text": '"Producto Solidario: Donamos 0,10€ por ticket a la lucha contra el Cáncer"',
                "qr_url": "https://premiosred.com",
                "legal_text": "Promoción de combinación aleatoria con fines publicitarios, excluida del ámbito del juego conforme a la Ley 13/2011. El importe satisfecho corresponde exclusivamente a la adquisición de un cupón de ahorro, IVA incluido. Sorteo ante notario el 22/12/2026 a las 12:00 h. Bases legales en www.premiosred.com. Prohibida la venta y participación a menores de 18 años. Organiza REDGLOBAL S.L.",
                "packs": [
                    {
                        "id": "tech", "name": "PACK TECNOLOGÍA", "subtitle": "Y LO QUE TE AHORRAS SI LO COMPRAS",
                        "price": "6", "color": "#f37021",
                        "items": [
                            "2 Códigos de Ahorro de (12 Cent € /L) en combustible en GALP.com",
                            "1 Bono de 2 Noches de hotel para 2 Pers (Solo Alojamiento gratuito).",
                            "1 Cupón Desc. Del 5% en Web/Tienda en APPLE.com",
                            "2 Participaciones gratis para el SORTEO de productos valorados en 3500 €."
                        ],
                        "logo": "https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg"
                    },
                    {
                        "id": "fashion", "name": "PACK MODA", "subtitle": "",
                        "price": "7", "color": "#4caf50",
                        "items": [
                            "3 Códigos de Ahorro de (12 Cent € /L) en combustible en GALP.com",
                            "2 Bonos de 2 Noches de hotel para 2 Pers (Solo Alojamiento gratuito).",
                            "1 Cupón Desc. Del 5% en Web/Tienda en ZARA.com",
                            "3 Participaciones gratis para el SORTEO de productos valorados en 4500 €."
                        ],
                        "logo": "https://upload.wikimedia.org/wikipedia/commons/f/fd/Zara_Logo.svg"
                    },
                    {
                        "id": "cosmetic", "name": "PACK COSMÉTICA", "subtitle": "",
                        "price": "8", "color": "#0071bc",
                        "items": [
                            "4 Códigos de Ahorro de (12 Cent € /L) en combustible en GALP.com",
                            "3 Bonos de 2 Noches de hotel para 2 Pers (Solo Alojamiento gratuito).",
                            "1 Cupón Desc. Del 5% en Web/Tienda en DRUNI.com",
                            "4 Participaciones gratis para el SORTEO de productos valorados en 5500 €."
                        ],
                        "logo": "https://static.brand.druni.es/logo-druni.svg"
                    },
                    {
                        "id": "travel", "name": "PACK CARIBE", "subtitle": "Todo incluido 7 noches/9 días 2 pers",
                        "price": "9", "color": "#ce1126",
                        "items": [
                            "5 Códigos de Ahorro de (12 Cent € /L) en combustible en GALP.com",
                            "4 Bonos de 2 Noches de hotel para 2 Pers (Solo Alojamiento gratuito).",
                            "1 Cupón Desc. Del 5% en Web/Tienda en RIU.com",
                            "5 Participaciones gratis para el SORTEO de productos valorados en 6500 €."
                        ],
                        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Riu_Hotels_%26_Resorts_logo.svg/1200px-Riu_Hotels_%26_Resorts_logo.svg.png"
                    }
                ]
            },
            "ui": {
                "show_partner_logos": True,
                "border_color": "#f37021",
                "border_width": "0px",
                "border_style": "solid",
                "border_radius": "0px",
                "show_security_border": False
            }
        }
        return json.dumps(default)

    def action_mark_ready(self):
        self.state = 'ready'

    def action_archive(self):
        self.state = 'archived'
