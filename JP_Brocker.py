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

# ==========================================
# 1. CONFIGURACIONES INICIALES GENERALES
# ==========================================
NUMERO_WHATSAPP = "593998076979" 
PASSWORD_DASHBOARD = "Escala2026" 

str_app.set_page_config(
    page_title="Escala Consultoría Empresarial y Financiera", 
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

# ==========================================
# 4. IDENTIDAD VISUAL PREMIUM Y ANIMACIONES (CSS)
# ==========================================
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
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 5. CABECERA PRINCIPAL Y HERRAMIENTA EXTERNA + CALCULADORA & SCORING
# ==========================================
str_app.markdown("<h1 style='text-align: center; font-size: 2.8rem; margin-bottom: 0;'>🏛️ Escala Consultoría Empresarial y Financiera</h1>", unsafe_allow_html=True)
str_app.markdown("<p style='text-align: center; color: #D4AF37; font-size: 1.4rem; font-weight: bold; margin-top: 0;'>Tu consultor financiero de confianza</p>", unsafe_allow_html=True)
str_app.write("")

tab_principal_herramienta, tab_principal_calculadora = str_app.tabs(["🚀 Herramienta Financiera (Golden Ledger)", "🧮 Simulador, Capacidad de Pago y Scoring"])

with tab_principal_herramienta:
    str_app.markdown("""
    <div class="card-corporativa">
        <h3>📊 Ecosistema de Finanzas Personales & Corporativas</h3>
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
        <h3>🧮 Simulador Financiero Avanzado (Dependientes e Independientes RUC)</h3>
        <p style='color: #4A5568;'>Emulación exacta del simulador del archivo Excel. Realiza cálculos para clientes Dependientes (Sueldo) e Independientes (RUC con listado completo de la columna A) y evalúa su capacidad de pago y scoring.</p>
    </div>
    """, unsafe_allow_html=True)
    
    subtab_sim1, subtab_sim2_dep, subtab_sim2_ind, subtab_sim3 = str_app.tabs([
        "💡 Simulador de Crédito", 
        "👔 Ingresos Dependientes (Sueldos)", 
        "🏢 Ingresos Independientes (RUC Completo)", 
        "📊 Análisis de Scoring & Calificación"
    ])
    
    with subtab_sim1:
        str_app.markdown("#### Parámetros del Crédito")
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

    with subtab_sim2_dep:
        str_app.markdown("#### 👔 Cálculo de Capacidad de Pago para Clientes Dependientes (Relación de Dependencia)")
        str_app.caption("Emulación de ingresos por roles de pago, aportes al IESS y deducciones de obligaciones financieras vigentes.")
        
        dep_c1, dep_c2 = str_app.columns(2)
        with dep_c1:
            sueldo_basico_mensual = str_app.number_input("Sueldo Nominal Mensual ($):", min_value=0.0, value=1200.0, step=100.0, key="dep_sueldo_input")
            otros_ingresos_fijos = str_app.number_input("Otros Ingresos Fijos (Horas extras / Comisiones promedio) [$]:", min_value=0.0, value=150.0, step=50.0, key="dep_otros_input")
        with dep_c2:
            descuentos_iess = sueldo_basico_mensual * 0.0945
            str_app.info(f"📌 **Aporte Personal IESS (9.45%):** `- ${descuentos_iess:,.2f}`")
            otros_egresos_mes = str_app.number_input("Otras Obligaciones / Descuentos Mensuales en Rol [$]:", min_value=0.0, value=100.0, step=50.0, key="dep_egresos_input")
            
        ingreso_neto_dependiente = sueldo_basico_mensual + otros_ingresos_fijos - descuentos_iess - otros_egresos_mes
        
        str_app.markdown("---")
        str_app.markdown("#### Resultado del Análisis de Capacidad (Dependiente)")
        
        dres1, dres2, dres3 = str_app.columns(3)
        dres1.metric("💼 Ingresos Totales Brutos", f"${sueldo_basico_mensual + otros_ingresos_fijos:,.2f}")
        dres2.metric("📉 Deducciones Ley / IESS", f"${descuentos_iess + otros_egresos_mes:,.2f}")
        dres3.metric("✨ Ingreso Neto Disponible", f"${ingreso_neto_dependiente:,.2f}")

    with subtab_sim2_ind:
        str_app.markdown("#### 🏢 Cálculo de Ingresos Netos para Clientes Independientes (Actividad Comercial / RUC - Columna A Completa)")
        str_app.caption("Listado completo de todos los códigos y actividades de la Columna A del archivo Excel para aplicar el margen de rentabilidad H30 exacto.")
        
        @str_app.cache_data
        def cargar_tabla_rentabilidades_completa():
            return pd.DataFrame({
                "Codigo_RUC": [
                    "A01", "A02", "B05", "C10", "C11", "D35", "F41", "F43", "G45", "G46", 
                    "G47", "H55", "I56", "J58", "J62", "K64", "L68", "M69", "M70", "M71", 
                    "N79", "O84", "P85", "Q86", "R90", "S95", "S96"
                ],
                "Actividad_Comercial": [
                    "Agricultura, ganadería, silvicultura y pesca",
                    "Explotación de minas y canteras",
                    "Aprovisionamiento de petróleo y minería metálica",
                    "Manufactura e Industria de Transformación",
                    "Elaboración de bebidas y productos de tabaco",
                    "Suministro de electricidad, gas, vapor y aire acondicionado",
                    "Construcción y obras civiles especializadas",
                    "Actividades especializadas de construcción",
                    "Comercio, mantenimiento y reparación de vehículos automotores",
                    "Comercio al por mayor y comisión",
                    "Comercio al por mayor y al por menor (Venta de mercadería general)",
                    "Hoteles y servicios de alojamiento turístico",
                    "Restaurantes, bares y servicios de provisión de alimentos",
                    "Edición, software y actividades de programación",
                    "Desarrollo de sistemas informáticos y consultoría tecnológica",
                    "Servicios financieros, bancarios y auxiliares",
                    "Actividades inmobiliarias con bienes propios o alquilados",
                    "Actividades jurídicas y de contabilidad",
                    "Actividades de gestión, consultoría administrativa y técnica",
                    "Arquitectura, ingeniería y ensayos técnicos",
                    "Agencias de viajes y servicios de reservaciones",
                    "Administración pública, defensa y seguridad social",
                    "Enseñanza, educación inicial, media y superior",
                    "Actividades de atención de la salud humana y asistencia social",
                    "Actividades artísticas, de entretenimiento y recreativas",
                    "Reparación de ordenadores y efectos personales",
                    "Otras actividades de servicios personales y profesionales diversos"
                ],
                "Margen_Rentabilidad": [
                    0.25, 0.20, 0.18, 0.30, 0.28, 0.15, 0.20, 0.22, 0.30, 0.25, 
                    0.25, 0.40, 0.35, 0.55, 0.60, 0.15, 0.35, 0.50, 0.50, 0.45, 
                    0.30, 0.10, 0.40, 0.45, 0.35, 0.40, 0.60
                ]
            })
        
        df_rent = cargar_tabla_rentabilidades_completa()
        
        ind_col1, ind_col2 = str_app.columns(2)
        with ind_col1:
            actividad_elegida = str_app.selectbox(
                "Selecciona la Actividad Comercial según RUC (Columna A):", 
                options=df_rent["Actividad_Comercial"].tolist(), 
                key="select_act_ruc_completo"
            )
            fila_act = df_rent[df_rent["Actividad_Comercial"] == actividad_elegida].iloc[0]
            codigo_ruc_val = fila_act["Codigo_RUC"]
            margen_h30 = float(fila_act["Margen_Rentabilidad"])
            
            str_app.info(f"📌 **Código RUC (Columna A):** `{codigo_ruc_val}` | **Margen de Utilidad (H30):** `{margen_h30*100:.1f}%`")
            
        with ind_col2:
            ingreso_bruto_d23 = str_app.number_input("Ingresos Brutos / Ventas Mensuales (D23) [$]:", min_value=0.0, value=3000.0, step=200.0, key="ingreso_d23_input")
            
        ingreso_neto_ajustado = ingreso_bruto_d23 * (1 - margen_h30)
        
        str_app.markdown("---")
        str_app.markdown("#### Resultado del Análisis de Capacidad (Independiente)")
        
        cp_ind1, cp_ind2, cp_ind3 = str_app.columns(3)
        cp_ind1.metric("💵 Ingresos Brutos (D23)", f"${ingreso_bruto_d23:,.2f}")
        cp_ind2.metric("📉 Gastos Operativos Estimados", f"${ingreso_bruto_d23 * margen_h30:,.2f}")
        cp_ind3.metric("💼 Ingreso Neto Ajustado Real", f"${ingreso_neto_ajustado:,.2f}")
        
        str_app.caption("Este ingreso neto ajustado refleja con precisión la estructura operativa declarada en los formatos estándar de evaluación.")

    with subtab_sim3:
        str_app.markdown("#### 📊 Simulador y Diagnóstico de Scoring Crediticio")
        str_app.caption("Responde las siguientes variables clave para estimar tu puntaje interno y probabilidad de aprobación:")
        
        sc_col1, sc_col2 = str_app.columns(2)
        with sc_col1:
            historial_buro = str_app.selectbox("Historial en Buró de Crédito:", options=["Excelente (Sin atrasos)", "Bueno (Atrasos menores < 30 días)", "Regular (Atrasos entre 30 y 90 días)", "Crítico (Atrasos > 90 días / Cartera castigada)"], index=0, key="score_buro_key")
            estabilidad_laboral = str_app.selectbox("Estabilidad Laboral / Actividad Comercial:", options=["Dependiente > 2 años / Negocio formal > 3 años", "Dependiente 1-2 años / Negocio 1-3 años", "Dependiente < 1 año / Negocio < 1 año", "Informal / Sin ingresos fijos comprobables"], index=0, key="score_lab_key")
        with sc_col2:
            nivel_endeudamiento_actual = str_app.selectbox("Ratio de Endeudamiento Actual (Debt-to-Income):", options=["Menor al 20%", "Entre 20% y 40%", "Entre 40% y 60%", "Mayor al 60%"], index=1, key="score_end_key")
            garantias_respaldo = str_app.selectbox("Garantías o Respaldo Patrimonial:", options=["Bienes raíces / Inversiones líquidas", "Vehículo propio / Garante solvente", "Sin garantías o avales sólidos"], index=0, key="score_gar_key")
            
        score_base = 350
        if "Excelente" in historial_buro: score_base += 300
        elif "Bueno" in historial_buro: score_base += 200
        elif "Regular" in historial_buro: score_base += 80
        else: score_base += 10
        
        if "Dependiente > 2" in estabilidad_laboral: score_base += 150
        elif "Dependiente 1-2" in estabilidad_laboral: score_base += 100
        elif "Dependiente < 1" in estabilidad_laboral: score_base += 50
        else: score_base += 20
        
        if "Menor al 20%" in nivel_endeudamiento_actual: score_base += 120
        elif "Entre 20% y 40%" in nivel_endeudamiento_actual: score_base += 80
        elif "Entre 40% y 60%" in nivel_endeudamiento_actual: score_base += 40
        else: score_base += 10
        
        if "Bienes raíces" in garantias_respaldo: score_base += 80
        elif "Vehículo" in garantias_respaldo: score_base += 50
        else: score_base += 20
        
        str_app.write("")
        str_app.markdown(f"### 📈 Puntaje de Scoring Estimado: **{score_base} / 1000 Puntos**")
        
        if score_base >= 750:
            str_app.success("🌟 **Perfil Crediticio: EXCELENTE (AAA).** Alta probabilidad de aprobación inmediata con tasas preferenciales en el sistema financiero.")
        elif score_base >= 600:
            str_app.info("👍 **Perfil Crediticio: BUENO (AA / A).** Elegible para la mayoría de productos de consumo y capital de trabajo con condiciones estándar.")
        elif score_base >= 450:
            str_app.warning("⚠️ **Perfil Crediticio: REGULAR (B / C).** Requiere estructuración de garantías adicionales o saneamiento de obligaciones previas.")
        else:
            str_app.error("🚨 **Perfil Crediticio: RIESGOSO / CRITICO.** Necesita asesoría especializada de reestructuración financiera antes de ingresar la solicitud.")

str_app.write("")

# ==========================================
# 6. BANNER ROTATIVO INTERACTIVO DE SERVICIOS
# ==========================================
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

str_app.markdown("""
<div class="card-corporativa">
    <h3 style='margin-top:0;'>✨ Asesoría Patrimonial y Estrategia de Financiamiento</h3>
    <p style='color: #4A5568; font-size: 1.1rem;'>Como Bróker especialista, conectamos tus metas con las mejores alternativas del ecosistema de manera independiente, mediante un análisis técnico riguroso.</p>
    <strong style='color: #0A2540;'>💼 Nuestra consultoría inicial no genera honorarios para ti</strong>.
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
            *Al presionar el botón inferior, usted otorga su <strong>consentimiento expreso</strong> para el tratamiento de sus datos personales.*
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
            str_app.success("🎉 ¡Trámite ingresado con éxito en la plataforma Escala Consultoría Empresarial y Financiera!")
            
            texto_ws = f"Hola Escala Finance & Insurance, he completado y autorizado mi pre-calificación en línea.\n\n" \
                       f"👤 *Consultante:* {nombre}\n" \
                       f"🪪 *Cédula:* {cedula}\n" \
                       f"📱 *Contacto:* {telefono}\n" \
                       f"📍 *Ciudad:* {ciudad}\n" \
                       f"🎯 *Línea:* Asesoría en {producto_interes}\n\n" \
                       f"📜 *Estado:* Trámite ingresado con éxito."
            
            url_whatsapp = f"https://api.whatsapp.com/send?phone={NUMERO_WHATSAPP}&text={urllib.parse.quote(texto_ws)}"
            str_app.balloons()
            str_app.link_button("🟢 Validar Identidad vía WhatsApp", url_whatsapp, type="primary")

with col_der:
    str_app.markdown("### 🤖 Asesor Ejecutivo Virtual")
    str_app.caption("Toca la fotografía de tu asesor para iniciar el flujo interactivo estructurado:")
    
    flujo_bot_whatsapp = (
        "🏛️ [Escala Consultoría Empresarial y Financiera - ASISTENTE VIRTUAL]\n\n"
        "🤖 ¡Hola! Bienvenido al canal interactivo de Escala.\n\n"
        "Por favor, bríndame tus DATOS PERSONALES base respondiendo en una sola línea:\n"
        "• Nombre y Apellido Completo:\n"
        "• Número de Cédula (10 dígitos):\n"
        "• Celular de Contacto:\n"
        "• Ciudad de Residencia:\n"
    )
    
    url_flujo_completo = f"https://api.whatsapp.com/send?phone={NUMERO_WHATSAPP}&text={urllib.parse.quote(flujo_bot_whatsapp)}"
    
    str_app.markdown(f"""
    <a href="{url_flujo_completo}" target="_blank" style="text-decoration: none; color: inherit;">
        <div class="ejecutivo-box">
            <img class="ejecutivo-avatar" src="{URL_FOTO_ASESOR}">
            <h4 style="margin: 0; color: #0A2540; font-size: 1.25rem;">Ec. Jonathan Vaca Cruz</h4>
            <p style="margin: 3px 0 10px 0; color: #10B981; font-weight: bold; font-size: 0.9rem;">💼 Broker & Consultor Financiero Senior</p>
            <div style="background-color: #F0F4F8; padding: 12px; border-radius: 8px; font-size: 0.88rem; color: #374151; text-align: justify; border-left: 3px solid #10B981;">
                💬 <strong>¿Deseas iniciar el flujo por WhatsApp?</strong> Toca mi fotografía para abrir el chat interactivo.
            </div>
            <br>
            <span style="background-color: #10B981; color: white; padding: 8px 18px; border-radius: 20px; font-weight: bold; font-size: 0.85rem; display: inline-block; box-shadow: 0 3px 6px rgba(16,185,129,0.3);">
                🟢 Abrir Flujo de WhatsApp Ahora
            </span>
        </div>
    </a>
    """, unsafe_allow_html=True)

str_app.write("---")

# ==========================================
# 7. INDICADORES ECONÓMICOS Y MERCADOS
# ==========================================
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

# ==========================================
# 8. PANEL DE ADMINISTRACIÓN
# ==========================================
with str_app.expander("🔒 Acceso a Panel de Administración y Informes"):
    password_ingresada = str_app.text_input("Contraseña de Administrador:", type="password", key="pwd_admin_key")
    
    if password_ingresada == PASSWORD_DASHBOARD:
        str_app.success("✅ Acceso autorizado.")
        
        tab_admin1, tab_admin2 = str_app.tabs(["📋 Leads en SQLite (Web)", "📊 Google Sheets & Informes PDF"])
        
        with tab_admin1:
            str_app.markdown("### Leads registrados desde el formulario web")
            df_leads = leer_leads()
            if not df_leads.empty:
                str_app.dataframe(df_leads, use_container_width=True)
            else:
                str_app.info("No hay registros guardados en SQLite todavía.")
                
        with tab_admin2:
            str_app.markdown("### Base de datos externa y Generador de Informes")
            df_gsheet = cargar_datos_google_sheet(URL_GOOGLE_SHEET)
            
            if not df_gsheet.empty:
                str_app.dataframe(df_gsheet, use_container_width=True)
                
                str_app.markdown("#### Generar Informe Ejecutivo PDF (Metodología McKinsey)")
                
                columna_nombre_preferida = None
                for col in df_gsheet.columns:
                    if any(k in col.lower() for k in ["empresa", "nombre", "cliente", "razon", "negocio"]):
                        columna_nombre_preferida = col
                        break
                
                indice_fila = str_app.selectbox(
                    "Selecciona el cliente para el informe:", 
                    options=range(len(df_gsheet)),
                    format_func=lambda x: f"Fila {x}: {df_gsheet.iloc[x][columna_nombre_preferida] if columna_nombre_preferida and pd.notna(df_gsheet.iloc[x][columna_nombre_preferida]) else df_gsheet.iloc[x].values[0]}",
                    key="select_cliente_pdf"
                )
                
                if str_app.button("📄 Generar y Descargar PDF Ejecutivo", key="btn_gen_pdf"):
                    fila_seleccionada = df_gsheet.iloc[indice_fila]
                    pdf_buffer = generar_pdf_mckinsey(fila_seleccionada)
                    
                    str_app.download_button(
                        label="📥 Descargar Informe en PDF",
                        data=pdf_buffer,
                        file_name=f"Informe_Ejecutivo_Escala_Fila_{indice_fila}.pdf",
                        mime="application/pdf",
                        key="btn_download_pdf"
                    )
            else:
                str_app.warning("No se pudo conectar o leer datos desde el Google Sheet configurado.")
    elif password_ingresada:
        str_app.error("❌ Contraseña incorrecta.")
