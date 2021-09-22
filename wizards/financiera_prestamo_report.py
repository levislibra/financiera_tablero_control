# -*- coding: utf-8 -*-

from openerp import fields, models, api

class FinancieraPrestamoReport(models.TransientModel):
	_name = 'financiera.prestamo.report'
	_description = 'Reporte de Prestamos'

	date_init = fields.Date("Fecha desde")
	date_finish = fields.Date("Fecha hasta")

	@api.multi
	def print_report(self):
		prestamo_obj = self.pool.get('financiera.prestamo')
		prestamo_ids = prestamo_obj.search(self.env.cr, self.env.uid, [
			# ('state', '=', 'acreditado'),
			('fecha', '>=', self.date_init),
			('fecha', '<=', self.date_finish)])
		print("prestamo_ids: ", prestamo_ids)
		records = self.env['financiera.prestamo'].browse(prestamo_ids)
		print("records: ", records)
		# data = {'date_init': self.date_init, 'date_finish': self.date_finish}
		return self.env['report'].get_action(records, 'financiera_tablero_control.prestamo_report_pdf_view')#, data=data)
