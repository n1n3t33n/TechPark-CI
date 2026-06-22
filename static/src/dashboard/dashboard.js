/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

class ItParcDashboard extends Component {
    static template = "it_parc.Dashboard";

    setup() {
        this.action = useService("action");
        this.state = useState({
            loading: true,
            kpis: {},
            graphiques: {},
            top_equipements: [],
            alertes_recentes: [],
        });

        onWillStart(async () => {
            await this._chargerDonnees();
        });
    }

    /**
     * Ouvre une vue liste filtrée. Utilisé pour rendre les KPIs cliquables.
     * @param {string} model  modèle Odoo (ex: 'it.equipement')
     * @param {Array}  domain domaine de recherche Odoo
     * @param {string} name   titre de la fenêtre
     */
    ouvrirListe(model, domain, name) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: name,
            res_model: model,
            domain: domain || [],
            views: [[false, "list"], [false, "form"]],
            target: "current",
        });
    }

    ouvrirEquipements(domain, name) {
        this.ouvrirListe("it.equipement", domain, name || "Équipements");
    }

    async _chargerDonnees() {
        try {
            const data = await rpc("/it_parc/dashboard/data", {});
            this.state.kpis             = data.kpis;
            this.state.graphiques       = data.graphiques;
            this.state.top_equipements  = data.top_equipements;
            this.state.alertes_recentes = data.alertes_recentes;
        } catch (e) {
            console.error("Erreur chargement dashboard IT Parc :", e);
        } finally {
            this.state.loading = false;
        }
    }

    formatMontant(valeur) {
        if (!valeur) return "0 FCFA";
        return new Intl.NumberFormat('fr-FR').format(Math.round(valeur)) + " FCFA";
    }

    getUrgenceClass(jours) {
        if (jours < 0)  return "badge-danger";
        if (jours < 30) return "badge-warning";
        return "badge-success";
    }

    getLargeurBarre(valeur, maximum) {
        if (!maximum) return "0%";
        return Math.round((valeur / maximum) * 100) + "%";
    }

    getMaxCategorie() {
        const cats = this.state.graphiques.categories || [];
        return Math.max(...cats.map(c => c.value), 1);
    }

    getMaxInterventions() {
        const mois = this.state.graphiques.interventions_mois || [];
        return Math.max(...mois.map(m => m.value), 1);
    }

    getCouleurCategorie(index) {
        const couleurs = [
            '#1F4E79', '#2E75B6', '#5BA3D9',
            '#70AD47', '#FFC000', '#FF6B6B'
        ];
        return couleurs[index % couleurs.length];
    }

    getDonutSegments() {
        const categories = this.state.graphiques.categories || [];
        const total = categories.reduce((s, c) => s + c.value, 0);
        if (!total) return [];

        const segments = [];
        let angle = -90;
        const cx = 80, cy = 80, r = 60;

        categories.forEach((cat, i) => {
            const pct    = cat.value / total;
            const deg    = pct * 360;
            const rad1   = (angle * Math.PI) / 180;
            const rad2   = ((angle + deg) * Math.PI) / 180;
            const x1 = cx + r * Math.cos(rad1);
            const y1 = cy + r * Math.sin(rad1);
            const x2 = cx + r * Math.cos(rad2);
            const y2 = cy + r * Math.sin(rad2);
            const largeArc = deg > 180 ? 1 : 0;

            segments.push({
                path:    `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2} Z`,
                couleur: this.getCouleurCategorie(i),
                label:   cat.label,
                value:   cat.value,
                pct:     Math.round(pct * 100),
            });
            angle += deg;
        });
        return segments;
    }
}

registry.category("actions").add("it_parc.action_dashboard", ItParcDashboard);