# -*- coding: utf-8 -*-
# PREMIOSRED -- QR Verification Controller + REST API
# Rutas publicas:
#   GET  /verify/<encrypted_id>            -- Portal HTML de validacion (web publica)
#   GET  /api/qr/verify/<encrypted_id>     -- JSON para React.js
#   GET  /api/qr/scan/<encrypted_id>       -- Registrar escaneo + devolver JSON
#   GET  /api/qr/records                   -- Listar todos los registros (auth requerida)
#   POST /api/qr/records                   -- Crear nuevo registro (auth requerida)
#   PUT  /api/qr/records/<id>              -- Actualizar registro (auth requerida)

import json
import hashlib
import datetime
import logging
from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)

# ---- CORS helper para React.js --------------------------------------------
CORS_HEADERS = {
    'Access-Control-Allow-Origin':  '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
    'Content-Type':                 'application/json; charset=utf-8',
}

def _json_response(data, status=200):
    """Helper: devuelve Response JSON con CORS."""
    return Response(
        json.dumps(data, default=str),
        status=status,
        headers=CORS_HEADERS,
    )

def _actor_to_dict(actor):
    """Serializa un pr.actor a dict para la API."""
    return {
        'id':           actor.id,
        'name':         actor.name,
        'col_code':     getattr(actor, 'col_code', '') or '',
        'sub_code':     getattr(actor, 'sub_code', '') or '',
        'sponsor_code': getattr(actor, 'sponsor_code', '') or '',
        'actor_type':   getattr(actor, 'actor_type', '') or '',
        'status':       getattr(actor, 'status', 'Activo') or 'Activo',
        'email':        getattr(actor, 'email', '') or '',
        'phone':        getattr(actor, 'phone', '') or '',
        'encrypted_id': _generate_encrypted_id(actor),
        'scan_count':   getattr(actor, 'scan_count', 0) or 0,
        'qr_url':       _build_qr_url(actor),
    }

def _generate_encrypted_id(actor):
    """Genera SHA-256 identico al frontend JS."""
    seed = f"actor-{actor.id}-{actor.name}"
    return hashlib.sha256(seed.encode('utf-8')).hexdigest()

def _build_qr_url(actor, portal_type=None, label=None):
    """Construye la URL completa del QR."""
    enc_id     = _generate_encrypted_id(actor)
    base_url   = request.httprequest.host_url.rstrip('/')
    url        = f"{base_url}/verify/{enc_id}"
    params     = []
    ptype      = portal_type or getattr(actor, 'portal_type', 'standard') or 'standard'
    lbl        = label or getattr(actor, 'custom_label', '') or 'Sorteo Navidad'
    sub        = getattr(actor, 'sub_code', '') or ''
    spon       = getattr(actor, 'sponsor_code', '') or ''
    if ptype and ptype != 'standard': params.append(f"type={ptype}")
    if lbl:  params.append(f"label={lbl}")
    if sub:  params.append(f"sub={sub}")
    if spon: params.append(f"spon={spon}")
    return f"{url}?{'&'.join(params)}" if params else url


# ==========================================================================
class PrQRController(http.Controller):

    # -----------------------------------------------------------------------
    # 1. PORTAL WEB PUBLICO — /verify/<encrypted_id>
    #    Replica: VerificationPortal.jsx
    # -----------------------------------------------------------------------
    @http.route('/verify/<string:encrypted_id>', type='http', auth='public', website=True, csrf=False)
    def verify_portal(self, encrypted_id, **kwargs):
        """
        Portal publico de validacion. Se abre al escanear el QR.
        Registra el escaneo, detecta el actor y renderiza la pagina.
        """
        portal_type = kwargs.get('type', 'standard')
        label       = kwargs.get('label', 'Verificacion PremiosRed')
        sub_code    = kwargs.get('sub', '')
        spon_code   = kwargs.get('spon', '')

        # Temas igual que VerificationPortal.jsx
        themes = {
            'standard':  {'color': '#111827', 'bg': '#f9fafb', 'icon': 'check'},
            'premium':   {'color': '#2563eb', 'bg': '#eff6ff', 'icon': 'star'},
            'marketing': {'color': '#db2777', 'bg': '#fdf2f8', 'icon': 'bell'},
        }
        theme  = themes.get(portal_type, themes['standard'])
        now_ts = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')

        # Buscar actor por encrypted_id (comparar SHA-256 generado)
        actor_data = None
        try:
            actors = request.env['pr.actor'].sudo().search([])
            for a in actors:
                if _generate_encrypted_id(a) == encrypted_id:
                    actor_data = a
                    # Registrar escaneo si tiene el campo
                    if hasattr(a, 'scan_count'):
                        a.sudo().write({'scan_count': (a.scan_count or 0) + 1})
                    break
        except Exception as e:
            _logger.warning("QR verify actor lookup failed: %s", e)

        values = {
            'encrypted_id': encrypted_id,
            'short_id':     encrypted_id[:24] + '...',
            'portal_type':  portal_type,
            'label':        label,
            'sub_code':     sub_code,
            'spon_code':    spon_code,
            'theme':        theme,
            'now_ts':       now_ts,
            'actor':        actor_data,
            'valid':        actor_data is not None,
        }
        return request.render('promocionesred_dashboard.qr_verify_portal', values)

    # -----------------------------------------------------------------------
    # 2. API REST -- Preflight OPTIONS (CORS para React)
    # -----------------------------------------------------------------------
    @http.route([
        '/api/qr/verify/<string:encrypted_id>',
        '/api/qr/scan/<string:encrypted_id>',
        '/api/qr/records',
        '/api/qr/records/<int:record_id>',
    ], type='http', auth='public', methods=['OPTIONS'], csrf=False)
    def api_options(self, **kwargs):
        return Response('', status=204, headers=CORS_HEADERS)

    # -----------------------------------------------------------------------
    # 3. API -- Verificar QR (GET)
    #    React: await fetch('/api/qr/verify/<id>')
    # -----------------------------------------------------------------------
    @http.route('/api/qr/verify/<string:encrypted_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def api_verify(self, encrypted_id, **kwargs):
        """
        Verifica un QR y devuelve JSON con los datos del actor.
        Sin autenticacion -- publico para la app React.
        """
        try:
            actors = request.env['pr.actor'].sudo().search([])
            for a in actors:
                if _generate_encrypted_id(a) == encrypted_id:
                    return _json_response({
                        'valid':        True,
                        'encrypted_id': encrypted_id,
                        'actor':        _actor_to_dict(a),
                        'portal_url':   _build_qr_url(a),
                        'verified_at':  datetime.datetime.now().isoformat(),
                    })
            return _json_response({
                'valid':        False,
                'encrypted_id': encrypted_id,
                'error':        'QR no encontrado o inactivo',
            }, status=404)
        except Exception as e:
            _logger.error("api_verify error: %s", e)
            return _json_response({'valid': False, 'error': str(e)}, status=500)

    # -----------------------------------------------------------------------
    # 4. API -- Registrar escaneo (GET/POST)
    #    React: await fetch('/api/qr/scan/<id>', {method:'POST'})
    # -----------------------------------------------------------------------
    @http.route('/api/qr/scan/<string:encrypted_id>', type='http', auth='public', methods=['GET', 'POST'], csrf=False)
    def api_register_scan(self, encrypted_id, **kwargs):
        """
        Registra un escaneo y devuelve el actor actualizado.
        Equivalente al StorageManager.registerScan() del React original.
        """
        try:
            ua      = request.httprequest.headers.get('User-Agent', '')
            device  = 'Mobile' if any(m in ua for m in ['Android','iPhone','iPad','Mobile']) else 'PC'
            now_iso = datetime.datetime.now().isoformat()

            actors = request.env['pr.actor'].sudo().search([])
            for a in actors:
                if _generate_encrypted_id(a) == encrypted_id:
                    # Incrementar contador
                    new_count = (getattr(a, 'scan_count', 0) or 0) + 1
                    try:
                        a.sudo().write({'scan_count': new_count})
                    except Exception:
                        pass

                    return _json_response({
                        'registered':   True,
                        'encrypted_id': encrypted_id,
                        'scan_count':   new_count,
                        'device':       device,
                        'scanned_at':   now_iso,
                        'actor':        _actor_to_dict(a),
                    })

            return _json_response({'registered': False, 'error': 'Actor no encontrado'}, status=404)
        except Exception as e:
            _logger.error("api_register_scan error: %s", e)
            return _json_response({'registered': False, 'error': str(e)}, status=500)

    # -----------------------------------------------------------------------
    # 5. API -- Listar registros (GET, auth requerida)
    #    React admin: Authorization: Bearer <odoo_session>
    # -----------------------------------------------------------------------
    @http.route('/api/qr/records', type='http', auth='user', methods=['GET'], csrf=False)
    def api_list_records(self, **kwargs):
        """
        Lista todos los actores con sus QR URLs.
        Requiere sesion Odoo (auth=user).
        Para React admin panel.
        """
        try:
            actors = request.env['pr.actor'].sudo().search([], order='id desc', limit=200)
            data   = [_actor_to_dict(a) for a in actors]
            return _json_response({
                'count':   len(data),
                'records': data,
            })
        except Exception as e:
            return _json_response({'error': str(e)}, status=500)

    # -----------------------------------------------------------------------
    # 6. API -- Crear registro (POST, auth requerida)
    # -----------------------------------------------------------------------
    @http.route('/api/qr/records', type='http', auth='user', methods=['POST'], csrf=False)
    def api_create_record(self, **kwargs):
        """
        Crea un nuevo actor/registro QR.
        Body JSON: {name, col_code, sub_code, sponsor_code, portal_type, custom_label}
        """
        try:
            body = json.loads(request.httprequest.data or '{}')
            actor = request.env['pr.actor'].sudo().create({
                'name':         body.get('name', ''),
                'col_code':     body.get('col_code', ''),
                'sub_code':     body.get('sub_code', ''),
                'sponsor_code': body.get('sponsor_code', ''),
                'status':       body.get('status', 'Activo'),
                'email':        body.get('email', ''),
                'phone':        body.get('phone', ''),
            })
            return _json_response({'created': True, 'record': _actor_to_dict(actor)}, status=201)
        except Exception as e:
            return _json_response({'created': False, 'error': str(e)}, status=400)

    # -----------------------------------------------------------------------
    # 7. API -- Actualizar registro (PUT, auth requerida)
    # -----------------------------------------------------------------------
    @http.route('/api/qr/records/<int:record_id>', type='http', auth='user', methods=['PUT', 'POST'], csrf=False)
    def api_update_record(self, record_id, **kwargs):
        try:
            body  = json.loads(request.httprequest.data or '{}')
            actor = request.env['pr.actor'].sudo().browse(record_id)
            if not actor.exists():
                return _json_response({'error': 'Registro no encontrado'}, status=404)
            fields = {}
            for f in ['name','col_code','sub_code','sponsor_code','status','email','phone']:
                if f in body:
                    fields[f] = body[f]
            if 'reset_scans' in body and body['reset_scans']:
                fields['scan_count'] = 0
            actor.sudo().write(fields)
            return _json_response({'updated': True, 'record': _actor_to_dict(actor)})
        except Exception as e:
            return _json_response({'updated': False, 'error': str(e)}, status=400)

    # -----------------------------------------------------------------------
    # 8. API -- Eliminar registro (DELETE, auth requerida)
    # -----------------------------------------------------------------------
    @http.route('/api/qr/records/<int:record_id>', type='http', auth='user', methods=['DELETE'], csrf=False)
    def api_delete_record(self, record_id, **kwargs):
        try:
            actor = request.env['pr.actor'].sudo().browse(record_id)
            if not actor.exists():
                return _json_response({'error': 'Registro no encontrado'}, status=404)
            actor.sudo().unlink()
            return _json_response({'deleted': True, 'id': record_id})
        except Exception as e:
            return _json_response({'deleted': False, 'error': str(e)}, status=400)

    # -----------------------------------------------------------------------
    # 9. API -- Info del sistema (GET publico, para health check)
    # -----------------------------------------------------------------------
    @http.route('/api/qr/info', type='http', auth='public', methods=['GET'], csrf=False)
    def api_info(self, **kwargs):
        return _json_response({
            'service':  'PremiosRed QR API',
            'version':  '3.0',
            'status':   'operational',
            'endpoints': {
                'verify':        '/api/qr/verify/<encrypted_id>',
                'scan':          '/api/qr/scan/<encrypted_id>',
                'records_list':  '/api/qr/records  [auth]',
                'records_create':'/api/qr/records  [auth, POST]',
                'records_update':'/api/qr/records/<id>  [auth, PUT]',
                'records_delete':'/api/qr/records/<id>  [auth, DELETE]',
                'portal_web':    '/verify/<encrypted_id>',
            },
            'timestamp': datetime.datetime.now().isoformat(),
        })
