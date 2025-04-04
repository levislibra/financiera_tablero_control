# -*- coding: utf-8 -*-
{
    'name': "Financiera Tablero de Control",

    'summary': """
        Informacion sobre Prestamos, Cuotas, Clientes, Cobros...""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Librasoft",
    'website': "https://libra-soft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'financiera',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'financiera_prestamos','financiera_cobranza_mora','financiera_app','financiera_buro_rol_base'],

    # always loaded
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
		'views/extends_account_move.xml',
        'views/financiera_prestamo_cuota.xml',
        'views/financiera_prestamo.xml',
        'views/financiera_tablero.xml',
		'views/extends_res_partner.xml',
        'views/financiera_servicios.xml',
        'views/views.xml',
        'wizards/financiera_prestamo_report.xml',
        'wizards/financiera_prestamo_detalle_report.xml',
        'wizards/res_partner_report_wizard.xml',
        'wizards/res_partner_prestamo_report_wizard.xml',
        'wizards/account_move_report.xml',
		'wizards/financiera_prestamo_cuota_report.xml',
		'wizards/financiera_cartera_report.xml',
		'wizards/res_partner_report_mora_wizard.xml',
    ],
    'css': [
        'static/src/css/tablero_style.css',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}