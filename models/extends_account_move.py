# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ExtendsAccountMove(models.Model):
	_name = 'account.move'
	_inherit = 'account.move'

	nro_asiento = fields.Integer('Nro. Asiento', default=1)