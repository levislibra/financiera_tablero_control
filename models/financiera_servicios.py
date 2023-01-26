# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta, date
from time import gmtime, strftime

import logging
_logger = logging.getLogger(__name__)

class FinancieraServicios(models.TransientModel):
	_name = 'financiera.servicios'

	company_id = fields.Many2one('res.company', 'Compañia', default=lambda self: self.env.user.company_id)
	servidor_correo_salientes = fields.Text('Servidores de correo saliente', compute='_get_servicios', store=True)
	test = fields.Text('Test', default='Test')
	# # Informes comerciales
	# # Veraz
	# veraz_contratado = fields.Boolean('Veraz contratado', compute='_get_servicios')
	# veraz_estado = fields.Selection(related='company_id.veraz_estado', string='Estado Veraz')
	# # ROL
	# rol_contratado = fields.Boolean('Rol contratado', compute='_get_servicios')
	# rol_saldo_informes = fields.Boolean('Rol saldo informes', compute='_get_servicios')
	# SMS
	sms_text = fields.Text('SMS contratado', compute='_get_servicios_sms')
	# Facturacion electronica
	diarios_facturacion_electronica = fields.Text('Diarios de facturacion electronica', compute='_get_servicios_facturacion_electronica')
	# Cobranza y seguimiento
	cobranza_y_seguimiento_text = fields.Text('Cobranza y seguimiento', compute='_get_servicios_cobranza_y_seguimiento')

	@api.one
	def button_update(self):
		self._get_servicios()

	@api.one
	def _get_servicios(self):
		servidor_correo_saliente_ids = self.env['ir.mail_server'].search([
			('company_id', '=', self.company_id.id),
			('name', '!=', False),
			('smtp_user', '!=', False),
			('smtp_pass', '!=', False),
			('smtp_port', '!=', False),
			('smtp_host', '!=', False),
			('smtp_encryption', '!=', False)
		])
		servidor_correo_salientes = 'Correos salientes: ' + str(len(servidor_correo_saliente_ids)) + '<br/>'
		for servidor_correo_saliente_id in servidor_correo_saliente_ids:
			user = servidor_correo_saliente_id.smtp_user
			state = self.get_state_servidor(servidor_correo_saliente_id)
			servidor_correo_salientes += user + ' - ' + state + '<br/>'

		self.servidor_correo_salientes = servidor_correo_salientes
	
	def get_state_servidor(self, servidor_id):
		try:
			servidor_id.test_smtp_connection()
			return '<span style="color:green;">Ok</span>'
		except Exception as e:
			if 'satisfactoria' in str(e):
				return '<span style="color:green;">Ok</span>'
			else:
				return '<span style="color:red;">Error</span>'
	
	@api.one
	def _get_servicios_sms(self):
		sms_text = 'SMS contratado: '
		sms_contratado = 'No'
		sms_saldo_mensajes = '0'
		if self.company_id.sms_configuracion_id:
			sms_contratado = 'Si'
		sms_text += sms_contratado + '<br/>'
		if sms_contratado == 'Si':
			sms_text += 'Estado de conexion: ' + self.get_state_sms() + '<br/>'
			sms_saldo_mensajes = str(self.company_id.sms_configuracion_id.sms_saldo)
			sms_text += 'Saldo de mensajes: ' + sms_saldo_mensajes + '<br/>'
		self.sms_text = sms_text
	
	def get_state_sms(self):
		try:
			self.company_id.sms_configuracion_id.actualizar_saldo()
			return '<span style="color:green;">Ok</span>'
		except Exception as e:
			return '<span style="color:red;">Error</span>'
	
	@api.one
	def _get_servicios_facturacion_electronica(self):
		diarios_facturacion_electronica = 'Puntos de venta: '
		diarios_facturacion_electronica_ids = self.env['account.journal'].search([
			('company_id', '=', self.company_id.id),
			('use_documents', '=', True),
			('type', '=', 'sale'),
		])
		diarios_facturacion_electronica += str(len(diarios_facturacion_electronica_ids)) + '<br/>'
		for diario_facturacion_electronica_id in diarios_facturacion_electronica_ids:
			diarios_facturacion_electronica += diario_facturacion_electronica_id.name + ' - ' + self.get_state_facturacion_electronica_connection(diario_facturacion_electronica_id) + ' - ' + self.get_state_facturacion_electronica_sincronize(diario_facturacion_electronica_id) + '<br/>'
		self.diarios_facturacion_electronica = diarios_facturacion_electronica


	def get_state_facturacion_electronica_connection(self, journal_id):
		try:
			journal_id.action_get_connection()
			return '<span style="color:green;">Ok</span>'
		except Exception as e:
			return '<span style="color:red;">Error</span>'
	
	def get_state_facturacion_electronica_sincronize(self, journal_id):
		try:
			journal_id.check_document_local_remote_number()
			return '<span style="color:green;">Ok</span>'
		except Exception as e:
			if 'Todos los documentos están sincronizados' in str(e):
				return '<span style="color:green;">Sincronizado</span>'
			else:
				return '<span style="color:red;">Desincronizado</span>'
	
	@api.one
	def _get_servicios_cobranza_y_seguimiento(self):
		cobranza_y_seguimiento_text = 'Cobranza y seguimiento contratado: '
		contratado = 'No'
		if self.company_id.cobranza_config_id:
			contratado = 'Si'
		cobranza_y_seguimiento_text += contratado + '<br/>'
		if contratado == 'Si':
			fecha_actualizacion_original = self.company_id.cobranza_config_id.fecha
			fecha_actualizacion = datetime.strptime(self.company_id.cobranza_config_id.fecha, '%Y-%m-%d %H:%M:%S').date()
			today = (datetime.now() - timedelta(hours=3)).date()
			diferencia = today - fecha_actualizacion
			if diferencia.days == 0:
				fecha_actualizacion_original += '<span style="color:green;">' + fecha_actualizacion_original + '</span><br/>'
			else:
				fecha_actualizacion_original += '<span style="color:red;">' + fecha_actualizacion_original + '</span><br/>'
			cobranza_y_seguimiento_text += 'Ultima actualizacion: ' + fecha_actualizacion_original + '<br/>'
		self.cobranza_y_seguimiento_text = cobranza_y_seguimiento_text
