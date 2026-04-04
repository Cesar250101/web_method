{
    'name': 'Web Method',
    'version': '16.0.1.0.0',
    'summary': 'Módulo para métodos web personalizados',
    'description': 'Módulo base para definir métodos web y controladores HTTP personalizados en Odoo.',
    'category': 'Technical',
    'license': 'LGPL-3',
    'author': '',
    'website': '',
    'depends': [
        'base',
        'web',
        'website',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'web_method/static/src/css/erp_free_trial_button.css',
            'web_method/static/src/js/erp_free_trial_button.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
