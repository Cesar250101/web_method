import json
import logging
import urllib.parse
import urllib.request

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

WEBHOOK_URL = 'https://n8n.method.cl/webhook/84c4ec6f-9179-4b37-844f-ef3e399510ce'
RECAPTCHA_SECRET = '6LfPU50sAAAAAEEcESvuRJ9u1n4z0yl_85qjt42j'


class WebMethodController(http.Controller):

    @http.route('/web_method/example', type='json', auth='user', methods=['POST'])
    def example_method(self, **kwargs):
        """Ejemplo de método web tipo JSON."""
        return {'status': 'ok', 'message': 'Web Method funcionando correctamente'}

    @http.route('/web_method/ping', type='http', auth='public', methods=['GET'])
    def ping(self, **kwargs):
        """Endpoint HTTP público de prueba."""
        return request.make_response('pong', headers=[('Content-Type', 'text/plain')])

    @http.route('/erp', type='http', auth='public', website=True, methods=['GET'])
    def erp_page(self, **kwargs):
        """Página de producto ERP."""
        return request.render('web_method.erp_page', {})

    @http.route(['/punto-de-venta', '/punto_de_venta'], type='http', auth='public', website=True, methods=['GET'])
    def punto_de_venta_page(self, **kwargs):
        """Página de producto Punto de Venta."""
        return request.render('web_method.punto_de_venta_page', {})

    @http.route('/prueba-gratis', type='http', auth='public', website=True, methods=['GET'])
    def free_trial_form(self, **kwargs):
        """Página con formulario de Prueba Gratis."""
        return request.render('web_method.free_trial_page', {})

    @http.route('/prueba-gratis/enviar', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def free_trial_submit(self, **post):
        """Procesa el formulario de Prueba Gratis."""
        name = post.get('name', '').strip()
        apellido = post.get('apellido', '').strip()
        email = post.get('email', '').strip()
        phone = post.get('phone', '').strip()
        company_name = post.get('company_name', '').strip()
        how_found = post.get('how_found', '').strip()

        if not name or not email:
            return request.render('web_method.free_trial_page', {
                'error': 'El nombre y el correo son obligatorios.',
                'values': post,
            })

        # Validar reCAPTCHA v2
        captcha_response = post.get('g-recaptcha-response', '')
        try:
            captcha_data = urllib.parse.urlencode({
                'secret': RECAPTCHA_SECRET,
                'response': captcha_response,
            }).encode('utf-8')
            captcha_req = urllib.request.Request(
                'https://www.google.com/recaptcha/api/siteverify',
                data=captcha_data,
                method='POST',
            )
            captcha_result = json.loads(urllib.request.urlopen(captcha_req, timeout=10).read())
        except Exception as e:
            _logger.warning('Error validando reCAPTCHA: %s', e)
            captcha_result = {'success': False}

        if not captcha_result.get('success'):
            return request.render('web_method.free_trial_page', {
                'error': 'Por favor completa el reCAPTCHA.',
                'values': post,
            })

        vals = {
            'name': name,
            'apellido': apellido,
            'email': email,
            'phone': phone,
            'company_name': company_name,
            'how_found': how_found,
        }

        lead = request.env['web_method.free_trial_lead'].sudo().create(vals)

        # Integración CRM condicional
        crm_module = request.env['ir.module.module'].sudo().search(
            [('name', '=', 'crm'), ('state', '=', 'installed')], limit=1
        )
        if crm_module:
            crm_lead = request.env['crm.lead'].sudo().create({
                'name': 'Prueba Gratis - %s %s' % (name, apellido),
                'contact_name': '%s %s' % (name, apellido),
                'email_from': email,
                'phone': phone,
                'partner_name': company_name,
                'description': '¿Cómo se enteró?: %s' % how_found,
                'type': 'lead',
            })
            lead.sudo().write({'crm_lead_id': crm_lead.id})

        # Llamar webhook n8n
        try:
            webhook_data = json.dumps(vals).encode('utf-8')
            req = urllib.request.Request(
                WEBHOOK_URL,
                data=webhook_data,
                headers={'Content-Type': 'application/json'},
                method='POST',
            )
            urllib.request.urlopen(req, timeout=10)
        except Exception as e:
            _logger.warning('Error al llamar webhook n8n: %s', e)

        return request.redirect('/prueba-gratis/gracias?nombre=%s' % name)

    @http.route('/prueba-gratis/gracias', type='http', auth='public', website=True, methods=['GET'])
    def free_trial_thanks(self, nombre='', **kwargs):
        """Página de agradecimiento tras registro."""
        return request.render('web_method.free_trial_thanks', {'nombre': nombre})
