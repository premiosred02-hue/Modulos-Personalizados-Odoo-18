/** @odoo-module **/
// ⚠️ REGLA DE ORO #1: Esta línea debe ser la primera del archivo.

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

// Importar sub-componentes — Operaciones
import { PrDashboard } from "./components/Dashboard";
import { PrLeadForm } from "./components/LeadForm";
import { PrNetworkView } from "./components/NetworkView";
import { PrMyQRView } from "./components/MyQRView";
import { PrEmailManager } from "./components/EmailManager";
import { PrFinanceView } from "./components/FinanceView";
import { PrLegalView } from "./components/LegalView";
import { PrAuditView } from "./components/AuditView";
import { PrSecurityView } from "./components/SecurityView";
import { PrOnboardingView } from "./components/OnboardingView";
// Importar sub-componentes — Portal de Ventas
import { PrEmpresasView } from "./components/EmpresasView";
import { PrCuponesView } from "./components/CuponesView";
import { PrPromotoresView } from "./components/PromotoresView";
import { PrPacksView } from "./components/PacksView";

/**
 * DashboardApp — Componente raíz.
 * Equivalente al componente App() de React.
 * Gestiona la navegación entre pestañas y los datos globales (leads, network).
 */
class DashboardApp extends Component {
    // ⚠️ REGLA DE ORO #2: Coincide con t-name en app.xml
    static template = "promocionesred_dashboard.DashboardApp";

    // Sub-componentes registrados para QWeb
    static components = {
        PrDashboard,
        PrLeadForm,
        PrNetworkView,
        PrMyQRView,
        PrEmailManager,
        PrFinanceView,
        PrLegalView,
        PrAuditView,
        PrSecurityView,
        PrOnboardingView,
        // Portal de Ventas
        PrEmpresasView,
        PrCuponesView,
        PrPromotoresView,
        PrPacksView,
    };

    static props = ["*"]; // Acepta props de Odoo (action, resId, etc.)

    setup() {
        // ── Servicios ────────────────────────────────────────────
        this.orm = useService("orm");
        this.notification = useService("notification");
        // session expuesto al template QWeb (session.name, session.is_admin)
        this.session = session;
        this.isAdmin = session.is_admin || session.is_superuser || false;

        // ── Estado global de navegación ──────────────────────────
        // Equivalente a: const [activeTab, setActiveTab] = useState('dashboard')
        this.state = useState({
            activeTab: "dashboard",
            isMenuOpen: false,
            isLoading: true,
            leads: [],
            network: [],
            emailHistory: [],
            emailTemplates: [],
            stats: {
                conversionRate: 0,
                activeSponsors: 0,
                guaranteeFund: 0,
                totalRevenue: 0,
                matrixProfit: 0,
                networkPayout: 0,
            },
        });

        // ── Carga inicial de datos ───────────────────────────────
        // Equivalente a: useEffect(() => { fetchData() }, [])
        onWillStart(async () => {
            await this._fetchData();
        });
    }

    // ── Datos globales ───────────────────────────────────────────

    async _fetchData() {
        this.state.isLoading = true;
        try {
            // Leads vinculados desde la Pasarela Externa al CRM (Core Models)
            this.state.leads = await this.orm.searchRead(
                "crm.lead",
                [],
                ["id", "name", "email_from", "phone", "pr_encrypted_id", "pr_scan_count", "pr_custom_label", "pr_portal_type", "create_date"],
                { order: "create_date desc" }
            );

            // Red de colaboradores unificada en res.partner
            this.state.network = await this.orm.searchRead(
                "res.partner",
                [["pr_role", "in", ["company-admin", "promoter-admin"]]],
                ["id", "name", "email", "pr_role", "pr_commission_pct", "pr_is_promoter", "pr_entity_id"]
            );

            // Historial de correos
            this.state.emailHistory = await this.orm.searchRead(
                "pr.email.log",
                [],
                ["id", "lead_id", "recipient", "name", "category",
                 "subject", "sent_at", "views", "clicks", "country", "last_action"],
                { order: "sent_at desc" }
            );

            // Plantillas de correo
            this.state.emailTemplates = await this.orm.searchRead(
                "pr.email.template",
                [],
                ["id", "name", "subject", "body"]
            );

            // KPIs enlazados a CRM
            const stats = await this.orm.call("crm.lead", "search_count", [[]]);
            this.state.stats = { ...this.state.stats, totalRevenue: 0, activeSponsors: stats };

        } catch (e) {
            this.notification.add("Error al cargar datos: " + e.message, { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
    }

    // ── Navegación ───────────────────────────────────────────────

    setTab(tab) {
        this.state.activeTab = tab;
        this.state.isMenuOpen = false;
    }

    toggleMenu() {
        this.state.isMenuOpen = !this.state.isMenuOpen;
    }

    closeMenu() {
        this.state.isMenuOpen = false;
    }

    // ── Permisos por rol Odoo ────────────────────────────────────

    get userRole() {
        // Usa session.is_admin (disponible en todos los contextos de Odoo)
        if (this.isAdmin) return "ADM";
        return "ADM"; // Por defecto ADM — personalizar con grupos Odoo
    }

    canAccess(tab) {
        const role = this.userRole;
        if (role === "ADM") return true;
        const colTabs = ["dashboard", "leads", "network", "finance", "legal", "email"];
        const subTabs = ["dashboard", "leads", "my-qr", "finance", "email"];
        if (role === "COL") return colTabs.includes(tab);
        if (role === "SUB") return subTabs.includes(tab);
        return false;
    }

    // ── Operaciones CRUD Leads ───────────────────────────────────

    async addLead(data) {
        try {
            const newId = await this.orm.create("crm.lead", [data]);
            await this._fetchData();
            this.notification.add("Lead registrado correctamente.", { type: "success" });
            return true;
        } catch (e) {
            this.notification.add("Error al registrar lead: " + e.message, { type: "danger" });
            return false;
        }
    }

    async updateLead(id, data) {
        try {
            await this.orm.write("crm.lead", [id], data);
            await this._fetchData();
        } catch (e) {
            this.notification.add("Error al actualizar lead: " + e.message, { type: "danger" });
        }
    }

    async deleteLead(id) {
        try {
            await this.orm.unlink("crm.lead", [id]);
            this.state.leads = this.state.leads.filter(l => l.id !== id);
        } catch (e) {
            this.notification.add("Error al eliminar lead: " + e.message, { type: "danger" });
        }
    }

    // ── Operaciones CRUD Red ─────────────────────────────────────

    async addNetworkActor(data) {
        try {
            await this.orm.create("res.partner", [{...data, pr_role: 'company-admin'}]);
            await this._fetchData();
            this.notification.add("Actor de red registrado.", { type: "success" });
            return true;
        } catch (e) {
            this.notification.add("Error: " + e.message, { type: "danger" });
            return false;
        }
    }

    async updateNetworkActor(id, data) {
        try {
            await this.orm.write("res.partner", [id], data);
            await this._fetchData();
        } catch (e) {
            this.notification.add("Error: " + e.message, { type: "danger" });
        }
    }

    async deleteNetworkActor(id) {
        try {
            await this.orm.unlink("res.partner", [id]);
            this.state.network = this.state.network.filter(n => n.id !== id);
        } catch (e) {
            this.notification.add("Error: " + e.message, { type: "danger" });
        }
    }

    // ── Email ────────────────────────────────────────────────────

    async clearEmailHistory() {
        try {
            const ids = this.state.emailHistory.map(h => h.id);
            if (ids.length > 0) await this.orm.unlink("pr.email.log", ids);
            this.state.emailHistory = [];
            this.notification.add("Historial de correos eliminado.", { type: "success" });
        } catch (e) {
            this.notification.add("Error: " + e.message, { type: "danger" });
        }
    }

    async saveTemplate(tpl) {
        try {
            if (tpl.id) {
                await this.orm.write("pr.email.template", [tpl.id], tpl);
            } else {
                await this.orm.create("pr.email.template", [tpl]);
            }
            await this._fetchData();
            return true;
        } catch (e) {
            this.notification.add("Error al guardar plantilla: " + e.message, { type: "danger" });
            return false;
        }
    }
}

// ⚠️ REGLA DE ORO #3: Coincide con <field name="tag"> en actions.xml
registry.category("actions").add("promocionesred.DashboardApp", DashboardApp);
