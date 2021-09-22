# -*- coding: utf-8 -*-

from openerp import fields, models, api
import xlwt
import base64
import StringIO

class ResPartnerReportWizard(models.TransientModel):
	_name = 'res.partner.report.wizard'
	_description = 'Reporte de Clientes'

	balance_date = fields.Date("Saldos a la fecha")
	actualizar_datos = fields.Boolean("Actualizar datos", default=True)
	file_pdf = fields.Binary('Archivo PDF')
	file_name_pdf = fields.Char('Nombre', default='Saldo Clientes.pdf')
	file = fields.Binary('Archivo excel')
	file_name = fields.Char('Nombre', default='Saldo Clientes.xls')

	@api.one
	@api.onchange('balance_date')
	def onchange_balance_date(self):
		self.actualizar_datos = True

	@api.multi
	def print_report(self):
		partner_obj = self.pool.get('res.partner')
		partner_ids = partner_obj.search(self.env.cr, self.env.uid, [
			('cuota_ids.state', 'in', ['activa'])
		])
		records = self.env['res.partner'].browse(partner_ids)
		if self.actualizar_datos:
			for partner_id in records:
				partner_id.set_saldos_reporte(self.balance_date)
		self.actualizar_datos = False
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
		sheet.write(0, 3, 'Facturacion sobre saldo vencido')
		sheet.write(0, 4, 'Saldo no vencido')
		sheet.write(0, 5, 'Saldo total')
		row = 1
		for partner_id in records:
			col = 0
			while col <= 5:
				if col == 0:
					sheet.write(row, col, partner_id.name)
				elif col == 1:
					sheet.write(row, col, partner_id.main_id_number)
				elif col == 2:
					sheet.write(row, col, partner_id.saldo_vencido)
				elif col == 3:
					sheet.write(row, col, partner_id.facturado_sobre_saldo_vencido)
				elif col == 4:
					sheet.write(row, col, partner_id.saldo_no_vencido)
				elif col == 5:
					sheet.write(row, col, partner_id.saldo_total)
				col += 1
			row +=1
		book.save(stream)
		self.file = base64.encodestring(stream.getvalue())
		self.actualizar_datos = False
		return {'type': 'ir.actions.do_nothing'}
