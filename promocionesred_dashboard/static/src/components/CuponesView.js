/** @odoo-module **/
/**
 * PREMIOSRED — CuponesView v5 (Odoo Owl)
 *
 *  • Tab 1: Banco de Códigos por Patrocinador
 *  • Tab 2: Cupones por Cliente (cards expandibles)
 *  • Tab 3: Seguimiento PDV — Carteles por COL/SUB/Tienda/Zona
 *           Trazabilidad completa: Patrocinador → COL → Tienda → SUB → Cartel → Cliente
 */
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

// ── Catálogo de patrocinadores ─────────────────────────────────────────────
const PATROCINADORES_INIT = [
    { num: 1,  cat: 'Tecnología',      obj: 'Apple España',           cod_prefix: 'APL', cargados: 500, usados: 312 },
    { num: 2,  cat: 'Moda',            obj: 'Zara / Inditex',         cod_prefix: 'ZAR', cargados: 500, usados: 289 },
    { num: 3,  cat: 'Cosmética',       obj: 'Kiko Milano',            cod_prefix: 'KIK', cargados: 300, usados: 201 },
    { num: 4,  cat: 'Viajes/Hotel',    obj: 'Marriott International', cod_prefix: 'MAR', cargados: 500, usados: 298 },
    { num: 5,  cat: 'Gran Superficie', obj: 'Por definir',            cod_prefix: 'GRN', cargados: 0,   usados: 0   },
    { num: 6,  cat: 'Restauración',    obj: 'Por definir',            cod_prefix: 'RES', cargados: 0,   usados: 0   },
    { num: 7,  cat: 'Electrónica',     obj: 'Por definir',            cod_prefix: 'ELC', cargados: 0,   usados: 0   },
    { num: 8,  cat: 'Salud/Belleza',   obj: 'Por definir',            cod_prefix: 'SAL', cargados: 0,   usados: 0   },
    { num: 9,  cat: 'Hotel (bono)',    obj: 'Proveedor hotelero',     cod_prefix: 'HOT', cargados: 400, usados: 156 },
    { num: 10, cat: 'Booking.com',     obj: 'Booking.com',            cod_prefix: 'BOK', cargados: 500, usados: 298 },
];

// ── Demo clientes (Tab 2) ───────────────────────────────────────────────────
const DEMO_CLIENTES = [
    {
        id: 'c1', user_name: 'María García', user_email: 'maria.g@gmail.com',
        user_phone: '+34 612 345 678', orden: 'ORD-2026-0001', pack: 'PTK',
        fecha_compra: '2026-04-28',
        col_name: 'Bar La Copa', sub_name: 'Carlos López', cartel_id: 'CAR-T01-A', zona: 'Chamberí',
        cupones: [
            { pat_num: 1,  pat_nombre: 'Apple España',           codigo: 'APL-X7KP2M',    usado: true,  fecha_uso: '2026-05-02' },
            { pat_num: 2,  pat_nombre: 'Zara / Inditex',         codigo: 'ZAR-Q9NR4T',    usado: true,  fecha_uso: '2026-05-01' },
            { pat_num: 3,  pat_nombre: 'Kiko Milano',            codigo: 'KIK-B3LW8S',    usado: false  },
            { pat_num: 4,  pat_nombre: 'Marriott International', codigo: 'MAR-H6VD1K',    usado: false  },
            { pat_num: 5,  pat_nombre: 'Por definir',            codigo: 'GRN-PENDIENTE', usado: false  },
            { pat_num: 6,  pat_nombre: 'Por definir',            codigo: 'RES-PENDIENTE', usado: false  },
            { pat_num: 7,  pat_nombre: 'Por definir',            codigo: 'ELC-PENDIENTE', usado: false  },
            { pat_num: 8,  pat_nombre: 'Por definir',            codigo: 'SAL-PENDIENTE', usado: false  },
            { pat_num: 9,  pat_nombre: 'Bono Hotel',             codigo: 'HOT-T4MR9Z',    usado: true,  fecha_uso: '2026-05-10' },
            { pat_num: 10, pat_nombre: 'Booking.com',            codigo: 'BOK-N2PC7X',    usado: false  },
        ],
        sorteo_code: 'PRE-2026-0001', own_hash: 'a3f8d2e1',
    },
    {
        id: 'c2', user_name: 'Carlos Herrera', user_email: 'carlos.h@hotmail.com',
        user_phone: '+34 678 901 234', orden: 'ORD-2026-0002', pack: 'PTK',
        fecha_compra: '2026-04-25',
        col_name: 'Bar La Copa', sub_name: 'Javier Ruiz', cartel_id: 'CAR-T02-A', zona: 'Malasaña',
        cupones: [
            { pat_num: 1,  pat_nombre: 'Apple España',           codigo: 'APL-M3NP8W',    usado: true,  fecha_uso: '2026-04-30' },
            { pat_num: 2,  pat_nombre: 'Zara / Inditex',         codigo: 'ZAR-K7RT2Q',    usado: false  },
            { pat_num: 3,  pat_nombre: 'Kiko Milano',            codigo: 'KIK-P9VB4L',    usado: true,  fecha_uso: '2026-05-05' },
            { pat_num: 4,  pat_nombre: 'Marriott International', codigo: 'MAR-S6WD3H',    usado: false  },
            { pat_num: 5,  pat_nombre: 'Por definir',            codigo: 'GRN-PENDIENTE', usado: false  },
            { pat_num: 6,  pat_nombre: 'Por definir',            codigo: 'RES-PENDIENTE', usado: false  },
            { pat_num: 7,  pat_nombre: 'Por definir',            codigo: 'ELC-PENDIENTE', usado: false  },
            { pat_num: 8,  pat_nombre: 'Por definir',            codigo: 'SAL-PENDIENTE', usado: false  },
            { pat_num: 9,  pat_nombre: 'Bono Hotel',             codigo: 'HOT-W2LN5T',    usado: false  },
            { pat_num: 10, pat_nombre: 'Booking.com',            codigo: 'BOK-Q4BM6P',    usado: true,  fecha_uso: '2026-05-01' },
        ],
        sorteo_code: 'PRE-2026-0002', own_hash: 'b4e9c3f2',
    },
    {
        id: 'c3', user_name: 'Ana Soto', user_email: 'ana.soto@gmail.com',
        user_phone: '+34 655 432 198', orden: 'ORD-2026-0003', pack: 'PTK',
        fecha_compra: '2026-05-01',
        col_name: 'Bar La Copa', sub_name: 'Ana Martínez', cartel_id: 'CAR-T03-B', zona: 'Lavapiés',
        cupones: [
            { pat_num: 1,  pat_nombre: 'Apple España',           codigo: 'APL-R8KT5N',    usado: false },
            { pat_num: 2,  pat_nombre: 'Zara / Inditex',         codigo: 'ZAR-V3PW9M',    usado: false },
            { pat_num: 3,  pat_nombre: 'Kiko Milano',            codigo: 'KIK-X7ND2L',    usado: false },
            { pat_num: 4,  pat_nombre: 'Marriott International', codigo: 'MAR-B4QS8K',    usado: false },
            { pat_num: 5,  pat_nombre: 'Por definir',            codigo: 'GRN-PENDIENTE', usado: false },
            { pat_num: 6,  pat_nombre: 'Por definir',            codigo: 'RES-PENDIENTE', usado: false },
            { pat_num: 7,  pat_nombre: 'Por definir',            codigo: 'ELC-PENDIENTE', usado: false },
            { pat_num: 8,  pat_nombre: 'Por definir',            codigo: 'SAL-PENDIENTE', usado: false },
            { pat_num: 9,  pat_nombre: 'Bono Hotel',             codigo: 'HOT-C9WP4T',    usado: false },
            { pat_num: 10, pat_nombre: 'Booking.com',            codigo: 'BOK-L7VR3N',    usado: false },
        ],
        sorteo_code: 'PRE-2026-0003', own_hash: 'c5f0d4g3',
    },
];

// ── Demo Seguimiento PDV (Tab 3) ────────────────────────────────────────────
// Estructura: 1 COL × 5 Tiendas × 1 SUB/Tienda × 3 Carteles/Tienda = 15 carteles
const DEMO_TIENDAS = [
    { id: 'T01', nombre: 'Bar La Copa - Chamberí',  zona: 'Madrid Norte',  sub_id: 'S01', sub_name: 'Carlos López',    sub_email: 'carlos.l@mail.com',  sub_phone: '+34 611 001 001' },
    { id: 'T02', nombre: 'Bar La Copa - Malasaña',  zona: 'Madrid Centro', sub_id: 'S02', sub_name: 'Javier Ruiz',     sub_email: 'javier.r@mail.com',  sub_phone: '+34 622 002 002' },
    { id: 'T03', nombre: 'Bar La Copa - Lavapiés',  zona: 'Madrid Sur',    sub_id: 'S03', sub_name: 'Ana Martínez',    sub_email: 'ana.m@mail.com',     sub_phone: '+34 633 003 003' },
    { id: 'T04', nombre: 'Bar La Copa - Retiro',    zona: 'Madrid Este',   sub_id: 'S04', sub_name: 'Pedro Sánchez',   sub_email: 'pedro.s@mail.com',   sub_phone: '+34 644 004 004' },
    { id: 'T05', nombre: 'Bar La Copa - Moncloa',   zona: 'Madrid Oeste',  sub_id: 'S05', sub_name: 'Laura García',    sub_email: 'laura.g@mail.com',   sub_phone: '+34 655 005 005' },
];

// ── Códigos individuales por cartel (trazabilidad) ────────────────────────
const CLIENTES_DEMO = ['María García','Carlos Herrera','Ana Soto','Pedro López','Laura Martínez','Juan Pérez','Sara Gómez'];
const PAT_PREFIXES  = ['APL','ZAR','KIK','MAR','HOT','BOK','GRN','RES','ELC','SAL'];
const FECHAS_USO    = ['2026-04-28','2026-04-30','2026-05-01','2026-05-02','2026-05-05','2026-05-06'];

function _sampleCodigos(cartelId, usados, pendientes) {
    const result = [];
    const seed = cartelId.replace(/[^A-Z0-9]/g,'');
    // Usados (máx 6 en demo, resto contados)
    const mU = Math.min(usados, 6);
    for (let i = 0; i < mU; i++) {
        const p = PAT_PREFIXES[i % PAT_PREFIXES.length];
        result.push({
            cod_id:    `${p}-${seed}${String(i+1).padStart(3,'0')}`,
            patron:     p,
            estado:    'usado',
            cliente:   CLIENTES_DEMO[i % CLIENTES_DEMO.length],
            fecha_uso: FECHAS_USO[i % FECHAS_USO.length],
            generado:  'auto',
            fecha_gen: '2026-02-15',
        });
    }
    // Disponibles (máx 4 en demo)
    const mD = Math.min(pendientes, 4);
    for (let i = 0; i < mD; i++) {
        const p = PAT_PREFIXES[(i+3) % PAT_PREFIXES.length];
        result.push({
            cod_id:    `${p}-${seed}D${String(i+1).padStart(2,'0')}`,
            patron:     p,
            estado:    'disponible',
            cliente:   null,
            fecha_uso: null,
            generado:  'auto',
            fecha_gen: '2026-02-15',
        });
    }
    return result;
}

// Genera 3 carteles por tienda → 15 carteles totales
function _buildDemoCarteles() {
    const posiciones = ['A', 'B', 'C'];
    const ubicaciones = ['Barra principal', 'Mesa exterior', 'Puerta entrada'];
    const resultados = [];
    const ventas = [
        // T01 [A,B,C] — Chamberí (buen rendimiento)
        [45, 32, 12],  [38, 28, 7],   [52, 40, 19],
        // T02 [A,B,C] — Malasaña (rendimiento medio)
        [28, 18, 5],   [33, 22, 9],   [20, 14, 3],
        // T03 [A,B,C] — Lavapiés (rendimiento bajo)
        [15,  8, 2],   [22, 12, 4],   [10,  5, 1],
        // T04 [A,B,C] — Retiro (rendimiento muy bueno)
        [60, 48, 24],  [55, 42, 21],  [70, 56, 31],
        // T05 [A,B,C] — Moncloa (rendimiento medio-alto)
        [40, 30, 10],  [35, 25, 8],   [42, 32, 12],
    ];
    let idx = 0;
    for (const t of DEMO_TIENDAS) {
        for (let i = 0; i < 3; i++) {
            const pos = posiciones[i];
            const v   = ventas[idx++] || [0, 0, 0];
            const cargados = v[0], usados = v[1], patron_usados = v[2];
            resultados.push({
                id:         `CAR-${t.id}-${pos}`,
                codigo:     `QR-${t.id}-${pos}-2026`,
                tienda_id:  t.id,
                tienda:     t.nombre,
                zona:       t.zona,
                sub_id:     t.sub_id,
                sub_name:   t.sub_name,
                sub_email:  t.sub_email,
                sub_phone:  t.sub_phone,
                ubicacion:  ubicaciones[i],
                posicion:   pos,
                activo:     true,
                cargados,
                usados,
                pendientes: cargados - usados,
                tasa:       cargados ? Math.round((usados / cargados) * 100) : 0,
                // Desglose por patrocinador (simplificado para demo)
                pat_stats: PATROCINADORES_INIT.map(p => ({
                    pat_num:  p.num,
                    pat_obj:  p.obj,
                    prefix:   p.cod_prefix,
                    vendidos: p.cargados > 0 ? Math.round((usados / 10) * (p.usados / (p.cargados || 1))) : 0,
                    usados:   p.cargados > 0 ? Math.round((patron_usados / 10)) : 0,
                })),
                ultimo_scan:   '2026-05-06',
                fecha_alta:    '2026-02-15',
                generado_auto: true,
                codigos: _sampleCodigos(`CAR-${t.id}-${pos}`, usados, cargados - usados),
                total_usados_real: usados,
                total_disp_real:   cargados - usados,
            });
        }
    }
    return resultados;
}

const DEMO_CARTELES = _buildDemoCarteles();

// COL demo
const DEMO_COL = {
    id: 'COL-001', name: 'Bar La Copa S.L.', cif: 'B-12345678',
    email: 'info@barlacopa.es', phone: '+34 915 000 111',
    commission_pct: 45, iban: 'ES91 2100 0418 4502 0005 1332',
};

function computeKPIs(pats) {
    const totalCodigos    = pats.reduce((s, p) => s + p.cargados, 0);
    const totalUsados     = pats.reduce((s, p) => s + p.usados, 0);
    const totalPendientes = totalCodigos - totalUsados;
    const tasaUso         = totalCodigos ? Math.round((totalUsados / totalCodigos) * 100) : 0;
    const patsConCodigos  = pats.filter(p => p.cargados > 0).length;
    const allPatsLoaded   = patsConCodigos === pats.length;
    return { totalCodigos, totalUsados, totalPendientes, tasaUso, patsConCodigos, allPatsLoaded };
}

// ─────────────────────────────────────────────────────────────────────────────
export class CuponesView extends Component {
    static template = "promocionesred_dashboard.CuponesView";

    setup() {
        this.orm = useService("orm");
        const kpis = computeKPIs(PATROCINADORES_INIT);
        this.state = useState({
            // Tabs
            activeTab: "banco",
            // Tab 1
            patrocinadores: PATROCINADORES_INIT.map(p => ({ ...p })),
            uploadModal:    null,
            uploadText:     "",
            ...kpis,
            // Tab 2
            clientes:         DEMO_CLIENTES,
            clienteExpanded:  null,
            searchCli:        "",
            // Tab 3: PDV
            carteles:         DEMO_CARTELES,
            col:              DEMO_COL,
            tiendas:          DEMO_TIENDAS,
            pdvFiltroTienda:  "all",
            pdvFiltroSub:     "all",
            pdvFiltroZona:    "all",
            pdvFiltroActivo:  "all",
            pdvSearch:        "",
            pdvCartelOpen:    null,
            // Árbol jerárquico
            expandedTiendas:  {},
            expandedCarteles: {},
            cartelCodFilter:  {},
            // General
            searchQuery:      "",
        });
        onWillStart(async () => { await this._loadCupones(); });
    }

    // ── ORM ───────────────────────────────────────────────────────────────
    async _loadCupones() {
        try {
            const rows = await this.orm.call("pr.cupon", "get_cupones_data", [], {});
            if (rows && rows.length > 0) {
                const clientesOdoo = this._mapOdooToClientes(rows);
                this.state.clientes = [...DEMO_CLIENTES, ...clientesOdoo];
            }
        } catch (e) {
            console.warn("[CuponesView] ORM no disponible, usando datos demo:", e.message);
        }
    }

    _mapOdooToClientes(rows) {
        const byUser = {};
        for (const c of rows) {
            const key = c.user_email;
            if (!byUser[key]) {
                byUser[key] = { id: 'odoo_' + key, user_name: c.user_name || c.user_email, user_email: c.user_email, user_phone: c.user_phone || '', orden: c.cupon_code, pack: c.pack_code || 'PTK', fecha_compra: c.created_at ? c.created_at.split('T')[0] : '', cupones: [], sorteo_code: c.cupon_code, own_hash: c.own_hash || '', col_name: '', sub_name: '', cartel_id: '', zona: '' };
            }
            byUser[key].cupones.push({ pat_num: 99, pat_nombre: c.pack_name || 'Pack General', codigo: c.cupon_code, usado: c.status === 'used', fecha_uso: c.used_at ? c.used_at.split('T')[0] : undefined });
        }
        return Object.values(byUser);
    }

    // ── GETTERS — Tab 2 ───────────────────────────────────────────────────
    // IMPORTANTE: getter del componente, NO de state (evita OwlError filteredClientes)
    get filteredClientes() {
        const q = (this.state.searchCli || "").toLowerCase();
        if (!q) return this.state.clientes;
        return this.state.clientes.filter(c =>
            c.user_name.toLowerCase().includes(q) ||
            c.user_email.toLowerCase().includes(q) ||
            c.orden.toLowerCase().includes(q)
        );
    }

    // ── GETTERS — Tab 3 ───────────────────────────────────────────────────
    get filteredCarteles() {
        let lista = this.state.carteles;
        if (this.state.pdvFiltroTienda !== "all")
            lista = lista.filter(c => c.tienda_id === this.state.pdvFiltroTienda);
        if (this.state.pdvFiltroSub !== "all")
            lista = lista.filter(c => c.sub_id === this.state.pdvFiltroSub);
        if (this.state.pdvFiltroZona !== "all")
            lista = lista.filter(c => c.zona === this.state.pdvFiltroZona);
        if (this.state.pdvFiltroActivo === "activo")
            lista = lista.filter(c => c.activo);
        if (this.state.pdvFiltroActivo === "inactivo")
            lista = lista.filter(c => !c.activo);
        if (this.state.pdvSearch) {
            const q = this.state.pdvSearch.toLowerCase();
            lista = lista.filter(c =>
                c.codigo.toLowerCase().includes(q) ||
                c.tienda.toLowerCase().includes(q) ||
                c.sub_name.toLowerCase().includes(q) ||
                c.zona.toLowerCase().includes(q)
            );
        }
        return lista;
    }

    get pdvKPIs() {
        const c = this.state.carteles;
        const totalVendidos  = c.reduce((s, x) => s + x.cargados, 0);
        const totalUsados    = c.reduce((s, x) => s + x.usados, 0);
        const totalPendiente = c.reduce((s, x) => s + x.pendientes, 0);
        const tasaGlobal     = totalVendidos ? Math.round((totalUsados / totalVendidos) * 100) : 0;
        const mejorCartel    = [...c].sort((a, b) => b.usados - a.usados)[0];
        const mejorSub       = this._mejorSub();
        const cartelesActivos = c.filter(x => x.activo).length;
        return { totalVendidos, totalUsados, totalPendiente, tasaGlobal, mejorCartel, mejorSub, cartelesActivos, totalCarteles: c.length };
    }

    _mejorSub() {
        const porSub = {};
        for (const c of this.state.carteles) {
            if (!porSub[c.sub_id]) porSub[c.sub_id] = { sub_name: c.sub_name, usados: 0 };
            porSub[c.sub_id].usados += c.usados;
        }
        return Object.values(porSub).sort((a, b) => b.usados - a.usados)[0] || { sub_name: '—', usados: 0 };
    }

    get zonasUnicas() {
        return [...new Set(this.state.carteles.map(c => c.zona))];
    }

    get subsUnicos() {
        return [...new Set(this.state.carteles.map(c => c.sub_id))]
            .map(id => this.state.carteles.find(c => c.sub_id === id))
            .map(c => ({ id: c.sub_id, name: c.sub_name }));
    }

    cartelOpenData() {
        if (!this.state.pdvCartelOpen) return null;
        return this.state.carteles.find(c => c.id === this.state.pdvCartelOpen) || null;
    }

    tasaColor(tasa) {
        if (tasa >= 70) return '#059669';
        if (tasa >= 40) return '#d97706';
        return '#dc2626';
    }

    tasaClass(tasa) {
        if (tasa >= 70) return 'pr_badge_green';
        if (tasa >= 40) return 'pr_badge_amber';
        return 'pr_badge_red';
    }

    // ── HANDLERS ─────────────────────────────────────────────────────
    setTab(tab)  { this.state.activeTab = tab; }
    toggleCliente(id) { this.state.clienteExpanded = this.state.clienteExpanded === id ? null : id; }
    openUploadModal(num) { this.state.uploadModal = num; this.state.uploadText = ""; }
    closeUploadModal()   { this.state.uploadModal = null; this.state.uploadText = ""; }
    openCartelModal(id)  { this.state.pdvCartelOpen = id; }
    closeCartelModal()   { this.state.pdvCartelOpen = null; }

    // Árbol jerárquico
    toggleTienda(id) {
        const cur = { ...this.state.expandedTiendas };
        cur[id] = !cur[id];
        this.state.expandedTiendas = cur;
    }
    toggleCartel(id) {
        const cur = { ...this.state.expandedCarteles };
        cur[id] = !cur[id];
        this.state.expandedCarteles = cur;
    }
    setCartelCodFilter(cartelId, filter) {
        const cur = { ...this.state.cartelCodFilter };
        cur[cartelId] = filter;
        this.state.cartelCodFilter = cur;
    }
    cartelesOf(tiendaId) {
        return this.state.carteles.filter(c => c.tienda_id === tiendaId);
    }
    codigosOf(cartel) {
        const f = this.state.cartelCodFilter[cartel.id] || 'todos';
        if (f === 'usado')      return cartel.codigos.filter(c => c.estado === 'usado');
        if (f === 'disponible') return cartel.codigos.filter(c => c.estado === 'disponible');
        return cartel.codigos;
    }
    codFilterLabel(cartelId) { return this.state.cartelCodFilter[cartelId] || 'todos'; }

    setPdvFiltroTienda(ev) { this.state.pdvFiltroTienda = ev.target.value; }
    setPdvFiltroSub(ev)    { this.state.pdvFiltroSub    = ev.target.value; }
    setPdvFiltroZona(ev)   { this.state.pdvFiltroZona   = ev.target.value; }
    setPdvFiltroActivo(ev) { this.state.pdvFiltroActivo = ev.target.value; }
    setPdvSearch(ev)       { this.state.pdvSearch       = ev.target.value; }

    autoGenerate(num, qty) {
        const pat = this.state.patrocinadores.find(p => p.num === num);
        if (!pat) return;
        pat.cargados += qty;
        this._recalcKPIs();
    }

    autoGenerateModal(num, qty) { this.autoGenerate(num, qty); }

    uploadCodes(num) {
        const lines = this.state.uploadText.split("\n").map(l => l.trim()).filter(Boolean);
        if (!lines.length) return;
        const pat = this.state.patrocinadores.find(p => p.num === num);
        if (!pat) return;
        pat.cargados += lines.length;
        this._recalcKPIs();
        this.closeUploadModal();
    }

    _recalcKPIs() {
        const kpis = computeKPIs(this.state.patrocinadores);
        Object.assign(this.state, kpis);
    }

    toggleCartelActivo(id) {
        const c = this.state.carteles.find(x => x.id === id);
        if (c) c.activo = !c.activo;
    }

    fmt(n) { return (n || 0).toLocaleString("es-ES"); }
    fmtEur(n) { return (n || 0).toLocaleString("es-ES", { style: "currency", currency: "EUR" }); }
}

export const PrCuponesView = CuponesView;
