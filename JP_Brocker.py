import streamlit as st
import urllib.parse

# 1. CONFIGURACIÓN DE TU NÚMERO DE WHATSAPP (¡Pon tu número aquí!)
# Código de país (593 para Ecuador) seguido de tu número sin el cero. Ej: "593987654321"
NUMERO_WHATSAPP = "593998076979" 

st.set_page_config(
    page_title="Valora | Consultor Financiero de Confianza", 
    page_icon="🏛️", 
    layout="wide" # Cambiado a ancho para organizar mejor las noticias y cifras
)

# 2. CONFIGURACIÓN DEL TEMA (COLORES AZUL Y DORADO EXECUTIVO + ESTILOS CSS)
st.markdown("""
    <style>
    /* Fondo general de la app */
    .stApp {
        background-color: #FFFFFF;
    }
    /* Títulos principales en Azul Corporativo */
    h1, h2, h3 {
        color: #0A2540 !important;
        font-family: 'Georgia', serif;
    }
    /* Estilo de Tarjetas con borde Dorado */
    .card-corporativa {
        background-color: #F8F9FA;
        padding: 25px;
        border-radius: 8px;
        border-top: 4px solid #D4AF37; /* Dorado */
        border-left: 1px solid #E2E8F0;
        border-right: 1px solid #E2E8F0;
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    /* Botones principales en Azul con letras doradas/blancas */
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
    /* Burbuja de Chatbot */
    .chat-bubble-vip {
        background-color: #F4F7FA;
        padding: 15px;
        border-radius: 12px;
        border-left: 4px solid #D4AF37;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. CABECERA Y PROPUESTA DE VALOR (Punto 1 y 2)
# ==========================================
st.markdown("<h1 style='text-align: center; font-size: 3rem; margin-bottom: 0;'>🏛️ VALORA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #D4AF37; font-size: 1.5rem; font-weight: bold; margin-top: 0;'>Consultor Financiero de Confianza</p>", unsafe_allow_html=True)

st.write("")

# Banner con Imagen de Confianza Financiera incorporada desde Unsplash (Punto 2)
st.image("https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=1200&q=80", use_container_width=True)

st.markdown("""
<div class="card-corporativa">
    <h3 style='margin-top:0;'>✨ Asesoría Patrimonial y Estrategia de Financiamiento</h3>
    <p style='color: #4A5568; font-size: 1.1rem;'>Conectamos tus metas con las mejores opciones de financiamiento, inversión o protección del mercado mediante un análisis técnico rigurojo y relaciones directas con proveedores aliados institucionales.</p>
    <strong style='color: #0A2540;'>💼 Nuestra consultoría inicial no genera honorarios para ti</strong> (estos son cubiertos de manera directa por las firmas aliadas del ecosistema).
</div>
""", unsafe_allow_html=True)

st.write("---")

# Creamos un diseño de dos columnas principales para la sección media
col_izq, col_der = st.columns([1.2, 0.8])

with col_izq:
    # ==========================================
    # FORMULARIO DE PRE-CALIFICACIÓN
    # ==========================================
    st.markdown("### 📋 Pre-Calificación de Perfil")
    st.caption("Introduce la información requerida para estructurar la solución a tu medida:")
    
    with st.form(key="formulario_leads", clear_on_submit=False):
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
            
        productos = [
            "🎓 Crédito Educativo / Financiamiento para Maestrías",
            "💼 Crédito de Consumo o Equipamiento para Profesionales (Odontólogos, Arquitectos, etc.)",
            "🏡 Crédito Hipotecario / Financiamiento de Vivienda",
            "🚗 Financiamiento Automotriz (Vehículos)",
            "🛡️ Seguros (Vehicular, Médico o Protección de Empresa)"
        ]
        producto_interes = st.selectbox("🎯 Solución Financiera Requerida:", opciones=productos)
        
        st.write("")
        boton_enviar = st.form_submit_button("Iniciar Evaluación de Caso 🚀")

    if boton_enviar:
        if not nombre or not cedula or not telefono:
            st.error("⚠️ Los campos Nombre, Cédula y Teléfono son estrictamente obligatorios.")
        elif len(cedula) < 10 or not cedula.isdigit():
            st.error("⚠️ Documento de identidad no válido (Debe contener 10 números).")
        else:
            st.success(f"🎉 Registro estructurado con éxito, {nombre}.")
            
            texto_ws = f"Hola VALORA, acabo de completar la pre-calificación en el portal.\n\n" \
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
    # CHATBOT CON EL BOTÓN DE WHATSAPP INTEGRADO (Punto 2)
    # ==========================================
    st.markdown("### 🤖 Consultor Virtual")
    
    with st.container(border=True):
        st.markdown("""
        <div class="chat-bubble-vip">
            <strong>🤖 ValoraBot:</strong> Bienvenido. ¿Tiene alguna inquietud técnica sobre los requisitos, tasas o líneas de seguros antes de enviar su formulario?
        </div>
        """, unsafe_allow_html=True)
        
        pregunta = st.text_input("Formule su pregunta financiera:", key="chat_input", placeholder="Ej: ¿Qué requisitos piden?")
        
        if pregunta:
            duda = pregunta.lower()
            if "maestria" in duda or "estudio" in duda or "educativo" in duda:
                st.write("🤖 **ValoraBot:** Las soluciones educativas requieren carta de admisión y un aval de ingresos estables (mínimo 1 año fiscal).")
            elif "seguro" in duda or "vehicular" in duda or "poliza" in duda:
                st.write("🤖 **ValoraBot:** Estructuramos pólizas de seguro con tasas preferenciales corporativas y deducibles optimizados.")
            elif "requisito" in duda or "papeles" in duda:
                st.write("🤖 **ValoraBot:** Documentación base: Cédula, Planilla de Servicios, y estados de cuenta o declaraciones de IVA/IR del SRI.")
            else:
                st.write("🤖 **ValoraBot:** Entendido. Para coordinar una respuesta técnica a esa consulta precisa, le sugiero hablar directamente con un analista:")
            
            # SOLUCIÓN: Botón de WhatsApp que SIEMPRE aparece en el chatbot tras preguntar
            msg_bot = f"Hola, deseo una consulta directa. Estaba usando el asistente virtual y tengo esta duda: '{pregunta}'"
            url_bot = f"https://api.whatsapp.com/send?phone={NUMERO_WHATSAPP}&text={urllib.parse.quote(msg_bot)}"
            st.write("")
            st.link_button("📱 Resolver Duda por WhatsApp Directo", url_bot)

st.write("---")

# ==========================================
# 4. MERCADOS FINANCIEROS (YAHOO FINANCE SIMULADO - Punto 5)
# ==========================================
st.markdown("### 📊 Indicadores Económicos Mundiales y Locales (Yahoo Finance & Bolsas)")
st.caption("Monitoreo macroeconómico referencial:")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric(label="🇺🇸 S&P 500", value="5,137.08", delta="+0.80%")
m2.metric(label="💻 NASDAQ 100", value="18,302.91", delta="+1.14%")
m3.metric(label="🛢️ Crudo Oriente (Ecuador)", value="$78.26", delta="-0.45%")
m4.metric(label="🏛️ BV Quito (Merval Ref)", value="1,045.20", delta="+0.12%")
m5.metric(label="🏦 BV Guayaquil", value="985.40", delta="-0.08%")

st.write("---")

# Diseño de 3 columnas para Noticias, LinkedIn y Educación
col_noticias, col_linkedin, col_youtube = st.columns([1, 1, 1])

# ==========================================
# 5. NOTICIAS DE NEGOCIOS (Punto 6)
# ==========================================
with col_noticias:
    st.markdown("### 📰 Actualidad y Economía")
    st.markdown("""
    *   **Bloomberg:** *Bancos centrales evalúan ajustes de tasas de interés comerciales para el tercer trimestre.*
    *   **CNN Business:** *Mercados globales reaccionan al alza impulsados por el sector de tecnología e IA.*
    *   **Revista Ekos:** *Ecuador registra un incremento del 4.2% en solicitudes de microcréditos productivos de consumo.*
    """)

# ==========================================
# 6. LINKEDIN CORPORATIVO (Punto 3)
# ==========================================
with col_linkedin:
    st.markdown("### 🔗 Publicaciones en LinkedIn")
    st.markdown("""
    Manténgase conectado con mis análisis de mercado, liderazgo y consejos corporativos semanales de primera mano.
    """)
    # Enlace directo a tu perfil o feed de LinkedIn
    st.link_button("🌐 Visitar Mi Perfil Profesional en LinkedIn", "https://www.linkedin.com")

# ==========================================
# 7. EDUCACIÓN FINANCIERA - YOUTUBE (Punto 4)
# ==========================================
with col_youtube:
    st.markdown("### 🎥 Educación Financiera")
    st.caption("Material audiovisual extraído de mi canal de YouTube:")
    # Video corporativo financiero de ejemplo (puedes cambiar esta URL por la de tu video)
    st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

st.write("---")

# ==========================================
# 8. COMENTARIOS Y TESTIMONIOS DE CLIENTES (Punto 7)
# ==========================================
st.markdown("### 💬 Opiniones y Testimonios de Clientes")

t1, t2, t3 = st.columns(3)
with t1:
    st.markdown("""
    <div style="background-color: #F8F9FA; padding: 15px; border-radius: 6px; border-left: 3px solid #D4AF37;">
        "La consultoría para el equipamiento de mi clínica odontológica fue impecable. Conseguí la tasa idónea."<br>
        <small style='color:#718096;'><strong>- Dr. Alejandro R. (Odontólogo)</strong></small>
    </div>
    """, unsafe_allow_html=True)
with t2:
    st.markdown("""
    <div style="background-color: #F8F9FA; padding: 15px; border-radius: 6px; border-left: 3px solid #D4AF37;">
        "Gracias a su asesoría técnica logré financiar mi Maestría en Dirección de Empresas sin comprometer mi liquidez."<br>
        <small style='color:#718096;'><strong>- Mgs. Lorena P. (Arquitecta)</strong></small>
    </div>
    """, unsafe_allow_html=True)
with t3:
    st.markdown("""
    <div style="background-color: #F8F9FA; padding: 15px; border-radius: 6px; border-left: 3px solid #D4AF37;">
        "Excelente servicio para la emisión de la póliza de seguro vehicular de nuestra flota de distribución empresarial."<br>
        <small style='color:#718096;'><strong>- Ing. Javier G. (Gerente General)</strong></small>
    </div>
    """, unsafe_allow_html=True)
