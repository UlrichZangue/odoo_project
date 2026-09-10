from odoo import fields, models


class SupportCategory(models.Model):
    _name = "client.support.category"
    _description = "Catégorie de support"
    _order = "name"

    name = fields.Char(required=True, translate=True)
    description = fields.Text(translate=True)
    color = fields.Integer()
    manager_id = fields.Many2one("res.users", string="Responsable")
    active = fields.Boolean(default=True)

    _sql_constraints = [("category_name_unique", "unique(name)", "Le nom de la catégorie doit être unique.")]

