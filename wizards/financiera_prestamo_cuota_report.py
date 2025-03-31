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
		('["activa","judicial","precancelada","cobrada","cobrada_con_reintegro"]','Toda la cartera'),
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
		sheet.write(0, 26, 'Nacimiento (ROL)')
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
			if cuota_id.partner_id.rol_variable_ids:
				fecha_nacimiento = cuota_id.partner_id.get_variable_name('persona_fecha_nacimiento')
				sheet.write(row, 26, fecha_nacimiento.valor if fecha_nacimiento else '-')
			else:
				sheet.write(row, 26, '-')
			row += 1
		book.save(stream)
		self.file = base64.encodestring(stream.getvalue())
		return {'type': 'ir.actions.do_nothing'}

	@api.multi
	def print_rol_report(self):
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
		self.generate_rol_excel(records)
		return {'type': 'ir.actions.do_nothing'}


	@api.multi
	def generate_rol_excel(self, records):
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
		sheet.write(0, 26, 'Ingreso')
		sheet.write(0, 27, 'Nivel de estudio')
		sheet.write(0, 28, 'Tipo de Vivienda')
		sheet.write(0, 29, 'Alquiler')
		sheet.write(0, 30, 'Hijos que conviven')
		sheet.write(0, 31, 'Medio de transporte frecuente')
		sheet.write(0, 32, 'Tiene un vehiculo a su nombre')
		sheet.write(0, 33, 'Modelo del vehiculo')
		sheet.write(0, 34, 'Persona Jubilado Beneficio (ROL)')
		sheet.write(0, 35, 'Persona Estado CUIT (ROL)')
		sheet.write(0, 36, 'Persona Jubilado (ROL)')
		sheet.write(0, 37, 'Persona PEP (ROL)')
		sheet.write(0, 38, 'Persona Clase (ROL)')
		sheet.write(0, 39, 'Persona Sexo (ROL)')
		sheet.write(0, 40, 'Persona Edad (ROL)')
		sheet.write(0, 41, 'Persona Tipo (ROL)')
		sheet.write(0, 42, 'Persona Fallecido (ROL)')
		sheet.write(0, 43, 'Actividad Empleado Publico')
		sheet.write(0, 44, 'Perfil Letra')
		sheet.write(0, 45, 'Ingresos NSE')
		sheet.write(0, 46, 'Bancarizacion sin mora meses')
		sheet.write(0, 47, 'Bancarizacion sin mora desde')
		sheet.write(0, 48, 'AFIP en linea forma juridica')
		sheet.write(0, 49, 'Empleador periodo')
		sheet.write(0, 50, 'Empleador empleados')
		sheet.write(0, 51, 'Autonomo categoria')
		sheet.write(0, 52, 'Autonomo hasta')
		sheet.write(0, 53, 'Autonomo desde')
		sheet.write(0, 54, 'ANSSES Prestacion Provincial')
		sheet.write(0, 55, 'ANSSES Asignacion Universal')
		sheet.write(0, 56, 'ANSSES Prestacion Nacional')
		sheet.write(0, 57, 'ANSSES Trabajador Casa Particular')
		sheet.write(0, 58, 'ANSSES Progresar')
		sheet.write(0, 59, 'ANSSES Prestacion Desempleo')
		sheet.write(0, 60, 'ANSSES Plan Social')
		sheet.write(0, 61, 'Actividad AFIP 1 Descripcion')
		sheet.write(0, 62, 'Actividad AFIP 1 Codigo')
		sheet.write(0, 63, 'Actividad AFIP 1 Formulario')
		sheet.write(0, 64, 'Actividad AFIP 1 Principal')
		sheet.write(0, 65, 'Condicion Tributaria 1 IVA')
		sheet.write(0, 66, 'Condicion Tributaria 1 Actividad')
		sheet.write(0, 67, 'Condicion Tributaria 1 Monotributo')
		sheet.write(0, 68, 'Condicion Tributaria 1 Hasta')
		sheet.write(0, 69, 'Condicion Tributaria 1 Desde')
		sheet.write(0, 70, 'Condicion Tributaria 1 Empleador')
		sheet.write(0, 71, 'Condicion Tributaria 1 Ganancias')
		sheet.write(0, 72, 'Plan')
		sheet.write(0, 73, 'Monto')
		sheet.write(0, 74, 'Zona')
		sheet.write(0, 75, 'Metodo de pago')


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
			sheet.write(row, 26, cuota_id.partner_id.app_ingreso)
			sheet.write(row, 27, cuota_id.partner_id.app_nivel_estudio)
			sheet.write(row, 28, cuota_id.partner_id.app_vivienda)
			sheet.write(row, 29, cuota_id.partner_id.app_alquiler)
			sheet.write(row, 30, cuota_id.partner_id.app_vivienda_hijos)
			sheet.write(row, 31, cuota_id.partner_id.app_transporte)
			sheet.write(row, 32, cuota_id.partner_id.app_vehiculo)
			sheet.write(row, 33, cuota_id.partner_id.app_vehiculo_modelo)
			if cuota_id.partner_id.rol_variable_ids:
				persona_jubilado_beneficio = cuota_id.partner_id.get_variable_name('persona_jubilado_beneficio')
				sheet.write(row, 34, persona_jubilado_beneficio.valor if persona_jubilado_beneficio else '')
			if cuota_id.partner_id.rol_variable_ids:
				persona_estado_cuit = cuota_id.partner_id.get_variable_name('persona_estado_cuit')
				sheet.write(row, 35, persona_estado_cuit.valor if persona_estado_cuit else '')
			if cuota_id.partner_id.rol_variable_ids:
				persona_jubilado = cuota_id.partner_id.get_variable_name('persona_jubilado')
				sheet.write(row, 36, persona_jubilado.valor if persona_jubilado else '')
			if cuota_id.partner_id.rol_variable_ids:
				persona_pep = cuota_id.partner_id.get_variable_name('persona_pep')
				sheet.write(row, 37, persona_pep.valor if persona_pep else '')
			if cuota_id.partner_id.rol_variable_ids:
				persona_clase = cuota_id.partner_id.get_variable_name('persona_clase')
				sheet.write(row, 38, persona_clase.valor if persona_clase else '')
			if cuota_id.partner_id.rol_variable_ids:
				persona_sexo = cuota_id.partner_id.get_variable_name('persona_sexo')
				sheet.write(row, 39, persona_sexo.valor if persona_sexo else '')
			if cuota_id.partner_id.rol_variable_ids:
				persona_edad = cuota_id.partner_id.get_variable_name('persona_edad')
				sheet.write(row, 40, persona_edad.valor if persona_edad else '')
			if cuota_id.partner_id.rol_variable_ids:
				persona_tipo = cuota_id.partner_id.get_variable_name('persona_tipo')
				sheet.write(row, 41, persona_tipo.valor if persona_tipo else '')
			if cuota_id.partner_id.rol_variable_ids:
				persona_fallecido = cuota_id.partner_id.get_variable_name('persona_fallecido')
				sheet.write(row, 42, persona_fallecido.valor if persona_fallecido else '')
			if cuota_id.partner_id.rol_variable_ids:
				actividad_empleado_publico = cuota_id.partner_id.get_variable_name('actividad_empleado_publico')
				sheet.write(row, 43, actividad_empleado_publico.valor if actividad_empleado_publico else '')
			if cuota_id.partner_id.rol_variable_ids:
				perfil_letra = cuota_id.partner_id.get_variable_name('perfil_letra')
				sheet.write(row, 44, perfil_letra.valor if perfil_letra else '')
			if cuota_id.partner_id.rol_variable_ids:
				ingresos_nse = cuota_id.partner_id.get_variable_name('ingresos_nse')
				sheet.write(row, 45, ingresos_nse.valor if ingresos_nse else '')
			if cuota_id.partner_id.rol_variable_ids:
				bancarizacion_sin_mora_meses = cuota_id.partner_id.get_variable_name('bancarizacion_sin_mora_meses')
				sheet.write(row, 46, bancarizacion_sin_mora_meses.valor if bancarizacion_sin_mora_meses else '')
			if cuota_id.partner_id.rol_variable_ids:
				bancarizacion_sin_mora_desde = cuota_id.partner_id.get_variable_name('bancarizacion_sin_mora_desde')
				sheet.write(row, 47, bancarizacion_sin_mora_desde.valor if bancarizacion_sin_mora_desde else '')
			if cuota_id.partner_id.rol_variable_ids:
				afip_en_linea_forma_juridica = cuota_id.partner_id.get_variable_name('afip_en_linea_forma_juridica')
				sheet.write(row, 48, afip_en_linea_forma_juridica.valor if afip_en_linea_forma_juridica else '')
			if cuota_id.partner_id.rol_variable_ids:
				empleador_periodo = cuota_id.partner_id.get_variable_name('empleador_periodo')
				sheet.write(row, 49, empleador_periodo.valor if empleador_periodo else '')
			if cuota_id.partner_id.rol_variable_ids:
				empleador_empleados = cuota_id.partner_id.get_variable_name('empleador_empleados')
				sheet.write(row, 50, empleador_empleados.valor if empleador_empleados else '')
			if cuota_id.partner_id.rol_variable_ids:
				autonomo_categoria = cuota_id.partner_id.get_variable_name('autonomo_categoria')
				sheet.write(row, 51, autonomo_categoria.valor if autonomo_categoria else '')
			if cuota_id.partner_id.rol_variable_ids:
				autonomo_hasta = cuota_id.partner_id.get_variable_name('autonomo_hasta')
				sheet.write(row, 52, autonomo_hasta.valor if autonomo_hasta else '')
			if cuota_id.partner_id.rol_variable_ids:
				autonomo_desde = cuota_id.partner_id.get_variable_name('autonomo_desde')
				sheet.write(row, 53, autonomo_desde.valor if autonomo_desde else '')
			if cuota_id.partner_id.rol_variable_ids:
				anses_prestacion_provincial = cuota_id.partner_id.get_variable_name('anses_prestacion_provincial')
				sheet.write(row, 54, anses_prestacion_provincial.valor if anses_prestacion_provincial else '')
			if cuota_id.partner_id.rol_variable_ids:
				anses_asignacion_universal = cuota_id.partner_id.get_variable_name('anses_asignacion_universal')
				sheet.write(row, 55, anses_asignacion_universal.valor if anses_asignacion_universal else '')
			if cuota_id.partner_id.rol_variable_ids:
				anses_prestacion_nacional = cuota_id.partner_id.get_variable_name('anses_prestacion_nacional')
				sheet.write(row, 56, anses_prestacion_nacional.valor if anses_prestacion_nacional else '')
			if cuota_id.partner_id.rol_variable_ids:
				anses_trabajador_casa_particular = cuota_id.partner_id.get_variable_name('anses_trabajador_casa_particular')
				sheet.write(row, 57, anses_trabajador_casa_particular.valor if anses_trabajador_casa_particular else '')
			if cuota_id.partner_id.rol_variable_ids:
				anses_progresar = cuota_id.partner_id.get_variable_name('anses_progresar')
				sheet.write(row, 58, anses_progresar.valor if anses_progresar else '')
			if cuota_id.partner_id.rol_variable_ids:
				anses_prestacion_desempleo = cuota_id.partner_id.get_variable_name('anses_prestacion_desempleo')
				sheet.write(row, 59, anses_prestacion_desempleo.valor if anses_prestacion_desempleo else '')
			if cuota_id.partner_id.rol_variable_ids:
				anses_plan_social = cuota_id.partner_id.get_variable_name('anses_plan_social')
				sheet.write(row, 60, anses_plan_social.valor if anses_plan_social else '')
			if cuota_id.partner_id.rol_variable_ids:
				actividades_afip_1_descripcion = cuota_id.partner_id.get_variable_name('actividades_afip_1_descripcion')
				sheet.write(row, 61, actividades_afip_1_descripcion.valor if actividades_afip_1_descripcion else '')
			if cuota_id.partner_id.rol_variable_ids:
				actividades_afip_1_codigo = cuota_id.partner_id.get_variable_name('actividades_afip_1_codigo')
				sheet.write(row, 62, actividades_afip_1_codigo.valor if actividades_afip_1_codigo else '')
			if cuota_id.partner_id.rol_variable_ids:
				actividades_afip_1_formulario = cuota_id.partner_id.get_variable_name('actividades_afip_1_formulario')
				sheet.write(row, 63, actividades_afip_1_formulario.valor if actividades_afip_1_formulario else '')
			if cuota_id.partner_id.rol_variable_ids:
				actividades_afip_1_principal = cuota_id.partner_id.get_variable_name('actividades_afip_1_principal')
				sheet.write(row, 64, actividades_afip_1_principal.valor if actividades_afip_1_principal else '')
			if cuota_id.partner_id.rol_variable_ids:
				condicion_tributaria_1_iva = cuota_id.partner_id.get_variable_name('condicion_tributaria_1_iva')
				sheet.write(row, 65, condicion_tributaria_1_iva.valor if condicion_tributaria_1_iva else '')
			if cuota_id.partner_id.rol_variable_ids:
				condicion_tributaria_1_actividad = cuota_id.partner_id.get_variable_name('condicion_tributaria_1_actividad')
				sheet.write(row, 66, condicion_tributaria_1_actividad.valor if condicion_tributaria_1_actividad else '')
			if cuota_id.partner_id.rol_variable_ids:
				condicion_tributaria_1_monotributo = cuota_id.partner_id.get_variable_name('condicion_tributaria_1_monotributo')
				sheet.write(row, 67, condicion_tributaria_1_monotributo.valor if condicion_tributaria_1_monotributo else '')
			if cuota_id.partner_id.rol_variable_ids:
				condicion_tributaria_1_hasta = cuota_id.partner_id.get_variable_name('condicion_tributaria_1_hasta')
				sheet.write(row, 68, condicion_tributaria_1_hasta.valor if condicion_tributaria_1_hasta else '')
			if cuota_id.partner_id.rol_variable_ids:
				condicion_tributaria_1_desde = cuota_id.partner_id.get_variable_name('condicion_tributaria_1_desde')
				sheet.write(row, 69, condicion_tributaria_1_desde.valor if condicion_tributaria_1_desde else '')
			if cuota_id.partner_id.rol_variable_ids:
				condicion_tributaria_1_empleador = cuota_id.partner_id.get_variable_name('condicion_tributaria_1_empleador')
				sheet.write(row, 70, condicion_tributaria_1_empleador.valor if condicion_tributaria_1_empleador else '')
			if cuota_id.partner_id.rol_variable_ids:
				condicion_tributaria_1_ganancias = cuota_id.partner_id.get_variable_name('condicion_tributaria_1_ganancias')
				sheet.write(row, 71, condicion_tributaria_1_ganancias.valor if condicion_tributaria_1_ganancias else '')
			if cuota_id.prestamo_id.plan_id:
				sheet.write(row, 72, cuota_id.prestamo_id.plan_id.name)
			if cuota_id.prestamo_id.monto_solicitado:
				sheet.write(row, 73, cuota_id.prestamo_id.monto_solicitado)
			if cuota_id.partner_id.city:
				sheet.write(row, 74, cuota_id.partner_id.city)
			if cuota_id.payment_ids:
				sheet.write(row, 75, cuota_id.payment_ids[0].journal_id.name)
			row += 1
		book.save(stream)
		self.file = base64.encodestring(stream.getvalue())
		return {'type': 'ir.actions.do_nothing'}