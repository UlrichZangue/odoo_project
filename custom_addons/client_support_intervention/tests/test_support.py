from datetime import timedelta

from odoo import fields
from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestClientSupport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Client", "is_company": True})
        cls.ticket = cls.env["client.support.ticket"].create({"title": "Test ticket", "partner_id": cls.partner.id})

    def test_ticket_reference_and_workflow(self):
        self.assertTrue(self.ticket.name.startswith("TKT/"))
        self.ticket.action_assign()
        self.assertEqual(self.ticket.state, "assigned")
        self.ticket.action_start()
        self.ticket.action_resolve()
        self.assertEqual(self.ticket.state, "resolved")
        self.assertTrue(self.ticket.resolved_date)

    def test_intervention_reference_and_count(self):
        intervention = self.env["client.support.intervention"].create({"ticket_id": self.ticket.id, "planned_date": fields.Datetime.now(), "diagnostic": "Diagnostic initial"})
        self.assertTrue(intervention.name.startswith("INT/"))
        self.assertEqual(self.ticket.intervention_count, 1)

    def test_incoherent_dates(self):
        with self.assertRaises(ValidationError):
            self.env["client.support.intervention"].create({"ticket_id": self.ticket.id, "planned_date": fields.Datetime.now(), "start_date": fields.Datetime.now(), "end_date": fields.Datetime.now() - timedelta(hours=1), "diagnostic": "Test"})

    def test_user_cannot_read_another_users_ticket(self):
        group = self.env.ref("client_support_intervention.group_support_user")
        first = self.env["res.users"].create({"name": "Support One", "login": "support.one", "groups_id": [(6, 0, [group.id])]})
        second = self.env["res.users"].create({"name": "Support Two", "login": "support.two", "groups_id": [(6, 0, [group.id])]})
        own_ticket = self.env["client.support.ticket"].with_user(first).create({"title": "Private", "partner_id": self.partner.id})
        with self.assertRaises(AccessError):
            own_ticket.with_user(second).read(["title"])

