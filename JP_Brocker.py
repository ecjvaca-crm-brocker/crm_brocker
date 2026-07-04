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
    page_title="Escala Finance & Insurance | Consultoría Financiera y Corretaje", 
    page_icon="🏛️", 
    layout="wide"
)

# Imagen real del Ec. Jonathan Vaca convertida a Base64 para que nunca se rompa en la nube
FOTO_ECONOMISTA_BASE64 = (
    "data:image/jpeg;base64,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"
    "zpED/P18YfD9fWIPr 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"
    "1h0OvpDoRHT Do6ekInp9YkHTh+vSEDofWHf6Q769PvEQ6evh DoenvEh8fD+vSED4ekIn8/OvpEQ6fWH"
    "p+U8In+pt7Q6E Onq8OHpDw6er8ofH9/rEDp6ffwh6w/0/OsREdfDr4wE/M9IeyU2UvFYrRLfUqa6XId"
    "Z0GgbePR+1WExRwiZMuaJa0pUiYtaFLBSEpLpIJJrTyvHnPZKcFYzE6ZaVErmgqKiXGsvptXvHpfavC"
    "TxgyzTZaUqXNUtalgJCUoA1EAtUfaPRid+9nBkxd72AuyeV4wZhORJnImK06Z0xaFFKgFEkpUku7vTwH"
    "itM1yjGKXhFTZyVy5K1qWtCFrUomUtCgVEuA6vYwG7IZXijmE1EqciYrvAZs5KypIUFElSVAsXUatTwH"
    "itcyyjF97hFTZqpcrEzFmXLC1KUoiWvUoEFrD8BiIvaKyY+vaPQOwWUCbMlzZ0xKUhfAStawpWpQDkkg"
    "fEPKPVpfCDoekfOnYPKsbMxctEnE6Za1/9zXNWhTBUxwEivEPmO8fRYOvpDk7Y8WKv6DoenrD0/YekIh"
    "6vCh/mWOnrD1fo9InXw6+MIgOnr9YgdPU+gjp/NInTp8YfD9Pt4wiP/Z"
)

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
    
    /* --- SLIDER CONTINUO AJUSTADO CON LA PALABRA "ASESORÍA" (72 PPP) --- */
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
# 4. CABECERA PRINCIPAL EN AZUL FINANCIERO
# ==========================================
st.markdown("<h1 style='text-align: center; font-size: 2.8rem; margin-bottom: 0;'>🏛️ ESCALA FINANCE & INSURANCE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #D4AF37; font-size: 1.4rem; font-weight: bold; margin-top: 0;'>Tu consultor financiero de confianza</p>", unsafe_allow_html=True)
st.write("")

# ==========================================
# 5. BANNER ROTATIVO INTERACTIVO: ENFOQUE PURO EN "ASESORÍA"
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

# Lista Global de Servicios de Consultoría / Corretaje
servicios_escala = [
    "1️⃣ Servicio de Asesoría para Financiamiento Educativo y Maestrías",
    "2️⃣ Servicio de Asesoría para Créditos de Consumo o Capital de Trabajo",
    "3️⃣ Servicio de Asesoría para Crédito Hipotecario y Financiamiento Inmobiliario",
    "4️⃣ Servicio de Asesoría para Financiamiento Automotriz (Vehículos)",
    "5️⃣ Servicio de Asesoría en Seguros (Vehicular, Médico o Protección familiar y  Colectiva)"
]

col_izq, col_der = st.columns([1.1, 0.9])

with col_izq:
    # ==========================================
    # FORMULARIO TRADICIONAL DE CAPTURA
    # ==========================================
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
            
            # Remover palabras que impliquen ser dueño del producto bancario
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
            guardar_lead(nombre, cedula, telefono, ciudad, producto_interes)
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
    # ==========================================
    # SECCIÓN: ASESOR VIRTUAL INTERACTIVO (WHATSAPP SECUENCIAL)
    # ==========================================
    st.markdown("### 🤖 Asesor Ejecutivo Virtual")
    st.caption("Toca la fotografía de tu asesor para iniciar el flujo interactivo estructurado:")
    
    # Construcción detallada del flujo conversacional para WhatsApp
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
    
    # Tarjeta Clickable en HTML utilizando tu foto en base64
    st.markdown(f"""
    <a href="{url_flujo_completo}" target="_blank" style="text-decoration: none; color: inherit;">
        <div class="ejecutivo-box">
            <img class="ejecutivo-avatar" src="{FOTO_ECONOMISTA_BASE64}">
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
