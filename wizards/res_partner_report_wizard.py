# -*- coding: utf-8 -*-

from openerp import fields, models, api
import xlwt
import base64
import StringIO

class ResPartnerReportWizard(models.TransientModel):
	_name = 'res.partner.report.wizard'
	_description = 'Reporte de Clientes'

	balance_date = fields.Date("Saldos a la fecha")
	file_pdf = fields.Binary('Archivo PDF')
	file_name_pdf = fields.Char('Nombre', default='Saldo Clientes.pdf')
	file = fields.Binary('Archivo excel')
	file_name = fields.Char('Nombre', default='Saldo Clientes.xls')

	@api.multi
	def print_report(self):
		partner_obj = self.pool.get('res.partner')
		partner_ids = partner_obj.search(self.env.cr, self.env.uid, [
			('company_id', '=', self.env.user.company_id.id),
			('cuota_ids.state', 'in', ['activa']),
			('fecha_vencimiento', '<=', self.balance_date),
		])
		records = self.env['res.partner'].browse(partner_ids)
		for partner_id in records:
			partner_id.set_saldos_reporte(self.balance_date)
		self.generate_excel(records)
		# data = {'balance_date': self.balance_date}
		report = self.env['report'].get_action(records, 'financiera_tablero_control.partner_report_pdf_view')#, data=data)
		# self.file_pdf = report
		return report

	@api.multi
	def generate_excel(self, records):
		stream = StringIO.StringIO()
		book = xlwt.Workbook(encoding='utf-8')
		sheet = book.add_sheet(u'Saldo de Clientes')
		sheet.write(0, 0, 'Cliente')
		sheet.write(0, 1, 'Identificacion')
		sheet.write(0, 2, 'Saldo vencido')
		sheet.write(0, 3, 'Saldo no vencido')
		sheet.write(0, 4, 'Saldo total')
		row = 1
		for partner_id in records:
			sheet.write(row, 0, partner_id.name)
			sheet.write(row, 1, partner_id.main_id_number)
			sheet.write(row, 2, partner_id.saldo_vencido)
			sheet.write(row, 3, partner_id.saldo_no_vencido)
			sheet.write(row, 4, partner_id.saldo_total)
			row +=1
		book.save(stream)
		self.file = base64.encodestring(stream.getvalue())
		self.actualizar_datos = False
		return {'type': 'ir.actions.do_nothing'}
