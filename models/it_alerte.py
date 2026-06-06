# -*- coding: utf-8 -*-
from odoo import models, fields

class ItAlerte(models.Model):
    _name = 'it.alerte'
    _description = 'Alerte garantie ou contrat'
    _order = 'date_echeance asc'

    name = fields.Char(string='Objet de l\'alerte', required=True)

    type_alerte = fields.Selection([
        ('garantie', 'Fin de garantie'),
        ('contrat',  'Expiration contrat'),
    ], string='Type', required=True)

    equipement_id = fields.Many2one(
        'it.equipement',
        string='Équipement concerné'
    )
    contrat_id = fields.Many2one(
        'it.contrat',
        string='Contrat concerné'
    )

    date_echeance   = fields.Date(string='Date d\'échéance', required=True)
    jours_restants  = fields.Integer(string='Jours restants')
    message         = fields.Text(string='Message de l\'alerte')

    state = fields.Selection([
        ('nouvelle',  'Nouvelle'),
        ('vue',       'Vue'),
        ('traitee',   'Traitée'),
    ], string='État', default='nouvelle')

    def action_marquer_vue(self):
        self.state = 'vue'

    def action_marquer_traitee(self):
        self.state = 'traitee'