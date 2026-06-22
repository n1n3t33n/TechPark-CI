# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date


class ItEquipement(models.Model):
    _name = 'it.equipement'
    _description = 'Équipement informatique'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'it.export.excel']
    _order = 'name asc'

    # ─── Informations générales ───────────────────────────────────────────────
    name = fields.Char(
        string='Nom de l\'équipement',
        required=True,
        tracking=True
    )
    reference = fields.Char(
        string='Référence interne',
        readonly=True,
        copy=False,
        default='Nouveau'
    )
    categorie = fields.Selection([
        ('pc_portable',   'Ordinateur portable'),
        ('pc_fixe',       'Ordinateur fixe'),
        ('serveur',       'Serveur'),
        ('imprimante',    'Imprimante / Scanner'),
        ('switch',        'Switch réseau'),
        ('routeur',       'Routeur / Firewall'),
        ('point_acces',   'Point d\'accès Wi-Fi'),
        ('telephone',     'Téléphone IP'),
        ('ecran',         'Écran / Moniteur'),
        ('peripherique',  'Périphérique (clavier, souris...)'),
        ('autre',         'Autre'),
    ], string='Catégorie', required=True, tracking=True)

    # Famille technique déduite de la catégorie (pilote l'affichage des specs)
    famille = fields.Selection([
        ('informatique', 'Informatique'),
        ('reseau',       'Réseau'),
        ('peripherique', 'Périphérique'),
        ('autre',        'Autre'),
    ], string='Famille', compute='_compute_famille', store=True)

    marque    = fields.Char(string='Marque')
    modele    = fields.Char(string='Modèle')
    numero_serie = fields.Char(
        string='Numéro de série',
        copy=False
    )
    description = fields.Text(string='Notes / Description')

    # ─── Caractéristiques techniques ──────────────────────────────────────────
    cpu = fields.Char(string='Processeur (CPU)')
    ram_go = fields.Integer(string='Mémoire RAM (Go)')
    stockage_go = fields.Integer(string='Stockage (Go)')
    type_stockage = fields.Selection([
        ('ssd',    'SSD'),
        ('hdd',    'HDD'),
        ('nvme',   'NVMe'),
        ('hybride','Hybride'),
    ], string='Type de stockage')
    systeme_exploitation = fields.Char(string='Système d\'exploitation')
    taille_ecran = fields.Float(string='Taille écran (pouces)')
    adresse_ip = fields.Char(string='Adresse IP')
    adresse_mac = fields.Char(string='Adresse MAC')
    nb_ports = fields.Integer(string='Nombre de ports')
    specifications = fields.Text(string='Spécifications complémentaires')

    # ─── Rattachement client / site ───────────────────────────────────────────
    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        tracking=True,
        help='Client propriétaire ou bénéficiaire de cet équipement.'
    )
    site_id = fields.Many2one(
        'it.site',
        string='Site client',
        domain="[('partner_id', 'child_of', partner_id)]",
        tracking=True
    )

    # ─── Affectation interne ──────────────────────────────────────────────────
    employe_id = fields.Many2one(
        'hr.employee',
        string='Employé affecté',
        tracking=True
    )
    departement_id = fields.Many2one(
        'hr.department',
        string='Département',
        tracking=True
    )

    # ─── Informations financières ──────────────────────────────────────────────
    date_achat       = fields.Date(string='Date d\'achat')
    valeur_achat     = fields.Float(string='Valeur d\'achat (FCFA)')
    fournisseur_id   = fields.Many2one('res.partner', string='Fournisseur')
    sale_order_id    = fields.Many2one('sale.order', string='Commande de vente')
    stock_picking_id = fields.Many2one('stock.picking', string='Bon de livraison')

    # ─── Location ─────────────────────────────────────────────────────────────
    locataire_id     = fields.Many2one('res.partner', string='Locataire', tracking=True)
    date_debut_location = fields.Date(string='Début de location')
    date_fin_location   = fields.Date(string='Fin de location', tracking=True)
    loyer_mensuel    = fields.Float(string='Loyer mensuel (FCFA)')
    jours_avant_fin_location = fields.Integer(
        string='Jours avant fin de location',
        compute='_compute_jours_location',
        store=True
    )
    location_bientot_finie = fields.Boolean(
        string='Fin de location proche',
        compute='_compute_jours_location',
        store=True
    )

    # ─── Garantie ─────────────────────────────────────────────────────────────
    date_fin_garantie   = fields.Date(string='Date de fin de garantie', tracking=True)
    jours_garantie_restants = fields.Integer(
        string='Jours de garantie restants',
        compute='_compute_jours_garantie',
        store=True
    )
    garantie_expiree = fields.Boolean(
        string='Garantie expirée',
        compute='_compute_jours_garantie',
        store=True
    )

    # ─── Workflow / État ──────────────────────────────────────────────────────
    state = fields.Selection([
        ('brouillon',     'Brouillon'),
        ('affecte',       'Affecté'),
        ('location',      'En location'),
        ('maintenance',   'En maintenance'),
        ('retire',        'Retiré'),
    ], string='État', default='brouillon', tracking=True, required=True)

    # ─── Relations ────────────────────────────────────────────────────────────
    affectation_ids  = fields.One2many('it.affectation',  'equipement_id', string='Historique des affectations')
    intervention_ids = fields.One2many('it.intervention', 'equipement_id', string='Interventions')
    contrat_ids      = fields.One2many('it.contrat',      'equipement_id', string='Contrats')
    ticket_ids       = fields.One2many('it.ticket',       'equipement_id', string='Tickets')
    license_ids      = fields.One2many('it.license',      'equipement_id', string='Licences')

    nb_interventions = fields.Integer(
        string='Nombre d\'interventions',
        compute='_compute_nb_interventions',
        store=True
    )
    cout_total_maintenance = fields.Float(
        string='Coût total maintenance (FCFA)',
        compute='_compute_cout_total',
        store=True
    )

    # ─── Méthodes computed ────────────────────────────────────────────────────
    @api.depends('categorie')
    def _compute_famille(self):
        mapping = {
            'pc_portable': 'informatique',
            'pc_fixe':     'informatique',
            'serveur':     'informatique',
            'imprimante':  'peripherique',
            'switch':      'reseau',
            'routeur':     'reseau',
            'point_acces': 'reseau',
            'telephone':   'reseau',
            'ecran':       'peripherique',
            'peripherique':'peripherique',
        }
        for rec in self:
            rec.famille = mapping.get(rec.categorie, 'autre')

    @api.depends('date_fin_garantie')
    def _compute_jours_garantie(self):
        today = date.today()
        for rec in self:
            if rec.date_fin_garantie:
                delta = (rec.date_fin_garantie - today).days
                rec.jours_garantie_restants = delta
                rec.garantie_expiree = delta < 0
            else:
                rec.jours_garantie_restants = 0
                rec.garantie_expiree = False

    @api.depends('date_fin_location')
    def _compute_jours_location(self):
        today = date.today()
        for rec in self:
            if rec.date_fin_location:
                delta = (rec.date_fin_location - today).days
                rec.jours_avant_fin_location = delta
                rec.location_bientot_finie = 0 <= delta <= 30
            else:
                rec.jours_avant_fin_location = 0
                rec.location_bientot_finie = False

    @api.depends('intervention_ids')
    def _compute_nb_interventions(self):
        for rec in self:
            rec.nb_interventions = len(rec.intervention_ids)

    @api.depends('intervention_ids.cout')
    def _compute_cout_total(self):
        for rec in self:
            rec.cout_total_maintenance = sum(rec.intervention_ids.mapped('cout'))

    # ─── Séquence automatique ─────────────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', 'Nouveau') == 'Nouveau':
                vals['reference'] = self.env['ir.sequence'].next_by_code('it.equipement') or 'Nouveau'
        return super().create(vals_list)

    # ─── Transitions du workflow ──────────────────────────────────────────────
    def action_affecter(self):
        for rec in self:
            if not rec.employe_id:
                raise UserError(_("Veuillez affecter un employé avant de valider."))
            rec.state = 'affecte'

    def action_mettre_en_location(self):
        for rec in self:
            if not rec.locataire_id:
                raise UserError(_("Veuillez indiquer le locataire avant de mettre en location."))
            if not rec.date_debut_location:
                rec.date_debut_location = fields.Date.today()
            rec.state = 'location'

    def action_terminer_location(self):
        for rec in self:
            if not rec.date_fin_location:
                rec.date_fin_location = fields.Date.today()
            rec.state = 'brouillon'

    def action_mettre_en_maintenance(self):
        for rec in self:
            rec.state = 'maintenance'

    def action_retirer(self):
        for rec in self:
            rec.state = 'retire'

    def action_remettre_en_brouillon(self):
        for rec in self:
            rec.state = 'brouillon'
