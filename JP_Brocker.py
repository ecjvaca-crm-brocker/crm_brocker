import streamlit as str_app
import urllib.parse
import sqlite3
import pandas as pd
import numpy as np
import tempfile
import os
import smtplib
import openpyxl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
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

# Credenciales SMTP para envío automático de correos (Ajustar con tu proveedor de email)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_EMISOR = "consultoria@escalafinance.com.ec"
PASSWORD_EMAIL = "tu_password_o_app_token"

str_app.set_page_config(
    page_title="Escala Corporate | Brokerage Financiero & Valuation Hub", 
    page_icon="🏛️", 
    layout="wide"
)

URL_FOTO_ASESOR = "https://raw.githubusercontent.com/ecjvaca-crm-brocker/crm_brocker/main/IMGAENJONAS.jpeg"
URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/1DiKGC8Q65SjouMutswiF00hsdbAXTIV5yDlGXGEAZnU/edit?gid=1469424641#gid=1469424641"
NOMBRE_PLANTILLA_EXCEL = "Solicitud de Crédito ESCALA CONSULTORES.xlsx"

# Inicialización de Estados Globales
if 'activos_tangibles' not in str_app.session_state:
    str_app.session_state.activos_tangibles = pd.DataFrame(columns=['Clase', 'Descripción', 'Valor Contable', 'Valor Razonable', 'Norma Aplicada'])

if 'impuestos_diferidos' not in str_app.session_state:
    str_app.session_state.impuestos_diferidos = pd.DataFrame(columns=['Concepto', 'Base Contable', 'Base Fiscal', 'Diferencia', 'Tipo', 'Impuesto Diferido'])

if 'enterprise_value' not in str_app.session_state:
    str_app.session_state.enterprise_value = 0.0

if 'tasa_fiscal_ecuador' not in str_app.session_state:
    str_app.session_state.tasa_fiscal_ecuador = 25.0

if 'respuestas_bancos_manual' not in str_app.session_state:
    str_app.session_state.respuestas_bancos_manual = []

# CATALOGO TÉCNICO DE TIPOS Y DESTINOS DE CRÉDITO
CATALOGO_CREDITO = {
    "Consumo": [
        "Estudios / Capacitación / Maestrías",
        "Remodelación de Vivienda",
        "Viajes / Turismo",
        "Tecnología / Equipamiento Personal",
        "Vehículo Particular",
        "Salud / Gastos Médicos"
    ],
    "Productivo Pymes": [
        "Capital de Trabajo",
        "Activo Fijo / Maquinaria y Equipos",
        "Expansión de Local / Infraestructura",
        "Inversión en Inventario / Mercadería"
    ],
    "Microcrédito Acumulación Simple": [
        "Capital de Trabajo (Giro del negocio)",
        "Compra de Mercadería / Materia Prima",
        "Herramientas y Maquinaria Menor"
    ],
    "Microcrédito Acumulación Ampliada": [
        "Capital de Trabajo de Escala",
        "Adquisición de Activos Fijos Industriales",
        "Adecuación Comercial y Locales"
    ]
}

# ENTIDADES FINANCIERAS ALIADAS DESTINATARIAS
ENTIDADES_DESTINO = [
    {"nombre": "Banco Guayaquil", "email": "creditos_pymes@bancoguayaquil.com"},
    {"nombre": "Banco Pichincha", "email": "evaluacion_riesgos@pichincha.com"},
    {"nombre": "Coop. Juventud Ecuatoriana Progresista (JEP)", "email": "solicitudes@jep.coop"},
    {"nombre": "Coop. Atuntaqui", "email": "creditos@atuntaqui.fin.ec"},
    {"nombre": "Microfinanciera Solidaria D-Miro", "email": "riesgos@d-miro.com"}
]

# ==============================================================================
# 2. CAPA DE PERSISTENCIA Y BASE DE DATOS LOCAL (SQLITE & GOOGLE SHEETS)
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
# 3. MANEJO DE PLANTILLA EXCEL Y GENERADOR DE SOLICITUD
# ==============================================================================
def cargar_plantilla_excel_bytes():
    with open(NOMBRE_PLANTILLA_EXCEL, "rb") as f:
        return f.read()

def prellenar_excel_solicitud(datos):
    """Carga el Excel oficial 'Solicitud de Crédito ESCALA CONSULTORES.xlsx' y rellena sus celdas."""
    wb = openpyxl.load_workbook(NOMBRE_PLANTILLA_EXCEL)
    ws = wb["Sol. Crédito PN"]
    
    # Inserción de datos clave en el formato oficial
    ws["D6"] = datetime.now().strftime("%Y-%m-%d")
    ws["D9"] = datos.get("monto", 0)
    ws["O9"] = datos.get("plazo", 12)
    ws["AB9"] = datos.get("dia_pago", 5)
    
    ws["D23"] = datos.get("apellido_paterno", "")
    ws["K23"] = datos.get("apellido_materno", "")
    ws["R23"] = datos.get("nombres", "")
    ws["D25"] = datos.get("cedula", "")
    ws["AD25"] = datos.get("telefono", "")
    ws["D39"] = datos.get("direccion", "")
    ws["AE39"] = datos.get("email", "")
    
    ws["R52"] = datos.get("empresa", "")
    ws["D54"] = datos.get("cargo", "")
    
    ws["H112"] = datos.get("ingresos_fijos", 0)
    ws["H113"] = datos.get("ventas", 0)
    ws["V112"] = datos.get("gastos_familiares", 0)
    ws["V113"] = datos.get("arriendo", 0)
    
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output

# ==============================================================================
# 4. GENERADOR DE PDF DE SOLICITUD Y ENVÍO POR CORREO
# ==============================================================================
class PDFSolicitudCredito(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 11)
        self.set_text_color(10, 37, 64)
        self.cell(0, 8, "ESCALA CONSULTORIA FINANCIERA - SOLICITUD DE CRÉDITO", 0, 1, "C")
        self.set_draw_color(212, 175, 55)
        self.set_line_width(0.8)
        self.line(10, 18, 200, 18)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, "Documento Informativo y de Recolección de Datos - Escala Consultores", 0, 0, "C")

def generar_pdf_solicitud(datos):
    pdf = PDFSolicitudCredito()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(10, 37, 64)
    pdf.cell(0, 8, f"Expediente de Solicitud N° {datetime.now().strftime('%Y%m%d%H%M')}", 0, 1, "L")
    pdf.ln(2)
    
    lineas = [
        ("Cliente / Solicitante:", datos["nombre"]),
        ("Cédula de Identidad / RUC:", datos["cedula"]),
        ("Contacto Telefónico:", datos["telefono"]),
        ("Ciudad / Ubicación:", datos["ciudad"]),
        ("Tipo de Crédito:", datos["tipo_credito"]),
        ("Destino del Crédito:", datos["destino_credito"]),
        ("Monto Solicitado:", f"${datos['monto']:,.2f}"),
        ("Plazo Solicitado:", f"{datos['plazo']} Meses"),
        ("Fecha de Emisión:", datetime.now().strftime('%Y-%m-%d %H:%M'))
    ]
    
    for label, val in lineas:
        pdf.set_font("helvetica", "B", 9)
        pdf.cell(65, 6, label, 1, 0, "L")
        pdf.set_font("helvetica", "", 9)
        pdf.cell(115, 6, str(val), 1, 1, "L")
        
    pdf.ln(5)
    pdf.set_font("helvetica", "I", 8)
    pdf.multi_cell(0, 4.5, "Aviso Legal: El presente documento constituye únicamente un formato para recoger información necesaria para una solicitud de crédito y NO constituye un documento legal vinculante. Las operaciones aprobadas serán regularizadas formalmente con el documento y requisitos establecidos por la entidad financiera que se adjudique la operación.")
    
    return BytesIO(pdf.output(dest='S'))

def enviar_expediente_por_correo(datos_solicitud, pdf_solicitud_bytes, excel_bytes, archivos_adjuntos, correos_destino):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_EMISOR
        msg['To'] = ", ".join(correos_destino)
        msg['Subject'] = f"EXPEDIENTE DE CRÉDITO: {datos_solicitud['nombre']} - {datos_solicitud['tipo_credito']}"
        
        body = f"""
        Estimado Equipo de Evaluación de Riesgos y Crédito,
        
        Remitimos el expediente formal de solicitud de crédito del cliente {datos_solicitud['nombre']}.
        
        - Tipo de Crédito: {datos_solicitud['tipo_credito']}
        - Destino del Crédito: {datos_solicitud['destino_credito']}
        - Monto Solicitado: ${datos_solicitud['monto']:,.2f}
        - Plazo: {datos_solicitud['plazo']} meses
        
        Se adjuntan el resumen en PDF, el formulario Excel oficial y los documentos soporte subidos por el cliente.
        
        Atentamente,
        Escala Consultoría Empresarial y Financiera
        """
        msg.attach(MIMEText(body, 'plain'))
        
        # Adjuntar PDF
        p_pdf = MIMEBase('application', 'octet-stream')
        p_pdf.set_payload(pdf_solicitud_bytes.getvalue())
        encoders.encode_base64(p_pdf)
        p_pdf.add_header('Content-Disposition', f'attachment; filename="Resumen_Solicitud_{datos_solicitud["cedula"]}.pdf"')
        msg.attach(p_pdf)
        
        # Adjuntar Excel
        p_xls = MIMEBase('application', 'octet-stream')
        p_xls.set_payload(excel_bytes.getvalue())
        encoders.encode_base64(p_xls)
        p_xls.add_header('Content-Disposition', f'attachment; filename="Solicitud_Oficial_Escala_{datos_solicitud["cedula"]}.xlsx"')
        msg.attach(p_xls)
        
        # Adjuntar Archivos cargados
        for adj in archivos_adjuntos:
            if adj is not None:
                p_file = MIMEBase('application', 'octet-stream')
                p_file.set_payload(adj.getvalue())
                encoders.encode_base64(p_file)
                p_file.add_header('Content-Disposition', f'attachment; filename="{adj.name}"')
                msg.attach(p_file)
                
        return True, "Expediente digital despachado exitosamente."
    except Exception as e:
        return False, str(e)

# ==============================================================================
# 5. GENERADOR DE INFORMES PDF MCKINSEY & ESTILOS CSS
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
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}} | Uso Exclusivo - Escala Consultoría Empresarial", 0, 0, "C")

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
    pdf = PDFConsultoria()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(10, 37, 64)
    pdf.cell(0, 8, "Informe Ejecutivo de Evaluacion de Cuenta", 0, 1, "L")
    pdf.ln(4)
    
    ruta_radar = generar_grafico_radar()
    pdf.image(ruta_radar, x=65, y=pdf.get_y(), w=75)
    pdf.ln(78)
    if os.path.exists(ruta_radar):
        os.remove(ruta_radar)

    return BytesIO(pdf.output(dest='S'))

str_app.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #FFFFFF 0%, #EBF4FC 100%); }
    h1, h2, h3, h4 { color: #0A2540 !important; font-family: 'Georgia', serif; }
    .card-corporativa {
        background-color: #FFFFFF; padding: 25px; border-radius: 10px;
        border-top: 5px solid #D4AF37; border-left: 1px solid #D1D5DB;
        border-right: 1px solid #D1D5DB; border-bottom: 2px solid #0A2540;
        margin-bottom: 20px; box-shadow: 0 6px 12px rgba(10,37,64,0.06);
    }
    div.stButton > button:first-child {
        background-color: #10B981; color: #FFFFFF; border: 2px solid #059669;
        border-radius: 6px; padding: 0.7rem 2rem; font-weight: bold; font-size: 16px;
        width: 100%; transition: all 0.3s ease; box-shadow: 0 4px 6px rgba(16,185,129,0.2);
    }
    div.stButton > button:first-child:hover {
        background-color: #0A2540; color: #D4AF37; border-color: #D4AF37;
    }
    .ejecutivo-box {
        background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px;
        padding: 20px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.04);
        border-top: 4px solid #10B981;
    }
    .ejecutivo-avatar {
        width: 130px; height: 130px; border-radius: 50%; object-fit: cover;
        border: 4px solid #D4AF37; margin: 0 auto 12px auto; display: block;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 6. CABECERA PRINCIPAL Y PESTAÑAS DE NAVEGACIÓN
# ==============================================================================
str_app.markdown("<h1 style='text-align: center; font-size: 2.8rem;'>🏛️ Escala Corporate: Brokerage & Valuation Hub</h1>", unsafe_allow_html=True)
str_app.markdown("<p style='text-align: center; color: #D4AF37; font-size: 1.3rem; font-weight: bold;'>Solución Integral de Intermediación Financiera e Inteligencia Fiscal</p>", unsafe_allow_html=True)

tab_solicitud, tab_calificacion, tab_simuladores, tab_valuacion, tab_cresa = str_app.tabs([
    "📝 1. Captura & Solicitud de Crédito", 
    "📊 2. Calificación del Top 3 de Ofertas", 
    "🧮 3. Simuladores, CDP & Amortización",
    "📈 4. Valuation & Tax Hub (NIIF / LRTI)",
    "🌐 5. Ecosistema CRESA & Validadores"
])

# ------------------------------------------------------------------------------
# PESTAÑA 1: CAPTURA & SOLICITUD DE CRÉDITO
# ------------------------------------------------------------------------------
with tab_solicitud:
    str_app.markdown("""
    <div class="card-corporativa" style="border-top: 5px solid #10B981;">
        <h3>📋 Registro de Solicitud y Empaquetamiento de Expediente</h3>
        <p style='color: #4A5568;'>Completa los datos del cliente. La plataforma generará automáticamente la solicitud en el formato oficial de Excel, compilará el resumen en PDF y despachará el expediente por correo a los bancos seleccionados.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Opción de descarga directa de la plantilla vacía
    with str_app.expander("📥 Descargar Plantilla Oficial Excel Vacía", expanded=False):
        try:
            p_bytes = cargar_plantilla_excel_bytes()
            str_app.download_button(
                label="Descargar Plantilla Excel 'Solicitud de Crédito ESCALA CONSULTORES.xlsx'",
                data=p_bytes,
                file_name="Solicitud_Credito_ESCALA_CONSULTORES_Vacia.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception:
            str_app.warning("Coloca el archivo 'Solicitud de Crédito ESCALA CONSULTORES.xlsx' en la carpeta raíz del proyecto.")

    with str_app.form("form_solicitud_completa", clear_on_submit=False):
        str_app.subheader("1. Datos Generales de la Operación")
        c1, c2, c3, c4 = str_app.columns(4)
        monto_sol = c1.number_input("Monto Requerido ($):", min_value=300.0, value=5000.0, step=250.0)
        plazo_sol = c2.selectbox("Plazo (Meses):", options=[6, 12, 18, 24, 36, 48, 60], index=3)
        dia_pago_sol = c3.selectbox("Día Preferido de Pago:", list(range(1, 31)), index=4)
        tipo_sujeto = c4.selectbox("Tipo de Sujeto:", ["Persona Natural", "Persona Jurídica"])
        
        str_app.subheader("2. Clasificación del Crédito")
        col_t, col_d = str_app.columns(2)
        tipo_cred_sel = col_t.selectbox("Tipo de Crédito:", options=list(CATALOGO_CREDITO.keys()))
        destino_cred_sel = col_d.selectbox("Destino del Crédito:", options=CATALOGO_CREDITO[tipo_cred_sel])
        
        str_app.subheader("3. Identificación del Solicitante")
        i1, i2, i3 = str_app.columns(3)
        ap_paterno = i1.text_input("Apellido Paterno:")
        ap_materno = i2.text_input("Apellido Materno:")
        nombres = i3.text_input("Nombres Completos:")
        
        id1, id2, id3, id4 = str_app.columns(4)
        cedula = id1.text_input("Cédula / RUC:", max_chars=13)
        telefono = id2.text_input("Celular / WhatsApp:")
        email = id3.text_input("Correo Electrónico:")
        ciudad = id4.text_input("Ciudad de Residencia:", value="Ibarra")
        
        direccion = str_app.text_input("Dirección Domiciliaria Completa:")
        
        str_app.subheader("4. Información Laboral y Financiera Básica")
        l1, l2, l3, l4 = str_app.columns(4)
        empresa = l1.text_input("Empresa / Negocio:")
        cargo = l2.text_input("Cargo / Actividad:")
        ing_fijos = l3.number_input("Ingresos Fijos / Ventas ($):", value=1200.0)
        gastos_fam = l4.number_input("Gastos Familiares / Arriendo ($):", value=500.0)
        
        str_app.subheader("5. Documentación Adjunta Digitalizada")
        f1, f2, f3 = str_app.columns(3)
        doc_cedula = f1.file_uploader("🪪 Cédulas (PDF/Imagen)", type=["pdf", "png", "jpg", "jpeg"])
        doc_ingresos = f2.file_uploader("📦 Sustento de Ingresos", type=["pdf", "png", "jpg", "jpeg"])
        doc_planilla = f3.file_uploader("🏠 Planilla de Servicio Básico", type=["pdf", "png", "jpg", "jpeg"])
        
        str_app.subheader("6. Selección de Entidades Financieras Destinatarias")
        bancos_sel = str_app.multiselect(
            "Selecciona las entidades a las que deseas remitir el expediente:",
            options=[b["nombre"] for b in ENTIDADES_DESTINO],
            default=[b["nombre"] for b in ENTIDADES_DESTINO[:3]]
        )
        
        btn_enviar_expediente = str_app.form_submit_button("🚀 Generar Expediente y Enviar a Instituciones Financieras")

    if btn_enviar_expediente:
        if not nombres or not cedula or not doc_cedula:
            str_app.error("⚠️ Nombres, Cédula y la Carga de la Cédula son obligatorios.")
        else:
            datos_sol = {
                "nombre": f"{nombres} {ap_paterno} {ap_materno}".strip(),
                "apellido_paterno": ap_paterno, "apellido_materno": ap_materno, "nombres": nombres,
                "cedula": cedula, "telefono": telefono, "email": email, "ciudad": ciudad, "direccion": direccion,
                "monto": monto_sol, "plazo": plazo_sol, "dia_pago": dia_pago_sol,
                "tipo_credito": tipo_cred_sel, "destino_credito": destino_cred_sel,
                "empresa": empresa, "cargo": cargo, "ingresos_fijos": ing_fijos, "gastos_familiares": gastos_fam
            }
            
            # 1. Generar Excel rellenado
            excel_bytes = prellenar_excel_solicitud(datos_sol)
            
            # 2. Generar PDF resumen
            pdf_bytes = generar_pdf_solicitud(datos_sol)
            
            # 3. Empaquetar y enviar por email
            adjuntos = [doc_cedula, doc_ingresos, doc_planilla]
            correos = [b["email"] for b in ENTIDADES_DESTINO if b["nombre"] in bancos_sel]
            
            exito, msg_e = enviar_expediente_por_correo(datos_sol, pdf_bytes, excel_bytes, adjuntos, correos)
            
            guardar_lead(datos_sol["nombre"], cedula, telefono, ciudad, f"Crédito {tipo_cred_sel}")
            
            str_app.success(f"🎉 ¡Expediente completo generado y enviado a {len(bancos_sel)} entidades!")
            
            c_down1, c_down2 = str_app.columns(2)
            c_down1.download_button(
                label="📥 Descargar Solicitud Rellenada en Excel (.xlsx)",
                data=excel_bytes,
                file_name=f"Solicitud_Escala_{cedula}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            c_down2.download_button(
                label="📥 Descargar Resumen de Solicitud en PDF",
                data=pdf_bytes,
                file_name=f"Resumen_Solicitud_{cedula}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

# ------------------------------------------------------------------------------
# PESTAÑA 2: CALIFICACIÓN DEL TOP 3 DE OFERTAS & ADJUDICACIÓN
# ------------------------------------------------------------------------------
with tab_calificacion:
    str_app.markdown("""
    <div class="card-corporativa" style="border-top: 5px solid #0A2540;">
        <h3>📥 Ingreso de Respuestas y Calificación del Top 3 de Ofertas</h3>
        <p style='color: #4A5568;'>Registra los dictámenes recibidos por correo de los bancos. El sistema calificará y ordenará las 3 mejores opciones para adjudicar el crédito con tu cliente.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_r1, col_r2 = str_app.columns([1, 1.4])
    
    with col_r1:
        str_app.subheader("Registrar Dictamen de Banco")
        with str_app.form("form_reg_respuesta", clear_on_submit=True):
            entidad_resp = str_app.selectbox("Entidad Financiera:", [b["nombre"] for b in ENTIDADES_DESTINO])
            estado_resp = str_app.selectbox("Dictamen:", ["APROBADO", "RECHAZADO", "CONDICIONADO"])
            monto_aprob = str_app.number_input("Monto Aprobado ($):", min_value=0.0, value=5000.0, step=250.0)
            tasa_tea = str_app.number_input("Tasa de Interés Efectiva (TEA %):", min_value=0.1, value=15.5, step=0.1)
            plazo_aprob = str_app.number_input("Plazo Otorgado (Meses):", min_value=1, value=24)
            obs = str_app.text_input("Observación / Requisito:", placeholder="Ej. Presentar garante o firma de pagaré")
            
            btn_guardar_oferta = str_app.form_submit_button("➕ Registrar Oferta en el Sistema")
            
        if btn_guardar_oferta:
            str_app.session_state.respuestas_bancos_manual.append({
                "Entidad": entidad_resp, "Estado": estado_resp, "Monto Aprobado": monto_aprob,
                "Tasa (TEA %)": tasa_tea, "Plazo (Meses)": plazo_aprob, "Observación": obs
            })
            str_app.success(f"Oferta de {entidad_resp} ingresada correctamente.")

    with col_r2:
        str_app.subheader("🏆 Cuadro Comparativo y Selección de Adjudicación")
        if str_app.session_state.respuestas_bancos_manual:
            df_resp = pd.DataFrame(str_app.session_state.respuestas_bancos_manual)
            aprobadas = df_resp[df_resp["Estado"] == "APROBADO"].copy()
            
            if not aprobadas.empty:
                aprobadas["Score"] = (100 / aprobadas["Tasa (TEA %)"]) * 0.6 + (aprobadas["Monto Aprobado"] / 100) * 0.4
                top_3 = aprobadas.sort_values(by="Score", ascending=False).head(3)
                
                str_app.markdown("### 🔥 Top 3 Mejores Ofertas Calificadas")
                str_app.dataframe(top_3[["Entidad", "Monto Aprobado", "Tasa (TEA %)", "Plazo (Meses)", "Observación"]], use_container_width=True)
                
                mejor_o = top_3.iloc[0]
                str_app.success(f"🥇 **Opción Prioritaria Adjudicada:** {mejor_o['Entidad']} por **${mejor_o['Monto Aprobado']:,.2f}** al **{mejor_o['Tasa (TEA %)}% TEA**.")
                
                msg_ws = f"Hola, he revisado el Top 3 de ofertas para mi crédito. La opción ganadora adjudicada es {mejor_o['Entidad']} por ${mejor_o['Monto Aprobado']} al {mejor_o['Tasa (TEA %)}%. Deseo continuar con el desembolso."
                url_ws = f"https://api.whatsapp.com/send?phone={NUMERO_WHATSAPP}&text={urllib.parse.quote(msg_ws)}"
                str_app.link_button("🟢 Continuar Desembolso de Oferta Adjudicada vía WhatsApp", url_ws, type="primary")
            else:
                str_app.warning("Todas las ofertas ingresadas actualmente están rechazadas o condicionadas.")
        else:
            str_app.info("Registra las respuestas recibidas en el panel de la izquierda para generar la calificación.")

# ------------------------------------------------------------------------------
# PESTAÑA 3: SIMULADORES, CDP & AMORTIZACIÓN
# ------------------------------------------------------------------------------
with tab_simuladores:
    s_tab1, s_tab2, s_tab3 = str_app.tabs(["🧮 CDP & Scoring", "📋 Amortización Francesa", "🎯 Planificador de Retiro"])
    
    with s_tab1:
        str_app.markdown("#### 1. Simulador de Capacidad de Pago (CDP)")
        sc1, sc2, sc3 = str_app.columns(3)
        m_calc = sc1.number_input("Monto ($):", value=10000.0, key="cdp_monto")
        t_calc = sc2.number_input("Tasa Anual (%):", value=15.0, key="cdp_tasa")
        p_calc = sc3.selectbox("Plazo (Meses):", [12, 24, 36, 48, 60], index=2, key="cdp_plazo")
        
        i_m = (t_calc / 100) / 12
        cuota_est = m_calc * (i_m * (1 + i_m)**p_calc) / ((1 + i_m)**p_calc - 1) if i_m > 0 else m_calc / p_calc
        str_app.metric("💵 Cuota Mensual Estimada", f"${cuota_est:,.2f}")
        
        str_app.markdown("---")
        ing_n = str_app.number_input("Ingresos Mensuales Netos ($):", value=1500.0)
        egr_f = str_app.number_input("Egresos Fijos ($):", value=500.0)
        deu_v = str_app.number_input("Otras Deudas ($):", value=200.0)
        
        excedente = ing_n - egr_f - deu_v
        cdp_disp = max(0.0, min(excedente * 0.8, ing_n * 0.45))
        str_app.metric("🛡️ Cuota Disponible Sugerida (CDP)", f"${cdp_disp:,.2f}")

    with s_tab2:
        str_app.markdown("#### 📋 Cronograma de Pagos (Tabla Francesa)")
        ma = str_app.number_input("Capital ($):", value=15000.0, key="am_monto")
        ta = str_app.number_input("Tasa Anual (%):", value=14.0, key="am_tasa")
        pa = str_app.selectbox("Plazo (Meses):", [12, 24, 36, 48, 60], index=2, key="am_plazo")
        
        if str_app.button("⚙️ Generar Tabla"):
            tm = (ta / 100) / 12
            c_fija = ma * (tm * (1 + tm)**pa) / ((1 + tm)**pa - 1)
            saldo = ma
            cronograma = []
            for mes in range(1, pa + 1):
                i_mes = saldo * tm
                cap_mes = c_fija - i_mes
                saldo -= cap_mes
                cronograma.append({
                    "Mes": mes, "Cuota": round(c_fija, 2), 
                    "Interés": round(i_mes, 2), "Abono Capital": round(cap_mes, 2), 
                    "Saldo Final": round(max(0, saldo), 2)
                })
            str_app.dataframe(pd.DataFrame(cronograma), use_container_width=True)

    with s_tab3:
        str_app.markdown("#### 🎯 Planificador de Retiro Patrimonial")
        e_a = str_app.number_input("Edad Actual:", value=35)
        e_r = str_app.number_input("Edad de Retiro:", value=60)
        g_r = str_app.number_input("Gasto Mensual Deseado ($):", value=2000.0)
        
        cap_obj = (g_r * 12) / 0.05
        str_app.markdown(f"Fondo de Retiro Requerido al 5% de rendimiento: **${cap_obj:,.2f}**")

# ------------------------------------------------------------------------------
# PESTAÑA 4: VALUATION & TAX HUB (NIIF / LRTI)
# ------------------------------------------------------------------------------
with tab_valuacion:
    v1, v2, v3, v4 = str_app.tabs(["1. Activos NIIF 13", "2. DCF & WACC", "3. NIC 12 & LRTI", "4. Reporte"])
    
    with v1:
        str_app.subheader("🏢 Registro de Activos Tangibles")
        clase = str_app.selectbox("Clase", ["Vehículos", "Maquinaria", "Inmuebles", "Inventario"])
        desc = str_app.text_input("Descripción", "Planta Industrial")
        vc = str_app.number_input("Valor Contable ($)", value=50000.0)
        vr = str_app.number_input("Valor Razonable ($)", value=70000.0)
        if str_app.button("Ingresar Activo NIIF"):
            nuevo = pd.DataFrame([{'Clase': clase, 'Descripción': desc, 'Valor Contable': vc, 'Valor Razonable': vr, 'Norma Aplicada': 'NIIF'}])
            str_app.session_state.activos_tangibles = pd.concat([str_app.session_state.activos_tangibles, nuevo], ignore_index=True)
            str_app.rerun()
        if not str_app.session_state.activos_tangibles.empty:
            str_app.dataframe(str_app.session_state.activos_tangibles, use_container_width=True)

    with v2:
        str_app.subheader("⚙️ Valoración por Flujo Descontado (DCF)")
        rf = str_app.number_input("Rf (%)", value=4.5) / 100
        beta = str_app.number_input("Beta", value=1.2)
        rm = str_app.number_input("Rm (%)", value=9.5) / 100
        rp = str_app.number_input("Riesgo País (pb)", value=1200) / 10000
        kd = str_app.number_input("Kd (%)", value=10.5) / 100
        tax = str_app.number_input("Tasa Impositiva (%)", value=36.25) / 100
        peso_e = str_app.slider("Proporción Equity (%)", 10, 100, 60) / 100
        
        ke = rf + beta * (rm - rf) + rp
        wacc = (peso_e * ke) + ((1 - peso_e) * kd * (1 - tax))
        
        fcl1 = str_app.number_input("Flujo Libre Año 1 ($)", value=500000.0)
        g_rate = str_app.slider("Crecimiento Años 2-5 (%)", 1.0, 15.0, 5.0) / 100
        g_perp = str_app.slider("Crecimiento Perpetuidad (%)", 0.5, 5.0, 2.0) / 100
        
        flujos = [fcl1 * ((1 + g_rate)**i) for i in range(5)]
        vp_flujos = sum([f / ((1 + wacc)**(i+1)) for i, f in enumerate(flujos)])
        v_term = (flujos[-1] * (1 + g_perp)) / (wacc - g_perp)
        vp_vterm = v_term / ((1 + wacc)**5)
        ev = vp_flujos + vp_vterm
        str_app.session_state.enterprise_value = ev
        str_app.metric("Enterprise Value (Valor Operativo)", f"${ev:,.2f}")

    with v3:
        str_app.subheader("⚖️ Conciliación Impuestos Diferidos (NIC 12)")
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
        if not str_app.session_state.impuestos_diferidos.empty:
            str_app.dataframe(str_app.session_state.impuestos_diferidos, use_container_width=True)

    with v4:
        str_app.subheader("VALORACIÓN INTEGRAL PRE-MONEY")
        tot_act = str_app.session_state.activos_tangibles['Valor Razonable'].sum() if not str_app.session_state.activos_tangibles.empty else 0.0
        str_app.metric("Valor Total Combinado", f"${str_app.session_state.enterprise_value + tot_act:,.2f}")

# ------------------------------------------------------------------------------
# PESTAÑA 5: ECOSISTEMA CRESA & VALIDACIONALES
# ------------------------------------------------------------------------------
with tab_cresa:
    str_app.markdown("""
    <div class="card-corporativa">
        <h3>🌐 Ecosistema CRESA & Canales Comerciales</h3>
        <p style='color: #4A5568;'>Plataformas de consulta institucional, verificación de identidad y redes de Social Selling.</p>
    </div>
    """, unsafe_allow_html=True)
    
    cb1, cb2 = str_app.columns(2)
    with cb1:
        str_app.link_button("🚀 Plataforma Nexum 360", "https://nexum360.com.ec/", use_container_width=True)
        str_app.link_button("🔍 Consulta RUC en SRI", "https://srienlinea.sri.gob.ec/sri-en-linea/SriRucWeb/ConsultaRuc/Consultas/consultaRuc", use_container_width=True)
        str_app.link_button("📋 Certificado Afiliación IESS", "https://www.iess.gob.ec/afiliado-web/pages/opcionesGenerales/seleccionCertificadoDeAfiliacion.jsf", use_container_width=True)
    with cb2:
        str_app.link_button("🩺 Cobertura de Salud MSP", "https://coberturasalud.msp.gob.ec/", use_container_width=True)
        str_app.link_button("🚦 Multas y Citaciones ANT", "https://consultaweb.ant.gob.ec/PortalWEB/paginas/clientes/clp_criterio_consulta.jsp", use_container_width=True)

# ==============================================================================
# INDICADORES ECONÓMICOS EN TIEMPO REAL & PANEL ADMINISTRATIVO
# ==============================================================================
str_app.write("---")
str_app.markdown("### 📊 Indicadores Económicos Globals")

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

# Panel Administrador
with str_app.expander("🔒 Panel de Administración y Registros"):
    pwd = str_app.text_input("Contraseña Administrador:", type="password")
    if pwd == PASSWORD_DASHBOARD:
        str_app.success("Acceso concedido.")
        df_leads = leer_leads()
        str_app.dataframe(df_leads, use_container_width=True)
