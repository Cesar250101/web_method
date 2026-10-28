odoo.define('web_method.evolucionai_landing', function (require) {
    'use strict';
    const publicWidget = require('web.public.widget');
    let sequence = 0;

    function mount(root, editable) {
        const listeners = [];
        const restore = [];
        const uid = 'eai' + (++sequence);
        const byOriginal = (name) => {
            const selector = '[data-eai-id="' + name + '"]';
            return root.matches(selector) ? root : root.querySelector(selector);
        };
        const remember = (el, name) => {
            const value = el.getAttribute(name);
            restore.push(() => value === null ? el.removeAttribute(name) : el.setAttribute(name, value));
        };
        const listen = (el, event, fn) => {
            el.addEventListener(event, fn);
            listeners.push(() => el.removeEventListener(event, fn));
        };
        const identified = [root].concat(Array.from(root.querySelectorAll('[data-eai-id]'))).filter(el => el.dataset.eaiId);
        identified.forEach(el => {
            remember(el, 'id');
            el.id = el.dataset.eaiId + '-' + uid;
        });
        ['for', 'aria-controls', 'aria-labelledby', 'aria-describedby'].forEach(attr => {
            root.querySelectorAll('[data-eai-ref-' + attr + ']').forEach(el => {
                remember(el, attr);
                el.setAttribute(attr, el.getAttribute('data-eai-ref-' + attr).split(/\s+/).map(id => byOriginal(id) ? id + '-' + uid : id).join(' '));
            });
        });
        const groups = [
            {attr: 'priceTab', selector: '[data-price-tab]', panel: '.eai-ob-plan-panel', initial: 'omnicanal'},
            {attr: 'auCase', selector: '[data-au-case]', panel: '.eai-au-case-panel', initial: 'ventas'},
            {attr: 'posScreen', selector: '[data-pos-screen]', panel: '.eai-pv-screen-panel', initial: 'caja'},
        ];
        groups.forEach(group => {
            group.tabs = Array.from(root.querySelectorAll(group.selector));
            group.panels = Array.from(root.querySelectorAll(group.panel));
            group.tabs.forEach(el => ['aria-selected', 'tabindex', 'class'].forEach(attr => remember(el, attr)));
            group.panels.forEach(el => remember(el, 'hidden'));
        });
        const select = (group, key, focus) => {
            if (!group.tabs.length) return;
            if (!group.tabs.some(tab => tab.dataset[group.attr] === key)) key = group.initial;
            group.tabs.forEach(tab => {
                const on = tab.dataset[group.attr] === key;
                tab.setAttribute('aria-selected', String(on));
                tab.tabIndex = on ? 0 : -1;
                if (group.attr === 'priceTab') tab.classList.toggle('eai-selected', on);
                const panel = root.querySelector('[id="' + tab.getAttribute('aria-controls') + '"]');
                if (panel) panel.hidden = !on;
                if (on && focus) tab.focus();
            });
        };
        if (editable) {
            groups.forEach(group => group.panels.forEach(panel => {panel.hidden = false;}));
            return () => restore.reverse().forEach(fn => fn());
        }
        groups.forEach(group => select(group, group.initial));
        const priceGroup = groups[0];
        const getForm = () => root.querySelector('form[data-contact-form]') || root.querySelector('form');
        const updateLeadName = () => {
            const form = getForm();
            if (!form) return;
            const service = form.elements.namedItem('Servicio');
            const plan = form.elements.namedItem('Plan');
            const name = form.elements.namedItem('name');
            if (name) name.value = ['Consulta web', service ? service.value : form.dataset.service, plan ? plan.value : ''].filter(Boolean).join(' · ').slice(0, 250);
        };
        const scrollToOriginal = (target) => {
            const el = byOriginal(target);
            if (!el) return false;
            el.scrollIntoView({behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start'});
            return true;
        };
        const readLocation = () => {
            select(priceGroup, new URLSearchParams(window.location.search).get('plan') || priceGroup.initial);
            if (window.location.hash) {
                let target;
                try {target = decodeURIComponent(window.location.hash.slice(1));} catch (error) {return;}
                scrollToOriginal(target);
            }
        };
        const closeMenus = () => {
            const links = byOriginal('eai-links');
            const hamb = byOriginal('eai-hamb');
            if (links) links.classList.remove('eai-open');
            if (hamb) {hamb.setAttribute('aria-expanded', 'false'); hamb.setAttribute('aria-label', 'Abrir menú');}
            root.querySelectorAll('.eai-dropdown').forEach(drop => {
                drop.classList.remove('eai-open');
                const button = drop.querySelector('.eai-dropbtn');
                if (button) button.setAttribute('aria-expanded', 'false');
            });
        };
        const lightbox = byOriginal('eai-pv-lightbox');
        let lightboxTrigger;
        if (lightbox) listen(lightbox, 'close', () => {if (lightboxTrigger) lightboxTrigger.focus();});

        listen(root, 'click', event => {
            const target = event.target.closest('a, button');
            if (!target || !root.contains(target)) return;
            for (const group of groups) {
                if (!target.matches(group.selector)) continue;
                select(group, target.dataset[group.attr]);
                if (group.attr === 'priceTab') {
                    const url = new URL(window.location.href);
                    url.searchParams.set('plan', target.dataset.priceTab);
                    window.history.replaceState(null, '', url.pathname + url.search + url.hash);
                }
                return;
            }
            if (target.matches('.eai-dropbtn')) {
                event.preventDefault();
                const drop = target.closest('.eai-dropdown');
                const open = !drop.classList.contains('eai-open');
                closeMenus();
                drop.classList.toggle('eai-open', open); target.setAttribute('aria-expanded', String(open));
                return;
            }
            if (target.dataset.eaiId === 'eai-hamb') {
                const links = byOriginal('eai-links');
                const open = links.classList.toggle('eai-open');
                target.setAttribute('aria-expanded', String(open)); target.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
                return;
            }
            if (target.hasAttribute('data-pos-expand') && lightbox) {
                const image = byOriginal('eai-pv-image-' + target.dataset.posExpand);
                const large = byOriginal('eai-pv-lightbox-image');
                const heading = byOriginal('eai-pv-lightbox-title');
                large.src = image.src; large.alt = image.alt;
                const tab = root.querySelector('[data-pos-screen="' + target.dataset.posExpand + '"]');
                heading.textContent = tab.textContent.replace(/^0[123]/, '').trim();
                lightboxTrigger = target; lightbox.showModal(); return;
            }
            if (target.dataset.eaiId === 'eai-pv-lightbox-close' && lightbox) {lightbox.close(); return;}
            const local = target.dataset.eaiTarget;
            if (!local || !byOriginal(local)) return;
            event.preventDefault();
            const form = getForm();
            if (form && local.indexOf('eai-contact-') === 0) {
                const service = form.elements.namedItem('Servicio');
                const desired = target.dataset.interest || form.dataset.service;
                if (service && desired && (service.tagName !== 'SELECT' || Array.from(service.options).some(option => option.value === desired))) service.value = desired;
                const plan = form.elements.namedItem('Plan');
                if (plan) plan.value = target.dataset.contactPlan || '';
                const note = form.querySelector('[data-contact-plan-note]');
                if (note) {note.textContent = plan && plan.value ? 'Plan seleccionado: ' + plan.value : ''; note.hidden = !(plan && plan.value);}
                updateLeadName();
            }
            if (target.dataset.plan) select(priceGroup, target.dataset.plan);
            if (target.closest('.eai-pv-report-band')) select(groups[2], 'informes');
            const url = new URL(window.location.href);
            if (target.dataset.plan) url.searchParams.set('plan', target.dataset.plan);
            url.hash = local;
            window.history.replaceState(null, '', url.pathname + url.search + url.hash);
            scrollToOriginal(local);
        });
        listen(root, 'keydown', event => {
            const group = groups.find(group => event.target.matches(group.selector));
            if (!group) return;
            const index = group.tabs.indexOf(event.target);
            let next;
            if (event.key === 'ArrowRight') next = (index + 1) % group.tabs.length;
            if (event.key === 'ArrowLeft') next = (index + group.tabs.length - 1) % group.tabs.length;
            if (event.key === 'Home') next = 0;
            if (event.key === 'End') next = group.tabs.length - 1;
            if (next === undefined) return;
            event.preventDefault(); select(group, group.tabs[next].dataset[group.attr], true);
        });
        listen(root, 'change', event => {
            if (event.target.name !== 'Servicio') return;
            const form = getForm(); const plan = form && form.elements.namedItem('Plan');
            if (plan) plan.value = '';
            const note = form && form.querySelector('[data-contact-plan-note]');
            if (note) {note.textContent = ''; note.hidden = true;}
            updateLeadName();
        });
        listen(document, 'click', event => {if (!root.contains(event.target)) closeMenus();});
        listen(document, 'keydown', event => {if (event.key === 'Escape') closeMenus();});
        listen(window, 'hashchange', readLocation);
        // website.s_website_form owns submission, validation, reCAPTCHA and success state.
        updateLeadName();
        requestAnimationFrame(readLocation);
        return () => {
            listeners.forEach(fn => fn());
            if (lightbox && lightbox.open) lightbox.close();
            restore.reverse().forEach(fn => fn());
        };
    }

    publicWidget.registry.EvolucionAILanding = publicWidget.Widget.extend({
        selector: '.s_evolucionai_page, .s_evolucionai_navigation',
        disabledInEditableMode: false,
        start: function () {
            this._eaiCleanup = mount(this.el, this.editableMode);
            return this._super.apply(this, arguments);
        },
        destroy: function () {
            if (this._eaiCleanup) this._eaiCleanup();
            return this._super.apply(this, arguments);
        },
    });
    return {mount: mount};
});
