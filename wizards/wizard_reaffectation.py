# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class WizardReaffectation(models.TransientModel):
    _name = 'wizard.reaffectation'
    _description = 'Wizard de réaffectation d\'un équipement'

    equipement_id = fields.Many2one(
        'it.equipement',
        string='Équipement',
        required=True,
        readonly=True,
    )
    # Ancien employé (affiché en lecture seule pour info)
    ancien_employe_id = fields.Many2one(
        'hr.employee',
        string='Employé actuel',
        readonly=True,
    )
    ancien_departement_id = fields.Many2one(
        'hr.department',
        string='Département actuel',
        readonly=True,
    )
    # Nouvel employé
    nouvel_employe_id = fields.Many2one(
        'hr.employee',
        string='Nouvel employé',
        required=True,
    )
    nouveau_departement_id = fields.Many2one(
        'hr.department',
        string='Nouveau département',
    )
    motif = fields.Text(
        string='Motif de la réaffectation',
        required=True,
    )
    date_reaffectation = fields.Date(
        string='Date de réaffectation',
        default=fields.Date.today,
        required=True,
    )

    @api.model
    def default_get(self, fields_list):
        """Pré-remplit le wizard avec les données actuelles de l'équipement."""
        res = super().default_get(fields_list)
        equipement_id = self.env.context.get('active_id')
        if equipement_id:
            equipement = self.env['it.equipement'].browse(equipement_id)
            res.update({
                'equipement_id':        equipement.id,
                'ancien_employe_id':    equipement.employe_id.id,
                'ancien_departement_id':equipement.departement_id.id,
            })
        return res

    def action_confirmer(self):
        """Exécute la réaffectation."""
        self.ensure_one()
        equipement = self.equipement_id

        # 1. Clôturer l'affectation active en cours
        affectation_active = self.env['it.affectation'].search([
            ('equipement_id', '=', equipement.id),
            ('active_line', '=', True),
        ], limit=1)
        if affectation_active:
            affectation_active.write({
                'active_line': False,
                'date_retour': self.date_reaffectation,
            })

        # 2. Créer la nouvelle affectation dans l'historique
        self.env['it.affectation'].create({
            'equipement_id':  equipement.id,
            'employe_id':     self.nouvel_employe_id.id,
            'departement_id': self.nouveau_departement_id.id,
            'date_affectation': self.date_reaffectation,
            'motif':          self.motif,
            'active_line':    True,
        })

        # 3. Mettre à jour l'équipement
        equipement.write({
            'employe_id':    self.nouvel_employe_id.id,
            'departement_id':self.nouveau_departement_id.id,
            'state':         'affecte',
        })

        # 4. Log dans le chatter
        equipement.message_post(
            body=f"Réaffecté à <b>{self.nouvel_employe_id.name}</b> "
                 f"(département : {self.nouveau_departement_id.name or 'N/A'}). "
                 f"Motif : {self.motif}"
        )

        return {'type': 'ir.actions.act_window_close'}