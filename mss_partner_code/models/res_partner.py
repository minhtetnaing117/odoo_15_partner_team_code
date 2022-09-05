from odoo import api, fields, models , _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    normal_code_id = fields.Char(size=64, index=True, tracking=True, readonly=True)
    partner_code_id = fields.Char(size=64, index=True, tracking=True, readonly=True)
    parent_partner = fields.Many2one("res.partner", string="Partner")
    is_partner = fields.Boolean("Is partner?")
    latest_code = fields.Char("Latest Code", readonly=True)
    show_is_partner = fields.Boolean("Show",default=False,compute='compute_show_is_partner')

    outlet_gp = fields.Selection([
        ('whole_sale', 'Whole Sale'),
        ('key', 'Key Outlet'),
        ('retail', 'Retail')], default='whole_sale', string='Outlet Group')

    outlet_type = fields.Many2one('outlet.type', string='Outlet Type')

    @api.depends('parent_partner')
    def compute_show_is_partner(self):
        for i in self:
            if i.parent_partner:
                i.show_is_partner = True
            else:
                i.show_is_partner = False

    @api.model
    def create(self, values):
        res = super(ResPartner, self).create(values)
        if not res.parent_partner and res.is_partner == False:    # For Normal Customer
            sequence =self.env['ir.sequence'].next_by_code('res.partner.normal')
            code = "CU" + sequence
            res.normal_code_id = code
    
        elif res.is_partner == True and res.city_group:         # For Partner
            partner_code = res.city_group.partner_code
            city_tag = res.city_group.name
            res.partner_code_id = partner_code + city_tag

        elif res.parent_partner and res.is_partner == False:    # For customer with partner
            partner_code = res.parent_partner.partner_code_id
            if not res.parent_partner.latest_code:
                res.parent_partner.latest_code = "CU" + partner_code[2:5] + "001"
                latest_code = res.parent_partner.latest_code
                res.normal_code_id = latest_code

            elif res.parent_partner.latest_code:
                latest_code = res.parent_partner.latest_code[5:]
                latest_code = int(latest_code)
                if len(str(latest_code)) <= 1:
                    code = "CU" + partner_code[2:5] + "00" + str(latest_code + 1)
                    res.normal_code_id = code
                else:
                    code = "CU" + partner_code[2:5] + "0" + str(latest_code + 1)
                    res.normal_code_id = code

                partner = self.env["res.partner"].browse(res.parent_partner.id)
                partner.write({'latest_code' : code})
        return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            args = ['|','|', ('name', operator, name),('normal_code_id', operator, name), ('partner_code_id', operator, name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)


    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        for i in self:
            if 'city_group' in vals:
                if i.is_partner == True and i.city_group:
                    partner_code = i.city_group.partner_code
                    city_tag = i.city_group.name
                    i.partner_code_id = partner_code + city_tag
        return res

class OutletType(models.Model):
    _name = 'outlet.type'

    name = fields.Char(string="Outlet Type")


class ResPartnerCityGroup(models.Model):
    _inherit = 'res.partner.city.group'

    partner_code = fields.Char(string="Code Format", required=True)