from odoo import fields, models


class EstateStreet(models.Model):
    _name = "estate.street"
    _description = "Улица"
    _order = "name"

    name = fields.Char(string="Название", required=True, index=True)
    district_id = fields.Many2one(
        "estate.district",
        string="Район",
        ondelete="restrict",
    )
    city_id = fields.Many2one(
        "estate.city",
        string="Город",
        related="district_id.city_id",
        store=True,
        readonly=True,
    )
    active = fields.Boolean(string="Активен", default=True)
