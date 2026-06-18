# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date

class ItContrat(models.Model):
    _name = 'it.contrat'
    _description = 'Contrat fournisseur'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'it.export.excel']
    _order = 'date_fin asc'

    name = fields.Char(string='Intitulé du contrat', required=True)
    reference = fields.Char(string='Référence contrat')

    fournisseur_id = fields.Many2one(
        'res.partner',
        string='Fournisseur',
        required=True
    )
    partner_id = fields.Many2one('res.partner', string='Client', tracking=True)
    type_contrat = fields.Selection([
        ('maintenance', 'Maintenance'),
        ('licence',     'Licence logicielle'),
        ('support',     'Support technique'),
        ('autre',       'Autre'),
    ], string='Type de contrat', required=True)

    date_debut  = fields.Date(string='Date de début', required=True)
    date_fin    = fields.Date(string='Date de fin',   required=True, tracking=True)
    montant     = fields.Float(string='Montant (FCFA)')

    equipement_id = fields.Many2one(
        'it.equipement',
        string='Équipement concerné',
        ondelete='set null'
    )
    site_id = fields.Many2one('it.site', string='Site client', domain="[('partner_id', 'child_of', partner_id)]")
    invoice_id = fields.Many2one('account.move', string='Facture liée')
    description = fields.Text(string='Description / Conditions')

    jours_restants = fields.Integer(
        string='Jours restants',
        compute='_compute_jours_restants',
        store=True
    )
    expire = fields.Boolean(
        string='Expiré',
        compute='_compute_jours_restants',
        store=True
    )
    state = fields.Selection([
        ('actif',    'Actif'),
        ('expire',   'Expiré'),
        ('renouvele','Renouvelé'),
        ('resilie',  'Résilié'),
    ], string='État', default='actif', tracking=True)

    @api.depends('date_fin')
    def _compute_jours_restants(self):
        today = date.today()
        for rec in self:
            if rec.date_fin:
                delta = (rec.date_fin - today).days
                rec.jours_restants = delta
                rec.expire = delta < 0
            else:
                rec.jours_restants = 0
                rec.expire = False

    def action_resilier(self):
        self.state = 'resilie'
