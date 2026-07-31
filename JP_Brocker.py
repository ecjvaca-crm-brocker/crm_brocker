import streamlit as st
import urllib.parse
import sqlite3
import pandas as pd
from datetime import datetime
from io import BytesIO
from fpdf import FPDF

# ==========================================
# 1. CONFIGURACIONES INICIALES GENERALES
# ==========================================
NUMERO_WHATSAPP = "593998076979" 
PASSWORD_DASHBOARD = "Escala2026" 

st.set_page_config(
    page_title="Escala Finance & Insurance | Consultoría Financiera y Corretaje", 
    page_icon="🏛️", 
    layout="wide"
)

URL_FOTO_ASESOR = "https://raw.githubusercontent.com/ecjvaca-crm-brocker/crm_brocker/main/IMGAENJONAS.jpeg"
URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/1DiKGC8Q65SjouMutswiF00hsdbAXTIV5yDlGXGEAZnU/edit?gid=1469424641#gid=1469424641"

# ==========================================
# 2. CAPA DE PERSISTENCIA Y CONEXIONES (SQLITE & GOOGLE SHEETS)
# ==========================================
def init_db():
    conn = sqlite3.connect("escala_web_leads.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS web_leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            nombre TEXT,
            cedula TEXT,
            telefono TEXT,
            ciudad TEXT,
            producto TEXT
        )
    """)
    conn.commit()
    conn.close()

def guardar_lead(nombre, cedula, telefono, ciudad, producto):
    conn = sqlite3.connect("escala_web_leads.db")
    cursor = conn.cursor()
    fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO web_leads (fecha, nombre, cedula, telefono, ciudad, producto)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha_hoy, nombre, cedula, telefono, ciudad, producto))
    conn.commit()
    conn.close()

def leer_leads():
    conn = sqlite3.connect("escala_web_leads.db")
    df = pd.read_sql_query("SELECT * FROM web_leads ORDER BY id DESC", conn)
    conn.close()
    return df

def cargar_datos_google_sheet(url_sheet):
    try:
        if "edit" in url_sheet:
            csv_url = url_sheet.split("/edit")[0] + "/export?format=csv"
        else:
            csv_url = url_sheet
        df = pd.read_csv(csv_url)
        if "<html" in str(df.iloc[0, 0]).lower():
            return pd.DataFrame()
        return df
    except Exception as e:
        return pd.DataFrame()

init_db()

# ==========================================
# 3. GENERADOR DE INFORMES PDF PROFESIONAL (MCKINSEY STYLE)
# ==========================================
class PDFConsultoria(FPDF):
    def header(self):
        # Cabecera Institucional (Sin caracteres especiales para evitar errores de codificación)
        self.set_font("helvetica", "B", 10)
        self.set_text_color(10, 37, 64)
        self.cell(0, 8, "ESCALA CONSULTING - METODOLOGIA MCKINSEY & COMPANY", 0, 1, "L")
        self.set_font("helvetica", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 5, "Informe Ejecutivo de Diagnostico y Madurez Empresarial", 0, 1, "L")
        self.set_draw_color(212, 175, 55) # Dorado ejecutivo
        self.set_line_width(0.8)
        self.line(10, 22, 200, 22)
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}} | Uso Exclusivo - Escala Finance & Insurance", 0, 0, "C")

def generar_pdf_mckinsey(fila_client):
    def buscar_col(keywords, defecto="No especificado"):
        for col in fila_client.index:
            if any(k.lower() in col.lower() for k in keywords):
                val = fila_client[col]
                return str(val) if pd.notna(val) else defecto
        return defecto

    empresa = buscar_col(["empresa", "negocio", "organización"], "Empresa Cliente")
    representante = buscar_col(["nombre", "representante", "propietario"], "Representante")
    sector = buscar_col(["sector", "industria", "antigüedad"], "Servicios Generales")
    contacto_email = buscar_col(["correo", "email"], "correo@ejemplo.com")
    contacto_tel = buscar_col(["teléfono", "celular", "whatsapp"], "0000000000")
    equipo = buscar_col(["empleados", "equipo", "colaboradores", "personas"], "Solo el dueño")
    
    objetivo_12m = buscar_col(["objetivo", "12 meses", "meta anual"], "Punto de equilibrio y rentabilidad")
    dolores = buscar_col(["dolor", "cuello", "problema", "obstáculo"], "Organización y crecimiento comercial")
    meta_consultoria = buscar_col(["consultoría", "esperas lograr", "ayuda"], "Aumentar ventas y captar clientes")
    
    fecha_actual = datetime.now().strftime("%Y-%m-%d")

    pdf = PDFConsultoria(orientation="P", unit="mm", format="A4")
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # TÍTULO PRINCIPAL DEL DOCUMENTO
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(10, 37, 64)
    pdf.cell(0, 10, f"DIAGNÓSTICO DIRECTIVO: {empresa.upper()}", 0, 1, "L")
    
    # METADATOS EN BLOQUE GRIS
    pdf.set_font("helvetica", "", 9)
    pdf.set_fill_color(240, 244, 248)
    pdf.set_text_color(50, 50, 50)
    
    meta_texto = (
        f"Representante: {representante}   |   Sector: {sector}   |   Fecha: {fecha_actual}\n"
        f"Contacto: {contacto_email} / {contacto_tel}   |   Estructura: {equipo}"
    )
    pdf.multi_cell(0, 6, meta_texto, 0, "L", fill=True)
    pdf.ln(5)

    # SECCIÓN 1: ESTADO DE SALUD Y MÉTRICAS
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(10, 37, 64)
    pdf.cell(0, 8, "1. Diagnóstico de Situación y Estado de Salud", 0, 1, "L")
    
    pdf.set_font("helvetica", "B", 9)
    pdf.set_fill_color(255, 243, 205) # Alerta amarilla
    pdf.set_text_color(133, 100, 4)
    pdf.cell(0, 7, "  ESTADO GENERAL: CRÍTICO / REQUIERE INTERVENCIÓN URGENTE", 0, 1, "L", fill=True)
    
    pdf.set_font("helvetica", "", 9)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 5, "Se detectan vulnerabilidades severas en liquidez, ausencia de controles financieros formales y una dependencia operativa total del fundador.")
    pdf.ln(4)

    # TABLA DE INDICADORES / DIMENSIÓN ESTRATÉGICA
    pdf.set_font("helvetica", "B", 9)
    pdf.set_fill_color(10, 37, 64)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(60, 7, " Dimensión Estratégica", 1, 0, "L", fill=True)
    pdf.cell(80, 7, " Respuesta Registrada", 1, 0, "L", fill=True)
    pdf.cell(50, 7, " Evaluación de Riesgo", 1, 1, "L", fill=True)

    datos_tabla_1 = [
        ("Objetivo a 12 Meses", objetivo_12m, "Meta Ambiciosa"),
        ("Principales Dolores", dolores, "Crítico Operativo"),
        ("Meta con Consultoría", meta_consultoria, "Prioridad Comercial")
    ]

    pdf.set_font("helvetica", "", 8)
    pdf.set_text_color(40, 40, 40)
    for dim, resp, riesgo in datos_tabla_1:
        pdf.cell(60, 10, f" {dim}", 1, 0, "L")
        pdf.cell(80, 10, f" {resp[:42]}", 1, 0, "L")
        pdf.cell(50, 10, f" {riesgo}", 1, 1, "L")
    pdf.ln(6)

    # SECCIÓN 2: MATRIZ DE RIESGOS Y CUELLOS DE BOTELLA
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(10, 37, 64)
    pdf.cell(0, 8, "2. Análisis de Riesgos y Cuellos de Botella (Matriz de KPIs)", 0, 1, "L")

    datos_tabla_2 = [
        ("Dependencia del Fundador", "Nivel 5/5 (Operación 100% dependiente de la memoria y presencia del dueño)."),
        ("Flujo de Caja y Liquidez", "Sufrimos constantemente por falta de efectivo o desfases temporales."),
        ("Separación de Finanzas", "No hay división clara entre recursos personales y corporativos."),
        ("Control P&L y Balance", "Ausencia de revisión mensual de Estados de Resultados."),
        ("Márgenes de Utilidad", "No se conocen con certeza analítica los márgenes netos por línea.")
    ]

    pdf.set_font("helvetica", "B", 8)
    pdf.set_fill_color(220, 225, 230)
    pdf.set_text_color(10, 37, 64)
    pdf.cell(60, 6, " Indicador Clave", 1, 0, "L", fill=True)
    pdf.cell(130, 6, " Situación Actual Detectada", 1, 1, "L", fill=True)

    pdf.set_font("helvetica", "", 8)
    pdf.set_text_color(40, 40, 40)
    for ind, sit in datos_tabla_2:
        pdf.cell(60, 8, f" {ind}", 1, 0, "L")
        pdf.cell(130, 8, f" {sit[:75]}", 1, 1, "L")
    pdf.ln(6)

    # SECCIÓN 3: HOJA DE RUTA (PLAN DE TRABAJO 90 DÍAS)
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(10, 37, 64)
    pdf.cell(0, 8, "3. Hoja de Ruta Preliminar (Plan de Trabajo Escala - 90 Días)", 0, 1, "L")

    fases = [
        ("Fase 1 (Mes 1): Control Financiero y Blindaje de Caja", 
         "Separación inmediata de finanzas personales y del negocio, implementación de Estado de Resultados (P&L) básico mensual y estructuración de proyecciones de flujo de caja a 90 días."),
        ("Fase 2 (Mes 2): Activación Comercial y Definición de Avatar", 
         "Definición rigurosa del perfil del cliente ideal (avatar), diseño de un embudo de ventas estructurado y formalización de propuestas comerciales."),
        ("Fase 3 (Mes 3): Estandarización y Reducción de Dependencia", 
         "Documentación de procesos clave mediante manuales operativos y uso de herramientas de gestión para disminuir la dependencia diaria del fundador.")
    ]

    for titulo_fase, desc_fase in fases:
        pdf.set_font("helvetica", "B", 9)
        pdf.set_text_color(16, 185, 129) # Verde corporativo
        pdf.cell(0, 6, titulo_fase, 0, 1, "L")
        pdf.set_font("helvetica", "", 8.5)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 5, desc_fase)
        pdf.ln(3)

    # Retornar los bytes del PDF generado
    return BytesIO(pdf.output(dest='S'))

# ==========================================
# 4. IDENTIDAD VISUAL PREMIUM Y ANIMACIONES (CSS)
# ==========================================
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #FFFFFF 0%, #EBF4FC 100%);
    }
    h1, h2, h3, h4 {
        color: #0A2540 !important;
        font-family: 'Georgia', serif;
    }
    .card-corporativa {
        background-color: #FFFFFF;
        padding: 25px;
        border-radius: 10px;
        border-top: 5px solid #D4AF37;
        border-left: 1px solid #D1D5DB;
        border-right: 1px solid #D1D5DB;
        border-bottom: 2px solid #0A2540;
        margin-bottom: 20px;
        box-shadow: 0 6px 12px rgba(10,37,64,0.06);
    }
    div.stButton > button:first-child {
        background-color: #10B981;
        color: #FFFFFF;
        border: 2px solid #059669;
        border-radius: 6px;
        padding: 0.7rem 2rem;
        font-weight: bold;
        font-size: 16px;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(16,185,129,0.2);
    }
    div.stButton > button:first-child:hover {
        background-color: #0A2540;
        color: #D4AF37;
        border-color: #D4AF37;
    }
    .ejecutivo-box {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.04);
        border-top: 4px solid #10B981;
        transition: transform 0.2s ease;
    }
    .ejecutivo-box:hover {
        transform: translateY(-3px);
        border-color: #D4AF37;
    }
    .ejecutivo-avatar {
        width: 130px;
        height: 130px;
        border-radius: 50%;
        object-fit: cover;
        border: 4px solid #D4AF37;
        margin: 0 auto 12px auto;
        display: block;
    }
    .slider-container {
        width: 100%;
        max-height: 230px;
        overflow: hidden;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        position: relative;
        border: 2px solid #D4AF37;
    }
    .slider-track {
        display: flex;
        width: 500%;
        animation: slideAnimation 25s infinite linear;
    }
    .slider-track-fast {
        display: flex;
        width: 300%;
        animation: slideAnimationThree 15s infinite linear;
    }
    .slide {
        width: 100%;
        position: relative;
    }
    .slide img {
        width: 100%;
        height: 230px;
        object-fit: cover;
        filter: brightness(65%);
    }
    .slide-text {
        position: absolute;
        bottom: 20px;
        left: 25px;
        right: 25px;
        color: #FFFFFF;
        font-family: 'Georgia', serif;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.9);
    }
    .slide-text h2, .slide-text h3 {
        color: #D4AF37 !important;
        margin: 0;
        font-size: 1.35rem;
    }
    .slide-text p {
        margin: 5px 0 0 0;
        font-size: 0.95rem;
        font-weight: bold;
        color: #FFFFFF;
    }
    @keyframes slideAnimation {
        0% { transform: translateX(0); }
        16% { transform: translateX(0); }
        20% { transform: translateX(-20%); }
        36% { transform: translateX(-20%); }
        40% { transform: translateX(-40%); }
        56% { transform: translateX(-40%); }
        60% { transform: translateX(-60%); }
        76% { transform: translateX(-60%); }
        80% { transform: translateX(-80%); }
        96% { transform: translateX(-80%); }
        100% { transform: translateX(0); }
    }
    @keyframes slideAnimationThree {
        0% { transform: translateX(0); }
        28% { transform: translateX(0); }
        33% { transform: translateX(-33.33%); }
        61% { transform: translateX(-33.33%); }
        66% { transform: translateX(-66.66%); }
        94% { transform: translateX(-66.66%); }
        100% { transform: translateX(0); }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 5. CABECERA PRINCIPAL
# ==========================================
st.markdown("<h1 style='text-align: center; font-size: 2.8rem; margin-bottom: 0;'>🏛️ ESCALA FINANCE & INSURANCE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #D4AF37; font-size: 1.4rem; font-weight: bold; margin-top: 0;'>Tu consultor financiero de confianza</p>", unsafe_allow_html=True)
st.write("")

# ==========================================
# 6. BANNER ROTATIVO INTERACTIVO DE SERVICIOS
# ==========================================
st.markdown("""
<div class="slider-container">
    <div class="slider-track">
        <div class="slide"><img src="https://images.unsplash.com/photo-1591696205602-2f950c417cb9?auto=format&fit=crop&w=1200&h=300&q=72"><div class="slide-text"><h2>Servicio de Asesoría Financiera Corporativa</h2><p>Estructuración técnica independiente de soluciones de liquidez.</p></div></div>
        <div class="slide"><img src="https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&w=1200&h=300&q=72"><div class="slide-text"><h2>Servicio de Asesoría en Finanzas Personales</h2><p>Optimización patrimonial y planificación de capital de largo plazo.</p></div></div>
        <div class="slide"><img src="https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=1200&h=300&q=72"><div class="slide-text"><h2>Servicio de Asesoría Inmobiliaria e Hipotecaria</h2><p>Intermediación técnica y corretaje ágil para compra de bienes.</p></div></div>
        <div class="slide"><img src="https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=1200&h=300&q=72"><div class="slide-text"><h2>Servicio de Asesoría para Estudios y Maestrías</h2><p>Canalización de recursos educativos para potenciar tu perfil profesional.</p></div></div>
        <div class="slide"><img src="https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=1200&h=300&q=72"><div class="slide-text"><h2>Servicio de Asesoría en Seguros y Respaldo Patrimonial</h2><p>Mitigación técnica de riesgos para ti, tu familia y tu empresa.</p></div></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card-corporativa">
    <h3 style='margin-top:0;'>✨ Asesoría Patrimonial y Estrategia de Financiamiento</h3>
    <p style='color: #4A5568; font-size: 1.1rem;'>Como Bróker especialista, conectamos tus metas con las mejores alternativas del ecosistema de manera independiente, mediante un análisis técnico riguroso y relaciones directas con proveedores institucionales.</p>
    <strong style='color: #0A2540;'>💼 Nuestra consultoría inicial no genera honorarios para ti</strong> (estos son cubiertos de manera directa por las firmas aliadas del mercado comercial).
</div>
""", unsafe_allow_html=True)

st.write("---")

servicios_escala = [
    "1️⃣ Servicio de Asesoría para Financiamiento Educativo y Maestrías",
    "2️⃣ Servicio de Asesoría para Créditos de Consumo o Capital de Trabajo",
    "3️⃣ Servicio de Asesoría para Crédito Hipotecario y Financiamiento Inmobiliario",
    "4️⃣ Servicio de Asesoría para Financiamiento Automotriz (Vehículos)",
    "5️⃣ Servicio de Asesoría en Seguros (Vehicular, Médico o Protección familiar y Colectiva)"
]

col_izq, col_der = st.columns([1.1, 0.9])

with col_izq:
    st.markdown("### 📋 Pre-Calificación de Perfil")
    st.caption("Introduce tus datos para ingresar el trámite en nuestro sistema en línea:")
    
    with st.form(key="formulario_leads", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("👤 Nombre Completo:", placeholder="Ej: Ec. Carlos Mendoza")
        with c2:
            cedula = st.text_input("🪪 Número de Cédula:", max_chars=10, placeholder="Ej: 100xxxxxxx")
            
        c3, c4 = st.columns(2)
        with c3:
            telefono = st.text_input("📱 Celular / WhatsApp:", placeholder="Ej: 099xxxxxxx")
        with c4:
            ciudad = st.text_input("📍 Ciudad de Residencia:", placeholder="Ej: Ibarra / Quito")
            
        opciones_formulario = [s.split("para ")[-1] if "para " in s else s.split("en ")[-1] for s in servicios_escala]
        producto_interes = st.selectbox("🎯 Solución Técnica de Interés:", options=opciones_formulario)
        
        st.markdown("""
        <p style='font-size: 0.82rem; color: #6B7280; text-align: justify; line-height: 1.25;'>
            *Al presionar el botón inferior, usted otorga su <strong>consentimiento expreso, voluntario e informado</strong> para el tratamiento de sus datos personales. Autoriza a Escala Finance & Insurance a almacenar su expediente y procesar la información en plataformas de análisis financiero exclusivamente para este trámite.*
        </p>
        """, unsafe_allow_html=True)
        
        st.write("")
        boton_enviar = st.form_submit_button("Ingresar Trámite Oficial 🚀")

    if boton_enviar:
        if not nombre or not cedula or not telefono:
            st.error("⚠️ Los campos Nombre, Cédula y Teléfono son estrictamente obligatorios.")
        elif len(cedula) < 10 or not cedula.isdigit():
            st.error("⚠️ Documento de identidad no válido (Debe contener 10 números).")
        else:
            guardar_lead(nombre, cedula, telefono, ciudad, producto_interes)
            st.success("🎉 ¡Trámite ingresado con éxito en la plataforma Escala Finance & Insurance!")
            
            texto_ws = f"Hola Escala Finance & Insurance, he completado y autorizado mi pre-calificación en línea.\n\n" \
                       f"👤 *Consultante:* {nombre}\n" \
                       f"🪪 *Cédula:* {cedula}\n" \
                       f"📱 *Contacto:* {telefono}\n" \
                       f"📍 *Ciudad:* {ciudad}\n" \
                       f"🎯 *Línea:* Asesoría en {producto_interes}\n\n" \
                       f"📜 *Estado:* Trámite ingresado con éxito. Consentimiento de datos corporativos aprobado."
            
            url_whatsapp = f"https://api.whatsapp.com/send?phone={NUMERO_WHATSAPP}&text={urllib.parse.quote(texto_ws)}"
            st.balloons()
            st.link_button("🟢 Validar Identidad vía WhatsApp", url_whatsapp, type="primary")

with col_der:
    st.markdown("### 🤖 Asesor Ejecutivo Virtual")
    st.caption("Toca la fotografía de tu asesor para iniciar el flujo interactivo estructurado:")
    
    flujo_bot_whatsapp = (
        "🏛️ [ESCALA FINANCE & INSURANCE - ASISTENTE VIRTUAL]\n\n"
        "🤖 ¡Hola! Bienvenido al canal interactivo de Escala. Estoy aquí para ingresar tu trámite de forma inmediata.\n\n"
        "Por favor, bríndame tus DATOS PERSONALES base respondiendo en una sola línea:\n"
        "• Nombre y Apellido Completo:\n"
        "• Número de Cédula (10 dígitos):\n"
        "• Celular de Contacto:\n"
        "• Ciudad de Residencia:\n\n"
        "-----------------------------------------\n"
        "📥 [MENSAJE DE RESPUESTA AUTOMÁTICA DE ESCALA]:\n"
        "¡Excelente! Tus datos han sido recibidos de forma preliminar. A continuación, selecciona el Servicio de Asesoría técnica que requieres respondiendo únicamente con el NÚMERO correspondiente:\n\n"
        f"{servicios_escala[0]}\n"
        f"{servicios_escala[1]}\n"
        f"{servicios_escala[2]}\n"
        f"{servicios_escala[3]}\n"
        f"{servicios_escala[4]}\n\n"
        "-----------------------------------------\n"
        "📜 [PROTECCIÓN DE DATOS Y AUTORIZACIÓN DE SCORING]:\n"
        "Al completar este flujo, otorgo mi consentimiento expreso para el tratamiento de mis datos personales y AUTORIZO de manera irrevocable a Escala Finance & Insurance para que realice las revisiones técnicas de mi perfil en las plataformas de Scoring y Buró crediticio vigentes. Con esto, mi trámite queda OFICIALMENTE INGRESADO en el sistema."
    )
    
    url_flujo_completo = f"https://api.whatsapp.com/send?phone={NUMERO_WHATSAPP}&text={urllib.parse.quote(flujo_bot_whatsapp)}"
    
    st.markdown(f"""
    <a href="{url_flujo_completo}" target="_blank" style="text-decoration: none; color: inherit;">
        <div class="ejecutivo-box">
            <img class="ejecutivo-avatar" src="{URL_FOTO_ASESOR}">
            <h4 style="margin: 0; color: #0A2540; font-size: 1.25rem;">Ec. Jonathan Vaca Cruz</h4>
            <p style="margin: 3px 0 10px 0; color: #10B981; font-weight: bold; font-size: 0.9rem;">💼 Broker & Consultor Financiero Senior</p>
            <div style="background-color: #F0F4F8; padding: 12px; border-radius: 8px; font-size: 0.88rem; color: #374151; text-align: justify; border-left: 3px solid #10B981;">
                💬 <strong>¿Deseas iniciar el flujo por WhatsApp?</strong> Toca mi fotografía o el botón inferior para abrir el chat interactivo. Podrás ingresar tus datos personales, seleccionar el servicio corporativo del menú numerado y autorizar de forma segura la revisión en plataformas de scoring. ¡Tu trámite quedará ingresado de inmediato!
            </div>
            <br>
            <span style="background-color: #10B981; color: white; padding: 8px 18px; border-radius: 20px; font-weight: bold; font-size: 0.85rem; display: inline-block; box-shadow: 0 3px 6px rgba(16,185,129,0.3);">
                🟢 Abrir Flujo de WhatsApp Ahora
            </span>
        </div>
    </a>
    """, unsafe_allow_html=True)

st.write("---")

# ==========================================
# 7. INDICADORES ECONÓMICOS
# ==========================================
st.markdown("### 📊 Indicadores Económicos Mundiales y Locales")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric(label="🇺🇸 S&P 500", value="5,137.08", delta="+0.80%")
m2.metric(label="💻 NASDAQ 100", value="18,302.91", delta="+1.14%")
m3.metric(label="🛢️ Crudo Oriente (Ecuador)", value="$78.26", delta="-0.45%")
m4.metric(label="🏛️ BV Quito", value="1,045.20", delta="+0.12%")
m5.metric(label="🏦 BV Guayaquil", value="985.40", delta="-0.08%")

st.write("---")

# ==========================================
# 8. MULTI-SLIDERS INTERACTIVOS
# ==========================================
col_noticias, col_linkedin, col_youtube = st.columns([1, 1, 1])

with col_noticias:
    st.markdown("### 📰 Actualidad Económica")
    st.caption("Noticias clave del ecosistema financiero global y local:")
    st.markdown("""
    <div class="slider-container">
        <div class="slider-track-fast">
            <div class="slide">
                <img src="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=400&h=230&q=60">
                <div class="slide-text"><h3>Bloomberg</h3><p>Bancos centrales evalúan ajustes de tasas de interés comerciales para el tercer trimestre.</p></div>
            </div>
            <div class="slide">
                <img src="https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=400&h=230&q=60">
                <div class="slide-text"><h3>CNN Business</h3><p>Mercados globales reaccionan al alza impulsados por el sector de tecnología e IA.</p></div>
            </div>
            <div class="slide">
                <img src="https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?auto=format&fit=crop&w=400&h=230&q=60">
                <div class="slide-text"><h3>Revista Ekos</h3><p>Ecuador registra un incremento en solicitudes de microcréditos productivos corporativos.</p></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_linkedin:
    st.markdown("### 🔗 Artículos en LinkedIn")
    st.caption("Haga clic en cualquiera de los slides para abrir el artículo original:")
    st.markdown("""
    <div class="slider-container">
        <div class="slider-track-fast">
            <a class="slide" href="https://www.linkedin.com/posts/jonathan-paul-vaca-cruz-70b378b8_estamos-delegando-nuestra-visi%C3%B3n-o-solo-share-7477466894040702976-aafK/" target="_blank">
                <img src="https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=400&h=230&q=60">
                <div class="slide-text"><h3>Liderazgo y Gestión</h3><p>¿Estamos delegando nuestra visión o solo el trabajo administrativo?</p></div>
            </a>
            <a class="slide" href="https://www.linkedin.com/posts/jonathan-paul-vaca-cruz-70b378b8_ugcPost-7474858018564870144-UZ2h/" target="_blank">
                <img src="https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=400&h=230&q=60">
                <div class="slide-text"><h3>Estrategia Profesional</h3><p>Análisis técnico sobre la optimización del ecosistema corporativo.</p></div>
            </a>
            <a class="slide" href="https://www.linkedin.com/posts/activity-7383934863373971456-Xp9F" target="_blank">
                <img src="https://images.unsplash.com/photo-1600880292203-757bb62b4baf?auto=format&fit=crop&w=400&h=230&q=60">
                <div class="slide-text"><h3>Actividad y Actualidad</h3><p>Últimas novedades, reflexiones del mercado y pulso financiero institucional.</p></div>
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.link_button("🌐 Visitar Mi Perfil Completo en LinkedIn", "https://linkedin.com/in/jonathan-paul-vaca-cruz-70b378b8", use_container_width=True)

with col_youtube:
    st.markdown("### 🎥 Educación Financiera")
    st.caption("Cápsulas de aprendizaje y videos clave de mi canal:")
    st.markdown("""
    <div class="slider-container">
        <div class="slider-track-fast">
            <div class="slide">
                <img src="https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=400&h=230&q=60">
                <div class="slide-text">Campañas Educativas<h3>Video: Crédito Inmobiliario</h3><p>Guía técnica paso a paso para pre-calificar con éxito a un financiamiento hipotecario.</p></div>
            </div>
            <div class="slide">
                <img src="https://images.unsplash.com/photo-1542744094-3a31f103e35f?auto=format&fit=crop&w=400&h=230&q=60">
                <div class="slide-text"><h3>Video: Financiamiento de Maestrías</h3><p>Cómo canalizar fondos para potenciar tu perfil profesional sin descapitalizarte.</p></div>
            </div>
            <div class="slide">
                <img src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=400&h=230&q=60">
                <div class="slide-text"><h3>Video: Análisis de Scoring</h3><p>Lo que las firmas aliadas analizan en tu buró crediticio al tramitar una línea de consumo.</p></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.link_button("📺 Ir a mi Canal de YouTube", "http://www.youtube.com/@jonathanvaca3000", use_container_width=True)

st.write("---")

# ==========================================
# 9. TESTIMONIOS CON AVATARES
# ==========================================
st.markdown("### 💬 Opiniones y Testimonios de Clientes")
st.write("")

t1, t2, t3 = st.columns(3)

with t1:
    ft1, txt1 = st.columns([1, 3])
    with ft1:
        st.image("https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&h=150&q=80", use_container_width=True)
    with txt1:
        st.markdown("""
        <div style="background-color: #FFFFFF; padding: 12px; border-radius: 6px; border-left: 3px solid #D4AF37; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            "La consultoría técnica para el equipamiento de mi clínica odontológica fue impecable. Conseguí la tasa idónea."<br>
            <small style='color:#718096;'><strong>- Dr. Alejandro R. (Odontólogo)</strong></small>
        </div>
        """, unsafe_allow_html=True)

with t2:
    ft2, txt2 = st.columns([1, 3])
    with ft2:
        st.image("https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&h=150&q=80", use_container_width=True)
    with txt2:
        st.markdown("""
        <div style="background-color: #FFFFFF; padding: 12px; border-radius: 6px; border-left: 3px solid #D4AF37; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            "Gracias a su asesoría estratégica logré estructurar el financiamiento de mi Maestría sin comprometer mi liquidez."<br>
            <small style='color:#718096;'><strong>- Mgs. Lorena P. (Arquitecta)</strong></small>
        </div>
        """, unsafe_allow_html=True)

with t3:
    ft3, txt3 = st.columns([1, 3])
    with ft3:
        st.image("https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&w=150&h=150&q=80", use_container_width=True)
    with txt3:
        st.markdown("""
        <div style="background-color: #FFFFFF; padding: 12px; border-radius: 6px; border-left: 3px solid #D4AF37; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            "Excelente servicio corporativo de corretaje para la emisión de la póliza de seguro vehicular de nuestra flota."<br>
            <small style='color:#718096;'><strong>- Ing. Javier G. (Gerente General)</strong></small>
        </div>
        """, unsafe_allow_html=True)

st.write("---")

# ==========================================
# 10. PANEL DE CONTROL INTERNO & DIAGNÓSTICO IA
# ==========================================
st.markdown("### 🔒 Panel de Control Interno")

with st.expander("🔑 Acceder al Dashboard Ejecutivo (Uso exclusivo de Consultores)"):
    pass_input = st.text_input("Ingrese la clave de seguridad para visualizar métricas:", type="password", key="pass_dash")
    
    if pass_input == PASSWORD_DASHBOARD:
        st.success("🔓 Acceso concedido de forma segura.")
        
        # --- SUBSECCIÓN A: LEADS TRADICIONALES SQL ---
        df_leads = leer_leads()
        if not df_leads.empty:
            total_leads = len(df_leads)
            st.metric(label="📈 Total de Prospectos Capturados (Web)", value=total_leads)
            
            dash_col1, dash_col2 = st.columns([1, 1])
            with dash_col1:
                st.markdown("#### 🎯 Solicitudes por Tipo de Producto")
                st.bar_chart(df_leads["producto"].value_counts())
            with dash_col2:
                st.markdown("#### 📍 Concentración Geográfica")
                st.bar_chart(df_leads["ciudad"].value_counts())
                
            st.write("")
            st.markdown("#### 📑 Historial Completo de Expedientes en SQL")
            st.dataframe(df_leads, use_container_width=True)
        else:
            st.info("📊 El sistema SQL está activo pero aún no hay registros web directos.")

        st.write("---")

        # --- SUBSECCIÓN B: GENERADOR DE INFORMES PDF MCKINSEY ---
        st.markdown("### 🤖 Generador de Diagnósticos McKinsey (Exportable a PDF)")
        st.caption("Selecciona una empresa registrada en tu Google Sheet para generar el informe directivo institucional:")
        
        df_clientes = cargar_datos_google_sheet(URL_GOOGLE_SHEET)

        if not df_clientes.empty:
            columnas_disponibles = list(df_clientes.columns)
            sugerencia_index = 0
            for i, col in enumerate(columnas_disponibles):
                if any(k in col.lower() for k in ["empresa", "nombre", "negocio", "razon"]):
                    sugerencia_index = i
                    break

            col_elegida = st.selectbox(
                "Selecciona la columna de tu Google Sheet que contiene el Nombre de la Empresa o Cliente:", 
                options=columnas_disponibles,
                index=sugerencia_index
            )
            
            if col_elegida:
                empresas_unicas = df_clientes[col_elegida].dropna().unique()
                
                if len(empresas_unicas) > 0:
                    empresa_seleccionada = st.selectbox("Selecciona la Empresa Específica:", options=empresas_unicas)
                    
                    if st.button("🚀 Generar Informe Estratégico McKinsey (PDF)"):
                        fila_datos = df_clientes[df_clientes[col_elegida] == empresa_seleccionada].iloc[0]
                        pdf_buffer = generar_pdf_mckinsey(fila_datos)
                        
                        st.success("✅ ¡Informe Ejecutivo estructurado y listo para descargar!")
                        
                        st.download_button(
                            label="📥 Descargar Informe Ejecutivo en Formato PDF (Corporativo)",
                            data=pdf_buffer,
                            file_name=f"Informe_McKinsey_{str(empresa_seleccionada).replace(' ', '_')}.pdf",
                            mime="application/pdf"
                        )
                else:
                    st.warning("⚠️ La columna seleccionada no contiene datos de empresas.")
        else:
            st.error("❌ No se pudo leer el Google Sheet. Verifica que el enlace sea accesible o público.")

    elif pass_input != "":
        st.error("❌ Contraseña incorrecta. El acceso al sistema central permanece revocado.")
