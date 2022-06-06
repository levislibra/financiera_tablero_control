# -*- coding: utf-8 -*-

from openerp import fields, models, api
import xlwt
import base64
import StringIO

class ResPartnerPrestamoReportWizard(models.TransientModel):
	_name = 'res.partner.prestamo.report.wizard'
	_description = 'Reporte de Saldo de Clientes por prestamos'

	balance_date = fields.Date("Saldos a la fecha")
	file_pdf = fields.Binary('Archivo PDF')
	file_name_pdf = fields.Char('Nombre', default='Saldo Clientes.pdf')
	file = fields.Binary('Archivo excel')
	file_name = fields.Char('Nombre', default='Saldo Clientes.xls')

	@api.multi
	def print_report(self):
		prestamo_obj = self.pool.get('financiera.prestamo')
		prestamo_ids = prestamo_obj.search(self.env.cr, self.env.uid, [
			('company_id', '=', self.env.user.company_id.id),
			('state', 'in', ['acreditado']),
			('cuota_ids.fecha_vencimiento', '<=', self.balance_date)
		])
		records = self.env['financiera.prestamo'].browse(prestamo_ids)
		for partner_id in records:
			partner_id.set_saldos_reporte(self.balance_date)
		self.generate_excel(records)
		report = self.env['report'].get_action(records, 'financiera_tablero_control.partner_prestamo_report_pdf_view')
		return report

	@api.multi
	def generate_excel(self, records):
		stream = StringIO.StringIO()
		book = xlwt.Workbook(encoding='utf-8')
		sheet = book.add_sheet(u'Saldo de Clientes')
		sheet.write(0, 0, 'Fecha')
		sheet.write(0, 1, 'PMO')
		sheet.write(0, 2, 'Clente')
		sheet.write(0, 3, 'Identificacion')
		sheet.write(0, 4, 'Entidad')
		sheet.write(0, 5, 'Saldo vencido')
		row = 1
		for prestamo_id in records:
			sheet.write(row, 0, prestamo_id.fecha)
			sheet.write(row, 1, prestamo_id.name)
			sheet.write(row, 2, prestamo_id.partner_id.name)
			sheet.write(row, 3, prestamo_id.partner_id.main_id_number)
			sheet.write(row, 4, prestamo_id.sucursal_id.name)
			sheet.write(row, 5, prestamo_id.reporte_saldo_vencido)
			row +=1
		book.save(stream)
		self.file = base64.encodestring(stream.getvalue())
		self.actualizar_datos = False
		return {'type': 'ir.actions.do_nothing'}
