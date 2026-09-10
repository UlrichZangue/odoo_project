from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SupportTicket(models.Model):
    _name = "client.support.ticket"
    _description = "Ticket de support client"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "priority desc, create_date desc"

    name = fields.Char(string="Référence", required=True, copy=False, readonly=True, default=lambda self: _("Nouveau"), tracking=True)
    title = fields.Char(string="Titre", required=True, tracking=True)
    description = fields.Html(string="Description")
    partner_id = fields.Many2one("res.partner", string="Client", required=True, tracking=True, domain="[('is_company', '=', True)]")
    contact_id = fields.Many2one("res.partner", string="Contact", tracking=True, domain="[('parent_id', '=', partner_id)]")
    user_id = fields.Many2one("res.users", string="Consultant assigné", tracking=True, domain="[('share', '=', False)]")
    category_id = fields.Many2one("client.support.category", string="Catégorie", tracking=True)
    priority = fields.Selection([("0", "Basse"), ("1", "Normale"), ("2", "Haute"), ("3", "Urgente")], default="1", required=True, tracking=True)
    state = fields.Selection([("new", "Nouveau"), ("assigned", "Assigné"), ("in_progress", "En cours"), ("waiting", "En attente"), ("resolved", "Résolu"), ("closed", "Fermé")], default="new", required=True, tracking=True, index=True)
    deadline = fields.Datetime(string="Date limite", tracking=True)
    resolved_date = fields.Datetime(string="Date de résolution", readonly=True, tracking=True)
    intervention_ids = fields.One2many("client.support.intervention", "ticket_id", string="Interventions")
    intervention_count = fields.Integer(compute="_compute_intervention_count", string="Nombre d'interventions")

    @api.depends("intervention_ids")
    def _compute_intervention_count(self):
        grouped = self.env["client.support.intervention"].read_group([("ticket_id", "in", self.ids)], ["ticket_id"], ["ticket_id"])
        counts = {row["ticket_id"][0]: row["ticket_id_count"] for row in grouped}
        for ticket in self:
            ticket.intervention_count = counts.get(ticket.id, 0)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("Nouveau")) == _("Nouveau"):
                vals["name"] = self.env["ir.sequence"].next_by_code("client.support.ticket") or _("Nouveau")
        tickets = super().create(vals_list)
        for ticket in tickets.filtered(lambda item: item.priority == "3"):
            ticket.activity_schedule("mail.mail_activity_data_todo", user_id=ticket.user_id.id or self.env.user.id, summary=_("Prendre en charge le ticket urgent"), note=_("Ce ticket urgent nécessite une prise en charge immédiate."))
        return tickets

    @api.constrains("deadline", "create_date")
    def _check_deadline(self):
        for ticket in self:
            if ticket.deadline and ticket.create_date and ticket.deadline < ticket.create_date:
                raise ValidationError(_("La date limite ne peut pas précéder la création du ticket."))

    def _set_state(self, state):
        self.write({"state": state, "resolved_date": fields.Datetime.now() if state == "resolved" else False})

    def action_assign(self):
        for ticket in self:
            if not ticket.user_id:
                ticket.user_id = self.env.user
        self._set_state("assigned")

    def action_start(self):
        self._set_state("in_progress")

    def action_wait(self):
        self._set_state("waiting")

    def action_resolve(self):
        self._set_state("resolved")

    def action_close(self):
        self._set_state("closed")

    def action_reopen(self):
        self.write({"state": "new", "resolved_date": False})

    def action_view_interventions(self):
        action = self.env.ref("client_support_intervention.action_support_intervention").read()[0]
        action["domain"] = [("ticket_id", "in", self.ids)]
        action["context"] = {"default_ticket_id": self.id} if len(self) == 1 else {}
        return action

    @api.model
    def _cron_deadline_reminders(self):
        now = fields.Datetime.now()
        tickets = self.search([("deadline", ">=", now), ("deadline", "<=", now + timedelta(days=1)), ("state", "not in", ["resolved", "closed"])])
        activity_type = self.env.ref("mail.mail_activity_data_todo")
        for ticket in tickets.filtered("user_id"):
            exists = self.env["mail.activity"].search_count([("res_model", "=", ticket._name), ("res_id", "=", ticket.id), ("activity_type_id", "=", activity_type.id), ("summary", "=", _("Échéance proche"))])
            if not exists:
                ticket.activity_schedule(activity_type.id, user_id=ticket.user_id.id, date_deadline=fields.Date.context_today(ticket), summary=_("Échéance proche"), note=_("La date limite de ce ticket est à moins de 24 heures."))

