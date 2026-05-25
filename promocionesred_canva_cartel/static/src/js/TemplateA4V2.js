/** @odoo-module **/
/**
 * TemplateA4V2.js — Conversión OWL del componente React TemplateA4V2.jsx
 * Plantilla A4 Vertical V2 (vertical-stack) con packs draggable.
 */
import { Component, useState, onMounted } from "@odoo/owl";
import { generateQR } from "./cartel_data";

export class TemplateA4V2 extends Component {
    static template = "cc_cartel.TemplateA4V2";
    static props = {
        content: Object,
        ui: Object,
        onReorderPacks: Function,
    };

    setup() {
        this.state = useState({ qrSrc: '' });
        this.dragSrc = -1;
        onMounted(() => this._refreshQR());
    }

    _refreshQR() {
        this.state.qrSrc = generateQR(this.props.content.qr_url, 110);
    }

    // Drag & Drop handlers — equivalentes a los de React
    onDragStart(ev, index) {
        this.dragSrc = index;
        ev.currentTarget.classList.add('dragging');
        ev.dataTransfer.effectAllowed = 'move';
    }

    onDragEnd(ev) {
        ev.currentTarget.classList.remove('dragging');
    }

    onDragOver(ev) {
        ev.preventDefault();
        ev.dataTransfer.dropEffect = 'move';
    }

    onDrop(ev, targetIndex) {
        ev.preventDefault();
        if (this.dragSrc !== -1 && this.dragSrc !== targetIndex) {
            this.props.onReorderPacks(this.dragSrc, targetIndex);
        }
        this.dragSrc = -1;
    }

    get packs() { return this.props.content.packs; }
    get qrSrc() { return this.state.qrSrc; }
    get showSecurity() { return this.props.ui?.show_security_border; }
}
