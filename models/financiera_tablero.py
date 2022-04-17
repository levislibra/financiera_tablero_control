# -*- coding: utf-8 -*-

from openerp import models, fields, api
from calendar import monthrange
from datetime import datetime, timedelta

MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre']

class FinancieraTablero(models.Model):
	_name = 'financiera.tablero'

	name = fields.Char()
	periodo = fields.Selection([
		('year', 'Año'),
		('month', 'Mes'),
		('day', 'Dia')], string='Periodo')
	day = fields.Integer('Dia')
	month = fields.Integer('Mes')
	month_string = fields.Char('Mes')
	year = fields.Integer('Año')
	state = fields.Selection([('borrador', 'Borrador'), ('creado', 'Creado')], 'Estado', default='borrador')
	prestamo_sucursal_ids = fields.One2many('financiera.tablero.prestamo', 'tablero_sucursal_id', 'Prestamos')
	prestamo_sucursal_graph_ids = fields.One2many('financiera.tablero.prestamo', 'tablero_sucursal_id', 'Prestamos')
	prestamo_comercio_ids = fields.One2many('financiera.tablero.prestamo', 'tablero_comercio_id', 'Prestamos')
	cuota_sucursal_ids = fields.One2many('financiera.tablero.cuota', 'tablero_sucursal_id', 'Cuotas')
	cuota_comercio_ids = fields.One2many('financiera.tablero.cuota', 'tablero_comercio_id', 'Cuotas')
	parent_year_id = fields.Many2one('financiera.tablero', 'Año')
	parent_month_id = fields.Many2one('financiera.tablero', 'Mes')
	month_ids = fields.One2many('financiera.tablero', 'parent_year_id', 'Meses', ondelete='cascade')
	day_ids = fields.One2many('financiera.tablero', 'parent_month_id', 'Dias', ondelete='cascade')
	fecha_desde = fields.Date("Fecha desde")
	fecha_hasta = fields.Date("Fecha hasta")
	color = fields.Integer('Color Index')
	company_id = fields.Many2one('res.company', 'Empresa', required=False, default=lambda self: self.env['res.company']._company_default_get('financiera.tablero'))

	@api.model
	def create(self, values):
		rec = super(FinancieraTablero, self).create(values)
		name = None
		if rec.periodo == 'day':
			name = 'Reporte '+str(rec.day).zfill(2)+' de '+rec.month_string+' de '+str(rec.year)
		elif rec.periodo == 'month':
			name = 'Reporte '+rec.month_string+' de '+str(rec.year)
		elif rec.periodo == 'year':
			name = 'Reporte '+str(rec.year)
		rec.update({
			'name': name,
		})

		return rec

	@api.one
	def button_crear_meses(self):
		self.fecha_desde = str(self.year)+"-01-01"
		self.fecha_hasta = str(self.year)+"-12-31"
		i = 1
		for month_string in MESES:
			dias_mes = monthrange(self.year, i)[1]
			fecha_desde = str(self.year)+"-"+str(i).zfill(2)+"-01"
			fecha_hasta = str(self.year)+"-"+str(i).zfill(2)+"-"+str(dias_mes).zfill(2)
			t_values = {
				'periodo': 'month',
				'month': i,
				'month_string': month_string,
				'year': self.year,
				'parent_year_id': self.id,
				'fecha_desde': fecha_desde,
				'fecha_hasta': fecha_hasta,
				'state': 'creado',
			}
			tablero_mes_id = self.env['financiera.tablero'].create(t_values)
			self.month_ids = [tablero_mes_id.id]
			# creamos los dias
			j = 1
			while j <= dias_mes:
				fecha_desde = str(self.year)+"-"+str(i).zfill(2)+"-"+str(j).zfill(2)
				fecha_hasta = str(self.year)+"-"+str(i).zfill(2)+"-"+str(j).zfill(2)
				t_values = {
					'periodo': 'day',
					'day': j,
					'month': i,
					'month_string': month_string,
					'year': self.year,
					'parent_month_id': tablero_mes_id.id,
					'fecha_desde': fecha_desde,
					'fecha_hasta': fecha_hasta,
					'state': 'creado',
				}
				tablero_dia_id = self.env['financiera.tablero'].create(t_values)
				tablero_mes_id.day_ids = [tablero_dia_id.id]
				j += 1
			i += 1
		self.state = 'creado'

	@api.one
	def actualizar_tablero(self):
		self.actualizar_prestamos()
		self.actualizar_cuotas()

	@api.one
	def actualizar_prestamos(self):
		cr = self.env.cr
		uid = self.env.uid
		entidad_obj = self.pool.get('financiera.entidad')
		entidad_ids = entidad_obj.search(cr, uid, [
			('company_id', '=', self.company_id.id)])
		for prestamo_id in self.prestamo_sucursal_ids:
			prestamo_id.unlink()
		for prestamo_id in self.prestamo_comercio_ids:
			prestamo_id.unlink()
		for _id in entidad_ids:
			entidad_id = entidad_obj.browse(cr, uid, _id)
			cantidad = 0
			capital = 0
			interes = 0
			total = 0
			meses_promedio = 0
			nuevos = 0
			prestamo_ids = []
			if entidad_id.type == 'sucursal':
				prestamo_obj = self.pool.get('financiera.prestamo')
				prestamo_ids = prestamo_obj.search(cr, uid, [
					('company_id', '=', self.company_id.id),
					('fecha', '>=', self.fecha_desde),
					('fecha', '<=', self.fecha_hasta),
					('sucursal_id', '=', entidad_id.id)])
			elif entidad_id.type == 'comercio':
				prestamo_obj = self.pool.get('financiera.prestamo')
				prestamo_ids = prestamo_obj.search(cr, uid, [
					('company_id', '=', self.company_id.id),
					('fecha', '>=', self.fecha_desde),
					('fecha', '<=', self.fecha_hasta),
					('sucursal_id', '=', entidad_id.id)])
			for _id in prestamo_ids:
				prestamo_id = prestamo_obj.browse(cr, uid, _id)
				if prestamo_id.state in ('acreditacion_pendiente', 
					'acreditado', 'precancelado', 'refinanciado', 'pagado', 'incobrable'):
					cantidad += 1
					capital += prestamo_id.monto_solicitado
					interes += prestamo_id.interes_a_cobrar
					total = capital+interes
					prestamo_partner_obj = self.pool.get('financiera.prestamo')
					prestamo_partner_ids = prestamo_partner_obj.search(cr, uid, [
						('company_id', '=', self.company_id.id),
						('partner_id', '=', prestamo_id.partner_id.id),
						('fecha', '<=', prestamo_id.fecha),
						('state', 'in', ('acreditacion_pendiente', 'acreditado', 
							'precancelado', 'refinanciado', 'pagado', 'incobrable'))])
					if len(prestamo_partner_ids) == 1:
						nuevos += 1
			tp_values = {
				'entidad_id': entidad_id.id,
				'cantidad': cantidad,
				'capital': capital,
				'interes': interes,
				'total': total,
				'meses_promedio': meses_promedio,
				'nuevos': nuevos,
			}
			tablero_prestamo_id = self.env['financiera.tablero.prestamo'].create(tp_values)
			if entidad_id.type == 'sucursal':
				self.prestamo_sucursal_ids = [tablero_prestamo_id.id]
			else:
				self.prestamo_comercio_ids = [tablero_prestamo_id.id]

	@api.one
	def actualizar_cuotas(self):
		cr = self.env.cr
		uid = self.env.uid
		entidad_obj = self.pool.get('financiera.entidad')
		entidad_ids = entidad_obj.search(cr, uid, [
			('company_id', '=', self.company_id.id)])
		for cuota_id in self.cuota_sucursal_ids:
			cuota_id.unlink()
		for cuota_id in self.cuota_comercio_ids:
			cuota_id.unlink()
		for _id in entidad_ids:
			entidad_id = entidad_obj.browse(cr, uid, _id)
			cantidad = 0
			capital = 0
			interes = 0
			punitorio = 0
			seguro = 0
			otros = 0
			parcial = 0
			total_cobrado = 0
			total_cuotas = 0
			por_cobrar = 0
			mora = 0
			total_cuotas_vencidas = 0
			saldo_cuotas_vencidas = 0
			cuota_ids = []
			if entidad_id.type == 'sucursal':
				cuota_obj = self.pool.get('financiera.prestamo.cuota')
				cuota_ids = cuota_obj.search(cr, uid, [
					('company_id', '=', self.company_id.id),
					('fecha_vencimiento', '>=', self.fecha_desde),
					('fecha_vencimiento', '<=', self.fecha_hasta),
					('sucursal_id', '=', entidad_id.id)])
			elif entidad_id.type == 'comercio':
				cuota_obj = self.pool.get('financiera.prestamo.cuota')
				cuota_ids = cuota_obj.search(cr, uid, [
					('company_id', '=', self.company_id.id),
					('fecha_vencimiento', '>=', self.fecha_desde),
					('fecha_vencimiento', '<=', self.fecha_hasta),
					('sucursal_id', '=', entidad_id.id)])
			for _id in cuota_ids:
				cuota_id = cuota_obj.browse(cr, uid, _id)
				if cuota_id.state in ('precancelada', 'cobrada'):
					cantidad += 1
					capital += cuota_id.capital 
					interes += cuota_id.interes
					punitorio += cuota_id.punitorio+cuota_id.punitorio_iva
					seguro += cuota_id.seguro+cuota_id.seguro_iva
					otros += cuota_id.ajuste+cuota_id.ajuste_iva
					total_cobrado += cuota_id.total
				elif cuota_id.state in ('activa', 'judicial', 'incobrable'):
					parcial += cuota_id.cobrado
					total_cobrado += cuota_id.cobrado
					por_cobrar += cuota_id.saldo
				total_cuotas += cuota_id.total
				fecha_vencimiento = datetime.strptime(cuota_id.fecha_vencimiento, "%Y-%m-%d")
				if fecha_vencimiento < datetime.now():
					total_cuotas_vencidas += cuota_id.total
					saldo_cuotas_vencidas += cuota_id.saldo
			if total_cuotas > 0:
				mora = saldo_cuotas_vencidas/total_cuotas_vencidas
			tc_values = {
				'entidad_id': entidad_id.id,
				'cantidad': cantidad,
				'capital': capital,
				'interes': interes,
				'punitorio': punitorio,
				'seguro': seguro,
				'otros': otros,
				'parcial': parcial,
				'total_cobrado': total_cobrado,
				'por_cobrar': por_cobrar,
				'total_cuotas': total_cuotas,
				'mora': mora,
			}
			tablero_cuota_id = self.env['financiera.tablero.cuota'].create(tc_values)
			if entidad_id.type == 'sucursal':
				self.cuota_sucursal_ids = [tablero_cuota_id.id]
			else:
				self.cuota_comercio_ids = [tablero_cuota_id.id]


	def open_line(self, cr, uid, id, context=None):
		return {
			'type': 'ir.actions.act_window',
			'name': 'Tablero', 
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': self._name,
			'res_id': id[0],
			'target': 'current',
		}

class FinancieraTableroPrestamo(models.Model):
	_name = 'financiera.tablero.prestamo'

	tablero_sucursal_id = fields.Many2one('financiera.tablero', 'Tablero')
	tablero_comercio_id = fields.Many2one('financiera.tablero', 'Tablero')
	entidad_id = fields.Many2one('financiera.entidad', 'Entidad')
	entidad_type = fields.Selection('Entidad tipo', related='entidad_id.type')
	cantidad = fields.Integer('Cantidad')
	capital = fields.Float('Capital', digits=(16,2))
	interes = fields.Float('Interes', digits=(16,2))
	total = fields.Float('Total', digits=(16,2))
	meses_promedio = fields.Float('Meses promedio', digits=(16,2))
	nuevos = fields.Integer('Nuevos')
	company_id = fields.Many2one('res.company', 'Empresa', required=False, default=lambda self: self.env['res.company']._company_default_get('financiera.prestamo'))

class FinancieraTableroCuota(models.Model):
	_name = 'financiera.tablero.cuota'

	tablero_sucursal_id = fields.Many2one('financiera.tablero', 'Tablero')
	tablero_comercio_id = fields.Many2one('financiera.tablero', 'Tablero')
	entidad_id = fields.Many2one('financiera.entidad', 'Entidad')
	entidad_type = fields.Selection('Entidad tipo', related='entidad_id.type')
	cantidad = fields.Integer('Cantidad')
	capital = fields.Float('Capital', digits=(16,2))
	interes = fields.Float('Interes', digits=(16,2))
	punitorio = fields.Float('Punitorio', digits=(16,2))
	seguro = fields.Float('Seguro', digits=(16,2))
	otros = fields.Float('Otros', digits=(16,2))
	parcial = fields.Float('Parcial', digits=(16,2))
	total_cobrado = fields.Float('Total cobrado', digits=(16,2))
	por_cobrar = fields.Float('Por cobrar', digits=(16,2))
	total_cuotas = fields.Float('Total cuotas', digits=(16,2))
	mora = fields.Float('Mora', digits=(16,2))
	company_id = fields.Many2one('res.company', 'Empresa', required=False, default=lambda self: self.env['res.company']._company_default_get('financiera.prestamo'))
