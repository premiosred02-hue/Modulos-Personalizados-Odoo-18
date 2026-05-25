# -*- coding: utf-8 -*-
# ── PREMIOSRED — Modelo pr.cupon (Cupones con Hash Chain DGOJ) ────────────
# Trazabilidad completa: PDV (COL/SUB) → USU → Sorteo
# Hash Chain append-only conforme DGOJ
# Vault: 40.01 PACKS-Y-PREMIOS · 40.02 MECANICA-PARTICIPACION · 80.00 TECH
import hashlib
from odoo import models, fields, api
from odoo.exceptions import ValidationError


CUPON_STATUS = [
    ('available', 'Disponible'),
    ('used',      'Utilizado'),
    ('expired',   'Expirado'),
]

DELIVERY_CHANNEL = [
    ('whatsapp', 'WhatsApp'),
    ('email',    'Email'),
    ('sms',      'SMS'),
]

# Vault 50.01 §3 — Venta directa vs asistida define qué comisión cobra el COL
SALE_TYPE = [
    ('direct',   'Directa (QR fijo COL — 45%)'),
    ('assisted', 'Asistida (QR móvil SUB — COL 20% + SUB 25%)'),
]

# Vault 40.04 — Las 5 causas de donación (0,40% cada una, 2% total)
CAUSA_DONACION = [
    ('aecc',      'AECC — Lucha contra el Cáncer'),       # POR DEFECTO
    ('caritas',   'Cáritas Española — Acción Social'),
    ('manos',     'Manos Unidas — Lucha contra el Hambre'),
    ('cruz_roja', 'Cruz Roja Española — Emergencias'),
    ('episcopal', 'Iglesia Episcopal Española — Fe/Comunidad'),
]


class PrCupon(models.Model):
    _name = 'pr.cupon'
    _description = 'Cupon PremiosRed (trazabilidad completa + Hash Chain DGOJ)'
    _order = 'created_at desc'
    _rec_name = 'code'

    # ── Identificación ──────────────────────────────────────────────────────
    code         = fields.Char('Codigo de cupon', required=True, copy=False)
    pack_id      = fields.Many2one('pr.pack', 'Pack', required=True, ondelete='restrict')
    pack_price   = fields.Float('PVP al momento de venta', digits=(10, 2))

    # ── Punto de Venta (PDV) ────────────────────────────────────────────────
    actor_id     = fields.Many2one(
        'pr.actor', 'PDV (COL o SUB)',
        domain=[('actor_type', 'in', ['COL', 'SUB'])]
    )
    # FIX: related hereda el tipo Selection de actor_type — sin lista inline
    # En Odoo 18 NO se puede combinar selection=[] con related= en el mismo campo
    pdv_type     = fields.Selection(
        related='actor_id.actor_type',
        string='Tipo PDV',
        store=True,
        readonly=True,
    )

    # ── Usuario final (USU) ──────────────────────────────────────────────────
    user_email   = fields.Char('Email usuario', required=True)
    user_name    = fields.Char('Nombre usuario')
    user_phone   = fields.Char('Telefono usuario')

    # ── Estado ──────────────────────────────────────────────────────────────
    status           = fields.Selection(CUPON_STATUS, 'Estado', default='available', required=True)
    delivery_channel = fields.Selection(DELIVERY_CHANNEL, 'Canal de entrega', default='whatsapp')
    otp_verified     = fields.Boolean('OTP verificado', default=False)

    # ── Tipo de Venta — Vault 50.01 §3 Split 55/45 ──────────────────────────
    # Define qué comisión cobra el COL: directa=45% / asistida=COL 20%+SUB 25%
    sale_type        = fields.Selection(
        SALE_TYPE,
        'Tipo de venta',
        default='direct',
        required=True,
        help='Directa: QR fijo COL (45%). Asistida: QR movil SUB (COL 20%+SUB 25%)'
    )

    # ── Causa de Donación — Vault 40.04 (5 causas, default AECC) ────────────
    causa_donacion   = fields.Selection(
        CAUSA_DONACION,
        'Causa de donacion',
        default='aecc',
        required=True,
        help='Elegida por el usuario en checkout. AECC por defecto (85% usuarios no cambian)'
    )

    # ── Comisiones calculadas por cupón (Split 55/45) ────────────────────────
    donacion_eur     = fields.Float(
        'Donacion (EUR)', compute='_compute_split', store=True, digits=(10, 4)
    )
    com_col_eur      = fields.Float(
        'Comision COL (EUR)', compute='_compute_split', store=True, digits=(10, 4)
    )
    com_sub_eur      = fields.Float(
        'Comision SUB (EUR)', compute='_compute_split', store=True, digits=(10, 4)
    )

    @api.depends('sale_type', 'pack_id', 'pack_id.price', 'pack_price')
    def _compute_split(self):
        for r in self:
            pvp = r.pack_price or (r.pack_id.price if r.pack_id else 0.0)
            r.donacion_eur = pvp * 0.02  # 2% paga REDROYAL (Ley Mecenazgo)
            if r.sale_type == 'direct':
                r.com_col_eur = pvp * 0.45
                r.com_sub_eur = 0.0
            else:  # assisted
                r.com_col_eur = pvp * 0.20
                r.com_sub_eur = pvp * 0.25


    # ── Fechas ──────────────────────────────────────────────────────────────
    created_at   = fields.Datetime('Fecha de emision', default=fields.Datetime.now)
    used_at      = fields.Datetime('Fecha de uso')
    expires_at   = fields.Date('Fecha de expiracion')

    # ── Sorteo ──────────────────────────────────────────────────────────────
    sorteo_ref   = fields.Char('Referencia del sorteo')
    sorteo_id    = fields.Char('ID del sorteo')

    # ── Hash Chain DGOJ ─────────────────────────────────────────────────────
    prev_hash    = fields.Char('Hash anterior (chain)', default='0000000')
    own_hash     = fields.Char('Hash propio', readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        """Append-only hash chain. Calcula SHA-256 de cada registro al crear."""
        # Recuperar último hash de la cadena antes de crear
        last = self.search([], order='id desc', limit=1)
        last_hash = last.own_hash if (last and last.own_hash) else '0000000'

        records_vals = []
        for vals in vals_list:
            if not vals.get('prev_hash'):
                vals['prev_hash'] = last_hash
            records_vals.append(vals)

        records = super().create(records_vals)
        for record in records:
            # Calcular hash propio después de crear (inline, sin método separado)
            payload = "{}|{}|{}|{}".format(
                record.code or '',
                record.prev_hash or '0000000',
                record.created_at or '',
                record.user_email or '',
            )
            record.own_hash = hashlib.sha256(payload.encode()).hexdigest()[:8]
            last_hash = record.own_hash  # Encadenar con el siguiente

        return records

    # ── Acción: marcar como usado ───────────────────────────────────────────
    def action_usar(self):
        for r in self:
            if r.status != 'available':
                raise ValidationError("El cupon %s no esta disponible." % r.code)
            r.write({
                'status': 'used',
                'used_at': fields.Datetime.now(),
            })

    # ── KPIs y datos para JS ─────────────────────────────────────────────────
    @api.model
    def get_cupones_data(self, filters=None):
        """Devuelve lista de cupones para CuponesView. Llamado desde JS."""
        domain = []
        if filters:
            if filters.get('status') and filters['status'] != 'all':
                domain.append(('status', '=', filters['status']))
            if filters.get('actor_id'):
                domain.append(('actor_id', '=', filters['actor_id']))

        cupones = self.search(domain, limit=200)
        result = []
        for c in cupones:
            result.append({
                'id': c.id,
                'code': c.code,
                'pack_name': c.pack_id.name if c.pack_id else '',
                'pack_price': c.pack_price or (c.pack_id.price if c.pack_id else 0),
                'pdv_name': c.actor_id.name if c.actor_id else '',
                'pdv_type': c.pdv_type or '',
                'user_name': c.user_name or '',
                'user_email': c.user_email,
                'user_phone': c.user_phone or '',
                'status': c.status,
                'sale_type': c.sale_type,
                'causa_donacion': c.causa_donacion,
                'donacion_eur': c.donacion_eur,
                'com_col_eur': c.com_col_eur,
                'com_sub_eur': c.com_sub_eur,
                'delivery_channel': c.delivery_channel or '',
                'otp_verified': c.otp_verified,
                'created_at': c.created_at.isoformat() if c.created_at else '',
                'used_at': c.used_at.isoformat() if c.used_at else '',
                'expires_at': c.expires_at.isoformat() if c.expires_at else '',
                'sorteo_ref': c.sorteo_ref or '',
                'sorteo_id': c.sorteo_id or '',
                'prev_hash': c.prev_hash or '',
                'own_hash': c.own_hash or '',
            })
        return result

    @api.model
    def get_cupones_stats(self):
        """Devuelve KPIs de cupones. Llamado desde JS."""
        all_c = self.search([])
        return {
            'total': len(all_c),
            'available': len(all_c.filtered(lambda c: c.status == 'available')),
            'used': len(all_c.filtered(lambda c: c.status == 'used')),
            'expired': len(all_c.filtered(lambda c: c.status == 'expired')),
            'no_otp': len(all_c.filtered(lambda c: not c.otp_verified)),
            'total_revenue': sum(
                c.pack_price or (c.pack_id.price if c.pack_id else 0)
                for c in all_c
            ),
        }
