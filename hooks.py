from odoo import api, SUPERUSER_ID

HOMEPAGE_URL = '/evolucionai'


def setup_method_website(env):
    """Sitio web 'Method': limpia el dominio (evita redirecciones en local) y usa la landing de EvolucionAI como inicio."""
    websites = env['website'].search([('name', '=', 'Method')])
    websites.write({'domain': False, 'homepage_url': HOMEPAGE_URL})


def post_init_hook(cr, registry):
    setup_method_website(api.Environment(cr, SUPERUSER_ID, {}))
