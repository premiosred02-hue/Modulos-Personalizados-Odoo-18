/** @odoo-module **/
// ── OnboardingView — Formularios de Alta de Actores ──────────────────────
// Migrado desde: D:\DEV\PREMIOSRED-PANEL-UNIFICADO\src\modules\05-onboarding\
// Equivalencias React → Owl aplicadas según REACT-A-OWL-ODOO.md

import { Component, useState, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

// ── Configuración de tipos de actor (equivalente a actors.ts) ────────────
const ACTOR_CONFIG = {
    COL: { label: 'Colaborador',          icon: '🏪', color: '#4f46e5', commission: '45% directa / 20% asistida', req: 'CIF + DNI Rep. + IBAN', desc: 'Punto de venta físico — bar, tienda, hotel, farmacia' },
    SUB: { label: 'Subcolaborador',        icon: '📱', color: '#059669', commission: '25% asistida',                req: 'DNI + IBAN',            desc: 'Fuerza de venta con QR móvil — propuesto por el COL' },
    CCP: { label: 'Captador Profesional',  icon: '🎯', color: '#d97706', commission: '3% pasivo',                  req: 'RETA + Certs AEAT/SS',  desc: 'Agente mercantil Ley 12/1992 — capta COLs profesionalmente' },
    COM: { label: 'Comercial B2B',         icon: '💼', color: '#7c3aed', commission: '2% pasivo',                  req: 'DNI + COL captado',     desc: 'Comercial B2B de REDROYAL — presenta COLs a la red' },
    ASE: { label: 'Asesor / Referido',     icon: '🤝', color: '#db2777', commission: '2% pasivo',                  req: 'DNI + IBAN',            desc: 'Conector / referido libre — el actor más sencillo' },
};
const ACTOR_TYPES = ['COL', 'SUB', 'CCP', 'COM', 'ASE'];
const KILL_SWITCH_DATE = new Date('2026-12-21T23:59:59');
const CRITICAL_RULES = [
    ['Solo 1 captador (CCP/COM/ASE) por COL — mutuamente excluyentes', '🔒'],
    ['REDROYAL SL paga directamente a TODOS los actores — ningún actor intermedia el pago', '💳'],
    ['El COL NUNCA puede ver el wallet ni el saldo del SUB (RBAC estanco)', '👁'],
    ['Prohibida la venta a menores de 18 años', '🔞'],
    ['Todas las comisiones cesan automáticamente el 21/12/2026 (Kill Switch)', '⚡'],
    ['Ningún checkbox RGPD puede estar pre-marcado (Art. 7 RGPD + Considerando 32)', '📋'],
];

// ── Formulario base vacío ─────────────────────────────────────────────────
function emptyForm(type) {
    return {
        actor_type: type,
        name: '', legal_name: '', tax_id: '',
        email: '', phone: '', address: '', municipio: '', provincia: '', cp: '',
        banco_titular: '', banco_nombre: '', banco_iban: '',
        fiscal_type: 'autonomo', fiscal_nss: '', fiscal_iae: '',
        parent_name: '', parent_code: '',
        // Consentimientos — NUNCA pre-marcados (Art. 7 RGPD)
        consent_titular: false, consent_contrato: false,
        consent_privacidad: false, consent_mayoria_edad: false,
        consent_comisiones: false, consent_rgpd: false,
    };
}

export class PrOnboardingView extends Component {
    static template = "promocionesred_dashboard.OnboardingView";
    static props = ["*"];

    setup() {
        this.orm          = useService("orm");
        this.notification = useService("notification");
        this.session      = session;

        this.state = useState({
            // Navegación
            activeView: 'dashboard',   // 'dashboard' | 'new-COL' | 'new-SUB' | ...
            // Datos
            actors: [],
            loading: true,
            saving: false,
            // Filtro tabla
            filterType: 'ALL',
            // Formulario activo
            form: {},
            // Countdown Kill Switch
            killSwitch: { days: 0, hours: 0, minutes: 0, seconds: 0 },
            // KPIs
            stats: { total: 0, activos: 0, pendientes: 0, cols: 0, subs: 0, ccps: 0, coms: 0, ases: 0 },
        });

        // Carga inicial de datos
        onWillStart(async () => {
            await this._fetchActors();
            await this._fetchStats();
        });

        // Kill Switch countdown
        onMounted(() => {
            this._ksInterval = setInterval(() => this._tickKillSwitch(), 1000);
            this._tickKillSwitch();
        });

        onWillUnmount(() => {
            clearInterval(this._ksInterval);
        });
    }

    // ── Kill Switch countdown ─────────────────────────────────────────────
    _tickKillSwitch() {
        const diff = KILL_SWITCH_DATE.getTime() - Date.now();
        if (diff <= 0) return;
        this.state.killSwitch = {
            days:    Math.floor(diff / 86400000),
            hours:   Math.floor((diff % 86400000) / 3600000),
            minutes: Math.floor((diff % 3600000) / 60000),
            seconds: Math.floor((diff % 60000) / 1000),
        };
    }

    // ── Datos ─────────────────────────────────────────────────────────────
    async _fetchActors() {
        this.state.loading = true;
        try {
            this.state.actors = await this.orm.searchRead(
                'pr.actor', [],
                ['id', 'code', 'actor_type', 'name', 'municipio', 'status', 'email', 'phone', 'create_date'],
                { order: 'create_date desc', limit: 50 }
            );
        } catch (e) {
            this.notification.add('Error al cargar actores: ' + e.message, { type: 'danger' });
        } finally {
            this.state.loading = false;
        }
    }

    async _fetchStats() {
        try {
            this.state.stats = await this.orm.call('pr.actor', 'get_onboarding_stats', []);
        } catch (_) {
            // Calcular localmente como fallback
            const a = this.state.actors;
            this.state.stats = {
                total:      a.length,
                activos:    a.filter(x => x.status === 'ACTIVO').length,
                pendientes: a.filter(x => x.status === 'PENDIENTE').length,
                cols:       a.filter(x => x.actor_type === 'COL').length,
                subs:       a.filter(x => x.actor_type === 'SUB').length,
                ccps:       a.filter(x => x.actor_type === 'CCP').length,
                coms:       a.filter(x => x.actor_type === 'COM').length,
                ases:       a.filter(x => x.actor_type === 'ASE').length,
            };
        }
    }

    // ── Navegación ────────────────────────────────────────────────────────
    openForm(type) {
        this.state.form = emptyForm(type);
        this.state.activeView = `new-${type}`;
    }

    backToDashboard() {
        this.state.activeView = 'dashboard';
        this.state.form = {};
    }

    setFilter(type) {
        this.state.filterType = type;
    }

    // ── Guardar actor ─────────────────────────────────────────────────────
    async saveActor() {
        const f = this.state.form;

        // Validación mínima
        if (!f.name?.trim()) {
            this.notification.add('El nombre es obligatorio.', { type: 'warning' });
            return;
        }
        if (!f.consent_privacidad || !f.consent_mayoria_edad || !f.consent_comisiones) {
            this.notification.add('Debe aceptar todos los consentimientos RGPD obligatorios.', { type: 'warning' });
            return;
        }

        this.state.saving = true;
        try {
            const vals = {
                actor_type:    f.actor_type,
                name:          f.name,
                legal_name:    f.legal_name || false,
                tax_id:        f.tax_id || false,
                email:         f.email || false,
                phone:         f.phone || false,
                address:       f.address || false,
                municipio:     f.municipio || false,
                provincia:     f.provincia || false,
                cp:            f.cp || false,
                banco_titular: f.banco_titular || false,
                banco_nombre:  f.banco_nombre || false,
                banco_iban:    f.banco_iban ? f.banco_iban.replace(/\s/g, '').toUpperCase() : false,
                fiscal_type:   f.fiscal_type || false,
                fiscal_nss:    f.fiscal_nss || false,
                status:        'PENDIENTE',
                zone:          f.provincia ? f.provincia.slice(0, 3).toUpperCase() : false,
                consent_log:   JSON.stringify({
                    privacidad:    f.consent_privacidad ? new Date().toISOString() : null,
                    mayoria_edad:  f.consent_mayoria_edad ? new Date().toISOString() : null,
                    comisiones:    f.consent_comisiones ? new Date().toISOString() : null,
                    titular:       f.consent_titular ? new Date().toISOString() : null,
                    contrato:      f.consent_contrato ? new Date().toISOString() : null,
                }),
            };

            await this.orm.create('pr.actor', [vals]);
            this.notification.add(
                `✅ ${ACTOR_CONFIG[f.actor_type].label} registrado correctamente. Estado: PENDIENTE de activación.`,
                { type: 'success' }
            );
            this.backToDashboard();
            await this._fetchActors();
            await this._fetchStats();
        } catch (e) {
            this.notification.add('Error al guardar: ' + e.message, { type: 'danger' });
        } finally {
            this.state.saving = false;
        }
    }

    // ── Activar actor ─────────────────────────────────────────────────────
    async activarActor(id) {
        try {
            await this.orm.call('pr.actor', 'action_activar', [[id]]);
            this.state.actors = this.state.actors.map(a =>
                a.id === id ? { ...a, status: 'ACTIVO' } : a
            );
            await this._fetchStats();
            this.notification.add('Actor activado correctamente.', { type: 'success' });
        } catch (e) {
            this.notification.add('Error al activar: ' + e.message, { type: 'danger' });
        }
    }

    // ── Getters de UI ─────────────────────────────────────────────────────
    get filteredActors() {
        const ft = this.state.filterType;
        return ft === 'ALL'
            ? this.state.actors
            : this.state.actors.filter(a => a.actor_type === ft);
    }

    get currentFormConfig() {
        const type = this.state.activeView.replace('new-', '');
        return ACTOR_CONFIG[type] || null;
    }

    get currentFormType() {
        return this.state.activeView.replace('new-', '');
    }

    getActorConfig(type) {
        return ACTOR_CONFIG[type] || {};
    }

    getCriticalRules() {
        return CRITICAL_RULES;
    }

    getActorTypes() {
        return ACTOR_TYPES;
    }

    padTime(n) {
        return String(n).padStart(2, '0');
    }

    // ── Handlers del formulario ───────────────────────────────────────────
    setFormField(field, ev) {
        const val = ev.target.type === 'checkbox' ? ev.target.checked : ev.target.value;
        this.state.form[field] = val;
    }
}
