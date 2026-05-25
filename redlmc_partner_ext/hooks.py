# -*- coding: utf-8 -*-
"""
hooks.py — redlmc_partner_ext
──────────────────────────────
post_init_hook  : redirige las vistas kanban/lista de la acción "Clientes"
                  (base.action_partner_customer_form_view1/2) a las vistas
                  dedicadas de REDLMC que incluyen el badge/columna de Rol.

uninstall_hook  : restaura las referencias originales para que Odoo quede
                  en su estado base al desinstalar el módulo.

Por qué hooks y no XML data:
  • Los registros de ir.actions.act_window.view en base tienen restricción
    de unicidad (act_window_view_unique_mode_per_action). Actualizarlos
    vía XML en un módulo distinto no es reversible al desinstalar.
  • Los hooks Python SÍ son reversibles y más explícitos.
"""
import logging

_logger = logging.getLogger(__name__)

# XMLIDs de las vistas dedicadas para Clientes
_KANBAN_VIEW_XMLID = 'redlmc_partner_ext.view_partner_customer_kanban_redlmc'
_LIST_VIEW_XMLID   = 'redlmc_partner_ext.view_partner_customer_list_redlmc'

# XMLIDs originales de base para restaurar al desinstalar
_BASE_KANBAN_XMLID = 'base.res_partner_kanban_view'
_BASE_LIST_XMLID   = 'base.view_partner_tree'

# XMLIDs de los registros act_window.view a modificar
_ACT_KANBAN_XMLID  = 'base.action_partner_customer_form_view1'
_ACT_LIST_XMLID    = 'base.action_partner_customer_form_view2'


def post_init_hook(env):
    """
    Al instalar el módulo: apunta las vistas de la acción Clientes
    a nuestras vistas dedicadas con columna/badge de Rol PremiosRed.
    """
    _logger.info('[REDLMC] post_init_hook: redirigiendo vistas de Clientes...')

    try:
        kanban_view = env.ref(_KANBAN_VIEW_XMLID, raise_if_not_found=False)
        list_view   = env.ref(_LIST_VIEW_XMLID,   raise_if_not_found=False)
        act_kanban  = env.ref(_ACT_KANBAN_XMLID,  raise_if_not_found=False)
        act_list    = env.ref(_ACT_LIST_XMLID,    raise_if_not_found=False)

        if kanban_view and act_kanban:
            act_kanban.view_id = kanban_view
            _logger.info('[REDLMC] Kanban Clientes → %s', _KANBAN_VIEW_XMLID)

        if list_view and act_list:
            act_list.view_id = list_view
            _logger.info('[REDLMC] Lista Clientes   → %s', _LIST_VIEW_XMLID)

    except Exception as exc:
        _logger.warning('[REDLMC] post_init_hook falló (no crítico): %s', exc)


def uninstall_hook(env):
    """
    Al desinstalar el módulo: restaura las referencias originales de base
    para que Odoo vuelva a funcionar normalmente sin nuestro módulo.
    """
    _logger.info('[REDLMC] uninstall_hook: restaurando vistas base de Clientes...')

    try:
        base_kanban = env.ref(_BASE_KANBAN_XMLID, raise_if_not_found=False)
        base_list   = env.ref(_BASE_LIST_XMLID,   raise_if_not_found=False)
        act_kanban  = env.ref(_ACT_KANBAN_XMLID,  raise_if_not_found=False)
        act_list    = env.ref(_ACT_LIST_XMLID,    raise_if_not_found=False)

        if base_kanban and act_kanban:
            act_kanban.view_id = base_kanban
            _logger.info('[REDLMC] Restaurado: Kanban Clientes → %s', _BASE_KANBAN_XMLID)

        if base_list and act_list:
            act_list.view_id = base_list
            _logger.info('[REDLMC] Restaurado: Lista Clientes   → %s', _BASE_LIST_XMLID)

    except Exception as exc:
        _logger.warning('[REDLMC] uninstall_hook falló (no crítico): %s', exc)
