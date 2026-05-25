from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, date

class ActorOnboardingWizard(models.TransientModel):
    _name = 'premiosred.onboarding.wizard'
    _description = 'Alta de Actor PremiosRed (KYB)'

    actor_type = fields.Selection([
        ('col', 'COL — Colaborador (Local Físico)'),
        ('sub', 'SUB — Subcolaborador (Vendedor Activo)'),
        ('ccp', 'CCP — Captador Profesional (3%)'),
        ('com', 'COM — Comercial Captador (2%)'),
        ('ase', 'ASE — Asesor Conector (2%)'),
    ], string='Tipo de Actor', required=True, default='col')
    
    step = fields.Integer(default=1)

    # Datos Básicos
    name = fields.Char('Nombre completo o Razón Social')
    nif = fields.Char('NIF / CIF / NIE')
    email = fields.Char('Email')
    phone = fields.Char('Teléfono móvil')
    iban = fields.Char('IBAN para comisiones')
    address = fields.Char('Dirección fiscal')

    # Específicos COL
    local_name = fields.Char('Nombre comercial del local')
    local_type = fields.Selection([
        ('bar', 'Bar / Café'),
        ('restaurant', 'Restaurante'),
        ('retail', 'Tienda / Comercio'),
        ('hotel', 'Hotel'),
        ('salon', 'Peluquería / Estética'),
        ('gym', 'Gimnasio'),
        ('other', 'Otro'),
    ], string='Tipo de Local')
    local_address = fields.Char('Dirección del local')
    local_footfall = fields.Integer('Afluencia diaria estimada')
    
    captador_id = fields.Many2one('res.partner', string='Captador (CCP/COM/ASE)',
        domain="[('redlmc_actor_type','in',['ccp','com','ase']), ('redlmc_actor_status','=','active')]")

    # Específicos SUB
    col_id = fields.Many2one('res.partner', string='COL Vinculado',
        domain="[('redlmc_actor_type','=','col'), ('redlmc_actor_status','=','active')]")
    is_company = fields.Boolean('Es Empresa / Alta RETA', default=False)

    # Documentos (Binarios en memoria)
    doc_dni_front = fields.Binary('DNI/NIE Anverso', attachment=False)
    doc_dni_back = fields.Binary('DNI Reverso', attachment=False)
    doc_cif = fields.Binary('CIF Empresa', attachment=False)
    doc_reta = fields.Binary('Alta RETA (Autónomos)', attachment=False)
    doc_aeat = fields.Binary('Certificado AEAT', attachment=False)
    doc_ss = fields.Binary('Certificado SS', attachment=False)
    doc_iban = fields.Binary('Certificado Bancario', attachment=False)
    doc_ubo = fields.Binary('Declaración UBO', attachment=False)
    doc_auth_col = fields.Binary('Autorización del COL (SUB)', attachment=False)
    doc_foto_local = fields.Binary('Foto del local (COL)', attachment=False)
    doc_contract = fields.Binary('Contrato Firmado (PDF)', attachment=False)

    # Consentimientos
    acepta_contrato = fields.Boolean('Acepta Contrato Mercantil', default=False)
    acepta_privacidad = fields.Boolean('Acepta Política de Privacidad (RGPD)', default=False)

    def action_next_step(self):
        if self.step == 1 and not self.actor_type:
            raise UserError('Seleccione un tipo de actor.')
        self.step += 1
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'premiosred.onboarding.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_previous_step(self):
        if self.step > 1:
            self.step -= 1
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'premiosred.onboarding.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_create_actor(self):
        self._validate_kill_switch()
        self._validate_nif()
        self._validate_iban()
        
        if not self.acepta_contrato or not self.acepta_privacidad:
            raise UserError('⚠️ Debe aceptar expresamente el contrato y la política de privacidad.')

        # Verificar obligatorios según tipo
        if not self.doc_dni_front:
            raise UserError('El DNI/NIE Anverso es obligatorio.')
        if not self.doc_contract:
            raise UserError('El Contrato firmado en PDF es obligatorio.')

        # Buscar el ID del rol
        type_map = {'col':'col', 'sub':'sub', 'ccp':'ccp', 'com':'com', 'ase':'ase'}
        role_code = type_map[self.actor_type]
        role = self.env['redlmc.actor.role'].search([('code', '=', role_code)], limit=1)
        if not role:
            raise UserError(f'No se encontró el rol con código "{role_code}" en la base de datos.')
        
        # Generar código secuencia
        seq_code = f'premiosred.actor.{self.actor_type}'
        seq = self.env['ir.sequence'].next_by_code(seq_code)
        if not seq:
            seq = '000001' # Fallback si no existe la secuencia aún
            
        actor_code = f'{self.actor_type.upper()}-{date.today().strftime("%Y%m%d")}-{seq}'

        vals = {
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'street': self.address,
            'vat': self.nif,
            'redlmc_actor_role_id': role.id,
            'redlmc_actor_code': actor_code,
            'redlmc_actor_status': 'draft',
            'redlmc_iban': self.iban,
            'redlmc_contract_signed': bool(self.doc_contract),
            'redlmc_kyb_estado': 'pendiente',
        }

        partner = self.env['res.partner'].create(vals)

        # Crear attachments y vincular a los campos de KYB
        if self.doc_dni_front:
            att = self._create_attachment(partner, self.doc_dni_front, 'DNI_Anverso.pdf')
            partner.redlmc_kyb_dni_front = att.id
        if self.doc_dni_back:
            att = self._create_attachment(partner, self.doc_dni_back, 'DNI_Reverso.pdf')
            partner.redlmc_kyb_dni_back = att.id
        if self.doc_cif:
            att = self._create_attachment(partner, self.doc_cif, 'CIF.pdf')
            partner.redlmc_kyb_cif = att.id
        if self.doc_reta:
            att = self._create_attachment(partner, self.doc_reta, 'Alta_RETA.pdf')
            partner.redlmc_kyb_reta = att.id
        if self.doc_aeat:
            att = self._create_attachment(partner, self.doc_aeat, 'Certificado_AEAT.pdf')
            partner.redlmc_kyb_aeat = att.id
        if self.doc_ss:
            att = self._create_attachment(partner, self.doc_ss, 'Certificado_SS.pdf')
            partner.redlmc_kyb_ss = att.id
        if self.doc_iban:
            att = self._create_attachment(partner, self.doc_iban, 'Certificado_IBAN.pdf')
            partner.redlmc_kyb_iban_cert = att.id
        if self.doc_ubo:
            att = self._create_attachment(partner, self.doc_ubo, 'Declaracion_UBO.pdf')
            partner.redlmc_kyb_ubo = att.id
        if self.doc_auth_col:
            att = self._create_attachment(partner, self.doc_auth_col, 'Autorizacion_COL.pdf')
            partner.redlmc_kyb_auth_col = att.id
        if self.doc_foto_local:
            att = self._create_attachment(partner, self.doc_foto_local, 'Foto_Local.jpg')
            partner.redlmc_kyb_foto_local = att.id
        if self.doc_contract:
            att = self._create_attachment(partner, self.doc_contract, 'Contrato_Firmado.pdf')
            partner.redlmc_kyb_contrato = att.id

        # Redirigir a la ficha del partner creado
        return {
            'type': 'ir.actions.act_window',
            'name': f'Actor {actor_code}',
            'res_model': 'res.partner',
            'res_id': partner.id,
            'view_mode': 'form',
        }

    def _create_attachment(self, partner, datas, filename):
        return self.env['ir.attachment'].create({
            'name': f'{partner.redlmc_actor_code}_{filename}',
            'type': 'binary',
            'datas': datas,
            'res_model': 'res.partner',
            'res_id': partner.id,
        })

    def _validate_kill_switch(self):
        if datetime.now() > datetime(2026, 12, 21, 23, 59, 59):
            raise UserError('⛔ Campaña cerrada. El Botón de Parada de Emergencia está activo. No se pueden dar de alta más actores.')

    def _validate_nif(self):
        try:
            import stdnum.es.nif as nif_validator
            if not nif_validator.is_valid(self.nif):
                raise UserError(f'⚠️ NIF/CIF/NIE inválido: {self.nif}')
        except ImportError:
            pass

    def _validate_iban(self):
        try:
            import stdnum.iban as iban_validator
            if not iban_validator.is_valid(self.iban):
                raise UserError(f'⚠️ IBAN inválido: {self.iban}')
        except ImportError:
            pass
