/** @odoo-module **/
// ── PREMIOSRED — PromotoresView (CCP/COM/ASE) ─────────────────────────────
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

const ROLE_CFG = {
    CCP: { icon: "🎯", color: "#4f46e5", bg: "rgba(79,70,229,0.1)",  label: "Captador CCP",  pct: 3 },
    COM: { icon: "💼", color: "#7c3aed", bg: "rgba(124,58,237,0.1)", label: "Comercial COM", pct: 2 },
    ASE: { icon: "🤝", color: "#0891b2", bg: "rgba(8,145,178,0.1)",  label: "Asesor ASE",    pct: 2 },
};

export class PrPromotoresView extends Component {
    static template = "promocionesred_dashboard.PromotoresView";

    setup() {
        this.orm   = useService("orm");
        this.state = useState({
            promotores: [],
            loading: true,
            search: "",
            fRole: "all",
            fActive: "all",
            selected: null,
        });
        onWillStart(() => this.loadData());
    }

    async loadData() {
        try {
            const data = await this.orm.call("pr.actor", "get_promotores_data", []);
            this.state.promotores = data;
        } catch (e) {
            console.error("[PromotoresView] Error:", e);
            this.state.promotores = [];
        } finally {
            this.state.loading = false;
        }
    }

    get filtered() {
        return this.state.promotores.filter(p => {
            if (this.state.fRole   !== "all" && p.role !== this.state.fRole)         return false;
            if (this.state.fActive === "active"   && !p.active)                      return false;
            if (this.state.fActive === "inactive" && p.active)                       return false;
            if (this.state.search) {
                const q = this.state.search.toLowerCase();
                return (p.name || "").toLowerCase().includes(q) ||
                       (p.email || "").toLowerCase().includes(q) ||
                       (p.city || "").toLowerCase().includes(q) ||
                       (p.dni || "").toLowerCase().includes(q);
            }
            return true;
        });
    }

    get kpis() {
        const p = this.state.promotores;
        return {
            total:         p.length,
            activos:       p.filter(x => x.active).length,
            totalCols:     p.reduce((s, x) => s + (x.cols_captados || 0), 0),
            totalEarned:   p.reduce((s, x) => s + (x.total_earned || 0), 0),
            totalPending:  p.reduce((s, x) => s + (x.pending_payout || 0), 0),
            sinIBAN:       p.filter(x => !x.iban_verified).length,
        };
    }

    roleCfg(role) { return ROLE_CFG[role] || ROLE_CFG.ASE; }

    fmt(n) {
        return (n || 0).toLocaleString("es-ES", { style: "currency", currency: "EUR" });
    }

    setSearch(ev)  { this.state.search  = ev.target.value; }
    setRole(ev)    { this.state.fRole   = ev.target.value; }
    setActive(ev)  { this.state.fActive = ev.target.value; }
    select(p)      { this.state.selected = p; }
    closeModal()   { this.state.selected = null; }
}
