# -*- coding: utf-8 -*-
from odoo import api, fields, models


class RedlmcCompanyLicense(models.Model):
    """
    Licencias SaaS registradas en una empresa del sistema.

    Modelo diseñado específicamente para la sección "Licencias" del
    formulario de empresa (res.company), equivalente a la sección
    "Ramas" que muestra las sucursales.

    Caso de uso principal:
      REDROYAL SL (empresa ID=2) tiene una licencia SaaS contratada
      con REDLMC SL → se registra aquí con todos los datos comerciales
      y técnicos (tenant code, API Key, cuota, contrato de referencia).

    Relaciones clave:
      - company_id      → La empresa que TIENE la licencia (ej: REDROYAL SL)
      - provider_id     → La empresa que OTORGA la licencia (ej: REDLMC SL)
      - contract_ref    → Referencia al contrato firmado (ej: 30.05)

    Base legal:
      Contrato SaaS 30.05 REDLMC SL → REDROYAL SL
      Factura RL-2026-001 (primera mensualidad)

    Ref: SKILL-GRUPO-EMPRESARIAL.md §5 · 80.05 BRIEF-DEV · 60.01 MODELO-FINANCIERO
    """
    _name = 'redlmc.company.license'
    _description = 'Licencia SaaS registrada en una empresa'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'company_id, license_status, date_start desc'
    _rec_name = 'name'

    # ---- Empresa titular de la licencia ----
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Empresa titular',
        required=True,
        ondelete='cascade',
        help='Empresa que tiene contratada esta licencia.',
    )

    # ---- Proveedor / Licenciante ----
    provider_id = fields.Many2one(
        comodel_name='res.partner',
        string='Proveedor de la licencia',
        help=(
            'Empresa que otorga la licencia. '
            'Ej: REDLMC SL (B26946525) para la licencia SaaS PremiosRed.'
        ),
    )

    provider_company_id = fields.Many2one(
        comodel_name='res.company',
        string='Empresa proveedora (intra-grupo)',
        help=(
            'Si el proveedor es también una empresa de este Odoo, '
            'vincularla aquí. Ej: REDLMC SL (empresa ID=1).'
        ),
    )

    # ---- Identificación de la licencia ----
    name = fields.Char(
        string='Nombre de la licencia',
        required=True,
        help='Nombre descriptivo. Ej: "SaaS PremiosRed — REDLMC SL"',
    )

    license_type = fields.Selection(
        selection=[
            ('saas_premiosred', 'SaaS PremiosRed (instancia completa)'),
            ('saas_white',      'SaaS White-Label (marca propia)'),
            ('basic',           'Básica (módulos core)'),
            ('professional',    'Profesional (core + extras)'),
            ('enterprise',      'Enterprise (suite completa + soporte)'),
            ('software',        'Software de terceros'),
            ('tool',            'Herramienta / SaaS externo'),
        ],
        string='Tipo de licencia',
        required=True,
        default='saas_premiosred',
    )

    tenant_code = fields.Char(
        string='Código de tenant',
        size=32,
        copy=False,
        help=(
            'Identificador único del tenant en la plataforma. '
            'Ej: REDROYAL. Usado como discriminador en las ir.rule '
            'multi-tenant y en la URL del API.'
        ),
    )

    api_key = fields.Char(
        string='API Key',
        copy=False,
        groups='base.group_system',
        help=(
            'Clave de autenticación para el acceso a los endpoints REST '
            '/api/premiosred/v1/. Solo visible para administradores.'
        ),
    )

    # ---- Referencia contractual ----
    contract_ref = fields.Char(
        string='Referencia del contrato',
        help='Número del contrato firmado. Ej: 30.05 (CONTRATO-SAAS-REDLMC-REDROYAL)',
    )

    contract_signed = fields.Boolean(
        string='Contrato firmado',
        default=False,
        help='Marcar cuando el contrato esté físicamente firmado por ambas partes.',
    )

    invoice_ref = fields.Char(
        string='Primera factura emitida',
        help='Referencia de la primera factura de la licencia. Ej: RL-2026-001',
    )

    # ---- Vigencia ----
    date_start = fields.Date(
        string='Fecha de inicio',
        required=True,
    )

    date_end = fields.Date(
        string='Fecha de fin',
        help='Dejar vacío si es indefinida o auto-renovable anualmente.',
    )

    auto_renew = fields.Boolean(
        string='Renovación automática',
        default=True,
        help='La licencia se renueva automáticamente al vencer.',
    )

    # ---- Estado ----
    license_status = fields.Selection(
        selection=[
            ('draft',     'Borrador'),
            ('pending',   'Pendiente de firma'),
            ('active',    'Activa'),
            ('suspended', 'Suspendida'),
            ('expired',   'Expirada'),
            ('cancelled', 'Cancelada'),
        ],
        string='Estado',
        default='draft',
        required=True,
    )

    # ---- Condiciones económicas ----
    monthly_fee = fields.Float(
        string='Cuota mensual (€ sin IVA)',
        digits=(10, 2),
        help=(
            'Base imponible mensual del contrato SaaS.\n'
            'Ej: 619,83€ + 21% IVA = 750,00€/mes total.\n'
            'La factura la emite REDLMC SL a REDROYAL SL el día 1 de cada mes.'
        ),
    )

    annual_fee = fields.Float(
        string='Cuota anual (€ sin IVA)',
        compute='_compute_annual_fee',
        store=True,
        help='monthly_fee × 12 (referencia, no incluye posibles descuentos por pago anual).',
    )

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
        default=lambda self: self.env.ref('base.EUR'),
        required=True,
    )

    @api.depends('monthly_fee')
    def _compute_annual_fee(self):
        for rec in self:
            rec.annual_fee = rec.monthly_fee * 12

    # ---- Alertas de vencimiento ----
    days_to_expiry = fields.Integer(
        string='Días hasta vencimiento',
        compute='_compute_days_to_expiry',
        store=False,
    )

    is_expiring_soon = fields.Boolean(
        string='Vence pronto',
        compute='_compute_days_to_expiry',
        store=False,
        help='True si vence en menos de 30 días.',
    )

    @api.depends('date_end')
    def _compute_days_to_expiry(self):
        import datetime
        today = datetime.date.today()
        for rec in self:
            if rec.date_end:
                delta = (rec.date_end - today).days
                rec.days_to_expiry = delta
                rec.is_expiring_soon = delta < 30
            else:
                rec.days_to_expiry = 9999
                rec.is_expiring_soon = False

    # ---- Notas ----
    notes = fields.Html(
        string='Notas y condiciones especiales',
        help='Condiciones SLA, limitaciones de uso, historial de renovaciones, etc.',
        sanitize=True,
    )


class ResCompany(models.Model):
    """
    Extiende res.company con la relación One2many hacia las licencias
    registradas. Sección "🔑 Licencias" en el formulario de empresa,
    análoga a la sección "Ramas" (child_ids).

    Smart button con contador en la cabecera del formulario.
    Acción de apertura con contexto pre-rellenado (company_id = empresa actual).

    Deployment note:
      El módulo es auto-contenido. No hay IDs hardcodeados.
      Al instalar en un servidor limpio, la tabla redlmc_company_license
      se crea vacía. El admin registra la licencia manualmente desde el
      smart button o desde Ajustes → Licencias SaaS.
    """
    _inherit = 'res.company'

    redlmc_license_ids = fields.One2many(
        comodel_name='redlmc.company.license',
        inverse_name='company_id',
        string='Licencias SaaS',
        help='Licencias de software contratadas por esta empresa.',
    )

    redlmc_license_count = fields.Integer(
        string='Nº de licencias',
        compute='_compute_redlmc_license_count',
        store=True,      # store=True → no recalcula en cada render del smart button
    )

    @api.depends('redlmc_license_ids')
    def _compute_redlmc_license_count(self):
        for rec in self:
            rec.redlmc_license_count = len(rec.redlmc_license_ids)

    def action_open_licenses(self):
        """
        Acción del smart button de Licencias en el formulario de empresa.
        Abre la lista filtrada de licencias de esta empresa, con el
        company_id pre-rellenado en el contexto para facilitar el alta.

        Deployment note:
          Este método funciona en cualquier instalación porque usa
          self.id (ID dinámico), no un ID hardcodeado.
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Licencias — {self.name}',
            'res_model': 'redlmc.company.license',
            'view_mode': 'list,form',
            'domain': [('company_id', '=', self.id)],
            'context': {
                'default_company_id': self.id,
                # Pre-rellena el proveedor si la empresa actual es REDROYAL
                # y existe REDLMC como empresa en el sistema
            },
            'target': 'current',
        }
