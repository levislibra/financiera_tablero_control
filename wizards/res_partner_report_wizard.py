# -*- coding: utf-8 -*-

from openerp import fields, models, api
from datetime import datetime
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
		total_procesados = 0
		balance_date = datetime.strptime(self.balance_date, '%Y-%m-%d')
		while True:
			partner_ids = partner_obj.search(self.env.cr, self.env.uid, [
				('company_id', '=', self.env.user.company_id.id),
				('cuota_ids', '!=', False),
				'|', ('reporte_fecha', '!=', balance_date), ('reporte_fecha', '=', False),
			], limit=400)
			if not partner_ids:
				break
			try:
				records = self.env['res.partner'].browse(partner_ids)
				for partner_id in records:
					partner_id.set_saldos_reporte(self.balance_date)
				self.env.cr.commit()
				total_procesados += len(records)
			except Exception as e:
				self.env.cr.rollback()
		partner_all_ids = partner_obj.search(self.env.cr, self.env.uid, [
			('company_id', '=', self.env.user.company_id.id),
			('cuota_ids', '!=', False)
		])
		partner_all_ids = self.env['res.partner'].browse(partner_all_ids)
		self.generate_excel(partner_all_ids)
		# data = {'balance_date': self.balance_date}
		report = self.env['report'].get_action(partner_all_ids, 'financiera_tablero_control.partner_report_pdf_view')#, data=data)
		# self.file_pdf = report
		return report

	@api.multi
	def generate_excel(self, records):
		stream = StringIO.StringIO()
		book = xlwt.Workbook(encoding='utf-8')
		sheet = book.add_sheet(u'Saldo de Clientes')
		sheet.write(0, 0, 'Cliente')
		sheet.write(0, 1, 'Identificacion')
		sheet.write(0, 2, 'Celular')
		sheet.write(0, 3, 'Email')
		sheet.write(0, 4, 'Saldo vencido')
		sheet.write(0, 5, 'Saldo no vencido')
		sheet.write(0, 6, 'Saldo total')
		sheet.write(0, 7, 'Prestamos activos')
		sheet.write(0, 8, 'Prestamos cobrados')
		sheet.write(0, 9, 'Cuotas activas')
		sheet.write(0, 10, 'Cuotas cobradas')
		sheet.write(0, 11, 'Cuotas sin mora')
		sheet.write(0, 12, 'Cuotas en preventiva')
		sheet.write(0, 13, 'Cuotas en mora temprana')
		sheet.write(0, 14, 'Cuotas en mora media')
		sheet.write(0, 15, 'Cuotas en mora tardia')
		sheet.write(0, 16, 'Cuotas incobrables')
		sheet.write(0, 17, 'Fecha ultimo pago')
		sheet.write(0, 18, 'Dias del ultimo pago')
		sheet.write(0, 19, 'Dias en mora')
		sheet.write(0, 20, 'Segmento de mora')
		sheet.write(0, 21, 'Sucursal')
		sheet.write(0, 22, 'Estudio')
		sheet.write(0, 23, 'Fecha de reporte')
		row = 1
		for partner_id in records:
			sheet.write(row, 0, partner_id.name)
			sheet.write(row, 1, partner_id.main_id_number)
			sheet.write(row, 2, partner_id.mobile)
			sheet.write(row, 3, partner_id.email)
			reporte_saldo_vencido = partner_id.reporte_saldo_vencido if partner_id.reporte_saldo_vencido > 1 else 0
			sheet.write(row, 4, reporte_saldo_vencido)
			sheet.write(row, 5, partner_id.reporte_saldo_no_vencido)
			sheet.write(row, 6, partner_id.reporte_saldo_total)
			sheet.write(row, 7, partner_id.alerta_prestamos_activos)
			sheet.write(row, 8, partner_id.alerta_prestamos_cobrados)
			sheet.write(row, 9, partner_id.alerta_cuotas_activas)
			sheet.write(row, 10, partner_id.alerta_cuotas_cobradas)
			sheet.write(row, 11, partner_id.alerta_cuotas_normal)
			sheet.write(row, 12, partner_id.alerta_cuotas_preventivas)
			sheet.write(row, 13, partner_id.alerta_cuotas_temprana)
			sheet.write(row, 14, partner_id.alerta_cuotas_media)
			sheet.write(row, 15, partner_id.alerta_cuotas_tardia)
			sheet.write(row, 16, partner_id.alerta_cuotas_incobrable)
			sheet.write(row, 17, partner_id.alerta_fecha_ultimo_pago)
			sheet.write(row, 18, partner_id.alerta_dias_ultimo_pago)
			sheet.write(row, 19, partner_id.dias_en_mora)
			sheet.write(row, 20, partner_id.mora_id.name)
			sheet.write(row, 21, partner_id.prestamo_ids[0].sucursal_id.name)
			sheet.write(row, 22, partner_id.cobranza_externa_id.name)
			sheet.write(row, 23, partner_id.reporte_fecha)
			# partner_id.reporte_fecha = False
			row +=1
		book.save(stream)
		self.file = base64.encodestring(stream.getvalue())
		self.actualizar_datos = False
		return {'type': 'ir.actions.do_nothing'}
