# -*- coding: utf-8 -*-

from openerp import models, fields, api
from calendar import monthrange

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
	prestamo_ids = fields.One2many('financiera.tablero.prestamo', 'tablero_id', 'Prestamos')
	cuota_ids = fields.One2many('financiera.tablero.cuota', 'tablero_id', 'Cuotas')
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
				}
				tablero_dia_id = self.env['financiera.tablero'].create(t_values)
				tablero_mes_id.day_ids = [tablero_dia_id.id]
				j += 1
			i += 1

	@api.one
	def actualizar_prestamos(self):
		cr = self.env.cr
		uid = self.env.uid
		entidad_obj = self.pool.get('financiera.entidad')
		entidad_ids = entidad_obj.search(cr, uid, [
			('company_id', '=', self.company_id.id)])
		for prestamo_id in self.prestamo_ids:
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
					('comercio_id', '=', entidad_id.id)])
			for _id in prestamo_ids:
				prestamo_id = prestamo_obj.browse(cr, uid, _id)
				cantidad += 1
				capital += prestamo_id.monto_solicitado
				interes += prestamo_id.interes_a_cobrar
				total = capital+interes
				prestamo_partner_obj = self.pool.get('financiera.prestamo')
				prestamo_partner_ids = prestamo_partner_obj.search(cr, uid, [
					('company_id', '=', self.company_id.id),
					('partner_id', '=', prestamo_id.partner_id.id)])
				if len(prestamo_partner_ids) == 1:
					nuevos += 1
			tp_values = {
				'tablero_id': self.id,
				'entidad_id': entidad_id.id,
				'cantidad': cantidad,
				'capital': capital,
				'interes': interes,
				'total': total,
				'meses_promedio': meses_promedio,
				'nuevos': nuevos,
			}
			tablero_prestamo_id = self.env['financiera.tablero.prestamo'].create(tp_values)
			self.prestamo_ids = [tablero_prestamo_id.id]

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

	tablero_id = fields.Many2one('financiera.tablero', 'Tablero')
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

	tablero_id = fields.Many2one('financiera.tablero', 'Tablero')
	entidad_id = fields.Many2one('financiera.entidad', 'Entidad')
	entidad_type = fields.Selection('Entidad tipo', related='entidad_id.type')
	cantidad = fields.Integer('Cantidad')
	capital = fields.Float('Capital', digits=(16,2))
	interes = fields.Float('Interes', digits=(16,2))
	punitorio = fields.Float('Punitorio', digits=(16,2))
	seguro = fields.Float('Seguro', digits=(16,2))
	otros = fields.Float('Otros', digits=(16,2))
	parcial = fields.Float('Parcial', digits=(16,2))
	total = fields.Float('Total', digits=(16,2))
	por_cobrar = fields.Float('Por cobrar', digits=(16,2))
	company_id = fields.Many2one('res.company', 'Empresa', required=False, default=lambda self: self.env['res.company']._company_default_get('financiera.prestamo'))
