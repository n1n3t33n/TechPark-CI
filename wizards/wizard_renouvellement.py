# -*- coding: utf-8 -*-
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class WizardRenouvellement(models.TransientModel):
    _name = 'wizard.renouvellement'
    _description = 'Wizard de renouvellement de contrat'

    contrat_id = fields.Many2one(
        'it.contrat',
        string='Contrat',
        required=True,
        readonly=True,
    )
    ancienne_date_fin = fields.Date(
        string='Ancienne date de fin',
        readonly=True,
    )
    nouvelle_date_fin = fields.Date(
        string='Nouvelle date de fin',
        required=True,
    )
    nouveau_montant = fields.Float(
        string='Nouveau montant (FCFA)',
    )
    notes = fields.Text(string='Notes de renouvellement')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        contrat_id = self.env.context.get('active_id')
        if contrat_id:
            contrat = self.env['it.contrat'].browse(contrat_id)
            # Propose automatiquement +1 an
            nouvelle_date = contrat.date_fin + relativedelta(years=1)
            res.update({
                'contrat_id':       contrat.id,
                'ancienne_date_fin':contrat.date_fin,
                'nouvelle_date_fin':nouvelle_date,
                'nouveau_montant':  contrat.montant,
            })
        return res

    def action_confirmer(self):
        self.ensure_one()
        contrat = self.contrat_id
        contrat.write({
            'date_fin': self.nouvelle_date_fin,
            'montant':  self.nouveau_montant or contrat.montant,
            'state':    'renouvele',
        })
        contrat.message_post(
            body=f"Contrat renouvelé jusqu'au <b>{self.nouvelle_date_fin}</b>. "
                 f"Nouveau montant : {self.nouveau_montant or contrat.montant} FCFA. "
                 f"{self.notes or ''}"
        )
        return {'type': 'ir.actions.act_window_close'}