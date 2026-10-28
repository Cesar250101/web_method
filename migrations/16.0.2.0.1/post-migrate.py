from odoo import api, SUPERUSER_ID

# Concept Store: textos sin mención a Odoo ni jerga técnica. Los mismos
# reemplazos se aplicaron a views/pages.xml y views/snippets.xml; aquí se
# parchean las vistas ya instaladas (pages.xml está en noupdate).
NAV_OLD = 'Gestión multimarca conectada a Odoo.'
NAV_NEW = 'Portal para las marcas de tu tienda.'

CONCEPT_REPLACEMENTS = [
    ('Tu Concept Store, <span class="eai-gradient">conectada de punta a punta.</span>',
     'Tu Concept Store, <span class="eai-gradient">con cada marca al día.</span>'),
    ('Un portal de proveedores para que cada marca revise sus ventas, gestione catálogo, solicite ingresos y retiros y descargue liquidaciones. Todo conectado directo a Odoo, sin copias ni planillas sueltas.',
     'El portal donde cada marca de tu tienda ve cuánto vendió, qué stock le queda y cuánto le liquidan. Sube productos, pide ingresos y retiros y descarga liquidaciones, todo en un solo lugar y sin planillas sueltas.'),
    ('Ver portal en vivo ↗', 'Ver el portal ↗'),
    ('Datos en tiempo real</span>', 'Información al día</span>'),
    ('Conectado a Odoo</span></div></div><div class="eai-concept-hero-shot">',
     'Seguro y privado</span></div></div><div class="eai-concept-hero-shot">'),
    ('Siete módulos pensados para que proveedores y administración trabajen con la misma información del ERP.',
     'Siete secciones pensadas para que cada marca y tu equipo trabajen con la misma información.'),
    ('Ventas por día, categoría y local, productos top y alertas de stock crítico.',
     'Ventas por día, categoría y local, productos estrella y avisos de stock bajo.'),
    ('Historial consolidado de POS y facturas, filtros por origen y exportación a Excel.',
     'Todo lo que vendiste en un solo historial, con filtros y descarga a Excel.'),
    ('Crea, edita y archiva productos con variantes y carga masiva por planilla.',
     'Crea, edita y archiva productos con variantes. Sube muchos de una vez con una planilla y ajusta tu inventario con otra.'),
    ('Solicita mercadería y genera el flujo real de orden de compra y recepción en bodega.',
     'Avisa a la tienda qué mercadería envías y sigue su recepción en bodega.'),
    ('Gestiona devoluciones desde la tienda hacia la marca con movimiento real de stock.',
     'Gestiona las devoluciones de la tienda hacia tu marca, con el stock siempre bien registrado.'),
    ('<h3>Todo conectado</h3><p>Los cambios se leen y escriben directamente en Odoo en tiempo real.</p>',
     '<h3>Siempre al día</h3><p>Lo que ves en el portal es el estado actual de tus ventas y tu stock.</p>'),
    ('<span class="eai-eyebrow">Conectado a Odoo</span><h2>No es una copia. <span class="eai-gradient">Es tu Odoo, en una vista hecha para tus marcas.</span></h2>',
     '<span class="eai-eyebrow">Tu marca, bajo control</span><h2>Tus ventas y tu stock, <span class="eai-gradient">siempre al día.</span></h2>'),
    ('Cada dato se consulta y se actualiza directamente en Odoo. Productos, ventas, stock y liquidaciones se mantienen alineados con la operación real.',
     'Cada marca ve lo que realmente pasa en la tienda: ventas, stock y comisiones, sin esperar reportes ni cruzar planillas.'),
    ('<b>Conectado en vivo</b><span>Lo que cada marca ve corresponde al estado real de ventas, stock y comisiones en Odoo.</span>',
     '<b>Siempre al día</b><span>Lo que cada marca ve es el estado actual de sus ventas, su stock y sus comisiones.</span>'),
    ('<b>Seguro, server-side</b><span>La autenticación se realiza contra Odoo sin exponer credenciales en el navegador.</span>',
     '<b>Seguro y privado</b><span>Cada marca entra con su cuenta y ve solo su información.</span>'),
    ('POS y facturas, filtros y exportación a Excel.', 'Tus ventas con filtros y descarga a Excel.'),
    ('revisemos cómo adaptar el portal a tu operación y conectarlo con Odoo.',
     'revisemos cómo adaptar el portal a tu operación.'),
]

META_REPLACEMENTS = {
    'website_meta_title': (
        'Concept Store · Gestión multimarca con Odoo | EvolucionAI',
        'Concept Store · Portal para las marcas de tu tienda | EvolucionAI'),
    'website_meta_description': (
        'Portal de proveedores para tiendas multimarca, conectado a Odoo. Ventas, catálogo, stock y liquidaciones.',
        'Portal para las marcas de tu tienda multimarca: revisa ventas y stock, sube productos, pide ingresos y retiros y descarga liquidaciones.'),
}


def _patch_arch(arch, concept):
    new = arch.replace(NAV_OLD, NAV_NEW)
    if concept:
        for old, repl in CONCEPT_REPLACEMENTS:
            new = new.replace(old, repl)
    return new


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    View = env['ir.ui.view'].with_context(active_test=False, lang=None)
    views = View.search([('key', 'like', 'web_method.page_eai_%')])
    for view in views:
        arch = view.arch_db or ''
        new_arch = _patch_arch(arch, view.key == 'web_method.page_eai_conceptstore')
        if new_arch != arch:
            view.write({'arch_db': new_arch})

    Page = env['website.page'].with_context(active_test=False, lang=None)
    for page in Page.search([('url', '=', '/evolucionai/concept-store')]):
        vals = {}
        for field, (old, new) in META_REPLACEMENTS.items():
            if page[field] == old:
                vals[field] = new
        if vals:
            page.write(vals)
