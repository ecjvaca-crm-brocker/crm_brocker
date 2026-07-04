import streamlit as st
import urllib.parse
import sqlite3
import pandas as pd

# ==========================================
# 1. CONFIGURACIONES INICIALES GENERALES
# ==========================================
# ¡Coloca tu número aquí! Código de país (593 para Ecuador) seguido de tu número sin el cero. Ej: "593987654321"
NUMERO_WHATSAPP = "593999999999" 

# Define la contraseña secreta que tú usarás para ver el Dashboard de tus leads
PASSWORD_DASHBOARD = "Escala2026" 

st.set_page_config(
    page_title="Escala Finance & Insurance | Tu consultor financiero de confianza", 
    page_icon="🏛️", 
    layout="wide"
)

# ==========================================
# 2. SISTEMA DE BASE DE DATOS (SQLITE AUTOMÁTICO)
# ==========================================
def conectar_db():
    conn = sqlite3.connect("escala_leads.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            nombre TEXT,
            cedula TEXT,
            telefono TEXT,
            ciudad TEXT,
            producto TEXT
        )
    """)
    conn.commit()
    return conn

def guardar_lead(nombre, cedula, telefono, ciudad, producto):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO leads (nombre, cedula, telefono, ciudad, producto) 
        VALUES (?, ?, ?, ?, ?)
    """, (nombre, cedula, telefono, ciudad, producto))
    conn.commit()
    conn.close()

def leer_leads():
    conn = conectar_db()
    df = pd.read_sql_query("SELECT fecha, nombre, cedula, telefono, ciudad, producto FROM leads ORDER BY fecha DESC", conn)
    conn.close()
    return df

# Inicializar la Base de Datos al cargar la página
conectar_db()

# ==========================================
# 3. DISEÑO DE TEMA CORPORATIVO (CSS)
# ==========================================
st.markdown("""
    <style>
    .stApp {
        background-color: #FFFFFF;
    }
    h1, h2, h3 {
        color: #0A2540 !important;
        font-family: 'Georgia', serif;
    }
    .card-corporativa {
        background-color: #F8F9FA;
        padding: 25px;
        border-radius: 8px;
        border-top: 4px solid #D4AF37;
        border-left: 1px solid #E2E8F0;
        border-right: 1px solid #E2E8F0;
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    div.stButton > button:first-child {
        background-color: #0A2540;
        color: #D4AF37;
        border: 2px solid #D4AF37;
        border-radius: 6px;
        padding: 0.6rem 2rem;
        font-weight: bold;
        font-size: 16px;
        width: 100%;
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #D4AF37;
        color: #0A2540;
        border-color: #0A2540;
    }
    .chat-bubble-vip {
        background-color: #F4F7FA;
        padding: 15px;
        border-radius: 12px;
        border-left: 4px solid #D4AF37;
        margin-bottom: 15px;
    }
    .avatar-img {
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #D4AF37;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. CABECERA PRINCIPAL Y PORTADA
# ==========================================
st.markdown("<h1 style='text-align: center; font-size: 2.8rem; margin-bottom: 0;'>🏛️ ESCALA FINANCE & INSURANCE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #D4AF37; font-size: 1.4rem; font-weight: bold; margin-top: 0;'>Tu consultor financiero de confianza</p>", unsafe_allow_html=True)

st.write("")
st.image("https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=1200&q=80", use_container_width=True)

st.markdown("""
<div class="card-corporativa">
    <h3 style='margin-top:0;'>✨ Asesoría Patrimonial y Estrategia de Financiamiento</h3>
    <p style='color: #4A5568; font-size: 1.1rem;'>Conectamos tus metas con las mejores opciones de financiamiento, inversión o protección del mercado mediante un análisis técnico riguroso y relaciones directas con proveedores institucionales.</p>
    <strong style='color: #0A2540;'>💼 Nuestra consultoría inicial no genera honorarios para ti</strong> (estos son cubiertos de manera directa por las firmas aliadas del ecosistema).
</div>
""", unsafe_allow_html=True)

st.write("---")

# Lista Global de Productos compartida por el Formulario y el Bot
productos = [
    "🎓 Crédito Educativo / Financiamiento para Maestrías",
    "💼 Crédito de Consumo o Capital de trabajo",
    "🏡 Crédito Hipotecario / Financiamiento de Vivienda",
    "🚗 Financiamiento Automotriz (Vehículos)",
    "🛡️ Seguros (Vehicular, Médico o Protección de Empresa)"
]

# Secciones principales: Formulario y Chatbot
col_izq, col_der = st.columns([1.1, 0.9])

with col_izq:
    # ==========================================
    # FORMULARIO TRADICIONAL DE CAPTURA
    # ==========================================
    st.markdown("### 📋 Pre-Calificación de Perfil")
    st.caption("Introduce la información requerida para estructurar la solución a tu medida:")
    
    with st.form(key="formulario_leads", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("👤 Nombre Completo:", placeholder="Ej: Ing. Carlos Mendoza")
        with c2:
            cedula = st.text_input("🪪 Número de Cédula:", max_chars=10, placeholder="Ej: 100xxxxxxx")
            
        c3, c4 = st.columns(2)
        with c3:
            telefono = st.text_input("📱 Celular / WhatsApp:", placeholder="Ej: 099xxxxxxx")
        with c4:
            ciudad = st.text_input("📍 Ciudad de Residencia:", placeholder="Ej: Quito / Ibarra")
            
        producto_interes = st.selectbox("🎯 Solución Financiera Requerida:", options=productos)
        
        st.write("")
        boton_enviar = st.form_submit_button("Iniciar Evaluación de Caso 🚀")

    if boton_enviar:
        if not nombre or not cedula or not telefono:
            st.error("⚠️ Los campos Nombre, Cédula y Teléfono son estrictamente obligatorios.")
        elif len(cedula) < 10 or not cedula.isdigit():
            st.error("⚠️ Documento de identidad no válido (Debe contener 10 números).")
        else:
            guardar_lead(nombre, cedula, telefono, ciudad, producto_interes)
            st.success(f"🎉 Registro guardado con éxito en el sistema central de Escala, {nombre}.")
            
            texto_ws = f"Hola Escala Finance & Insurance, acabo de completar la pre-calificación en el portal.\n\n" \
                       f"👤 *Consultante:* {nombre}\n" \
                       f"🪪 *Cédula:* {cedula}\n" \
                       f"📱 *Contacto:* {telefono}\n" \
                       f"📍 *Ciudad:* {ciudad}\n" \
                       f"🎯 *Línea:* {producto_interes}"
            
            url_whatsapp = f"https://api.whatsapp.com/send?phone={NUMERO_WHATSAPP}&text={urllib.parse.quote(texto_ws)}"
            st.balloons()
            st.markdown("""
            <div style="background-color: #FEF3C7; padding: 15px; border-radius: 6px; border: 1px solid #F59E0B; color: #92400E;">
                <strong>⚠️ ACCIÓN NECESARIA:</strong> Para validar tu identidad de forma segura y asignarte un consultor, presiona el botón inferior:
            </div>
            """, unsafe_allow_html=True)
            st.write("")
            st.link_button("🟢 Enviar Expediente vía WhatsApp", url_whatsapp, type="primary")

with col_der:
    # ==========================================
    # CHATBOT VIRTUAL INTERACTIVO CON PASOS (SOCIABLE)
    # ==========================================
    st.markdown("### 🤖 Consultor Virtual Interactivo")
    
    # Inicialización de las variables de sesión del bot para recordar las respuestas
    if "bot_paso" not in st.session_state:
        st.session_state.bot_paso = 0
        st.session_state.bot_producto = ""
        st.session_state.bot_nombre = ""
        st.session_state.bot_cedula = ""
        st.session_state.bot_telefono = ""
        st.session_state.bot_ciudad = ""

    with st.container(border=True):
        
        # --- PASO 0: Bienvenida y Selección del Producto ---
        if st.session_state.bot_paso == 0:
            st.markdown("""
            <div class="chat-bubble-vip">
                <strong>🤖 EscalaBot:</strong> ¡Hola! Bienvenido a Escala Finance & Insurance. Soy tu asesor virtual corporativo. <br><br>
                Para guiarte de forma personalizada, <strong>¿cuál de nuestras soluciones financieras o de protección estás buscando hoy?</strong>
            </div>
            """, unsafe_allow_html=True)
            
            prod_elegido = st.selectbox("Selecciona una opción para iniciar el chat:", ["-- Selecciona un servicio --"] + productos, key="bot_prod_select")
            if prod_elegido != "-- Selecciona un servicio --":
                st.session_state.bot_producto = prod_elegido
                st.session_state.bot_paso = 1
                st.rerun()

        # --- PASO 1: Captura de Nombre ---
        elif st.session_state.bot_paso == 1:
            st.markdown(f"""
            <div class="chat-bubble-vip">
                🎯 <strong>Línea seleccionada:</strong> {st.session_state.bot_producto}<br><br>
                <strong>🤖 EscalaBot:</strong> Excelente elección. Contamos con convenios institucionales directos para esa área.<br>
                Por favor, ingresa tu <strong>Nombre y Apellido Completo</strong> para registrar tu atención:
            </div>
            """, unsafe_allow_html=True)
            
            nom_input = st.text_input("Escribe tu nombre aquí:", key="input_bot_nom")
            if st.button("Continuar ➡️", key="btn_bot_1"):
                if nom_input.strip() != "":
                    st.session_state.bot_nombre = nom_input
                    st.session_state.bot_paso = 2
                    st.rerun()
                else:
                    st.error("Por favor, ingresa tu nombre para continuar.")

        # --- PASO 2: Captura de Cédula ---
        elif st.session_state.bot_paso == 2:
            st.markdown(f"""
            <div class="chat-bubble-vip">
                <strong>🤖 EscalaBot:</strong> Un gusto saludarte, {st.session_state.bot_nombre}.<br>
                Para la pre-calificación en el sistema, necesito que me indiques tu <strong>Número de Cédula</strong> (10 dígitos):
            </div>
            """, unsafe_allow_html=True)
            
            ced_input = st.text_input("Escribe tu cédula aquí:", max_chars=10, key="input_bot_ced")
            if st.button("Continuar ➡️", key="btn_bot_2"):
                if len(ced_input) == 10 and ced_input.isdigit():
                    st.session_state.bot_cedula = ced_input
                    st.session_state.bot_paso = 3
                    st.rerun()
                else:
                    st.error("La cédula debe tener estrictamente 10 números.")

        # --- PASO 3: Captura de Teléfono y Ciudad ---
        elif st.session_state.bot_paso == 3:
            st.markdown(f"""
            <div class="chat-bubble-vip">
                <strong>🤖 EscalaBot:</strong> ¡Perfecto! Ya casi terminamos.<br>
                Por último, confírmame tu <strong>Número de Celular (WhatsApp)</strong> y tu <strong>Ciudad de residencia</strong> actual:
            </div>
            """, unsafe_allow_html=True)
            
            tel_input = st.text_input("Celular (Ej: 099xxxxxxx):", key="input_bot_tel")
            ciu_input = st.text_input("Ciudad (Ej: Quito):", key="input_bot_ciu")
            
            if st.button("Finalizar Consultoría Virtual 🚀", key="btn_bot_3"):
                if tel_input.strip() != "" and ciu_input.strip() != "":
                    st.session_state.bot_telefono = tel_input
                    st.session_state.bot_ciudad = ciu_input
                    
                    # GUARDAR EN SQL DESDE EL BOT
                    guardar_lead(
                        st.session_state.bot_nombre, 
                        st.session_state.bot_cedula, 
                        st.session_state.bot_telefono, 
                        st.session_state.bot_ciudad, 
                        st.session_state.bot_producto
                    )
                    st.session_state.bot_paso = 4
                    st.rerun()
                else:
                    st.error("Ambos campos son obligatorios para guardar el registro.")

        # --- PASO 4: Cierre Exitoso y Enlace Directo a tu WhatsApp ---
        elif st.session_state.bot_paso == 4:
            st.markdown(f"""
            <div class="chat-bubble-vip" style="border-left: 4px solid #10B981;">
                <strong>🎉 ¡Análisis del Bot Terminado con Éxito!</strong><br><br>
                <strong>🤖 EscalaBot:</strong> He generado tu expediente técnico y lo he guardado de forma segura en nuestro servidor central.<br><br>
                Para asignarte un analista humano en este instante y revisar tasas de interés vigentes, presiona el botón verde de abajo para enviarme tu resumen directamente a mi WhatsApp. ¡Un placer ayudarte!
            </div>
            """, unsafe_allow_html=True)
            
            texto_bot_ws = f"Hola Escala Finance & Insurance, completé la consulta interactiva con el EscalaBot.\n\n" \
                           f"👤 *Consultante:* {st.session_state.bot_nombre}\n" \
                           f"🪪 *Cédula:* {st.session_state.bot_cedula}\n" \
                           f"📱 *Contacto:* {st.session_state.bot_telefono}\n" \
                           f"📍 *Ciudad:* {st.session_state.bot_ciudad}\n" \
                           f"🎯 *Línea Solicitada:* {st.session_state.bot_producto}"
            
            url_bot_whatsapp = f"https://api.whatsapp.com/send?phone={NUMERO_WHATSAPP}&text={urllib.parse.quote(texto_bot_ws)}"
            
            st.link_button("🟢 Conectarse con un Analista por WhatsApp", url_bot_whatsapp, type="primary")
            st.write("")
            
            if st.button("🔄 Iniciar otra consulta en el Bot"):
                st.session_state.bot_paso = 0
                st.session_state.bot_producto = ""
                st.session_state.bot_nombre = ""
                st.session_state.bot_cedula = ""
                st.session_state.bot_telefono = ""
                st.session_state.bot_ciudad = ""
                st.rerun()

st.write("---")

# ==========================================
# 5. INDICADORES ECONÓMICOS & NOTICIAS
# ==========================================
st.markdown("### 📊 Indicadores Económicos Mundiales y Locales")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric(label="🇺🇸 S&P 500", value="5,137.08", delta="+0.80%")
m2.metric(label="💻 NASDAQ 100", value="18,302.91", delta="+1.14%")
m3.metric(label="🛢️ Crudo Oriente (Ecuador)", value="$78.26", delta="-0.45%")
m4.metric(label="🏛️ BV Quito", value="1,045.20", delta="+0.12%")
m5.metric(label="🏦 BV Guayaquil", value="985.40", delta="-0.08%")

st.write("---")

col_noticias, col_linkedin, col_youtube = st.columns([1, 1, 1])

with col_noticias:
    st.markdown("### 📰 Actualidad y Economía")
    st.markdown("""
    * **Bloomberg:** *Bancos centrales evalúan ajustes de tasas de interés comerciales para el tercer trimestre.*
    * **CNN Business:** *Mercados globales reaccionan al alza impulsados por el sector de tecnología e IA.*
    * **Revista Ekos:** *Ecuador registra un incremento en solicitudes de microcréditos productivos corporativos.*
    """)

with col_linkedin:
    st.markdown("### 🔗 Publicaciones en LinkedIn")
    st.markdown("Manténgase conectado con mis análisis de mercado, liderazgo y consejos corporativos de primera mano.")
    st.write("")
    st.link_button("🌐 Visitar Mi Perfil en LinkedIn", "https://linkedin.com/in/jonathan-paul-vaca-cruz-70b378b8")

with col_youtube:
    st.markdown("### 🎥 Educación Financiera")
    st.caption("Material audiovisual extraído de mi canal de YouTube:")
    st.write("")
    st.link_button("📺 Ir a mi Canal de YouTube", "http://www.youtube.com/@jonathanvaca3000")

st.write("---")

# ==========================================
# 6. TESTIMONIOS CON FOTOGRAFÍAS REALES/PROFESIONALES
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
        <div style="background-color: #F8F9FA; padding: 12px; border-radius: 6px; border-left: 3px solid #D4AF37;">
            "La consultoría para el equipamiento de mi clínica odontológica fue impecable. Conseguí la tasa idónea."<br>
            <small style='color:#718096;'><strong>- Dr. Alejandro R. (Odontólogo)</strong></small>
        </div>
        """, unsafe_allow_html=True)

with t2:
    ft2, txt2 = st.columns([1, 3])
    with ft2:
        st.image("https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&h=150&q=80", use_container_width=True)
    with txt2:
        st.markdown("""
        <div style="background-color: #F8F9FA; padding: 12px; border-radius: 6px; border-left: 3px solid #D4AF37;">
            "Gracias a su asesoría técnica logré financiar mi Maestría en Dirección de Empresas sin comprometer mi liquidez."<br>
            <small style='color:#718096;'><strong>- Mgs. Lorena P. (Arquitecta)</strong></small>
        </div>
        """, unsafe_allow_html=True)

with t3:
    ft3, txt3 = st.columns([1, 3])
    with ft3:
        st.image("https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&w=150&h=150&q=80", use_container_width=True)
    with txt3:
        st.markdown("""
        <div style="background-color: #F8F9FA; padding: 12px; border-radius: 6px; border-left: 3px solid #D4AF37;">
            "Excelente servicio para la emisión de la póliza de seguro vehicular de nuestra flota de distribución empresarial."<br>
            <small style='color:#718096;'><strong>- Ing. Javier G. (Gerente General)</strong></small>
        </div>
        """, unsafe_allow_html=True)

st.write("---")

# ==========================================
# 7. CONTROL INTERNO: DASHBOARD DE SEGUIMIENTO (OCULTO)
# ==========================================
st.markdown("### 🔒 Panel de Control Interno")

with st.expander("🔑 Acceder al Dashboard Ejecutivo (Uso exclusivo de Consultores)"):
    pass_input = st.text_input("Ingrese la clave de seguridad para visualizar métricas:", type="password")
    
    if pass_input == PASSWORD_DASHBOARD:
        st.success("🔓 Acceso concedido de forma segura.")
        
        df_leads = leer_leads()
        
        if df_leads.empty:
            st.info("📊 El sistema de bases de datos se encuentra activo pero aún no se registran leads el día de hoy.")
        else:
            total_leads = len(df_leads)
            st.metric(label="📈 Total de Prospectos Capturados", value=total_leads)
            
            dash_col1, dash_col2 = st.columns([1, 1])
            
            with dash_col1:
                st.markdown("#### 🎯 Solicitudes por Tipo de Producto")
                conteo_productos = df_leads["producto"].value_counts()
                st.bar_chart(conteo_productos)
                
            with dash_col2:
                st.markdown("#### 📍 Concentración Geográfica")
                conteo_ciudades = df_leads["ciudad"].value_counts()
                st.bar_chart(conteo_ciudades)
                
            st.write("")
            st.markdown("#### 📑 Historial Completo de Expedientes en SQL")
            st.dataframe(df_leads, use_container_width=True)
    elif pass_input != "":
        st.error("❌ Contraseña incorrecta. El acceso al sistema central permanece revocado.")
