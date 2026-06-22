# IT Parc — Module Odoo 18

Gestion complète d'un parc informatique **et** de prestations de services IT pour les clients (B2B).

Le module couvre deux usages :
1. **Parc interne** — équipements, affectations aux employés, interventions, contrats, alertes.
2. **Prestataire IT (B2B)** — rattachement des équipements à des clients et à des sites, tickets de support, licences logicielles, et un **portail client** en libre-service.

---

## Prérequis
- Odoo 18
- Python 3.11+ (le projet fournit un venv dans `odoo-18.0/venv/`)
- PostgreSQL 16
- wkhtmltopdf installé et configuré (ou Chromium pour la génération PDF)
- `xlsxwriter` : `pip install xlsxwriter`

---

## Installation pas à pas

### 1. Copier le module
Place le dossier `it_parc/` dans le dossier `addons/` d'Odoo :
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
Le `odoo.conf` doit pointer vers le dossier `addons/` :
```ini
addons_path = C:\Users\LENOVO\Downloads\odoo-18.0\odoo-18.0\addons
```

### 4. Activer le mode développeur
Odoo → **Paramètres** → bas de page → **Activer le mode développeur**.

### 5. Installer le module
**Paramètres** → **Applications** → chercher **IT Parc** → **Installer**.

> ⚠️ Le module dépend désormais de `sale`, `stock`, `account` et `portal` :
> ces applications seront installées automatiquement avec IT Parc.

Pour charger les données de démo, coche **« Charger les données de démonstration »**
avant l'installation, ou installe en ligne de commande :
```bash
python odoo-bin -c odoo.conf -i it_parc --load-language=fr_FR
```

### 6. Mise à jour (après modification du module)
```bash
python odoo-bin -c odoo.conf -d <base> -u it_parc
```
Vérification sans interface (utile en CI / debug) :
```bash
python odoo-bin -c odoo.conf -d <base> -u it_parc --stop-after-init --log-level=warn
```

---

## Démarrage rapide pour tester

### Démarrer le serveur (Windows / venv du projet)
```powershell
cd C:\Users\LENOVO\Downloads\odoo-18.0\odoo-18.0
.\venv\Scripts\python.exe odoo-bin -c odoo.conf -d odoo
```
Ouvrir **http://localhost:8069**.

### Se connecter en EMPLOYÉ (back-office)
1. Aller sur **http://localhost:8069/odoo**.
2. Login : `admin` — Mot de passe : `admin` (mot de passe par défaut de la base ; adapter si modifié).
3. Donner les droits IT : *Paramètres → Utilisateurs → (l'utilisateur) → onglet Autorisations → IT Parc → **IT Manager***.

### Se connecter en CLIENT (portail)
1. Créer un utilisateur **type Portail** dont le *contact associé* est rattaché à une **société cliente** (ex. `Baobab Industries SA`).
2. Lui définir un mot de passe (bouton *Changer le mot de passe* en mode dev, ou *Renvoyer l'invitation*).
3. S'y connecter via **http://localhost:8069/web/login**.
4. Astuce dev : sur la fiche utilisateur, le bouton **« Se connecter en tant que »** ouvre directement sa session.

> 🔑 Le portail filtre les données par **`commercial_partner_id`** (la société du client).
> Pour qu'un client voie des données, les équipements / tickets / contrats correspondants
> doivent avoir leur champ **Client** renseigné avec sa société.

> 🏠 **Accueil client redirigé** : un utilisateur portail qui ouvre `/my` ou `/my/home`
> est automatiquement redirigé vers **`/my/it-parc`** (son parc IT devient sa page d'accueil).
> Les utilisateurs internes conservent l'accueil natif Odoo.
> Un raccourci **« Mon parc IT »** et **« Mon compte »** est ajouté dans le menu déroulant
> utilisateur (en haut à droite).

---

## Groupes de sécurité
| Groupe | Droits |
|---|---|
| **IT Technicien** | Consulte équipements/sites/licences ; crée et gère interventions et tickets |
| **IT Manager** | Accès complet (hérite de Technicien) : équipements, sites, tickets, licences, contrats, alertes, exports, dashboard |
| **Utilisateur portail** | Accès en lecture à *ses* données via `/my/it-parc` + création de tickets (via le contrôleur, en `sudo` filtré par société) |

---

## Modèles de données

| Modèle | Rôle |
|---|---|
| `it.equipement` | Équipement informatique (catégories détaillées, caractéristiques techniques, workflow 5 états dont location, garantie, client, site, liens vente/stock) |
| `it.affectation` | Historique des affectations d'un équipement à un employé (+ localisation précise) |
| `it.intervention` | Intervention / maintenance (corrective ou préventive) |
| `it.contrat` | Contrat fournisseur (ou client) avec suivi d'expiration |
| `it.alerte` | Alertes générées (garanties, contrats) |
| `it.site` | **Site d'un client** (adresse, contact, équipements, tickets) |
| `it.ticket` | **Ticket de support client** (priorité, workflow, SLA, séquence `TCK/…`) |
| `it.license` | **Licence logicielle** (type, postes, expiration, état calculé) |

---

## Fonctionnalités

### Équipements
- Workflow **5 états** : Brouillon → Affecté → **En location** → En maintenance → Retiré
- **Catégories détaillées** : ordinateur portable, ordinateur fixe, serveur, imprimante/scanner,
  switch, routeur/firewall, point d'accès Wi-Fi, téléphone IP, écran, périphérique, autre
- **Caractéristiques techniques** dédiées et **affichées selon la catégorie** :
  - *Informatique* : processeur (CPU), RAM (Go), stockage (Go), type (SSD/HDD/NVMe), système d'exploitation
  - *Réseau* : adresse IP, adresse MAC, nombre de ports
  - *Écran* : taille en pouces
  - champ libre *Spécifications complémentaires*
- **Location** (état « En location ») : locataire, date de début/fin, loyer mensuel,
  alerte « fin de location proche » (≤ 30 j), boutons *Mettre en location* / *Fin de location*
- Suivi des garanties avec alertes automatiques (cron quotidien)
- Historique des affectations (avec **localisation précise** : bureau, salle…)
- **Rattachement à un Client et un Site client**
- **Liens vers la Commande de vente et le Bon de livraison** (intégration `sale` / `stock`)
- **Onglets Tickets et Licences** sur la fiche
- Vue kanban (regroupée par état), liste (colonnes specs optionnelles), formulaire, recherche

> Le champ « Site » texte (3 villes en dur) a été **retiré** ; la localisation se gère
> désormais par le **Site client** (`it.site`) et la **localisation précise** dans l'historique
> d'affectation.

### Sites client *(nouveau)*
- Un site appartient à un client (société) et regroupe ses équipements et tickets
- Adresse, ville, contact dédié, notes

### Tickets de support *(nouveau)*
- Référence automatique `TCK/<année>/####`
- Priorités : Basse / Normale / Haute / Critique
- Workflow : Nouveau → Assigné → En cours → Résolu (+ Annulé) via boutons
- Champ **Échéance SLA**, technicien assigné, équipement et site liés
- Création possible **depuis le portail client**

### Licences logicielles *(nouveau)*
- Types : Abonnement / Perpétuelle / Essai / Autre
- Nombre de postes, clé, dates de début et d'expiration
- **État calculé automatiquement** : Active / Expire bientôt (≤ 30 jours) / Expirée
- Décorations de couleur et filtres dédiés dans la liste

### Interventions
- Suivi des maintenances (correctives et préventives)
- Vue calendrier des interventions
- Calcul automatique de la durée et des coûts
- **Client et Site** déduits de l'équipement (champs liés), **ticket et facture liés**

### Contrats fournisseurs / clients
- Gestion des contrats avec dates d'expiration
- Alertes de renouvellement automatiques
- **Client, Site et Facture liés** (intégration `account`)

### Portail client *(front-end personnalisé)*
Espace client redesigné (CSS dédié `static/src/portal/portal.css`, hors thème natif Odoo) :
héro coloré, navigation par onglets, **cartes KPI cliquables**, tableaux stylisés et
**badges d'état/priorité**. Accessible aux utilisateurs portail :

| Page | URL | Cliquable |
|---|---|---|
| Résumé (cartes Machines / Tickets ouverts / Contrats / Licences) | `/my/it-parc` | cartes → listes |
| Mes machines | `/my/it-parc/equipements` | ligne → détail machine |
| Détail d'une machine | `/my/it-parc/equipement/<id>` | — |
| Mes tickets | `/my/it-parc/tickets` | ligne → détail ticket |
| Détail d'un ticket | `/my/it-parc/ticket/<id>` | — |
| Créer un ticket | `/my/it-parc/tickets/new` | — |
| Mes contrats | `/my/it-parc/contrats` | — |
| Mes interventions | `/my/it-parc/interventions` | — |
| Mes licences | `/my/it-parc/licenses` | — |

- Les données sont filtrées par société (`child_of`) et exposées en lecture (`sudo`) ;
  les pages de détail re-vérifient l'appartenance au client (sécurité).
- La création de ticket valide les champs obligatoires et l'appartenance du site/machine.
- `/my` et `/my/home` redirigent le client vers `/my/it-parc` ; un raccourci
  **« Mon parc IT »** + **« Mon compte »** est ajouté au menu utilisateur du portail.

### Wizards
- Réaffectation d'équipement
- Renouvellement de contrat
- **Import CSV en masse** : colonnes obligatoires `name`, `categorie` ; optionnelles
  `marque, modele, numero_serie, cpu, ram_go, stockage_go, valeur_achat, date_fin_garantie`.
  Possibilité de **rattacher tous les équipements importés à un Client + Site**.
- Scan manuel des alertes

### Rapports PDF (QWeb)
| Rapport | Modèle | Description |
|---|---|---|
| **Fiche Équipement** | `it.equipement` | Fiche complète par équipement (identification, finances, garantie, historique interventions) |
| **Inventaire** | `it.equipement` | Tableau récapitulatif avec indicateurs de garantie |
| **Historique Maintenances** | `it.intervention` | Liste des interventions avec totaux |

> **Accès :** ouvrir la liste/fiche d'un équipement ou d'une intervention → bouton **Imprimer**.

### Exports Excel (xlsxwriter)
| Export | Description |
|---|---|
| **Inventaire complet** | Tous les équipements avec mise en forme conditionnelle garantie |
| **Coûts de maintenance** | Synthèse par équipement (interventions terminées uniquement) |
| **Contrats à renouveler** | Contrats expirant dans les 60 jours |

> **Accès :** menu **IT Parc** → section **Exports Excel**.

### Dashboard OWL
- 8 KPIs **cliquables** (ouvrent la liste filtrée correspondante) : total équipements,
  affectés, **en location**, en maintenance, garanties expirées, alertes nouvelles,
  contrats urgents, interventions ce mois ; + coût total maintenance
- 2 graphiques : répartition par catégorie (donut), interventions sur 6 mois (barres)
- Top 5 équipements les plus maintenus — **lignes cliquables** vers la fiche
- Accès via **IT Parc → Dashboard**

---

## Plan de test (résumé)

**Back-office (employé)**
1. Donner le groupe *IT Manager* à l'utilisateur.
2. Créer un **Site client** rattaché à une société.
3. Sur un **Équipement** : choisir une catégorie « Ordinateur portable » ⇒ les champs
   *CPU / RAM / Stockage / OS* apparaissent ; choisir « Switch réseau » ⇒ *IP / MAC / ports*.
4. Renseigner *Client* + *Site* (vérifier le filtrage des sites par client).
5. **Location** : bouton *Mettre en location* (locataire requis) ⇒ état *En location* + bloc location.
6. Créer une **Licence** : expiration dans 15 j ⇒ *Expire bientôt* ; date passée ⇒ *Expirée*.
7. Créer un **Ticket**, vérifier la réf `TCK/…`, dérouler *Assigner → Démarrer → Résoudre*.
8. **Dashboard** : cliquer une carte KPI (ex. « En location ») ⇒ ouvre la liste filtrée.

**Portail (client)**
9. Créer/utiliser un utilisateur portail rattaché à la même société.
10. Se connecter ⇒ on arrive directement sur `/my/it-parc` (redirection depuis `/my`).
11. Cliquer une **carte KPI**, puis une **ligne machine/ticket** ⇒ page de détail.
12. Créer un ticket depuis `/my/it-parc/tickets/new` ⇒ vérifier sa présence côté back-office.
13. Vérifier l'isolation : un client d'une autre société ne voit pas les données.

**Technique**
14. `... -u it_parc --stop-after-init --log-level=warn` ⇒ aucun warning `it_parc` *(vérifié)*.

---

## Données de démo
Le fichier `data/it_parc_demo.xml` fournit un jeu complet et cohérent pour tester sans saisie :
- **2 clients** (`Baobab Industries SA`, `Lagune Distribution`) avec contacts
- **3 sites client**
- **10 équipements** variés et renseignés (CPU/RAM/stockage, IP/ports, écran…),
  dont **1 en location** et **1 retiré**
- **3 contrats**, **3 interventions**, **4 tickets** (états variés), **3 licences**
  (active / expire bientôt / expirée)

> ⚠️ **Important** : les données de démo ne se chargent **qu'à la première installation**
> d'une base avec la démo activée. Sur une base existante où le module est déjà installé
> **sans** démo (cas de la base `odoo`), elles n'apparaîtront pas — utilise une base neuve :
> ```powershell
> .\venv\Scripts\python.exe odoo-bin -c odoo.conf -d itparc_demo -i it_parc
> ```
> (Odoo crée la base et charge la démo automatiquement.)

---

## Notes techniques

### Dépendances Odoo
```python
'depends': ['base', 'hr', 'mail', 'web', 'portal', 'sale', 'stock', 'account']
```
`portal` fournit la couche d'espace client ; `sale` / `stock` / `account` permettent de
relier équipements, contrats et interventions aux commandes, livraisons et factures.

### Compatibilité Odoo 18
- Vues kanban en syntaxe Odoo 18 (`<t t-name="card">`).
- Chatter via la balise `<chatter/>`.
- Encarts d'information accessibles (`role="status"` sur les blocs `alert`).
- Portail basé sur `portal.portal_layout` + CSS personnalisé ; héritages via xpath robustes
  (`//div[@role='menu']`) et mécanisme de compteurs `placeholder_count`.
- `external_dependencies` déclare `xlsxwriter` (le module ne casse plus si la lib manque).

### Champs Selection dans les rapports / exports
Les valeurs Selection (Catégorie, État…) sont converties en libellés lisibles via
`record._fields['champ'].selection` — les libellés restent corrects même si on ajoute
de nouvelles catégories/états (plus de dictionnaires figés à maintenir).

### Champs calculés stockés
`jours_garantie_restants`, `garantie_expiree`, `jours_avant_fin_location` et
`location_bientot_finie` sont **stockés** (`store=True`) afin d'être filtrables/searchables.
Ils dépendent de dates ; le **cron quotidien** rafraîchit les valeurs dérivées du jour courant.

### Compatibilité PDF
Templates compatibles wkhtmltopdf et Chromium (moteur PDF d'Odoo 17/18).

---

## Auteur
**Moussa Ben Youssouf TRAORE**
- *Projet réalisé dans le cadre du projet de fin de Module de création de module ODOO Institut Ivoirien de Technologie (IIT) — Abidjan, juin 2026*

## Instructeur
**M Sedrick KOUAGNI**
