/** @odoo-module **/
// ── PREMIOSRED — LegalView — Contratos y T&C por Actor ──────────────────
// Fuente: 30.01 CONTRATOS-B2B.md · 20.02 BASES-LEGALES.md · 20.03 TERMINOS-Y-CONDICIONES.md
import { Component, useState } from "@odoo/owl";

// ── Mapa de contratos por actor ──────────────────────────────────────────
const CONTRATOS = [
    {
        id: "col",
        code: "4-COL",
        label: "COL — Colaborador",
        icon: "🏪",
        version: "v2.3",
        color: "#4f46e5",
        bg: "rgba(79,70,229,0.08)",
        comision: "45% directa / 20% asistida",
        descripcion: "Punto de venta QR fijo en local físico. REDROYAL SL paga directamente.",
        partes: "REDROYAL SL (NIF: B26946517) + COL (persona física o jurídica con alta IAE)",
        marco_legal: "Código de Comercio · Código Civil · Art. 3.i Ley 13/2011",
        clausulas: [
            { titulo: "§0 — Fundamentación Jurídica", texto: "Combinación Aleatoria con Fines Publicitarios (Art. 3.i Ley 13/2011). NO requiere licencia DGOJ. Respaldada por TJUE C-304/08, C-261/07, C-540/08. REDROYAL asume Modelo 685 (IAJ 10%) y IRPF 19% del ganador. Depósito notarial ABACO." },
            { titulo: "§1 — Objeto", texto: "REDROYAL SL designa al COL como punto de distribución oficial de los Packs PremiosRed 2026. El COL coloca cartelería QR en su establecimiento. Relación mercantil — sin relación laboral." },
            { titulo: "§2 — Productos", texto: "Pack PTK «Recupera Tu Inversión Al Instante» · 6€ IVA incl. · Incluye: cupones de 8 patrocinadores + bono hotel 1-2 noches + cupón Booking.com 10% + 1 participación en sorteo de 40.000€ el 22/12/2026." },
            { titulo: "§3 — Cartelería y QR", texto: "QR Fijo: 45% comisión directa. QR Móvil SUB: 20% COL + 25% SUB. QR Global (digital/RRSS): 45% COL. Cesión de espacio gratuita. Permanencia mínima 3 meses desde instalación." },
            { titulo: "§4 — Comisiones", texto: "Venta directa QR Fijo: 45% del PVP (6€→2,70€ · 7€→3,15€ · 8€→3,60€ · 9€→4,05€). Venta asistida SUB: 20% COL + 25% SUB. Liquidación días 6-10 de cada mes por transferencia SEPA." },
            { titulo: "§5 — Obligaciones COL", texto: "✅ Cartelería visible y en buen estado. ✅ Verificar mayoría de edad clientes. ✅ Fotografías de instalación. ✅ Usar solo textos oficiales RRSS. ❌ NO modificar precios. ❌ NO cobrar efectivo. ❌ NO vender a menores. ❌ NO usar terminología DGOJ prohibida (lotería, rifa, apuesta)." },
            { titulo: "§8Q — Autofacturación KYC", texto: "Autofactura mensual por REDROYAL. Base = Comisión ÷ 1,21. Alta KYC: certificado IBAN + logotipo en 72h. Sin documentos en 15 días: resolución de pleno derecho." },
            { titulo: "§8V — Chargebacks", texto: "Comisiones ya liquidadas: INTOCABLES e irreclamables. Comisiones pendientes: se descuenta solo la venta afectada. Reserva interna REDROYAL: 1% de ingresos mensuales para chargebacks." },
            { titulo: "§10 — Vigencia", texto: "Hasta 21/12/2026 (Botón de Parada de Emergencia automático a las 23:59:59). Resolución voluntaria: preaviso 30 días. Rescisión anticipada (<3 meses): compensación 45€ salvo causas excluyentes. Causas de resolución inmediata: venta a menores, fraude, QR no autorizado." },
            { titulo: "§13 — No Competencia", texto: "Prohibido copiar el modelo de negocio durante vigencia + 12 meses posteriores. Sanción: 10.000€ + acciones Ley 3/1991. COL autoriza uso de nombre/logo en premiosred.com revocable con 30 días de preaviso." },
            { titulo: "§14 — Distribución Digital", texto: "QR Global solo compartible desde el Panel oficial. Textos RRSS inmutables. Penalizaciones: Nivel 1 (leve) → advertencia. Nivel 2 (grave) → expulsión + 500€ cláusula penal. Nivel 3 (daño grave) → expulsión + 2.000€ + acciones judiciales." },
        ],
        tabla_comisiones: [
            { pack: "PTK Tecnología", pvp: "6€", col_45: "2,70€", sub_25: "1,50€", col_asist: "1,20€" },
            { pack: "PTK Moda", pvp: "7€", col_45: "3,15€", sub_25: "1,75€", col_asist: "1,40€" },
            { pack: "PTK Cosmética", pvp: "8€", col_45: "3,60€", sub_25: "2,00€", col_asist: "1,60€" },
            { pack: "PTK Viaje Caribe", pvp: "9€", col_45: "4,05€", sub_25: "2,25€", col_asist: "1,80€" },
        ],
        kyb_docs: ["CIF/NIF del negocio", "Certificado Titularidad Bancaria (IBAN)", "Logotipo TIFF/PNG ≥300DPI", "Alta IAE / Mod. 036-037"],
    },
    {
        id: "sub",
        code: "5.1-SUB",
        label: "SUB — Subcolaborador",
        icon: "🧑‍💼",
        version: "v2.0",
        color: "#059669",
        bg: "rgba(5,150,105,0.08)",
        comision: "25% venta asistida",
        descripcion: "Fuerza de venta activa vinculada a un COL. QR móvil personal. REDROYAL paga directamente al SUB.",
        partes: "REDROYAL SL + COL vinculado + SUB (autónomo RETA o mercantil)",
        marco_legal: "Estatuto Trabajo Autónomo (L.20/2007) · Código Civil Art. 1544",
        clausulas: [
            { titulo: "§1 — Objeto", texto: "El SUB realiza venta activa de Packs PremiosRed usando su QR móvil personal en el establecimiento del COL. Actúa como fuerza de venta independiente con relación directa con REDROYAL SL. Vinculación 1:1 con un único COL." },
            { titulo: "§3 — Comisión", texto: "25% del PVP en venta asistida (su QR móvil). Liquidación días 6-10 de cada mes. REDROYAL SL paga DIRECTAMENTE al SUB — el dinero NUNCA pasa por el COL. Fuente de datos: registros plataforma (inapelables)." },
            { titulo: "§5 — QR Móvil", texto: "QR personal, intransferible, trazable e inalterable. 4 canales: presencial, cartel A4 imprimible, badge/lanyard, RRSS. Uso de QR ajeno = fraude grave → baja inmediata + pérdida comisiones." },
            { titulo: "§8 — Comisión Fija", texto: "La comisión es FIJA e INVARIABLE al 25% del PVP. No existen bonos, escalados ni incentivos adicionales de ningún tipo." },
            { titulo: "Blindaje Laboral (6 Reglas de Oro)", texto: "1. Sin órdenes del COL. 2. REDROYAL paga directamente al SUB. 3. Vinculación 1:1. 4. Sin horario fijo. 5. Usa su propio móvil. 6. Alta en RETA antes de iniciar actividad." },
            { titulo: "§10 — Vigencia", texto: "Hasta 21/12/2026. Preaviso resolución voluntaria: 7 días." },
        ],
        tabla_comisiones: [
            { pack: "PTK Tecnología", pvp: "6€", sub_25: "1,50€" },
            { pack: "PTK Moda", pvp: "7€", sub_25: "1,75€" },
            { pack: "PTK Cosmética", pvp: "8€", sub_25: "2,00€" },
            { pack: "PTK Viaje Caribe", pvp: "9€", sub_25: "2,25€" },
        ],
        kyb_docs: ["DNI/NIE", "IBAN personal", "Número Seguridad Social", "Alta RETA (si autónomo)"],
    },
    {
        id: "ccp",
        code: "1.1-CCP",
        label: "CCP — Captador Profesional",
        icon: "🎯",
        version: "v1.0",
        color: "#7c3aed",
        bg: "rgba(124,58,237,0.08)",
        comision: "3% pasivo sobre ventas del COL captado",
        descripcion: "Agente comercial profesional que capta COLs. Ley 12/1992 de Contrato de Agencia. Autónomo RETA obligatorio.",
        partes: "REDROYAL SL (El Principal) + CCP (Agente — Autónomo RETA o empresa)",
        marco_legal: "Ley 12/1992 del Contrato de Agencia · Código Mercantil",
        clausulas: [
            { titulo: "§1 — Objeto", texto: "El CCP capta establecimientos físicos (COLs) para la red PremiosRed. Identifica potenciales COLs, presenta el modelo, facilita el alta. El CCP NO puede cerrar contratos en nombre de REDROYAL SL." },
            { titulo: "§4 — Comisión (3%)", texto: "3% sobre PVP de TODAS las ventas del COL captado (directas + asistidas). Aplica mientras el COL esté activo hasta 21/12/2026. Facturas mensuales emitidas por el CCP antes del día 5." },
            { titulo: "§5 — Anti-Duplicidad", texto: "Un COL = un captador. El derecho lo adquiere el primero en registrar el alta en la plataforma (timestamp inapelable). La plataforma valida automáticamente unicidad por CIF/NIF." },
            { titulo: "§7 — Vigencia", texto: "Hasta 21/12/2026. No renovación automática. En nueva campaña: el CCP NO tiene derechos sobre COLs que renovaron; SÍ puede captar nuevos COLs; NO puede re-captar COLs de cartera anterior." },
            { titulo: "§9 — Indemnización por Clientela (Art. 28 L.12/1992)", texto: "Derecho potencial a indemnización si aportó COLs que continúan vendiendo y la extinción es ajena al CCP. Máximo: 1 año de comisiones promedio. Sin derecho si: incumplimiento del CCP, fin natural (Botón Parada), rescisión voluntaria." },
            { titulo: "Límite AML", texto: "Si comisión mensual supera 3.000€ sin historial justificado, REDROYAL puede solicitar documentación adicional o bloquear temporalmente el pago (Ley 10/2010 PBC)." },
        ],
        tabla_comisiones: [
            { pack: "PTK Tecnología", pvp: "6€", captador: "0,18€/venta" },
            { pack: "PTK Moda", pvp: "7€", captador: "0,21€/venta" },
            { pack: "PTK Cosmética", pvp: "8€", captador: "0,24€/venta" },
            { pack: "PTK Viaje Caribe", pvp: "9€", captador: "0,27€/venta" },
        ],
        kyb_docs: ["NIF/CIF", "IBAN", "Certificado alta RETA", "Certificado corriente AEAT", "Certificado corriente SS", "Mod. 036/037"],
    },
    {
        id: "com",
        code: "2.1-COM",
        label: "COM — Captador Corporativo",
        icon: "🏢",
        version: "v3.0",
        color: "#0891b2",
        bg: "rgba(8,145,178,0.08)",
        comision: "2% pasivo sobre ventas del COL captado",
        descripcion: "Captador pasivo B2B. SIN QR de venta. SIN contacto con usuarios finales. REDROYAL paga directamente.",
        partes: "REDROYAL SL + COM (persona jurídica o autónomo profesional)",
        marco_legal: "Ley 12/1992 · Código Mercantil",
        clausulas: [
            { titulo: "§ Objeto y Naturaleza", texto: "El COM capta nuevos COLs para la red PremiosRed recibiendo comisión pasiva del 2%. El COM NO realiza ventas directas. NO dispone de QR de venta. NO interactúa con usuarios finales. REDROYAL paga directamente al COM." },
            { titulo: "§ Comisión (2%)", texto: "2% sobre PVP de TODAS las ventas del COL captado (directas + asistidas). Liquidación el día 5 del mes siguiente. Factura mensual del COM (Base + IVA 21% + IRPF 15% si autónomo)." },
            { titulo: "§ Prohibición Absoluta", texto: "El COM NUNCA puede: tener QR de venta, vender packs directamente al público, cobrar en nombre de REDROYAL SL, intermediar pagos entre actores. Violación: rescisión inmediata + pérdida comisiones pendientes." },
            { titulo: "Argumentos de Captación", texto: "✅ «Si falla el patrocinador, REDROYAL devuelve el 100%» · ✅ «El cliente no paga impuestos del premio» · ✅ «Es legal — Combinación Aleatoria, no juego de azar» · ✅ «El COL no maneja dinero del cliente»" },
        ],
        tabla_comisiones: [
            { concepto: "500€ ventas COL/mes", com_2: "10,00€" },
            { concepto: "1.000€ ventas COL/mes", com_2: "20,00€" },
            { concepto: "5.000€ ventas COL/mes", com_2: "100,00€" },
            { concepto: "10.000€ ventas COL/mes", com_2: "200,00€" },
        ],
        kyb_docs: ["NIF/CIF", "IBAN", "Cartera de COLs potenciales", "Alta actividad económica"],
    },
    {
        id: "ase",
        code: "3.1-ASE",
        label: "ASE — Asesor Comercial Libre",
        icon: "🤝",
        version: "v1.0",
        color: "#d97706",
        bg: "rgba(217,119,6,0.08)",
        comision: "2% pasivo sobre ventas del COL captado",
        descripcion: "Intermediario informal que conecta COLs de su red personal. Sin obligación RETA. Sin exclusividad territorial.",
        partes: "REDROYAL SL + ASE (autónomo libre o persona física sin actividad)",
        marco_legal: "Código Civil Art. 1709 (mandato) · Código Mercantil (comisión)",
        clausulas: [
            { titulo: "§ Objeto", texto: "El ASE colabora en la captación de COLs presentando y vinculando potenciales COLs. Actúa como intermediario independiente sin exclusividad territorial, sin obligación de resultados mínimos, sin vínculo laboral." },
            { titulo: "§ Comisión (2%)", texto: "2% sobre PVP de TODAS las ventas del COL captado. Sin derecho a indemnización por clientela (a diferencia del CCP). Liquidación días 6-10 del mes siguiente." },
            { titulo: "§ Anti-Recaptación", texto: "Un COL, un captador. En nueva campaña: el ASE NO tiene derechos sobre el mismo COL captado anteriormente; SÍ puede captar nuevos COLs. Incumplimiento: resolución inmediata + pérdida comisiones." },
            { titulo: "§ Régimen Fiscal", texto: "Autónomo RETA: factura con IVA 21% + IRPF 15%. Persona física sin actividad: REDROYAL aplica retención fiscal correspondiente. Entidad mercantil: factura con IVA 21%." },
        ],
        tabla_comisiones: [
            { concepto: "500€ ventas COL/mes", ase_2: "10,00€" },
            { concepto: "1.000€ ventas COL/mes", ase_2: "20,00€" },
            { concepto: "5.000€ ventas COL/mes", ase_2: "100,00€" },
        ],
        kyb_docs: ["DNI/NIE/CIF", "IBAN", "Declaración condición fiscal (RETA / sin actividad / mercantil)"],
    },
    {
        id: "tc_b2c",
        code: "B2C",
        label: "T&C — Usuario Final (B2C)",
        icon: "📜",
        version: "v1.3",
        color: "#dc2626",
        bg: "rgba(220,38,38,0.06)",
        comision: "—",
        descripcion: "Términos y Condiciones del contrato con el usuario final. Regula la compra de Packs PremiosRed 2026.",
        partes: "REDROYAL SL (NIF: B26946517) + Usuario Final (≥18 años)",
        marco_legal: "TRLGDCU RDL 1/2007 · LSSI-CE Ley 34/2002 · RGPD 2016/679",
        clausulas: [
            { titulo: "§1 — Prestador", texto: "REDROYAL, S.L. · NIF: B26946517 · C/ Quemada 2-1°, 13730 Santa Cruz de Mudela (Ciudad Real) · info@premiosred.com · +34 652 940 284 · www.premiosred.com · RM Ciudad Real Prot. 394/2026" },
            { titulo: "§3 — Descripción del Servicio", texto: "Pack PTK «Recupera Tu Inversión Al Instante» (6€ IVA incl.): cupones de 8 patrocinadores + bono hotel 1-2 noches + cupón Booking.com 10% en 220+ países + participación accesoria y gratuita en sorteo de 40.000€." },
            { titulo: "§4 — Precios y Pago", texto: "Pack PTK: 6€ IVA incluido. Pago: tarjeta (Visa/MC/Amex) · Apple Pay · Google Pay. 3D Secure (SCA/PSD2). Procesado por Stripe y/o Redsys. REDROYAL NO almacena datos de tarjetas." },
            { titulo: "§6 — Desistimiento (Art. 103.m TRLGDCU)", texto: "El usuario RENUNCIA EXPRESAMENTE al derecho de desistimiento de 14 días al tratarse de contenido digital de acceso inmediato. Renuncia confirmada con checkbox obligatorio en el checkout. Excepción: Garantía Riesgo Cero si el contenido es defectuoso." },
            { titulo: "§9 — Sorteo", texto: "Fecha: 22/12/2026 a las 12:00h ante Notario. 1 único ganador del gran premio de 40.000€ (8 patrocinadores × 5.000€). REDROYAL asume IRPF 19% (9.383€) + IAJ 10% (4.000€). El ganador recibe el premio íntegro." },
            { titulo: "§10 — Garantía Riesgo Cero", texto: "Contenido no entregado: reenvío inmediato o reembolso 100%. Cupón no aceptado: sustitución o reembolso. Bono hotel no disponible: alternativa equivalente o reembolso. Reclamaciones: info@premiosred.com — máx. 48h respuesta." },
            { titulo: "§7 — Condiciones de Uso", texto: "Cupones: 1 solo uso, no acumulables, válidos hasta 31/12/2026. Bono hotel: 2 noches / 2 personas, mínimo 15 días antelación, hasta 31/12/2027. Booking.com: 10% descuento en 220+ países, hasta 31/12/2026." },
            { titulo: "§13 — Legislación y Disputas", texto: "Ley española aplicable. 1ª instancia: info@premiosred.com. 2ª: Plataforma ODR de la UE. 3ª: Juzgados y Tribunales del domicilio del consumidor." },
        ],
        tabla_comisiones: null,
        kyb_docs: null,
    },
    {
        id: "bases",
        code: "20.02",
        label: "Bases Legales — Campaña 2026",
        icon: "⚖️",
        version: "v2.0",
        color: "#374151",
        bg: "rgba(55,65,81,0.06)",
        comision: "—",
        descripcion: "Bases legales del sorteo «Gana con PremiosRed.com». Pendiente depósito notarial ABACO, Ciudad Real.",
        partes: "Organizador: REDROYAL SL · Participantes: compradores de Packs PTK ≥18 años",
        marco_legal: "Ley 13/2011 Art. 3.i · TRLGDCU · IRPF · RGPD · Ley 34/1988",
        clausulas: [
            { titulo: "§2 — Objeto de la Campaña", texto: "(1) Distribución de cupón gratuito (Marca Gancho Principal) al escanear QR. (2) Venta del Pack PTK «Recupera Tu Inversión Al Instante» por 6€ IVA incl. (3) Combinación Aleatoria (Art. 3.i Ley 13/2011) con sorteo de 40.000€ en especie." },
            { titulo: "§3 — Ámbito y Duración", texto: "Compra en territorio español. Consumo global (cobertura RCG: ≥17 mercados). Inicio: 01/08/2026 (pendiente). Cierre venta: 21/12/2026 23:59:59. Sorteo: 22/12/2026 12:00h ante Notario ABACO Ciudad Real." },
            { titulo: "§5 — Requisitos de Participación", texto: "≥18 años. Compra en España (o canal transporte autorizado). Dispositivo con cámara QR. Teléfono válido (OTP). Método de pago válido. Excluidos: trabajadores REDROYAL, colaboradores activos, empleados de patrocinadores." },
            { titulo: "§7 — Premio", texto: "1 ÚNICO GANADOR. 8 patrocinadores × 5.000€ en especie = 40.000€ TOTAL. + 3 suplentes. Los nombres definitivos se publican en www.premiosred.com cuando los contratos de patrocinio estén firmados." },
            { titulo: "§8 — Fiscalidad del Premio", texto: "IAJ Modelo 685: 10% × 40.000€ = 4.000€ (REDROYAL). IRPF ingreso a cuenta: 19% × base = 9.383€ (REDROYAL). PROVISIÓN TOTAL: 15.123€ (IAJ + IRPF + contingencia 1.740€). El ganador recibe el premio ÍNTEGRO." },
            { titulo: "§10 — Aceptación del Premio", texto: "El ganador tiene 15 días hábiles para aceptar. KYC Nivel 2: DNI/NIE + selfie + domicilio + firma electrónica. Entrega: 30 días hábiles desde verificación. Si no acepta → suplente 1 → suplente 2 → suplente 3 → donación benéfica." },
            { titulo: "§14 — Depósito Notarial", texto: "Estado: PENDIENTE depósito en Notaría ABACO, Ciudad Real. BLOQUEANTE: no iniciar ventas antes de completar el depósito notarial y pagar el Modelo 685." },
        ],
        tabla_comisiones: null,
        kyb_docs: null,
    },
];

// ── Split financiero centralizado ────────────────────────────────────────
const SPLIT_INFO = [
    { label: "Pool Actores (distribución)", pct: "45%", color: "#4f46e5", detalle: "COL 45% directa · COL 20% + SUB 25% asistida · COL Digital 45% QR Global" },
    { label: "Pool REDROYAL SL", pct: "55%", color: "#059669", detalle: "Captador: CCP 3% | COM 2% | ASE 2% · Donación social 2% · Provisión impuestos premio · Plataforma + beneficio" },
];

export class PrLegalView extends Component {
    static template = "promocionesred_dashboard.PrLegalView";

    setup() {
        this.state = useState({
            activeContrato: "col",
            activeTab: "clausulas",  // 'clausulas' | 'comisiones' | 'kyb'
        });
    }

    get contratos() { return CONTRATOS; }
    get splitInfo() { return SPLIT_INFO; }

    get selected() {
        return CONTRATOS.find(c => c.id === this.state.activeContrato) || CONTRATOS[0];
    }

    selectContrato(id) {
        this.state.activeContrato = id;
        this.state.activeTab = "clausulas";
    }

    setTab(tab) { this.state.activeTab = tab; }

    downloadPDF() {
        const c = this.selected;
        window.alert(`📄 Contrato ${c.label} ${c.version}\n\nEn producción, este botón generará el PDF oficial del contrato para firma digital.\n\nContacto: legal@premiosred.com`);
    }

    copyEmail() {
        navigator.clipboard.writeText("legal@premiosred.com").catch(() => {});
    }
}
