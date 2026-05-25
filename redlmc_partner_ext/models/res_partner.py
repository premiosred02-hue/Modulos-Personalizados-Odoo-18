# -*- coding: utf-8 -*-
import secrets
from odoo import api, fields, models


class RedlmcActorRole(models.Model):
    _name = 'redlmc.actor.role'
    _description = 'Roles de PremiosRed'

    name = fields.Char(string='Nombre del Rol', required=True, translate=True)
    code = fields.Char(string='Código Interno', help='Ej: col, sub, ccp, com, ase, usu_qr, usu_gen')
    commission_pct = fields.Float(string='% Comisión Estándar', default=0.0)
    excludes_from_draw = fields.Boolean(string='Excluye del Sorteo', default=True, help="Si se marca, el actor queda excluido del sorteo (Ej: Actores B2B).")
    active = fields.Boolean(default=True)


class ResPartner(models.Model):
    """
    Extiende res.partner con secciones del modelo de negocio REDLMC/PremiosRed:

    1. TAB "Licencias SaaS"
       Relación contractual REDLMC → cliente tenant.
       API Key segura para los endpoints REST /api/premiosred/v1/.

    2. TAB "Sub-colaboradores" (solo si is_company=True / tipo Empresa)
       COL (punto de venta) → lista de SUBs vinculados con datos fiscales.

    3. SECCIÓN "Red Comercial PremiosRed" (cabecera del formulario)
       Clasifica al partner en uno de los roles de la red usando redlmc.actor.role.
       Incluye:
       - Exclusión automática del sorteo
       - Zona geográfica + URL del QR fijo para el COL
       - Acumulador de comisiones
       - Seguimiento avanzado de Usuarios QR

    Ref: SKILL-GRUPO-EMPRESARIAL.md §3 · 60.03 CASH-SWEEP.md · Split 55/45
    """
    _inherit = 'res.partner'

    # =========================================================
    #  CAMPO DISCRIMINADOR — PROVEEDOR VS CLIENTE REDLMC
    #  Controla la visibilidad de las secciones REDLMC en la vista.
    #  No usamos supplier_rank/customer_rank porque requieren
    #  los módulos sale/purchase que pueden no estar instalados.
    #
    #  Regla de negocio:
    #    redlmc_is_supplier = True  → proveedor de servicios (OpenAI, Hetzner, etc.)
    #                                  → oculta secciones REDLMC en su formulario
    #    redlmc_is_supplier = False → cliente / actor de la red / contacto neutral
    #                                  → muestra secciones REDLMC normalmente
    #
    #  El campo se activa MANUALMENTE en el formulario del proveedor.
    #  Se puede marcar al crear el proveedor para que quede limpio.
    # =========================================================

    redlmc_is_supplier = fields.Boolean(
        string='Es proveedor externo',
        default=False,
        help=(
            'Marcar para proveedores de servicios externos (ej: OpenAI, Hetzner, '
            'gestoría, banco). Al activar, se ocultan las secciones de Red Comercial '
            'PremiosRed en este formulario, dejando la vista original de Odoo 18.\n\n'
            'NO marcar para: COLs, SUBs, CCPs, patrocinadores, tenants SaaS ni '
            'contactos de la red aunque hagan alguna compra puntual.'
        ),
        index=True,
    )

    # =========================================================
    #  BLOQUE A — ROL EN LA RED COMERCIAL PREMIOSRED
    #  (visible en la parte superior del formulario — antes de las tabs)
    # =========================================================

    redlmc_actor_role_id = fields.Many2one(
        comodel_name='redlmc.actor.role',
        string='Rol PremiosRed',
        index=True,
        help='Rol dinámico del actor en la red PremiosRed (Permite añadir nuevos roles).'
    )

    redlmc_actor_type = fields.Char(
        string='Código de Rol',
        related='redlmc_actor_role_id.code',
        store=True,
        readonly=True,
        index=True,
        help='Mantiene compatibilidad con vistas XML que dependen del código.'
    )

    redlmc_actor_code = fields.Char(
        string='Código de actor',
        size=16,
        copy=False,
        index=True,
        help=(
            'Código único en la plataforma. Formato:\n'
            '  COL-001, SUB-042, CCP-003, COM-001, ASE-007\n'
            'Se usa en la URL del QR y como referencia en el SEPA PAIN.001.'
        ),
    )

    redlmc_actor_status = fields.Selection(
        selection=[
            ('draft',     'Pendiente de alta'),
            ('active',    'Activo'),
            ('suspended', 'Suspendido'),
            ('inactive',  'Baja definitiva'),
        ],
        string='Estado en la red',
        default='draft',
        help='Estado contractual del actor en la red PremiosRed.',
    )

    redlmc_actor_contract_date = fields.Date(
        string='Fecha de firma del contrato',
        help='Fecha en que se firmó el contrato de agencia mercantil.',
    )

    # ---- Exclusión automática del sorteo ----
    redlmc_excluded_from_draw = fields.Boolean(
        string='Excluido del sorteo',
        compute='_compute_redlmc_excluded_from_draw',
        store=True,
        help=(
            'TRUE automáticamente si el partner tiene un rol activo en la '
            'red comercial (COL, SUB, CCP, COM, ASE).\n'
            'Base legal: Art. 8 Bases Legales v2.1 PremiosRed 2026.\n'
            'REDROYAL SL está obligada a mantener esta exclusión en la BBDD '
            'para garantizar la validez del sorteo ante notario (22/12/2026).'
        ),
    )

    @api.depends('redlmc_actor_role_id', 'redlmc_is_col')
    def _compute_redlmc_excluded_from_draw(self):
        for rec in self:
            rec.redlmc_excluded_from_draw = (
                (rec.redlmc_actor_role_id and rec.redlmc_actor_role_id.excludes_from_draw)
                or rec.redlmc_is_col
            )

    # ---- Comisiones acumuladas (base AML + SEPA) ----
    redlmc_commission_pct = fields.Float(
        string='% Comisión estándar',
        digits=(5, 2),
        help=(
            'Porcentaje de comisión sobre el pool del 45% según rol:\n'
            '  COL: 20.0%  |  SUB: 25.0%  |  CCP: 3.0%\n'
            '  COM: 2.0%   |  ASE: 2.0%\n'
            'Se puede personalizar por actor si hay acuerdo especial.'
        ),
    )

    redlmc_commission_ytd = fields.Float(
        string='Comisiones acumuladas en el año (€)',
        digits=(10, 2),
        readonly=True,
        default=0.0,
        help=(
            'Suma de todas las liquidaciones SEPA ejecutadas este año.\n'
            'Actualizado automáticamente en cada Cash Sweep del Día 6.\n'
            '⚠️ AML: Si supera 36.000€/año (3.000€/mes promedio) → '
            'revisión documental obligatoria (Ley 10/2010).'
        ),
    )

    redlmc_commission_pending = fields.Float(
        string='Comisión acumulada pendiente de pago (€)',
        digits=(10, 2),
        readonly=True,
        default=0.0,
        help=(
            'Importe acumulado que aún no alcanza el mínimo SEPA de 50€.\n'
            'Se suma automáticamente al próximo Cash Sweep.'
        ),
    )

    redlmc_aml_alert = fields.Boolean(
        string='⚠️ Alerta AML activa',
        compute='_compute_redlmc_aml_alert',
        store=False,
        help='Activo si las comisiones YTD superan 3.000€/mes × meses transcurridos.',
    )

    @api.depends('redlmc_commission_ytd')
    def _compute_redlmc_aml_alert(self):
        import datetime
        current_month = datetime.date.today().month or 1
        for rec in self:
            monthly_avg = rec.redlmc_commission_ytd / current_month
            rec.redlmc_aml_alert = monthly_avg > 3000.0

    # ---- Zona geográfica + QR (solo para COL) ----
    redlmc_col_locality = fields.Char(
        string='Localidad del punto de venta',
        help='Ciudad o localidad donde está ubicado el local COL.',
    )

    redlmc_col_province_id = fields.Many2one(
        comodel_name='res.country.state',
        string='Provincia',
        domain=[('country_id.code', '=', 'ES')],
        help='Provincia española del punto de venta.',
    )

    redlmc_col_postal_code = fields.Char(
        string='Código postal',
        size=5,
        help='CP del local. Usado para la geolocalización del QR.',
    )

    redlmc_qr_url = fields.Char(
        string='URL del QR fijo',
        compute='_compute_redlmc_qr_url',
        store=True,
        help=(
            'URL única del QR del punto de venta.\n'
            'Formato: https://premiosred.com/q/{actor_code}\n'
            'Se genera automáticamente al asignar el código de actor.'
        ),
    )

    @api.depends('redlmc_actor_code', 'redlmc_actor_type')
    def _compute_redlmc_qr_url(self):
        for rec in self:
            if rec.redlmc_actor_code and rec.redlmc_actor_type == 'col':
                rec.redlmc_qr_url = (
                    f'https://premiosred.com/q/{rec.redlmc_actor_code}'
                )
            else:
                rec.redlmc_qr_url = False

    # ---- Onchange: rellena % comisión estándar según el rol ----
    @api.onchange('redlmc_actor_role_id')
    def _onchange_redlmc_actor_role_id(self):
        if self.redlmc_actor_role_id:
            self.redlmc_commission_pct = self.redlmc_actor_role_id.commission_pct
            if self.redlmc_actor_role_id.code == 'col':
                self.redlmc_is_col = True
        else:
            self.redlmc_commission_pct = 0.0

    # =========================================================
    #  SEGUIMIENTO USUARIOS QR
    # =========================================================
    redlmc_qr_scanned_date = fields.Datetime(
        string='Fecha Captó QR', 
        help='Momento en el que el usuario escaneó el código QR.'
    )
    redlmc_qr_filled_data = fields.Boolean(
        string='Rellenó Email y Teléfono', 
        default=False,
        help='El usuario proporcionó sus datos de contacto.'
    )
    redlmc_qr_opened_whatsapp = fields.Boolean(
        string='Abrió WhatsApp', 
        default=False,
        help='El usuario abrió el enlace de WhatsApp para reclamar su regalo.'
    )
    redlmc_qr_accepted_gift = fields.Boolean(
        string='Aceptó Regalo Directo', 
        default=False,
        help='El usuario decidió aceptar el regalo/cupón directo.'
    )
    redlmc_qr_bought_pack = fields.Boolean(
        string='Compró Pack', 
        default=False,
        help='El usuario finalizó el flujo y compró un pack de 6€.'
    )

    # =========================================================
    #  DATOS BANCARIOS Y KYB (ONBOARDING)
    # =========================================================
    redlmc_iban = fields.Char(
        string='IBAN para comisiones',
        help='Número de cuenta bancaria para liquidaciones SEPA.'
    )
    redlmc_contract_signed = fields.Boolean(
        string='Contrato Firmado',
        default=False,
        help='Indica si el actor ha firmado y adjuntado el contrato de agencia mercantil.'
    )
    redlmc_kyb_estado = fields.Selection(
        selection=[
            ('pendiente', 'Pendiente de Revisión'),
            ('aprobado', 'KYB Aprobado'),
            ('rechazado', 'KYB Rechazado'),
        ],
        string='Estado KYB',
        default='pendiente',
        help='Estado de la verificación de documentos (Conoce a tu Negocio).'
    )
    
    # Documentos KYB (Relaciones directas al adjunto para fácil acceso)
    redlmc_kyb_dni_front = fields.Many2one('ir.attachment', string='DNI Anverso')
    redlmc_kyb_dni_back = fields.Many2one('ir.attachment', string='DNI Reverso')
    redlmc_kyb_cif = fields.Many2one('ir.attachment', string='CIF Empresa')
    redlmc_kyb_reta = fields.Many2one('ir.attachment', string='Alta RETA')
    redlmc_kyb_aeat = fields.Many2one('ir.attachment', string='Certificado AEAT')
    redlmc_kyb_ss = fields.Many2one('ir.attachment', string='Certificado SS')
    redlmc_kyb_iban_cert = fields.Many2one('ir.attachment', string='Certificado IBAN')
    redlmc_kyb_ubo = fields.Many2one('ir.attachment', string='Declaración UBO')
    redlmc_kyb_auth_col = fields.Many2one('ir.attachment', string='Autorización COL')
    redlmc_kyb_foto_local = fields.Many2one('ir.attachment', string='Foto Local')
    redlmc_kyb_contrato = fields.Many2one('ir.attachment', string='Contrato Firmado PDF')

    # =========================================================
    #  ACCESO PORTAL / DASHBOARD EXTERNO
    # =========================================================

    redlmc_api_key = fields.Char(
        string='API Key',
        copy=False,
        help=(
            'Clave de autenticación para el acceso al Dashboard externo.\n'
            'Usar el botón "Generar" para renovar. La key anterior\n'
            'queda invalidada inmediatamente.'
        ),
    )

    redlmc_saas_license_key = fields.Char(
        string='SaaS License API Key',
        help='Clave de Licencia de Uso para operar en el ecosistema REDLMC',
        copy=False
    )
    redlmc_portal_username = fields.Char(
        string='Usuario Portal',
        help='Nombre de usuario para acceso al portal externo (suele ser el email)'
    )
    redlmc_portal_password = fields.Char(
        string='Clave Portal',
        help='Clave temporal de acceso al portal externo'
    )

    redlmc_api_key_date = fields.Datetime(
        string='Fecha de generación de la API Key',
        readonly=True,
        help='Cuándo se generó o renovó la API Key por última vez.',
    )

    # =========================================================
    #  TAB 2 — SUB-COLABORADORES (solo si is_company=True)
    # =========================================================

    redlmc_is_col = fields.Boolean(
        string='Es punto de venta COL',
        default=False,
        help=(
            'Marcar si este partner actúa como Colaborador (COL):\n'
            'local físico que expone el QR y vende packs de 6€.\n'
            'Al activar, se muestra la lista de SUBs vinculados.'
        ),
    )

    redlmc_col_code = fields.Char(
        string='Código COL (legacy)',
        size=16,
        copy=False,
        help='Código heredado. Usar "Código de actor" en el nuevo sistema.',
    )

    redlmc_col_commission_pct = fields.Float(
        string='% Comisión COL (sobre 45%)',
        default=20.0,
        help=(
            'Del pool del 45% de la venta de 6€, el porcentaje\n'
            'que recibe el propio COL como punto de venta fijo.\n'
            'Ejemplo: COL 20% + SUB 25% = 45% pool actores.'
        ),
    )

    redlmc_sub_ids = fields.One2many(
        comodel_name='redlmc.col.sub',
        inverse_name='col_partner_id',
        string='Sub-colaboradores (SUBs)',
        help='Personas físicas que venden bajo el paraguas de este COL.',
    )

    redlmc_store_ids = fields.One2many(
        comodel_name='redlmc.store',
        inverse_name='col_id',
        string='Tiendas y Sucursales',
        help='Locales físicos pertenecientes a esta Empresa Colaboradora.',
    )

    redlmc_dashboard_url = fields.Char(
        string='Acceso Dashboard Externo',
        compute='_compute_dashboard_url',
        help='Enlace seguro para que el actor acceda a su panel de control en PromocionesRed Portal.'
    )

    redlmc_invitation_url = fields.Char(
        string='URL de Invitación (Onboarding)',
        compute='_compute_redlmc_invitation_url',
        help='Enlace único para que este actor invite a su red (ej: un COL invita a sus SUBs).'
    )

    @api.depends('redlmc_api_key', 'redlmc_actor_code')
    def _compute_dashboard_url(self):
        # Obtain base URL from System Parameters, default to localhost:3000 for development
        base_url = self.env['ir.config_parameter'].sudo().get_param('redlmc.portal_url', 'http://localhost:3000')
        for rec in self:
            if rec.redlmc_api_key:
                rec.redlmc_dashboard_url = f"{base_url}/auth/login?token={rec.redlmc_api_key}"
            elif rec.redlmc_actor_code:
                rec.redlmc_dashboard_url = f"{base_url}/auth/login?actor={rec.redlmc_actor_code}"
            else:
                rec.redlmc_dashboard_url = False

    @api.depends('redlmc_actor_code')
    def _compute_redlmc_invitation_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('redlmc.portal_url', 'http://localhost:3000')
        for rec in self:
            if rec.redlmc_actor_code:
                rec.redlmc_invitation_url = f"{base_url}/onboarding?sponsor={rec.redlmc_actor_code}"
            else:
                rec.redlmc_invitation_url = False

    redlmc_sub_count = fields.Integer(
        string='Nº de SUBs',
        compute='_compute_redlmc_sub_count',
        store=True,
    )

    @api.depends('redlmc_sub_ids')
    def _compute_redlmc_sub_count(self):
        for rec in self:
            rec.redlmc_sub_count = len(rec.redlmc_sub_ids)

    # =========================================================
    #  ACCIONES
    # =========================================================

    def action_generate_api_key(self):
        """Genera una API Key segura de ~40 caracteres y registra la fecha."""
        for rec in self:
            rec.redlmc_api_key = secrets.token_urlsafe(30)
            rec.redlmc_api_key_date = fields.Datetime.now()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'API Key generada',
                'message': (
                    'La nueva clave ha sido generada. '
                    'Guarda el registro para confirmarla.'
                ),
                'type': 'success',
                'sticky': False,
            },
        }

    def action_open_dashboard_url(self):
        """Redirige al usuario al dashboard externo abriendo la URL calculada."""
        self.ensure_one()
        if self.redlmc_dashboard_url:
            return {
                'type': 'ir.actions.act_url',
                'url': self.redlmc_dashboard_url,
                'target': 'new',
            }
