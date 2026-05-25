/** @odoo-module **/
/**
 * cartel_data.js
 * Equivalente al defaultData de React + useDesign hook.
 * Provee el estado inicial y los métodos de mutación en OWL.
 */

export const DEFAULT_FORMATS = {
    a4_v2:        { name: "A4 Vertical V2",    width: "210mm",  height: "297mm",  layout: "vertical-stack" },
    a4_v1:        { name: "A4 Vertical V1",    width: "210mm",  height: "297mm",  layout: "compact-grid" },
    square_50:    { name: "50x50 CM Cuadrado", width: "500mm",  height: "500mm",  layout: "grid-2x2" },
    banner_150_50:{ name: "Banner 150x50 CM",  width: "1500mm", height: "500mm",  layout: "horizontal-banner" },
    poster_70_100:{ name: "Poster 70x100 CM",  width: "700mm",  height: "1000mm", layout: "large-format" },
};

export const DEFAULT_DESIGN = {
    active_format: "a4_v2",
    formats: DEFAULT_FORMATS,
    content: {
        brand: "PremiosRed.com",
        promo_title: "GRAN PROMOCIÓN DE PREMIOS EXCLUSIVOS",
        promo_subtitle: "Y PARTICIPA EN EL SORTEO DE 20.000 €",
        solidarity_text: '"Producto Solidario: Donamos 0,10€ por ticket a la lucha contra el Cáncer"',
        qr_url: "https://premiosred.com",
        legal_text: "Promoción de combinación aleatoria con fines publicitarios, excluida del ámbito del juego conforme a la Ley 13/2011. El importe satisfecho corresponde exclusivamente a la adquisición de un cupón de ahorro, IVA incluido, que incorpora beneficios económicos reales (ahorro en combustible y 2 noches de hotel para 2 personas en régimen de solo alojamiento), conforme a las condiciones de cada pack. Sorteo ante notario el 22/12/2026 a las 12:00 h. Bases legales en www.premiosred.com. Prohibida la venta y participación a menores de 18 años. Organiza REDGLOBAL S.L.",
        packs: [
            {
                id: "tech", name: "PACK TECNOLOGÍA", subtitle: "Y LO QUE TE AHORRAS SI LO COMPRAS",
                price: "6", color: "#f37021",
                items: [
                    "2 Códigos de Ahorro de (12 Cent € /L) en combustible en GALP.com",
                    "1 Bono de 2 Noches de hotel para 2 Pers (Solo Alojamiento gratuito).",
                    "1 Cupón Desc. Del 5% en Web/Tienda en APPLE.com",
                    "2 Participaciones gratis para el SORTEO de productos valorados en 3500 €."
                ],
                logo: "https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg"
            },
            {
                id: "fashion", name: "PACK MODA", subtitle: "",
                price: "7", color: "#4caf50",
                items: [
                    "3 Códigos de Ahorro de (12 Cent € /L) en combustible en GALP.com",
                    "2 Bonos de 2 Noches de hotel para 2 Pers (Solo Alojamiento gratuito).",
                    "1 Cupón Desc. Del 5% en Web/Tienda en ZARA.com",
                    "3 Participaciones gratis para el SORTEO de productos valorados en 4500 €."
                ],
                logo: "https://upload.wikimedia.org/wikipedia/commons/f/fd/Zara_Logo.svg"
            },
            {
                id: "cosmetic", name: "PACK COSMÉTICA", subtitle: "",
                price: "8", color: "#0071bc",
                items: [
                    "4 Códigos de Ahorro de (12 Cent € /L) en combustible en GALP.com",
                    "3 Bonos de 2 Noches de hotel para 2 Pers (Solo Alojamiento gratuito).",
                    "1 Cupón Desc. Del 5% en Web/Tienda en DRUNI.com",
                    "4 Participaciones gratis para el SORTEO de productos valorados en 5500 €."
                ],
                logo: "https://static.brand.druni.es/logo-druni.svg"
            },
            {
                id: "travel", name: "PACK CARIBE", subtitle: "Todo incluido 7 noches/9 días 2 pers",
                price: "9", color: "#ce1126",
                items: [
                    "5 Códigos de Ahorro de (12 Cent € /L) en combustible en GALP.com",
                    "4 Bonos de 2 Noches de hotel para 2 Pers (Solo Alojamiento gratuito).",
                    "1 Cupón Desc. Del 5% en Web/Tienda en RIU.com",
                    "5 Participaciones gratis para el SORTEO de productos valorados en 6500 €."
                ],
                logo: "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Riu_Hotels_%26_Resorts_logo.svg/1200px-Riu_Hotels_%26_Resorts_logo.svg.png"
            }
        ]
    },
    ui: {
        show_partner_logos: true,
        border_color: "#f37021",
        border_width: "0px",
        border_style: "solid",
        border_radius: "0px",
        show_security_border: false
    }
};

/**
 * Carga el diseño desde localStorage o usa el default.
 * Equivalente al useState(() => { const saved = localStorage... }) de React.
 */
export function loadDesign() {
    const STORAGE_KEY = 'cc_cartel_design_v1';
    try {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved) {
            const parsed = JSON.parse(saved);
            // Siempre fuerza formatos actualizados
            parsed.formats = DEFAULT_FORMATS;
            if (parsed.active_format === 'banner_50_150') parsed.active_format = 'banner_150_50';
            if (!parsed.ui) parsed.ui = { ...DEFAULT_DESIGN.ui };
            return parsed;
        }
    } catch (e) {
        console.warn('[CartelEditor] Error leyendo localStorage, usando default.', e);
    }
    return JSON.parse(JSON.stringify(DEFAULT_DESIGN));
}

/**
 * Persiste el diseño en localStorage.
 */
export function saveDesign(design) {
    const STORAGE_KEY = 'cc_cartel_design_v1';
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(design));
    } catch (e) {
        console.warn('[CartelEditor] Error guardando en localStorage.', e);
    }
}

/**
 * Genera un QR como Data URL usando QRious.js (sin dependencia de React).
 * @param {string} url - URL a codificar
 * @param {number} size - Tamaño en px
 * @returns {string} Data URL de la imagen PNG del QR
 */
export function generateQR(url, size = 110) {
    try {
        if (typeof window.QRious === 'undefined') {
            console.warn('[CartelEditor] QRious no está cargado.');
            return '';
        }
        const canvas = document.createElement('canvas');
        new window.QRious({
            element: canvas,
            value: url || 'https://premiosred.com',
            size: size,
            backgroundAlpha: 1,
            foreground: '#000000',
            background: '#ffffff',
            level: 'M'
        });
        return canvas.toDataURL('image/png');
    } catch (e) {
        console.error('[CartelEditor] Error generando QR:', e);
        return '';
    }
}
