# -*- coding: utf-8 -*-

from openerp import fields, models, api
from datetime import datetime, timedelta
import xlwt
import base64
import StringIO
import json
import logging

_logger = logging.getLogger(__name__)

class FinancieraCarteraReport(models.TransientModel):
	_name = 'financiera.cartera.report'
	_description = 'Reporte de Cuotas'

	date = fields.Date('Estado de cartera al día')
	file = fields.Binary('Archivo excel')
	file_name = fields.Char('Nombre', default='Estado de cartera.xls')
	file2 = fields.Binary('Archivo excel')
	file_name2 = fields.Char('Nombre', default='Saldo de clientes.xls')

	@api.one
	def _set_date_tmp_cuotas(self):
		print("_set_date_tmp_cuotas")
		cuotas_obj = self.pool.get('financiera.prestamo.cuota')
		total = 0
		count = 0
		while True:
			print("self.date: ", self.date)
			print("self.env.user.company_id.id: ", self.env.user.company_id.id)
			cuotas_ids = cuotas_obj.search(self.env.cr, self.env.uid, [
				# ('company_id.id', '=', self.env.user.company_id.id),
				('state', '!=', 'cotizacion'),
				('prestamo_id.fecha', '<=', str(self.date)),
				'|', ('fecha_cobro', '=', False), ('fecha_cobro', '>', str(self.date)),
				'|', ('fecha_tmp', '=', False), ('fecha_tmp', '!=', str(self.date)),
			], limit=200)
			print("cuotas_ids: ", cuotas_ids)
			if not cuotas_ids:
				break
			total += len(cuotas_ids)
			_logger.info('Init Set saldo tmp de cuotas %s', str(total))
			try:
				for _id in cuotas_ids:
					cuota_id = cuotas_obj.browse(self.env.cr, self.env.uid, _id)
					cuota_id.set_saldo_tmp(self.date)
					count += 1
				self.env.cr.commit()
			except Exception as e:
				_logger.error('Error Set saldo tmp de cuotas: %s', str(e))
				self.env.cr.rollback()
		_logger.info('Finish Set saldo tmp de cuotas: %s cuotas actualizadas', count)

	@api.multi
	def print_report(self):
		print("print_report ESTADO DE CARTERA AL DIA XXX")
		self._set_date_tmp_cuotas()
		print("===================")
		print("self.date: ", self.date)
		prestamo_cuota_obj = self.pool.get('financiera.prestamo.cuota')
		prestamo_cuota_ids = prestamo_cuota_obj.search(self.env.cr, self.env.uid, [
			('state', '!=', 'cotizacion'),
			('prestamo_id.fecha', '<=', str(self.date)),
			'|', ('fecha_cobro', '=', False), ('fecha_cobro', '>', str(self.date)),
			# ('fecha_tmp', '=', str(self.date)),
			# ('active_tmp', '=', True),
		], order='fecha_vencimiento')
		records = self.env['financiera.prestamo.cuota'].browse(prestamo_cuota_ids)
		print("records: ", records)
		self.generate_excel_cartera(records)
		partner_saldo_ids = prestamo_cuota_obj.read_group(self.env.cr, self.env.uid, [
			('state', '!=', 'cotizacion'),
			('prestamo_id.fecha', '<=', str(self.date)),
			'|', ('fecha_cobro', '=', False), ('fecha_cobro', '>', str(self.date)),
		], fields=[
			'partner_id', 'main_id_number', 'capital_tmp', 'interes_tmp', 'interes_iva_tmp', 
			'punitorio_tmp', 'punitorio_iva_tmp', 'seguro_tmp', 'seguro_iva_tmp', 'ajuste_tmp', 'ajuste_iva_tmp', 'total_tmp', 
			'cobrado_tmp', 'saldo_tmp'
		], groupby=['partner_id'])
		self.generate_excel_saldo_clientes(partner_saldo_ids)
		return {'type': 'ir.actions.do_nothing'}


	@api.multi
	def generate_excel_cartera(self, records):
		stream = StringIO.StringIO()
		book = xlwt.Workbook(encoding='utf-8')
		sheet = book.add_sheet(u'Reporte de Cuotas')
		sheet.write(0, 0, 'Creado')
		sheet.write(0, 1, 'Cliente')
		sheet.write(0, 2, 'Identificación')
		sheet.write(0, 3, 'Celular')
		sheet.write(0, 4, 'Nro de cuota')
		sheet.write(0, 5, 'Prestamo')
		sheet.write(0, 6, 'Responsable')
		sheet.write(0, 7, 'Fecha de vencimiento')
		sheet.write(0, 8, 'Saldo capital')
		sheet.write(0, 9, 'Capital')
		sheet.write(0, 10, 'Interes')
		sheet.write(0, 11, 'Interes IVA')
		sheet.write(0, 12, 'Punitorio')
		sheet.write(0, 13, 'Punitorio IVA')
		sheet.write(0, 14, 'Seguro')
		sheet.write(0, 15, 'Seguro IVA')
		sheet.write(0, 16, 'Otros conceptos')
		sheet.write(0, 17, 'Otros conceptos IVA')
		sheet.write(0, 18, 'Total')
		sheet.write(0, 19, 'Cobrado')
		# sheet.write(0, 20, 'Reintegro')
		sheet.write(0, 20, 'Saldo')
		sheet.write(0, 21, 'Sucursal')
		row = 1
		for cuota_id in records:
			sheet.write(row, 0, cuota_id.create_date)
			sheet.write(row, 1, cuota_id.partner_id.name)
			sheet.write(row, 2, cuota_id.main_id_number)
			sheet.write(row, 3, cuota_id.partner_mobile)
			sheet.write(row, 4, cuota_id.display_numero_cuota)
			sheet.write(row, 5, cuota_id.prestamo_id.name)
			sheet.write(row, 6, cuota_id.responsable_id.name)
			sheet.write(row, 7, cuota_id.fecha_vencimiento)
			sheet.write(row, 8, cuota_id.saldo_capital)
			sheet.write(row, 9, cuota_id.capital)
			sheet.write(row, 10, cuota_id.interes)
			sheet.write(row, 11, cuota_id.interes_iva)
			sheet.write(row, 12, cuota_id.punitorio_tmp)
			sheet.write(row, 13, cuota_id.punitorio_iva_tmp)
			sheet.write(row, 14, cuota_id.seguro)
			sheet.write(row, 15, cuota_id.seguro_iva)
			sheet.write(row, 16, cuota_id.ajuste)
			sheet.write(row, 17, cuota_id.ajuste_iva)
			sheet.write(row, 18, cuota_id.total_tmp)
			sheet.write(row, 19, cuota_id.cobrado_tmp)
			# sheet.write(row, 20, cuota_id.reintegro)
			sheet.write(row, 20, cuota_id.saldo_tmp)
			sheet.write(row, 21, cuota_id.sucursal_id.name)
			row += 1
		book.save(stream)
		self.file = base64.encodestring(stream.getvalue())
		return {'type': 'ir.actions.do_nothing'}

	@api.multi
	def generate_excel_saldo_clientes(self, records):
		stream = StringIO.StringIO()
		book = xlwt.Workbook(encoding='utf-8')
		sheet = book.add_sheet(u'Saldo de Clientes')
		sheet.write(0, 0, 'ID Cliente')
		sheet.write(0, 1, 'Cliente')
		sheet.write(0, 2, 'Identificación')
		sheet.write(0, 3, 'Capital')
		sheet.write(0, 4, 'Interes')
		sheet.write(0, 5, 'Interes IVA')
		sheet.write(0, 6, 'Punitorio')
		sheet.write(0, 7, 'Punitorio IVA')
		sheet.write(0, 8, 'Seguro')
		sheet.write(0, 9, 'Seguro IVA')
		sheet.write(0, 10, 'Otros conceptos')
		sheet.write(0, 11, 'Otros conceptos IVA')
		sheet.write(0, 12, 'Total')
		sheet.write(0, 13, 'Cobrado')
		sheet.write(0, 14, 'Saldo')
		row = 1
		for partner in records:
			sheet.write(row, 0, partner['partner_id'][0])
			sheet.write(row, 1, partner['partner_id'][1])
			sheet.write(row, 2, self.env['res.partner'].browse(partner['partner_id'][0]).main_id_number)
			sheet.write(row, 3, partner['capital_tmp'])
			sheet.write(row, 4, partner['interes_tmp'])
			sheet.write(row, 5, partner['interes_iva_tmp'])
			sheet.write(row, 6, partner['punitorio_tmp'])
			sheet.write(row, 7, partner['punitorio_iva_tmp'])
			sheet.write(row, 8, partner['seguro_tmp'])
			sheet.write(row, 9, partner['seguro_iva_tmp'])
			sheet.write(row, 10, partner['ajuste_tmp'])
			sheet.write(row, 11, partner['ajuste_iva_tmp'])
			sheet.write(row, 12, partner['total_tmp'])
			sheet.write(row, 13, partner['cobrado_tmp'])
			sheet.write(row, 14, partner['saldo_tmp'])
			row += 1
		book.save(stream)
		self.file2 = base64.encodestring(stream.getvalue())
		return {'type': 'ir.actions.do_nothing'}