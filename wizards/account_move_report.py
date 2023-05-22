# -*- coding: utf-8 -*-

from openerp import fields, models, api
import xlwt
import base64
import StringIO
import json

class AccountMoveReport(models.TransientModel):
	_name = 'account.move.report'
	_description = 'Reporte de Asientos contables'

	date_init = fields.Date("Fecha desde")
	date_finish = fields.Date("Fecha hasta")
	file = fields.Binary('Archivo excel')
	file_name = fields.Char('Nombre', default='Reporte de asientos.xls')

	@api.multi
	def print_report(self):
		move_obj = self.pool.get('account.move')
		move_ids = move_obj.search(self.env.cr, self.env.uid, [
			('company_id', '=', self.env.user.company_id.id),
			('state', '=', 'posted'),
			('date', '>=', self.date_init),
			('date', '<=', self.date_finish)])
		records = self.env['account.move'].browse(move_ids)
		return self.env['report'].get_action(records, 'financiera_tablero_control.move_report_pdf_view')

	# @api.multi
	# def generate_excel(self, records):
	# 	stream = StringIO.StringIO()
	# 	book = xlwt.Workbook(encoding='utf-8')
	# 	sheet = book.add_sheet(u'Reporte moves')
	# 	sheet.write(0, 0, 'Creado')
	# 	sheet.write(0, 1, 'Cliente')
	# 	sheet.write(0, 2, 'Fecha')
	# 	sheet.write(0, 3, 'PMO')
	# 	sheet.write(0, 4, 'Tipo')
	# 	sheet.write(0, 5, 'Responsable')
	# 	sheet.write(0, 6, 'Monto Solicitado')
	# 	sheet.write(0, 7, 'Saldo')
	# 	sheet.write(0, 8, 'Plan')
	# 	sheet.write(0, 9, 'Entidad')
	# 	sheet.write(0, 10, 'Estado')
	# 	sheet.write(0, 11, 'Origen')
	# 	row = 1
	# 	for move_id in records:
	# 		sheet.write(row, 0, move_id.create_date)
	# 		sheet.write(row, 1, move_id.partner_id.name)
	# 		sheet.write(row, 2, move_id.fecha)
	# 		sheet.write(row, 3, move_id.name)
	# 		sheet.write(row, 4, move_id.move_tipo_id.name)
	# 		sheet.write(row, 5, move_id.responsable_id.name)
	# 		sheet.write(row, 6, move_id.monto_solicitado)
	# 		sheet.write(row, 7, move_id.saldo)
	# 		sheet.write(row, 8, move_id.plan_id.name)
	# 		sheet.write(row, 9, move_id.sucursal_id.name)
	# 		sheet.write(row, 10, move_id.state)
	# 		sheet.write(row, 11, move_id.origen_id.name)
	# 		row += 1
	# 	book.save(stream)
	# 	self.file = base64.encodestring(stream.getvalue())
	# 	return {'type': 'ir.actions.do_nothing'}