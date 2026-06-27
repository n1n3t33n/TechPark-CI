# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
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

    @api.constrains('date_debut', 'date_fin')
    def _check_dates(self):
        for rec in self:
            if rec.date_debut and rec.date_fin and rec.date_fin < rec.date_debut:
                raise ValidationError(_(
                    "La date de fin du contrat ne peut pas être antérieure à la date de début."
                ))

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Vide le site si celui-ci n'appartient pas au nouveau client."""
        if self.site_id and self.site_id.partner_id != self.partner_id:
            self.site_id = False

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

    @api.model
    def _cron_mise_a_jour_contrats(self):
        """Recalcule les jours restants et passe à 'Expiré' les contrats échus.
        Appelé quotidiennement par la tâche planifiée."""
        contrats = self.search([])
        # Force le recalcul des champs stockés dépendant de la date du jour
        contrats.modified(['date_fin'])
        contrats.mapped('jours_restants')
        # Auto-passage à l'état 'Expiré' (sans toucher aux résiliés/renouvelés)
        today = fields.Date.today()
        a_expirer = contrats.filtered(
            lambda c: c.state == 'actif' and c.date_fin and c.date_fin < today
        )
        if a_expirer:
            a_expirer.write({'state': 'expire'})
        return True

    def action_resilier(self):
        self.state = 'resilie'

    def action_ouvrir_renouvellement(self):
        """Ouvre le wizard de renouvellement pré-rempli pour ce contrat."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Renouveler le contrat',
            'res_model': 'wizard.renouvellement',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id, 'active_model': 'it.contrat'},
        }
