odoo.define('web_method.erp_free_trial_button', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    var MODULES_LIST = [
        'Informes financieros contables',
        'Asistencias',
        'CRM (Gestión de relaciones con el cliente)',
        'Calendario',
        'Nómina y Recursos Humanos de Chile',
        'Contactos',
        'Conversaciones',
        'Marketing por correo electrónico',
        'Contratos de empleados',
        'Empleados',
        'Rendición de Gastos',
        'Flota',
        'Inventario',
        'Etiqueta de factura',
        'Contabilidad',
        'Constructor MIS (Reportes contables)',
        'Fabricación',
        'Notas',
        'Nómina',
        'Punto de venta',
        'Proyecto',
        'Compras',
        'Reparaciones',
        'Ventas',
        'Gestión de habilidades',
        'Tasas de cambio automáticas Chile',
        'Tiempo libre (Ausencias)',
        'Sitio web',
        'Comercio electrónico',
        'eLearning (Aprendizaje en línea)',
    ];

    var DTE_LIST = [
        'Boleta / Factura Electrónica Chilena',
        'Cesión de Créditos Electrónica para Chile',
        'Factura de Exportación Electrónica para Chile',
        'Facturación Electrónica para Chile',
        'Guías de Despacho Electrónica para Chile',
        'Factura de compras electrónica',
    ];

    // Modules excluded from ERP Startup (red cross)
    var STARTUP_EXCLUDED = [
        'Nómina y Recursos Humanos de Chile',
        'Nómina',
        'Marketing por correo electrónico',
        'Rendición de Gastos',
        'Flota',
        'Constructor MIS (Reportes contables)',
        'Fabricación',
        'Reparaciones',
        'Gestión de habilidades',
        'Sitio web',
        'Comercio electrónico',
        'eLearning (Aprendizaje en línea)',
    ];

    // cardType: 'trial', 'startup', 'full'
    function buildModulesHTML(cardType) {
        var html = '';
        MODULES_LIST.forEach(function (mod) {
            if (cardType === 'startup' && STARTUP_EXCLUDED.indexOf(mod) !== -1) {
                html += '<li class="o_mod_disabled"><i class="fas fa-times" style="color: #dc3545;"></i> ' + mod + '</li>';
            } else {
                html += '<li><i class="fas fa-check" style="color: #28a745;"></i> ' + mod + '</li>';
            }
        });
        // DTE section
        html += '<li class="o_dte_header"><strong>Facturación Electrónica</strong></li>';
        DTE_LIST.forEach(function (mod) {
            if (cardType === 'trial') {
                html += '<li class="o_mod_disabled"><i class="fas fa-times" style="color: #dc3545;"></i> ' + mod + '</li>';
            } else {
                html += '<li><i class="fas fa-check" style="color: #28a745;"></i> ' + mod + '</li>';
            }
        });
        return html;
    }

    // --- POS page lists ---
    var POS_BASE_LIST = [
        'Punto de venta',
        'Compras',
        'Inventario',
        'Ventas',
        'Facturación',
    ];

    var POS_DTE_LIST = [
        'Factura electrónica',
        'Boleta electrónica',
        'Nota de crédito electrónica',
        'Nota de débito electrónica',
        'Guía de despacho electrónica',
    ];

    // cardType: 'trial', 'startup', 'full'
    function buildPosModulesHTML(cardType) {
        var html = '';
        html += '<li class="o_dte_header"><strong>Módulos Base</strong></li>';
        POS_BASE_LIST.forEach(function (mod) {
            html += '<li><i class="fas fa-check" style="color: #28a745;"></i> ' + mod + '</li>';
        });
        html += '<li class="o_dte_header"><strong>Facturación Electrónica</strong></li>';
        POS_DTE_LIST.forEach(function (mod) {
            if (cardType === 'trial') {
                html += '<li class="o_mod_disabled"><i class="fas fa-times" style="color: #dc3545;"></i> ' + mod + '</li>';
            } else {
                html += '<li><i class="fas fa-check" style="color: #28a745;"></i> ' + mod + '</li>';
            }
        });
        return html;
    }

    function buildModulesSection(borderColor, cardType, page) {
        var html, totalCount;
        if (page === '/punto-de-venta') {
            totalCount = POS_BASE_LIST.length + POS_DTE_LIST.length;
            html = buildPosModulesHTML(cardType);
        } else {
            totalCount = MODULES_LIST.length + DTE_LIST.length;
            html = buildModulesHTML(cardType);
        }
        return '<div class="o_modules_section">' +
            '<button type="button" class="o_modules_toggle" style="border-color: ' + borderColor + ';">' +
                '<span><i class="fas fa-th-list"></i> <strong>Módulos incluidos</strong> (' + totalCount + ')</span>' +
                '<i class="fas fa-chevron-down o_modules_arrow"></i>' +
            '</button>' +
            '<ul class="feature-list o_modules_list">' +
                html +
            '</ul>' +
        '</div>';
    }

    // Global click delegation - most reliable way
    document.addEventListener('click', function (ev) {
        var toggle = ev.target.closest('.o_modules_toggle');
        if (!toggle) {
            return;
        }
        ev.preventDefault();
        ev.stopPropagation();
        var section = toggle.closest('.o_modules_section');
        if (section) {
            section.classList.toggle('open');
        }
    });

    publicWidget.registry.ErpFreeTrialButton = publicWidget.Widget.extend({
        selector: '#wrap, #wrapwrap',

        start: function () {
            var self = this;
            var path = window.location.pathname;
            var SUPPORTED_PAGES = ['/erp', '/punto-de-venta'];
            return this._super.apply(this, arguments).then(function () {
                if (SUPPORTED_PAGES.indexOf(path) === -1) {
                    return;
                }
                self._currentPage = path;
                self._addFreeTrialCard();
                self._fixUserCounts();
                self._addModulesToCards();
            });
        },

        _fixUserCounts: function () {
            var pricingRow = this.el.querySelector('#precios .row.justify-content-center');
            if (!pricingRow) {
                return;
            }
            var cards = pricingRow.querySelectorAll('.pricing-card:not(.o_trial_card)');
            cards.forEach(function (card) {
                var isFeatured = card.classList.contains('featured');
                var strongs = card.querySelectorAll('.feature-list strong');
                strongs.forEach(function (el) {
                    var text = el.textContent.trim();
                    if (!isFeatured && text === '6 Usuarios') {
                        // Startup: 6 -> 3
                        el.textContent = '3 Usuarios';
                    } else if (isFeatured && text === '20 Usuarios') {
                        // Full: 20 -> 6
                        el.textContent = '6 Usuarios';
                    }
                });
            });
        },

        _addFreeTrialCard: function () {
            var pricingRow = this.el.querySelector('#precios .row.justify-content-center');
            if (!pricingRow) {
                return;
            }

            if (pricingRow.querySelector('.o_erp_free_trial_card')) {
                return;
            }

            var startupCol = pricingRow.querySelector('.col-lg-5');
            if (!startupCol) {
                return;
            }

            var allCols = pricingRow.querySelectorAll('.col-lg-5');
            allCols.forEach(function (col) {
                col.classList.remove('col-lg-5');
                col.classList.add('col-lg-4');
            });

            var cardCol = document.createElement('div');
            cardCol.className = 'col-lg-4 col-md-6 o_erp_free_trial_card';
            cardCol.innerHTML =
                '<div class="pricing-card o_trial_card">' +
                    '<div class="badge-highlight" style="background: #28a745;">Sin Costo</div>' +
                    '<h3 class="text-uppercase font-weight-bold mb-2" style="color: #28a745;">Prueba Gratis</h3>' +
                    '<p class="text-sm text-muted">Conoce Method sin compromiso.</p>' +
                    '<div class="price-tag">0 <span>UF</span></div>' +
                    '<span class="price-period">30 días gratis</span>' +
                    '<ul class="feature-list">' +
                        '<li><i class="fas fa-check"></i> Acceso completo al sistema</li>' +
                        '<li><i class="fas fa-check"></i> Sin tarjeta de crédito</li>' +
                        '<li><i class="fas fa-check"></i> Soporte por correo</li>' +
                        '<li><i class="fas fa-user-friends"></i> Hasta <strong>1 Usuario</strong></li>' +
                        '<li style="background: #e8f5e9; padding: 10px; border-radius: 8px;"><i class="fas fa-info-circle" style="color: #28a745;"></i> Sin emisión de DTE</li>' +
                        '<li><i class="fas fa-rocket" style="color: #28a745;"></i> Activación inmediata</li>' +
                    '</ul>' +
                    buildModulesSection('#28a745', 'trial', this._currentPage) +
                    '<a href="/prueba-gratis" class="btn-method-cta w-100 o_trial_cta">Prueba Gratis</a>' +
                '</div>';

            pricingRow.insertBefore(cardCol, startupCol);
        },

        _addModulesToCards: function () {
            var currentPage = this._currentPage;
            var pricingRow = this.el.querySelector('#precios .row.justify-content-center');
            if (!pricingRow) {
                return;
            }

            var cards = pricingRow.querySelectorAll('.pricing-card');
            cards.forEach(function (card) {
                if (card.classList.contains('o_trial_card')) {
                    return;
                }
                if (card.querySelector('.o_modules_section')) {
                    return;
                }

                var ctaBtn = card.querySelector('.btn-method-cta');
                if (!ctaBtn) {
                    return;
                }

                var isFeatured = card.classList.contains('featured');
                var borderColor = isFeatured ? '#f37720' : '#676a76';

                var modulesDiv = document.createElement('div');
                var cardType = isFeatured ? 'full' : 'startup';
                modulesDiv.innerHTML = buildModulesSection(borderColor, cardType, currentPage);
                var section = modulesDiv.firstChild;

                card.insertBefore(section, ctaBtn);
            });
        },
    });

    return publicWidget.registry.ErpFreeTrialButton;
});
