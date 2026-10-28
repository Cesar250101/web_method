from lxml import etree

from odoo.tests.common import HttpCase, TransactionCase, tagged

KEYS = ['inicio', 'onebox', 'vidia', 'erp', 'pos', 'conceptstore', 'automatizacion', 'contacto']


@tagged('post_install', '-at_install', 'web_method')
class TestEvolucionAILandings(TransactionCase):
    """Run on a disposable/staging database after installing this module."""

    def test_pages_are_published_and_editable(self):
        pages = self.env['website.page']
        for key in KEYS:
            page = self.env.ref('web_method.website_page_eai_' + key)
            self.assertTrue(page.is_published)
            self.assertTrue(page.url.startswith('/evolucionai'))
            self.assertTrue(page.website_meta_title)
            self.assertTrue(page.website_meta_description)
            # el contenido vive en la propia vista de la pagina (no en un t-call), para que el editor lo guarde
            arch = page.view_id.arch_db
            self.assertNotIn('t-call="web_method.s_eai_', arch)
            root = etree.fromstring(arch.encode())
            self.assertTrue(root.xpath('.//div[@id="wrap"][contains(@class, "oe_structure")]/section[@data-snippet]'))
            pages |= page
        self.assertEqual(len(set(pages.mapped('url'))), 8)
        self.assertNotIn('/', pages.mapped('url'))

    def test_native_crm_forms(self):
        self.assertTrue(self.env['ir.model']._get('crm.lead').website_form_access)
        for key in KEYS:
            for arch in (
                self.env.ref('web_method.s_eai_' + key).arch_db,
                self.env.ref('web_method.page_eai_' + key).arch_db,
            ):
                root = etree.fromstring(arch.encode())
                forms = root.xpath('.//form')
                self.assertEqual(len(forms), 1)
                form = forms[0]
                self.assertEqual(form.get('data-model_name'), 'crm.lead')
                self.assertEqual(form.get('action'), '/website/form/')
                self.assertEqual(form.get('data-success-mode'), 'message')
                names = set(form.xpath('.//input/@name | .//textarea/@name | .//select/@name'))
                self.assertTrue({'name', 'contact_name', 'partner_name', 'email_from', 'Servicio', 'description'} <= names)
                self.assertFalse(root.xpath('.//script | .//style'))
                self.assertFalse(root.xpath('.//section/section'))

    def test_pos_and_onebox_content(self):
        pos = self.env.ref('web_method.s_eai_pos').arch_db
        self.assertIn('POS Startup', pos)
        self.assertIn('POS Full', pos)
        self.assertEqual(pos.count('data-pos-screen='), 3)
        self.assertEqual(pos.count('data-pos-expand='), 3)
        onebox = self.env.ref('web_method.s_eai_onebox').arch_db
        self.assertEqual(onebox.count('data-price-tab='), 3)



@tagged('post_install', '-at_install', 'web_method')
class TestLegacyRoutes(HttpCase):

    def test_legacy_routes_redirect(self):
        for old, new in (('/erp', '/evolucionai/erp'), ('/punto-de-venta', '/evolucionai/punto-de-venta'),
                         ('/prueba-gratis', '/evolucionai/contacto')):
            response = self.url_open(old, allow_redirects=False)
            self.assertEqual(response.status_code, 301)
            self.assertTrue(response.headers['Location'].endswith(new))

    def test_landing_renders(self):
        response = self.url_open('/evolucionai/erp')
        self.assertEqual(response.status_code, 200)
        self.assertIn('eai-site', response.text)
