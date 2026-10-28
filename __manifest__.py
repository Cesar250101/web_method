{
    'name': 'Web Method',
    'version': '16.0.2.0.1',
    'summary': 'Sitio web EvolucionAI (landings y snippets editables) y métodos web',
    'description': 'Sitio web de EvolucionAI v9.7: ocho landings editables desde el editor de Odoo, '
                   'ocho snippets y formularios nativos de CRM. Incluye controladores HTTP de apoyo.',
    'category': 'Technical',
    'license': 'LGPL-3',
    'author': 'EvolucionAI',
    'website': 'https://evolucionai.cl',
    'depends': [
        'base',
        'web',
        'website',
        'website_crm',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/website_config.xml',
        'views/snippets.xml',
        'views/pages.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'web_method/static/src/css/evolucionai.css',
            'web_method/static/src/js/evolucionai.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}
