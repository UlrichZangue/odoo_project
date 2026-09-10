from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SupportIntervention(models.Model):
    _name = "client.support.intervention"
    _description = "Intervention de support client"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "planned_date desc"

    name = fields.Char(string="Référence", required=True, copy=False, readonly=True, default=lambda self: _("Nouveau"))
    ticket_id = fields.Many2one("client.support.ticket", string="Ticket", required=True, ondelete="cascade", tracking=True)
    partner_id = fields.Many2one(related="ticket_id.partner_id", string="Client", store=True, readonly=True)
    user_id = fields.Many2one("res.users", string="Consultant", required=True, default=lambda self: self.env.user, tracking=True)
    planned_date = fields.Datetime(string="Date et heure prévues", required=True, tracking=True)
    start_date = fields.Datetime(string="Début réel", tracking=True)
    end_date = fields.Datetime(string="Fin réelle", tracking=True)
    intervention_type = fields.Selection([("remote", "À distance"), ("onsite", "Sur site")], string="Type", default="remote", required=True, tracking=True)
    diagnostic = fields.Text(required=True)
    actions_done = fields.Text(string="Actions réalisées")
    result = fields.Text(string="Résultat")
    state = fields.Selection([("planned", "Planifiée"), ("in_progress", "En cours"), ("done", "Terminée"), ("cancelled", "Annulée")], default="planned", required=True, tracking=True)
    client_validation = fields.Char(string="Validation/signature du client", help="Nom du client validant l'intervention.")
    validation_date = fields.Datetime(readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("Nouveau")) == _("Nouveau"):
                vals["name"] = self.env["ir.sequence"].next_by_code("client.support.intervention") or _("Nouveau")
        return super().create(vals_list)

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date and record.end_date < record.start_date:
                raise ValidationError(_("La date de fin doit être postérieure à la date de début."))

    def action_start(self):
        self.write({"state": "in_progress", "start_date": fields.Datetime.now()})

    def action_done(self):
        for record in self:
            if not record.actions_done or not record.result:
                raise ValidationError(_("Renseignez les actions réalisées et le résultat avant de terminer."))
        self.write({"state": "done", "end_date": fields.Datetime.now()})

    def action_validate_client(self):
        for record in self:
            if not record.client_validation:
                raise ValidationError(_("Indiquez le nom du client validant l'intervention."))
        self.write({"validation_date": fields.Datetime.now()})

    def action_cancel(self):
        self.write({"state": "cancelled"})

