# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Qué es

Módulo Odoo 16 (`web_method`, v16.0.2.0.0) que implementa el sitio web de **EvolucionAI** (web v9.7): 8 landings editables desde el editor de Odoo, 8 snippets y formularios nativos de CRM. Reemplazó al sitio anterior de Method (páginas `/erp`, `/punto-de-venta`, `/prueba-gratis` y snippets `s_method_*`). Depende de `base`, `web`, `website`, `website_crm`. Es un repositorio Git propio (`origin` = `Cesar250101/web_method`, rama `16.0`) dentro de `addons/` de la instalación local; las reglas del harness de la raíz (`AGENTS.md`) aplican: antes de editar, `scripts/sync-addon.ps1 -Module web_method` desde la raíz, y al cerrar la tarea proponer al usuario subir a GitHub (no hacer commit/push sin confirmación).

## Comandos

No hay build ni linter. Se prueba levantando Odoo y actualizando el módulo (desde la raíz del servidor):

```
python odoo-bin -c <odoo.conf> -d <db> -u web_method --stop-after-init
python odoo-bin -c <odoo.conf> -d <db_desechable> -i web_method --test-enable --test-tags web_method --stop-after-init
```

- Cambios en Python (controllers/models) requieren reiniciar Odoo; cambios en XML/assets requieren `-u web_method`.
- Si se agregan archivos nuevos al módulo (XML, assets), el proceso del debugger de VS Code aplica y revierte `-u` por su cuenta: matar ese PID antes de actualizar.
- Las migraciones (`migrations/<versión>/post-migrate.py`) solo corren al subir `version` en `__manifest__.py`.
- Para probar, usar una BD desechable (crear, `-i web_method`, borrar); `-u` sobre una BD real reescribe los snippets pero no las páginas (ver abajo).

## Arquitectura

- **Landings** (`views/pages.xml`): 8 `website.page` (`/evolucionai`, `/evolucionai/onebox`, `/vidia`, `/erp`, `/punto-de-venta`, `/concept-store`, `/automatizacion`, `/contacto`), publicadas y **sin `website_id`** (visibles en todos los sitios; al editar, Odoo crea la copia propia del sitio). Cada una es una vista QWeb con `website.layout`, cabecera y pie propios (`eai-nav`, `eai-footer`; ocultan los predeterminados solo en esas páginas) y el contenido **en línea** dentro de `<div id="wrap" class="oe_structure">`, no con `t-call`: así el editor guarda sobre la propia vista de la página (verificado con `ir.ui.view.save`: crea la vista específica del sitio y no toca la genérica). No volver a usar `t-call` hacia los `s_eai_*`. Están en `noupdate="1"`: `-u` no las pisa, así que un cambio de contenido en el XML no llega a BD ya instaladas (requiere migración o editar en el editor).
- **Snippets** (`views/snippets.xml`): 8 plantillas `s_eai_*` («EvolucionAI · …») en «Estructura» del editor, vía `eai_snippets` (hereda `website.snippets`). Usar **una landing completa por página**. El contenido de `pages.xml` es una copia de estos: si se cambia uno, cambiar el otro.
- **Formularios**: nativos de Odoo (`/website/form/`, `crm.lead`, campos `Servicio` y `Plan` en la descripción). Sin controladores propios ni reCAPTCHA propio (usa el de Odoo si está configurado). Se probó solo la estructura, no un envío real al CRM.
- **JS/CSS** (`web.assets_frontend`): `evolucionai.css` (prefijo `eai-`) y `evolucionai.js` (widget `web_method.evolucionai_landing`: menú, pestañas de Onebox/Automatización/POS, modal de planes, contexto del plan en el formulario). Fuentes Inter y Manrope en `static/src/fonts/` (licencias OFL incluidas).
- **Inicio del sitio «Method»**: `hooks.setup_method_website` (post_init_hook y migración 16.0.2.0.0) deja `homepage_url = /evolucionai` y limpia `domain` solo en el website llamado `Method`. Otros sitios no se tocan. El homepage antiguo (`/`) sigue en la BD, solo queda tapado por `homepage_url`.
- **Rutas heredadas** (`controllers/main.py`): `/erp`, `/punto-de-venta`, `/punto_de_venta`, `/prueba-gratis`, `/prueba-gratis/gracias` redirigen 301 a las landings nuevas. `/web_method/ping` y `/web_method/example` son de prueba.
- **Modelo `web_method.free_trial_lead`**: ya sin uso (el flujo «Prueba Gratis» con reCAPTCHA + webhook n8n se eliminó); se conserva con su ACL para no perder las solicitudes históricas.
- **Migraciones**: 1.0.1 (limpia `domain`) y 1.0.2 (parcha por regex el homepage antiguo con `method-home-scope`) son históricas y ya no corren. Si el contenido de las páginas cambia, hay que parchear `arch_db` por migración (el contenido editado vive en la BD).
- **Pruebas** (`tests/test_landings.py`, tag `web_method`): páginas publicadas y con contenido en línea, un formulario CRM por landing, contenido de POS/Onebox, redirecciones heredadas y render de `/evolucionai/erp`.

## Paquete de origen: `EvolucionAI_Web_v9_7_Addon_Odoo16/`

Subcarpeta sin versionar (ignorada en `.gitignore`) con el addon original `evolucionai_website` del que se integró todo lo anterior. No instalar a la vez que `web_method` (duplicaría las rutas `/evolucionai*`). Su `LEEME_INSTALACION.md` y `VALIDACION.json` quedan como referencia; se puede mover fuera del módulo.
