from odoo import api, SUPERUSER_ID

from odoo.addons.web_method.hooks import setup_method_website


def migrate(cr, version):
    """Sitio EvolucionAI: el sitio 'Method' pasa a usar /evolucionai como inicio."""
    setup_method_website(api.Environment(cr, SUPERUSER_ID, {}))
