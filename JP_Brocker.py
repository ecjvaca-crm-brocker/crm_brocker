from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import shutil
import sqlite3
import smtplib
from io import BytesIO

import gspread
import openpyxl
import pandas as pd
import streamlit as st

# ==========================================
# 1. CONFIGURACIÓN INICIAL Y BRANDING DE ESCALA
# ==========================================
st.set_page_config(
    page_title="ESCALA Consultoría Financiera y Empresarial",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

NOMBRE_PLANTILLA_EXCEL = "Solicitud_Credito_Template.xlsx"
DIR_RESPALDOS = "./respaldos_crm"

if not os.path.exists(DIR_RESPALDOS):
    os.makedirs(DIR_RESPALDOS)

# Estilos CSS Avanzados
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 5px solid #1E3A8A;
    }
    .stButton>button {
        background-color: #1E3A8A;
        color: white;
        font-weight: bold;
        border-radius: 6px;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 2. BASE DE DATOS LOCAL Y DRIVE BACKUP
# ==========================================
def init_db():
    conn = sqlite3.connect("crm_escala.db")
    c = conn.cursor()
    c.execute(
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
            entidad TEXT,
            tipo_credito TEXT,
            estado TEXT,
            score TEXT,
            directorio_docs TEXT
        )
    """
    )
    conn.commit()
    conn.close()


init_db()


# ==========================================
# 3. CONEXIÓN A GOOGLE SHEETS & EXCEL
# ==========================================
@st.cache_data(ttl=300)
def cargar_entidades_financieras():
    """Carga la lista de bancos/cooperativas desde Google Sheets de forma segura."""
    try:
        if "gcp_service_account" in st.secrets:
            gc = gspread.service_account_from_dict(
                st.secrets["gcp_service_account"]
            )
            sh = gc.open_by_key(
                st.secrets.get("spreadsheet_id", "")
            )  # Carga según secrets
            ws = sh.worksheet("ENTIDADES_FIN")
            datos = ws.get_all_records()
            df = pd.DataFrame(datos)
            if "ENTIDAD FINA" in df.columns:
                return df["ENTIDAD FINA"].dropna().tolist()
    except Exception:
        pass
    return [
        "BANCO IBARRA",
        "BANCO DEL AUSTRO",
        "COOPERATIVA ATUNTAQUI",
        "COOPERATIVA PABLO MUÑOZ VEGA",
        "COOPERATIVA MEGAPROGRESO",
        "OTRA ENTIDAD",
    ]


def escribir_celda_segura(ws, fila, columna, valor):
    """Garantiza la compatibilidad con openpyxl en celdas unificadas."""
    try:
        celda = ws.cell(row=fila, column=columna)
        celda.value = valor
    except Exception:
        pass


def prellenar_excel_solicitud(datos):
    """Carga y completa la matriz de crédito en Excel usando openpyxl."""
    if os.path.exists(NOMBRE_PLANTILLA_EXCEL):
        wb = openpyxl.load_workbook(NOMBRE_PLANTILLA_EXCEL)
    else:
        wb = openpyxl.Workbook()

    if "ENTIDADES_FIN" in wb.sheetnames:
        ws = wb["ENTIDADES_FIN"]
    elif "Sol. Crédito PN" in wb.sheetnames:
        ws = wb["Sol. Crédito PN"]
    else:
        ws = wb.active

    # Rellenar información general
    escribir_celda_segura(ws, 2, 4, datetime.now().strftime("%Y-%m-%d"))  # Col D
    escribir_celda_segura(ws, 2, 1, datos.get("nombre", ""))  # Col A
    escribir_celda_segura(ws, 2, 2, datos.get("cedula", ""))  # Col B
    escribir_celda_segura(ws, 2, 3, datos.get("email", ""))  # Col C
    escribir_celda_segura(ws, 2, 5, datos.get("telefono", ""))  # Col E
    escribir_celda_segura(ws, 2, 6, datos.get("monto", 0.0))  # Col F
    escribir_celda_segura(ws, 2, 7, datos.get("plazo", 12))  # Col G
    escribir_celda_segura(ws, 2, 8, datos.get("tipo_credito", ""))  # Col H

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output


# ==========================================
# 4. SISTEMA DE RESPALDO Y PRIVACIDAD CRM
# ==========================================
def guardar_solicitud_crm(datos_sol, archivos_cargados):
    """Crea la estructura de carpetas local e inserta el registro en el CRM."""
    cedula = datos_sol.get("cedula", "sin_cedula")
    dir_cliente = os.path.join(
        DIR_RESPALDOS, f"{cedula}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    os.makedirs(dir_cliente, exist_ok=True)

    if archivos_cargados:
        for archivo in archivos_cargados:
            ruta_archivo = os.path.join(dir_cliente, archivo.name)
            with open(ruta_archivo, "wb") as f:
                f.write(archivo.getbuffer())
            archivo.seek(0)

    conn = sqlite3.connect("crm_escala.db")
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO solicitudes 
        (fecha, nombre, cedula, telefono, email, monto, plazo, entidad, tipo_credito, estado, score, directorio_docs)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            datos_sol.get("nombre"),
            datos_sol.get("cedula"),
            datos_sol.get("telefono"),
            datos_sol.get("email"),
            datos_sol.get("monto"),
            datos_sol.get("plazo"),
            datos_sol.get("entidad"),
            datos_sol.get("tipo_credito"),
            "En Proceso",
            datos_sol.get("score", "Baja Exposición"),
            dir_cliente,
        ),
    )
    conn.commit()
    conn.close()


def eliminar_documentos_cliente(dir_cliente):
    """Limpia la documentación adjunta para liberar espacio y asegurar el cumplimiento de privacidad."""
    if os.path.exists(dir_cliente):
        try:
            shutil.rmtree(dir_cliente)
            return True
        except Exception as e:
            st.error(f"Error al eliminar carpeta: {e}")
            return False
    return False


# ==========================================
# 5. NOTIFICACIONES SMTP (GMAIL)
# ==========================================
def enviar_correo_smtp(datos_sol, excel_bytes, archivos_cargados):
    """Envía la notificación automática al Broker por correo electrónico SMTP."""
    smtp_server = st.secrets["smtp"]["server"]
    smtp_port = int(st.secrets["smtp"]["port"])
    sender_email = st.secrets["smtp"]["email"]
    sender_password = st.secrets["smtp"]["password"]

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = sender_email
    msg["Subject"] = (
        f"NUEVA SOLICITUD DE CRÉDITO - {datos_sol.get('nombre', 'Cliente')}"
    )

    cuerpo = f"""
    🏢 ESCALA Consultoría Financiera y Empresarial
    ==================================================
    Se ha ingresado una nueva solicitud de crédito:

    👤 CLIENTE: {datos_sol.get('nombre')}
    🆔 CÉDULA: {datos_sol.get('cedula')}
    📞 TELÉFONO: {datos_sol.get('telefono')}
    ✉️ CORREO: {datos_sol.get('email')}

    💰 MONTO SOLICITADO: ${datos_sol.get('monto'):,.2f}
    📅 PLAZO: {datos_sol.get('plazo')} meses
    🏦 ENTIDAD DESTINO: {datos_sol.get('entidad')}
    🏷️ TIPO DE CRÉDITO: {datos_sol.get('tipo_credito')}
    📊 PRE-SCORING: {datos_sol.get('score')}
    ==================================================
    Los documentos adjuntos y el archivo de solicitud prellenado están adjuntos a este correo.
    """
    msg.attach(MIMEText(cuerpo, "plain"))

    # Adjuntar Excel
    adjunto_excel = MIMEApplication(
        excel_bytes.getvalue(), name=f"Solicitud_{datos_sol.get('cedula')}.xlsx"
    )
    adjunto_excel["Content-Disposition"] = (
        f'attachment; filename="Solicitud_{datos_sol.get("cedula")}.xlsx"'
    )
    msg.attach(adjunto_excel)

    # Adjuntar Archivos del cliente
    if archivos_cargados:
        for arch in archivos_cargados:
            adjunto = MIMEApplication(arch.read(), name=arch.name)
            adjunto["Content-Disposition"] = (
                f'attachment; filename="{arch.name}"'
            )
            msg.attach(adjunto)
            arch.seek(0)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)


# ==========================================
# 6. ENCABEZADO Y MENU
# ==========================================
st.markdown(
    '<div class="main-header">ESCALA Consultoría Financiera</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-header">Fábrica de Crédito y Pipeline Integrado CRM</div>',
    unsafe_allow_html=True,
)

st.sidebar.title("Navegación ESCALA")
opcion = st.sidebar.radio(
    "Seleccione el Módulo",
    [
        "📝 Ingreso de Solicitud",
        "📊 Pipeline CRM / Expedientes",
        "🧮 Simulador Financiero",
        "🏛️ Salas de Experiencia",
    ],
)

# LISTA DINÁMICA DE BANCOS DESDE SHEETS
entidades_lista = cargar_entidades_financieras()

# ==========================================
# MÓDULO 1: INGRESO DE SOLICITUD
# ==========================================
if opcion == "📝 Ingreso de Solicitud":
    st.subheader("Formulario de Admisión de Crédito")

    with st.form("form_admision", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre Completo del Cliente")
            cedula = st.text_input("Número de Cédula / RUC")
            telefono = st.text_input("Teléfono celular")
            email = st.text_input("Correo Electrónico")

        with col2:
            monto = st.number_input(
                "Monto Solicitado ($)", min_value=500.0, step=500.0, value=5000.0
            )
            plazo = st.selectbox(
                "Plazo Sugerido (meses)", [12, 24, 36, 48, 60, 72]
            )
            tipo_credito = st.selectbox(
                "Tipo de Crédito",
                [
                    "Consumo Prioritario",
                    "Microcrédito / Emprendimiento",
                    "Comercial Pyme",
                    "Hipotecario",
                    "Inversión Vehicular",
                ],
            )
            entidad = st.selectbox("Entidad Financiera Target", entidades_lista)

        st.markdown("---")
        st.subheader("📎 Documentos de Soporte Requeridos")
        archivos_cargados = st.file_uploader(
            "Cargar Cédula, Planillas, ROL de Pagos o Declaraciones (PDF / PNG / JPG)",
            accept_multiple_files=True,
        )

        btn_enviar = st.form_submit_button("🚀 Procesar Solicitud de Crédito")

    if btn_enviar:
        if not nombre or not cedula or not email:
            st.error("⚠️ Complete los campos requeridos (Nombre, Cédula y Correo).")
        else:
            # Pre-scoring automático rápido
            score_calculado = "Óptimo" if monto <= 15000 else "Evaluación Especial"

            datos_sol = {
                "nombre": nombre,
                "cedula": cedula,
                "telefono": telefono,
                "email": email,
                "monto": monto,
                "plazo": plazo,
                "tipo_credito": tipo_credito,
                "entidad": entidad,
                "score": score_calculado,
            }

            with st.spinner("Generando matrices y registrando en el CRM..."):
                try:
                    excel_bytes = prellenar_excel_solicitud(datos_sol)
                    guardar_solicitud_crm(datos_sol, archivos_cargados)
                    enviar_correo_smtp(
                        datos_sol, excel_bytes, archivos_cargados
                    )
                    st.success(
                        f"✅ ¡Solicitud ingresada con éxito! Registro creado en el CRM y notificación enviada."
                    )
                except Exception as e:
                    st.error(f"❌ Error al procesar solicitud: {e}")

# ==========================================
# MÓDULO 2: PIPELINE CRM / EXPEDIENTES
# ==========================================
elif opcion == "📊 Pipeline CRM / Expedientes":
    st.subheader("Panel de Control del Pipeline de Crédito")

    conn = sqlite3.connect("crm_escala.db")
    df_solicitudes = pd.read_sql_query(
        "SELECT * FROM solicitudes ORDER BY id DESC", conn
    )

    if df_solicitudes.empty:
        st.info("No hay registros almacenados en la base de datos CRM.")
    else:
        # Métricas de la parte superior
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Solicitudes", len(df_solicitudes))
        m2.metric(
            "Monto Solicitado Total",
            f"${df_solicitudes['monto'].sum():,.2f}",
        )
        m3.metric(
            "En Proceso",
            len(df_solicitudes[df_solicitudes["estado"] == "En Proceso"]),
        )
        m4.metric(
            "Aprobados",
            len(df_solicitudes[df_solicitudes["estado"] == "Aprobado"]),
        )

        st.markdown("---")

        for idx, row in df_solicitudes.iterrows():
            with st.expander(
                f"📌 [{row['estado']}] - {row['nombre']} | {row['tipo_credito']} - ${row['monto']:,.2f}"
            ):
                c_a, c_b = st.columns(2)
                with c_a:
                    st.write(
                        f"**Cédula / RUC:** {row['cedula']} | **Teléfono:** {row['telefono']}"
                    )
                    st.write(f"**Correo:** {row['email']}")
                    st.write(
                        f"**Monto:** ${row['monto']:,.2f} a {row['plazo']} meses"
                    )
                with c_b:
                    st.write(f"**Entidad Financiera:** {row['entidad']}")
                    st.write(f"**Pre-scoring:** {row['score']}")
                    st.write(f"**Fecha Ingreso:** {row['fecha']}")

                # Descarga de Archivos
                dir_docs = row["directorio_docs"]
                st.subheader("📁 Documentos en Custodia")
                if dir_docs and os.path.exists(dir_docs):
                    archivos = os.listdir(dir_docs)
                    if archivos:
                        for arch in archivos:
                            ruta_f = os.path.join(dir_docs, arch)
                            with open(ruta_f, "rb") as file_data:
                                st.download_button(
                                    label=f"⬇️ Descargar {arch}",
                                    data=file_data,
                                    file_name=arch,
                                    key=f"dl_{row['id']}_{arch}",
                                )
                    else:
                        st.caption("Carpeta vacía.")
                else:
                    st.warning(
                        "🔒 Los documentos de este cliente han sido eliminados por cumplimiento y privacidad."
                    )

                # Cambio de estado y destrucción segura de datos
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    nuevo_estado = st.selectbox(
                        "Actualizar Estado",
                        ["En Proceso", "Aprobado", "Rechazado", "Liquidado"],
                        index=[
                            "En Proceso",
                            "Aprobado",
                            "Rechazado",
                            "Liquidado",
                        ].index(row["estado"]),
                        key=f"st_{row['id']}",
                    )
                    if st.button("Guardar Cambios", key=f"btn_st_{row['id']}"):
                        cursor = conn.cursor()
                        cursor.execute(
                            "UPDATE solicitudes SET estado = ? WHERE id = ?",
                            (nuevo_estado, row["id"]),
                        )
                        conn.commit()
                        st.success("Estado actualizado correctamente.")
                        st.rerun()

                with col_e2:
                    st.write("**Seguridad & Limpieza de Espacio**")
                    if st.button(
                        "🗑️ Destruir Documentación y Cerrar Expediente",
                        key=f"btn_del_{row['id']}",
                    ):
                        if dir_docs and os.path.exists(dir_docs):
                            if eliminar_documentos_cliente(dir_docs):
                                cursor = conn.cursor()
                                cursor.execute(
                                    "UPDATE solicitudes SET directorio_docs = '' WHERE id = ?",
                                    (row["id"],),
                                )
                                conn.commit()
                                st.success(
                                    "Documentación borrada definitivamente."
                                )
                                st.rerun()

    conn.close()

# ==========================================
# MÓDULO 3: SIMULADOR FINANCIERO
# ==========================================
elif opcion == "🧮 Simulador Financiero":
    st.subheader("Simulador de Cuota Alemana y Francesa")

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        monto_sim = st.number_input(
            "Monto ($)", min_value=1000.0, value=10000.0, step=1000.0
        )
    with col_s2:
        tasa_sim = st.number_input(
            "Tasa Interés Anual (%)",
            min_value=1.0,
            max_value=30.0,
            value=16.0,
            step=0.5,
        )
    with col_s3:
        plazo_sim = st.slider("Plazo (Meses)", 6, 72, 24)

    tasa_mensual = (tasa_sim / 100) / 12
    cuota_francesa = (monto_sim * tasa_mensual) / (
        1 - (1 + tasa_mensual) ** (-plazo_sim)
    )

    st.markdown("---")
    st.markdown(
        f"### 💡 **Cuota Fija Estimada (Sistema Francés):** `${cuota_francesa:,.2f} / mes`"
    )

# ==========================================
# MÓDULO 4: SALAS DE EXPERIENCIA
# ==========================================
elif opcion == "🏛️ Salas de Experiencia":
    st.subheader("Enlaces y Portales de la Red de Brockerage")
    st.write(
        "Acceda rápidamente a los portales institucionales de las entidades aliadas:"
    )

    c1, c2, c3 = st.columns(3)
    c1.link_button("🌐 Banco del Austro", "https://www.bancodelaustro.com")
    c2.link_button("🌐 Cooperativa Atuntaqui", "https://atuntaqui.fin.ec")
    c3.link_button(
        "🌐 Coop. Pablo Muñoz Vega", "https://www.cpmv.fin.ec"
    )
