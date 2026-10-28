from odoo import http
from odoo.http import request


class WebMethodController(http.Controller):

    @http.route('/web_method/example', type='json', auth='user', methods=['POST'])
    def example_method(self, **kwargs):
        """Ejemplo de método web tipo JSON."""
        return {'status': 'ok', 'message': 'Web Method funcionando correctamente'}

    @http.route('/web_method/ping', type='http', auth='public', methods=['GET'])
    def ping(self, **kwargs):
        """Endpoint HTTP público de prueba."""
        return request.make_response('pong', headers=[('Content-Type', 'text/plain')])

    # Rutas del sitio anterior de Method: se redirigen a las landings de EvolucionAI.
    @http.route('/erp', type='http', auth='public', website=True, methods=['GET'])
    def erp_redirect(self, **kwargs):
        return request.redirect('/evolucionai/erp', code=301)

    @http.route(['/punto-de-venta', '/punto_de_venta'], type='http', auth='public', website=True, methods=['GET'])
    def punto_de_venta_redirect(self, **kwargs):
        return request.redirect('/evolucionai/punto-de-venta', code=301)

    @http.route(['/prueba-gratis', '/prueba-gratis/gracias'], type='http', auth='public', website=True, methods=['GET'])
    def free_trial_redirect(self, **kwargs):
        return request.redirect('/evolucionai/contacto', code=301)
