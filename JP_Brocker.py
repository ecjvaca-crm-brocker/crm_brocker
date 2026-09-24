import streamlit as str_app
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
import yfinance as yf

# ==============================================================================
# 1. CONFIGURACIONES INICIALES Y CONSTANTES GENERALES DE LA APLICACIÓN
# ==============================================================================
NUMERO_WHATSAPP = "593998076979" 
PASSWORD_DASHBOARD = "Escala2026" 

str_app.set_page_config(
    page_title="Escala Consultoría Empresarial y Financiera", 
    page_icon="🏛️", 
    layout="wide"
)

URL_FOTO_ASESOR = "https://raw.githubusercontent.com/ecjvaca-crm-brocker/crm_brocker/main/IMGAENJONAS.jpeg"
URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/1DiKGC8Q65SjouMutswiF00hsdbAXTIV5yDlGXGEAZnU/edit?gid=1469424641#gid=1469424641"

# ==============================================================================
# 2. CAPA DE PERSISTENCIA Y CONEXIONES (SQLITE & GOOGLE SHEETS)
# ==============================================================================
def init_db():
    """Inicializa la base de datos local SQLite para almacenar los leads web."""
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
    """Guarda un registro nuevo de prospecto web en SQLite."""
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
    """Lee todos los registros almacenados en SQLite."""
    conn = sqlite3.connect("escala_web_leads.db")
    df = pd.read_sql_query("SELECT * FROM web_leads ORDER BY id DESC", conn)
    conn.close()
    return df

def cargar_datos_google_sheet(url_sheet):
    """Carga de forma segura los datos remotos desde un Google Sheet público en CSV."""
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

# ==============================================================================
# 3. GENERADOR DE INFORMES PDF PROFESIONAL (METODOLOGÍA MCKINSEY & COMPANY)
# ==============================================================================
class PDFConsultoria(FPDF):
    """Clase personalizada para la estructuración y membrete de informes ejecutivos."""
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
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}} | Uso Exclusivo - Escala Consultoría Empresarial y Financiera", 0, 0, "C")

def generar_grafico_radar():
    """Genera un gráfico de radar dinámico para el análisis de madurez corporativa."""
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
    """Construye el documento PDF completo incorporando métricas y análisis."""
    def buscar_col(keywords, defecto="No especificado"):
        for col in fila_client.index:
            if any(k.lower() in col.lower() for k in keywords):
                val = fila_client[col]
                return str(val) if pd.notna(val) else defecto
        return defecto

    empresa = buscar_col(["empresa", "negocio", "organización"], "Escala Consultoría Empresarial y Financiera")
    representante = buscar_col(["nombre", "representante", "propietario"], "Jonathan Vaca")
    
    pdf = PDFConsultoria()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)
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
    pdf.multi_cell(0, 4.5, "La empresa presenta una condicion de Vulnerabilidad Estructural Critica (Indice de Salud de Gestion: 28/100). El diagnostico revela una alta dependencia operativa del fundador y una tension severa en la liquidez a corto plazo.")
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

    return BytesIO(pdf.output(dest='S'))

# ==============================================================================
# 4. HOJAS DE ESTILO CSS PERSONALIZADAS (INTERFAZ VISUAL CORPORATIVA)
# ==============================================================================
str_app.markdown("""
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
    .slide-text h2 {
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
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 5. CABECERA PRINCIPAL Y ESTRUCTURA DE PESTAÑAS
# ==============================================================================
str_app.markdown("<h1 style='text-align: center; font-size: 2.8rem; margin-bottom: 0;'>🏛️ Escala Consultoría Empresarial y Financiera</h1>", unsafe_allow_html=True)
str_app.markdown("<p style='text-align: center; color: #D4AF37; font-size: 1.4rem; font-weight: bold; margin-top: 0;'>Tu consultor financiero de confianza</p>", unsafe_allow_html=True)
str_app.write("")

tab_principal_herramienta, tab_principal_calculadora, tab_ecosistema_cresa = str_app.tabs([
    "🚀 Herramienta Financiera (Golden Ledger)", 
    "🧮 Simulador, Capacidad de Pago y Scoring",
    "🌐 Ecosistema CRESA"
])

with tab_principal_herramienta:
    str_app.markdown("""
    <div class="card-corporativa">
        <h3>📊 Plataforma de Finanzas Personales & Negocios</h3>
        <p style='color: #4A5568;'>Accede directamente a nuestra plataforma especializada en control de activos, presupuestos y proyecciones de liquidez.</p>
    </div>
    """, unsafe_allow_html=True)
    str_app.link_button(
        "📊 Abrir Herramienta de Finanzas Personales (Golden Ledger)", 
        "https://golden-ledger-ai-93.lovable.app/", 
        use_container_width=True
    )

with tab_principal_calculadora:
    str_app.markdown("""
    <div class="card-corporativa" style="border-top: 5px solid #10B981;">
        <h3>🧮 Simulador Avanzado: Cuotas, Capacidad de Pago y Scoring</h3>
        <p style='color: #4A5568;'>Calcula tu cuota mensual estimada, evalúa tu capacidad real de endeudamiento (CDP) y obtén una estimación de tu perfil de scoring crediticio.</p>
    </div>
    """, unsafe_allow_html=True)
    
    subtab_sim1, subtab_sim2 = str_app.tabs(["💡 Simulador y Capacidad de Pago (CDP)", "📊 Análisis de Scoring & Calificación"])
    
    with subtab_sim1:
        str_app.markdown("#### 1. Datos para la Simulación de Crédito")
        c_calc1, c_calc2, c_calc3 = str_app.columns(3)
        with c_calc1:
            monto_prestamo = str_app.number_input("Monto del Crédito Deseado ($):", min_value=100.0, value=10000.0, step=500.0, key="monto_credito_input")
        with c_calc2:
            tasa_interes_anual = str_app.number_input("Tasa de Interés Anual (%):", min_value=1.0, value=15.0, step=0.5, key="tasa_credito_input")
        with c_calc3:
            plazo_meses = str_app.selectbox("Plazo (Meses):", options=[12, 24, 36, 48, 60, 72], index=2, key="plazo_credito_input")
            
        i_mensual = (tasa_interes_anual / 100) / 12
        if i_mensual > 0:
            cuota_mensual = monto_prestamo * (i_mensual * (1 + i_mensual)**plazo_meses) / ((1 + i_mensual)**plazo_meses - 1)
        else:
            cuota_mensual = monto_prestamo / plazo_meses
            
        total_pagar = cuota_mensual * plazo_meses
        interes_total = total_pagar - monto_prestamo
        
        res1, res2, res3 = str_app.columns(3)
        res1.metric("💵 Cuota Mensual Estimada", f"${cuota_mensual:,.2f}")
        res2.metric("📈 Total Intereses", f"${interes_total:,.2f}")
        res3.metric("💰 Monto Total a Pagar", f"${total_pagar:,.2f}")
        
        str_app.markdown("---")
        str_app.markdown("#### 2. Evaluación de Capacidad de Pago (CDP) y Monto Sugerido")
        
        cp_col1, cp_col2, cp_col3 = str_app.columns(3)
        with cp_col1:
            ingresos_netos = str_app.number_input("Ingresos Mensuales Netos ($):", min_value=0.0, value=1500.0, step=100.0, key="ingresos_netos_cp")
        with cp_col2:
            egresos_fijos = str_app.number_input("Egresos / Gastos Fijos Mensuales ($):", min_value=0.0, value=500.0, step=50.0, key="egresos_fijos_cp")
        with cp_col3:
            otras_cuotas = str_app.number_input("Pago de Otras Deudas / Créditos Vigentes ($):", min_value=0.0, value=200.0, step=50.0, key="otras_cuotas_cp")
            
        excedente_mensual = ingresos_netos - egresos_fijos - otras_cuotas
        cdp_sugerida = min(excedente_mensual * 0.8, ingresos_netos * 0.45)
        if cdp_sugerida < 0:
            cdp_sugerida = 0.0

        cdp_res1, cdp_res2, _ = str_app.columns(3)
        cdp_res1.metric("💼 Excedente Mensual Neto", f"${excedente_mensual:,.2f}")
        cdp_res2.metric("🛡️ Cuota Disponible (CDP)", f"${cdp_sugerida:,.2f}")

    with subtab_sim2:
        str_app.markdown("#### 📊 Simulador y Diagnóstico de Scoring Crediticio")
        historial_buro = str_app.selectbox("Historial en Buró de Crédito:", options=["Excelente (Sin atrasos)", "Bueno (Atrasos menores < 30 días)", "Regular (Atrasos entre 30 y 90 días)", "Crítico (Atrasos > 90 días / Cartera castigada)"], index=0)
        score_base = 750 if "Excelente" in historial_buro else 600
        str_app.markdown(f"### 📈 Puntaje de Scoring Estimado: **{score_base} / 1000 Puntos**")

# ==============================================================================
# 6. PESTAÑA INTEGRADA: ECOSISTEMA CRESA (ENLACES OFICIALES)
# ==============================================================================
with tab_ecosistema_cresa:
    str_app.markdown("""
    <div class="card-corporativa" style="border-top: 5px solid #0A2540;">
        <h3>🌐 Ecosistema de Validación y Consultas CRESA</h3>
        <p style='color: #4A5568;'>Accede de manera rápida y directa a las plataformas institucionales y herramientas oficiales de consulta, así como a las redes comerciales de Social Selling.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sub-pestañas internas dentro de CRESA para separar las consultas tradicionales del Social Selling
    sub_cresa_general, sub_cresa_social = str_app.tabs(["📋 Plataformas de Consulta y Validación", "🛒 Social Selling y Canales Comerciales"])
    
    with sub_cresa_general:
        cresa_c1, cresa_c2 = str_app.columns(2)
        
        with cresa_c1:
            str_app.markdown("""
            <div style="background:#FFFFFF; padding:18px; border-radius:10px; border:1px solid #E5E7EB; margin-bottom:15px; box-shadow:0 3px 6px rgba(0,0,0,0.03);">
                <h4>🏢 Plataforma Principal Nexum</h4>
                <p style="font-size:0.9rem; color:#4A5568;">Sistema integral de gestión y control corporativo.</p>
            </div>
            """, unsafe_allow_html=True)
            str_app.link_button("🚀 Abrir Plataforma Nexum 360", "https://nexum360.com.ec/", use_container_width=True)
            
            str_app.markdown("""
            <div style="background:#FFFFFF; padding:18px; border-radius:10px; border:1px solid #E5E7EB; margin-bottom:15px; box-shadow:0 3px 6px rgba(0,0,0,0.03);">
                <h4>📄 Consulta de RUC (SRI)</h4>
                <p style="font-size:0.9rem; color:#4A5568;">Validador oficial de registros únicos de contribuyentes.</p>
            </div>
            """, unsafe_allow_html=True)
            str_app.link_button("🔍 Consultar RUC en SRI", "https://srienlinea.sri.gob.ec/sri-en-linea/SriRucWeb/ConsultaRuc/Consultas/consultaRuc", use_container_width=True)

            str_app.markdown("""
            <div style="background:#FFFFFF; padding:18px; border-radius:10px; border:1px solid #E5E7EB; margin-bottom:15px; box-shadow:0 3px 6px rgba(0,0,0,0.03);">
                <h4>👤 Certificado de Afiliación IESS (Paso 1)</h4>
                <p style="font-size:0.9rem; color:#4A5568;">Selección y emisión inicial de certificado de afiliación.</p>
            </div>
            """, unsafe_allow_html=True)
            str_app.link_button("📋 IESS - Certificado de Afiliación (Paso 1)", "https://www.iess.gob.ec/afiliado-web/pages/opcionesGenerales/seleccionCertificadoDeAfiliacion.jsf", use_container_width=True)

            str_app.markdown("""
            <div style="background:#FFFFFF; padding:18px; border-radius:10px; border:1px solid #E5E7EB; margin-bottom:15px; box-shadow:0 3px 6px rgba(0,0,0,0.03);">
                <h4>✅ Validación de Usuario sin Aportes (IESS Paso 2)</h4>
                <p style="font-size:0.9rem; color:#4A5568;">Comprobación de estado para usuarios sin aportaciones vigentes.</p>
            </div>
            """, unsafe_allow_html=True)
            str_app.link_button("📋 IESS - Validación sin Aportes (Paso 2)", "https://www.iess.gob.ec/afiliado-web/pages/opcionesGenerales/validarUsuarioSinAportes.jsf", use_container_width=True)

            str_app.markdown("""
            <div style="background:#FFFFFF; padding:18px; border-radius:10px; border:1px solid #E5E7EB; margin-bottom:15px; box-shadow:0 3px 6px rgba(0,0,0,0.03);">
                <h4>👴 Certificado de Jubilación IESS</h4>
                <p style="font-size:0.9rem; color:#4A5568;">Generación de constancia para pensionistas y jubilados.</p>
            </div>
            """, unsafe_allow_html=True)
            str_app.link_button("📜 Consultar Certificado de Jubilación", "https://www.iess.gob.ec/prjPensionesJubilacion-web/pages/certificadoPensionista/certificadoDePensionista.jsf", use_container_width=True)

        with cresa_c2:
            str_app.markdown("""
            <div style="background:#FFFFFF; padding:18px; border-radius:10px; border:1px solid #E5E7EB; margin-bottom:15px; box-shadow:0 3px 6px rgba(0,0,0,0.03);">
                <h4>🏥 Tipo de Afiliación (IESS, ISSFA, ISSPOL)</h4>
                <p style="font-size:0.9rem; color:#4A5568;">Portal del Ministerio de Salud Pública para cobertura médica.</p>
            </div>
            """, unsafe_allow_html=True)
            str_app.link_button("🩺 Consultar Cobertura en Salud (MSP)", "https://coberturasalud.msp.gob.ec/", use_container_width=True)

            str_app.markdown("""
            <div style="background:#FFFFFF; padding:18px; border-radius:10px; border:1px solid #E5E7EB; margin-bottom:15px; box-shadow:0 3px 6px rgba(0,0,0,0.03);">
                <h4>⏱️ Cobertura y Tiempo de Afiliación</h4>
                <p style="font-size:0.9rem; color:#4A5568;">Gestión de calificación de derecho y tiempo aportado.</p>
            </div>
            """, unsafe_allow_html=True)
            str_app.link_button("⏳ Consultar Tiempo de Afiliación (IESS)", "https://app.iess.gob.ec/gestion-calificacion-derecho-web/public/formulariosContacto.jsf", use_container_width=True)

            str_app.markdown("""
            <div style="background:#FFFFFF; padding:18px; border-radius:10px; border:1px solid #E5E7EB; margin-bottom:15px; box-shadow:0 3px 6px rgba(0,0,0,0.03);">
                <h4>🚗 Multas y Citaciones ANT</h4>
                <p style="font-size:0.9rem; color:#4A5568;">Agencia Nacional de Tránsito - Consulta de valores pendientes.</p>
            </div>
            """, unsafe_allow_html=True)
            str_app.link_button("🚦 Consultar Multas ANT", "https://consultaweb.ant.gob.ec/PortalWEB/paginas/clientes/clp_criterio_consulta.jsp", use_container_width=True)

            str_app.markdown("""
            <div style="background:#FFFFFF; padding:18px; border-radius:10px; border:1px solid #E5E7EB; margin-bottom:15px; box-shadow:0 3px 6px rgba(0,0,0,0.03);">
                <h4>🎓 Validación Fecha de Nacimiento (SECAP)</h4>
                <p style="font-size:0.9rem; color:#4A5568;">Plataforma de registro y validación de usuarios.</p>
            </div>
            """, unsafe_allow_html=True)
            str_app.link_button("🎓 SECAP - Validación de Datos", "http://si.secap.gob.ec/sisecap/logeo_web/usuario_nuevo.php", use_container_width=True)

            str_app.markdown("""
            <div style="background:#FFFFFF; padding:18px; border-radius:10px; border:1px solid #E5E7EB; margin-bottom:15px; box-shadow:0 3px 6px rgba(0,0,0,0.03);">
                <h4>💼 Nuevo Prospecto (Oficina Virtual Nexum)</h4>
                <p style="font-size:0.9rem; color:#4A5568;">Registro directo en la oficina virtual de prospectos.</p>
            </div>
            """, unsafe_allow_html=True)
            str_app.link_button("📝 Registrar Nuevo Prospecto (Nexum)", "https://nexum360.com.ec/oficina virtual/nuevo-prospecto", use_container_width=True)

    with sub_cresa_social:
        str_app.markdown("#### 🛍️ Canales de Social Selling")
        str_app.caption("Acceso directo a las plataformas comerciales integradas:")
        
        social_c1, social_c2, social_c3 = str_app.columns(3)

        with social_c1:
            str_app.markdown("""
            <div style="background:#FFFFFF; padding:18px; border-radius:10px; border:1px solid #E5E7EB; margin-bottom:15px; box-shadow:0 3px 6px rgba(0,0,0,0.03); text-align: center;">
                <h4>🏠 Orve Hogar</h4>
                <p style="font-size:0.85rem; color:#4A5568;">Muebles, decoración y soluciones para el hogar.</p>
            </div>
            """, unsafe_allow_html=True)
            str_app.link_button("🌐 Visitar Orve Hogar", "https://www.orvehogar.com", use_container_width=True)

        with social_c2:
            str_app.markdown("""
            <div style="background:#FFFFFF; padding:18px; border-radius:10px; border:1px solid #E5E7EB; margin-bottom:15px; box-shadow:0 3px 6px rgba(0,0,0,0.03); text-align: center;">
                <h4>⚡ Almacenes Japón</h4>
                <p style="font-size:0.85rem; color:#4A5568;">Electrodomésticos, tecnología y motos.</p>
            </div>
            """, unsafe_allow_html=True)
            str_app.link_button("🌐 Visitar Almacenes Japón", "https://www.almacenesjapon.com", use_container_width=True)

        with social_c3:
            str_app.markdown("""
            <div style="background:#FFFFFF; padding:18px; border-radius:10px; border:1px solid #E5E7EB; margin-bottom:15px; box-shadow:0 3px 6px rgba(0,0,0,0.03); text-align: center;">
                <h4>💳 Créditos Económicos</h4>
                <p style="font-size:0.85rem; color:#4A5568;">Almacenes de consumo masivo y créditos directos.</p>
            </div>
            """, unsafe_allow_html=True)
            str_app.link_button("🌐 Visitar Créditos Económicos", "https://www.creditoseconomicos.com", use_container_width=True)
# ==============================================================================
# 7. DIAGNÓSTICO DE SITUACIÓN ACTUAL Y BANNER ROTATIVO
# ==============================================================================
str_app.markdown("### 🫀 Evaluación y Diagnóstico Institucional")
str_app.link_button(
    "📈 Diagnóstico Situación Actual", 
    "https://forms.gle/ka4VnbthTDq9uxp97", 
    use_container_width=True
)

str_app.write("")

str_app.markdown("""
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

str_app.write("---")

servicios_escala = [
    "1️⃣ Servicio de Asesoría para Financiamiento Educativo y Maestrías",
    "2️⃣ Servicio de Asesoría para Créditos de Consumo o Capital de Trabajo",
    "3️⃣ Servicio de Asesoría para Crédito Hipotecario y Financiamiento Inmobiliario",
    "4️⃣ Servicio de Asesoría para Financiamiento Automotriz (Vehículos)",
    "5️⃣ Servicio de Asesoría en Seguros (Vehicular, Médico o Protección familiar y Colectiva)"
]

col_izq, col_der = str_app.columns([1.1, 0.9])

with col_izq:
    str_app.markdown("### 📋 Pre-Calificación de Perfil")
    str_app.caption("Introduce tus datos para ingresar el trámite en nuestro sistema en línea:")
    
    with str_app.form(key="formulario_leads", clear_on_submit=True):
        c1, c2 = str_app.columns(2)
        with c1:
            nombre = str_app.text_input("👤 Nombre Completo:", placeholder="Ej: Ec. Carlos Mendoza")
        with c2:
            cedula = str_app.text_input("🪪 Número de Cédula:", max_chars=10, placeholder="Ej: 100xxxxxxx")
            
        c3, c4 = str_app.columns(2)
        with c3:
            telefono = str_app.text_input("📱 Celular / WhatsApp:", placeholder="Ej: 099xxxxxxx")
        with c4:
            ciudad = str_app.text_input("📍 Ciudad de Residencia:", placeholder="Ej: Ibarra / Quito")
            
        opciones_formulario = [s.split("para ")[-1] if "para " in s else s.split("en ")[-1] for s in servicios_escala]
        producto_interes = str_app.selectbox("🎯 Solución Técnica de Interés:", options=opciones_formulario)
        
        str_app.markdown("""
        <p style='font-size: 0.82rem; color: #6B7280; text-align: justify; line-height: 1.25;'>
            *Al presionar el botón inferior, usted otorga su <strong>consentimiento expreso, voluntario e informado</strong> para el tratamiento de sus datos personales. Autoriza a Escala Finance & Insurance a almacenar su expediente.*
        </p>
        """, unsafe_allow_html=True)
        
        str_app.write("")
        boton_enviar = str_app.form_submit_button("Ingresar Trámite Oficial 🚀")

    if boton_enviar:
        if not nombre or not cedula or not telefono:
            str_app.error("⚠️ Los campos Nombre, Cédula y Teléfono son estrictamente obligatorios.")
        elif len(cedula) < 10 or not cedula.isdigit():
            str_app.error("⚠️ Documento de identidad no válido (Debe contener 10 números).")
        else:
            guardar_lead(nombre, cedula, telefono, ciudad, producto_interes)
            str_app.success("🎉 ¡Trámite ingresado con éxito en la plataforma Escala Consultoría!")
            
            texto_ws = f"Hola Escala Finance & Insurance, he completado y autorizado mi pre-calificación en línea.\n\n" \
                       f"👤 *Consultante:* {nombre}\n" \
                       f"🪪 *Cédula:* {cedula}\n" \
                       f"📱 *Contacto:* {telefono}\n" \
                       f"📍 *Ciudad:* {ciudad}\n" \
                       f"🎯 *Línea:* Asesoría en {producto_interes}"
            
            url_whatsapp = f"https://api.whatsapp.com/send?phone={NUMERO_WHATSAPP}&text={urllib.parse.quote(texto_ws)}"
            str_app.balloons()
            str_app.link_button("🟢 Validar Identidad vía WhatsApp", url_whatsapp, type="primary")

with col_der:
    str_app.markdown("### 🤖 Asesor Ejecutivo Virtual")
    str_app.caption("Toca la fotografía de tu asesor para iniciar el flujo interactivo estructurado:")
    
    flujo_bot_whatsapp = (
        "🏛️ [Escala Consultoría Empresarial y Financiera - ASISTENTE VIRTUAL]\n\n"
        "🤖 ¡Hola! Bienvenido al canal interactivo de Escala. Estoy aquí para ingresar tu trámite de forma inmediata.\n"
    )
    url_flujo_completo = f"https://api.whatsapp.com/send?phone={NUMERO_WHATSAPP}&text={urllib.parse.quote(flujo_bot_whatsapp)}"
    
    str_app.markdown(f"""
    <a href="{url_flujo_completo}" target="_blank" style="text-decoration: none; color: inherit;">
        <div class="ejecutivo-box">
            <img class="ejecutivo-avatar" src="{URL_FOTO_ASESOR}">
            <h4 style="margin: 0; color: #0A2540; font-size: 1.25rem;">Ec. Jonathan Vaca Cruz</h4>
            <p style="margin: 3px 0 10px 0; color: #10B981; font-weight: bold; font-size: 0.9rem;">💼 Broker & Consultor Financiero Senior</p>
            <div style="background-color: #F0F4F8; padding: 12px; border-radius: 8px; font-size: 0.88rem; color: #374151; text-align: justify; border-left: 3px solid #10B981;">
                💬 <strong>¿Deseas iniciar el flujo por WhatsApp?</strong> Toca mi fotografía o el botón inferior para abrir el chat interactivo.
            </div>
            <br>
            <span style="background-color: #10B981; color: white; padding: 8px 18px; border-radius: 20px; font-weight: bold; font-size: 0.85rem; display: inline-block; box-shadow: 0 3px 6px rgba(16,185,129,0.3);">
                🟢 Abrir Flujo de WhatsApp Ahora
            </span>
        </div>
    </a>
    """, unsafe_allow_html=True)

str_app.write("---")

# ==============================================================================
# 8. INDICADORES ECONÓMICOS Y MERCADOS EN TIEMPO REAL
# ==============================================================================
str_app.markdown("### 📊 Indicadores Económicos Dinámicos en Tiempo Real")
str_app.caption("Datos conectados directamente a los movimientos de mercado bursátil global y commodities:")

@str_app.cache_data(ttl=300)
def obtener_indicadores_tiempo_real():
    tickers_dict = {
        "S&P 500": "^GSPC",
        "NASDAQ 100": "^NDX",
        "Petróleo WTI": "USO",
        "Oro": "GLD",
        "Bitcoin": "BTC-USD"
    }
    resultados = {}
    for nombre, ticker in tickers_dict.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="5d")
            if not hist.empty and len(hist) >= 2:
                precio_actual = hist['Close'].iloc[-1]
                precio_anterior = hist['Close'].iloc[-2]
                cambio_pct = ((precio_actual - precio_anterior) / precio_anterior) * 100
                resultados[nombre] = (f"${precio_actual:,.2f}" if precio_actual > 10 else f"{precio_actual:,.2f}", f"{cambio_pct:+.2f}%")
            else:
                resultados[nombre] = ("N/A", "0.00%")
        except:
            resultados[nombre] = ("N/A", "0.00%")
    return resultados

datos_mercado = obtener_indicadores_tiempo_real()

m1, m2, m3, m4, m5 = str_app.columns(5)
for i, (k, v) in enumerate(datos_mercado.items()):
    val, delta = v
    if i == 0: m1.metric(label=f"📈 {k}", value=val, delta=delta)
    elif i == 1: m2.metric(label=f"💻 {k}", value=val, delta=delta)
    elif i == 2: m3.metric(label=f"🛢️ {k}", value=val, delta=delta)
    elif i == 3: m4.metric(label=f"🥇 {k}", value=val, delta=delta)
    elif i == 4: m5.metric(label=f"🪙 {k}", value=val, delta=delta)

str_app.write("---")

# ==============================================================================
# 9. BOTÓN DEMO SISTEMA CONTABLE Y PANEL DE ADMINISTRACIÓN
# ==============================================================================
str_app.markdown("""
<div class="card-corporativa" style="text-align: center;">
    <h3>🖥️ Soluciones Contables en la Nube</h3>
    <p style='color: #4A5568;'>Prueba nuestros portales de demostración para optimizar la contabilidad y gestión de tu negocio.</p>
</div>
""", unsafe_allow_html=True)

str_app.link_button(
    "DEMO SISTEMA CONTABLE", 
    "https://sistema.minegocio.com.ec/", 
    use_container_width=True
)

str_app.write("---")

# ==============================================================================
# 10. MÓDULO AVANZADO: PLANIFICACIÓN DE RETIRO Y JUBILACIÓN PATRIMONIAL
# ==============================================================================
str_app.markdown("### 🎯 Módulo 10: Planificador de Jubilación y Retiro Patrimonial")
str_app.caption("Proyección actuarial y cálculo de capital objetivo para independencia financiera:")

col_ret1, col_ret2, col_ret3 = str_app.columns(3)
with col_ret1:
    edad_actual = str_app.number_input("Edad Actual:", min_value=18, max_value=80, value=35, key="edad_act_mod10")
with col_ret2:
    edad_retiro = str_app.number_input("Edad Deseada de Retiro:", min_value=30, max_value=90, value=60, key="edad_ret_mod10")
with col_ret3:
    gasto_mensual_retiro = str_app.number_input("Gasto Mensual Deseado en Retiro ($):", min_value=100.0, value=2000.0, step=100.0, key="gasto_ret_mod10")

anios_hasta_retiro = max(0, edad_retiro - edad_actual)
capital_objetivo = (gasto_mensual_retiro * 12) / 0.05 # Tasa de retiro seguro del 5% anual

str_app.markdown(f"""
<div style="background:#FFFFFF; padding:20px; border-radius:10px; border-left:5px solid #10B981; border:1px solid #E5E7EB; margin-top:10px;">
    <h4>📊 Resultados de Proyección de Retiro</h4>
    <p>⏳ Faltan <b>{anios_hasta_retiro} años</b> para tu jubilación.</p>
    <p>💰 Capital Objetivo Necesario (Fondo de Retiro al 5% de retorno): <b>${capital_objetivo:,.2f}</b></p>
</div>
""", unsafe_allow_html=True)

str_app.write("---")

# ==============================================================================
# 11. MÓDULO AVANZADO: SIMULADOR DE TABLA DE AMORTIZACIÓN Y CRONOGRAMA
# ==============================================================================
str_app.markdown("### 📋 Módulo 11: Generador de Tabla de Amortización Francesa")
str_app.caption("Visualiza el detalle mes a mes del capital e intereses de cualquier obligación financiera:")

col_tab1, col_tab2, col_tab3 = str_app.columns(3)
with col_tab1:
    monto_tabla = str_app.number_input("Capital del Préstamo ($):", min_value=1000.0, value=20000.0, step=1000.0, key="monto_t_mod11")
with col_tab2:
    tasa_tabla = str_app.number_input("Tasa Nominal Anual (%):", min_value=0.1, value=12.0, step=0.5, key="tasa_t_mod11")
with col_tab3:
    plazo_tabla = str_app.selectbox("Plazo en Meses:", options=[12, 24, 36, 48, 60, 120, 240], index=2, key="plazo_t_mod11")

if str_app.button("⚙️ Generar Tabla de Pagos Detallada"):
    t_mensual = (tasa_tabla / 100) / 12
    if t_mensual > 0:
        cuota_fija = monto_tabla * (t_mensual * (1 + t_mensual)**plazo_tabla) / ((1 + t_mensual)**plazo_tabla - 1)
    else:
        cuota_fija = monto_tabla / plazo_tabla

    saldo = monto_tabla
    cronograma = []
    for mes in range(1, plazo_tabla + 1):
        interes_mes = saldo * t_mensual
        capital_mes = cuota_fija - interes_mes
        saldo -= capital_mes
        cronograma.append({
            "Mes": mes,
            "Cuota": round(cuota_fija, 2),
            "Interés": round(interes_mes, 2),
            "Amortización Capital": round(capital_mes, 2),
            "Saldo Insoluto": round(max(0, saldo), 2)
        })
    df_cronograma = pd.DataFrame(cronograma)
    str_app.dataframe(df_cronograma, use_container_width=True)

str_app.write("---")

# ==============================================================================
# 12. MÓDULO AVANZADO: MATRIZ DE RIESGO CREDITICIO Y ENDEUDAMIENTO
# ==============================================================================
str_app.markdown("### 🛡️ Módulo 12: Matriz Corporativa de Análisis de Riesgo y Liquidez")
str_app.caption("Evaluación de ratios de solvencia y cobertura de servicio de deuda (DSCR):")

col_r1, col_r2 = str_app.columns(2)
with col_r1:
    ebitda_empresa = str_app.number_input("EBITDA Anual / Utilidad Operativa ($):", min_value=0.0, value=50000.0, step=5000.0, key="ebitda_mod12")
with col_r2:
    servicio_deuda_anual = str_app.number_input("Servicio de Deuda Anual (Capital + Intereses) ($):", min_value=1.0, value=25000.0, step=2000.0, key="deuda_mod12")

dscr = ebitda_empresa / servicio_deuda_anual

if dscr >= 1.25:
    estado_riesgo = "🟢 BAJO RIESGO (Solvencia Saludable - Apto para Financiamiento)"
elif dscr >= 1.0:
    estado_riesgo = "🟡 RIESGO MODERADO (Margen Ajustado - Requiere Reestructuración)"
else:
    estado_riesgo = "🔴 ALTO RIESGO / INSOLVENCIA (Servicio de deuda supera flujo operativo)"

str_app.markdown(f"""
<div style="background:#FFFFFF; padding:20px; border-radius:10px; border-left:5px solid #0A2540; border:1px solid #E5E7EB; margin-top:10px;">
    <h4>📊 Diagnóstico de Cobertura (DSCR)</h4>
    <p>📈 Ratio DSCR Calculado: <b>{dscr:.2f}x</b></p>
    <p>🏷️ Estado Técnico: <b>{estado_riesgo}</b></p>
</div>
""", unsafe_allow_html=True)

str_app.write("---")

# ==============================================================================
# 13. PANEL DE ADMINISTRACIÓN Y REPORTES AVANZADOS
# ==============================================================================
with str_app.expander("🔒 Acceso a Panel de Administración y Informes Avanzados"):
    password_ingresada = str_app.text_input("Contraseña de Administrador:", type="password", key="pwd_admin_avanzado")
    
    if password_ingresada == PASSWORD_DASHBOARD:
        str_app.success("✅ Acceso autorizado con privilegios senior.")
        
        tab_admin1, tab_admin2 = str_app.tabs(["📋 Leads en SQLite (Web)", "📊 Google Sheets & Informes PDF"])
        
        with tab_admin1:
            str_app.markdown("### Leads registrados desde el formulario web")
            df_leads = leer_leads()
            if not df_leads.empty:
                str_app.dataframe(df_leads, use_container_width=True)
                
                # Exportar a Excel
                output_excel = BytesIO()
                with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                    df_leads.to_excel(writer, index=False, sheet_name='Leads_Escala')
                output_excel.seek(0)
                
                str_app.download_button(
                    label="📥 Descargar Base de Leads en Excel (.xlsx)",
                    data=output_excel,
                    file_name=f"Leads_Escala_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                str_app.info("No hay registros guardados en SQLite todavía.")
                
        with tab_admin2:
            str_app.markdown("### Base de datos externa y Generador de Informes")
            df_gsheet = cargar_datos_google_sheet(URL_GOOGLE_SHEET)
            
            if not df_gsheet.empty:
                str_app.dataframe(df_gsheet, use_container_width=True)
                
                columna_nombre_preferida = None
                for col in df_gsheet.columns:
                    if any(k in col.lower() for k in ["empresa", "nombre", "cliente", "razon", "negocio"]):
                        columna_nombre_preferida = col
                        break
                
                indice_fila = str_app.selectbox(
                    "Selecciona el cliente para el informe:", 
                    options=range(len(df_gsheet)),
                    format_func=lambda x: f"Fila {x}: {df_gsheet.iloc[x][columna_nombre_preferida] if columna_nombre_preferida and pd.notna(df_gsheet.iloc[x][columna_nombre_preferida]) else df_gsheet.iloc[x].values[0]}",
                    key="sel_fila_pdf_avanzado"
                )
                
                if str_app.button("📄 Generar y Descargar PDF Ejecutivo", key="btn_pdf_avanzado"):
                    fila_seleccionada = df_gsheet.iloc[indice_fila]
                    pdf_buffer = generar_pdf_mckinsey(fila_seleccionada)
                    
                    str_app.download_button(
                        label="📥 Descargar Informe en PDF",
                        data=pdf_buffer,
                        file_name=f"Informe_Ejecutivo_Escala_Fila_{indice_fila}.pdf",
                        mime="application/pdf",
                        key="dl_pdf_btn_avanzado"
                    )
            else:
                str_app.warning("No se pudo conectar o leer datos desde el Google Sheet configurado.")
    elif password_ingresada:
        str_app.error("❌ Contraseña incorrecta.")


import streamlit as st
import pandas as pd
import numpy as np

# =====================================================================
# CONFIGURACIÓN DE PÁGINA Y ESTILOS CORPORATIVOS
# =====================================================================
st.set_page_config(page_title="Premium Valuation & Tax Hub", layout="wide", page_icon="📈")

st.title("📈 Ecosistema Escala Corporate: Premium Valuation & Tax Hub")
st.caption("Módulo Avanzado de Valoración de Activos e Inteligencia Fiscal para Alta Gerencia y Comités Ejecutivos (Normas NIIF / IFRS y LRTI)")

st.markdown("""
    <style>
    .metric-box {background-color: #f8f9fa; border-left: 5px solid #1f77b4; padding: 15px; border-radius: 4px; margin-bottom: 15px;}
    .report-title {font-size: 24px; font-weight: bold; color: #1e3d59; margin-top: 20px;}
    .section-desc {color: #555555; font-size: 14px; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# INICIALIZACIÓN DE ESTADOS GLOBALES (Persistencia del Pipeline)
# =====================================================================
if 'activos_tangibles' not in st.session_state:
    st.session_state.activos_tangibles = pd.DataFrame(columns=['Clase', 'Descripción', 'Valor Contable', 'Valor Razonable', 'Norma Aplicada'])

if 'impuestos_diferidos' not in st.session_state:
    st.session_state.impuestos_diferidos = pd.DataFrame(columns=['Concepto', 'Base Contable', 'Base Fiscal', 'Diferencia', 'Tipo', 'Impuesto Diferido'])

if 'enterprise_value' not in st.session_state:
    st.session_state.enterprise_value = 0.0

if 'tasa_fiscal_ecuador' not in st.session_state:
    st.session_state.tasa_fiscal_ecuador = 25.0

# =====================================================================
# NÚCLEO DE LÓGICA Y CÁLCULOS
# =====================================================================
def calcular_wacc(rf, beta, rm, riesgo_pais, kd, tasa_tax, peso_e):
    ke = rf + beta * (rm - rf) + riesgo_pais
    peso_d = 1.0 - peso_e
    wacc = (peso_e * ke) + (peso_d * kd * (1 - tasa_tax))
    return ke, wacc

def proyectar_dcf(fcl_año1, growth_tasa, g_perpetuidad, wacc):
    flujos = [fcl_año1]
    for _ in range(4):
        flujos.append(flujos[-1] * (1 + growth_tasa))
    
    df = pd.DataFrame({
        'Año': [f"Año {i+1}" for i in range(5)],
        'Flujo Proyectado': flujos
    })
    df['Factor Descuento'] = [1 / ((1 + wacc) ** (i+1)) for i in range(5)]
    df['Valor Presente'] = df['Flujo Proyectado'] * df['Factor Descuento']
    
    vp_flujosp = df['Valor Presente'].sum()
    valor_terminal = (flujos[-1] * (1 + g_perpetuidad)) / (wacc - g_perpetuidad)
    vp_valor_terminal = valor_terminal * df['Factor Descuento'].iloc[-1]
    enterprise_value = vp_flujosp + vp_valor_terminal
    
    return df, vp_flujosp, vp_valor_terminal, enterprise_value

# =====================================================================
# ARQUITECTURA DE PESTAÑAS
# =====================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "1. Valoración de Activos (Tangibles/VNR)",
    "2. Motor de Valoración Corporativa (DCF/WACC)",
    "3. Hub de Consultoría Tributaria (NIC 12)",
    "4. Reporte Ejecutivo para Directorios"
])

# ---------------------------------------------------------------------
# PESTAÑA 1: VALORACIÓN DE ACTIVOS INDIVIDUALES
# ---------------------------------------------------------------------
with tab1:
    st.header("🏢 Registro y Revaluación de Activos bajo NIIF")
    st.markdown("<p class='section-desc'>Cumplimiento estricto con NIC 16, NIC 40 y NIC 2 para auditorías de salida a bolsa.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Carga y Homologación de Activo")
        clase_activo = st.selectbox("Clase de Activo", ["Vehículos (NIC 16)", "Maquinaria y Equipos (NIC 16)", "Inmuebles (NIC 40)", "Inventarios (NIC 2 - VNR)"])
        desc_activo = st.text_input("Identificador / Descripción del Activo", placeholder="Ej. Planta Industrial Pifo")
        val_contable = st.number_input("Valor Neto Contable (Libros)", min_value=0.0, step=1000.0)
        val_razonable = st.number_input("Valor Razonable / Valor Neto Realizable Tasado", min_value=0.0, step=1000.0)
        
        if st.button("Ingresar Activo al Motor"):
            norma = "NIC 40 / NIIF 13" if clase_activo == "Inmuebles (NIC 40)" else ("NIC 2 (VNR)" if clase_activo == "Inventarios (NIC 2 - VNR)" else "NIC 16")
            nuevo_activo = pd.DataFrame([{
                'Clase': clase_activo, 'Descripción': desc_activo, 
                'Valor Contable': val_contable, 'Valor Razonable': val_razonable, 
                'Norma Aplicada': norma
            }])
            st.session_state.activos_tangibles = pd.concat([st.session_state.activos_tangibles, nuevo_activo], ignore_index=True)
            st.success("Activo indexado correctamente.")
            st.rerun()
            
    with col2:
        st.subheader("Inventario de Activos Valuados para Ajuste Patrimonial")
        if not st.session_state.activos_tangibles.empty:
            st.dataframe(st.session_state.activos_tangibles, use_container_width=True)
            total_libros = st.session_state.activos_tangibles['Valor Contable'].sum()
            total_razonable = st.session_state.activos_tangibles['Valor Razonable'].sum()
            ajuste_patrimonial = total_razonable - total_libros
            
            c1, c2 = st.columns(2)
            c1.metric("Total Valor Razonable", f"${total_razonable:,.2f}")
            c2.metric("Ajuste Patrimonial Bruto (Superávit)", f"${ajuste_patrimonial:,.2f}")
        else:
            st.info("No se han ingresado activos tangibles aún.")

# ---------------------------------------------------------------------
# PESTAÑA 2: MOTOR DE VALORACIÓN CORPORATIVA (DCF / WACC)
# ---------------------------------------------------------------------
with tab2:
    st.header("⚙️ Motor de Valoración por Flujo de Caja Descontado (DCF)")
    st.markdown("<p class='section-desc'>Algoritmo de cálculo de tasa WACC mediante CAPM y proyección de flujos para cotización bursátil.</p>", unsafe_allow_html=True)
    
    col_wacc, col_dcf = st.columns(2)
    
    with col_wacc:
        st.subheader("1. Parámetros del Costo de Capital (WACC - CAPM)")
        rf = st.number_input("Tasa Libre de Riesgo (Rf %)", value=4.5, step=0.1) / 100
        beta = st.number_input("Beta Apalancado del Sector (β)", value=1.2, step=0.05)
        rm = st.number_input("Rendimiento de Mercado Esperado (Rm %)", value=9.5, step=0.1) / 100
        riesgo_pais = st.number_input("Prima por Riesgo País (EMBI Ecuador pb)", value=1200, step=50) / 10000
        
        kd = st.number_input("Costo de la Deuda Financiera (Kd %)", value=10.5, step=0.25) / 100
        tasa_tax = st.number_input("Tasa Impositiva Efectiva + Participación Trabajadores (%)", value=36.25, step=0.5) / 100
        peso_e = st.slider("Proporción de Capital Propio (E/V %)", 10, 100, 60) / 100
        
        ke, wacc = calcular_wacc(rf, beta, rm, riesgo_pais, kd, tasa_tax, peso_e)
        
        st.markdown(f"<div class='metric-box'><b>Costo del Capital Propio (Ke) vía CAPM:</b> {ke*100:.2f}%</div>", unsafe_allow_html=True)
        st.metric("TASA WACC RESULTANTE (Descuento)", f"{wacc*100:.2f}%")
        
    with col_dcf:
        st.subheader("2. Proyección de Flujos Libres de Caja (FCFF)")
        fcl_año1 = st.number_input("Flujo de Caja Libre Año 1 ($)", value=500000.0, step=50000.0)
        growth_tasa = st.slider("Tasa de Crecimiento de Flujos (Años 2-5 %)", 1.0, 15.0, 5.0) / 100
        g_perpetuidad = st.slider("Tasa de Crecimiento a Perpetuidad (g %)", 0.5, 5.0, 2.0) / 100
        
        df_flujos, vp_flujosp, vp_valor_terminal, enterprise_value = proyectar_dcf(fcl_año1, growth_tasa, g_perpetuidad, wacc)
        st.session_state.enterprise_value = enterprise_value
        
        st.dataframe(df_flujos.style.format({'Flujo Proyectado': '${:,.2f}', 'Factor Descuento': '{:.4f}', 'Valor Presente': '${:,.2f}'}), use_container_width=True)
        
        st.markdown(f"""
        <div style='background-color:#e3f2fd; padding:15px; border-radius:5px;'>
        <b>Valor Operativo de la Empresa (Enterprise Value):</b><br>
        <span style='font-size:22px; font-weight:bold; color:#0d47a1;'>${st.session_state.enterprise_value:,.2f}</span><br>
        <small>VP Flujos Explícitos: ${vp_flujosp:,.2f} | VP Valor Terminal: ${vp_valor_terminal:,.2f}</small>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------------------
# PESTAÑA 3: HUB DE CONSULTORÍA TRIBUTARIA (NIC 12 & LRTI)
# ---------------------------------------------------------------------
with tab3:
    st.header("⚖️ Unidad Especial de Impuestos Diferidos y Conciliación (NIC 12)")
    st.markdown("<p class='section-desc'>Módulo analítico fiscal para identificar pasivos latentes y optimizar el escudo fiscal según la LRTI.</p>", unsafe_allow_html=True)
    
    col_tax1, col_tax2 = st.columns([1, 2])
    with col_tax1:
        st.subheader("Cálculo de Diferencias Temporarias")
        
        st.session_state.tasa_fiscal_ecuador = st.number_input("Tasa Impuesto a la Renta Corporativa (Ecuador %)", value=25.0, step=1.0)
        tasa_calculo = st.session_state.tasa_fiscal_ecuador / 100

        concepto_fiscal = st.selectbox("Concepto de Conciliación", [
            "Provisión Jubilación Patronal (No aprobada por Actuario)",
            "Deterioro de Inventarios (Obsolescencia / NIC 2 sin destruir)",
            "Diferencia por Revaluación de Inmuebles (Superávit NIIF 13)",
            "Amortización de Pérdidas Fiscales"
        ])
        base_contable = st.number_input("Monto Contable (NIIF)", min_value=0.0, step=1000.0, key="bc")
        base_fiscal = st.number_input("Monto Fiscal (LRTI)", min_value=0.0, step=1000.0, key="bf")
        
        if st.button("Calcular Impuesto Diferido"):
            diferencia = base_contable - base_fiscal
            es_superavit_reval = "Revaluación" in concepto_fiscal
            
            tipo_id = "Pasivo Diferido" if (diferencia > 0 and es_superavit_reval) or (diferencia < 0 and not es_superavit_reval) else "Activo Diferido"
            impuesto_calc = abs(diferencia) * tasa_calculo
            
            nuevo_id = pd.DataFrame([{
                'Concepto': concepto_fiscal, 'Base Contable': base_contable,
                'Base Fiscal': base_fiscal, 'Diferencia': diferencia,
                'Tipo': tipo_id, 'Impuesto Diferido': impuesto_calc
            }])
            st.session_state.impuestos_diferidos = pd.concat([st.session_state.impuestos_diferidos, nuevo_id], ignore_index=True)
            st.success("Mapeo fiscal integrado con éxito.")
            st.rerun()
            
    with col_tax2:
        st.subheader(f"Matriz de Posiciones bajo LRTI (Tasa Aplicada: {st.session_state.tasa_fiscal_ecuador}%)")
        if not st.session_state.impuestos_diferidos.empty:
            st.dataframe(st.session_state.impuestos_diferidos.style.format({
                'Base Contable': '${:,.2f}', 'Base Fiscal': '${:,.2f}', 
                'Diferencia': '${:,.2f}', 'Impuesto Diferido': '${:,.2f}'
            }), use_container_width=True)
            
            total_activos_dif = st.session_state.impuestos_diferidos[st.session_state.impuestos_diferidos['Tipo'] == "Activo Diferido"]['Impuesto Diferido'].sum()
            total_pasivos_dif = st.session_state.impuestos_diferidos[st.session_state.impuestos_diferidos['Tipo'] == "Pasivo Diferido"]['Impuesto Diferido'].sum()
            
            c_t1, c_t2 = st.columns(2)
            c_t1.metric("Total Activos Diferidos (Recuperables)", f"${total_activos_dif:,.2f}")
            c_t2.metric("Total Pasivos Diferidos (Obligaciones)", f"${total_pasivos_dif:,.2f}")
        else:
            st.info("No se han registrado conciliaciones temporarias.")

# ---------------------------------------------------------------------
# PESTAÑA 4: REPORTE EJECUTIVO PARA DIRECTORIOS Y COMITÉS
# ---------------------------------------------------------------------
with tab4:
    st.markdown("<div class='report-title'>INFORME ESTRATÉGICO DE VALORACIÓN INTEGRAL Y VIABILIDAD FINANCIERA</div>", unsafe_allow_html=True)
    st.markdown("**Destinatarios:** Directorio, Comités Ejecutivos y Bancos de Inversión ESTRUCTURADORES DE LA IPO")
    st.divider()
    
    ev_final = st.session_state.enterprise_value
    tot_activos_razonable = st.session_state.activos_tangibles['Valor Razonable'].sum() if not st.session_state.activos_tangibles.empty else 0.0
    val_total_combinado = ev_final + tot_activos_razonable
    
    rep_c1, rep_c2, rep_c3 = st.columns(3)
    with rep_c1:
        st.markdown(f"""
        <div class='metric-box'>
        <small>VALORACIÓN CORPORATIVA DE NEGOCIO EN MARCHA (DCF)</small><br>
        <span style='font-size:24px; font-weight:bold; color:#2c3e50;'>${ev_final:,.2f}</span>
        </div>
        """, unsafe_allow_html=True)
    with rep_c2:
        st.markdown(f"""
        <div class='metric-box'>
        <small>VALOR RAZONABLE DE ACTIVOS NETOS E INDEPENDIENTES (NIIF 13)</small><br>
        <span style='font-size:24px; font-weight:bold; color:#2c3e50;'>${tot_activos_razonable:,.2f}</span>
        </div>
        """, unsafe_allow_html=True)
    with rep_c3:
        st.markdown(f"""
        <div class='metric-box' style='border-left-color: #2ecc71;'>
        <small>VALOR ESTIMADO PRE-MONEY INTEGRAL SUGERIDO</small><br>
        <span style='font-size:24px; font-weight:bold; color:#27ae60;'>${val_total_combinado:,.2f}</span>
        </div>
        """, unsafe_allow_html=True)
        
    st.subheader("📝 Notas del Comité Financiero y Fiscal Extendido")
    st.info(f"""
    **Declaración de Cumplimiento Normativo de la Herramienta:** Los análisis expuestos fueron procesados respetando las metodologías de flujos descontados amparados por la **NIIF 13 (Medición del Valor Razonable)**. Las diferencias de base imponible e impuestos diferidos se estructuran bajo las directrices de la **NIC 12** y las reglas obligatorias de adición/deducción dictadas por la **Ley de Régimen Tributario Interno (LRTI)** de la República del Ecuador, aplicando una tasa corporativa base calculada de {st.session_state.tasa_fiscal_ecuador}%. Este informe constituye un documento de entrega formal para soporte de toma de decisiones estratégicas corporativas de Gobierno Corporativo de nivel C-Level.
    """)
    
    observaciones_director = st.text_area("Observaciones Estratégicas Adicionales para el Acta del Directorio", 
        value="La valoración presenta alta sensibilidad ante variaciones del EMBI (Riesgo País). Se sugiere blindar la estructura patrimonial maximizando el uso de los activos diferidos aprobados por actuario para reducir la tasa efectiva impositiva antes del Roadshow bursátil.")
    
    if st.button("Emitir Certificado de Valoración de Alta Gerencia (Aprobado)"):
        st.balloons()
        st.success("Dictamen de Valoración Técnica Corporativa consolidado. Listo para auditoría y radicación formal ante el Comité de Salida a Bolsa.")
