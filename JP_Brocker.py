import streamlit as st
import urllib.parse
import sqlite3
import pandas as pd
from datetime import datetime

# ==========================================
# 1. CONFIGURACIONES INICIALES GENERALES
# ==========================================
# ¡Código de país (593 para Ecuador) seguido de tu número sin el cero.
NUMERO_WHATSAPP = "593998076979" 

# Contraseña de acceso al Dashboard Corporativo
PASSWORD_DASHBOARD = "Escala2026" 

st.set_page_config(
    page_title="Escala Finance & Insurance | Consultoría Financiera y Corretaje", 
    page_icon="🏛️", 
    layout="wide"
)

# URL de respaldo estable en la nube para el avatar corporativo (Evita rupturas por strings base64 truncados)
URL_FOTO_ASESOR = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

# ==========================================
# 2. CAPA DE PERSISTENCIA (CONEXIÓN BASE DE DATOS SQLITE)
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

# Inicializar Base de Datos de manera segura en cada arranque
init_db()

# ==========================================
# 3. IDENTIDAD VISUAL PREMIUM (CSS)
# ==========================================
st.markdown("""
    <style>
    /* Fondo Financiero Corporativo */
    .stApp {
        background: linear-gradient(135deg, #FFFFFF 0%, #EBF4FC 100%);
    }
    h1, h2, h3 {
        color: #0A2540 !important;
        font-family: 'Georgia', serif;
    }
    
    /* Contenedor Principal Elegante */
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
    
    /* Botones con el Verde Éxito Corporativo */
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
    
    /* Caja Especial del Asesor Ejecutivo Virtual */
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
        width: 115px;
        height: 115px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #D4AF37;
        margin: 0 auto 12px auto;
        display: block;
    }
    
    /* --- SLIDER CONTINUO --- */
    .slider-container {
        width: 100%;
        max-height: 220px;
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
        width: 20%;
        position: relative;
    }
    .slide img {
        width: 100%;
        height: 220px;
        object-fit: cover;
        filter: brightness(70%);
    }
    .slide-text {
        position: absolute;
        bottom: 20px;
        left: 30px;
        color: #FFFFFF;
        font-family: 'Georgia', serif;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.85);
    }
    .slide-text h2 {
        color: #D4AF37 !important;
        margin: 0;
        font-size: 1.7rem;
    }
    .slide-text p {
        margin: 5px 0 0 0;
        font-size: 1.1rem;
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
# 4. CABECERA PRINCIPAL
# ==========================================
st.markdown("<h1 style='text-align: center; font-size: 2.8rem; margin-bottom: 0;'>🏛️ ESCALA FINANCE & INSURANCE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #D4AF37; font-size: 1.4rem; font-weight: bold; margin-top: 0;'>Tu consultor financiero de confianza</p>", unsafe_allow_html=True)
st.write("")

# ==========================================
# 5. BANNER ROTATIVO INTERACTIVO
# ==========================================
st.markdown("""
<div class="slider-container">
    <div class="slider-track">
        <div class="slide">
            <img src="https://images.unsplash.com/photo-1591696205602-2f950c417cb9?auto=format&fit=crop&w=1200&h=300&q=72">
            <div class="slide-text">
                <h2>Servicio de Asesoría Financiera Corporativa</h2>
                <p>Estructuración técnica independiente de soluciones de liquidez.</p>
            </div>
        </div>
        <div class="slide">
            <img src="https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&w=1200&h=300&q=72">
            <div class="slide-text">
                <h2>Servicio de Asesoría en Finanzas Personales</h2>
                <p>Optimización patrimonial y planificación de capital de largo plazo.</p>
            </div>
        </div>
        <div class="slide">
            <img src="https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=1200&h=300&q=72">
            <div class="slide-text">
                <h2>Servicio de Asesoría Inmobiliaria e Hipotecaria</h2>
                <p>Intermediación técnica y corretaje ágil para compra de bienes.</p>
            </div>
        </div>
        <div class="slide">
            <img src="https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=1200&h=300&q=72">
            <div class="slide-text">
                <h2>Servicio de Asesoría para Estudios y Maestrías</h2>
                <p>Canalización de recursos educativos para potenciar tu perfil profesional.</p>
            </div>
        </div>
        <div class="slide">
            <img src="https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=1200&h=300&q=72">
            <div class="slide-text">
                <h2>Servicio de Asesoría en Seguros y Respaldo Patrimonial</h2>
                <p>Mitigación técnica de riesgos para ti, tu familia y tu empresa.</p>
            </div>
        </div>
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
            guardar_lead(nombre, cedula, telefono, city=ciudad, product=producto_interes)
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
# 6. INDICADORES ECONÓMICOS & REDES SOCIALES
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
# 7. TESTIMONIOS CON AVATARES
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
# 8. PANEL DE CONTROL INTERNO (DASHBOARD)
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
