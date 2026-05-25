# -*- coding: utf-8 -*-
from odoo import fields, models


class RedlmcColSub(models.Model):
    """
    Registro de la relación COL → SUB en el modelo comercial PremiosRed.

    Cada SUB (Sub-colaborador / vendedor itinerante) está vinculado a
    exactamente un COL (punto de venta fijo). El SUB recibe una comisión
    del 25% por venta que realice con su QR móvil personal.

    Datos fiscales incluidos para:
    - Generación de XML SEPA PAIN.001 (transferencia bancaria día 6)
    - Modelo 111 (retenciones IRPF si el SUB es autónomo)
    - Modelo 190 (resumen anual retenciones)
    - Prevención Blanqueo de Capitales: alerta si comisiones > 3.000€/mes

    Ref: SKILL-GRUPO-EMPRESARIAL.md §3 · 60.03 CASH-SWEEP.md · 80.05 §B1
    """
    _name = 'redlmc.col.sub'
    _description = 'Sub-colaborador (SUB) vinculado a un punto de venta COL'
    _order = 'col_partner_id, status, name'
    _rec_name = 'name'

    # ---- Relación COL ----
    col_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='COL (Punto de venta)',
        required=True,
        ondelete='cascade',
        domain=[('is_company', '=', True)],
        help='Empresa/local COL al que está vinculado este SUB.',
    )

    store_id = fields.Many2one(
        comodel_name='redlmc.store',
        string='Tienda asignada',
        domain="[('col_id', '=', col_partner_id)]",
        help='Opcional. Tienda física del COL donde trabaja este SUB.',
    )

    # ---- Datos del SUB ----
    sub_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Persona (Persona Física)',
        required=True,
        domain=[('is_company', '=', False)],
        help='Persona física que actúa como SUB. '
             'Debe ser tipo "Persona Física" en Contactos.',
    )

    name = fields.Char(
        string='Nombre SUB',
        related='sub_partner_id.name',
        store=True,
        readonly=True,
    )

    sub_code = fields.Char(
        string='Código SUB',
        size=16,
        copy=False,
        help='Código único del SUB (ej: SUB-001). Usado en liquidaciones y QR móvil.',
    )

    # ---- Estado contractual ----
    status = fields.Selection(
        selection=[
            ('draft',     'Pendiente de activación'),
            ('active',    'Activo'),
            ('suspended', 'Suspendido'),
            ('inactive',  'Baja'),
        ],
        string='Estado',
        default='draft',
        required=True,
    )

    contract_date = fields.Date(
        string='Fecha de firma del contrato',
        help='Fecha en que el SUB firmó el contrato de agencia mercantil.',
    )

    qr_mobile_active = fields.Boolean(
        string='QR móvil activado',
        default=False,
        help='El QR personal del SUB está activado y operativo.',
    )

    # ---- Comisiones ----
    commission_pct = fields.Float(
        string='% Comisión SUB',
        default=25.0,
        digits=(5, 2),
        help='Porcentaje que recibe el SUB del pool del 45% de actores. '
             'Ejemplo estándar: SUB = 25%, COL = 20%. '
             'El total COL+SUB no debe superar el 45%.',
    )

    # ---- Datos fiscales (Modelo 111 / SEPA) ----
    nif = fields.Char(
        string='NIF / DNI / NIE',
        help='Número de identificación fiscal. Obligatorio para el Modelo 111.',
    )

    iban = fields.Char(
        string='IBAN (transferencia SEPA)',
        help='Cuenta bancaria destino para el Cash Sweep del día 6. '
             'Formato: ES00 0000 0000 0000 0000 0000.',
    )

    fiscal_type = fields.Selection(
        selection=[
            ('autonomo',   'Autónomo (factura + IRPF 19%)'),
            ('empresa',    'Empresa (factura sin retención IRPF)'),
            ('particular', 'Particular (no factura — liquidación directa)'),
        ],
        string='Tipo fiscal',
        default='autonomo',
        required=True,
        help='Determina si se aplica retención IRPF 19% (Modelo 111). '
             'Los autónomos tributan como rendimientos de actividad económica. '
             'Los particulares tributan como rendimientos del trabajo (Art. 16 LIRPF).',
    )

    is_irpf_subject = fields.Boolean(
        string='Sujeto a retención IRPF 19%',
        default=True,
        help='Si True, se deduce el 19% de IRPF en cada liquidación '
             'y se incluye en el Modelo 111 trimestral y 190 anual.',
    )

    reta_active = fields.Boolean(
        string='Alta en RETA confirmada',
        default=False,
        help='El SUB ha acreditado su alta en el Régimen Especial de Trabajadores Autónomos. '
             'Obligatorio para cumplir el blindaje laboral (§15.3 BASES-LEGALES).',
    )

    # ---- Control AML ----
    aml_alert = fields.Boolean(
        string='Alerta AML activa',
        default=False,
        compute='_compute_aml_alert',
        store=False,
        help='Se activa si las comisiones del SUB superan 3.000€/mes. '
             'Requiere revisión documental según Ley 10/2010 de Prevención '
             'de Blanqueo de Capitales.',
    )

    monthly_commission_estimated = fields.Float(
        string='Comisión mensual estimada (€)',
        default=0.0,
        digits=(10, 2),
        help='Estimación manual de comisiones mensuales para control AML. '
             'Introducir el promedio mensual estimado.',
    )

    def _compute_aml_alert(self):
        for rec in self:
            rec.aml_alert = rec.monthly_commission_estimated > 3000.0

    # ---- Notas ----
    notes = fields.Text(
        string='Observaciones',
        help='Condiciones especiales, incidencias, historial de actividad.',
    )
