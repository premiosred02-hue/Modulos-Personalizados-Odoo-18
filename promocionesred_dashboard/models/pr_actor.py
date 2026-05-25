# -*- coding: utf-8 -*-
# ── PREMIOSRED — Modelo pr.actor (Onboarding de actores) ─────────────────
# Migrado desde tabla `actors` de Supabase
# Tipos: COL | SUB | CCP | COM | ASE
# ADR-001: Solo ORM. ADR-003: Decimal para comisiones.
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date, datetime


ACTOR_TYPES = [
    ('COL', '🏪 Colaborador'),
    ('SUB', '📱 Subcolaborador'),
    ('CCP', '🎯 Captador Profesional'),
    ('COM', '💼 Comercial B2B'),
    ('ASE', '🤝 Asesor / Referido'),
]

ACTOR_STATUS = [
    ('PENDIENTE',   'Pendiente'),
    ('ACTIVO',      'Activo'),
    ('SUSPENDIDO',  'Suspendido'),
    ('BAJA',        'Baja'),
]

FISCAL_TYPES = [
    ('autonomo',   'Autónomo / RETA'),
    ('mercantil',  'Sociedad Mercantil'),
    ('informal',   'Informal / Sin alta'),
]

KYB_STATUS = [
    ('pending',   'Pendiente'),
    ('submitted', 'Enviado'),
    ('approved',  'Aprobado'),
    ('rejected',  'Rechazado'),
]

SECTOR_TYPES = [
    ('hosteleria',   '🍺 Hostelería'),
    ('restauracion', '🍽️ Restauración'),
    ('transporte',   '🚌 Transporte'),
    ('hotel',        '🏨 Hotel'),
    ('comercio',     '🛍️ Comercio'),
    ('aerolinea',    '✈️ Aerolínea'),
    ('otro',         '🏢 Otro'),
]


class PrActor(models.Model):
    _name = 'pr.actor'
    _description = 'Actor PremiosRed (COL/SUB/CCP/COM/ASE)'
    _order = 'create_date desc'
    _rec_name = 'name'

    # ── Identificación ──────────────────────────────────────────────────────
    name        = fields.Char('Nombre / Razón Social', required=True)
    code        = fields.Char('Código de actor', readonly=True, copy=False)
    actor_type  = fields.Selection(ACTOR_TYPES, 'Tipo de actor', required=True)
    status      = fields.Selection(ACTOR_STATUS, 'Estado', default='PENDIENTE', required=True)
    legal_name  = fields.Char('Nombre legal / Razón social')
    tax_id      = fields.Char('CIF / NIF / NIE')

    # ── Contacto ────────────────────────────────────────────────────────────
    email       = fields.Char('Email')
    phone       = fields.Char('Teléfono')
    address     = fields.Char('Dirección')
    city        = fields.Char('Ciudad')
    municipio   = fields.Char('Municipio')
    provincia   = fields.Char('Provincia')
    cp          = fields.Char('Código Postal')
    zone        = fields.Char('Zona (3 letras)')

    # ── Bancario ────────────────────────────────────────────────────────────
    banco_titular = fields.Char('Titular de la cuenta')
    banco_nombre  = fields.Char('Entidad bancaria')
    banco_iban    = fields.Char('IBAN')
    iban_verified = fields.Boolean('IBAN verificado', default=False)

    # ── Fiscal ──────────────────────────────────────────────────────────────
    fiscal_type = fields.Selection(FISCAL_TYPES, 'Régimen fiscal')
    fiscal_nss  = fields.Char('NSS (Número Seguridad Social)')
    fiscal_iae  = fields.Char('IAE')

    # ── KYB (Know Your Business) — solo COL ─────────────────────────────────
    kyb_status       = fields.Selection(KYB_STATUS, 'Estado KYB', default='pending')
    sector           = fields.Selection(SECTOR_TYPES, 'Sector de actividad')
    contract_version = fields.Char('Versión contrato')  # 'COL-v2.0'
    qr_code_id       = fields.Char('ID QR asignado')   # 'QR-020001'
    contrato_firmado = fields.Boolean('Contrato firmado', default=False)

    # ── Sistema QR ─────────────────────────────────────────────────────────
    col_code     = fields.Char('Código COL', help='Identificador COL para el QR, ej: COL-001')
    sub_code     = fields.Char('Código SUB vinculado', help='Subcolaborador asociado, ej: SUB-001')
    sponsor_code = fields.Char('Código Patrocinador (SPP)', help='Código del patrocinador, ej: SPP-01')
    scan_count   = fields.Integer('Escaneos del QR', default=0, help='Número de veces que se ha escaneado el QR')
    portal_type  = fields.Selection([
        ('standard',  'Standard'),
        ('premium',   'Premium'),
        ('marketing', 'Marketing'),
    ], 'Tipo de portal QR', default='standard')
    custom_label = fields.Char('Etiqueta QR personalizada', default='Sorteo Navidad',
                               help='Texto que aparece en el portal de verificación del QR')

    # ── Comisiones y financiero ──────────────────────────────────────────────
    commission_pct    = fields.Float('% Comisión pasiva', digits=(5, 2))
    total_sales       = fields.Float('Ventas totales', digits=(12, 2))
    total_earned      = fields.Float('Comisión ganada', digits=(12, 2))
    pending_payout    = fields.Float('Pendiente SEPA', digits=(12, 2))

    # ── Jerarquía ───────────────────────────────────────────────────────────
    parent_id   = fields.Many2one('pr.actor', 'COL padre (para SUB)')
    captor_id   = fields.Many2one(
        'pr.actor', 'Captador (CCP/COM/ASE)',
        domain=[('actor_type', 'in', ['CCP', 'COM', 'ASE'])]
    )
    child_ids   = fields.One2many('pr.actor', 'parent_id', 'Sub-actores')

    # ── Conteo computed ─────────────────────────────────────────────────────
    subs_count = fields.Integer(
        'Nº SUBs vinculados',
        compute='_compute_subs_count',
        store=True
    )

    @api.depends('child_ids')
    def _compute_subs_count(self):
        for r in self:
            r.subs_count = len(r.child_ids.filtered(
                lambda c: c.actor_type == 'SUB'
            ))

    cols_captados = fields.Integer(
        'COLs captados',
        compute='_compute_cols_captados',
        store=False  # No stored: @api.depends() vacio causaria error en instalacion
    )

    @api.depends('actor_type', 'captor_id')
    def _compute_cols_captados(self):
        for r in self:
            if r.actor_type in ('CCP', 'COM', 'ASE') and r.id:
                r.cols_captados = self.search_count([
                    ('captor_id', '=', r.id),
                    ('actor_type', '=', 'COL')
                ])
            else:
                r.cols_captados = 0

    # ── Extra data (JSON) ───────────────────────────────────────────────────
    extra_data  = fields.Text('Datos extra (JSON)')
    kyb_docs    = fields.Text('Documentos KYB (JSON)')
    consent_log = fields.Text('Log de consentimientos (JSON)')

    # ── Fechas ──────────────────────────────────────────────────────────────
    activated_at = fields.Datetime('Fecha de activación')
    valid_until  = fields.Date('Válido hasta')

    # ── Computed labels ─────────────────────────────────────────────────────
    @api.depends('actor_type')
    def _compute_type_label(self):
        labels = dict(ACTOR_TYPES)
        for r in self:
            r.type_label = labels.get(r.actor_type, '')

    type_label = fields.Char('Tipo (etiqueta)', compute='_compute_type_label', store=False)

    @api.depends('actor_type')
    def _compute_commission_label(self):
        comms = {
            'COL': '45% directa / 20% asistida',
            'SUB': '25% asistida',
            'CCP': '3% pasivo',
            'COM': '2% pasivo',
            'ASE': '2% pasivo',
        }
        for r in self:
            r.commission_label = comms.get(r.actor_type, '')

    commission_label = fields.Char('Comisión', compute='_compute_commission_label', store=False)

    # ── Generación de código único ──────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if not record.code:
                today = date.today().strftime('%Y%m%d')
                zone = (record.provincia or 'XXX')[:3].upper()
                seq = self.env['ir.sequence'].next_by_code('pr.actor.sequence') or '000001'
                record.code = f"RR-{record.actor_type}-{today}-{zone}-{seq}"
        return records

    # ── KPIs para el dashboard ──────────────────────────────────────────────
    @api.model
    def get_onboarding_stats(self):
        """Devuelve KPIs del módulo onboarding. Llamado desde JS con orm.call."""
        actors = self.search([])
        return {
            'total':      len(actors),
            'activos':    len(actors.filtered(lambda a: a.status == 'ACTIVO')),
            'pendientes': len(actors.filtered(lambda a: a.status == 'PENDIENTE')),
            'cols':       len(actors.filtered(lambda a: a.actor_type == 'COL')),
            'subs':       len(actors.filtered(lambda a: a.actor_type == 'SUB')),
            'ccps':       len(actors.filtered(lambda a: a.actor_type == 'CCP')),
            'coms':       len(actors.filtered(lambda a: a.actor_type == 'COM')),
            'ases':       len(actors.filtered(lambda a: a.actor_type == 'ASE')),
        }

    @api.model
    def get_empresas_data(self):
        """Devuelve lista de COLs para EmpresasView. Llamado desde JS."""
        cols = self.search([('actor_type', '=', 'COL')])
        result = []
        for c in cols:
            result.append({
                'id': c.id,
                'name': c.name,
                'code': c.code or '',
                'tax_id': c.tax_id or '',
                'email': c.email or '',
                'phone': c.phone or '',
                'address': c.address or '',
                'city': c.city or c.municipio or '',
                'sector': c.sector or 'otro',
                'kyb_status': c.kyb_status or 'pending',
                'status': c.status,
                'active': c.status == 'ACTIVO',
                'iban_verified': c.iban_verified,
                'contract_version': c.contract_version or '',
                'qr_code_id': c.qr_code_id or '',
                'subs_count': c.subs_count,
                'total_sales': c.total_sales,
                'total_earned': c.total_earned,
                'captador': c.captor_id.name if c.captor_id else '',
                'captador_role': c.captor_id.actor_type if c.captor_id else '',
                'joined_at': c.create_date.strftime('%Y-%m-%d') if c.create_date else '',
            })
        return result

    @api.model
    def get_promotores_data(self):
        """Devuelve lista de CCP/COM/ASE para PromotoresView. Llamado desde JS."""
        promotores = self.search([('actor_type', 'in', ['CCP', 'COM', 'ASE'])])
        comm_pct = {'CCP': 3, 'COM': 2, 'ASE': 2}
        result = []
        for p in promotores:
            result.append({
                'id': p.id,
                'name': p.name,
                'code': p.code or '',
                'dni': p.tax_id or '',
                'email': p.email or '',
                'phone': p.phone or '',
                'city': p.city or p.municipio or '',
                'role': p.actor_type,
                'commission_pct': comm_pct.get(p.actor_type, 2),
                'active': p.status == 'ACTIVO',
                'cols_captados': p.cols_captados,
                'total_sales_red': p.total_sales,
                'total_earned': p.total_earned,
                'pending_payout': p.pending_payout,
                'iban_verified': p.iban_verified,
                'contrato_firmado': p.contrato_firmado,
                'joined_at': p.create_date.strftime('%Y-%m-%d') if p.create_date else '',
            })
        return result

    # ── Activar actor ───────────────────────────────────────────────────────
    def action_activar(self):
        for r in self:
            r.write({
                'status': 'ACTIVO',
                'activated_at': datetime.now(),
            })

    # ── Validación IBAN básica ──────────────────────────────────────────────
    @api.constrains('banco_iban')
    def _check_iban(self):
        for r in self:
            if r.banco_iban and not r.banco_iban.upper().startswith('ES'):
                raise ValidationError(
                    f"IBAN inválido para actor {r.name}: debe empezar por ES (IBAN español)."
                )
