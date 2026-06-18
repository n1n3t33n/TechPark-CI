# -*- coding: utf-8 -*-
from odoo import fields, models


class ItSite(models.Model):
    _name = 'it.site'
    _description = 'Site client'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'partner_id, name'

    name = fields.Char(string='Nom du site', required=True, tracking=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        required=True,
        tracking=True,
        domain=[('is_company', '=', True)],
    )
    contact_id = fields.Many2one(
        'res.partner',
        string='Contact du site',
        domain="[('parent_id', '=', partner_id)]",
    )
    street = fields.Char(string='Adresse')
    city = fields.Char(string='Ville')
    phone = fields.Char(string='Téléphone')
    active = fields.Boolean(default=True)
    notes = fields.Text(string='Notes')

    equipement_ids = fields.One2many('it.equipement', 'site_id', string='Équipements')
    ticket_ids = fields.One2many('it.ticket', 'site_id', string='Tickets')

