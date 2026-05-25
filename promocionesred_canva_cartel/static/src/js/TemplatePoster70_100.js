/** @odoo-module **/
/** TemplatePoster70_100.js — Plantilla Poster 70x100 CM gran formato */
import { Component, useState, onMounted } from "@odoo/owl";
import { generateQR } from "./cartel_data";

export class TemplatePoster70_100 extends Component {
    static template = "cc_cartel.TemplatePoster70_100";
    static props = { content: Object, ui: Object, onReorderPacks: Function };

    setup() {
        this.state = useState({ qrSrc: '' });
        onMounted(() => { this.state.qrSrc = generateQR(this.props.content.qr_url, 200); });
    }

    get packs() { return this.props.content.packs; }
    get qrSrc() { return this.state.qrSrc; }
}
