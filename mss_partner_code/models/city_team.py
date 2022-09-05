from odoo import api, fields, models , _
from odoo.exceptions import ValidationError


class CityTeam(models.Model):
    _name = 'city.team'

    city_name = fields.Char(string="City Team", required=True)
    user_id = fields.Many2one('res.users', string="SR Team" )


    def name_get(self):
        result = []
        for i in self:
            result.append((i.id,'%s' % (i.city_name)))
        return result