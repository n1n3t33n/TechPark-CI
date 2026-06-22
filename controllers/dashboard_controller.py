# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from datetime import date

class ItParcDashboardController(http.Controller):

    @http.route('/it_parc/dashboard/data', type='json', auth='user')
    def get_dashboard_data(self):
        """
        Endpoint JSON-RPC appelé par le composant OWL.
        Retourne tous les KPIs et données graphiques.
        """
        env = request.env
        today = date.today()

        # ── KPI 1 : Total équipements ─────────────────────────────────────
        total_equipements = env['it.equipement'].search_count([])

        # ── KPI 2 : Répartition par état ─────────────────────────────────
        etats = {}
        for etat in ['brouillon', 'affecte', 'location', 'maintenance', 'retire']:
            etats[etat] = env['it.equipement'].search_count([('state', '=', etat)])

        # ── KPI 3 : Garanties expirées ────────────────────────────────────
        garanties_expirees = env['it.equipement'].search_count([
            ('garantie_expiree', '=', True)
        ])

        # ── KPI 4 : Alertes non traitées ─────────────────────────────────
        alertes_nouvelles = env['it.alerte'].search_count([
            ('state', '=', 'nouvelle')
        ])

        # ── KPI 5 : Interventions ce mois ────────────────────────────────
        debut_mois = today.replace(day=1)
        interventions_mois = env['it.intervention'].search_count([
            ('date_debut', '>=', str(debut_mois)),
            ('state', '!=', 'annule'),
        ])

        # ── KPI 6 : Coût total maintenance ───────────────────────────────
        interventions_terminees = env['it.intervention'].search([
            ('state', '=', 'termine')
        ])
        cout_total = sum(interventions_terminees.mapped('cout'))

        # ── KPI 7 : Contrats expirant dans 60 jours ──────────────────────
        contrats_urgents = env['it.contrat'].search_count([
            ('jours_restants', '<=', 60),
            ('state', 'not in', ['resilie', 'renouvele']),
        ])

        # ── Graphique 1 : Équipements par catégorie ───────────────────────
        # Libellés dérivés directement de la définition du champ Selection
        labels_cat = dict(env['it.equipement']._fields['categorie'].selection)
        data_categories = []
        for cat, label in labels_cat.items():
            nb = env['it.equipement'].search_count([('categorie', '=', cat)])
            if nb > 0:
                data_categories.append({
                    'label': label,
                    'value': nb,
                })

        # ── Graphique 2 : Interventions par mois (6 derniers mois) ────────
        from dateutil.relativedelta import relativedelta
        data_interventions_mois = []
        for i in range(5, -1, -1):
            mois_debut = (today - relativedelta(months=i)).replace(day=1)
            mois_fin   = (mois_debut + relativedelta(months=1))
            nb = env['it.intervention'].search_count([
                ('date_debut', '>=', str(mois_debut)),
                ('date_debut', '<',  str(mois_fin)),
                ('state', '!=', 'annule'),
            ])
            data_interventions_mois.append({
                'label': mois_debut.strftime('%b %Y'),
                'value': nb,
            })

        # ── Top 5 équipements les plus maintenus ──────────────────────────
        top_equipements = []
        equipements = env['it.equipement'].search([], order='nb_interventions desc', limit=5)
        for eq in equipements:
            if eq.nb_interventions > 0:
                top_equipements.append({
                    'id':               eq.id,
                    'name':             eq.name,
                    'reference':        eq.reference,
                    'nb_interventions': eq.nb_interventions,
                    'cout_total':       eq.cout_total_maintenance,
                })

        # ── Alertes récentes ──────────────────────────────────────────────
        alertes_recentes = []
        alertes = env['it.alerte'].search(
            [('state', '=', 'nouvelle')],
            order='date_echeance asc',
            limit=5
        )
        for a in alertes:
            alertes_recentes.append({
                'name':          a.name,
                'type_alerte':   a.type_alerte,
                'date_echeance': str(a.date_echeance),
                'jours_restants':a.jours_restants,
            })

        return {
            'kpis': {
                'total_equipements':   total_equipements,
                'affectes':            etats.get('affecte', 0),
                'en_location':         etats.get('location', 0),
                'en_maintenance':      etats.get('maintenance', 0),
                'retires':             etats.get('retire', 0),
                'garanties_expirees':  garanties_expirees,
                'alertes_nouvelles':   alertes_nouvelles,
                'interventions_mois':  interventions_mois,
                'cout_total':          cout_total,
                'contrats_urgents':    contrats_urgents,
            },
            'graphiques': {
                'categories':          data_categories,
                'interventions_mois':  data_interventions_mois,
            },
            'top_equipements':         top_equipements,
            'alertes_recentes':        alertes_recentes,
        }