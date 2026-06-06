# -*- coding: utf-8 -*-
import base64
import csv
import io
from odoo import models, fields, api
from odoo.exceptions import UserError

class WizardImportCsv(models.TransientModel):
    _name = 'wizard.import.csv'
    _description = 'Import en masse d\'équipements via CSV'

    fichier_csv = fields.Binary(
        string='Fichier CSV',
        required=True,
    )
    nom_fichier = fields.Char(string='Nom du fichier')

    # Résultats affichés après import
    resultat = fields.Text(
        string='Résultat de l\'import',
        readonly=True,
    )
    import_effectue = fields.Boolean(default=False)

    def action_importer(self):
        self.ensure_one()
        if not self.fichier_csv:
            raise UserError("Veuillez sélectionner un fichier CSV.")

        # Décoder le fichier base64
        contenu = base64.b64decode(self.fichier_csv).decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(contenu), delimiter=',')

        crees    = 0
        ignores  = 0
        erreurs  = []
        lignes_erreur = []

        # Colonnes attendues dans le CSV :
        # name, categorie, marque, modele, numero_serie, site, valeur_achat, date_fin_garantie
        colonnes_requises = {'name', 'categorie', 'site'}

        for i, ligne in enumerate(reader, start=2):
            # Vérifier les colonnes obligatoires
            manquantes = colonnes_requises - set(ligne.keys())
            if manquantes:
                raise UserError(
                    f"Colonnes obligatoires manquantes dans le CSV : {manquantes}\n"
                    f"Colonnes attendues : name, categorie, site (+ optionnel : "
                    f"marque, modele, numero_serie, valeur_achat, date_fin_garantie)"
                )

            try:
                numero_serie = ligne.get('numero_serie', '').strip()

                # Détecter les doublons par numéro de série
                if numero_serie:
                    existant = self.env['it.equipement'].search([
                        ('numero_serie', '=', numero_serie)
                    ], limit=1)
                    if existant:
                        ignores += 1
                        continue

                # Préparer les valeurs
                vals = {
                    'name':     ligne.get('name', '').strip(),
                    'categorie':ligne.get('categorie', 'autre').strip(),
                    'site':     ligne.get('site', 'abidjan_cocody').strip(),
                    'marque':   ligne.get('marque', '').strip(),
                    'modele':   ligne.get('modele', '').strip(),
                    'numero_serie': numero_serie,
                }

                # Champs optionnels
                if ligne.get('valeur_achat'):
                    try:
                        vals['valeur_achat'] = float(ligne['valeur_achat'])
                    except ValueError:
                        pass

                if ligne.get('date_fin_garantie'):
                    vals['date_fin_garantie'] = ligne['date_fin_garantie'].strip()

                if not vals['name']:
                    lignes_erreur.append(f"Ligne {i} : nom manquant.")
                    continue

                self.env['it.equipement'].create(vals)
                crees += 1

            except Exception as e:
                lignes_erreur.append(f"Ligne {i} : {str(e)}")

        # Construire le rapport d'import
        rapport = (
            f"✅ Équipements créés   : {crees}\n"
            f"⚠️  Doublons ignorés   : {ignores}\n"
            f"❌ Erreurs             : {len(lignes_erreur)}\n"
        )
        if lignes_erreur:
            rapport += "\nDétail des erreurs :\n" + "\n".join(lignes_erreur)

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