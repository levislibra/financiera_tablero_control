# -*- coding: utf-8 -*-

from openerp import models, fields, api
from calendar import monthrange
from datetime import datetime, timedelta

import base64
import requests
import random

MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre']
PRESTAMOS_OTORGADOS = ['acreditacion_pendiente','acreditado','precancelado','refinanciado','pagado','incobrable']

class FinancieraTablero(models.TransientModel):
	_name = 'financiera.tablero'

	month = fields.Selection([('01', 'Enero'), ('02', 'Febrero'), ('03', 'Marzo'), ('04', 'Abril'), ('05', 'Mayo'), ('06', 'Junio'), ('07', 'Julio'), ('08', 'Agosto'), ('09', 'Setiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')], 'Mes', required=True, default=lambda self: datetime.now().strftime('%m'))
	year = fields.Integer('Año', required=True, default=lambda self: datetime.now().year)
	company_id = fields.Many2one('res.company', 'Empresa', required=False, default=lambda self: self.env['res.company']._company_default_get('financiera.tablero'))
	# Prestamos
	prestamos_otorgados = fields.Integer('Prestamos otorgados', compute='_get_prestamos_otorgados', store=True)
	prestamos_otorgados_capital = fields.Float('Capital', digits=(16, 2), compute='_get_prestamos_otorgados', store=True)
	prestamos_otorgados_total_a_cobrar = fields.Float('Total a cobrar', digits=(16, 2), compute='_get_prestamos_otorgados', store=True)
	prestamos_otorgados_chart = fields.Binary('Prestamos otorgados grafico', compute='_get_prestamos_otorgados', store=True)
	# Cuotas
	cobros = fields.Integer('Cobros', compute='_get_cobros', store=True)
	cobros_capital = fields.Float('Capital', digits=(16, 2), compute='_get_cobros', store=True)
	cobros_interes = fields.Float('Interes', digits=(16, 2), compute='_get_cobros', store=True)
	cobros_interes_iva = fields.Float('Interes IVA', digits=(16, 2), compute='_get_cobros', store=True)
	cobros_punitorio = fields.Float('Punitorio', digits=(16, 2), compute='_get_cobros', store=True)
	cobros_punitorio_iva = fields.Float('Punitorio IVA', digits=(16, 2), compute='_get_cobros', store=True)
	cobros_seguro = fields.Float('Seguro', digits=(16, 2), compute='_get_cobros', store=True)
	cobros_seguro_iva = fields.Float('Seguro IVA', digits=(16, 2), compute='_get_cobros', store=True)
	cobros_ajuste = fields.Float('Ajuste', digits=(16, 2), compute='_get_cobros', store=True)
	cobros_ajuste_iva = fields.Float('Ajuste IVA', digits=(16, 2), compute='_get_cobros', store=True)
	cobros_total = fields.Float('Total', digits=(16, 2), compute='_get_cobros', store=True)

	@api.one
	@api.depends('month', 'year')
	def _get_prestamos_otorgados(self):
		prestamos_otorgados_capital = 0
		prestamos_otorgados_total_a_cobrar = 0
		# Prestamos
		date_init = str(self.year) + '-' + self.month + '-01'
		date_end = str(self.year) + '-' + self.month + '-' + str(monthrange(self.year, int(self.month))[1])
		prestamos = self.env['financiera.prestamo'].search([
			('state', 'in', PRESTAMOS_OTORGADOS),
			('fecha', '>=', date_init),
			('fecha', '<=', date_end),
		])
		data_set = [random.randint(1,50) for i in range(0, monthrange(self.year, int(self.month))[1]-1)]
		self.prestamos_otorgados = len(prestamos)
		for prestamo in prestamos:
			data_set[int(prestamo.fecha[8:10])-1] += 1
			prestamos_otorgados_capital += prestamo.monto_solicitado
			prestamos_otorgados_total_a_cobrar += prestamo.total
		self.prestamos_otorgados_capital = prestamos_otorgados_capital
		self.prestamos_otorgados_total_a_cobrar = prestamos_otorgados_total_a_cobrar
		data_values = ""
		ejex_values = ""
		print("data_set: ", data_set)
		day = 1
		for data in data_set:
			data_values += str(data) + ","
			ejex_values += "|" + str(day)
			day += 1
		print("data_values: ", data_values)
		print("ejex_values: ", ejex_values)
		endpoint = "http://chart.apis.google.com/chart?"
		image_size = "chs=650x250&"
		graph_name = "chtt=Prestamos otorgados por dia&"
		graph_type = "cht=bvg&" # bar vertical group
		data_colors = "chco=80C65A&"
		data = "chd=t:" + data_values[0:len(data_values)-1] + "&"
		ejex = "chxl=0:" + ejex_values + "&"
		tags = "" # "chdl=Me+gusta+%286+votos%29|no+me+gusta+%281+voto%29|nsnc+%283+votos%29"
		marcador_valores = "chm=N,000000,0,-1,11&"
		# chds=0,50&
		# chxr=1,0,50
		default = "chxt=x,y&chbh=a"
		url = endpoint + image_size + graph_name + graph_type + data_colors + data + ejex + tags + marcador_valores + default
		print("url: ", url)
		self.prestamos_otorgados_chart = base64.b64encode(requests.get(url).content)


		
	@api.one
	@api.depends('month', 'year')
	def _get_cobros(self):
		cobros_capital = 0
		cobros_interes = 0
		cobros_interes_iva = 0
		cobros_punitorio = 0
		cobros_punitorio_iva = 0
		cobros_seguro = 0
		cobros_seguro_iva = 0
		cobros_ajuste = 0
		cobros_ajuste_iva = 0
		cobros_total = 0
		# Cobros de Cuotas
		date_init = str(self.year) + '-' + self.month + '-01'
		date_end = str(self.year) + '-' + self.month + '-' + str(monthrange(self.year, int(self.month))[1])
		payment_ids = self.env['account.payment'].search([
			('state', '=', 'posted'),
			('cuota_id', '!=', False),
			('payment_date', '>=', date_init),
			('payment_date', '<=', date_end),
		])
		self.cobros = len(payment_ids)
		for payment in payment_ids:
			cobros_capital += payment.capital
			cobros_interes += payment.interes
			cobros_interes_iva += payment.interes_iva
			cobros_punitorio += payment.punitorio
			cobros_punitorio_iva += payment.punitorio_iva
			cobros_seguro += payment.seguro
			cobros_seguro_iva += payment.seguro_iva
			cobros_ajuste += payment.ajuste
			cobros_ajuste_iva += payment.ajuste_iva
			cobros_total += payment.amount
		self.cobros_capital = cobros_capital
		self.cobros_interes = cobros_interes
		self.cobros_interes_iva = cobros_interes_iva
		self.cobros_punitorio = cobros_punitorio
		self.cobros_punitorio_iva = cobros_punitorio_iva
		self.cobros_seguro = cobros_seguro
		self.cobros_seguro_iva = cobros_seguro_iva
		self.cobros_ajuste = cobros_ajuste
		self.cobros_ajuste_iva = cobros_ajuste_iva
		self.cobros_total = cobros_total

