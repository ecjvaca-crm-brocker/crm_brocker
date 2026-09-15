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
# 1. CONFIGURACIÓN INICIAL Y BASE DE DATOS
# ==========================================
st.set_page_config(
    page_title="ESCALA Consultoría Financiera y Empresarial",
    page_layout="wide",
    initial_sidebar_state="expanded",
)

NOMBRE_PLANTILLA_EXCEL = "Solicitud_Credito_Template.xlsx"
DIR_RESPALDOS = "./respaldos_crm"

if not os.path.exists(DIR_RESPALDOS):
    os.makedirs(DIR_RESPALDOS)


def init_db():
    """Inicializa la base de datos SQLite local para el seguimiento del CRM."""
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
            entidad TEXT,
            estado TEXT,
            directorio_docs TEXT
        )
    """
    )
    conn.commit()
    conn.close()


init_db()


# ==========================================
# 2. FUNCIONES DE MANEJO DE EXCEL (OPENPYXL)
# ==========================================
def escribir_celda_segura(ws, fila, columna, valor):
    """Escribe en la celda indicada sin fallar si hay celdas unificadas o lectura de solapamientos."""
    try:
        celda = ws.cell(row=fila, column=columna)
        celda.value = valor
    except Exception:
        pass


def prellenar_excel_solicitud(datos):
    """Abre la plantilla Excel y escribe la información requerida de forma segura."""
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

    # Fecha actual en fila 2, columna D (columna 4)
    escribir_celda_segura(ws, 2, 4, datetime.now().strftime("%Y-%m-%d"))

    # Datos del solicitante
    escribir_celda_segura(ws, 2, 1, datos.get("nombre", ""))  # Columna A
    escribir_celda_segura(ws, 2, 2, datos.get("cedula", ""))  # Columna B
    escribir_celda_segura(ws, 2, 3, datos.get("email", ""))  # Columna C
    escribir_celda_segura(ws, 2, 5, datos.get("telefono", ""))  # Columna E
    escribir_celda_segura(ws, 2, 6, datos.get("monto", 0.0))  # Columna F

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output


# ==========================================
# 3. ALMACENAMIENTO DE DOCUMENTOS Y CRM
# ==========================================
def guardar_solicitud_crm(datos_sol, archivos_cargados):
    """Guarda la solicitud en SQLite y almacena localmente los documentos subidos por el cliente."""
    cedula = datos_sol.get("cedula", "sin_cedula")
    dir_cliente = os.path.join(
        DIR_RESPALDOS, f"{cedula}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    os.makedirs(dir_cliente, exist_ok=True)

    # Guardar archivos físicamente
    if archivos_cargados:
        for archivo in archivos_cargados:
            ruta_archivo = os.path.join(dir_cliente, archivo.name)
            with open(ruta_archivo, "wb") as f:
                f.write(archivo.getbuffer())
            archivo.seek(0)

    # Registrar en SQLite
    conn = sqlite3.connect("crm_escala.db")
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO solicitudes (fecha, nombre, cedula, telefono, email, monto, entidad, estado, directorio_docs)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            datos_sol.get("nombre"),
            datos_sol.get("cedula"),
            datos_sol.get("telefono"),
            datos_sol.get("email"),
            datos_sol.get("monto"),
            datos_sol.get("entidad"),
            "En Proceso",
            dir_cliente,
        ),
    )
    conn.commit()
    conn.close()


def eliminar_documentos_cliente(dir_cliente):
    """Elimina la carpeta de documentos de un cliente para liberar espacio y asegurar privacidad."""
    if os.path.exists(dir_cliente):
        try:
            shutil.rmtree(dir_cliente)
            return True
        except Exception as e:
            st.error(f"Error al eliminar archivos del directorio: {e}")
            return False
    return False


# ==========================================
# 4. ENVÍO DE CORREO VÍA SMTP
# ==========================================
def enviar_correo_smtp(datos_sol, excel_bytes, archivos_cargados):
    """Envía la notificación por correo usando las credenciales SMTP configuradas en Secrets."""
    # Leer credenciales desde Secrets de Streamlit
    smtp_server = st.secrets["smtp"]["server"]
    smtp_port = int(st.secrets["smtp"]["port"])
    sender_email = st.secrets["smtp"]["email"]
    sender_password = st.secrets["smtp"]["password"]

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = sender_email  # Notificación interna al brocker
    msg["Subject"] = (
        f"Nueva Solicitud de Crédito - {datos_sol.get('nombre', 'Cliente')}"
    )

    cuerpo = f"""
    Se ha ingresado una nueva solicitud a través del portal:
    --------------------------------------------------
    • Cliente: {datos_sol.get('nombre')}
    • Cédula: {datos_sol.get('cedula')}
    • Teléfono: {datos_sol.get('telefono')}
    • Correo: {datos_sol.get('email')}
    • Monto Solicitado: ${datos_sol.get('monto'):,.2f}
    • Entidad Seleccionada: {datos_sol.get('entidad')}
    • Fecha de Registro: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    --------------------------------------------------
    Los documentos adjuntos y el formulario prellenado se encuentran adjuntos a este correo.
    """
    msg.attach(MIMEText(cuerpo, "plain"))

    # Adjuntar Excel prellenado
    adjunto_excel = MIMEApplication(
        excel_bytes.getvalue(), name=f"Solicitud_{datos_sol.get('cedula')}.xlsx"
    )
    adjunto_excel["Content-Disposition"] = (
        f'attachment; filename="Solicitud_{datos_sol.get("cedula")}.xlsx"'
    )
    msg.attach(adjunto_excel)

    # Adjuntar documentos subidos por el usuario
    if archivos_cargados:
        for arch in archivos_cargados:
            adjunto = MIMEApplication(arch.read(), name=arch.name)
            adjunto["Content-Disposition"] = (
                f'attachment; filename="{arch.name}"'
            )
            msg.attach(adjunto)
            arch.seek(0)

    # Conexión al servidor SMTP
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)


# ==========================================
# 5. INTERFAZ Y NAVEGACIÓN EN STREAMLIT
# ==========================================
st.sidebar.title("ESCALA Broker")
opcion = st.sidebar.radio(
    "Navegación",
    [
        "Ingreso de Solicitud",
        "Pipeline CRM / Expedientes",
        "Salas de Experiencia",
    ],
)

if opcion == "Ingreso de Solicitud":
    st.title("📄 Formulario de Solicitud de Crédito")
    st.write(
        "Ingrese la información requerida del cliente y adjunte los documentos de soporte."
    )

    with st.form("form_solicitud", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre Completo del Solicitante")
            cedula = st.text_input("Número de Cédula")
            telefono = st.text_input("Teléfono de Contacto")
        with col2:
            email = st.text_input("Correo Electrónico")
            monto = st.number_input(
                "Monto Solicitado ($)", min_value=100.0, step=500.0
            )
            entidad = st.selectbox(
                "Entidad Financiera Destino",
                [
                    "BANCO IBARRA",
                    "BANCO DEL AUSTRO",
                    "COOPERATIVA ATUNTAQUI",
                    "OTRA",
                ],
            )

        archivos_cargados = st.file_uploader(
            "Adjuntar Documentos (Cédula, Planilla, Rol de Pagos, etc.)",
            accept_multiple_files=True,
        )

        btn_enviar = st.form_submit_button("🚀 Enviar Solicitud de Crédito")

    if btn_enviar:
        if not nombre or not cedula or not email:
            st.warning(
                "⚠️ Por favor complete los campos obligatorios (Nombre, Cédula y Correo)."
            )
        else:
            datos_sol = {
                "nombre": nombre,
                "cedula": cedula,
                "telefono": telefono,
                "email": email,
                "monto": monto,
                "entidad": entidad,
            }

            with st.spinner("Procesando formulario y generando expediente..."):
                try:
                    # 1. Generar Excel rellenado
                    excel_bytes = prellenar_excel_solicitud(datos_sol)

                    # 2. Guardar registro en CRM y guardar copias locales de los documentos
                    guardar_solicitud_crm(datos_sol, archivos_cargados)

                    # 3. Enviar notificación por correo SMTP
                    enviar_correo_smtp(
                        datos_sol, excel_bytes, archivos_cargados
                    )

                    st.success(
                        "✅ ¡Solicitud procesada con éxito! Registro creado en el CRM y notificación enviada."
                    )
                except Exception as e:
                    st.error(f"❌ Error al procesar la solicitud: {e}")

elif opcion == "Pipeline CRM / Expedientes":
    st.title("📊 CRM Pipeline de Expedientes")

    conn = sqlite3.connect("crm_escala.db")
    df_solicitudes = pd.read_sql_query(
        "SELECT * FROM solicitudes ORDER BY id DESC", conn
    )

    if df_solicitudes.empty:
        st.info("No hay solicitudes registradas actualmente.")
    else:
        for idx, row in df_solicitudes.iterrows():
            with st.expander(
                f"📌 [{row['estado']}] - {row['nombre']} (Cédula: {row['cedula']}) - ${row['monto']:,.2f}"
            ):
                st.write(f"**Fecha Ingreso:** {row['fecha']}")
                st.write(f"**Contacto:** {row['telefono']} | {row['email']}")
                st.write(f"**Entidad:** {row['entidad']}")

                dir_docs = row["directorio_docs"]

                # Lista de documentos adjuntos
                st.subheader("📁 Documentación de Soporte")
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
                        st.caption(
                            "No hay archivos almacenados en el directorio."
                        )
                else:
                    st.caption(
                        "🔒 Los documentos de este expediente han sido eliminados por cumplimiento o cierre de la operación."
                    )

                # Gestión de Estados y Eliminación de Documentos
                st.subheader("⚙️ Gestión del Expediente")
                col_e1, col_e2 = st.columns(2)

                with col_e1:
                    nuevo_estado = st.selectbox(
                        "Actualizar Estado",
                        ["En Proceso", "Aprobado", "Rechazado", "Cancelado"],
                        index=[
                            "En Proceso",
                            "Aprobado",
                            "Rechazado",
                            "Cancelado",
                        ].index(row["estado"]),
                        key=f"st_{row['id']}",
                    )

                    if st.button("Guardar Estado", key=f"btn_st_{row['id']}"):
                        cursor = conn.cursor()
                        cursor.execute(
                            "UPDATE solicitudes SET estado = ? WHERE id = ?",
                            (nuevo_estado, row["id"]),
                        )
                        conn.commit()
                        st.success("Estado actualizado.")
                        st.rerun()

                with col_e2:
                    st.write("**Liberación de Almacenamiento & Privacidad**")
                    if st.button(
                        "🗑️ Cerrar Operación y Borrar Documentos",
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
                                    " Archivos eliminados de forma permanente para seguridad del cliente."
                                )
                                st.rerun()
                        else:
                            st.info("No hay archivos pendientes por borrar.")

    conn.close()

elif opcion == "Salas de Experiencia":
    st.title("🏬 Salas de Experiencia")
    st.write(
        "Acceso rápido a portales comerciales y simuladores financieros."
    )
