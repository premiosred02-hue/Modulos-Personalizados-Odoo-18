/** @odoo-module **/
import { Component, useState, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class PrSecurityView extends Component {
    static template = "promocionesred_dashboard.PrSecurityView";
    static props = { initialTab: { type: String, optional: true } };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            secTab: this.props.initialTab || "users",
            users: [],
            logs: [],
            newUser: { name: "", login: "", password: "" },
        });

        onMounted(async () => {
            await this._loadUsers();
            if (this.state.secTab === "movements") await this._loadLogs();
        });
    }

    async setSecTab(tab) {
        this.state.secTab = tab;
        if (tab === "movements") await this._loadLogs();
        else await this._loadUsers();
    }

    async _loadUsers() {
        // Usa el modelo nativo de Odoo res.users
        this.state.users = await this.orm.searchRead(
            "res.users",
            [["share", "=", false]],
            ["id", "name", "login", "groups_id"]
        );
    }

    async _loadLogs() {
        // Usa mail.message de Odoo como log de auditoría básico
        // Para logs completos, crear un modelo pr.audit.log adicional
        this.state.logs = await this.orm.searchRead(
            "mail.message",
            [["message_type", "=", "notification"]],
            ["id", "date", "author_id", "body", "subject"],
            { limit: 50, order: "date desc" }
        );
    }

    async handleCreateUser(ev) {
        ev.preventDefault();
        try {
            await this.orm.create("res.users", [{
                name: this.state.newUser.name,
                login: this.state.newUser.login,
                password: this.state.newUser.password,
            }]);
            this.notification.add("Usuario creado correctamente.", { type: "success" });
            this.state.newUser = { name: "", login: "", password: "" };
            await this._loadUsers();
        } catch (e) {
            this.notification.add("Error al crear usuario: " + e.message, { type: "danger" });
        }
    }

    onUserField(field, ev) {
        this.state.newUser = { ...this.state.newUser, [field]: ev.target.value };
    }

    formatDate(dateStr) {
        return dateStr ? new Date(dateStr).toLocaleString("es-ES") : "-";
    }
}
