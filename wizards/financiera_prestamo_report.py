# -*- coding: utf-8 -*-

from openerp import fields, models, api
import xlwt
import base64
import StringIO
import json
class FinancieraPrestamoReport(models.TransientModel):
	_name = 'financiera.prestamo.report'
	_description = 'Reporte de Prestamos'

	date_init = fields.Date("Fecha desde")
	date_finish = fields.Date("Fecha hasta")
	state = fields.Selection([
		('["acreditado","precancelado","refinanciado","pagado","incobrable"]', 'Prestamos otorgados'),
		('["acreditado"]', 'Prestamos activos'),
		('["precancelado"]', 'Prestamos precancelados'),
		('["refinanciado"]', 'Prestamos refinanciados'),
		('["pagado"]', 'Prestamos pagados'),
		('["incobrable"]', 'Prestamos incobrables'),], 'Estados', default='["acreditado","precancelado","refinanciado","pagado","incobrable"]')
	file = fields.Binary('Archivo excel')
	file_name = fields.Char('Nombre', default='Reporte Prestamos.xls')

	@api.multi
	def print_report(self):
		prestamo_obj = self.pool.get('financiera.prestamo')
		prestamo_ids = prestamo_obj.search(self.env.cr, self.env.uid, [
			('company_id', '=', self.env.user.company_id.id),
			('state', 'in', json.loads(self.state)),
			('fecha', '>=', self.date_init),
			('fecha', '<=', self.date_finish)])
		records = self.env['financiera.prestamo'].browse(prestamo_ids)
		self.generate_excel(records)
		return self.env['report'].get_action(records, 'financiera_tablero_control.prestamo_report_pdf_view')

	@api.multi
	def generate_excel(self, records):
		stream = StringIO.StringIO()
		book = xlwt.Workbook(encoding='utf-8')
		sheet = book.add_sheet(u'Reporte Prestamos')
		sheet.write(0, 0, 'Creado')
		sheet.write(0, 1, 'Cliente')
		sheet.write(0, 2, 'Fecha')
		sheet.write(0, 3, 'PMO')
		sheet.write(0, 4, 'Tipo')
		sheet.write(0, 5, 'Responsable')
		sheet.write(0, 6, 'Monto Solicitado')
		sheet.write(0, 7, 'Saldo')
		sheet.write(0, 8, 'Plan')
		sheet.write(0, 9, 'Entidad')
		sheet.write(0, 10, 'Estado')
		sheet.write(0, 11, 'Origen')
		row = 1
		for prestamo_id in records:
			sheet.write(row, 0, prestamo_id.create_date)
			sheet.write(row, 1, prestamo_id.partner_id.name)
			sheet.write(row, 2, prestamo_id.fecha)
			sheet.write(row, 3, prestamo_id.name)
			sheet.write(row, 4, prestamo_id.prestamo_tipo_id.name)
			sheet.write(row, 5, prestamo_id.responsable_id.name)
			sheet.write(row, 6, prestamo_id.monto_solicitado)
			sheet.write(row, 7, prestamo_id.saldo)
			sheet.write(row, 8, prestamo_id.plan_id.name)
			sheet.write(row, 9, prestamo_id.sucursal_id.name)
			sheet.write(row, 10, prestamo_id.state)
			sheet.write(row, 11, prestamo_id.origen_id.name)
			row += 1
		book.save(stream)
		self.file = base64.encodestring(stream.getvalue())
		return {'type': 'ir.actions.do_nothing'}