from odoo import fields, models


class FreeTrialLead(models.Model):
    _name = 'web_method.free_trial_lead'
    _description = 'Prueba Gratis - Solicitud'
    _order = 'create_date desc'

    name = fields.Char(string='Nombre', required=True)
    apellido = fields.Char(string='Apellido')
    email = fields.Char(string='Correo', required=True)
    phone = fields.Char(string='Teléfono')
    company_name = fields.Char(string='Nombre del negocio')
    how_found = fields.Char(string='¿Cómo se enteró de nosotros?')
    state = fields.Selection(
        [('nuevo', 'Nuevo'), ('procesado', 'Procesado')],
        string='Estado',
        default='nuevo',
    )
    crm_lead_id = fields.Many2one(
        'crm.lead',
        string='Lead CRM',
        ondelete='set null',
    )
