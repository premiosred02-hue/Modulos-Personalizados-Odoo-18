/** @odoo-module **/
// PREMIOSRED -- FinanceView v3
// Replica EXACTA de: D:\Dev\PREMIOSRED-PANEL-UNIFICADO\src\modules\03-admin-empresas\views\FinanzasView.tsx
// Datos: vault 60.01 + 85.08 — Modelo 55/45 v1.2
import { Component, useState } from "@odoo/owl";

// ── Datos vault (identicos a FinanzasView.tsx) ──────────────────────────────
const PACKS = [
    { id: 'PTK', nombre: 'Pack Tecnologia',  pvp: 6 },
    { id: 'PMO', nombre: 'Pack Moda',        pvp: 7 },
    { id: 'PCO', nombre: 'Pack Cosmetica',   pvp: 8 },
    { id: 'PCA', nombre: 'Pack Calzado',     pvp: 9 },
];

const ACTORES_DIRECTA = [
    { actor: 'COL (directo)',       pct: 45, col: '#15803d' },
    { actor: 'CCP (captador)',      pct: 3,  col: '#d97706' },
    { actor: 'Donaciones',          pct: 2,  col: '#7c3aed' },
    { actor: 'REDROYAL disponible', pct: 50, col: '#4f46e5' },
];
const ACTORES_ASISTIDA = [
    { actor: 'COL (asistida)',      pct: 20, col: '#15803d' },
    { actor: 'SUB',                 pct: 25, col: '#059669' },
    { actor: 'ASE (captador)',      pct: 2,  col: '#d97706' },
    { actor: 'Donaciones',          pct: 2,  col: '#7c3aed' },
    { actor: 'REDROYAL disponible', pct: 51, col: '#4f46e5' },
];

const ESCENARIOS = [
    { ico: 'Pesimista',  packs: 20000,  ingreso: 150000,  rr_bruto: 82500,  rr_neto: 72000,  col: '#dc2626' },
    { ico: 'Moderado',   packs: 50000,  ingreso: 375000,  rr_bruto: 206250, rr_neto: 180000, col: '#d97706' },
    { ico: 'Objetivo',   packs: 100000, ingreso: 750000,  rr_bruto: 412500, rr_neto: 360000, col: '#15803d' },
    { ico: 'Optimo',     packs: 200000, ingreso: 1500000, rr_bruto: 825000, rr_neto: 720000, col: '#4f46e5' },
];

const BREAK_EVEN = [
    { packs: 500,   ingreso: 3750,  pool: 2063,  captadores: 75,   donaciones: 75,   disponible: 1913,  aeat: 6560, margen: -4647 },
    { packs: 1000,  ingreso: 7500,  pool: 4125,  captadores: 150,  donaciones: 150,  disponible: 3825,  aeat: 6560, margen: -2735 },
    { packs: 2000,  ingreso: 15000, pool: 8250,  captadores: 300,  donaciones: 300,  disponible: 7650,  aeat: 6560, margen: 1090  },
    { packs: 5000,  ingreso: 37500, pool: 20625, captadores: 750,  donaciones: 750,  disponible: 19125, aeat: 6560, margen: 12565 },
    { packs: 10000, ingreso: 75000, pool: 41250, captadores: 1500, donaciones: 1500, disponible: 38250, aeat: 6560, margen: 31690 },
];

const COSTES_FIJOS = [
    { concepto: 'Servidor AX52 PROD (Hetzner)',         categoria: 'Infraestructura', mes: 64,    anual: 768,    estado: 'pendiente'  },
    { concepto: 'Servidor AX42 STANDBY/DEV (Hetzner)',  categoria: 'Infraestructura', mes: 47,    anual: 564,    estado: 'pendiente'  },
    { concepto: 'Floating IP (Hetzner)',                 categoria: 'Infraestructura', mes: 2.5,  anual: 30,     estado: 'pendiente'  },
    { concepto: 'Object Storage backups (50GB)',         categoria: 'Infraestructura', mes: 1.15, anual: 13.8,   estado: 'pendiente'  },
    { concepto: 'Storage Box BX11 1TB',                  categoria: 'Infraestructura', mes: 3.81, anual: 45.72,  estado: 'pendiente'  },
    { concepto: 'Cloudflare (Free Fase 1)',               categoria: 'Infraestructura', mes: 0,    anual: 0,      estado: 'activo'     },
    { concepto: 'Odoo 18 Community',                     categoria: 'Licencias',       mes: 0,    anual: 0,      estado: 'activo'     },
    { concepto: 'SSL Let\'s Encrypt',                    categoria: 'Licencias',       mes: 0,    anual: 0,      estado: 'activo'     },
    { concepto: 'Desarrollador Core (autonomo)',         categoria: 'Personal',        mes: 1200, anual: 14400,  estado: 'planificado'},
    { concepto: 'Administrador/Contable (autonomo)',     categoria: 'Personal',        mes: 600,  anual: 7200,   estado: 'planificado'},
    { concepto: 'Impresion carteles COL (lote inicial)', categoria: 'Operativo',       mes: 150,  anual: 1800,   estado: 'planificado'},
    { concepto: 'Envio postal carteles',                 categoria: 'Operativo',       mes: 80,   anual: 960,    estado: 'planificado'},
    { concepto: 'Stripe (1.4%+0.25 EU) por 1000 ventas',categoria: 'Pagos',           mes: 93.65,anual: 1123.8, estado: 'variable'   },
    { concepto: 'SMS OTP post-pago x1000',               categoria: 'Pagos',           mes: 50,   anual: 600,    estado: 'variable'   },
    { concepto: 'WhatsApp entrega pack x1000',           categoria: 'Pagos',           mes: 70,   anual: 840,    estado: 'variable'   },
];

const CUENTAS = [
    { id:'A', nombre:'COBROS',   banco:'CaixaBank',         funcion:'Recibe pagos Stripe/Redsys/Bizum',             exposicion:'Internet',          color:'#dc2626', bg:'#fef2f2' },
    { id:'B', nombre:'GASTOS',   banco:'CaixaBank',         funcion:'Nominas, impuestos AEAT, provision IRPF',      exposicion:'Interna',           color:'#d97706', bg:'#fffbeb' },
    { id:'C', nombre:'REMESAS',  banco:'CaixaBank',         funcion:'SEPA masivo a COL/SUB/CCP/COM/ASE',            exposicion:'Interna saldo 0',   color:'#7c3aed', bg:'#faf5ff' },
    { id:'D', nombre:'RESERVAS', banco:'Banco secundario',  funcion:'Beneficio neto + fondo de maniobra',           exposicion:'Sin tarjetas',      color:'#15803d', bg:'#f0fdf4' },
];

const FISCAL = [
    { fecha:'Antes lanzamiento',  accion:'Modelo 685 (IAJ 2.000EUR)',                             responsable:'REDROYAL SL',          importe:2000, tipo:'pago'      },
    { fecha:'2026-07 / 10',       accion:'IVA trimestral packs digitales 21%',                    responsable:'Gestoria',             importe:0,    tipo:'trimestral'},
    { fecha:'2026-07 / 10',       accion:'IRPF retenciones autonomos Mod.111',                    responsable:'Gestoria',             importe:0,    tipo:'trimestral'},
    { fecha:'2026-12-22',         accion:'Sorteo notarial ante notario',                          responsable:'Luis Miguel Cantero',  importe:0,    tipo:'evento'    },
    { fecha:'Post-sorteo +20d',   accion:'IRPF ingreso cuenta ganadores Mod.111',                 responsable:'REDROYAL SL',          importe:3800, tipo:'pago'      },
    { fecha:'Enero 2027',         accion:'Declaracion anual consolidada + Mod.190',               responsable:'Gestoria',             importe:0,    tipo:'anual'     },
    { fecha:'Enero 2027',         accion:'Certificados fiscales actores COL/SUB/CCP',             responsable:'REDROYAL SL',          importe:0,    tipo:'anual'     },
];

// Helpers de formato
function fmtEur(n) { return n.toLocaleString('es-ES') + 'EUR'; }
function fmtNum(n) { return n.toLocaleString('es-ES'); }
function fmtFixed(n, d=2) { return n.toFixed(d); }

export class PrFinanceView extends Component {
    static template = "promocionesred_dashboard.PrFinanceView";
    static props = {};

    setup() {
        this.PACKS           = PACKS;
        this.ACTORES_DIRECTA = ACTORES_DIRECTA;
        this.ACTORES_ASISTIDA= ACTORES_ASISTIDA;
        this.ESCENARIOS      = ESCENARIOS;
        this.BREAK_EVEN      = BREAK_EVEN;
        this.COSTES_FIJOS    = COSTES_FIJOS;
        this.CUENTAS         = CUENTAS;
        this.FISCAL          = FISCAL;
        this.CATEGORIAS      = ['Infraestructura','Personal','Operativo','Licencias','Pagos'];
        this.CASH_SWEEP      = [
            { paso:'Paso 1', flujo:'A → C', desc:'Transferir comisiones COL/SUB/CCP al mismo dia', col:'#7c3aed' },
            { paso:'Paso 2', flujo:'A → B', desc:'Transferir gastos fijos + provision IRPF',       col:'#d97706' },
            { paso:'Paso 3', flujo:'A → D', desc:'Resto = beneficio neto a reservas',              col:'#15803d' },
        ];
        this.PROVISION_ITEMS = [
            { desc:'IAJ Modelo 685 (10% x 20.000EUR)',        val:'2.000EUR', cuando:'Antes del lanzamiento', col:'#dc2626' },
            { desc:'IRPF ingreso a cuenta ganadores 19%',     val:'3.800EUR', cuando:'Enero 2027',            col:'#dc2626' },
            { desc:'Provision extra seguridad',               val:'760EUR',   cuando:'Margen contingencia',   col:'#d97706' },
        ];

        this.state = useState({
            tab:       'reparto',   // 'reparto'|'proyecciones'|'costes'|'bancos'|'fiscal'
            pvpSel:    7,
            tipoVenta: 'directa',   // 'directa'|'asistida'
        });
    }

    // ── Helpers reactivos ───────────────────────────────────────────────────
    get actores()    { return this.state.tipoVenta === 'directa' ? ACTORES_DIRECTA : ACTORES_ASISTIDA; }
    get totalFijo()  { return COSTES_FIJOS.filter(c=>c.categoria!=='Pagos').reduce((s,c)=>s+c.mes,0); }
    get totalVar()   { return COSTES_FIJOS.filter(c=>c.categoria==='Pagos').reduce((s,c)=>s+c.mes,0); }

    costePorCat(cat) { return COSTES_FIJOS.filter(c=>c.categoria===cat); }
    totalCat(cat)    { return this.costePorCat(cat).reduce((s,c)=>s+c.mes,0); }

    eurosActor(actor) { return (this.state.pvpSel * actor.pct / 100).toFixed(2) + 'EUR'; }
    eurosPack(p, actor) { return (p.pvp * actor.pct / 100).toFixed(2) + 'EUR'; }

    // KPIs de cabecera
    get kpiInfra()   { return fmtFixed(COSTES_FIJOS.filter(c=>c.categoria==='Infraestructura').reduce((s,c)=>s+c.mes,0),2) + 'EUR/mes'; }
    get kpiPersonal(){ return fmtFixed(COSTES_FIJOS.filter(c=>c.categoria==='Personal').reduce((s,c)=>s+c.mes,0),0) + 'EUR/mes'; }
    get kpiVar()     { return fmtFixed(this.totalVar,2) + 'EUR/mes'; }

    // Colores estado costes
    estadoColor(e) { return e==='activo'?'#16a34a':e==='pendiente'?'#dc2626':e==='variable'?'#7c3aed':'#d97706'; }
    estadoBg(e)    { return e==='activo'?'#f0fdf4':e==='pendiente'?'#fef2f2':e==='variable'?'#faf5ff':'#fffbeb'; }

    // Colores tipo fiscal
    tipoColor(t)   { return t==='pago'?'#dc2626':t==='trimestral'?'#d97706':t==='evento'?'#4f46e5':'#6b7280'; }
    tipoBg(t)      { return t==='pago'?'#fef2f2':t==='trimestral'?'#fffbeb':t==='evento'?'#eff6ff':'#f9fafb'; }

    margenColor(m) { return m >= 0 ? '#16a34a' : '#dc2626'; }
    margenFmt(m)   { return (m>=0?'+':'') + fmtNum(m) + 'EUR'; }

    setTab(t)      { this.state.tab = t; }
    setPvp(pvp)    { this.state.pvpSel = pvp; }
    setTipo(t)     { this.state.tipoVenta = t; }

    // fmtEur para templates
    fmtNum(n) { return fmtNum(n); }
    fmtEur(n) { return fmtEur(n); }
    fmtFixed(n,d=2) { return fmtFixed(n,d); }
}
