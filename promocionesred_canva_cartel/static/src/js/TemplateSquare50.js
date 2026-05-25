/** @odoo-module **/
/** TemplateSquare50.js — Plantilla 50x50 CM cuadrado */
import { Component, useState, onMounted } from "@odoo/owl";
import { generateQR } from "./cartel_data";

export class TemplateSquare50 extends Component {
    static template = "cc_cartel.TemplateSquare50";
    static props = { content: Object, ui: Object, onReorderPacks: Function };

    setup() {
        this.state = useState({ qrSrc: '' });
        onMounted(() => { this.state.qrSrc = generateQR(this.props.content.qr_url, 150); });
    }

    get packs() { return this.props.content.packs; }
    get qrSrc() { return this.state.qrSrc; }
}
