/** @odoo-module **/
/**
 * CartelSidebar.js
 * Conversión OWL del componente React Sidebar.jsx
 * Panel de edición lateral con secciones: Configuración, Contenido, Packs, Legal
 */
import { Component, useState } from "@odoo/owl";

export class CartelSidebar extends Component {
    static template = "cc_cartel.CartelSidebar";

    /** Props recibidas desde el editor padre (equivale a props de React) */
    static props = {
        design: Object,
        onUpdateContent: Function,
        onUpdateUI: Function,
        onUpdatePack: Function,
        onUpdatePackItem: Function,
        onChangeFormat: Function,
        onExport: Function,
    };

    setup() {
        this.state = useState({
            activeSection: 'general',  // 'general' | 'content' | 'packs' | 'legal'
            expandedPack: 0,           // índice del pack expandido
        });
    }

    // ── Delegadores al componente padre ──────────────────────────────────

    updateContent(field, value) {
        this.props.onUpdateContent(field, value);
    }

    updateUI(field, value) {
        this.props.onUpdateUI(field, value);
    }

    updatePack(index, field, value) {
        this.props.onUpdatePack(index, field, value);
    }

    updatePackItem(packIndex, itemIndex, value) {
        this.props.onUpdatePackItem(packIndex, itemIndex, value);
    }

    changeFormat(ev) {
        this.props.onChangeFormat(ev.target.value);
    }

    toggleSection(section) {
        this.state.activeSection = section;
    }

    togglePack(idx) {
        this.state.expandedPack = this.state.expandedPack === idx ? -1 : idx;
    }

    // ── Handlers de eventos UI ───────────────────────────────────────────

    onBorderColorChange(ev) { this.updateUI('border_color', ev.target.value); }
    onBorderWidthChange(ev) { this.updateUI('border_width', `${ev.target.value}px`); }
    onBorderStyleChange(ev) { this.updateUI('border_style', ev.target.value); }
    onBorderRadiusChange(ev) { this.updateUI('border_radius', `${ev.target.value}px`); }
    onSecurityBorderChange(ev) { this.updateUI('show_security_border', ev.target.checked); }
    onShowPartnersChange(ev) { this.updateUI('show_partner_logos', ev.target.checked); }

    onPromoTitleChange(ev) { this.updateContent('promo_title', ev.target.value); }
    onPromoSubtitleChange(ev) { this.updateContent('promo_subtitle', ev.target.value); }
    onSolidarityChange(ev) { this.updateContent('solidarity_text', ev.target.value); }
    onQrUrlChange(ev) { this.updateContent('qr_url', ev.target.value); }
    onLegalChange(ev) { this.updateContent('legal_text', ev.target.value); }

    onPackLogoChange(idx, ev) { this.updatePack(idx, 'logo', ev.target.value); }
    onPackNameChange(idx, ev) { this.updatePack(idx, 'name', ev.target.value); }
    onPackPriceChange(idx, ev) { this.updatePack(idx, 'price', ev.target.value); }
    onPackColorChange(idx, ev) { this.updatePack(idx, 'color', ev.target.value); }
    onPackSubtitleChange(idx, ev) { this.updatePack(idx, 'subtitle', ev.target.value); }
    onPackItemChange(packIdx, itemIdx, ev) { this.updatePackItem(packIdx, itemIdx, ev.target.value); }

    // ── Getters de estado ────────────────────────────────────────────────

    get design() { return this.props.design; }
    get formats() { return Object.entries(this.props.design.formats); }
    get packs() { return this.props.design.content.packs; }
    get borderWidthNum() { return parseInt(this.props.design.ui?.border_width || '0'); }
    get borderRadiusNum() { return parseInt(this.props.design.ui?.border_radius || '0'); }

    isPackExpanded(idx) { return this.state.expandedPack === idx; }
    isActiveSection(s) { return this.state.activeSection === s; }
}
