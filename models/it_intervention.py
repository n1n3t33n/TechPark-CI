# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ItIntervention(models.Model):
    _name = 'it.intervention'
    _description = 'Intervention / Maintenance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_debut desc'

    name = fields.Char(
        string='Objet de l\'intervention',
        required=True
    )
    equipement_id = fields.Many2one(
        'it.equipement',
        string='Équipement',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        related='equipement_id.partner_id',
        store=True,
        readonly=True
    )
    site_id = fields.Many2one(
        'it.site',
        string='Site',
        related='equipement_id.site_id',
        store=True,
        readonly=True
    )
    ticket_id = fields.Many2one('it.ticket', string='Ticket lié')
    type_intervention = fields.Selection([
        ('corrective',  'Corrective'),
        ('preventive',  'Préventive'),
    ], string='Type', required=True, default='corrective')

    technicien_id = fields.Many2one(
        'hr.employee',
        string='Technicien responsable'
    )
    date_debut = fields.Datetime(
        string='Date de début',
        required=True,
        default=fields.Datetime.now
    )
    date_fin   = fields.Datetime(string='Date de fin')

    duree_heures = fields.Float(
        string='Durée (heures)',
        compute='_compute_duree',
        store=True
    )
    cout        = fields.Float(string='Coût (FCFA)')
    rapport     = fields.Text(string='Rapport d\'intervention')
    invoice_id  = fields.Many2one('account.move', string='Facture liée')

    state = fields.Selection([
        ('planifie',  'Planifiée'),
        ('en_cours',  'En cours'),
        ('termine',   'Terminée'),
        ('annule',    'Annulée'),
    ], string='État', default='planifie', tracking=True)

    @api.constrains('date_debut', 'date_fin')
    def _check_dates(self):
        for rec in self:
            if rec.date_debut and rec.date_fin and rec.date_fin < rec.date_debut:
                raise ValidationError(_(
                    "La date de fin ne peut pas être antérieure à la date de début."
                ))

    @api.depends('date_debut', 'date_fin')
    def _compute_duree(self):
        for rec in self:
            if rec.date_debut and rec.date_fin:
                delta = rec.date_fin - rec.date_debut
                rec.duree_heures = delta.total_seconds() / 3600
            else:
                rec.duree_heures = 0.0

    def action_demarrer(self):
        self.state = 'en_cours'

    def action_terminer(self):
        self.state = 'termine'

    def action_annuler(self):
        self.state = 'annule'
