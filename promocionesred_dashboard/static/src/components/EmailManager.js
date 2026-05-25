/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class PrEmailManager extends Component {
    static template = "promocionesred_dashboard.PrEmailManager";
    static props = {
        leads: Array,
        history: Array,
        templates: Array,
        onClearHistory: Function,
        onSaveTemplate: Function,
    };

    setup() {
        this.notification = useService("notification");
        this.state = useState({
            selectedLeadId: "",
            category: "COL",
            templateId: "",
            showEditor: false,
            editingTemplate: { name: "", subject: "", body: "" },
        });
    }

    get baseTemplates() {
        return [
            { id: "inv", name: "Invitación Inicial", subject: "Invitación Especial - Promociones Red", body: "Hola [NAME],\n\nTe invitamos a formar parte de nuestra red exclusiva de Sponsors...\n\n[LINK]" },
            { id: "rem", name: "Recordatorio Registro", subject: "Seguimos pensando en ti - Promociones Red", body: "Hola [NAME],\n\nNotamos que no terminaste tu registro...\n\n[LINK]" },
        ];
    }

    get allTemplates() {
        return [...this.baseTemplates, ...this.props.templates];
    }

    get currentTemplate() {
        return this.allTemplates.find(t => t.id == this.state.templateId) || this.allTemplates[0];
    }

    get totalViews() {
        return this.props.history.reduce((acc, h) => acc + (h.views || 0), 0);
    }

    get totalClicks() {
        return this.props.history.reduce((acc, h) => acc + (h.clicks || 0), 0);
    }

    get conversionRate() {
        if (!this.props.history.length) return "0.0";
        const converted = this.props.history.filter(h => h.clicks > 0).length;
        return ((converted / this.props.history.length) * 100).toFixed(1);
    }

    onSelectLead(ev) { this.state.selectedLeadId = ev.target.value; }
    onSelectCategory(ev) { this.state.category = ev.target.value; }
    onSelectTemplate(ev) { this.state.templateId = ev.target.value; }
    onTplField(field, ev) {
        this.state.editingTemplate = { ...this.state.editingTemplate, [field]: ev.target.value };
    }

    toggleEditor() {
        this.state.showEditor = !this.state.showEditor;
        this.state.editingTemplate = { name: "", subject: "", body: "" };
    }

    async saveTpl(ev) {
        ev.preventDefault();
        const ok = await this.props.onSaveTemplate(this.state.editingTemplate);
        if (ok) {
            this.state.showEditor = false;
            this.notification.add("Plantilla guardada correctamente.", { type: "success" });
        }
    }

    async clearHistory() {
        if (window.confirm("¿Eliminar TODO el historial de correos enviados?")) {
            await this.props.onClearHistory();
        }
    }

    // Nota: El envío real de Gmail requiere OAuth2 fuera del módulo Odoo.
    // Se puede integrar con mail.template de Odoo para envíos internos.
    sendEmail() {
        this.notification.add(
            "Integración Gmail: configura mail.outgoing.server en Odoo para envíos reales.",
            { type: "info" }
        );
    }
}
