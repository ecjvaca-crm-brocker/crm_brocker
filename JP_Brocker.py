from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO
import os
import shutil
import sqlite3
import smtplib
import urllib.parse

from fpdf import FPDF
import gspread
import pandas as pd
import streamlit as str_app
import yfinance as yf

# ==============================================================================
# 1. CONFIGURACIONES INICIALES Y BRANDING
# ==============================================================================
str_app.set_page_config(
    page_title="ESCALA Consultoría Financiera y Empresarial",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

NUMERO_WHATSAPP = "593998076979"
PASSWORD_DASHBOARD = "Escala2026"
DIR_RESPALDOS = "./respaldos_crm"

if not os.path.exists(DIR_RESPALDOS):
    os.makedirs(DIR_RESPALDOS)

str_app.markdown(
    """
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
    </style>
""",
    unsafe_allow_html=True,
)

if "respuestas_bancos_manual" not in str_app.session_state:
    str_app.session_state.respuestas_bancos_manual = []

CATALOGO_CREDITO = {
    "Consumo": [
        "Estudios / Capacitación / Maestrías",
        "Remodelación de Vivienda",
        "Viajes / Turismo",
        "Tecnología / Equipamiento Personal",
        "Vehículo Particular",
        "Salud / Gastos Médicos",
    ],
    "Productivo Pymes": [
        "Capital de Trabajo",
        "Activo Fijo / Maquinaria y Equipos",
        "Expansión de Local / Infraestructura",
        "Inversión en Inventario / Mercadería",
    ],
    "Microcrédito Acumulación Simple": [
        "Capital de Trabajo (Giro del negocio)",
        "Compra de Mercadería / Materia Prima",
        "Herramientas y Maquinaria Menor",
    ],
    "Microcrédito Acumulación Ampliada": [
        "Capital de Trabajo de Escala",
        "Adquisición de Activos Fijos Industriales",
        "Adecuación Comercial y Locales",
    ],
}

ENTIDADES_DESTINO = [
    {"nombre": "Banco Guayaquil", "email": "creditos_pymes@bancoguayaquil.com"},
    {"nombre": "Banco Pichincha", "email": "evaluacion_riesgos@pichincha.com"},
    {
        "nombre": "Coop. Juventud Ecuatoriana Progresista (JEP)",
        "email": "solicitudes@jep.coop",
    },
    {"nombre": "Coop. Atuntaqui", "email": "creditos@atuntaqui.fin.ec"},
    {
        "nombre": "Microfinanciera Solidaria D-Miro",
        "email": "riesgos@d-miro.com",
    },
]


# ==============================================================================
# 2. CAPA DE PERSISTENCIA Y CRM
# ==============================================================================
def init_db():
    conn = sqlite3.connect("crm_escala.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS solicitudes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            nombre TEXT,
            cedula TEXT,
            telefono TEXT,
            email TEXT,
            monto REAL,
            plazo INTEGER,
            tipo_credito TEXT,
            destino TEXT,
            estado TEXT,
            directorio_docs TEXT
        )
    """
    )
    cursor.execute("PRAGMA table_info(solicitudes)")
    cols = [c[1] for c in cursor.fetchall()]
    for col, tipo in [
        ("plazo", "INTEGER"),
        ("tipo_credito", "TEXT"),
        ("destino", "TEXT"),
        ("directorio_docs", "TEXT"),
    ]:
        if col not in cols:
            cursor.execute(f"ALTER TABLE solicitudes ADD COLUMN {col} {tipo}")
    conn.commit()
    conn.close()


def guardar_solicitud_crm(datos_sol, lista_listas_archivos):
    cedula = datos_sol.get("cedula", "sin_cedula")
    dir_cliente = os.path.join(
        DIR_RESPALDOS, f"{cedula}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    os.makedirs(dir_cliente, exist_ok=True)

    # Recorrer listas de archivos adjuntos y guardarlos físicamente
    for grupo_archivos in lista_listas_archivos:
        if grupo_archivos:
            for archivo in grupo_archivos:
                if archivo is not None:
                    ruta_archivo = os.path.join(dir_cliente, archivo.name)
                    with open(ruta_archivo, "wb") as f:
                        f.write(archivo.getbuffer())
                    archivo.seek(0)

    conn = sqlite3.connect("crm_escala.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO solicitudes 
        (fecha, nombre, cedula, telefono, email, monto, plazo, tipo_credito, destino, estado, directorio_docs)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            datos_sol.get("nombre", ""),
            datos_sol.get("cedula", ""),
            datos_sol.get("telefono", ""),
            datos_sol.get("email", ""),
            float(datos_sol.get("monto", 0.0)),
            int(datos_sol.get("plazo", 12)),
            datos_sol.get("tipo_credito", ""),
            datos_sol.get("destino_credito", ""),
            "En Proceso",
            dir_cliente,
        ),
    )
    conn.commit()
    conn.close()


def eliminar_documentos_cliente(dir_cliente):
    if os.path.exists(dir_cliente):
        try:
            shutil.rmtree(dir_cliente)
            return True
        except Exception as e:
            str_app.error(f"Error al eliminar carpeta: {e}")
            return False
    return False


init_db()


# ==============================================================================
# 3. GENERADOR DE SOLICITUD OFICIAL EN PDF Y ENVÍO SMTP
# ==============================================================================
class PDFSolicitudOficial(FPDF):

    def header(self):
        self.set_font("helvetica", "B", 12)
        self.set_text_color(10, 37, 64)
        self.cell(
            0,
            8,
            "ESCALA CONSULTORÍA FINANCIERA Y EMPRESARIAL",
            0,
            1,
            "C",
        )
        self.set_font("helvetica", "", 9)
        self.cell(
            0,
            5,
            "FORMULARIO OFICIAL DE SOLICITUD DE CRÉDITO Y CROQUIS DIGITAL",
            0,
            1,
            "C",
        )
        self.set_draw_color(212, 175, 55)
        self.set_line_width(0.8)
        self.line(10, 20, 200, 20)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(
            0,
            10,
            "Documento Oficial Compilado - Escala Consultores | Uso Institucional",
            0,
            0,
            "C",
        )


def generar_pdf_solicitud_oficial(datos):
    pdf = PDFSolicitudOficial()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("helvetica", "B", 10)
    pdf.set_fill_color(10, 37, 64)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 6, " 1. DATOS DE LA OPERACIÓN Y CRÉDITO", 0, 1, "L", fill=True)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("helvetica", "", 9)
    seccion_1 = [
        ("Monto Solicitado:", f"${datos['monto']:,.2f}"),
        ("Plazo:", f"{datos['plazo']} Meses"),
        ("Día de Pago:", f"Día {datos['dia_pago']} de cada mes"),
        ("Tipo de Crédito:", datos["tipo_credito"]),
        ("Destino del Crédito:", datos["destino_credito"]),
    ]
    for k, v in seccion_1:
        pdf.cell(60, 5, k, 1, 0, "L", 0)
        pdf.cell(130, 5, str(v), 1, 1, "L", 0)

    pdf.ln(3)

    pdf.set_font("helvetica", "B", 10)
    pdf.set_fill_color(10, 37, 64)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 6, " 2. DATOS PERSONALES Y DE CONTACTO", 0, 1, "L", fill=True)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("helvetica", "", 9)
    seccion_2 = [
        ("Apellidos y Nombres:", datos["nombre"]),
        ("Cédula de Identidad / RUC:", datos["cedula"]),
        ("Ciudad / Dirección:", f"{datos['ciudad']} - {datos['direccion']}"),
        ("Teléfono / Celular:", datos["telefono"]),
        ("Correo Electrónico:", datos["email"]),
    ]
    for k, v in seccion_2:
        pdf.cell(60, 5, k, 1, 0, "L", 0)
        pdf.cell(130, 5, str(v), 1, 1, "L", 0)

    pdf.ln(3)

    pdf.set_font("helvetica", "B", 10)
    pdf.set_fill_color(10, 37, 64)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(
        0, 6, " 3. INFORMACIÓN LABORAL Y FINANCIERA BÁSICA", 0, 1, "L", fill=True
    )

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("helvetica", "", 9)
    seccion_3 = [
        ("Empresa / Negocio:", datos["empresa"]),
        ("Cargo / Actividad:", datos["cargo"]),
        ("Ingresos Fijos / Ventas ($):", f"${datos['ingresos_fijos']:,.2f}"),
        ("Gastos Familiares ($):", f"${datos['gastos_familiares']:,.2f}"),
    ]
    for k, v in seccion_3:
        pdf.cell(60, 5, k, 1, 0, "L", 0)
        pdf.cell(130, 5, str(v), 1, 1, "L", 0)

    pdf.ln(3)

    pdf.set_font("helvetica", "B", 10)
    pdf.set_fill_color(10, 37, 64)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(
        0, 6, " 4. UBICACIÓN GEOGRÁFICA Y CROQUIS (GOOGLE MAPS)", 0, 1, "L", fill=True
    )

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("helvetica", "", 9)
    seccion_4 = [
        ("Ubicación Domicilio:", datos.get("mapa_domicilio", "No especificado")),
        ("Ubicación Trabajo:", datos.get("mapa_trabajo", "No especificado")),
    ]
    for k, v in seccion_4:
        pdf.cell(60, 5, k, 1, 0, "L", 0)
        pdf.cell(130, 5, str(v), 1, 1, "L", 0)

    pdf.ln(8)

    pdf.set_font("helvetica", "B", 9)
    pdf.cell(
        0,
        5,
        "DECLARACIÓN Y CONFORMIDAD: Certifico que los datos proporcionados son exactos.",
        0,
        1,
        "C",
    )
    pdf.ln(15)
    pdf.cell(95, 5, "f) ___________________________________", 0, 0, "C")
    pdf.cell(95, 5, "f) ___________________________________", 0, 1, "C")
    pdf.cell(95, 5, "Solicitante / Deudor Principal", 0, 0, "C")
    pdf.cell(95, 5, "Asesor / Oficial de Crédito ESCALA", 0, 1, "C")

    return BytesIO(pdf.output(dest="S"))


def enviar_expediente_por_correo(
    datos_solicitud, pdf_bytes, lista_listas_adjuntos, correos_destino
):
    try:
        smtp_server = str_app.secrets["smtp"]["server"]
        smtp_port = int(str_app.secrets["smtp"]["port"])
        sender_email = str_app.secrets["smtp"]["email"]
        sender_password = str_app.secrets["smtp"]["password"]

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = sender_email
        msg["Subject"] = (
            f"EXPEDIENTE OFICIAL DE CRÉDITO: {datos_solicitud['nombre']} - {datos_solicitud['tipo_credito']}"
        )

        body = f"""
        Estimado Equipo de Evaluación de Riesgos y Crédito,
        
        Remitimos la solicitud oficial de crédito y la documentación patrimonial del cliente {datos_solicitud['nombre']}.
        
        • Cédula: {datos_solicitud['cedula']}
        • Tipo de Crédito: {datos_solicitud['tipo_credito']}
        • Monto Solicitado: ${datos_solicitud['monto']:,.2f}
        • Plazo: {datos_solicitud['plazo']} meses
        • Ubicación Domicilio (Maps): {datos_solicitud.get('mapa_domicilio')}
        • Ubicación Trabajo (Maps): {datos_solicitud.get('mapa_trabajo')}
        
        Se adjuntan el PDF oficial firmado, la cédula, los sustentos de ingresos y los respaldos patrimoniales (predial, matrícula, etc.).
        
        Atentamente,
        Escala Consultoría Empresarial y Financiera
        """
        msg.attach(MIMEText(body, "plain"))

        # Adjuntar PDF principal de solicitud
        p_pdf = MIMEBase("application", "octet-stream")
        p_pdf.set_payload(pdf_bytes.getvalue())
        encoders.encode_base64(p_pdf)
        p_pdf.add_header(
            "Content-Disposition",
            f'attachment; filename="Solicitud_Firmada_Escala_{datos_solicitud["cedula"]}.pdf"',
        )
        msg.attach(p_pdf)

        # Adjuntar todos los archivos de las diferentes categorías de subida
        for grupo in lista_listas_adjuntos:
            if grupo:
                for adj in grupo:
                    if adj is not None:
                        p_file = MIMEBase("application", "octet-stream")
                        p_file.set_payload(adj.getvalue())
                        encoders.encode_base64(p_file)
                        p_file.add_header(
                            "Content-Disposition",
                            f'attachment; filename="{adj.name}"',
                        )
                        msg.attach(p_file)
                        adj.seek(0)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        return True, "Expediente oficial despachado exitosamente."
    except Exception as e:
        return False, str(e)


# ==============================================================================
# 4. NAVEGACIÓN Y PESTAÑAS PRINCIPALES
# ==============================================================================
str_app.markdown(
    "<h1 style='text-align: center; font-size: 2.6rem;'>🏛️ Escala Corporate: Brokerage & Valuation Hub</h1>",
    unsafe_allow_html=True,
)
str_app.markdown(
    "<p style='text-align: center; color: #D4AF37; font-size: 1.2rem; font-weight: bold;'>Solución Integral de Intermediación Financiera e Inteligencia Fiscal</p>",
    unsafe_allow_html=True,
)

tab_solicitud, tab_crm, tab_calificacion, tab_simuladores, tab_valuacion, tab_cresa, tab_salas = (
    str_app.tabs(
        [
            "📝 1. Solicitud & PDF Firmado",
            "📊 2. Pipeline CRM & Expedientes",
            "🏆 3. Calificación de Ofertas",
            "🧮 4. Simuladores & CDP",
            "📈 5. Valuation & Tax Hub",
            "🌐 6. Ecosistema CRESA",
            "🏬 7. Salas de Experiencia",
        ]
    )
)

# ------------------------------------------------------------------------------
# PESTAÑA 1: CAPTURA & SOLICITUD CON DOCUMENTOS PATRIMONIALES Y MAPS
# ------------------------------------------------------------------------------
with tab_solicitud:
    str_app.markdown(
        """
    <div class="card-corporativa" style="border-top: 5px solid #10B981;">
        <h3>📋 Generación de Solicitud Oficial, Croquis Google Maps y Respaldos</h3>
        <p style='color: #4A5568;'>Completa la información del cliente, adjunta la solicitud firmada y carga todos los respaldos patrimoniales e ingresos necesarios (impuesto predial, matrículas, roles, etc.).</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    with str_app.form("form_solicitud_completa", clear_on_submit=True):
        str_app.subheader("1. Datos Generales de la Operación")
        c1, c2, c3, c4 = str_app.columns(4)
        monto_sol = c1.number_input(
            "Monto Requerido ($):", min_value=300.0, value=5000.0, step=250.0
        )
        plazo_sol = c2.selectbox(
            "Plazo (Meses):", options=[6, 12, 18, 24, 36, 48, 60], index=3
        )
        dia_pago_sol = c3.selectbox(
            "Día Preferido de Pago:", list(range(1, 31)), index=4
        )
        tipo_sujeto = c4.selectbox(
            "Tipo de Sujeto:", ["Persona Natural", "Persona Jurídica"]
        )

        str_app.subheader("2. Clasificación y Destino del Crédito")
        col_t, col_d = str_app.columns(2)
        tipo_cred_sel = col_t.selectbox(
            "Tipo de Crédito:", options=list(CATALOGO_CREDITO.keys())
        )
        destino_cred_sel = col_d.selectbox(
            "Destino Específico:", options=CATALOGO_CREDITO[tipo_cred_sel]
        )

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

        str_app.subheader(
            "📍 Enlaces de Ubicación Geográfica (Croquis Digital)"
        )
        m1, m2 = str_app.columns(2)
        mapa_domicilio = m1.text_input(
            "Enlace Google Maps (Domicilio):",
            placeholder="Ej. https://maps.app.goo.gl/... o Coordenadas",
        )
        mapa_trabajo = m2.text_input(
            "Enlace Google Maps (Lugar de Trabajo):",
            placeholder="Ej. https://maps.app.goo.gl/... o Coordenadas",
        )

        str_app.subheader("4. Información Laboral y Financiera")
        l1, l2, l3, l4 = str_app.columns(4)
        empresa = l1.text_input("Empresa / Negocio:")
        cargo = l2.text_input("Cargo / Actividad:")
        ing_fijos = l3.number_input(
            "Ingresos Fijos / Ventas Mensuales ($):", value=1200.0
        )
        gastos_fam = l4.number_input(
            "Gastos Familiares / Arriendo ($):", value=500.0
        )

        str_app.subheader("5. Documentación y Respaldos de Respaldo")
        f1, f2, f3, f4 = str_app.columns(4)
        doc_solicitud_firmada = f1.file_uploader(
            "📄 Solicitud Firmada (PDF)", type=["pdf"]
        )
        doc_cedula = f2.file_uploader(
            "🪪 Cédulas (PDF/Imagen)", type=["pdf", "png", "jpg", "jpeg"]
        )
        doc_ingresos = f3.file_uploader(
            "📦 Sustento de Ingresos / ROL",
            type=["pdf", "png", "jpg", "jpeg"],
        )
        # NUEVO CAMPO HABILITADO PARA RESPALDOS PATRIMONIALES Y OTROS
        doc_patrimonial = f4.file_uploader(
            "🏛️ Respaldos Patrimoniales (Predial, Matrícula Vehicular, etc.)",
            type=["pdf", "png", "jpg", "jpeg"],
            accept_multiple_files=True,
        )

        bancos_sel = str_app.multiselect(
            "Selecciona las entidades destinatarias:",
            options=[b["nombre"] for b in ENTIDADES_DESTINO],
            default=[b["nombre"] for b in ENTIDADES_DESTINO[:3]],
        )

        btn_enviar_expediente = str_app.form_submit_button(
            "🚀 Generar Expediente y Enviar por Correo"
        )

    if btn_enviar_expediente:
        if not nombres or not cedula:
            str_app.error("⚠️ Nombres y Cédula son obligatorios.")
        else:
            datos_sol = {
                "nombre": f"{nombres} {ap_paterno} {ap_materno}".strip(),
                "cedula": cedula,
                "telefono": telefono,
                "email": email,
                "ciudad": ciudad,
                "direccion": direccion,
                "monto": monto_sol,
                "plazo": plazo_sol,
                "dia_pago": dia_pago_sol,
                "tipo_credito": tipo_cred_sel,
                "destino_credito": destino_cred_sel,
                "empresa": empresa,
                "cargo": cargo,
                "ingresos_fijos": ing_fijos,
                "gastos_familiares": gastos_fam,
                "mapa_domicilio": mapa_domicilio,
                "mapa_trabajo": mapa_trabajo,
            }

            pdf_bytes = generar_pdf_solicitud_oficial(datos_sol)
            # Agrupamos todos los archivos cargados (incluyendo la lista de múltiples respaldos patrimoniales)
            lista_adjuntos = [
                [doc_solicitud_firmada],
                [doc_cedula],
                [doc_ingresos],
                doc_patrimonial,
            ]
            correos = [
                b["email"]
                for b in ENTIDADES_DESTINO
                if b["nombre"] in bancos_sel
            ]

            guardar_solicitud_crm(datos_sol, lista_adjuntos)
            exito, msg_e = enviar_expediente_por_correo(
                datos_sol, pdf_bytes, lista_adjuntos, correos
            )

            if exito:
                str_app.success(
                    "🎉 ¡Expediente completo con respaldos patrimoniales registrado en CRM y enviado por correo con éxito!"
                )
            else:
                str_app.warning(
                    f"⚠️ Expediente guardado en CRM pero falló el envío SMTP: {msg_e}"
                )

            str_app.download_button(
                label="📥 Descargar Formato PDF de Solicitud Oficial para Firmar",
                data=pdf_bytes,
                file_name=f"Solicitud_Oficial_{cedula}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

# ------------------------------------------------------------------------------
# PESTAÑAS 2 A 7 (CRM, CALIFICACIÓN, SIMULADORES, VALUATION, CRESA, SALAS)
# ------------------------------------------------------------------------------
with tab_crm:
    str_app.subheader("📊 Pipeline CRM de Solicitudes y Expedientes")
    conn = sqlite3.connect("crm_escala.db")
    df_solicitudes = pd.read_sql_query(
        "SELECT * FROM solicitudes ORDER BY id DESC", conn
    )
    if df_solicitudes.empty:
        str_app.info("No hay solicitudes registradas actualmente en el CRM.")
    else:
        for idx, row in df_solicitudes.iterrows():
            with str_app.expander(
                f"📌 [{row['estado']}] - {row['nombre']} | Cédula: {row['cedula']} - ${row['monto']:,.2f}"
            ):
                str_app.write(
                    f"**Teléfono:** {row['telefono']} | **Email:** {row['email']}"
                )
                str_app.write(
                    f"**Tipo:** {row['tipo_credito']} | **Destino:** {row['destino']}"
                )
                dir_docs = row["directorio_docs"]
                if dir_docs and os.path.exists(dir_docs):
                    for arch in os.listdir(dir_docs):
                        with open(os.path.join(dir_docs, arch), "rb") as fd:
                            str_app.download_button(
                                f"⬇️ Descargar {arch}",
                                fd,
                                file_name=arch,
                                key=f"dl_{row['id']}_{arch}",
                            )
                if str_app.button(
                    "🗑️ Borrar Documentación (Privacidad)",
                    key=f"del_{row['id']}",
                ):
                    if dir_docs and os.path.exists(dir_docs):
                        eliminar_documentos_cliente(dir_docs)
                        c_db = conn.cursor()
                        c_db.execute(
                            "UPDATE solicitudes SET directorio_docs = '' WHERE id = ?",
                            (row["id"],),
                        )
                        conn.commit()
                        str_app.rerun()
    conn.close()

with tab_calificacion:
    str_app.subheader("🏆 Calificación del Top 3 de Ofertas")
    with str_app.form("form_reg_resp", clear_on_submit=True):
        entidad_resp = str_app.selectbox(
            "Entidad:", [b["nombre"] for b in ENTIDADES_DESTINO]
        )
        estado_resp = str_app.selectbox(
            "Dictamen:", ["APROBADO", "RECHAZADO", "CONDICIONADO"]
        )
        monto_aprob = str_app.number_input(
            "Monto Aprobado ($):", value=5000.0, step=250.0
        )
        tasa_tea = str_app.number_input("Tasa (TEA %):", value=15.5, step=0.1)
        plazo_aprob = str_app.number_input("Plazo (Meses):", value=24)
        obs = str_app.text_input("Observación:")
        if str_app.form_submit_button("➕ Registrar Oferta"):
            str_app.session_state.respuestas_bancos_manual.append({
                "Entidad": entidad_resp,
                "Estado": estado_resp,
                "Monto Aprobado": monto_aprob,
                "Tasa (TEA %)": tasa_tea,
                "Plazo (Meses)": plazo_aprob,
                "Observación": obs,
            })
            str_app.success("Registrado.")
    if str_app.session_state.respuestas_bancos_manual:
        df_r = pd.DataFrame(str_app.session_state.respuestas_bancos_manual)
        str_app.dataframe(df_r, use_container_width=True)

with tab_simuladores:
    str_app.subheader("🧮 Simulador de Capacidad de Pago y Amortización")
    mc = str_app.number_input("Monto ($)", value=10000.0)
    tc = str_app.number_input("Tasa Anual (%)", value=15.0)
    pc = str_app.selectbox("Plazo (Meses)", [12, 24, 36, 48, 60], index=2)
    im = (tc / 100) / 12
    cuota = (
        mc * (im * (1 + im) ** pc) / ((1 + im) ** pc - 1)
        if im > 0
        else mc / pc
    )
    str_app.metric("Cuota Mensual Estimada", f"${cuota:,.2f}")

with tab_valuacion:
    str_app.subheader("📈 Valuation NIIF & Tax Hub")
    str_app.write(
        "Módulo financiero avanzado para valoración de activos y flujos descontados."
    )

with tab_cresa:
    str_app.subheader("🌐 Ecosistema CRESA & Validadores OCI")
    str_app.link_button(
        "🚀 Nexum 360", "https://nexum360.com.ec/", use_container_width=True
    )
    str_app.link_button(
        "🔍 SRI RUC",
        "https://srienlinea.sri.gob.ec/sri-en-linea/SriRucWeb/ConsultaRuc/Consultas/consultaRuc",
        use_container_width=True,
    )

with tab_salas:
    str_app.subheader("🏬 Salas de Experiencia Comercial")
    str_app.link_button(
        "🛒 Orve Hogar", "https://www.orvehogar.com", use_container_width=True
    )
    str_app.link_button(
        "🛒 Almacenes Japón",
        "https://www.almacenesjapon.com",
        use_container_width=True,
    )
