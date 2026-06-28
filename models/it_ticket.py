# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import api, fields, models


class ItTicket(models.Model):
    _name = 'it.ticket'
    _description = 'Ticket support client'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, create_date desc'

    name = fields.Char(string='Référence', readonly=True, copy=False, default='Nouveau')
    subject = fields.Char(string='Sujet', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Client', required=True, tracking=True)
    site_id = fields.Many2one('it.site', string='Site', domain="[('partner_id', 'child_of', partner_id)]")
    equipement_id = fields.Many2one(
        'it.equipement',
        string='Équipement concerné',
        domain="[('partner_id', 'child_of', partner_id)]",
    )
    technicien_id = fields.Many2one('hr.employee', string='Technicien assigné', tracking=True)
    priority = fields.Selection([
        ('0', 'Basse'),
        ('1', 'Normale'),
        ('2', 'Haute'),
        ('3', 'Critique'),
    ], string='Priorité', default='1', tracking=True)
    state = fields.Selection([
        ('new', 'Nouveau'),
        ('assigned', 'Assigné'),
        ('in_progress', 'En cours'),
        ('done', 'Résolu'),
        ('cancelled', 'Annulé'),
    ], string='État', default='new', tracking=True)
    description = fields.Text(string='Description', required=True)
    resolution = fields.Text(string='Résolution')
    date_deadline = fields.Datetime(string='Échéance SLA')
    en_retard = fields.Boolean(
        string='En retard (SLA dépassé)',
        compute='_compute_en_retard',
        store=True,
    )

    @api.depends('date_deadline', 'state')
    def _compute_en_retard(self):
        now = datetime.now()
        for rec in self:
            rec.en_retard = bool(
                rec.date_deadline
                and rec.state not in ('done', 'cancelled')
                and rec.date_deadline < now
            )

    @api.model
    def _cron_mise_a_jour_tickets(self):
        """Recalcule le drapeau « en retard » des tickets ouverts.
        Appelé quotidiennement par la tâche planifiée."""
        tickets = self.search([('state', 'not in', ('done', 'cancelled'))])
        tickets.modified(['date_deadline'])
        tickets.mapped('en_retard')
        return True

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Vide le site et l'équipement s'ils n'appartiennent pas au nouveau client."""
        if self.site_id and self.site_id.partner_id != self.partner_id:
            self.site_id = False
        if self.equipement_id and self.equipement_id.partner_id != self.partner_id:
            self.equipement_id = False

    @api.onchange('equipement_id')
    def _onchange_equipement_id(self):
        """Pré-remplit le client (si vide) et le site depuis l'équipement choisi."""
        if self.equipement_id:
            if self.equipement_id.partner_id and not self.partner_id:
                self.partner_id = self.equipement_id.partner_id
            if self.equipement_id.site_id:
                self.site_id = self.equipement_id.site_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code('it.ticket') or 'Nouveau'
        return super().create(vals_list)

    def action_assign(self):
        self.write({'state': 'assigned'})

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

