# IT Parc — Module Odoo 18
Gestion de parc informatique pour TECHPARK CI

## Prérequis
- Odoo 18
- Python 3.11+
- PostgreSQL 16
- wkhtmltopdf installé et configuré
- xlsxwriter : `pip install xlsxwriter`

## Installation

1. Copie le dossier `it_parc/` dans ton dossier `addons/` d'Odoo.

2. Redémarre le serveur Odoo : python odoo-bin -c odoo.conf

3. Dans Odoo, active le **mode développeur** :
   Paramètres → Activer le mode développeur

4. Va dans **Paramètres → Applications**, cherche **IT Parc** et clique **Installer**.

5. Pour charger les données de démo, installe avec l'option "Charger les données de démonstration" cochée.

## Mise à jour du module
python odoo-bin -c odoo.conf -u it_parc

## Groupes de sécurité
- **IT Technicien** : consultation des équipements, création d'interventions
- **IT Manager** : accès complet (équipements, contrats, alertes, exports, dashboard)

## Fonctionnalités
- Gestion des équipements (workflow 4 étapes)
- Affectation aux employés avec historique complet
- Suivi des interventions avec vue calendrier
- Gestion des contrats fournisseurs
- Alertes automatiques garanties et contrats (cron quotidien)
- Import CSV en masse
- 3 rapports PDF (QWeb)
- 3 exports Excel (xlsxwriter)
- Dashboard OWL avec 7 KPIs et 2 graphiques