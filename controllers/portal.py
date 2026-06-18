# -*- coding: utf-8 -*-
from odoo import _, http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class ItParcPortal(CustomerPortal):

    def _portal_partner(self):
        return request.env.user.partner_id.commercial_partner_id

    def _portal_domain(self, field='partner_id'):
        return [(field, 'child_of', self._portal_partner().id)]

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = self._portal_partner()
        if 'it_ticket_count' in counters:
            values['it_ticket_count'] = request.env['it.ticket'].sudo().search_count([
                ('partner_id', 'child_of', partner.id),
                ('state', 'in', ['new', 'assigned', 'in_progress']),
            ])
        if 'it_equipment_count' in counters:
            values['it_equipment_count'] = request.env['it.equipement'].sudo().search_count([
                ('partner_id', 'child_of', partner.id),
            ])
        return values

    def _prepare_it_portal_values(self):
        partner = self._portal_partner()
        env = request.env
        values = self._prepare_portal_layout_values()
        values.update({
            'page_name': 'it_parc',
            'partner': partner,
            'sites': env['it.site'].sudo().search([('partner_id', 'child_of', partner.id)]),
            'equipements': env['it.equipement'].sudo().search([('partner_id', 'child_of', partner.id)]),
            'tickets': env['it.ticket'].sudo().search([('partner_id', 'child_of', partner.id)], limit=20),
            'contrats': env['it.contrat'].sudo().search([('partner_id', 'child_of', partner.id)], limit=20),
            'interventions': env['it.intervention'].sudo().search([('partner_id', 'child_of', partner.id)], limit=20),
            'licenses': env['it.license'].sudo().search([('partner_id', 'child_of', partner.id)], limit=20),
        })
        return values

    @http.route(['/my/it-parc'], type='http', auth='user', website=True)
    def portal_it_parc_home(self, **kw):
        return request.render('it_parc.portal_it_parc_home', self._prepare_it_portal_values())

    @http.route(['/my/it-parc/equipements'], type='http', auth='user', website=True)
    def portal_it_parc_equipements(self, **kw):
        values = self._prepare_it_portal_values()
        values['page_name'] = 'it_parc_equipements'
        return request.render('it_parc.portal_it_parc_equipements', values)

    @http.route(['/my/it-parc/contrats'], type='http', auth='user', website=True)
    def portal_it_parc_contrats(self, **kw):
        values = self._prepare_it_portal_values()
        values['page_name'] = 'it_parc_contrats'
        return request.render('it_parc.portal_it_parc_contrats', values)

    @http.route(['/my/it-parc/interventions'], type='http', auth='user', website=True)
    def portal_it_parc_interventions(self, **kw):
        values = self._prepare_it_portal_values()
        values['page_name'] = 'it_parc_interventions'
        return request.render('it_parc.portal_it_parc_interventions', values)

    @http.route(['/my/it-parc/licenses'], type='http', auth='user', website=True)
    def portal_it_parc_licenses(self, **kw):
        values = self._prepare_it_portal_values()
        values['page_name'] = 'it_parc_licenses'
        return request.render('it_parc.portal_it_parc_licenses', values)

    @http.route(['/my/it-parc/tickets'], type='http', auth='user', website=True)
    def portal_it_parc_tickets(self, **kw):
        values = self._prepare_it_portal_values()
        values['page_name'] = 'it_parc_tickets'
        return request.render('it_parc.portal_it_parc_tickets', values)

    @http.route(['/my/it-parc/tickets/new'], type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_it_parc_ticket_new(self, **post):
        values = self._prepare_it_portal_values()
        values['page_name'] = 'it_parc_ticket_new'
        if request.httprequest.method == 'POST':
            subject = (post.get('subject') or '').strip()
            description = (post.get('description') or '').strip()
            if not subject or not description:
                values['error'] = _('Le sujet et la description sont obligatoires.')
                return request.render('it_parc.portal_it_parc_ticket_new', values)

            partner = self._portal_partner()
            vals = {
                'subject': subject,
                'description': description,
                'partner_id': partner.id,
                'priority': post.get('priority') or '1',
            }
            site_id = int(post.get('site_id') or 0)
            equipment_id = int(post.get('equipement_id') or 0)
            if site_id and request.env['it.site'].sudo().search_count([
                ('id', '=', site_id),
                ('partner_id', 'child_of', partner.id),
            ]):
                vals['site_id'] = site_id
            if equipment_id and request.env['it.equipement'].sudo().search_count([
                ('id', '=', equipment_id),
                ('partner_id', 'child_of', partner.id),
            ]):
                vals['equipement_id'] = equipment_id
            ticket = request.env['it.ticket'].sudo().create(vals)
            ticket.message_post(body=_('Ticket créé depuis le portail client.'))
            return request.redirect('/my/it-parc/tickets')
        return request.render('it_parc.portal_it_parc_ticket_new', values)

