"""
Fix: texto blanco en tarjetas de módulos del homepage Method.

Causa raíz: la section s_embed_code tiene clase o_colored_level que hereda
color blanco con !important desde el tema Odoo.

Solución:
  1. Eliminar o_colored_level de la section s_embed_code.
  2. Reemplazar el grid de módulos con HTML que incluye color:#333 !important
     directamente en el contenedor de cada tarjeta (el editor NO stripped
     !important de valores que entran via SQL, solo los que entran via UI).
"""
import logging
import re

_logger = logging.getLogger(__name__)

MODULES = [
    ("fa-handshake",        "CRM",               "Centraliza prospectos y oportunidades para cerrar más negocios con tu equipo."),
    ("fa-shopping-cart",    "Ventas",             "Genera cotizaciones y pedidos en minutos con seguimiento de cada oportunidad."),
    ("fa-truck",            "Compras",            "Automatiza órdenes de compra y recepciones con control de proveedores."),
    ("fa-cubes",            "Inventario",         "Stock en tiempo real, multi-bodega y trazabilidad completa de productos."),
    ("fa-calculator",       "Contabilidad",       "Conciliación bancaria, reportes financieros y cierre de mes sin fricciones."),
    ("fa-file-invoice",     "Facturación DTE",    "Boletas, facturas y guías electrónicas integradas al SII de Chile."),
    ("fa-id-card",          "Recursos Humanos",   "Contratos, ausencias y liquidaciones de sueldo en un único sistema."),
    ("fa-tasks",            "Proyectos",          "Tableros Kanban, control de tareas y seguimiento de tiempos por proyecto."),
    ("fa-globe",            "eCommerce",          "Tienda online sincronizada al inventario con medios de pago locales."),
    ("fa-envelope-open-text","Email Marketing",   "Campañas segmentadas con métricas de apertura y conversión en tiempo real."),
    ("fa-cash-register",    "Punto de Venta",     "POS ágil para locales físicos, conectado al stock en tiempo real."),
    ("fa-cogs",             "Manufactura",        "Producción, listas de materiales y control de calidad integrados a tu operación."),
]


def _card(icon, title, desc):
    """Genera el HTML de una tarjeta con colores forzados via !important en el contenedor."""
    return (
        '<div style="background:#ffffff !important;border-radius:14px;padding:20px 16px;'
        'box-shadow:0 2px 12px rgba(0,0,0,0.06);display:flex;flex-direction:column;gap:10px;'
        'color:#1a1a2e !important;">'

        '<div style="width:46px;height:46px;border-radius:10px;'
        'background:rgba(243,119,32,0.09);display:flex;align-items:center;justify-content:center;">'
        f'<i class="fas {icon}" style="color:#F37720 !important;font-size:1.2rem;"></i>'
        '</div>'

        f'<div style="font-weight:800;font-size:0.9rem;color:#1a1a2e !important;">{title}</div>'

        f'<div style="font-size:0.78rem;color:#555555 !important;line-height:1.5;">{desc}</div>'

        '</div>'
    )


def _build_grid():
    cards = "".join(_card(ic, t, d) for ic, t, d in MODULES)
    return (
        '<div style="margin-top:80px;max-width:1100px;margin-left:auto;margin-right:auto;'
        'position:relative;z-index:2;">'
        '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;">'
        + cards +
        '</div></div>'
    )


def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("web_method 1.0.2: fixing module card text colors...")

    views = env['ir.ui.view'].sudo().with_context(lang=None).search([('type', '=', 'qweb')])
    updated = 0

    new_grid = _build_grid()

    for view in views:
        try:
            arch = view.with_context(lang=None).arch_db or ''
        except Exception:
            continue

        if 'method-home-scope' not in arch:
            continue

        new_arch = arch

        # ── Fix 1: quitar o_colored_level que hereda color blanco ────────────
        new_arch = new_arch.replace(
            's_embed_code o_colored_level',
            's_embed_code'
        )

        # ── Fix 2: reemplazar el grid de módulos (tenga o no el dashboard) ──
        # Intentar con el bloque del dashboard-mockup
        if 'dashboard-mockup' in new_arch:
            # Reemplazar todo el bloque que envuelve el mockup
            new_arch = re.sub(
                r'<div[^>]+margin-top:\s*80px[^>]+max-width:\s*900px[^>]*>.*?dashboard-mockup.*?</div>\s*</div>\s*</div>',
                new_grid,
                new_arch,
                flags=re.DOTALL,
            )
            _logger.info("  view %s (%s): replaced dashboard-mockup", view.id, view.key)

        # Intentar con el grid existente de módulos (cualquier versión)
        elif 'fa-handshake' in new_arch:
            new_arch = re.sub(
                r'<div[^>]+margin-top:\s*80px[^>]+max-width:\s*1100px[^>]*>.*?fa-handshake.*?(?:</div>\s*){2,5}',
                new_grid,
                new_arch,
                flags=re.DOTALL,
            )
            _logger.info("  view %s (%s): replaced existing modules grid", view.id, view.key)

        if new_arch != arch:
            # Validate XML before writing to avoid malformed arch errors
            try:
                import lxml.etree as _etree
                _etree.fromstring(new_arch.encode('utf-8'))
            except Exception as xml_err:
                _logger.warning(
                    "  view %s (%s): skipping — new_arch is invalid XML: %s",
                    view.id, view.key, xml_err,
                )
                continue
            view.with_context(lang=None).write({'arch_db': new_arch})
            updated += 1
            _logger.info("  view %s: saved OK", view.id)
        else:
            _logger.warning("  view %s (%s): arch unchanged — regex no coincidió", view.id, view.key)

    _logger.info("web_method 1.0.2: done — %d view(s) updated", updated)
