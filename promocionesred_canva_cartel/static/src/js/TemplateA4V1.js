/** @odoo-module **/
/** TemplateA4V1.js — Plantilla A4 Vertical V1 (compact-grid con 2 columnas) */
import { Component, useState, onMounted } from "@odoo/owl";
import { generateQR } from "./cartel_data";

export class TemplateA4V1 extends Component {
    static template = "cc_cartel.TemplateA4V1";
    static props = { content: Object, ui: Object, onReorderPacks: Function };

    setup() {
        this.state = useState({ qrSrc: '' });
        onMounted(() => { this.state.qrSrc = generateQR(this.props.content.qr_url, 160); });
    }

    get packs() { return this.props.content.packs; }
    get qrSrc() { return this.state.qrSrc; }
}
