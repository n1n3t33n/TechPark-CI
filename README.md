# IT Parc — Module Odoo 18
Gestion de parc informatique pour TECHPARK CI

## Prérequis
- Odoo 18
- Python 3.11+
- PostgreSQL 16
- wkhtmltopdf installé et configuré (ou Chromium pour la génération PDF)
- xlsxwriter : `pip install xlsxwriter`

## Installation pas à pas

### 1. Copier le module
Copie le dossier `it_parc/` dans le dossier `addons/` de ton installation Odoo :
```
odoo-18.0/addons/it_parc/
```

### 2. Installer la dépendance Python
```bash
pip install xlsxwriter
```

### 3. Démarrer le serveur Odoo
```bash
python odoo-bin -c odoo.conf
```
Assure-toi que le fichier `odoo.conf` contient le chemin vers `addons/` :
```ini
addons_path = addons,custom_addons   # adapter selon ta configuration
```

### 4. Activer le mode développeur
Dans Odoo → **Paramètres** → bas de page → **Activer le mode développeur**

### 5. Installer le module
**Paramètres** → **Applications** → chercher **IT Parc** → cliquer **Installer**

Pour charger les données de démo (équipements, interventions, contrats pré-remplis),
coche **"Charger les données de démonstration"** avant l'installation, ou lance :
```bash
python odoo-bin -c odoo.conf -i it_parc --load-language=fr_FR
```

### 6. Mise à jour (après modification du module)
```bash
python odoo-bin -c odoo.conf -u it_parc
```

---

## Groupes de sécurité
| Groupe | Droits |
|---|---|
| **IT Technicien** | Consultation équipements, création et suivi d'interventions |
| **IT Manager** | Accès complet : équipements, contrats, alertes, exports, dashboard |

---

## Fonctionnalités

### Équipements
- Workflow 4 étapes : Brouillon → Affecté → En maintenance → Retiré
- Suivi des garanties avec alertes automatiques (cron quotidien)
- Historique complet des affectations

### Interventions
- Suivi des maintenances (correctives et préventives)
- Vue calendrier des interventions
- Calcul automatique de la durée et des coûts

### Contrats fournisseurs
- Gestion des contrats avec dates d'expiration
- Alertes de renouvellement automatiques

### Wizards
- Réaffectation d'équipement
- Renouvellement de contrat
- Import CSV en masse
- Scan manuel des alertes

### Rapports PDF (QWeb)
| Rapport | Modèle | Description |
|---|---|---|
| **Fiche Équipement** | `it.equipement` | Fiche complète par équipement (identification, finances, garantie, historique interventions) |
| **Inventaire** | `it.equipement` | Tableau récapitulatif avec indicateurs de garantie |
| **Historique Maintenances** | `it.intervention` | Liste des interventions avec totaux |

> **Accès :** Ouvrir la liste ou la fiche d'un équipement/intervention → bouton **Imprimer**

### Exports Excel (xlsxwriter)
| Export | Description |
|---|---|
| **Inventaire complet** | Tous les équipements avec mise en forme conditionnelle garantie |
| **Coûts de maintenance** | Synthèse par équipement (interventions terminées uniquement) |
| **Contrats à renouveler** | Contrats expirant dans les 60 jours |

> **Accès :** Menu **IT Parc** → section **Exports Excel**

### Dashboard OWL
- 7 KPIs : total équipements, affectés, en maintenance, retirés, garanties expirées, interventions ouvertes, coût total maintenance
- 2 graphiques : répartition par état, répartition par catégorie
- Accès via **IT Parc → Dashboard**

---

## Données de démo
Le fichier `data/it_parc_demo.xml` contient :
- Des équipements variés (postes de travail, serveurs, imprimantes, équipements réseau)
- Des interventions de maintenance associées
- Des contrats fournisseurs
- Des alertes d'exemple

Ces données permettent une démonstration complète sans saisie manuelle.

---

## Notes techniques

### Champs Selection dans les rapports PDF
Les valeurs des champs de type Selection (Catégorie, Site, Type d'intervention, État)
sont converties en libellés lisibles via des dictionnaires dans les templates QWeb,
conformément au comportement de Odoo 18.

### Compatibilité Bootstrap 5
Les templates QWeb utilisent les classes Bootstrap 5 d'Odoo 18
(`text-end`, `rounded-pill`, `text-bg-info`, etc.).

### Compatibilité PDF
Les templates sont compatibles avec wkhtmltopdf et Chromium (moteur PDF d'Odoo 17/18).
Les emojis ont été remplacés par des alternatives textuelles pour assurer la compatibilité
avec toutes les configurations de rendu PDF.

### Dépendances Odoo
```python
'depends': ['base', 'hr', 'mail', 'web']
```
Aucun module tiers Odoo n'est requis (pas de `account`, `sale`, etc.).


## Auteur
**Moussa Ben Youssouf TRAORE**
- *Projet réalisé dans le cadre du projet de fin de Module de création de module ODOO Institut Ivoirien de Technologie (IIT) — Abidjan, juin 2026*


## Instructeur
**M Sedrick KOUAGNI**
