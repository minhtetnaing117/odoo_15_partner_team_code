from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    parent_partner = fields.Many2one(
        'res.partner', 
        string="Partner",
        domain="[('is_partner', '=', True)]")

    city_name_id = fields.Many2one('city.team', string="Team Code")
    normal_code_id = fields.Char(string='Customer Code')
    partner_code_id = fields.Char(string='Partner Code')

    partner_id = fields.Many2one(
        'res.partner', string='Customer', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        required=True, change_default=True, index=True, tracking=1,
        domain="[('city_group', '=', city_group),('parent_partner', '=', parent_partner), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",)

    @api.onchange('user_id')
    def onchange_user_id(self):
        city_name = self.env['city.team'].search([('user_id', '=', self.user_id.id)])
        for i in self:
            if i.user_id:
                i.city_name_id = city_name


    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.normal_code_id = self.partner_id.normal_code_id
            
    @api.onchange('parent_partner')
    def onchange_parent_partner(self):
        if self.parent_partner:
            self.partner_code_id = self.parent_partner.partner_code_id