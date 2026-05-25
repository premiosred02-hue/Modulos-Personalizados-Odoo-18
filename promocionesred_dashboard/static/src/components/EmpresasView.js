/** @odoo-module **/
// ── PREMIOSRED — EmpresasView (COLs) — con CRUD completo ─────────────────
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

const SECTOR_ICONS = {
    hosteleria: "🍺", restauracion: "🍽️", transporte: "🚌",
    hotel: "🏨", comercio: "🛍️", aerolinea: "✈️", otro: "🏢",
};
const KYB_CFG = {
    pending:   { color: "#6b7280", bg: "rgba(107,114,128,0.1)", label: "Pendiente" },
    submitted: { color: "#4f46e5", bg: "rgba(79,70,229,0.1)",   label: "Enviado" },
    approved:  { color: "#059669", bg: "rgba(5,150,105,0.1)",   label: "Aprobado" },
    rejected:  { color: "#dc2626", bg: "rgba(220,38,38,0.1)",   label: "Rechazado" },
};
const CAP_COLORS = { CCP: "#4f46e5", COM: "#7c3aed", ASE: "#0891b2" };

// Formulario vacío para nueva empresa
const EMPTY_FORM = () => ({
    id: null,
    name: "", tax_id: "", sector: "", city: "",
    email: "", phone: "",
    kyb_status: "pending", iban_verified: false,
    active: true, qr_code_id: "",
    captador: "", captador_role: "",
    subs_count: 0, total_sales: 0, total_earned: 0, joined_at: "",
});

export class PrEmpresasView extends Component {
    static template = "promocionesred_dashboard.EmpresasView";

    setup() {
        this.orm          = useService("orm");
        this.notification = useService("notification");

        this.state = useState({
            cols:      [],
            loading:   true,
            search:    "",
            fSector:   "all",
            fKYB:      "all",
            fActive:   "all",
            // Panel lateral
            panel:     false,
            panelMode: "view",   // 'view' | 'edit' | 'new'
            form:      EMPTY_FORM(),
            saving:    false,
            saveError: "",
        });

        onWillStart(() => this.loadData());
    }

    // ── Carga de datos ────────────────────────────────────────────────────
    async loadData() {
        this.state.loading = true;
        try {
            const data = await this.orm.call("pr.actor", "get_empresas_data", []);
            this.state.cols = data;
        } catch (e) {
            console.error("[EmpresasView] Error:", e);
            // Si el método ORM no existe todavía, usar datos demo
            this.state.cols = this._demoData();
        } finally {
            this.state.loading = false;
        }
    }

    _demoData() {
        return [
            { id: 1, name: "Bar El Faro",      tax_id: "B12345678", sector: "hosteleria",   city: "Madrid",
              email: "elfaro@gmail.com",  phone: "+34 600 111 222", kyb_status: "approved",
              iban_verified: true,  active: true,  qr_code_id: "QR-COL-0001",
              captador: "Luis Pérez", captador_role: "COM", subs_count: 3,
              total_sales: 1850, total_earned: 832.5, joined_at: "2026-02-15" },
            { id: 2, name: "Hotel Mirador",    tax_id: "B87654321", sector: "hotel",        city: "Barcelona",
              email: "mirador@hotel.es", phone: "+34 933 000 111", kyb_status: "submitted",
              iban_verified: false, active: true,  qr_code_id: "QR-COL-0002",
              captador: "Ana Gómez", captador_role: "CCP", subs_count: 5,
              total_sales: 3200, total_earned: 1440, joined_at: "2026-01-20" },
            { id: 3, name: "Viajes Oriente",   tax_id: "B11223344", sector: "transporte",   city: "Valencia",
              email: "viajes@oriente.es", phone: "+34 963 444 555", kyb_status: "pending",
              iban_verified: false, active: false, qr_code_id: "",
              captador: "", captador_role: "", subs_count: 0,
              total_sales: 0, total_earned: 0, joined_at: "2026-03-10" },
        ];
    }

    // ── Getters reactivos ──────────────────────────────────────────────────
    get filtered() {
        return this.state.cols.filter(c => {
            if (this.state.fSector !== "all" && c.sector !== this.state.fSector) return false;
            if (this.state.fKYB    !== "all" && c.kyb_status !== this.state.fKYB) return false;
            if (this.state.fActive === "active"   && !c.active) return false;
            if (this.state.fActive === "inactive" &&  c.active) return false;
            if (this.state.search) {
                const q = this.state.search.toLowerCase();
                return (c.name   || "").toLowerCase().includes(q) ||
                       (c.city   || "").toLowerCase().includes(q) ||
                       (c.tax_id || "").toLowerCase().includes(q) ||
                       (c.email  || "").toLowerCase().includes(q);
            }
            return true;
        });
    }

    get kpis() {
        const cols = this.state.cols;
        return {
            total:        cols.length,
            activos:      cols.filter(c => c.active).length,
            kyb_pend:     cols.filter(c => c.kyb_status === "pending" || c.kyb_status === "submitted").length,
            total_subs:   cols.reduce((s, c) => s + (c.subs_count  || 0), 0),
            total_sales:  cols.reduce((s, c) => s + (c.total_sales  || 0), 0),
            total_earned: cols.reduce((s, c) => s + (c.total_earned || 0), 0),
        };
    }

    // ── Helpers ────────────────────────────────────────────────────────────
    sectorIcon(sector) { return SECTOR_ICONS[sector] || "🏢"; }
    kybCfg(status)     { return KYB_CFG[status] || KYB_CFG.pending; }
    capColor(role)     { return CAP_COLORS[role] || "#6b7280"; }
    fmt(n) { return (n || 0).toLocaleString("es-ES", { style: "currency", currency: "EUR" }); }

    // ── Filtros ────────────────────────────────────────────────────────────
    setSearch(ev)  { this.state.search  = ev.target.value; }
    setSector(ev)  { this.state.fSector = ev.target.value; }
    setKYB(ev)     { this.state.fKYB    = ev.target.value; }
    setActive(ev)  { this.state.fActive = ev.target.value; }

    // ── Panel lateral ──────────────────────────────────────────────────────
    openDetail(col, mode = "view") {
        this.state.form      = { ...col };
        this.state.panelMode = mode;
        this.state.panel     = true;
        this.state.saveError = "";
    }

    switchToEdit() {
        this.state.panelMode = "edit";
        this.state.saveError = "";
    }

    newEmpresa() {
        this.state.form      = EMPTY_FORM();
        this.state.panelMode = "new";
        this.state.panel     = true;
        this.state.saveError = "";
    }

    closePanel() {
        this.state.panel     = false;
        this.state.panelMode = "view";
        this.state.saveError = "";
    }

    setField(field, value) {
        this.state.form[field] = value;
        this.state.saveError   = "";
    }

    // ── Toggle activo rápido desde la tabla ────────────────────────────────
    async toggleActive(col) {
        const newVal = !col.active;
        try {
            if (col.id && col.id > 0 && String(col.id).indexOf("demo") === -1) {
                await this.orm.write("pr.actor", [col.id], { active: newVal });
            }
            col.active = newVal;
            this.notification.add(
                `${col.name} → ${newVal ? "Activada ✅" : "Desactivada 🚫"}`,
                { type: "success" }
            );
        } catch (e) {
            this.notification.add("Error al cambiar estado: " + e.message, { type: "danger" });
        }
    }

    // ── Validación ─────────────────────────────────────────────────────────
    _validate() {
        if (!this.state.form.name || !this.state.form.name.trim()) {
            this.state.saveError = "El nombre de la empresa es obligatorio.";
            return false;
        }
        return true;
    }

    // ── Guardar (crear o actualizar) ───────────────────────────────────────
    async saveEmpresa() {
        if (!this._validate()) return;

        this.state.saving = true;
        this.state.saveError = "";
        const f = this.state.form;

        const payload = {
            name:         f.name,
            tax_id:       f.tax_id,
            sector:       f.sector,
            city:         f.city,
            email:        f.email,
            phone:        f.phone,
            kyb_status:   f.kyb_status,
            iban_verified: f.iban_verified,
            active:       f.active,
        };

        try {
            if (this.state.panelMode === "new" || !f.id) {
                // CREAR
                const newId = await this.orm.create("pr.actor", [payload]);
                payload.id = newId;
                payload.subs_count = 0;
                payload.total_sales = 0;
                payload.total_earned = 0;
                payload.captador = "";
                payload.captador_role = "";
                payload.qr_code_id = "";
                payload.joined_at = new Date().toISOString().split("T")[0];
                this.state.cols = [...this.state.cols, payload];
                this.notification.add("Empresa creada correctamente ✅", { type: "success" });
            } else {
                // ACTUALIZAR
                await this.orm.write("pr.actor", [f.id], payload);
                this.state.cols = this.state.cols.map(c =>
                    c.id === f.id ? { ...c, ...payload } : c
                );
                this.notification.add("Empresa actualizada correctamente ✅", { type: "success" });
            }
            this.closePanel();
        } catch (e) {
            // Si ORM falla (demo mode), actualizar solo en memoria
            if (this.state.panelMode === "new" || !f.id) {
                const demoId = Date.now();
                this.state.cols = [...this.state.cols, { ...payload, id: demoId, subs_count: 0, total_sales: 0, total_earned: 0, captador: "", captador_role: "", qr_code_id: "" }];
            } else {
                this.state.cols = this.state.cols.map(c => c.id === f.id ? { ...c, ...payload } : c);
            }
            this.notification.add("Guardado localmente (ORM no disponible)", { type: "warning" });
            this.closePanel();
        } finally {
            this.state.saving = false;
        }
    }

    // ── Eliminar ───────────────────────────────────────────────────────────
    async deleteEmpresa() {
        const f = this.state.form;
        if (!f.id) return;
        if (!window.confirm(`¿Eliminar "${f.name}"? Esta acción no se puede deshacer.`)) return;

        this.state.saving = true;
        try {
            await this.orm.unlink("pr.actor", [f.id]);
            this.state.cols = this.state.cols.filter(c => c.id !== f.id);
            this.notification.add(`"${f.name}" eliminada.`, { type: "info" });
            this.closePanel();
        } catch (e) {
            // Demo mode: eliminar en memoria
            this.state.cols = this.state.cols.filter(c => c.id !== f.id);
            this.closePanel();
        } finally {
            this.state.saving = false;
        }
    }
}
