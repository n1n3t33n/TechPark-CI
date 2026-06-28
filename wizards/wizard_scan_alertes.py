# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date

class WizardScanAlertes(models.TransientModel):
    _name = 'wizard.scan.alertes'
    _description = 'Scan manuel des alertes garanties et contrats'

    delai_jours = fields.Integer(
        string='Délai d\'alerte (jours)',
        default=60,
        required=True,
        help="Générer des alertes pour les échéances dans moins de X jours."
    )
    resultat = fields.Text(
        string='Résultat du scan',
        readonly=True,
    )
    scan_effectue = fields.Boolean(default=False)

    def action_scanner(self):
        self.ensure_one()
        today = date.today()
        alertes_crees = 0
        alertes_ignorees = 0

        # ── 1. Scanner les garanties d'équipements ────────────────────────
        equipements = self.env['it.equipement'].search([
            ('date_fin_garantie', '!=', False),
            ('state', '!=', 'retire'),
        ])
        for eq in equipements:
            jours = (eq.date_fin_garantie - today).days
            if jours <= self.delai_jours:
                # Vérifier si une alerte existe déjà pour cet équipement
                existante = self.env['it.alerte'].search([
                    ('equipement_id', '=', eq.id),
                    ('type_alerte', '=', 'garantie'),
                    ('state', '!=', 'traitee'),
                ], limit=1)
                if not existante:
                    self.env['it.alerte'].create({
                        'name': f"Garantie expirant bientôt : {eq.name}",
                        'type_alerte': 'garantie',
                        'equipement_id': eq.id,
                        'date_echeance': eq.date_fin_garantie,
                        'jours_restants': jours,
                        'message': (
                            f"La garantie de l'équipement '{eq.name}' "
                            f"(réf. {eq.reference}) expire dans {jours} jour(s), "
                            f"le {eq.date_fin_garantie}."
                        ),
                    })
                    alertes_crees += 1
                else:
                    # Mettre à jour les jours restants
                    existante.jours_restants = jours
                    alertes_ignorees += 1

        # ── 2. Scanner les contrats ───────────────────────────────────────
        contrats = self.env['it.contrat'].search([
            ('date_fin', '!=', False),
            ('state', 'not in', ['resilie', 'renouvele']),
        ])
        for contrat in contrats:
            jours = (contrat.date_fin - today).days
            if jours <= self.delai_jours:
                existante = self.env['it.alerte'].search([
                    ('contrat_id', '=', contrat.id),
                    ('type_alerte', '=', 'contrat'),
                    ('state', '!=', 'traitee'),
                ], limit=1)
                if not existante:
                    self.env['it.alerte'].create({
                        'name': f"Contrat expirant bientôt : {contrat.name}",
                        'type_alerte': 'contrat',
                        'contrat_id': contrat.id,
                        'equipement_id': contrat.equipement_id.id or False,
                        'date_echeance': contrat.date_fin,
                        'jours_restants': jours,
                        'message': (
                            f"Le contrat '{contrat.name}' avec {contrat.fournisseur_id.name} "
                            f"expire dans {jours} jour(s), le {contrat.date_fin}."
                        ),
                    })
                    alertes_crees += 1
                else:
                    existante.jours_restants = jours
                    alertes_ignorees += 1

        # ── 3. Scanner les licences logicielles ───────────────────────────
        licences = self.env['it.license'].search([
            ('date_expiration', '!=', False),
        ])
        for lic in licences:
            jours = (lic.date_expiration - today).days
            if jours <= self.delai_jours:
                existante = self.env['it.alerte'].search([
                    ('license_id', '=', lic.id),
                    ('type_alerte', '=', 'licence'),
                    ('state', '!=', 'traitee'),
                ], limit=1)
                if not existante:
                    self.env['it.alerte'].create({
                        'name': f"Licence expirant bientôt : {lic.name}",
                        'type_alerte': 'licence',
                        'license_id': lic.id,
                        'equipement_id': lic.equipement_id.id or False,
                        'date_echeance': lic.date_expiration,
                        'jours_restants': jours,
                        'message': (
                            f"La licence '{lic.name}'"
                            f"{' (' + lic.partner_id.name + ')' if lic.partner_id else ''} "
                            f"expire dans {jours} jour(s), le {lic.date_expiration}."
                        ),
                    })
                    alertes_crees += 1
                else:
                    existante.jours_restants = jours
                    alertes_ignorees += 1

        # ── 4. Scanner les fins de location d'équipements ──────────────────
        locations = self.env['it.equipement'].search([
            ('state', '=', 'location'),
            ('date_fin_location', '!=', False),
        ])
        for eq in locations:
            jours = (eq.date_fin_location - today).days
            if jours <= self.delai_jours:
                existante = self.env['it.alerte'].search([
                    ('equipement_id', '=', eq.id),
                    ('type_alerte', '=', 'location'),
                    ('state', '!=', 'traitee'),
                ], limit=1)
                if not existante:
                    self.env['it.alerte'].create({
                        'name': f"Fin de location proche : {eq.name}",
                        'type_alerte': 'location',
                        'equipement_id': eq.id,
                        'date_echeance': eq.date_fin_location,
                        'jours_restants': jours,
                        'message': (
                            f"La location de '{eq.name}'"
                            f"{' par ' + eq.locataire_id.name if eq.locataire_id else ''} "
                            f"se termine dans {jours} jour(s), le {eq.date_fin_location}."
                        ),
                    })
                    alertes_crees += 1
                else:
                    existante.jours_restants = jours
                    alertes_ignorees += 1

        rapport = (
            f"✅ Nouvelles alertes créées : {alertes_crees}\n"
            f"ℹ️  Alertes déjà existantes  : {alertes_ignorees}\n"
            f"📅 Délai scanné             : {self.delai_jours} jours\n"
            f"🗓️  Date du scan             : {today}"
        )
        self.write({
            'resultat': rapport,
            'scan_effectue': True,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }