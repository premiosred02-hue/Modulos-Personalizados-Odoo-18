/** @odoo-module **/
// PREMIOSRED -- Leads CRM v4
// CRUD completo con sistema de permisos por rol: ADM | COL | SUB
// Vault refs: 50.06 NICHOS-OBJETIVO-COL · 50.05 ESTRATEGIA-VISITAS-COL
// Permisos: D:\Dev\PREMIOSRED-PANEL-UNIFICADO\src\core\permissions.ts
import { Component, useState, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

// ========================================================================
// PERMISOS POR ROL (mirror de permissions.ts del React)
// ADM: CRUD completo
// COL: crear, editar propios, agregar notas -- NO eliminar
// SUB: solo leer + agregar nota propia
// ========================================================================
const PERMS = {
    ADM: { canCreate:true,  canEdit:true,  canDelete:true,  canNote:true,  canChangeStage:true  },
    COL: { canCreate:true,  canEdit:true,  canDelete:false, canNote:true,  canChangeStage:true  },
    SUB: { canCreate:false, canEdit:false, canDelete:false, canNote:true,  canChangeStage:false },
};

function getRole(isAdmin) {
    // Odoo groups: base.group_system -> ADM, base.group_user -> COL default
    // El ADM viene del session.is_admin || is_superuser
    if (isAdmin) return "ADM";
    // TODO: mapear grupos Odoo a COL/SUB cuando existan grupos propios
    return "COL"; // Default COL para usuarios autenticados no-admin
}

// ========================================================================
// DATOS DEL VAULT
// ========================================================================
const NICHOS = [
    { tier:1, id:"1A", name:"Autobuses interurbanos",   ej:"SAMAR, ALSA, Avanza",      cautivo:"2-3 h",      vol:3, fric:"BAJA",  fricOk:true,  score:9,  ingreso:"97.200 EUR (SAMAR)" },
    { tier:1, id:"1B", name:"Transporte aereo",          ej:"Vueling, Ryanair, Binter", cautivo:"1-3 h",      vol:3, fric:"ALTA",  fricOk:false, score:7,  ingreso:"Pendiente" },
    { tier:1, id:"1C", name:"Clinicas / Espera medica",  ej:"Quironsalud, Sanitas",     cautivo:"20-60 min",  vol:2, fric:"MEDIA", fricOk:null,  score:8,  ingreso:"236 EUR" },
    { tier:1, id:"1D", name:"Hosteleria prolongada",     ej:"Cafeterias, Restaurantes", cautivo:"30-45 min",  vol:3, fric:"BAJA",  fricOk:true,  score:7,  ingreso:"226 EUR" },
    { tier:2, id:"2A", name:"Gasolineras",               ej:"Repsol, Cepsa, BP",        cautivo:"3-5 min",    vol:3, fric:"MEDIA", fricOk:null,  score:6,  ingreso:"567 EUR" },
    { tier:2, id:"2B", name:"Metro / Bus urbano",        ej:"EMT, TMB, Metro Madrid",   cautivo:"15-40 min",  vol:3, fric:"ALTA",  fricOk:false, score:5,  ingreso:"Pendiente" },
    { tier:2, id:"2C", name:"Pelucherias / Estetica",   ej:"Marco Aldany, barrio",     cautivo:"20-120 min", vol:1, fric:"BAJA",  fricOk:true,  score:8,  ingreso:"226 EUR" },
    { tier:3, id:"3A", name:"Iglesias / ONGs",           ej:"Cruz Roja, Caritas",       cautivo:"60-90 min",  vol:2, fric:"MEDIA", fricOk:null,  score:6,  ingreso:"--" },
    { tier:3, id:"3B", name:"Gimnasios",                 ej:"Altafit, McFit",           cautivo:"30-60 min",  vol:2, fric:"MEDIA", fricOk:null,  score:5,  ingreso:"--" },
    { tier:3, id:"3C", name:"Locutorios / Multiprecio",  ej:"Tiendas barrio, 24h",      cautivo:"5-10 min",   vol:1, fric:"BAJA",  fricOk:true,  score:4,  ingreso:"--" },
];

const FASES_VISITA = [
    { n:1, title:"Apertura (2 min)",     desc:"Presentacion personal + pitch de 60 segundos." },
    { n:2, title:"Demostracion (5 min)", desc:"Tablet con calculadora + landing PremiosRed." },
    { n:3, title:"Objeciones (5 min)",   desc:"Argumentario: coste CERO, legal 100%, sin gestion." },
    { n:4, title:"Contrato (3 min)",     desc:"3 lineas clave: sin pago, 3 meses, 45% en cuenta." },
    { n:5, title:"Cierre (1 min)",       desc:"Firmar hoy o dejar dossier + fecha de follow-up." },
];

const CALC_TABLE = [
    { tipo:"Bus (1 unidad)",    clientes:"120",   conv:"1%", packs:"~36",    comision:"162 EUR",    star:false },
    { tipo:"SAMAR (600 buses)", clientes:"72.000",conv:"1%", packs:"~21.600",comision:"97.200 EUR", star:true  },
    { tipo:"Bar medio",         clientes:"80",    conv:"3%", packs:"~72",    comision:"226 EUR",    star:false },
    { tipo:"Gasolinera AP",     clientes:"300",   conv:"2%", packs:"~180",   comision:"567 EUR",    star:false },
    { tipo:"Clinica",           clientes:"50",    conv:"5%", packs:"~75",    comision:"236 EUR",    star:false },
    { tipo:"Peluqueria",        clientes:"30",    conv:"8%", packs:"~72",    comision:"226 EUR",    star:false },
];

const ESTRATEGIA = [
    { fase:"Fase 1 - Mes 1-2", title:"Prueba de concepto", desc:"Autocares Bernardo (Almeria). Cerrar acuerdo, medir conversion real, crear caso de exito documentado." },
    { fase:"Fase 2 - Mes 3-6", title:"Expansion regional", desc:"5-10 empresas Tier 1+2. Palanca: 'Ya funcionamos con Autocares Bernardo, estas son sus metricas'." },
    { fase:"Fase 3 - Mes 7-12",title:"Escala nacional",    desc:"ALSA, Quironsalud, Vueling. Base: 10+ COLs con datos de conversion probados." },
];

const LEADS_MOCK = [
    { id:1, nombre:"SAMAR",             nicho:"Autobuses", contacto:"Dir. Operaciones", zona:"Almeria",   estado:"PROSPECTO",  tier:1, score:9, nota:"600 buses. Target P1 Elite. 97.200 EUR/mes potencial.", notas_log:[], created_by:"ADM" },
    { id:2, nombre:"Clinica Salud Plus",nicho:"Clinica",   contacto:"Director Medico",  zona:"CiudadReal",estado:"CONTACTADO", tier:1, score:8, nota:"Sala espera 30 pax/h. Reunion programada.",             notas_log:[], created_by:"ADM" },
    { id:3, nombre:"Bar El Rincon",     nicho:"Hosteleria",contacto:"Propietario",       zona:"Madrid",    estado:"ACTIVO",     tier:1, score:7, nota:"Alta completada. COL activo desde 25/04.",               notas_log:[], created_by:"COL" },
    { id:4, nombre:"Autocares Bernardo",nicho:"Autobuses", contacto:"Gerente",           zona:"Almeria",   estado:"EN PROCESO", tier:1, score:9, nota:"CIF A04032983. +60 autocares. Caso de exito Fase 1.",    notas_log:[], created_by:"ADM" },
    { id:5, nombre:"Farmacia Centro",   nicho:"Farmacia",  contacto:"Farmaceutico",      zona:"Sevilla",   estado:"ACTIVO",     tier:2, score:7, nota:"COL activo desde 28/04. Conversion 4.2%.",               notas_log:[], created_by:"COL" },
    { id:6, nombre:"Galp M30",          nicho:"Gasolinera",contacto:"Franquiciado",      zona:"Madrid",    estado:"PROSPECTO",  tier:2, score:6, nota:"300 clientes/dia. QR en surtidor pendiente.",            notas_log:[], created_by:"COL" },
    { id:7, nombre:"Barber Palace",     nicho:"Peluqueria",contacto:"Dueno",             zona:"Valdenenas",estado:"CONTACTADO", tier:2, score:8, nota:"45 min espera promedio. Alto potencial.",                notas_log:[], created_by:"COL" },
];

const ESTADOS   = ["PROSPECTO","CONTACTADO","EN PROCESO","ACTIVO"];
const TIER_LABELS = { 0:"Todos", 1:"Tier 1 - Elite", 2:"Tier 2 - Gran impacto", 3:"Tier 3 - Estrategico" };
const LEAD_DEFAULTS = () => ({ nombre:"", nicho:"Hosteleria", contacto:"", zona:"", tier:1, score:5, estado:"PROSPECTO", nota:"", email:"", phone:"", notas_log:[], created_by:"" });

// ========================================================================
export class PrLeadForm extends Component {
    static template = "promocionesred_dashboard.PrLeadForm";
    static props = {
        network: { type: Array,    optional: true },
        onAdd:   { type: Function, optional: true },
        leads:   { type: Array,    optional: true },
    };

    setup() {
        this.notification = useService("notification");
        this.orm          = useService("orm");
        this.session      = session;

        // Determinar rol
        const isAdmin = session.is_admin || session.is_superuser || false;
        this.userRole = getRole(isAdmin);
        this.perms    = PERMS[this.userRole];
        this.userName = session.name || "Usuario";

        // Exponer datos vault al template
        this.NICHOS      = NICHOS;
        this.FASES       = FASES_VISITA;
        this.CALC_TABLE  = CALC_TABLE;
        this.ESTRATEGIA  = ESTRATEGIA;
        this.ESTADOS     = ESTADOS;
        this.TIER_LABELS = TIER_LABELS;

        this.state = useState({
            tab:          "pipeline",
            filterTier:   0,
            filterEstado: "",
            search:       "",
            leads:        LEADS_MOCK,
            loading:      false,

            // Modal add/edit
            modalMode:    null,   // null | "add" | "edit"
            formData:     LEAD_DEFAULTS(),

            // Drawer detalle
            selectedLead: null,

            // Modal nota
            notaModal:    null,   // null | lead
            notaText:     "",

            saving: false,
        });

        onMounted(() => this._loadLeads());
    }

    // ---- Carga ORM ---------------------------------------------------------
    async _loadLeads() {
        this.state.loading = true;
        try {
            const data = await this.orm.searchRead(
                "pr.lead", [],
                ["id","name","lead_type","status","email","phone","city","notes","create_date","create_uid"],
                { order:"create_date desc", limit:200 }
            );
            if (data.length) {
                this.state.leads = data.map(d => ({
                    id: d.id, nombre: d.name, nicho: d.lead_type || "N/A",
                    contacto: "", zona: d.city || "", estado: d.status || "PROSPECTO",
                    tier: 1, score: 7, nota: d.notes || "",
                    email: d.email || "", phone: d.phone || "",
                    notas_log: [], created_by: d.create_uid?.[1] || "",
                }));
            }
        } catch (_) { /* usa mock */ }
        finally { this.state.loading = false; }
    }

    // ---- Computed ----------------------------------------------------------
    get filteredLeads() {
        let l = this.state.leads;
        if (this.state.filterTier)   l = l.filter(x => x.tier   === this.state.filterTier);
        if (this.state.filterEstado) l = l.filter(x => x.estado === this.state.filterEstado);
        if (this.state.search.trim()) {
            const q = this.state.search.toLowerCase();
            l = l.filter(x =>
                (x.nombre||"").toLowerCase().includes(q) ||
                (x.zona  ||"").toLowerCase().includes(q) ||
                (x.nicho ||"").toLowerCase().includes(q) ||
                (x.nota  ||"").toLowerCase().includes(q)
            );
        }
        return l;
    }

    get filteredNichos() {
        if (!this.state.filterTier) return this.NICHOS;
        return this.NICHOS.filter(n => n.tier === this.state.filterTier);
    }

    get kpi() {
        const l = this.state.leads;
        return {
            total:      l.length,
            activos:    l.filter(x => x.estado === "ACTIVO").length,
            prospectos: l.filter(x => x.estado === "PROSPECTO").length,
            proceso:    l.filter(x => x.estado === "EN PROCESO").length,
        };
    }

    // Helpers de color/estilo
    fricColor(ok) { return ok === true ? "#16a34a" : ok === false ? "#dc2626" : "#d97706"; }
    tierColor(t)  { return t === 1 ? "#111827" : t === 2 ? "#d97706" : "#9ca3af"; }
    starDot(n)    { return "★".repeat(n) + "☆".repeat(3-n); }

    estadoStyle(e) {
        const m = {
            "PROSPECTO":  "background:#f3f4f6;color:#6b7280",
            "CONTACTADO": "background:#fef9c3;color:#d97706",
            "EN PROCESO": "background:#dbeafe;color:#1d4ed8",
            "ACTIVO":     "background:#dcfce7;color:#16a34a",
        };
        return m[e] || "background:#f3f4f6;color:#6b7280";
    }

    roleBadgeStyle(role) {
        const m = {
            ADM: "background:#111827;color:#fff",
            COL: "background:#eef2ff;color:#4f46e5",
            SUB: "background:#f0fdf4;color:#16a34a",
        };
        return m[role] || "background:#f3f4f6;color:#6b7280";
    }

    // ---- Navegacion --------------------------------------------------------
    setTab(t)        { this.state.tab = t; this.state.selectedLead = null; }
    setTier(t)       { this.state.filterTier   = t; }
    setEstado(e)     { this.state.filterEstado = e; }
    setSearch(ev)    { this.state.search = ev.target.value; }

    // ---- Drawer ------------------------------------------------------------
    openDrawer(lead) {
        this.state.selectedLead = this.state.selectedLead?.id === lead.id ? null : lead;
    }
    closeDrawer()    { this.state.selectedLead = null; }

    // ---- Modal ADD ---------------------------------------------------------
    openAdd() {
        if (!this.perms.canCreate) {
            this.notification.add("No tienes permiso para crear leads.", { type: "warning" });
            return;
        }
        this.state.modalMode = "add";
        this.state.formData  = { ...LEAD_DEFAULTS(), created_by: this.userRole };
    }

    // ---- Modal EDIT --------------------------------------------------------
    openEdit(lead, ev) {
        if (ev) ev.stopPropagation();
        if (!this.perms.canEdit) {
            this.notification.add("No tienes permiso para editar leads.", { type: "warning" });
            return;
        }
        this.state.modalMode = "edit";
        this.state.formData  = { ...lead };
    }

    closeModal() {
        this.state.modalMode = null;
        this.state.formData  = LEAD_DEFAULTS();
    }

    onField(f, ev)   { this.state.formData = { ...this.state.formData, [f]: ev.target.value }; }
    onNum(f, ev)     { this.state.formData = { ...this.state.formData, [f]: parseInt(ev.target.value)||0 }; }

    async submitLead(ev) {
        ev.preventDefault();
        if (this.state.saving) return;
        this.state.saving = true;
        try {
            const fd = this.state.formData;
            if (this.state.modalMode === "add") {
                const newLead = { ...fd, id: Date.now(), notas_log: [] };
                this.state.leads = [newLead, ...this.state.leads];
                if (this.props.onAdd) {
                    await this.props.onAdd({
                        name: fd.nombre, lead_type: fd.nicho, status: fd.estado,
                        email: fd.email, phone: fd.phone, city: fd.zona, notes: fd.nota,
                    });
                }
                this.notification.add("Lead registrado correctamente.", { type: "success" });
            } else {
                // EDIT
                const idx = this.state.leads.findIndex(l => l.id === fd.id);
                if (idx >= 0) {
                    this.state.leads[idx] = { ...this.state.leads[idx], ...fd };
                    this.state.leads = [...this.state.leads];
                    // Si el drawer esta abierto, actualizar
                    if (this.state.selectedLead?.id === fd.id) {
                        this.state.selectedLead = this.state.leads[idx];
                    }
                }
                try {
                    await this.orm.write("pr.lead", [fd.id], {
                        name: fd.nombre, status: fd.estado, city: fd.zona,
                        email: fd.email, phone: fd.phone, notes: fd.nota,
                    });
                } catch(_) {}
                this.notification.add("Lead actualizado correctamente.", { type: "success" });
            }
            this.closeModal();
        } finally {
            this.state.saving = false;
        }
    }

    // ---- DELETE ------------------------------------------------------------
    async deleteLead(lead, ev) {
        if (ev) ev.stopPropagation();
        if (!this.perms.canDelete) {
            this.notification.add("Sin permiso para eliminar leads. Solo ADM puede eliminar.", { type: "warning" });
            return;
        }
        if (!window.confirm(`Eliminar "${lead.nombre}"? Esta accion no se puede deshacer.`)) return;
        this.state.leads = this.state.leads.filter(l => l.id !== lead.id);
        if (this.state.selectedLead?.id === lead.id) this.state.selectedLead = null;
        try { await this.orm.unlink("pr.lead", [lead.id]); } catch(_) {}
        this.notification.add("Lead eliminado.", { type: "success" });
    }

    // ---- NOTAS -------------------------------------------------------------
    openNota(lead, ev) {
        if (ev) ev.stopPropagation();
        if (!this.perms.canNote) return;
        this.state.notaModal = lead;
        this.state.notaText  = "";
    }

    closeNota()       { this.state.notaModal = null; this.state.notaText = ""; }
    onNotaText(ev)    { this.state.notaText = ev.target.value; }

    async saveNota(ev) {
        ev.preventDefault();
        if (!this.state.notaText.trim()) return;
        const lead    = this.state.notaModal;
        const now     = new Date().toLocaleString("es-ES");
        const entrada = `[${now}] ${this.userName} (${this.userRole}): ${this.state.notaText.trim()}`;

        // Actualizar en local
        const idx = this.state.leads.findIndex(l => l.id === lead.id);
        if (idx >= 0) {
            const updated = { ...this.state.leads[idx] };
            updated.notas_log = [...(updated.notas_log || []), entrada];
            // Concatenar al campo nota principal como historial
            updated.nota = updated.nota ? updated.nota + "\n" + entrada : entrada;
            this.state.leads[idx] = updated;
            this.state.leads = [...this.state.leads];
            if (this.state.selectedLead?.id === lead.id) {
                this.state.selectedLead = updated;
            }
        }
        // Persistir en ORM
        try {
            await this.orm.write("pr.lead", [lead.id], { notes: this.state.leads[idx]?.nota || "" });
        } catch(_) {}

        this.notification.add("Nota agregada.", { type: "success" });
        this.closeNota();
    }

    // ---- Cambio estado rapido ----------------------------------------------
    moveEstado(lead, ev) {
        if (!this.perms.canChangeStage) {
            this.notification.add("Sin permiso para cambiar etapa.", { type: "warning" });
            return;
        }
        const newEstado = ev.target.value;
        lead.estado = newEstado;
        this.state.leads = [...this.state.leads];
        try { this.orm.write("pr.lead", [lead.id], { status: newEstado }); } catch(_) {}
    }
}
