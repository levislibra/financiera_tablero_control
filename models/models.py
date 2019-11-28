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
	parent_id = fields.Many2one('financiera.tablero', 'Año o Mes')
	month_ids = fields.One2many('financiera.tablero', 'parent_id', 'Meses', ondelete='cascade')
	day_ids = fields.One2many('financiera.tablero', 'parent_id', 'Dias', ondelete='cascade')
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
		i = 1
		# print("Crear")
		for month_string in MESES:
			# print("Creando mes "+str(month_string))
			t_values = {
				'periodo': 'month',
				'month': i,
				'month_string': month_string,
				'year': self.year,
				'parent_id': self.id,
			}
			tablero_mes_id = self.env['financiera.tablero'].create(t_values)
			self.month_ids = [tablero_mes_id.id]
			
			# creamos los dias
			dias_mes = monthrange(self.year, i)[1]
			j = 1
			# print("  dias del mes: "+str(dias_mes))
			while j <= dias_mes:
				# print("  Creando dia: "+str(j))
				t_values = {
					'periodo': 'day',
					'day': j,
					'month': i,
					'month_string': month_string,
					'year': self.year,
					'parent_id': tablero_mes_id.id,
				}
				tablero_dia_id = self.env['financiera.tablero'].create(t_values)
				tablero_mes_id.day_ids = [tablero_dia_id.id]
				j += 1
			i += 1

class FinancieraTableroPrestamo(models.Model):
	_name = 'financiera.tablero.prestamo'

	entidad_id = fields.Many2one('financiera.entidad', 'Entidad')
	cantidad = fields.Integer('Cantidad')
	capital = fields.Float('Capital', digits=(16,2))
	interes = fields.Float('Interes', digits=(16,2))
	meses_promedio = fields.Float('Meses promedio', digits=(16,2))
	nuevos = fields.Integer('Nuevos')
	company_id = fields.Many2one('res.company', 'Empresa', required=False, default=lambda self: self.env['res.company']._company_default_get('financiera.prestamo'))

class FinancieraTableroCuota(models.Model):
	_name = 'financiera.tablero.cuota'

	entidad_id = fields.Many2one('financiera.entidad', 'Entidad')
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
