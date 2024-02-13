# -*- coding: utf-8 -*-

from openerp import fields, models, api
import xlwt
import base64
import StringIO
import json

class FinancieraPrestamoCuotaReport(models.TransientModel):
	_name = 'financiera.prestamo.cuota.report'
	_description = 'Reporte de Cuotas'

	date_init = fields.Date("Fecha desde")
	date_finish = fields.Date("Fecha hasta")
	state = fields.Selection([
		('["activa"]', 'Cuotas activas'),
		('["activa","judicial"]', 'Cuotas activas y judiciales'),
		('["precancelada"]', 'Cuotas precanceladas'),
		('["cobrada","cobrada_con_reintegro"]', 'Cuotas cobradas'),
		('["refinanciada"]', 'Cuotas refinanciadas'),
		('["judicial"]', 'Cuotas en estado judicial'),
		('["incobrable"]', 'Cuotas incobrables'),
	], 'Estados', default='["activa"]')
	file = fields.Binary('Archivo excel')
	file_name = fields.Char('Nombre', default='Reporte Cuotas.xls')

	@api.multi
	def print_report(self):
		print("print_report")
		prestamo_cuota_obj = self.pool.get('financiera.prestamo.cuota')
		domain_date = []
		if self.date_init:
			domain_date.append(('fecha_vencimiento', '>=', self.date_init))
		if self.date_finish:
			domain_date.append(('fecha_vencimiento', '<=', self.date_finish))
		print("domain_date: ", domain_date)
		prestamo_cuota_ids = prestamo_cuota_obj.search(self.env.cr, self.env.uid, [
			('company_id', '=', self.env.user.company_id.id),
			('state', 'in', json.loads(self.state))] + domain_date)
		records = self.env['financiera.prestamo.cuota'].browse(prestamo_cuota_ids)
		print("records: ", records)
		self.generate_excel(records)
		return {'type': 'ir.actions.do_nothing'}


	@api.multi
	def generate_excel(self, records):
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
		sheet.write(0, 20, 'Reintegro')
		sheet.write(0, 21, 'Saldo')
		sheet.write(0, 22, 'Sucursal')
		sheet.write(0, 23, 'Facturada')
		sheet.write(0, 24, 'Estado')
		sheet.write(0, 25, 'Estado mora')
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
			sheet.write(row, 12, cuota_id.punitorio)
			sheet.write(row, 13, cuota_id.punitorio_iva)
			sheet.write(row, 14, cuota_id.seguro)
			sheet.write(row, 15, cuota_id.seguro_iva)
			sheet.write(row, 16, cuota_id.ajuste)
			sheet.write(row, 17, cuota_id.ajuste_iva)
			sheet.write(row, 18, cuota_id.total)
			sheet.write(row, 19, cuota_id.cobrado)
			sheet.write(row, 20, cuota_id.reintegro)
			sheet.write(row, 21, cuota_id.saldo)
			sheet.write(row, 22, cuota_id.sucursal_id.name)
			sheet.write(row, 23, cuota_id.facturada)
			sheet.write(row, 24, cuota_id.state)
			sheet.write(row, 25, cuota_id.state_mora)
			row += 1
		book.save(stream)
		self.file = base64.encodestring(stream.getvalue())
		return {'type': 'ir.actions.do_nothing'}