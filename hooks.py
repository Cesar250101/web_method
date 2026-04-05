from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    """Limpia el dominio del sitio web 'Method' para evitar redirecciones en local."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['website'].search([('name', '=', 'Method')]).write({'domain': False})
