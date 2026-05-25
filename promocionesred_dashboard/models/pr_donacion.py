# -*- coding: utf-8 -*-
# ── PREMIOSRED — Modelo pr.donacion (Acumuladores mensuales 5 causas) ────
# Vault 40.04 FONDO-DONACIONES — 2% por pack vendido (paga REDROYAL SL)
# Marco fiscal: Ley de Mecenazgo 49/2002 — deducción IS 35-40%
# 5 causas x 0,40% cada una — el usuario elige en el checkout
# Operativa: 5 transferencias SEPA mensuales (una por causa)
from odoo import models, fields, api


class PrDonacion(models.Model):
    _name = 'pr.donacion'
    _description = 'Acumulador mensual de donaciones PremiosRed (5 causas)'
    _order = 'periodo desc'
    _rec_name = 'display_name'

    # ── Periodo ──────────────────────────────────────────────────────────────
    periodo      = fields.Date(
        'Periodo (mes)',
        required=True,
        help='Primer dia del mes de acumulacion (ej: 2026-01-01 para enero 2026)'
    )
    display_name = fields.Char(
        'Periodo (texto)',
        compute='_compute_display',
        store=True
    )

    # ── Acumuladores por causa (Vault 40.04 — 5 causas x 0,40%) ─────────────
    # CAUSA 1 — Lucha contra el Cancer (AECC) — POR DEFECTO
    total_aecc       = fields.Float(
        'AECC — Lucha contra el Cancer (EUR)',
        digits=(12, 4), default=0.0
    )
    # CAUSA 2 — Accion Social
    total_caritas    = fields.Float(
        'Caritas Espanola — Accion Social (EUR)',
        digits=(12, 4), default=0.0
    )
    # CAUSA 3 — Lucha contra el Hambre
    total_manos      = fields.Float(
        'Manos Unidas — Hambre (EUR)',
        digits=(12, 4), default=0.0
    )
    # CAUSA 4 — Emergencias Humanitarias
    total_cruz_roja  = fields.Float(
        'Cruz Roja Espanola — Emergencias (EUR)',
        digits=(12, 4), default=0.0
    )
    # CAUSA 5 — Fe / Comunidad Espiritual
    total_episcopal  = fields.Float(
        'Iglesia Episcopal Espanola — Fe/Comunidad (EUR)',
        digits=(12, 4), default=0.0
    )

    # ── Totales ──────────────────────────────────────────────────────────────
    total_general    = fields.Float(
        'Total donado (EUR)',
        compute='_compute_total',
        store=True,
        digits=(12, 4)
    )
    num_cupones      = fields.Integer('Cupones del periodo', default=0)

    # ── Estado SEPA ──────────────────────────────────────────────────────────
    sepa_enviado     = fields.Boolean(
        'SEPA enviado',
        default=False,
        help='True cuando las 5 transferencias SEPA del Dia 6 han sido ejecutadas'
    )
    sepa_fecha       = fields.Date('Fecha transferencia SEPA')
    notas            = fields.Text('Notas operativas')

    # ── Computed ─────────────────────────────────────────────────────────────
    @api.depends('periodo')
    def _compute_display(self):
        import calendar
        meses_es = [
            '', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ]
        for r in self:
            if r.periodo:
                r.display_name = "%s %s" % (meses_es[r.periodo.month], r.periodo.year)
            else:
                r.display_name = 'Sin periodo'

    @api.depends(
        'total_aecc', 'total_caritas', 'total_manos',
        'total_cruz_roja', 'total_episcopal'
    )
    def _compute_total(self):
        for r in self:
            r.total_general = (
                r.total_aecc + r.total_caritas + r.total_manos
                + r.total_cruz_roja + r.total_episcopal
            )

    # ── ORM: obtener o crear registro del mes actual ──────────────────────────
    @api.model
    def get_or_create_periodo(self, anio, mes):
        """Obtiene o crea el acumulador del periodo dado."""
        import datetime
        fecha = datetime.date(anio, mes, 1)
        registro = self.search([('periodo', '=', fecha)], limit=1)
        if not registro:
            registro = self.create({'periodo': fecha})
        return registro

    # ── ORM: acumular donacion de un cupon ───────────────────────────────────
    @api.model
    def acumular_donacion(self, causa, importe_eur, anio=None, mes=None):
        """
        Suma la donacion de un cupon al acumulador mensual.
        Llamado desde pr.cupon.create() tras generar el hash.
        """
        import datetime
        hoy = datetime.date.today()
        registro = self.get_or_create_periodo(anio or hoy.year, mes or hoy.month)
        campo_mapa = {
            'aecc':      'total_aecc',
            'caritas':   'total_caritas',
            'manos':     'total_manos',
            'cruz_roja': 'total_cruz_roja',
            'episcopal': 'total_episcopal',
        }
        campo = campo_mapa.get(causa, 'total_aecc')
        nuevo_valor = getattr(registro, campo) + importe_eur
        registro.write({
            campo: nuevo_valor,
            'num_cupones': registro.num_cupones + 1,
        })
        return registro.id

    # ── Datos para JS ────────────────────────────────────────────────────────
    @api.model
    def get_donaciones_data(self, limit=12):
        """Devuelve los ultimos N periodos para el panel de donaciones."""
        registros = self.search([], limit=limit)
        result = []
        for r in registros:
            result.append({
                'id': r.id,
                'periodo': r.periodo.isoformat() if r.periodo else '',
                'display_name': r.display_name,
                'total_aecc': r.total_aecc,
                'total_caritas': r.total_caritas,
                'total_manos': r.total_manos,
                'total_cruz_roja': r.total_cruz_roja,
                'total_episcopal': r.total_episcopal,
                'total_general': r.total_general,
                'num_cupones': r.num_cupones,
                'sepa_enviado': r.sepa_enviado,
                'sepa_fecha': r.sepa_fecha.isoformat() if r.sepa_fecha else '',
            })
        return result

    @api.model
    def get_donaciones_stats(self):
        """KPIs globales de donaciones para el Dashboard."""
        todos = self.search([])
        return {
            'total_historico': sum(r.total_general for r in todos),
            'total_aecc': sum(r.total_aecc for r in todos),
            'total_caritas': sum(r.total_caritas for r in todos),
            'total_manos': sum(r.total_manos for r in todos),
            'total_cruz_roja': sum(r.total_cruz_roja for r in todos),
            'total_episcopal': sum(r.total_episcopal for r in todos),
            'periodos_pendientes_sepa': len(todos.filtered(lambda r: not r.sepa_enviado)),
        }
