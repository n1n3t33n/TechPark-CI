# -*- coding: utf-8 -*-
from odoo import models, fields

class ItAffectation(models.Model):
    _name = 'it.affectation'
    _description = 'Historique des affectations'
    _order = 'date_affectation desc'

    equipement_id = fields.Many2one(
        'it.equipement',
        string='Équipement',
        required=True,
        ondelete='cascade'
    )
    employe_id = fields.Many2one(
        'hr.employee',
        string='Employé',
        required=True
    )
    departement_id = fields.Many2one(
        'hr.department',
        string='Département'
    )
    date_affectation = fields.Date(
        string='Date d\'affectation',
        required=True,
        default=fields.Date.today
    )
    date_retour    = fields.Date(string='Date de retour')
    localisation   = fields.Char(string='Localisation précise (bureau, salle...)')
    motif          = fields.Text(string='Motif de l\'affectation / réaffectation')
    active_line    = fields.Boolean(string='Affectation active', default=True)