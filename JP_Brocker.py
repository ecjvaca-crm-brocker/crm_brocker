import streamlit as st
import urllib.parse
import sqlite3
import pandas as pd
import numpy as np
import tempfile
import os
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
import matplotlib.pyplot as plt

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
# 3. GENERADOR DE INFORMES PDF PROFESIONAL CON GRÁFICO DE RADAR
# ==========================================
class PDFConsultoria(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 10)
        self.set_text_color(10, 37, 64)
        self.cell(0, 8, "ESCALA CONSULTING - METODOLOGIA MCKINSEY & COMPANY", 0, 1, "L")
        self.set_font("helvetica", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 5, "Informe Ejecutivo de Diagnostico y Madurez Empresarial", 0, 1, "L")
        self.set_draw_color(212, 175, 55)
        self.set_line_width(0.8)
        self.line(10, 22, 200, 22)
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}} | Uso Exclusivo - Escala Finance & Insurance", 0, 0, "C")

def generar_grafico_radar():
    labels = ['Comercial', 'Financiero', 'Operativo', 'Legal & Gov']
    stats = [35, 20, 15, 40]
    
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    stats += stats[:1]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.plot(angles, stats, color='#0A2540', linewidth=2, linestyle='solid')
    ax.fill(angles, stats, color='#10B981', alpha=0.3)
    
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, size=8, color='#0A2540', fontweight='bold')
    
    ax.spines['polar'].set_color('#D1D5DB')
    ax.grid(color='#E5E7EB', linestyle='--', linewidth=0.7)
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    plt.tight_layout()
    plt.savefig(temp_file.name, format='png', dpi=200, bbox_inches='tight')
    plt.close(fig)
    return temp_file.name

def generar_pdf_mckinsey(fila_client):
    def buscar_col(keywords, defecto="No especificado"):
        for col in fila_client.index:
            if any(k.lower() in col.lower() for k in keywords):
                val = fila_client[col]
                return str(val) if pd.notna(val) else defecto
        return defecto

    empresa = buscar_col(["empresa", "negocio", "organización"], "Escala Consulting (Kinetic Motor Studio)")
    representante = buscar_col(["nombre", "representante", "propietario"], "Jonathan Vaca")
    
    pdf = PDFConsultoria()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # ---------------------------------------------------------
    # PÁGINA 1: Portada, Resumen, Radar y Tabla de Madurez
    # ---------------------------------------------------------
    pdf.add_page()
    
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(10, 37, 64)
    pdf.cell(0, 8, "Informe Ejecutivo de Evaluacion de Cuenta", 0, 1, "L")
    
    pdf.set_font("helvetica", "B", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"CLIENTE / REPRESENTANTE: {representante}", 0, 1, "L")
    pdf.cell(0, 5, f"RAZON SOCIAL / COMERCIAL: {empresa}", 0, 1, "L")
    pdf.cell(0, 5, f"FECHA DE EMISION: {datetime.now().strftime('%d de %B, %Y')}", 0, 1, "L")
    pdf.ln(4)
    
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(10, 37, 64)
    pdf.cell(0, 6, "Resumen Ejecutivo:", 0, 1, "L")
    pdf.set_font("helvetica", "", 9)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 4.5, "La empresa presenta una condicion de Vulnerabilidad Estructural Critica (Indice de Salud de Gestion: 28/100). El diagnostico revela una alta dependencia operativa del fundador y una tension severa en la liquidez a corto plazo, amenazando la sostenibilidad del negocio y obstaculizando la meta estrategica.")
    pdf.ln(4)
    
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(10, 37, 64)
    pdf.cell(0, 6, "1. Indice de Madurez de Gestion (Maturity Assessment)", 0, 1, "L")
    
    ruta_radar = generar_grafico_radar()
    pdf.image(ruta_radar, x=65, y=pdf.get_y(), w=75)
    pdf.ln(78)
    
    if os.path.exists(ruta_radar):
        os.remove(ruta_radar)

    pdf.set_font("helvetica", "B", 8)
    pdf.set_fill_color(10, 37, 64)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(35, 5.5, "Pilar Estrategico", 1, 0, "C", True)
    pdf.cell(75, 5.5, "Variable Evaluada", 1, 0, "C", True)
    pdf.cell(25, 5.5, "Puntuacion", 1, 0, "C", True)
    pdf.cell(45, 5.5, "Estado Tecnico", 1, 1, "C", True)

    pdf.set_font("helvetica", "", 8)
    pdf.set_text_color(0, 0, 0)
    
    datos_tabla = [
        ("Comercial", "Embudo de ventas & Definicion de Avatar", "35%", "Incipiente / Intuitivo"),
        ("Financiero", "Flujo de caja, P&L & Separacion patrimonial", "20%", "Critico / Hemorragia"),
        ("Operativo", "Dependencia del fundador & Procesos", "15%", "Colapso por Autoempleo"),
        ("Legal & Gobierno", "Tributacion, Contratos & Activos", "40%", "Riesgo Moderado")
    ]
    
    for pilar, var, punt, estado in datos_tabla:
        pdf.cell(35, 5.5, pilar, 1, 0, "L")
        pdf.cell(75, 5.5, var, 1, 0, "L")
        pdf.cell(25, 5.5, punt, 1, 0, "C")
        pdf.cell(45, 5.5, estado, 1, 1, "C")

    # ---------------------------------------------------------
    # PÁGINA 2: Análisis Técnico por Pilares
    # ---------------------------------------------------------
    pdf.add_page()
    
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(10, 37, 64)
    pdf.cell(0, 6, "2. Analisis Tecnico por Pilares (Diagnostico Profundo)", 0, 1, "L")
    pdf.ln(2)
    
    pdf.set_font("helvetica", "B", 9)
    pdf.cell(0, 5, "A. Pilar Financiero & Control de Caja", 0, 1, "L")
    pdf.set_font("helvetica", "", 8.5)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 4, "Se detecta una mezcla critica entre el patrimonio personal del fundador y las finanzas operativas de la compania, lo que distorsiona la visibilidad real de la rentabilidad. La empresa sufre de escasez recurrente de liquidez a corto plazo (\"cash crunch\") debido a la ausencia de un presupuesto de caja proyectado a 13 semanas.")
    pdf.ln(3)
    
    pdf.set_font("helvetica", "B", 9)
    pdf.set_text_color(10, 37, 64)
    pdf.cell(0, 5, "B. Pilar Comercial & Estrategia de Mercado", 0, 1, "L")
    pdf.set_font("helvetica", "", 8.5)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 4, "El modelo de adquisicion descansa enteramente en la intuicion comercial y en esfuerzos de redes sociales sin un embudo (funnel) estructurado. La ausencia de un perfil de cliente ideal (avatar) documentado genera altos costos de adquisicion de clientes (CAC).")
    pdf.ln(3)
    
    pdf.set_font("helvetica", "B", 9)
    pdf.set_text_color(10, 37, 64)
    pdf.cell(0, 5, "C. Pilar Operativo & Eficiencia de Procesos", 0, 1, "L")
    pdf.set_font("helvetica", "", 8.5)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 4, "El negocio exhibe el nivel maximo de dependencia operativa del fundador (5/5). La organizacion opera bajo un esquema de \"cultura de memoria\", donde ningun proceso clave cuenta con manuales o procedimientos documentados.")
    pdf.ln(3)
    
    pdf.set_font("helvetica", "B", 9)
    pdf.set_text_color(10, 37, 64)
    pdf.cell(0, 5, "D. Pilar Legal & Gobierno Corporativo", 0, 1, "L")
    pdf.set_font("helvetica", "", 8.5)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 4, "Se identifican pendientes en obligaciones tributarias y una practica generalizada de operar mediante acuerdos de palabra con proveedores y clientes en lugar de contratos escritos y blindados.")

    # ---------------------------------------------------------
    # PÁGINA 3: Hoja de Ruta Estratégica (Plan de Trabajo 90 Días)
    # ---------------------------------------------------------
    pdf.add_page()
    
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(10, 37, 64)
    pdf.cell(0, 6, "3. Hoja de Ruta Estratégica (Plan de Trabajo 90 Dias)", 0, 1, "L")
    pdf.ln(2)
    
    pdf.set_font("helvetica", "B", 9)
    pdf.set_text_color(212, 175, 55)
    pdf.cell(0, 5, "Fase 1: Estabilizacion de Urgencias y Caja (Mes 1)", 0, 1, "L")
    pdf.set_font("helvetica", "", 8.5)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 4, "Objetivo: Detener la quema de efectivo y blindar el patrimonio.\n- Establecer cuentas bancarias corporativas 100% separadas de las personales.\n- Implementar un Flujo de Caja Operativo diario a 13 semanas.\n- Auditoria tributaria expres para sanear pendientes fiscales.")
    pdf.ln(3)
    
    pdf.set_font("helvetica", "B", 9)
    pdf.set_text_color(212, 175, 55)
    pdf.cell(0, 5, "Fase 2: Reingenieria Comercial y Claridad de Oferta (Mes 2)", 0, 1, "L")
    pdf.set_font("helvetica", "", 8.5)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 4, "Objetivo: Estructurar un motor de ventas predecible.\n- Definicion estricta del Avatar y propuesta de valor basada en margenes.\n- Diseno e implementacion de un embudo (funnel) comercial medible.\n- Estandarizacion de contratos base.")
    pdf.ln(3)
    
    pdf.set_font("helvetica", "B", 9)
    pdf.set_text_color(212, 175, 55)
    pdf.cell(0, 5, "Fase 3: Estandarizacion y Desacoplamiento Operativo (Mes 3)", 0, 1, "L")
    pdf.set_font("helvetica", "", 8.5)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 4, "Objetivo: Reducir la dependencia del fundador y escalar con autonomia.\n- Documentacion de los 3 procesos core de entrega de servicio.\n- Automatizacion de flujos con herramientas en la nube.\n- Establecimiento de un cuadro de mando integral (KPIs).")
    
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
            "El acompañamiento en la estructuración de capital de trabajo salvó la operación trimestral de nuestra empresa."<br>
            <small style='color:#718096;'><strong>- Ing. Marcelo P. (Gerente General)</strong></small>
        </div>
        """, unsafe_allow_html=True)

with t3:
    ft3, txt3 = st.columns([1, 3])
    with ft3:
        st.image("https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=150&h=150&q=80", use_container_width=True)
    with txt3:
        st.markdown("""
        <div style="background-color: #FFFFFF; padding: 12px; border-radius: 6px; border-left: 3px solid #D4AF37; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            "Canalizar mi financiamiento educativo para la maestría en el exterior fue transparente y muy rápido gracias a Escala."<br>
            <small style='color:#718096;'><strong>- Mtr. Valeria S. (Consultora)</strong></small>
        </div>
        """, unsafe_allow_html=True)

st.write("---")

# ==========================================
# 10. PANEL DE ADMINISTRACIÓN Y REVISIÓN DE INFORMES
# ==========================================
st.write("---")
with st.expander("🔒 Acceso a Panel de Administración y Informes"):
    password_ingresada = st.text_input("Contraseña de Administrador:", type="password")
    
    if password_ingresada == PASSWORD_DASHBOARD:
        st.success("✅ Acceso autorizado.")
        
        tab_admin1, tab_admin2 = st.tabs(["📋 Leads en SQLite (Web)", "📊 Google Sheets & Informes PDF"])
        
        with tab_admin1:
            st.markdown("### Leads registrados desde el formulario web")
            df_leads = leer_leads()
            if not df_leads.empty:
                st.dataframe(df_leads, use_container_width=True)
            else:
                st.info("No hay registros guardados en SQLite todavía.")
                
        with tab_admin2:
            st.markdown("### Base de datos externa y Generador de Informes")
            df_gsheet = cargar_datos_google_sheet(URL_GOOGLE_SHEET)
            
            if not df_gsheet.empty:
                st.dataframe(df_gsheet, use_container_width=True)
                
                st.markdown("#### Generar Informe Ejecutivo PDF (Metodología McKinsey)")
                
                # Buscar dinámicamente la columna que contenga el nombre de la empresa o cliente
                columna_nombre_preferida = None
                for col in df_gsheet.columns:
                    if any(k in col.lower() for k in ["empresa", "nombre", "cliente", "razon", "negocio"]):
                        columna_nombre_preferida = col
                        break
                
                indice_fila = st.selectbox(
                    "Selecciona el cliente para el informe:", 
                    options=range(len(df_gsheet)),
                    format_func=lambda x: f"Fila {x}: {df_gsheet.iloc[x][columna_nombre_preferida] if columna_nombre_preferida and pd.notna(df_gsheet.iloc[x][columna_nombre_preferida]) else df_gsheet.iloc[x].values[0]}"
                )
                
                if st.button("📄 Generar y Descargar PDF Ejecutivo"):
                    fila_seleccionada = df_gsheet.iloc[indice_fila]
                    pdf_buffer = generar_pdf_mckinsey(fila_seleccionada)
                    
                    st.download_button(
                        label="📥 Descargar Informe en PDF",
                        data=pdf_buffer,
                        file_name=f"Informe_Ejecutivo_Escala_Fila_{indice_fila}.pdf",
                        mime="application/pdf"
                    )
            else:
                st.warning("No se pudo conectar o leer datos desde el Google Sheet configurado.")
    elif password_ingresada:
        st.error("❌ Contraseña incorrecta.")
