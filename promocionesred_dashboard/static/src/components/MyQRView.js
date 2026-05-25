/** @odoo-module **/
// PREMIOSRED -- MyQR View v3
// Replica: D:\Antigravity\PremiosRed\...\SISTEMA QR
// URL estructura: /verify/<col_id>/<sub_id?>/<sponsor_id?>?type=<portal>&label=<label>
// SHA-256 para encryptedId -- compatible con sistema original
import { Component, useState, onMounted, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

// ---- Configuracion de portales (replica VerificationPortal.jsx) -----------
const PORTAL_TYPES = [
    { value: "standard",  label: "Standard",  color: "#111827", bg: "#f9fafb",  icon: "check" },
    { value: "premium",   label: "Premium",   color: "#2563eb", bg: "#eff6ff",  icon: "star"  },
    { value: "marketing", label: "Marketing", color: "#db2777", bg: "#fdf2f8",  icon: "bell"  },
];

// ---- URL base del portal de validacion -----------------------------------
// El controller verify.py registra la ruta como /verify/<encrypted_id> (sin /web/)
const PORTAL_BASE_URL = window.location.origin + "/verify";

// ---- Generar SHA-256 (replica generateSHA256 de crypto.js) ----------------
async function sha256(str) {
    try {
        const buf  = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(str));
        return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2,"0")).join("");
    } catch (_) {
        // Fallback: hash simple si SubtleCrypto no disponible
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            hash = ((hash << 5) - hash) + str.charCodeAt(i);
            hash |= 0;
        }
        return Math.abs(hash).toString(16).padStart(16, "0");
    }
}

// ---- Construir URL del QR -------------------------------------------------
function buildQRUrl(encryptedId, portalType, label, subId, sponsorId) {
    let url = `${PORTAL_BASE_URL}/${encryptedId}`;
    const params = new URLSearchParams();
    if (portalType && portalType !== "standard") params.append("type", portalType);
    if (label)     params.append("label", label);
    if (subId)     params.append("sub",   subId);
    if (sponsorId) params.append("spon",  sponsorId);
    const q = params.toString();
    return q ? `${url}?${q}` : url;
}

// ---- Generar QR via Canvas (sin libreria externa) -------------------------
// Usamos Google Charts API como fallback -- compatible con entorno Odoo
function getQRImageUrl(text, size) {
    return `https://api.qrserver.com/v1/create-qr-code/?size=${size}x${size}&data=${encodeURIComponent(text)}&ecc=H&margin=2`;
}

// ---- Mock de actores para inicializar ------------------------------------
const MOCK_ACTORS = [
    { id:1, col_code:"COL-001", sub_code:"",       sponsor_code:"SPP-01", name:"Bar El Rincon",      portalType:"standard",  label:"PremiosRed 2026", customLabel:"Sorteo Navidad", scanCount:42, status:"Activo",   encryptedId:"" },
    { id:2, col_code:"COL-002", sub_code:"SUB-001", sponsor_code:"",       name:"Farmacia Garcia",    portalType:"premium",   label:"Farmacia Premio", customLabel:"Pack Salud",     scanCount:18, status:"Activo",   encryptedId:"" },
    { id:3, col_code:"COL-003", sub_code:"",        sponsor_code:"SPP-02", name:"Autocares Bernardo", portalType:"marketing", label:"SAMAR QR Tour",   customLabel:"Pack Viaje",     scanCount:156,status:"Activo",   encryptedId:"" },
    { id:4, col_code:"COL-004", sub_code:"SUB-002", sponsor_code:"",       name:"Barber Palace",      portalType:"standard",  label:"PremiosRed 2026", customLabel:"Peluqueria",     scanCount:7,  status:"Inactivo", encryptedId:"" },
];

export class PrMyQRView extends Component {
    static template = "promocionesred_dashboard.PrMyQRView";
    static props = {};

    setup() {
        this.orm          = useService("orm");
        this.notification = useService("notification");
        this.session      = session;
        this.PORTAL_TYPES = PORTAL_TYPES;

        this.state = useState({
            records:      [],
            loading:      true,

            // Vista
            view:         "table",   // "table" | "my-qr"

            // Record seleccionado para ver/editar QR
            selected:     null,
            showQRModal:  false,
            showAddModal: false,
            showEditModal:false,
            copiedUrl:    false,

            // Formulario nuevo registro / editar
            form: {
                name:"", col_code:"", sub_code:"", sponsor_code:"",
                portalType:"standard", label:"PremiosRed 2026", customLabel:"Sorteo Navidad",
                status:"Activo",
            },
            saving: false,
        });

        onMounted(() => this._init());
    }

    // ---- Inicializacion ----------------------------------------------------
    async _init() {
        this.state.loading = true;
        try {
            // Cargar actores desde ORM usando los campos reales de pr.actor
            const actors = await this.orm.searchRead(
                "pr.actor", [],
                [
                    "id", "name", "actor_type", "status",
                    // Código del actor (generado en create)
                    "code", "qr_code_id",
                    // Campos del sistema QR (añadidos en pr_actor.py)
                    "col_code", "sub_code", "sponsor_code",
                    "scan_count", "portal_type", "custom_label",
                ],
                { limit: 100 }
            );

            if (actors.length) {
                const enriched = await Promise.all(actors.map(async a => {
                    // El seed debe ser idéntico al que usa verify.py en el backend
                    const seed  = `actor-${a.id}-${a.name}`;
                    const encId = await sha256(seed);
                    return {
                        id:           a.id,
                        name:         a.name,
                        // col_code usa el campo QR; si está vacío cae al campo "code" del actor
                        col_code:     a.col_code     || a.code || `COL-${String(a.id).padStart(3, "0")}`,
                        sub_code:     a.sub_code     || "",
                        sponsor_code: a.sponsor_code || "",
                        portalType:   a.portal_type  || "standard",
                        label:        "PremiosRed 2026",
                        customLabel:  a.custom_label || "Sorteo Navidad",
                        // Los estados de pr.actor son ACTIVO/PENDIENTE/SUSPENDIDO/BAJA
                        status:       a.status === "ACTIVO" ? "Activo" : (a.status || "Pendiente"),
                        scanCount:    a.scan_count   || 0,
                        encryptedId:  encId,
                    };
                }));
                this.state.records = enriched;
            } else {
                // Sin actores en BD: cargar mock para demo
                const enriched = await Promise.all(MOCK_ACTORS.map(async a => {
                    const encId = await sha256(`actor-${a.id}-${a.name}`);
                    return { ...a, encryptedId: encId };
                }));
                this.state.records = enriched;
            }
        } catch (err) {
            // Error en ORM (ej: campo aún no existe tras migración): fallback a mock
            console.warn("[MyQRView] ORM error, usando mock:", err);
            const enriched = await Promise.all(MOCK_ACTORS.map(async a => ({
                ...a, encryptedId: await sha256(`actor-${a.id}-${a.name}`)
            })));
            this.state.records = enriched;
        } finally {
            this.state.loading = false;
        }
    }

    // ---- Helpers -----------------------------------------------------------
    getPortal(type) { return PORTAL_TYPES.find(p => p.value === type) || PORTAL_TYPES[0]; }

    getQRUrl(record) {
        return buildQRUrl(
            record.encryptedId,
            record.portalType,
            record.customLabel || record.label,
            record.sub_code,
            record.sponsor_code
        );
    }

    getQRImg(record, size = 240) {
        return getQRImageUrl(this.getQRUrl(record), size);
    }

    getShortId(enc) {
        if (!enc) return "---";
        return enc.substring(0, 12) + "...";
    }

    // ---- Navegacion --------------------------------------------------------
    setView(v)   { this.state.view = v; }

    // ---- Modal QR ----------------------------------------------------------
    openQR(record) {
        this.state.selected   = record;
        this.state.showQRModal = true;
    }
    closeQR()    { this.state.showQRModal = false; this.state.selected = null; this.state.copiedUrl = false; }

    async copyUrl(record) {
        const url = this.getQRUrl(record);
        try {
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(url);
            } else {
                const ta = document.createElement("textarea");
                ta.value = url;
                document.body.appendChild(ta);
                ta.select();
                document.execCommand("copy");
                document.body.removeChild(ta);
            }
            this.state.copiedUrl = true;
            this.notification.add("URL copiada al portapapeles.", { type: "success" });
            setTimeout(() => { this.state.copiedUrl = false; }, 2000);
        } catch (_) {
            this.notification.add("Copia manual: " + url, { type: "warning" });
        }
    }

    downloadQR(record) {
        const url = this.getQRImg(record, 600);
        const a = document.createElement("a");
        a.href = url;
        a.download = `QR_${record.name.replace(/\s+/g,"_")}.png`;
        a.target = "_blank";
        a.click();
    }

    printQR(record) {
        const url = this.getQRImg(record, 400);
        const qrUrl = this.getQRUrl(record);
        const portal = this.getPortal(record.portalType);
        const win = window.open("", "_blank");
        win.document.write(`
            <html><head><title>QR - ${record.name}</title>
            <style>body{font-family:Arial,sans-serif;text-align:center;padding:2rem;background:#fff;}
            img{border:1px solid #e5e7eb;border-radius:12px;padding:1rem;}
            code{display:block;font-size:10px;color:#6b7280;word-break:break-all;margin-top:1rem;border:1px solid #e5e7eb;padding:.5rem;border-radius:6px;}
            h2{color:#111827;margin-bottom:.25rem}p{color:#6b7280;margin:.25rem 0 1.5rem}
            </style></head><body>
            <h2>${record.customLabel || "PremiosRed QR"}</h2>
            <p>${record.name} · COL: ${record.col_code}${record.sub_code ? " · SUB: "+record.sub_code : ""}${record.sponsor_code ? " · SPP: "+record.sponsor_code : ""}</p>
            <img src="${url}" width="300" height="300"/>
            <code>${qrUrl}</code>
            <p style="margin-top:1rem;font-size:.75rem;color:#9ca3af">Portal: ${portal.label} · PremiosRed 2026</p>
            <script>window.onload=()=>{window.print();window.close();}</script>
            </body></html>
        `);
        win.document.close();
    }

    // ---- Reset escaneos ----------------------------------------------------
    resetScans(record) {
        if (!window.confirm(`Resetear ${record.scanCount} escaneos de "${record.name}"?`)) return;
        const idx = this.state.records.findIndex(r => r.id === record.id);
        if (idx >= 0) {
            this.state.records[idx] = { ...this.state.records[idx], scanCount: 0 };
            this.state.records = [...this.state.records];
            if (this.state.selected?.id === record.id) {
                this.state.selected = this.state.records[idx];
            }
        }
        this.notification.add("Escaneos reseteados.", { type: "success" });
    }

    // ---- Regenerar ID (nuevo SHA-256) ------------------------------------
    async regenerateId(record) {
        if (!window.confirm(`Regenerar ID de seguridad para "${record.name}"? El QR anterior dejara de ser valido.`)) return;
        const seed   = `actor-${record.id}-${record.name}-${Math.random().toString(36).slice(2)}`;
        const newEnc = await sha256(seed);
        const idx = this.state.records.findIndex(r => r.id === record.id);
        if (idx >= 0) {
            this.state.records[idx] = { ...this.state.records[idx], encryptedId: newEnc };
            this.state.records = [...this.state.records];
            if (this.state.selected?.id === record.id) {
                this.state.selected = this.state.records[idx];
            }
        }
        this.notification.add("ID regenerado. Nuevo QR disponible.", { type: "success" });
    }

    // ---- Cambio de estado --------------------------------------------------
    changeStatus(record, ev) {
        const idx = this.state.records.findIndex(r => r.id === record.id);
        if (idx >= 0) {
            this.state.records[idx] = { ...this.state.records[idx], status: ev.target.value };
            this.state.records = [...this.state.records];
        }
    }

    // ---- Modal ADD/EDIT ----------------------------------------------------
    openAdd() {
        this.state.form = { name:"", col_code:"", sub_code:"", sponsor_code:"", portalType:"standard", label:"PremiosRed 2026", customLabel:"Sorteo Navidad", status:"Activo" };
        this.state.showAddModal = true;
    }

    openEdit(record, ev) {
        if (ev) ev.stopPropagation();
        this.state.form = { ...record };
        this.state.showEditModal = true;
    }

    closeModal() {
        this.state.showAddModal  = false;
        this.state.showEditModal = false;
    }

    onForm(f, ev) { this.state.form = { ...this.state.form, [f]: ev.target.value }; }

    async submitForm(ev) {
        ev.preventDefault();
        this.state.saving = true;
        try {
            const fd = this.state.form;
            if (this.state.showEditModal) {
                const idx = this.state.records.findIndex(r => r.id === fd.id);
                if (idx >= 0) {
                    this.state.records[idx] = { ...this.state.records[idx], ...fd };
                    this.state.records = [...this.state.records];
                }
                this.notification.add("Registro actualizado.", { type: "success" });
            } else {
                const nextId  = this.state.records.length ? Math.max(...this.state.records.map(r => r.id)) + 1 : 1;
                const encId   = await sha256(`actor-${nextId}-${fd.name}`);
                const newRec  = { ...fd, id: nextId, encryptedId: encId, scanCount: 0 };
                this.state.records = [newRec, ...this.state.records];
                this.notification.add("Registro creado. QR disponible.", { type: "success" });
            }
            this.closeModal();
        } finally {
            this.state.saving = false;
        }
    }

    // ---- Delete ------------------------------------------------------------
    async deleteRecord(record, ev) {
        if (ev) ev.stopPropagation();
        if (!window.confirm(`Eliminar "${record.name}"? El QR asociado dejara de funcionar.`)) return;
        this.state.records = this.state.records.filter(r => r.id !== record.id);
        this.notification.add("Registro eliminado.", { type: "success" });
    }

    // ---- KPIs globales -----------------------------------------------------
    get kpi() {
        const r = this.state.records;
        return {
            total:    r.length,
            activos:  r.filter(x => x.status === "Activo").length,
            scans:    r.reduce((s, x) => s + (x.scanCount || 0), 0),
            topScan:  r.reduce((m, x) => x.scanCount > m ? x.scanCount : m, 0),
        };
    }
}
