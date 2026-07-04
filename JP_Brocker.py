import streamlit as st

# 1. Configuración de la página (Pestaña del navegador)
st.set_page_config(page_title="Broker Financiero Independiente", page_icon="💼", layout="centered")

# 2. Diseño de la Cabecera (Tu propuesta de valor)
st.title("💼 Conecta Finanzas")
st.subheader("Asesoría Financiera y Patrimonial Integral en Imbabura")
st.markdown("""
    Te ayudamos a conseguir el **crédito ideal, el financiamiento para tu maestría, vehículo, vivienda o el seguro perfecto** 
    a través de nuestra red de proveedores aliados. 
    \n*Nuestra asesoría es **100% gratuita** para ti (nuestros honorarios los cubren las instituciones aliadas).*
""")

st.write("---")

# 3. El Formulario de Entrada (Filtro Base)
st.markdown("### 📋 Formulario de Pre-Calificación Inicial")
st.write("Completa tus datos básicos para evaluar tu caso con nuestros proveedores:")

with st.form(key="formulario_leads", clear_on_submit=True):
    
    # Campo 1: Nombre
    nombre = st.text_input("Nombre Completo:", placeholder="Ej: Juan Pérez")
    
    # Campo 2: Cédula
    cedula = st.text_input("Número de Cédula (10 dígitos):", max_chars=10, placeholder="Ej: 100xxxxxxx")
    
    # Campo 3: Teléfono/WhatsApp
    telefono = st.text_input("Número de Teléfono Celular:", placeholder="Ej: 099xxxxxxx")
    
    # Campo 4: Ciudad (Menú desplegable)
    ciudades = ["Ibarra", "Otavalo", "Cotacachi", "Antonio Ante (Atuntaqui)", "Pimampiro", "Urcuquí", "Otra ciudad"]
    ciudad = st.selectbox("Ciudad de Residencia:", opciones=ciudades)
    
    # Campo 5: Producto (Menú desplegable)
    productos = [
        "🎓 Crédito Educativo / Financiamiento para Maestrías",
        "💼 Crédito de Consumo o Equipamiento para Profesionales (Odontólogos, Arquitectos, etc.)",
        "🏡 Crédito Hipotecario / Financiamiento de Vivienda",
        "🚗 Financiamiento Automotriz (Vehículos)",
        "🛡️ Seguros (Vehicular, Médico o Protección de Empresa)"
    ]
    producto_interes = st.selectbox("¿Qué producto o servicio necesitas?", opciones=productos)
    
    # Botón de envío
    boton_enviar = st.form_submit_form("Solicitar Asesoría Gratuita 🚀")

# 4. Procesamiento de los datos (Aquí es donde se conectará el CRM más adelante)
if boton_enviar:
    # Validación básica de campos vacíos
    if not nombre or not cedula or not telefono:
        st.error("⚠️ Por favor, llena todos los campos obligatorios (Nombre, Cédula y Teléfono).")
    elif len(cedula) < 10 or not cedula.isdigit():
        st.error("⚠️ El número de cédula debe tener exactamente 10 dígitos numéricos.")
    else:
        # Mensaje de éxito temporal para el cliente
        st.success(f"🎉 ¡Gracias {nombre}! Tus datos han sido recibidos con éxito.")
        st.info(f"Un asesor te contactará a tu celular para evaluar tu solicitud de **{producto_interes}**.")
        
        # AQUÍ EL CÓDIGO GUARDARÁ EN EL CRM EN EL SIGUIENTE PASO:
        # Por ahora, simulamos que los datos ya están listos para ser procesados.
        datos_capturados = {
            "Nombre": nombre,
            "Cédula": cedula,
            "Teléfono": telefono,
            "Ciudad": ciudad,
            "Producto": producto_interes
        }