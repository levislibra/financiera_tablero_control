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
    'depends': ['base', 'financiera_prestamos'],

    # always loaded
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
				'views/financiera_prestamo_cuota.xml',
				'views/financiera_prestamo.xml',
				'views/financiera_tablero.xml',
        'views/views.xml',
				'reports/generic_reports.xml',
				'wizards/financiera_prestamo_report.xml',
				'wizards/res_partner_report_wizard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}