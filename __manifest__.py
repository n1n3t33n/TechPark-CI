# -*- coding: utf-8 -*-
{
    'name': 'IT Parc - Gestion de parc informatique',
    'version': '18.0.1.0.0',
    'category': 'Technical',
    'summary': 'Gestion complète du parc informatique de TECHPARK CI',
    'description': """
        Module de gestion de parc informatique pour TECHPARK CI.
        Fonctionnalités :
        - Gestion des équipements avec workflow
        - Affectation aux employés et départements
        - Suivi des interventions (maintenance)
        - Gestion des contrats fournisseurs
        - Alertes automatiques (garanties, contrats)
        - Import en masse CSV
        - Rapports PDF (QWeb) et exports Excel
        - Dashboard OWL avec KPIs
    """,
    'author': 'TECHPARK CI',
    'depends': [
        'base',
        'hr',
        'mail',
        'web',
        'portal',
        'sale',
        'stock',
        'account',
    ],
    'external_dependencies': {
        'python': ['xlsxwriter'],
    },
    'data': [
        # Sécurité - toujours en premier
        'security/security_groups.xml',
        'security/ir.model.access.csv',

        # Données système
        'data/sequences.xml',
        'data/ir_cron.xml',

        # Vues
        'views/site_views.xml',
        'views/equipement_views.xml',
        'views/affectation_views.xml',
        'views/intervention_views.xml',
        'views/contrat_views.xml',
        'views/ticket_views.xml',
        'views/license_views.xml',
        'views/alerte_views.xml',
        'views/portal_templates.xml',

        # Wizards
        'views/wizard_reaffectation_views.xml',
        'views/wizard_renouvellement_views.xml',
        'views/wizard_import_csv_views.xml',
        'views/wizard_scan_alertes_views.xml',

        # Rapports PDF
        'report/report_fiche_equipement.xml',
        'report/report_inventaire.xml',
        'report/report_historique_maintenance.xml',
        'report/report_fiche_equipement_template.xml',
        'report/report_inventaire_template.xml',
        'report/report_historique_template.xml',

        # Menus - toujours en dernier
        'views/dashboard_action.xml',
        'views/menus.xml',
    ],
    'demo': [
        'data/it_parc_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'it_parc/static/src/dashboard/dashboard.js',
            'it_parc/static/src/dashboard/dashboard.xml',
            'it_parc/static/src/dashboard/dashboard.css',
        ],
        'web.assets_frontend': [
            'it_parc/static/src/portal/portal.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
