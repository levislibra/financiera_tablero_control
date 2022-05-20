# -*- coding: utf-8 -*-

from openerp import fields, models, api
import xlwt
import base64
import StringIO
import json
class FinancieraPrestamoReport(models.TransientModel):
	_name = 'financiera.prestamo.detalle.report'
	_description = 'Reporte de Prestamos con Detalle de Cuotas'

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
		data = {
			'date_init': self.date_init,
			'date_finish': self.date_finish,
		}
		return self.env['report'].get_action(records, 'financiera_tablero_control.prestamo_report_pdf_view')

	@api.multi
	def generate_excel(self, records):
		stream = StringIO.StringIO()
		book = xlwt.Workbook(encoding='utf-8')
		sheet = book.add_sheet(u'Reporte Prestamos')
		row = 0
		col = 0
		for prestamo_id in records:
			sheet.write(row, col, 'Fecha')
			sheet.write(row+1, col, 'Codigo')
			sheet.write(row+2, col, 'Cliente')
			sheet.write(row+3, col, 'Identificacion')
			sheet.write(row+4, col, 'Monto Solicitado')
			sheet.write(row+5, col, 'Entidad')
			sheet.write(row+6, col, 'Estado actual')
			
			sheet.write(row, col+1, prestamo_id.fecha)
			sheet.write(row+1, col+1, prestamo_id.name)
			sheet.write(row+2, col+1, prestamo_id.partner_id.name)
			sheet.write(row+3, col+1, prestamo_id.partner_id.main_id_number)
			sheet.write(row+4, col+1, prestamo_id.monto_solicitado)
			sheet.write(row+5, col+1, prestamo_id.sucursal_id.name)
			sheet.write(row+6, col+1, prestamo_id.state)
			# Ahora escribimos las cuotas
			sheet.write(row+8, col, 'Numero de cuota')
			sheet.write(row+8, col+1, 'Fecha')
			sheet.write(row+8, col+2, 'Saldo capital')
			sheet.write(row+8, col+3, 'Capital')
			sheet.write(row+8, col+4, 'Interes')
			sheet.write(row+8, col+5, 'Cuota pura')
			sheet.write(row+8, col+6, 'IVA interes')
			sheet.write(row+8, col+7, 'Punitorio')
			sheet.write(row+8, col+8, 'IVA Punitorio')
			sheet.write(row+8, col+9, 'Seguro')
			sheet.write(row+8, col+10, 'IVA seguro')
			sheet.write(row+8, col+11, 'Otros')
			sheet.write(row+8, col+12, 'IVA otros')
			sheet.write(row+8, col+13, 'Monto cuota')
			sheet.write(row+8, col+14, 'Bonificado / Reintegro')
			sheet.write(row+8, col+15, 'Pago')
			sheet.write(row+8, col+16, 'Saldo')
			sheet.write(row+8, col+17, 'Estado')
			i = 1
			for cuota_id in prestamo_id.cuota_ids:
				sheet.write(row+8+i, col, cuota_id.numero_cuota)
				sheet.write(row+8+i, col+1, cuota_id.fecha_vencimiento)
				sheet.write(row+8+i, col+2, cuota_id.saldo_capital)
				sheet.write(row+8+i, col+3, cuota_id.capital)
				sheet.write(row+8+i, col+4, cuota_id.interes)
				sheet.write(row+8+i, col+5, cuota_id.cuota_pura)
				sheet.write(row+8+i, col+6, cuota_id.interes_iva)
				sheet.write(row+8+i, col+7, cuota_id.punitorio)
				sheet.write(row+8+i, col+8, cuota_id.punitorio_iva)
				sheet.write(row+8+i, col+9, cuota_id.seguro)
				sheet.write(row+8+i, col+10, cuota_id.seguro_iva)
				sheet.write(row+8+i, col+11, cuota_id.ajuste)
				sheet.write(row+8+i, col+12, cuota_id.ajuste_iva)
				sheet.write(row+8+i, col+13, cuota_id.total)
				sheet.write(row+8+i, col+14, cuota_id.reintegro)
				sheet.write(row+8+i, col+15, cuota_id.cobrado)
				sheet.write(row+8+i, col+16, cuota_id.saldo)
				sheet.write(row+8+i, col+17, cuota_id.state)
				i += 1
			row += + 10 + i
		book.save(stream)
		self.file = base64.encodestring(stream.getvalue())
		return {'type': 'ir.actions.do_nothing'}