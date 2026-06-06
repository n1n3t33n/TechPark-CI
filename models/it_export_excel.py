# -*- coding: utf-8 -*-
import io
import base64
from datetime import date
import xlsxwriter
from odoo import models, fields, api

class ItExportExcel(models.AbstractModel):
    """
    Modèle abstrait portant toutes les méthodes d'export Excel.
    AbstractModel = pas de table en base de données, juste de la logique.
    On l'hérite dans les modèles concernés via _inherit.
    """
    _name = 'it.export.excel'
    _description = 'Exports Excel du parc informatique'

    # ─────────────────────────────────────────────────────────────────────────
    # EXPORT 1 — Inventaire complet
    # ─────────────────────────────────────────────────────────────────────────
    def action_export_inventaire_excel(self):
        """Génère l'inventaire complet de tous les équipements."""
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Inventaire')

        # ── Styles ────────────────────────────────────────────────────────
        fmt_titre = workbook.add_format({
            'bold': True, 'font_size': 16,
            'font_color': '#1F4E79', 'align': 'left'
        })
        fmt_entete = workbook.add_format({
            'bold': True, 'bg_color': '#1F4E79',
            'font_color': 'white', 'border': 1,
            'align': 'center', 'valign': 'vcenter',
            'text_wrap': True
        })
        fmt_normal = workbook.add_format({
            'border': 1, 'valign': 'vcenter'
        })
        fmt_nombre = workbook.add_format({
            'border': 1, 'num_format': '#,##0', 'align': 'right'
        })
        fmt_date = workbook.add_format({
            'border': 1, 'num_format': 'dd/mm/yyyy', 'align': 'center'
        })
        fmt_garantie_ok = workbook.add_format({
            'border': 1, 'bg_color': '#E2EFDA', 'align': 'center'
        })
        fmt_garantie_warn = workbook.add_format({
            'border': 1, 'bg_color': '#FFF2CC', 'align': 'center'
        })
        fmt_garantie_expire = workbook.add_format({
            'border': 1, 'bg_color': '#FFE0E0',
            'font_color': '#C00000', 'bold': True, 'align': 'center'
        })
        fmt_etat = {
            'brouillon':  workbook.add_format({'border':1,'bg_color':'#D9D9D9','align':'center'}),
            'affecte':    workbook.add_format({'border':1,'bg_color':'#E2EFDA','align':'center'}),
            'maintenance':workbook.add_format({'border':1,'bg_color':'#FFF2CC','align':'center'}),
            'retire':     workbook.add_format({'border':1,'bg_color':'#FFE0E0','align':'center'}),
        }

        # ── Titre ─────────────────────────────────────────────────────────
        sheet.merge_range('A1:J1', 'INVENTAIRE DU PARC INFORMATIQUE — TECHPARK CI', fmt_titre)
        sheet.write('A2', f"Généré le : {date.today().strftime('%d/%m/%Y')}", 
                    workbook.add_format({'italic': True, 'font_color': '#666666'}))
        sheet.write_blank('B2', None)

        # ── En-têtes colonnes ─────────────────────────────────────────────
        colonnes = [
            ('Référence',      15),
            ('Nom',            25),
            ('Catégorie',      15),
            ('Marque',         12),
            ('Modèle',         15),
            ('N° Série',       18),
            ('Site',           18),
            ('Employé affecté',20),
            ('Département',    18),
            ('Date achat',     13),
            ('Valeur achat\n(FCFA)', 15),
            ('Date fin\ngarantie',  13),
            ('Jours\nrestants',     10),
            ('État',           14),
        ]
        for col, (nom, largeur) in enumerate(colonnes):
            sheet.write(3, col, nom, fmt_entete)
            sheet.set_column(col, col, largeur)
        sheet.set_row(3, 30)

        # ── Données ───────────────────────────────────────────────────────
        equipements = self.env['it.equipement'].search([], order='reference asc')
        for row, eq in enumerate(equipements, start=4):
            sheet.write(row, 0,  eq.reference or '',          fmt_normal)
            sheet.write(row, 1,  eq.name or '',               fmt_normal)
            sheet.write(row, 2,  eq.categorie or '',          fmt_normal)
            sheet.write(row, 3,  eq.marque or '',             fmt_normal)
            sheet.write(row, 4,  eq.modele or '',             fmt_normal)
            sheet.write(row, 5,  eq.numero_serie or '',       fmt_normal)
            sheet.write(row, 6,  eq.site or '',               fmt_normal)
            sheet.write(row, 7,  eq.employe_id.name if eq.employe_id else '', fmt_normal)
            sheet.write(row, 8,  eq.departement_id.name if eq.departement_id else '', fmt_normal)

            if eq.date_achat:
                sheet.write_datetime(row, 9, eq.date_achat, fmt_date)
            else:
                sheet.write_blank(row, 9, None, fmt_normal)

            sheet.write_number(row, 10, eq.valeur_achat or 0, fmt_nombre)

            # Couleur conditionnelle sur la garantie
            if eq.date_fin_garantie:
                if eq.garantie_expiree:
                    fmt_g = fmt_garantie_expire
                elif eq.jours_garantie_restants < 90:
                    fmt_g = fmt_garantie_warn
                else:
                    fmt_g = fmt_garantie_ok
                sheet.write_datetime(row, 11, eq.date_fin_garantie, fmt_g)
                sheet.write_number(row, 12, eq.jours_garantie_restants, fmt_g)
            else:
                sheet.write_blank(row, 11, None, fmt_normal)
                sheet.write_blank(row, 12, None, fmt_normal)

            sheet.write(row, 13, eq.state or '',
                        fmt_etat.get(eq.state, fmt_normal))

        # ── Figer la ligne d'en-tête ──────────────────────────────────────
        sheet.freeze_panes(4, 0)

        workbook.close()
        output.seek(0)

        # ── Retourner comme pièce jointe ──────────────────────────────────
        nom_fichier = f"inventaire_parc_{date.today().strftime('%Y%m%d')}.xlsx"
        return self._retourner_fichier_excel(output, nom_fichier)

    # ─────────────────────────────────────────────────────────────────────────
    # EXPORT 2 — Synthèse des coûts de maintenance
    # ─────────────────────────────────────────────────────────────────────────
    def action_export_couts_maintenance_excel(self):
        """Synthèse des coûts de maintenance par équipement et par mois."""
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Coûts maintenance')

        fmt_titre = workbook.add_format({
            'bold': True, 'font_size': 16, 'font_color': '#1F4E79'
        })
        fmt_entete = workbook.add_format({
            'bold': True, 'bg_color': '#375623',
            'font_color': 'white', 'border': 1, 'align': 'center'
        })
        fmt_normal  = workbook.add_format({'border': 1})
        fmt_nombre  = workbook.add_format({'border': 1, 'num_format': '#,##0', 'align': 'right'})
        fmt_total   = workbook.add_format({
            'bold': True, 'bg_color': '#E2EFDA',
            'border': 1, 'num_format': '#,##0', 'align': 'right'
        })
        fmt_zero    = workbook.add_format({
            'border': 1, 'font_color': '#AAAAAA',
            'align': 'right', 'num_format': '#,##0'
        })

        sheet.merge_range('A1:F1', 'SYNTHÈSE DES COÛTS DE MAINTENANCE — TECHPARK CI', fmt_titre)
        sheet.write('A2', f"Généré le : {date.today().strftime('%d/%m/%Y')}",
                    workbook.add_format({'italic': True, 'font_color': '#666666'}))

        # En-têtes
        headers = ['Équipement', 'Référence', 'Nb interventions',
                   'Durée totale (h)', 'Coût total (FCFA)', 'Dernière intervention']
        largeurs = [30, 15, 18, 18, 20, 20]
        for col, (h, l) in enumerate(zip(headers, largeurs)):
            sheet.write(3, col, h, fmt_entete)
            sheet.set_column(col, col, l)
        sheet.set_row(3, 25)

        # Données — groupées par équipement
        equipements = self.env['it.equipement'].search(
            [('intervention_ids', '!=', False)], order='name asc'
        )
        total_global = 0
        for row, eq in enumerate(equipements, start=4):
            interventions = eq.intervention_ids.filtered(
                lambda i: i.state == 'termine'
            )
            nb       = len(interventions)
            duree    = sum(interventions.mapped('duree_heures'))
            cout     = sum(interventions.mapped('cout'))
            derniere = max(interventions.mapped('date_debut')) if interventions else False

            total_global += cout

            sheet.write(row, 0, eq.name, fmt_normal)
            sheet.write(row, 1, eq.reference or '', fmt_normal)
            sheet.write_number(row, 2, nb,    fmt_nombre if nb else fmt_zero)
            sheet.write_number(row, 3, duree, fmt_nombre if duree else fmt_zero)
            sheet.write_number(row, 4, cout,  fmt_nombre if cout else fmt_zero)
            if derniere:
                sheet.write(row, 5, str(derniere)[:10], fmt_normal)
            else:
                sheet.write_blank(row, 5, None, fmt_normal)

        # Ligne total
        last_row = 4 + len(equipements)
        sheet.write(last_row, 3, 'TOTAL', fmt_total)
        sheet.write_number(last_row, 4, total_global, fmt_total)

        sheet.freeze_panes(4, 0)
        workbook.close()
        output.seek(0)

        nom_fichier = f"couts_maintenance_{date.today().strftime('%Y%m%d')}.xlsx"
        return self._retourner_fichier_excel(output, nom_fichier)

    # ─────────────────────────────────────────────────────────────────────────
    # EXPORT 3 — Contrats expirant dans les 60 jours
    # ─────────────────────────────────────────────────────────────────────────
    def action_export_contrats_excel(self):
        """Liste des contrats expirant dans les 60 jours avec mise en couleur."""
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Contrats à renouveler')

        fmt_titre = workbook.add_format({
            'bold': True, 'font_size': 16, 'font_color': '#1F4E79'
        })
        fmt_entete = workbook.add_format({
            'bold': True, 'bg_color': '#833C00',
            'font_color': 'white', 'border': 1, 'align': 'center'
        })
        fmt_normal  = workbook.add_format({'border': 1})
        fmt_nombre  = workbook.add_format({'border': 1, 'num_format': '#,##0', 'align': 'right'})
        fmt_date    = workbook.add_format({'border': 1, 'num_format': 'dd/mm/yyyy', 'align': 'center'})
        # Couleurs selon urgence
        fmt_urgent  = workbook.add_format({
            'border': 1, 'bg_color': '#FFE0E0',
            'font_color': '#C00000', 'bold': True
        })
        fmt_warning = workbook.add_format({
            'border': 1, 'bg_color': '#FFF2CC'
        })
        fmt_ok      = workbook.add_format({
            'border': 1, 'bg_color': '#E2EFDA'
        })

        sheet.merge_range('A1:G1',
            'CONTRATS EXPIRANT DANS LES 60 JOURS — TECHPARK CI', fmt_titre)
        sheet.write('A2', f"Généré le : {date.today().strftime('%d/%m/%Y')}",
                    workbook.add_format({'italic': True, 'font_color': '#666666'}))

        headers  = ['Intitulé', 'Référence', 'Type', 'Fournisseur',
                    'Équipement', 'Date fin', 'Jours restants', 'Montant (FCFA)']
        largeurs = [30, 15, 15, 25, 25, 13, 15, 18]
        for col, (h, l) in enumerate(zip(headers, largeurs)):
            sheet.write(3, col, h, fmt_entete)
            sheet.set_column(col, col, l)
        sheet.set_row(3, 25)

        # Contrats expirant dans 60 jours
        contrats = self.env['it.contrat'].search([
            ('jours_restants', '<=', 60),
            ('state', 'not in', ['resilie', 'renouvele']),
        ], order='jours_restants asc')

        for row, c in enumerate(contrats, start=4):
            # Choisir le format selon l'urgence
            if c.expire or c.jours_restants < 0:
                fmt_ligne = fmt_urgent
            elif c.jours_restants <= 30:
                fmt_ligne = fmt_warning
            else:
                fmt_ligne = fmt_ok

            sheet.write(row, 0, c.name or '',                   fmt_ligne)
            sheet.write(row, 1, c.reference or '',              fmt_ligne)
            sheet.write(row, 2, c.type_contrat or '',           fmt_ligne)
            sheet.write(row, 3, c.fournisseur_id.name if c.fournisseur_id else '', fmt_ligne)
            sheet.write(row, 4, c.equipement_id.name if c.equipement_id else '',   fmt_ligne)
            if c.date_fin:
                sheet.write_datetime(row, 5, c.date_fin, fmt_date)
            else:
                sheet.write_blank(row, 5, None, fmt_ligne)
            sheet.write_number(row, 6, c.jours_restants, fmt_ligne)
            sheet.write_number(row, 7, c.montant or 0,   fmt_nombre)

        # Légende
        last_row = 5 + len(contrats)
        sheet.write(last_row, 0, 'Légende :',
                    workbook.add_format({'bold': True}))
        sheet.write(last_row + 1, 0, 'Expiré ou < 0 jour',  fmt_urgent)
        sheet.write(last_row + 2, 0, '1 à 30 jours',         fmt_warning)
        sheet.write(last_row + 3, 0, '31 à 60 jours',        fmt_ok)

        sheet.freeze_panes(4, 0)
        workbook.close()
        output.seek(0)

        nom_fichier = f"contrats_a_renouveler_{date.today().strftime('%Y%m%d')}.xlsx"
        return self._retourner_fichier_excel(output, nom_fichier)

    # ─────────────────────────────────────────────────────────────────────────
    # Méthode utilitaire partagée
    # ─────────────────────────────────────────────────────────────────────────
    def _retourner_fichier_excel(self, output, nom_fichier):
        """
        Encode le fichier en base64, crée une pièce jointe
        et retourne une action de téléchargement.
        """
        contenu_b64 = base64.b64encode(output.read())

        attachment = self.env['ir.attachment'].create({
            'name':     nom_fichier,
            'type':     'binary',
            'datas':    contenu_b64,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type':  'ir.actions.act_url',
            'url':   f'/web/content/{attachment.id}?download=true',
            'target':'self',
        }