/** @odoo-module **/
/** TemplateBanner150_50.js — Plantilla Banner 150x50 CM horizontal */
import { Component, useState, onMounted } from "@odoo/owl";
import { generateQR } from "./cartel_data";

export class TemplateBanner150_50 extends Component {
    static template = "cc_cartel.TemplateBanner150_50";
    static props = { content: Object, ui: Object, onReorderPacks: Function };

    setup() {
        this.state = useState({ qrSrc: '' });
        onMounted(() => { this.state.qrSrc = generateQR(this.props.content.qr_url, 180); });
    }

    get packs() { return this.props.content.packs; }
    get qrSrc() { return this.state.qrSrc; }
}
