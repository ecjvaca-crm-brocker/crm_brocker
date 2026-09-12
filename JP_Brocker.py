import streamlit as str_app
import urllib.parse
import sqlite3
import pandas as pd
import numpy as np
import tempfile
import os
import time
import concurrent.futures
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
import matplotlib.pyplot as plt
import yfinance as yf

# ==============================================================================
# 1. CONFIGURACIONES INICIALES Y ESTADOS GLOBALES DE LA PÁGINA
# ==============================================================================
NUMERO_WHATSAPP = "593998076979" 
PASSWORD_DASHBOARD = "Escala2026" 

str_app.set_page_config(
    page_title="Escala| Consultoria financera emresarial ", 
    page_icon="🏛️", 
    layout="wide"
)

URL_FOTO_ASESOR = "https://raw.githubusercontent.com/ecjvaca-crm-brocker/crm_brocker/main/IMGAENJONAS.jpeg"
URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/1DiKGC8Q65SjouMutswiF00hsdbAXTIV5yDlGXGEAZnU/edit?gid=1469424641#gid=1469424641"

# Inicialización de Estados Globales
if 'activos_tangibles' not in str_app.session_state:
    str_app.session_state.activos_tangibles = pd.DataFrame(columns=['Clase', 'Descripción', 'Valor Contable', 'Valor Razonable', 'Norma Aplicada'])

if 'impuestos_diferidos' not in str_app.session_state:
    str_app.session_state.impuestos_diferidos = pd.DataFrame(columns=['Concepto', 'Base Contable', 'Base Fiscal', 'Diferencia', 'Tipo', 'Impuesto Diferido'])

if 'enterprise_value' not in str_app.session_state:
    str_app.session_state.enterprise_value = 0.0

if 'tasa_fiscal_ecuador' not in str_app.session_state:
    str_app.session_state.tasa_fiscal_ecuador = 25.0

if 'ofertas_brokerage' not in str_app.session_state:
    str_app.session_state.ofertas_brokerage = []

# ==============================================================================
# 2. CAPA DE PERSISTENCIA Y BASE DE DATOS LOCAL (SQLITE)
# ==============================================================================
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
        csv_url = url_sheet.split("/edit")[0] + "/export?format=csv" if "edit" in url_sheet else url_sheet
        df = pd.read_csv(csv_url)
        if "<html" in str(df.iloc[0, 0]).lower():
            return pd.DataFrame()
        return df
    except Exception:
        return pd.DataFrame()

init_db()

# ==============================================================================
# 3. MOTOR FINANCIERO,
# ==============================================================================
ENTIDADES_ALIADAS = [
    {"id": "BANCO_A", "nombre": "Banco Guayaquil / Microcrédito", "tasa_base": 15.5, "tiempo_seg": 2.5, "max_monto": 25000},
    {"id": "BANCO_B", "nombre": "Banco Pichincha / Pymes", "tasa_base": 14.8, "tiempo_seg": 4.1, "max_monto": 50000},
    {"id": "COOP_C", "nombre": "Cooperativa Juventud Ecuatoriana Progresista (JEP)", "tasa_base": 16.0, "tiempo_seg": 1.8, "max_monto": 15000},
    {"id": "COOP_D", "nombre": "Cooperativa Atuntaqui", "tasa_base": 15.2, "tiempo_seg": 3.0, "max_monto": 20000},
    {"id": "MICRO_E", "nombre": "Microfinanciera Solidaria D-Miro", "tasa_base": 17.5, "tiempo_seg": 1.2, "max_monto": 10000}
]

def consultar_entidad_api(entidad, datos_solicitud):
    """Simula o ejecuta la petición API hacia el Core Bancario o Cooperativa."""
    time.sleep(entidad["tiempo_seg"]) # Simulación de tiempo de latencia/red
    
    # Regla de simulación de aprobación basada en la capacidad del negocio
    monto_sol = datos_solicitud["monto"]
    if monto_sol <= entidad["max_monto"]:
        # Variación aleatoria controlada de la oferta final
        tasa_ofrecida = entidad["tasa_base"] + np.random.choice([-0.5, 0.0, 0.5])
        monto_aprobado = min(monto_sol, entidad["max_monto"])
        return {
            "entidad": entidad["nombre"],
            "estado": "APROBADO",
            "monto_ofrecido": monto_aprobado,
            "tasa_anual": round(tasa_ofrecida, 2),
            "plazo_meses": datos_solicitud["plazo"],
            "tiempo_respuesta_seg": entidad["tiempo_seg"]
        }
    else:
        return {
            "entidad": entidad["nombre"],
            "estado": "RECHAZADO",
            "motivo": "Monto excede el límite de la política interna de la entidad."
        }

def procesar_envio_multibanco_async(datos_solicitud):
    """Envía la solicitud en paralelo a todas las entidades bancarias aliadas."""
    resultados = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(consultar_entidad_api, entidad, datos_solicitud)
            for entidad in ENTIDADES_ALIADAS
        ]
        for future in concurrent.futures.as_completed(futures):
            resultados.append(future.result())
    return resultados

def calcular_score_oferta(oferta):
    """
    Algoritmo de Adjudicación Automática.
    Evalúa: Velocidad de respuesta (30%), Menor Tasa (40%), Monto (20%), Plazo (10%).
    """
    if oferta["estado"] != "APROBADO":
        return -1
    
    peso_tasa = 0.40
    peso_velocidad = 0.30
    peso_monto = 0.20
    peso_plazo = 0.10
    
    score_tasa = (1 / oferta["tasa_anual"]) * 100
    score_velocidad = (1 / oferta["tiempo_respuesta_seg"]) * 10
    score_monto = oferta["monto_ofrecido"] / 1000
    score_plazo = oferta["plazo_meses"] / 12
    
    return (score_tasa * peso_tasa) + (score_velocidad * peso_velocidad) + (score_monto * peso_monto) + (score_plazo * peso_plazo)

def adjudicar_mejor_oferta(ofertas):
    aprobadas = [o for o in ofertas if o["estado"] == "APROBADO"]
    if not aprobadas:
        return None, []
    
    # Ordenar por el score calculado de mayor a menor
    ordenadas = sorted(aprobadas, key=calcular_score_oferta, reverse=True)
    return ordenadas[0], ordenadas

# ==============================================================================
# 4. GENERADOR DE INFORMES PDF Y GRÁFICOS 
# ==============================================================================
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
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}} | Uso Exclusivo - Escala Consultoría Empresarial y Financiera", 0, 0, "C")

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
    empresa = "Escala Consultoría Empresarial"
    representante = "Jonathan Vaca"
    
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
    pdf.multi_cell(0, 4.5, "La empresa presenta una condicion de Vulnerabilidad Estructural Critica (Indice de Salud de Gestion: 28/100). El diagnostico revela alta dependencia operativa del fundador y tension en liquidez a corto plazo.")
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
# 5. HOJAS DE ESTILO CSS PERSONALIZADAS
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
    .metric-box {
        background-color: #f8f9fa; 
        border-left: 5px solid #10B981; 
        padding: 15px; 
        border-radius: 6px; 
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
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
    @keyframes slideAnimation {
        0% { transform: translateX(0); }
        20% { transform: translateX(-20%); }
        40% { transform: translateX(-40%); }
        60% { transform: translateX(-60%); }
        80% { transform: translateX(-80%); }
        100% { transform: translateX(0); }
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 6. CABECERA Y NAVEGACIÓN PRINCIPAL
# ==============================================================================
str_app.markdown("<h1 style='text-align: center; font-size: 2.8rem; margin-bottom: 0;'>🏛️ Escala Consultoria financiera empresarial </h1>", unsafe_allow_html=True)
str_app.markdown("<p style='text-align: center; color: #D4AF37; font-size: 1.4rem; font-weight: bold; margin-top: 0;'>Ecosistema Digital de Brokerage Financiero B2B2C e Inteligencia Fiscal</p>", unsafe_allow_html=True)
str_app.write("")

tab_brokerage, tab_herramientas, tab_valuacion_tax, tab_cresa = str_app.tabs([
    "⚡ Crédito & Precalificación (B2B2C)", 
    "🧮 Simuladores, CDP, Retiro & Amortización",
    "📈 Premium Valuation & Tax Hub (NIIF / LRTI)",
    "🌐 Ecosistema CRESA & Validadores"
])

# ==============================================================================
# PESTAÑA 1: MOTOR DIGITAL DE CRÉDITO  B2B2C
# ==============================================================================
with tab_brokerage:
    str_app.markdown("""
    <div class="card-corporativa" style="border-top: 5px solid #10B981;">
        <h3>🚀 Plataforma de Intermediación y Subasta Crediticia en Tiempo Real</h3>
        <p style='color: #4A5568;'>Diseñado para comercios informales (tiendas, ropa, abarrotes) y Pymes. Digitaliza tu expediente, precalifica e ingresa a subasta paralela con Bancos y Cooperativas aliadas.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with str_app.form("form_marketplace_credito", clear_on_submit=False):
        str_app.subheader("1. Datos Generales del Negocio o Comercio")
        col_m1, col_m2, col_m3 = str_app.columns(3)
        with col_m1:
            nombre_cliente = str_app.text_input("Nombre / Solicitante:", placeholder="Ej: Juan Carlos Pérez")
            tipo_actividad = str_app.selectbox("Sector / Actividad Comercial:", ["Comercio al por menor (Abarrotes, Tiendas)", "Venta de Ropa y Calzado", "Servicios (Talleres, Estéticas)", "Gastronomía / Alimentos", "Otro"])
        with col_m2:
            cedula_cliente = str_app.text_input("Número de Cédula:", max_chars=10, placeholder="Ej: 100xxxxxxx")
            monto_solicitado = str_app.number_input("Monto de Crédito Requerido ($):", min_value=500.0, value=3000.0, step=250.0)
        with col_m3:
            telefono_cliente = str_app.text_input("Celular / WhatsApp:", placeholder="Ej: 099xxxxxxx")
            plazo_deseado = str_app.selectbox("Plazo Requerido (Meses):", [6, 12, 18, 24, 36, 48, 60], index=3)
            
        str_app.subheader("2. Carga del Expediente Digital (Documentación Obligatoria)")
        str_app.caption("Carga fotos legibles o archivos PDF para la evaluación inmediata de riesgos.")
        
        col_f1, col_f2, col_f3 = str_app.columns(3)
        with col_f1:
            doc_cedula = str_app.file_uploader("🪪 Cédula / Identificación (Frontal y Posterior)", type=["pdf", "png", "jpg", "jpeg"])
        with col_f2:
            doc_ingresos = str_app.file_uploader("📦 Soportes de Ingresos / Fotos Negocio / Facturas Proveedor", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True)
        with col_f3:
            doc_servicio_basico = str_app.file_uploader("🏠 Planilla de Servicio Básico / RUC (Opcional)", type=["pdf", "png", "jpg", "jpeg"])
            
        btn_enviar_subasta = str_app.form_submit_button("🔥 Iniciar Subasta de Crédito en Tiempo Real 🚀")

    if btn_enviar_subasta:
        if not nombre_cliente or not cedula_cliente or not doc_cedula:
            str_app.error("⚠️ Se requiere ingresar el Nombre, Cédula y subir el Documento de Identidad.")
        else:
            with str_app.spinner("Procesando precalificación y consultando APIs de Bancos y Cooperativas aliadas..."):
                datos_sol = {
                    "nombre": nombre_cliente,
                    "monto": monto_solicitado,
                    "plazo": plazo_deseado
                }
                # Ejecutar motor asíncrono
                resultados_subasta = procesar_envio_multibanco_async(datos_sol)
                str_app.session_state.ofertas_brokerage = resultados_subasta
                
            guardar_lead(nombre_cliente, cedula_cliente, telefono_cliente, "Brokerage Digital", f"Monto: ${monto_solicitado} - {tipo_actividad}")
            str_app.success("✅ ¡Expediente ruteado exitosamente a la red de entidades financieras!")

    # Desplegar Resultados de la Adjudicación si existen
    if str_app.session_state.ofertas_brokerage:
        oferta_ganadora, ranking_ofertas = adjudicar_mejor_oferta(str_app.session_state.ofertas_brokerage)
        
        if oferta_ganadora:
            str_app.markdown("---")
            str_app.markdown(f"""
            <div style="background-color: #ECFDF5; border: 2px solid #10B981; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h2 style="color: #047857 !important; margin: 0;">🏆 ¡OFERTA GANADORA ADJUDICADA PARA EL CLIENTE!</h2>
                <p style="font-size: 1.1rem; color: #065F46; margin-top: 5px;">Esta entidad ofreció la mejor combinación de velocidad, tasa de interés y monto aprobatorio.</p>
            </div>
            """, unsafe_allow_html=True)
            
            c_win1, c_win2, c_win3, c_win4 = str_app.columns(4)
            c_win1.metric("Entidad Adjudicada", oferta_ganadora["entidad"])
            c_win2.metric("Monto Aprobado", f"${oferta_ganadora['monto_ofrecido']:,.2f}")
            c_win3.metric("Tasa de Interés (TEA)", f"{oferta_ganadora['tasa_anual']}%")
            c_win4.metric("Tiempo de Respuesta", f"{oferta_ganadora['tiempo_respuesta_seg']} seg")
            
            # WhatsApp Directo con la oferta
            msg_ws_adjudicado = f"¡Hola Escala Finance! Mi crédito por ${monto_solicitado} ha sido ADJUDICADO a {oferta_ganadora['entidad']} con una tasa de {oferta_ganadora['tasa_anual']}%. Deseo proceder con el desembolso."
            url_ws_adj = f"https://api.whatsapp.com/send?phone={NUMERO_WHATSAPP}&text={urllib.parse.quote(msg_ws_adjudicado)}"
            str_app.link_button("🟢 Formalizar Desembolso de Crédito Adjudicado vía WhatsApp", url_ws_adj, type="primary")

            str_app.subheader("📊 Cuadro Comparativo de Todas las Ofertas Recibidas")
            df_ranking = pd.DataFrame(ranking_ofertas)
            str_app.dataframe(df_ranking[['entidad', 'estado', 'monto_ofrecido', 'tasa_anual', 'plazo_meses', 'tiempo_respuesta_seg']], use_container_width=True)
        else:
            str_app.warning("Ninguna entidad crediticia aprobó la solicitud con los parámetros actuales. Te recomendamos ajustar el monto o revisar el CDP en la pestaña de simuladores.")

# ==============================================================================
# PESTAÑA 2: SIMULADORES, CAPACIDAD DE PAGO, RETIRO Y AMORTIZACIÓN
# ==============================================================================
with tab_herramientas:
    sub_herr1, sub_herr2, sub_herr3 = str_app.tabs(["🧮 Simulador CDP & Scoring", "📋 Tabla de Amortización Francesa", "🎯 Planificador de Retiro"])
    
    with sub_herr1:
        str_app.markdown("#### 1. Simulador de Cuotas y Capacidad de Pago (CDP)")
        col_c1, col_c2, col_c3 = str_app.columns(3)
        with col_c1:
            m_prestamo = str_app.number_input("Monto del Crédito ($):", min_value=100.0, value=10000.0, key="sim_monto")
        with col_c2:
            t_anual = str_app.number_input("Tasa de Interés Anual (%):", min_value=1.0, value=15.0, key="sim_tasa")
        with col_c3:
            p_meses = str_app.selectbox("Plazo (Meses):", [12, 24, 36, 48, 60], index=2, key="sim_plazo")
            
        i_mensual = (t_anual / 100) / 12
        cuota = m_prestamo * (i_mensual * (1 + i_mensual)**p_meses) / ((1 + i_mensual)**p_meses - 1) if i_mensual > 0 else m_prestamo / p_meses
        
        r1, r2, r3 = str_app.columns(3)
        r1.metric("💵 Cuota Mensual Estimada", f"${cuota:,.2f}")
        r2.metric("📈 Total Intereses", f"${(cuota*p_meses)-m_prestamo:,.2f}")
        r3.metric("💰 Total a Pagar", f"${cuota*p_meses:,.2f}")
        
        str_app.markdown("---")
        str_app.markdown("#### 2. Diagnóstico de Capacidad de Pago (CDP)")
        ing_n = str_app.number_input("Ingresos Mensuales Netos ($):", value=1500.0, key="cdp_ing")
        egr_f = str_app.number_input("Egresos Fijos Mensuales ($):", value=500.0, key="cdp_egr")
        deu_v = str_app.number_input("Pago de Otras Deudas ($):", value=200.0, key="cdp_deu")
        
        excedente = ing_n - egr_f - deu_v
        cdp_disp = max(0.0, min(excedente * 0.8, ing_n * 0.45))
        
        c_res1, c_res2 = str_app.columns(2)
        c_res1.metric("💼 Excedente Mensual", f"${excedente:,.2f}")
        c_res2.metric("🛡️ Cuota Máxima Recomendada (CDP)", f"${cdp_disp:,.2f}")

    with sub_herr2:
        str_app.markdown("#### 📋 Generador de Cronograma de Pagos (Tabla Francesa)")
        m_t = str_app.number_input("Capital ($):", value=20000.0, key="amort_monto")
        t_t = str_app.number_input("Tasa Anual (%):", value=12.0, key="amort_tasa")
        p_t = str_app.selectbox("Plazo (Meses):", [12, 24, 36, 48, 60], index=2, key="amort_plazo")
        
        if str_app.button("⚙️ Calcular Cronograma"):
            tm = (t_t / 100) / 12
            c_fija = m_t * (tm * (1 + tm)**p_t) / ((1 + tm)**p_t - 1)
            saldo = m_t
            cronograma = []
            for mes in range(1, p_t + 1):
                i_mes = saldo * tm
                cap_mes = c_fija - i_mes
                saldo -= cap_mes
                cronograma.append({
                    "Mes": mes, "Cuota": round(c_fija, 2), 
                    "Interés": round(i_mes, 2), "Abono Capital": round(cap_mes, 2), 
                    "Saldo Final": round(max(0, saldo), 2)
                })
            str_app.dataframe(pd.DataFrame(cronograma), use_container_width=True)

    with sub_herr3:
        str_app.markdown("#### 🎯 Planificador de Retiro y Jubilación Patrimonial")
        e_act = str_app.number_input("Edad Actual:", value=35)
        e_ret = str_app.number_input("Edad de Retiro:", value=60)
        g_ret = str_app.number_input("Gasto Mensual Deseado ($):", value=2000.0)
        
        capital_obj = (g_ret * 12) / 0.05
        str_app.markdown(f"""
        <div style="background:#FFFFFF; padding:20px; border-radius:10px; border-left:5px solid #10B981; border:1px solid #E5E7EB;">
            <h4>📊 Fondo de Retiro Necesario</h4>
            <p>⏳ Tiempo restante: <b>{e_ret - e_act} años</b></p>
            <p>💰 Capital Objetivo Recomendado (al 5% de rendimiento): <b>${capital_obj:,.2f}</b></p>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# PESTAÑA 3: PREMIUM VALUATION & TAX HUB (VALORACIÓN Y LEY TRIBUTARIA)
# ==============================================================================
with tab_valuacion_tax:
    v_tab1, v_tab2, v_tab3, v_tab4 = str_app.tabs([
        "1. Activos (NIIF 13 / NIC 16)", 
        "2. DCF & Costo de Capital WACC", 
        "3. Impuestos Diferidos (NIC 12 & LRTI)", 
        "4. Reporte Ejecutivo"
    ])
    
    with v_tab1:
        str_app.subheader("🏢 Registro y Revaluación de Activos under NIIF")
        c_act1, c_act2 = str_app.columns([1, 2])
        with c_act1:
            clase = str_app.selectbox("Clase Activo", ["Vehículos (NIC 16)", "Maquinaria (NIC 16)", "Inmuebles (NIC 40)", "Inventario (NIC 2)"])
            desc = str_app.text_input("Descripción Activo", "Planta Industrial Pifo")
            v_cont = str_app.number_input("Valor Contable ($)", value=50000.0)
            v_raz = str_app.number_input("Valor Razonable Tasado ($)", value=75000.0)
            if str_app.button("Ingresar Activo"):
                nuevo = pd.DataFrame([{'Clase': clase, 'Descripción': desc, 'Valor Contable': v_cont, 'Valor Razonable': v_raz, 'Norma Aplicada': 'NIIF'}])
                str_app.session_state.activos_tangibles = pd.concat([str_app.session_state.activos_tangibles, nuevo], ignore_index=True)
                str_app.rerun()
        with c_act2:
            if not str_app.session_state.activos_tangibles.empty:
                str_app.dataframe(str_app.session_state.activos_tangibles, use_container_width=True)
                str_app.metric("Total Valor Razonable", f"${str_app.session_state.activos_tangibles['Valor Razonable'].sum():,.2f}")

    with v_tab2:
        str_app.subheader("⚙️ Motor de Valoración por Flujo de Caja Descontado (DCF)")
        cw1, cw2 = str_app.columns(2)
        with cw1:
            rf = str_app.number_input("Rf (%)", value=4.5) / 100
            beta = str_app.number_input("Beta (β)", value=1.2)
            rm = str_app.number_input("Rm (%)", value=9.5) / 100
            rp = str_app.number_input("Riesgo País (pb)", value=1200) / 10000
            kd = str_app.number_input("Kd (%)", value=10.5) / 100
            tax = str_app.number_input("Tasa Impositiva (%)", value=36.25) / 100
            peso_e = str_app.slider("Proporción Equity (%)", 10, 100, 60) / 100
            
            ke = rf + beta * (rm - rf) + rp
            wacc = (peso_e * ke) + ((1 - peso_e) * kd * (1 - tax))
            str_app.metric("WACC Resultante", f"{wacc*100:.2f}%")
        with cw2:
            fcl1 = str_app.number_input("Flujo Libre Año 1 ($)", value=500000.0)
            g_rate = str_app.slider("Crecimiento Años 2-5 (%)", 1.0, 15.0, 5.0) / 100
            g_perp = str_app.slider("Crecimiento Perpetuidad (%)", 0.5, 5.0, 2.0) / 100
            
            flujos = [fcl1 * ((1 + g_rate)**i) for i in range(5)]
            vp_flujos = sum([f / ((1 + wacc)**(i+1)) for i, f in enumerate(flujos)])
            v_term = (flujos[-1] * (1 + g_perp)) / (wacc - g_perp)
            vp_vterm = v_term / ((1 + wacc)**5)
            enterprise_value = vp_flujos + vp_vterm
            str_app.session_state.enterprise_value = enterprise_value
            str_app.metric("Enterprise Value (Valor Operativo)", f"${enterprise_value:,.2f}")

    with v_tab3:
        str_app.subheader("⚖️ Conciliación de Impuestos Diferidos (NIC 12 & LRTI)")
        ci1, ci2 = str_app.columns([1, 2])
        with ci1:
            concepto = str_app.selectbox("Concepto", ["Provisión Jubilación Patronal", "Deterioro Inventario", "Superávit Revaluación"])
            bc = str_app.number_input("Base Contable", value=10000.0)
            bf = str_app.number_input("Base Fiscal", value=0.0)
            if str_app.button("Calcular Impuesto Diferido"):
                dif = bc - bf
                imp = abs(dif) * (str_app.session_state.tasa_fiscal_ecuador / 100)
                tipo = "Pasivo Diferido" if "Revaluación" in concepto else "Activo Diferido"
                nuevo_id = pd.DataFrame([{'Concepto': concepto, 'Base Contable': bc, 'Base Fiscal': bf, 'Diferencia': dif, 'Tipo': tipo, 'Impuesto Diferido': imp}])
                str_app.session_state.impuestos_diferidos = pd.concat([str_app.session_state.impuestos_diferidos, nuevo_id], ignore_index=True)
                str_app.rerun()
        with ci2:
            if not str_app.session_state.impuestos_diferidos.empty:
                str_app.dataframe(str_app.session_state.impuestos_diferidos, use_container_width=True)

    with v_tab4:
        str_app.subheader("INFORME ESTRATÉGICO DE VALORACIÓN INTEGRAL")
        ev_f = str_app.session_state.enterprise_value
        act_f = str_app.session_state.activos_tangibles['Valor Razonable'].sum() if not str_app.session_state.activos_tangibles.empty else 0.0
        str_app.metric("VALOR TOTAL COMBINADO PRE-MONEY", f"${ev_f + act_f:,.2f}")

# ==============================================================================
# PESTAÑA 4: ECOSISTEMA CRESA & SOCIAL SELLING
# ==============================================================================
with tab_cresa:
    str_app.markdown("""
    <div class="card-corporativa" style="border-top: 5px solid #0A2540;">
        <h3>🌐 Ecosistema de Validación y Consultas CRESA</h3>
        <p style='color: #4A5568;'>Herramientas institucionales de verificación de identidad, RUC, cobertura de salud y canales comerciales.</p>
    </div>
    """, unsafe_allow_html=True)
    
    sub_c1, sub_c2 = str_app.tabs(["📋 Plataformas de Consulta y Validación", "🛒 Social Selling"])
    with sub_c1:
        col_c1, col_c2 = str_app.columns(2)
        with col_c1:
            str_app.link_button("🚀 Abrir Plataforma Nexum 360", "https://nexum360.com.ec/", use_container_width=True)
            str_app.link_button("🔍 Consultar RUC en SRI", "https://srienlinea.sri.gob.ec/sri-en-linea/SriRucWeb/ConsultaRuc/Consultas/consultaRuc", use_container_width=True)
            str_app.link_button("📋 IESS - Certificado de Afiliación", "https://www.iess.gob.ec/afiliado-web/pages/opcionesGenerales/seleccionCertificadoDeAfiliacion.jsf", use_container_width=True)
        with col_c2:
            str_app.link_button("🩺 Consultar Cobertura en Salud (MSP)", "https://coberturasalud.msp.gob.ec/", use_container_width=True)
            str_app.link_button("🚦 Consultar Multas ANT", "https://consultaweb.ant.gob.ec/PortalWEB/paginas/clientes/clp_criterio_consulta.jsp", use_container_width=True)
            str_app.link_button("📝 Registrar Prospecto (Nexum)", "https://nexum360.com.ec/oficina virtual/nuevo-prospecto", use_container_width=True)
            
    with sub_c2:
        sc1, sc2, sc3 = str_app.columns(3)
        with sc1:
            str_app.link_button("🏠 Orve Hogar", "https://www.orvehogar.com", use_container_width=True)
        with sc2:
            str_app.link_button("⚡ Almacenes Japón", "https://www.almacenesjapon.com", use_container_width=True)
        with sc3:
            str_app.link_button("💳 Créditos Económicos", "https://www.creditoseconomicos.com", use_container_width=True)

# ==============================================================================
# SECCIÓN INFERIOR: INDICADORES EN TIEMPO REAL & PANEL ADMINISTRATIVO
# ==============================================================================
str_app.write("---")
str_app.markdown("### 📊 Indicadores Económicos en Tiempo Real")

@str_app.cache_data(ttl=300)
def obtener_indicadores():
    tickers = {"S&P 500": "^GSPC", "NASDAQ 100": "^NDX", "Petróleo WTI": "USO", "Oro": "GLD", "Bitcoin": "BTC-USD"}
    res = {}
    for k, v in tickers.items():
        try:
            hist = yf.Ticker(v).history(period="2d")
            if len(hist) >= 2:
                p_act = hist['Close'].iloc[-1]
                p_ant = hist['Close'].iloc[-2]
                pct = ((p_act - p_ant) / p_ant) * 100
                res[k] = (f"${p_act:,.2f}", f"{pct:+.2f}%")
            else: res[k] = ("N/A", "0.00%")
        except: res[k] = ("N/A", "0.00%")
    return res

datos_m = obtener_indicadores()
m1, m2, m3, m4, m5 = str_app.columns(5)
for i, (k, v) in enumerate(datos_m.items()):
    val, delta = v
    if i == 0: m1.metric(f"📈 {k}", val, delta)
    elif i == 1: m2.metric(f"💻 {k}", val, delta)
    elif i == 2: m3.metric(f"🛢️ {k}", val, delta)
    elif i == 3: m4.metric(f"🥇 {k}", val, delta)
    elif i == 4: m5.metric(f"🪙 {k}", val, delta)

# Panel de Administración
with str_app.expander("🔒 Acceso a Panel Administrador"):
    pwd = str_app.text_input("Contraseña de Administrador:", type="password")
    if pwd == PASSWORD_DASHBOARD:
        str_app.success("Acceso con privilegios de Administrador.")
        df_l = leer_leads()
        str_app.dataframe(df_l, use_container_width=True)
