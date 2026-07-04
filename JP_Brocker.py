import streamlit as st
import urllib.parse
import sqlite3
import pandas as pd

# ==========================================
# 1. CONFIGURACIONES INICIALES GENERALES
# ==========================================
# ¡Coloca tu número aquí! Código de país (593 para Ecuador) seguido de tu número sin el cero. Ej: "593999999999"
NUMERO_WHATSAPP = "593998076979" 

# Contraseña de acceso al Dashboard Corporativo
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

# Inicializar Base de Datos
conectar_db()

# ==========================================
# 3. IDENTIDAD VISUAL PREMIUM: AZUL MARINO, DORADO Y VERDE FINANCIERO (CSS)
# ==========================================
st.markdown("""
    <style>
    /* Fondo con degradado sofisticado corporativo */
    .stApp {
        background: linear-gradient(135deg, #FFFFFF 0%, #F0F4F8 100%);
    }
    h1, h2, h3 {
        color: #0A2540 !important;
        font-family: 'Georgia', serif;
    }
    
    /* Contenedor principal con bordes dorados y fondos pulidos */
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
    
    /* Botones principales con el Verde Éxito Financiero */
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
    
    /* Perfil del Ejecutivo Virtual */
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
        width: 110px;
        height: 110px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #D4AF37;
        margin: 0 auto 15px auto;
        display: block;
    }
    
    /* --- ANIMACIÓN SLIDER CONTINUO (De Derecha a Izquierda) --- */
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
        width: 500%; /* Espacio para las 5 imágenes de servicios */
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
        filter: brightness(75%);
    }
    .slide-text {
        position: absolute;
        bottom: 20px;
        left: 30px;
        color: #FFFFFF;
        font-family: 'Georgia', serif;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.8);
    }
    .slide-text h2 {
        color: #D4AF37 !important;
        margin: 0;
        font-size: 1.8rem;
    }
    .slide-text p {
        margin: 5px 0 0 0;
        font-size: 1.1rem;
        font-weight: bold;
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
# 4. CABECERA PRINCIPAL EN AZUL CORPORATIVO
# ==========================================
st.markdown("<h1 style='text-align: center; font-size: 2.8rem; margin-bottom: 0;'>🏛️ ESCALA FINANCE & INSURANCE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #D4AF37; font-size: 1.4rem; font-weight: bold; margin-top: 0;'>Tu consultor financiero de confianza</p>", unsafe_allow_html=True)
st.write("")

# ==========================================
# 5. BANNER ROTATIVO INTERACTIVO DE SERVICIOS (72 PPP DINÁMICO)
# ==========================================
st.markdown("""
<div class="slider-container">
    <div class="slider-track">
        <!-- Slide 1: Asesoría Financiera -->
        <div class="slide">
            <img src="https://images.unsplash.com/photo-1591696205602-2f950c417cb9?auto=format&fit=crop&w=1200&h=300&q=72">
            <div class="slide-text">
                <h2>Asesoría Financiera Corporativa</h2>
                <p>Estrategia y estructura de financiamiento a tu medida.</p>
            </div>
        </div>
        <!-- Slide 2: Finanzas Personales -->
        <div class="slide">
            <img src="https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&w=1200&h=300&q=72">
            <div class="slide-text">
                <h2>Educación y Finanzas Personales</h2>
                <p>Optimiza el rendimiento y planificación de tu capital.</p>
            </div>
        </div>
        <!-- Slide 3: Crédito Hipotecario -->
        <div class="slide">
            <img src="https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=1200&h=300&q=72">
            <div class="slide-text">
                <h2>Crédito Hipotecario e Inmobiliario</h2>
                <p>Financiamos la propiedad de tus sueños con agilidad.</p>
            </div>
        </div>
        <!-- Slide 4: Estudios -->
        <div class="slide">
            <img src="https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=1200&h=300&q=72">
            <div class="slide-text">
                <h2>Crédito Educativo y Maestrías</h2>
                <p>Impulsa tu perfil profesional en las mejores universidades.</p>
            </div>
        </div>
        <!-- Slide 5: Seguros -->
        <div class="slide">
            <img src="https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=1200&h=300&q=72">
            <div class="slide-text">
                <h2>Seguros y Respaldo Patrimonial</h2>
                <p>Protección estratégica integral para ti y tu empresa.</p>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card-corporativa">
    <h3 style='margin-top:0;'>✨ Asesoría Patrimonial y Estrategia de Financiamiento</h3>
    <p style='color: #4A5568; font-size: 1.1rem;'>Conectamos tus metas con las mejores opciones de financiamiento, inversión o protección del mercado mediante un análisis técnico riguroso y relaciones directas con proveedores institucionales.</p>
    <strong style='color: #0A2540;'>💼 Nuestra consultoría inicial no genera honorarios para ti</strong> (estos son cubiertos de manera directa por las firmas aliadas del ecosistema).
</div>
""", unsafe_allow_html=True)

st.write("---")

# Estructura en dos columnas: Formulario de Registro y Ejecutivo Virtual
col_izq, col_der = st.columns([1.1, 0.9])

# Lista unificada de productos de Escala
productos = [
    "🎓 Crédito Educativo / Financiamiento para Maestrías",
    "💼 Crédito de Consumo o Equipamiento para Profesionales (Odontólogos, Arquitectos, etc.)",
    "🏡 Crédito Hipotecario / Financiamiento de Vivienda",
    "🚗 Financiamiento Automotriz (Vehículos)",
    "🛡️ Seguros (Vehicular, Médico o Protección de Empresa)"
]

with col_izq:
    # ==========================================
    # FORMULARIO TRADICIONAL DE CAPTURA
    # ==========================================
    st.markdown("### 📋 Pre-Calificación de Perfil")
    st.caption("Introduce tus datos para ingresar el trámite en nuestro sistema en línea:")
    
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
        
        # Cláusula obligatoria de Tratamiento de Datos
        st.markdown("""
        <p style='font-size: 0.82rem; color: #6B7280; text-align: justify; line-height: 1.2;'>
            *Al presionar el botón de envío, usted otorga su <strong>consentimiento expreso e informado</strong> para el tratamiento de sus datos personales, con la única finalidad de evaluar su perfil y estructurar sus requerimientos financieros en los servidores centrales de Escala.*
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
            # Guardado inmediato en base central
            guardar_lead(nombre, cedula, telefono, ciudad, producto_interes)
            st.success("🎉 ¡Trámite ingresado con éxito en la plataforma Escala Finance & Insurance!")
            
            texto_ws = f"Hola Escala Finance & Insurance, he completado y autorizado mi pre-calificación en línea.\n\n" \
                       f"👤 *Consultante:* {nombre}\n" \
                       f"🪪 *Cédula:* {cedula}\n" \
                       f"📱 *Contacto:* {telefono}\n" \
                       f"📍 *Ciudad:* {ciudad}\n" \
                       f"🎯 *Línea:* {producto_interes}\n\n" \
                       f"📜 *Estado:* Trámite ingresado en línea con consentimiento de datos aprobado."
            
            url_whatsapp = f"https://api.whatsapp.com/send?phone={NUMERO_WHATSAPP}&text={urllib.parse.quote(texto_ws)}"
            st.balloons()
            st.link_button("🟢 Validar Identidad vía WhatsApp", url_whatsapp, type="primary")

with col_der:
    # ==========================================
    # NUEVA SECCIÓN: EJECUTIVO VIRTUAL DIRECTO A WHATSAPP
    # ==========================================
    st.markdown("### 🤖 Asesor Ejecutivo Virtual")
    st.caption("Haz clic en nuestro especialista interactivo para iniciar un flujo guiado:")
    
    # Mensaje de consentimiento embebido en la API de WhatsApp
    mensaje_interactivo_bot = (
        "¡Hola Escala Finance & Insurance! Deseo iniciar mi proceso de asesoría personalizada directamente desde WhatsApp.\n\n"
        "Me interesa registrar mis datos para las siguientes soluciones:\n"
        "- Nombre Completo:\n"
        "- Número de Cédula:\n"
        "- Celular / Contacto:\n"
        "- Ciudad de Residencia:\n"
        "- Servicio de Interés (Crédito / Seguros / Inversión):\n\n"
        "📜 [CONSENTIMIENTO DE PRIVACIDAD]: Al enviar este mensaje, otorgo mi consentimiento voluntario para el tratamiento de mis datos personales de acuerdo con las normativas vigentes, con el objetivo exclusivo de procesar este trámite corporativo. Entiendo que una vez completado el flujo, mi trámite quedará ingresado de forma exitosa en el ecosistema."
    )
    
    url_ejecutivo_ws = f"https://api.whatsapp.com/send?phone={NUMERO_WHATSAPP}&text={urllib.parse.quote(mensaje_interactivo_bot)}"
    
    # Tarjeta de Perfil Profesional clickable
    st.markdown(f"""
    <a href="{url_ejecutivo_ws}" target="_blank" style="text-decoration: none; color: inherit;">
        <div class="ejecutivo-box">
            <img class="ejecutivo-avatar" src="https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&w=200&h=200&q=80">
            <h4 style="margin: 0; color: #0A2540; font-size: 1.25rem;">Ing. Jonathan Vaca</h4>
            <p style="margin: 3px 0 10px 0; color: #10B981; font-weight: bold; font-size: 0.9rem;">💼 Consultor Financiero Senior</p>
            <div style="background-color: #F3F4F6; padding: 10px; border-radius: 6px; font-size: 0.88rem; color: #4B5563; text-align: justify;">
                💬 <strong>¿Prefieres atención en WhatsApp?</strong> Toca mi imagen o este cuadro para iniciar el flujo guiado. Podrás ingresar tus datos paso a paso y el trámite quedará registrado en nuestro sistema con tu consentimiento de datos al finalizar.
            </div>
            <br>
            <span style="background-color: #10B981; color: white; padding: 8px 15px; border-radius: 20px; font-weight: bold; font-size: 0.85rem; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                🟢 Chatear en WhatsApp Ahora
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
        <div style="background-color: #FFFFFF; padding: 12px; border-radius: 6px; border-left: 3px solid #D4AF37; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
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
        <div style="background-color: #FFFFFF; padding: 12px; border-radius: 6px; border-left: 3px solid #D4AF37; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            "Excelente servicio para la emisión de la póliza de seguro vehicular de nuestra flota de distribución empresarial."<br>
            <small style='color:#718096;'><strong>- Ing. Javier G. (Gerente General)</strong></small>
        </div>
        """, unsafe_allow_html=True)

st.write("---")

# ==========================================
# 8. PANEL DE CONTROL INTERNO (DASHBOARD RE-LEÍDO)
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
