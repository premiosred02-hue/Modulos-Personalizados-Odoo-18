/** @odoo-module **/
// PREMIOSRED -- Dashboard v4 -- Inspirado en React Panel Unificado
// Referencia: D:\Dev\PREMIOSRED-PANEL-UNIFICADO\src\modules\03-admin-empresas\views\DashboardView.tsx
import { Component, useState, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

// Datos mock realistas (sustituibles por ORM)
const MOCK_SALES = [
    { id: 1, local: "Bar El Rincon",       pack: "Tecnologia", pvp: 6,  zone: "MAD", date: "28 abr", ok: true },
    { id: 2, local: "Farmacia Centro",     pack: "Cosmetica",  pvp: 8,  zone: "SEV", date: "28 abr", ok: true },
    { id: 3, local: "Hotel City BCN",      pack: "Caribe",     pvp: 9,  zone: "BCN", date: "27 abr", ok: true },
    { id: 4, local: "Restaurante Luna",    pack: "Moda",       pvp: 7,  zone: "VAL", date: "27 abr", ok: true },
    { id: 5, local: "Cafeteria del Sol",   pack: "Tecnologia", pvp: 6,  zone: "BIL", date: "26 abr", ok: false },
];

const MOCK_ZONES = [
    { name: "Madrid",    n: 487, pct: 88 },
    { name: "Sevilla",   n: 312, pct: 63 },
    { name: "Barcelona", n: 278, pct: 56 },
    { name: "Valencia",  n: 201, pct: 41 },
    { name: "Bilbao",    n: 143, pct: 29 },
];

const MOCK_FEED = [
    { t: "12:41", label: "VENTA",  text: "Bar El Rincon -- Pack Tecnologia 6 EUR" },
    { t: "12:28", label: "ALTA",   text: "Juan Garcia (CCP) -- Estado: pendiente" },
    { t: "12:09", label: "ACTIV.", text: "Farmacia Centro -- COL activado" },
    { t: "11:54", label: "VENTA",  text: "Hotel City BCN -- Pack Caribe 9 EUR" },
    { t: "11:31", label: "ALTA",   text: "Maria Lopez (ASE) -- Acuerdo firmado" },
    { t: "10:58", label: "VENTA",  text: "Restaurante Luna -- Pack Moda 7 EUR" },
];

const ACTOR_TYPES = [
    { code: "COL", name: "Colaboradores",    n: 85, pct: 85, color: "#4f46e5" },
    { code: "SUB", name: "Subcolaboradores", n: 48, pct: 48, color: "#059669" },
    { code: "CCP", name: "Captadores",       n: 32, pct: 32, color: "#7c3aed" },
    { code: "COM", name: "Comerciales",      n: 18, pct: 18, color: "#0891b2" },
    { code: "ASE", name: "Asesores",         n: 12, pct: 12, color: "#d97706" },
];

const QUICK_ACTIONS = [
    { label: "Onboarding Actores", section: "onboarding",  primary: true  },
    { label: "Empresas",           section: "empresas",    primary: false },
    { label: "Cupones",            section: "cupones",     primary: false },
    { label: "Red",                section: "network",     primary: false },
    { label: "Finanzas",           section: "finance",     primary: false },
    { label: "Legal",              section: "legal",       primary: false },
];

export class PrDashboard extends Component {
    static template = "promocionesred_dashboard.PrDashboard";
    static props = {
        stats:    { type: Object,   optional: true },
        leads:    { type: Array,    optional: true },
        onDelete: { type: Function, optional: true },
        onUpdate: { type: Function, optional: true },
        navigate: { type: Function, optional: true },
    };

    setup() {
        this.orm          = useService("orm");
        this.notification = useService("notification");

        this.state = useState({
            actors:  [],
            loading: true,
            editingId:   null,
            editValues:  {},
        });

        // Calcular dias hasta kill switch
        this.daysLeft = Math.max(
            0,
            Math.ceil((new Date("2026-12-21T23:59:59").getTime() - Date.now()) / 86400000)
        );

        onMounted(() => this._loadActors());
    }

    async _loadActors() {
        try {
            const data = await this.orm.searchRead(
                "pr.actor",
                [],
                ["name", "actor_type", "status"],
                { limit: 200 }
            );
            this.state.actors  = data;
        } catch (_) {
            // fallback silencioso -- usamos mock
        } finally {
            this.state.loading = false;
        }
    }

    // ---- KPI helpers -------------------------------------------------------
    get leads()        { return this.props.leads || []; }
    get stats()        { return this.props.stats || {}; }

    get totalActors() {
        return this.state.actors.length || 195;
    }
    get activeActors() {
        return this.state.actors.filter(a => a.status === "activo").length || 165;
    }
    get colCount() {
        return this.state.actors.filter(a => a.actor_type === "COL").length || 85;
    }
    get revenue()      { return this.stats.revenue || "1.248"; }
    get scans()        { return this.stats.scans    || 1421; }
    get convRate()     { return this.stats.conv     || "4.2"; }

    // ---- Actor por tipo ----------------------------------------------------
    getActorCount(code) {
        const n = this.state.actors.filter(a => a.actor_type === code).length;
        return n || ACTOR_TYPES.find(a => a.code === code)?.n || 0;
    }

    // ---- Feed label color --------------------------------------------------
    feedColor(label) {
        if (label === "VENTA")  return "#16a34a";
        if (label === "ACTIV.") return "#4f46e5";
        return "#d97706";
    }

    // ---- Zona bar pct ------------------------------------------------------
    get zones() { return MOCK_ZONES; }
    get feed()  { return MOCK_FEED; }
    get sales() { return MOCK_SALES; }
    get actors(){ return ACTOR_TYPES; }
    get quickActions() { return QUICK_ACTIONS; }

    // ---- Inline lead editing (heredado) ------------------------------------
    getTypeLabel(type) {
        const m = { SPP:"Empresas", PAT:"Patrocinador", COL:"Colaborador", CCP:"Captador", SUB:"Subcolaborador", CLI:"Cliente", EMP:"Empleado", ASE:"Asesor", COM:"Comercial" };
        return m[type] || type;
    }
    formatDate(d) {
        if (!d) return "-";
        return new Date(d).toLocaleDateString("es-ES");
    }
    startEditing(lead) {
        this.state.editingId  = lead.id;
        this.state.editValues = { ...lead };
    }
    cancelEditing() {
        this.state.editingId  = null;
        this.state.editValues = {};
    }
    async saveEdit() {
        if (this.props.onUpdate) {
            await this.props.onUpdate(this.state.editingId, {
                name:      this.state.editValues.name,
                lead_type: this.state.editValues.lead_type,
                email:     this.state.editValues.email,
                phone:     this.state.editValues.phone,
                status:    this.state.editValues.status,
            });
        }
        this.state.editingId = null;
    }
    async handleDelete(id) {
        if (window.confirm("¿Eliminar este lead?") && this.props.onDelete) {
            await this.props.onDelete(id);
        }
    }
    onEditField(field, ev) {
        this.state.editValues = { ...this.state.editValues, [field]: ev.target.value };
    }

    // ---- Navegacion quick actions (llama setTab del padre) -----------------
    goTo(section) {
        if (typeof this.props.navigate === "function") {
            this.props.navigate(section);
        }
    }
}
