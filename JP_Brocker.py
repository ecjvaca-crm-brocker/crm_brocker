import streamlit as st
import urllib.parse

# 1. CONFIGURACIÓN DE TU NÚMERO DE WHATSAPP (¡CAMBIA ESTO!)
# Usa el código de país (593 para Ecuador) seguido de tu número sin el cero. Ej: "593987654321"
NUMERO_WHATSAPP = "593999999999" 

st.set_page_config(
    page_title="Valora | Broker Financiero Independiente", 
    page_icon="💼", 
    layout="centered"
)

# Estilo personalizado con CSS
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #0B3C5D;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 2rem;
        font-weight: bold;
        font-size: 16px;
        width: 100%;
    }
    div.stButton > button:first-child:hover {
        background-color: #328CC1;
        color: white;
    }
    .card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #0B3C5D;
        margin-bottom: 20px;
    }
    .chat-bubble {
        background-color: #e1f5fe;
        padding: 15px;
        border-radius: 15px;
        border-bottom-left-radius: 2px;
        border: 1px solid #b3e5fc;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. CABECERA
st.markdown("<h1 style='text-align: center; color: #0B3C5D;'>🏛️ VALORA</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #328CC1;'>Broker Financiero & Patrimonial Independiente</h3>", unsafe_allow_html=True)

st.write("")

st.markdown("""
<div class="card">
    <h4>✨ Tu aliado financiero estratégico en Imbabura</h4>
    <p>Conectamos tus proyectos con la mejor opción de financiamiento, inversión o protección del mercado.</p>
    <strong>💼 Nuestra asesoría es 100% gratuita para ti.</strong>
</div>
""", unsafe_allow_html=True)

st.write("---")

# 3. FORMULARIO DE PRE-CALIFICACIÓN
st.markdown("### 📋 Formulario de Pre-Calificación Inicial")
st.caption("Completa tus datos básicos para evaluar tu caso:")

with st.container():
    with st.form(key="formulario_leads", clear_on_submit=False):
        
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("👤 Nombre Completo:", placeholder="Ej: Juan Pérez")
        with col2:
            cedula = st.text_input("🪪 Número de Cédula:", max_chars=10, placeholder="Ej: 100xxxxxxx")
            
        col3, col4 = st.columns(2)
        with col3:
            telefono = st.text_input("📱 Teléfono Celular (WhatsApp):", placeholder="Ej: 099xxxxxxx")
        with col4:
            ciudades = ["Ibarra", "Otavalo", "Cotacachi", "Antonio Ante (Atuntaqui)", "Pimampiro", "Urcuquí", "Otra ciudad"]
            ciudad = st.selectbox("📍 Ciudad de Residencia:", opciones=ciudades)
            
        st.write("")
        
        productos = [
            "🎓 Crédito Educativo / Financiamiento para Maestrías",
            "💼 Crédito de Consumo o Equipamiento para Profesionales (Odontólogos, Arquitectos, etc.)",
            "🏡 Crédito Hipotecario / Financiamiento de Vivienda",
            "🚗 Financiamiento Automotriz (Vehículos)",
            "🛡️ Seguros (Vehicular, Médico o Protección de Empresa)"
        ]
        producto_interes = st.selectbox("🎯 ¿Qué solución o producto financiero necesitas?", opciones=productos)
        
        st.write("")
        boton_enviar = st.form_submit_button("Evaluar Mi Caso Gratis 🚀")

# Procesamiento del Formulario
if boton_enviar:
    if not nombre or not cedula or not telefono:
        st.error("⚠️ Por favor, llena todos los campos obligatorios para continuar.")
    elif len(cedula) < 10 or not cedula.isdigit():
        st.error("⚠️ El número de cédula ingresado debe tener 10 dígitos.")
    else:
        st.success(f"🎉 ¡Formulario procesado, {nombre}!")
        
        # CREACIÓN DEL TEXTO AUTOMÁTICO PARA WHATSAPP
        texto_ws = f"Hola VALORA, acabo de pre-calificar en la web.\n\n" \
                   f"👤 *Nombre:* {nombre}\n" \
                   f"🪪 *Cédula:* {cedula}\n" \
                   f"📱 *Teléfono:* {telefono}\n" \
                   f"📍 *Ciudad:* {ciudad}\n" \
                   f"🎯 *Interés:* {producto_interes}"
        
        # Codificar el texto para que internet lo entienda
        texto_codificado = urllib.parse.quote(texto_ws)
        url_whatsapp = f"https://api.whatsapp.com/send?phone={NUMERO_WHATSAPP}&text={texto_codificado}"
        
        # Mostrar instrucciones y el botón de redirección de WhatsApp
        st.balloons()
        st.markdown(f"""
        <div style="background-color: #d4edda; padding: 15px; border-radius: 5px; border: 1px solid #c3e6cb;">
            <strong>👉 PASO FINAL REQUERIDO:</strong> Para enviar tu solicitud directamente al analista de turno, haz clic en el siguiente botón para abrir tu WhatsApp:
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.link_button("🟢 Enviar datos por WhatsApp y Hablar con Asesor", url_whatsapp, type="primary")

st.write("---")

# 4. CHATBOT INTERACTIVO
st.markdown("### 🤖 ¿Tienes dudas? Habla con nuestro Asistente")

with st.expander("💬 Hacer una pregunta rápida en vivo"):
    st.markdown("""
    <div class="chat-bubble">
        <strong>🤖 ValoraBot:</strong> ¡Hola! Soy tu asistente financiero virtual. ¿En qué línea de negocio tienes dudas o te gustaría recibir una guía rápida antes de postular?
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    pregunta_usuario = st.text_input("Escribe tu pregunta aquí:", placeholder="Ej: ¿Qué requisitos piden?")
    
    if pregunta_usuario:
        st.write("")
        duda = pregunta_usuario.lower()
        if "maestria" in duda or "estudio" in duda or "educativo" in duda:
            st.info("🤖 **ValoraBot:** Para créditos de maestrías piden carta de aceptación, buen buró y respaldo de ingresos estables de 1 año.")
        elif "seguro" in duda or "vehicular" in duda or "poliza" in duda:
            st.info("🤖 **ValoraBot:** Manejamos pólizas de seguros vehiculares e inmobiliarios con coberturas completas para Imbabura.")
        elif "requisito" in duda or "papeles" in duda:
            st.info("🤖 **ValoraBot:** Los requisitos básicos son: Cédula, Planilla de servicios y justificativos de ingresos (roles o SRI).")
        else:
            st.info("🤖 **ValoraBot:** Interesante consulta. Para darte la información exacta de montos y tasas según tu perfil, hablemos directamente por WhatsApp.")
            
            # Enlace de WhatsApp también en el Chatbot si no sabe la respuesta
            msg_bot = f"Hola, estuve hablando con el asistente virtual sobre: '{pregunta_usuario}'. Deseo más información."
            url_bot = f"https://api.whatsapp.com/send?phone={NUMERO_WHATSAPP}&text={urllib.parse.quote(msg_bot)}"
            st.link_button("📱 Hablar con un Asesor Humano ahora", url_bot)
