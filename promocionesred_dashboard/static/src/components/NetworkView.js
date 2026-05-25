/** @odoo-module **/
import { Component, useState } from "@odoo/owl";

export class PrNetworkView extends Component {
    static template = "promocionesred_dashboard.PrNetworkView";
    static props = {
        network: Array,
        onAdd: Function,
        onUpdate: Function,
        onDelete: Function,
    };

    setup() {
        this.state = useState({
            editingId: null,
            editValues: {},
            showAddForm: false,
            searchTerm: "",
            viewMode: "list",
            newActor: {
                name: "", role: "2.6 SUB", parent_id: false,
                status: "Active", base_commission_pct: 30, override_commission_pct: 15,
            },
        });
    }

    get filteredNetwork() {
        const term = this.state.searchTerm.toLowerCase();
        if (!term) return this.props.network;
        return this.props.network.filter(a =>
            a.name.toLowerCase().includes(term) || a.role.toLowerCase().includes(term)
        );
    }

    get colNodes() {
        return this.props.network.filter(n => n.role === "2 COL");
    }

    getChildren(parentId) {
        return this.props.network.filter(n => n.parent_id && n.parent_id[0] === parentId);
    }

    startEditing(actor) {
        this.state.editingId = actor.id;
        this.state.editValues = { ...actor };
    }

    cancelEditing() { this.state.editingId = null; }

    async saveEdit() {
        const { parent_id, ...rest } = this.state.editValues;
        await this.props.onUpdate(this.state.editingId, {
            ...rest,
            parent_id: parent_id && parent_id[0] ? parent_id[0] : false,
        });
        this.state.editingId = null;
    }

    async handleDelete(id) {
        if (window.confirm("¿Eliminar este actor de la red?")) {
            await this.props.onDelete(id);
        }
    }

    async handleAddSubmit(ev) {
        ev.preventDefault();
        const data = { ...this.state.newActor };
        if (!data.parent_id) data.parent_id = false;
        const ok = await this.props.onAdd(data);
        if (ok) {
            this.state.showAddForm = false;
            this.state.newActor = {
                name: "", role: "2.6 SUB", parent_id: false,
                status: "Active", base_commission_pct: 30, override_commission_pct: 15,
            };
        }
    }

    onNewActorField(field, ev) {
        this.state.newActor = { ...this.state.newActor, [field]: ev.target.value };
    }

    onEditField(field, ev) {
        this.state.editValues = { ...this.state.editValues, [field]: ev.target.value };
    }
}
