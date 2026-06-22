# -*- coding: utf-8 -*-
import base64
import csv
import io
from odoo import models, fields, _
from odoo.exceptions import UserError


class WizardImportCsv(models.TransientModel):
    _name = 'wizard.import.csv'
    _description = 'Import en masse d\'équipements via CSV'

    fichier_csv = fields.Binary(
        string='Fichier CSV',
        required=True,
    )
    nom_fichier = fields.Char(string='Nom du fichier')

    # Rattachement appliqué à tous les équipements importés
    partner_id = fields.Many2one('res.partner', string='Client à associer')
    site_id = fields.Many2one(
        'it.site',
        string='Site client à associer',
        domain="[('partner_id', 'child_of', partner_id)]",
    )

    # Résultats affichés après import
    resultat = fields.Text(
        string='Résultat de l\'import',
        readonly=True,
    )
    import_effectue = fields.Boolean(default=False)

    def action_importer(self):
        self.ensure_one()
        if not self.fichier_csv:
            raise UserError(_("Veuillez sélectionner un fichier CSV."))

        # Décoder le fichier base64
        contenu = base64.b64decode(self.fichier_csv).decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(contenu), delimiter=',')

        crees = 0
        ignores = 0
        lignes_erreur = []

        # Colonnes attendues dans le CSV :
        # name, categorie, marque, modele, numero_serie, cpu, ram_go,
        # stockage_go, valeur_achat, date_fin_garantie
        colonnes_requises = {'name', 'categorie'}
        categories_valides = dict(
            self.env['it.equipement']._fields['categorie'].selection
        )

        for i, ligne in enumerate(reader, start=2):
            # Vérifier les colonnes obligatoires
            manquantes = colonnes_requises - set(ligne.keys())
            if manquantes:
                raise UserError(_(
                    "Colonnes obligatoires manquantes dans le CSV : %s\n"
                    "Colonnes attendues : name, categorie (+ optionnel : "
                    "marque, modele, numero_serie, cpu, ram_go, stockage_go, "
                    "valeur_achat, date_fin_garantie)"
                ) % ', '.join(manquantes))

            try:
                numero_serie = (ligne.get('numero_serie') or '').strip()

                # Détecter les doublons par numéro de série
                if numero_serie:
                    existant = self.env['it.equipement'].search([
                        ('numero_serie', '=', numero_serie)
                    ], limit=1)
                    if existant:
                        ignores += 1
                        continue

                nom = (ligne.get('name') or '').strip()
                if not nom:
                    lignes_erreur.append(_("Ligne %s : nom manquant.") % i)
                    continue

                categorie = (ligne.get('categorie') or 'autre').strip()
                if categorie not in categories_valides:
                    categorie = 'autre'

                # Préparer les valeurs (rattachement client/site appliqué à tous)
                vals = {
                    'name':         nom,
                    'categorie':    categorie,
                    'marque':       (ligne.get('marque') or '').strip(),
                    'modele':       (ligne.get('modele') or '').strip(),
                    'numero_serie': numero_serie,
                    'cpu':          (ligne.get('cpu') or '').strip(),
                }
                if self.partner_id:
                    vals['partner_id'] = self.partner_id.id
                if self.site_id:
                    vals['site_id'] = self.site_id.id

                for champ in ('ram_go', 'stockage_go'):
                    if ligne.get(champ):
                        try:
                            vals[champ] = int(float(ligne[champ]))
                        except ValueError:
                            pass

                if ligne.get('valeur_achat'):
                    try:
                        vals['valeur_achat'] = float(ligne['valeur_achat'])
                    except ValueError:
                        pass

                if ligne.get('date_fin_garantie'):
                    vals['date_fin_garantie'] = ligne['date_fin_garantie'].strip()

                self.env['it.equipement'].create(vals)
                crees += 1

            except Exception as e:
                lignes_erreur.append(_("Ligne %s : %s") % (i, str(e)))

        # Construire le rapport d'import
        rapport = _(
            "Équipements créés   : %(crees)s\n"
            "Doublons ignorés    : %(ignores)s\n"
            "Erreurs             : %(erreurs)s\n"
        ) % {'crees': crees, 'ignores': ignores, 'erreurs': len(lignes_erreur)}
        if lignes_erreur:
            rapport += _("\nDétail des erreurs :\n") + "\n".join(lignes_erreur)

        self.write({
            'resultat': rapport,
            'import_effectue': True,
        })

        # Réouvrir le wizard pour afficher le résultat
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
