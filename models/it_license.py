# -*- coding: utf-8 -*-
from datetime import date

from odoo import api, fields, models


class ItLicense(models.Model):
    _name = 'it.license'
    _description = 'Licence logicielle'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_expiration asc, name'

    name = fields.Char(string='Logiciel', required=True, tracking=True)
    license_key = fields.Char(string='Clé de licence')
    license_type = fields.Selection([
        ('subscription', 'Abonnement'),
        ('perpetual', 'Perpétuelle'),
        ('trial', 'Essai'),
        ('other', 'Autre'),
    ], string='Type', default='subscription')
    partner_id = fields.Many2one('res.partner', string='Client', tracking=True)
    equipement_id = fields.Many2one('it.equipement', string='Machine')
    seat_count = fields.Integer(string='Nombre de postes', default=1)
    date_start = fields.Date(string='Date de début')
    date_expiration = fields.Date(string='Expiration', tracking=True)
    state = fields.Selection([
        ('active', 'Active'),
        ('expiring', 'Expire bientôt'),
        ('expired', 'Expirée'),
    ], string='État', compute='_compute_state', store=True)
    notes = fields.Text(string='Notes')

    @api.model
    def _cron_mise_a_jour_licences(self):
        """Recalcule l'état (active / expire bientôt / expirée) de toutes les
        licences. Appelé quotidiennement par la tâche planifiée."""
        licences = self.search([])
        licences.modified(['date_expiration'])
        licences.mapped('state')
        return True

    @api.depends('date_expiration')
    def _compute_state(self):
        today = date.today()
        for rec in self:
            if not rec.date_expiration:
                rec.state = 'active'
            else:
                days = (rec.date_expiration - today).days
                if days < 0:
                    rec.state = 'expired'
                elif days <= 30:
                    rec.state = 'expiring'
                else:
                    rec.state = 'active'

