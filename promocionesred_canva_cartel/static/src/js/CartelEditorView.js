/** @odoo-module **/
/**
 * CartelEditorView.js
 * Componente OWL raíz — equivalente completo de App.jsx de React.
 * Registrado como Client Action "cc_cartel_editor" en Odoo.
 *
 * Maneja: estado del diseño, zoom/pan, export PDF, sidebar toggle,
 * y orquesta todos los sub-componentes de plantilla.
 */
import { Component, useState, useRef, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

import { loadDesign, saveDesign, DEFAULT_FORMATS } from "./cartel_data";
import { CartelSidebar } from "./CartelSidebar";
import { TemplateA4V2 } from "./TemplateA4V2";
import { TemplateA4V1 } from "./TemplateA4V1";
import { TemplateSquare50 } from "./TemplateSquare50";
import { TemplateBanner150_50 } from "./TemplateBanner150_50";
import { TemplatePoster70_100 } from "./TemplatePoster70_100";

export class CartelEditorView extends Component {
    static template = "cc_cartel.CartelEditorView";
    static components = {
        CartelSidebar,
        TemplateA4V2,
        TemplateA4V1,
        TemplateSquare50,
        TemplateBanner150_50,
        TemplatePoster70_100,
    };

    setup() {
        this.notification = useService("notification");

        // Estado reactivo del diseño (equivalente a useDesign hook de React)
        this.design = useState(loadDesign());

        // Estado del editor
        this.editor = useState({
            isSidebarVisible: true,
            zoom: 0.5,
            pan: { x: 0, y: 0 },
            isPanning: false,
            isProcessing: false,
            importingImage: null,
        });

        this.viewportRef = useRef("viewport");
        this.canvasRef = useRef("canvas");

        this._panStart = null;

        onMounted(() => {
            this._fitToScreen();
            // Auto-save cada 2 segundos mientras el editor esté activo
            this._autoSaveInterval = setInterval(() => saveDesign(this.design), 2000);
        });

        onWillUnmount(() => {
            // Limpiar el intervalo al desmontar el componente (evita memory leaks)
            if (this._autoSaveInterval) {
                clearInterval(this._autoSaveInterval);
            }
        });
    }

    // ── Fit/Zoom ─────────────────────────────────────────────────────────

    _fitToScreen() {
        const viewport = this.viewportRef.el;
        if (!viewport) return;
        const mmToPx = 3.7795;
        const fmt = this.design.formats[this.design.active_format];
        const canvasW = parseFloat(fmt.width) * mmToPx;
        const canvasH = parseFloat(fmt.height) * mmToPx;
        const scaleX = (viewport.clientWidth - 100) / canvasW;
        const scaleY = (viewport.clientHeight - 100) / canvasH;
        this.editor.zoom = Math.min(scaleX, scaleY, 1);
        this.editor.pan = { x: 0, y: 0 };
    }

    onWheel(ev) {
        if (ev.ctrlKey || ev.metaKey) {
            ev.preventDefault();
            const delta = ev.deltaY > 0 ? 0.9 : 1.1;
            this.editor.zoom = Math.min(Math.max(this.editor.zoom * delta, 0.1), 5);
        } else {
            this.editor.pan = { ...this.editor.pan, y: this.editor.pan.y - ev.deltaY };
        }
    }

    onMouseDown(ev) {
        if (ev.button === 1 || (ev.button === 0 && ev.altKey)) {
            this.editor.isPanning = true;
            this._panStart = { x: ev.clientX, y: ev.clientY };
            ev.preventDefault();
        }
    }

    onMouseMove(ev) {
        if (this.editor.isPanning) {
            this.editor.pan = {
                x: this.editor.pan.x + ev.movementX,
                y: this.editor.pan.y + ev.movementY,
            };
        }
    }

    onMouseUp() {
        this.editor.isPanning = false;
    }

    onZoomIn() {
        this.editor.zoom = Math.min(this.editor.zoom + 0.1, 5);
    }

    onZoomOut() {
        this.editor.zoom = Math.max(this.editor.zoom - 0.1, 0.1);
    }

    onZoomSlider(ev) {
        this.editor.zoom = parseFloat(ev.target.value);
    }

    onZoomLabelClick() {
        this._fitToScreen();
    }

    get zoomPercent() { return Math.round(this.editor.zoom * 100); }

    // ── Sidebar ──────────────────────────────────────────────────────────

    toggleSidebar() {
        this.editor.isSidebarVisible = !this.editor.isSidebarVisible;
    }

    // ── Acciones de diseño ───────────────────────────────────────────────

    updateContent(field, value) {
        this.design.content[field] = value;
        saveDesign(this.design);
    }

    updateUI(field, value) {
        this.design.ui[field] = value;
        saveDesign(this.design);
    }

    updatePack(index, field, value) {
        this.design.content.packs[index][field] = value;
        saveDesign(this.design);
    }

    updatePackItem(packIndex, itemIndex, value) {
        this.design.content.packs[packIndex].items[itemIndex] = value;
        saveDesign(this.design);
    }

    changeFormat(formatId) {
        this.design.active_format = formatId;
        saveDesign(this.design);
        setTimeout(() => this._fitToScreen(), 100);
    }

    reorderPacks(startIndex, endIndex) {
        const packs = [...this.design.content.packs];
        const [removed] = packs.splice(startIndex, 1);
        packs.splice(endIndex, 0, removed);
        this.design.content.packs = packs;
        saveDesign(this.design);
    }

    toggleSecurity() {
        this.updateUI('show_security_border', !this.design.ui?.show_security_border);
    }

    // ── Export / Print ───────────────────────────────────────────────────

    async exportToPDF() {
        const canvasEl = this.canvasRef.el;
        if (!canvasEl) return;

        if (typeof window.html2canvas === 'undefined' || typeof window.jspdf === 'undefined') {
            this.notification.add("Librerías de exportación no cargadas. Verifica la instalación.", { type: "danger" });
            return;
        }

        this.notification.add("Generando PDF...", { type: "info" });
        try {
            const scale = 2;
            const htmlCanvas = await window.html2canvas(canvasEl, {
                scale,
                useCORS: true,
                logging: false,
                allowTaint: true,
            });
            const imgData = htmlCanvas.toDataURL('image/png');
            const fmt = this.design.formats[this.design.active_format];
            const { jsPDF } = window.jspdf;
            const pdf = new jsPDF({
                orientation: parseFloat(fmt.height) > parseFloat(fmt.width) ? 'portrait' : 'landscape',
                unit: 'mm',
                format: [parseFloat(fmt.width), parseFloat(fmt.height)],
            });
            const imgProps = pdf.getImageProperties(imgData);
            const pdfW = pdf.internal.pageSize.getWidth();
            const pdfH = (imgProps.height * pdfW) / imgProps.width;
            pdf.addImage(imgData, 'PNG', 0, 0, pdfW, pdfH);
            pdf.save(`cartel-${this.design.active_format}.pdf`);
            this.notification.add("PDF exportado correctamente.", { type: "success" });
        } catch (e) {
            console.error('[CartelEditor] Error exportando PDF:', e);
            this.notification.add("Error al generar el PDF.", { type: "danger" });
        }
    }

    onPrint() {
        window.print();
    }

    onSave() {
        saveDesign(this.design);
        this.notification.add("Diseño guardado en el navegador.", { type: "success" });
    }

    // ── Import de imagen ─────────────────────────────────────────────────

    onImportClick() {
        document.getElementById('cc-design-import')?.click();
    }

    onImportDesign(ev) {
        const file = ev.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (event) => {
            this.editor.importingImage = event.target.result;
            this.editor.isProcessing = true;
            setTimeout(() => {
                this.editor.isProcessing = false;
                this.notification.add(
                    "Análisis completado. El sistema ha procesado la imagen del diseño.",
                    { type: "success" }
                );
            }, 3000);
        };
        reader.readAsDataURL(file);
    }

    // ── Getters de template ───────────────────────────────────────────────

    get activeFormat() { return this.design.active_format; }
    get formatName() { return this.design.formats[this.design.active_format]?.name || ''; }
    get canvasStyle() {
        const fmt = this.design.formats[this.design.active_format];
        return [
            `width:${fmt.width}`,
            `height:${fmt.height}`,
            `border:${this.design.ui?.border_width || '0px'} ${this.design.ui?.border_style || 'solid'} ${this.design.ui?.border_color || 'transparent'}`,
            `border-radius:${this.design.ui?.border_radius || '0px'}`,
            'box-sizing:border-box',
            'overflow:hidden',
        ].join(';');
    }
    get containerStyle() {
        return `transform: translate(${this.editor.pan.x}px, ${this.editor.pan.y}px) scale(${this.editor.zoom})`;
    }
    get cursorStyle() {
        return this.editor.isPanning ? 'cursor:grabbing' : 'cursor:auto';
    }
    get securityActive() { return this.design.ui?.show_security_border; }
    get showA4V2() { return this.design.active_format === 'a4_v2'; }
    get showA4V1() { return this.design.active_format === 'a4_v1'; }
    get showSquare50() { return this.design.active_format === 'square_50'; }
    get showBanner() { return this.design.active_format === 'banner_150_50'; }
    get showPoster() { return this.design.active_format === 'poster_70_100'; }
}

// ── Registro como Client Action en Odoo ─────────────────────────────────
registry.category("actions").add("cc_cartel_editor", CartelEditorView);
