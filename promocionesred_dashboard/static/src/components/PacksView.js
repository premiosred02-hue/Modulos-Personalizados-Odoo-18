/** @odoo-module **/
// ── PREMIOSRED — PacksView (Catálogo de packs) ────────────────────────────
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

const STATUS_CFG = {
    active:   { color: "#059669", bg: "rgba(5,150,105,0.1)",   label: "Activo",          icon: "✅" },
    inactive: { color: "#6b7280", bg: "rgba(107,114,128,0.1)", label: "Inactivo",         icon: "⏸️" },
    future:   { color: "#4f46e5", bg: "rgba(79,70,229,0.1)",   label: "Campaña futura",   icon: "🔜" },
};

export class PrPacksView extends Component {
    static template = "promocionesred_dashboard.PacksView";

    setup() {
        this.orm   = useService("orm");
        this.state = useState({
            packs: [],
            loading: true,
        });
        onWillStart(() => this.loadData());
    }

    async loadData() {
        try {
            const data = await this.orm.call("pr.pack", "get_packs_data", []);
            this.state.packs = data;
        } catch (e) {
            console.error("[PacksView] Error:", e);
            this.state.packs = [];
        } finally {
            this.state.loading = false;
        }
    }

    get activePacks() {
        return this.state.packs.filter(p => p.pack_status === "active");
    }

    get totalRevenue() {
        return this.state.packs.reduce((s, p) => s + (p.total_revenue || 0), 0);
    }

    get totalDonations() {
        return this.state.packs.reduce((s, p) => s + (p.total_donations || 0), 0);
    }

    get totalSold() {
        return this.state.packs.reduce((s, p) => s + (p.total_sold || 0), 0);
    }

    statusCfg(s) { return STATUS_CFG[s] || STATUS_CFG.inactive; }

    fmt(n) {
        return (n || 0).toLocaleString("es-ES", { style: "currency", currency: "EUR", minimumFractionDigits: 2 });
    }
}
