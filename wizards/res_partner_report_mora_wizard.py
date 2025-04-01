# -*- coding: utf-8 -*-

from openerp import fields, models, api
from datetime import datetime
import xlwt
import base64
import StringIO


class ResPartnerReportMoraWizard(models.TransientModel):
	_name = 'res.partner.report.mora.wizard'
	_description = 'Reporte de mora de Clientes'

	file = fields.Binary('Archivo excel')
	file_name = fields.Char('Nombre', default='Mora Clientes.xls')

	@api.multi
	def print_report(self):
		segmento_mora_ids = self.env['res.partner.mora'].search([
			('activo', '=', True),
			('company_id', '=', self.env.user.company_id.id),
		], order='orden asc')
		self.generate_excel(segmento_mora_ids)
		report = self.env['report'].get_action(segmento_mora_ids, 'financiera_tablero_control.partner_report_mora_pdf_view')#, data=data)
		return report

	@api.multi
	def generate_excel(self, records):
		stream = StringIO.StringIO()
		book = xlwt.Workbook(encoding='utf-8')
		# Crear estilo para mostrar número con separador de miles y dos decimales
		style_num = xlwt.XFStyle()
		style_num.num_format_str = '#,##0.00'
		sheet = book.add_sheet(u'Saldo de Clientes')
		sheet.write(0, 0, 'Segmento')
		sheet.write(0, 1, 'Monto de la cartera')
		sheet.write(0, 2, 'Porcentaje de la cartera')
		sheet.write(0, 3, 'Número de cliente')
		row = 1
		total_cartera = 0.0
		total_porcentaje = 0.0
		for segmento_mora_id in records:
			sheet.write(row, 0, segmento_mora_id.name)
			sheet.write(row, 1, segmento_mora_id.monto, style_num)
			total_cartera += segmento_mora_id.monto
			sheet.write(row, 2, segmento_mora_id.porcentaje)
			total_porcentaje += segmento_mora_id.porcentaje
			sheet.write(row, 3, segmento_mora_id.partner_cantidad)
			row +=1
		# Write total
		if total_cartera > 0:
			sheet.write(row, 0, u'Total Cartera')
			sheet.write(row, 1, total_cartera, style_num)
			sheet.write(row, 2, total_porcentaje)
			sheet.write(row, 3, sum([segmento_mora_id.partner_cantidad for segmento_mora_id in records])) # Total de clientes en todos los segmentos
			row += 1
		book.save(stream)
		self.file = base64.encodestring(stream.getvalue())
		return {'type': 'ir.actions.do_nothing'}
