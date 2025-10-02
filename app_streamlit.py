import streamlit as st
import pandas as pd
import csv
import os
from funcionesCSV import csv_a_diccionarios, agregar_registro, borrar_por_indice, modificar_interactivo

# Configuración de la página
st.set_page_config(
    page_title="Gestor de Archivos CSV",
    page_icon="📊",
    layout="wide"
)

# Inicializar estado de sesión
if 'archivo_actual' not in st.session_state:
    st.session_state.archivo_actual = None
if 'datos' not in st.session_state:
    st.session_state.datos = []
if 'campos' not in st.session_state:
    st.session_state.campos = []

def cargar_archivo(uploaded_file=None, nombre_archivo=None):
    """Carga un archivo CSV"""
    try:
        if uploaded_file is not None:
            # Leer el archivo subido
            df = pd.read_csv(uploaded_file)
            nombre = uploaded_file.name
            
            # Guardar como archivo local
            with open(nombre, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            st.session_state.archivo_actual = nombre
            st.session_state.datos = csv_a_diccionarios(nombre)
            st.session_state.campos = list(st.session_state.datos[0].keys()) if st.session_state.datos else []
            
            st.success(f"Archivo '{nombre}' cargado exitosamente!")
            return True
        
        elif nombre_archivo and os.path.exists(nombre_archivo):
            st.session_state.archivo_actual = nombre_archivo
            st.session_state.datos = csv_a_diccionarios(nombre_archivo)
            st.session_state.campos = list(st.session_state.datos[0].keys()) if st.session_state.datos else []
            
            st.success(f"Archivo '{nombre_archivo}' cargado exitosamente!")
            return True
            
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return False

def mostrar_registros():
    """Muestra los registros en una tabla"""
    if not st.session_state.datos:
        st.info("No hay registros para mostrar")
        return
    
    df = pd.DataFrame(st.session_state.datos)
    st.dataframe(df, use_container_width=True)
    
    # Mostrar estadísticas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de registros", len(st.session_state.datos))
    with col2:
        st.metric("Campos", len(st.session_state.campos))
    with col3:
        st.metric("Archivo", st.session_state.archivo_actual)

def crear_nuevo_archivo(nombre_archivo, campos):
    """Crea un nuevo archivo CSV"""
    try:
        if not nombre_archivo.endswith('.csv'):
            nombre_archivo += '.csv'
        
        # Crear archivo con encabezados
        with open(nombre_archivo, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=campos)
            writer.writeheader()
        
        st.session_state.archivo_actual = nombre_archivo
        st.session_state.datos = []
        st.session_state.campos = campos
        
        st.success(f"Archivo '{nombre_archivo}' creado exitosamente!")
        return True
    except Exception as e:
        st.error(f"Error al crear archivo: {e}")
        return False

def agregar_registro_interfaz():
    """Interfaz para agregar nuevo registro"""
    st.subheader("➕ Agregar Nuevo Registro")
    
    if not st.session_state.campos:
        st.warning("No hay campos definidos. Primero carga un archivo existente o crea uno nuevo.")
        return
    
    with st.form("form_agregar_registro"):
        registro = {}
        cols = st.columns(2)
        
        for i, campo in enumerate(st.session_state.campos):
            with cols[i % 2]:
                registro[campo] = st.text_input(f"{campo}", key=f"add_{campo}")
        
        submitted = st.form_submit_button("Agregar Registro")
        
        if submitted:
            if all(registro.values()):
                if agregar_registro(st.session_state.archivo_actual, registro):
                    # Actualizar datos
                    st.session_state.datos = csv_a_diccionarios(st.session_state.archivo_actual)
                    st.rerun()
            else:
                st.error("Todos los campos son obligatorios")

def borrar_registro_interfaz():
    """Interfaz para borrar registros"""
    st.subheader("🗑️ Borrar Registro")
    
    if not st.session_state.datos:
        st.warning("No hay registros para borrar")
        return
    
    # Mostrar registros con selección
    df = pd.DataFrame(st.session_state.datos)
    
    # Agregar columna de selección
    df_seleccion = df.copy()
    df_seleccion['Seleccionar'] = False
    
    # Crear editor de datos para selección
    edited_df = st.data_editor(
        df_seleccion,
        column_config={
            "Seleccionar": st.column_config.CheckboxColumn(
                "Seleccionar",
                help="Selecciona los registros a borrar",
                default=False,
            )
        },
        disabled=df.columns.tolist(),
        use_container_width=True
    )
    
    # Contar registros seleccionados
    registros_seleccionados = edited_df[edited_df['Seleccionar'] == True]
    
    if not registros_seleccionados.empty:
        st.warning(f"Se borrarán {len(registros_seleccionados)} registros")
        
        if st.button("Confirmar Borrado", type="primary"):
            # Obtener índices de los registros seleccionados
            indices = []
            for idx in registros_seleccionados.index:
                indices.append(idx)
            
            # Borrar registros
            borrados = borrar_por_indice(st.session_state.archivo_actual, indices)
            
            if borrados > 0:
                st.success(f"Se borraron {borrados} registros exitosamente!")
                # Actualizar datos
                st.session_state.datos = csv_a_diccionarios(st.session_state.archivo_actual)
                st.rerun()

def modificar_registro_interfaz():
    """Interfaz para modificar registros"""
    st.subheader("✏️ Modificar Registro")
    
    if not st.session_state.datos:
        st.warning("No hay registros para modificar")
        return
    
    # Seleccionar registro
    opciones = [f"Registro {i+1}: {str(registro)[:50]}..." for i, registro in enumerate(st.session_state.datos)]
    registro_seleccionado = st.selectbox("Selecciona el registro a modificar:", opciones)
    
    if registro_seleccionado:
        indice = opciones.index(registro_seleccionado)
        registro_actual = st.session_state.datos[indice]
        
        st.write("**Registro seleccionado:**")
        st.json(registro_actual)
        
        # Formulario para modificación
        with st.form("form_modificar_registro"):
            st.write("**Nuevos valores:**")
            nuevo_registro = {}
            cols = st.columns(2)
            
            for i, campo in enumerate(st.session_state.campos):
                with cols[i % 2]:
                    valor_actual = registro_actual.get(campo, '')
                    nuevo_registro[campo] = st.text_input(f"{campo}", value=valor_actual, key=f"mod_{campo}_{indice}")
            
            submitted = st.form_submit_button("Actualizar Registro")
            
            if submitted:
                # Aplicar cambios
                registros_modificados = st.session_state.datos.copy()
                registros_modificados[indice] = nuevo_registro
                
                # Escribir de vuelta al archivo
                try:
                    with open(st.session_state.archivo_actual, 'w', newline='', encoding='utf-8') as file:
                        writer = csv.DictWriter(file, fieldnames=st.session_state.campos)
                        writer.writeheader()
                        writer.writerows(registros_modificados)
                    
                    st.success("Registro modificado exitosamente!")
                    # Actualizar datos
                    st.session_state.datos = csv_a_diccionarios(st.session_state.archivo_actual)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al modificar registro: {e}")

# Interfaz principal
st.title("📊 Gestor de Archivos CSV")
st.markdown("---")

# Sidebar para carga de archivos
with st.sidebar:
    st.header("📁 Gestión de Archivos")
    
    # Opción 1: Subir archivo existente
    st.subheader("Cargar Archivo Existente")
    uploaded_file = st.file_uploader("Sube un archivo CSV", type=['csv'])
    
    if uploaded_file is not None:
        if st.button("Cargar Archivo Subido"):
            cargar_archivo(uploaded_file=uploaded_file)
    
    # Opción 2: Cargar archivo local
    st.subheader("Cargar Archivo Local")
    archivos_csv = [f for f in os.listdir('.') if f.endswith('.csv')]
    if archivos_csv:
        archivo_seleccionado = st.selectbox("Selecciona un archivo:", archivos_csv)
        if st.button("Cargar Archivo Local"):
            cargar_archivo(nombre_archivo=archivo_seleccionado)
    else:
        st.info("No hay archivos CSV en el directorio actual")
    
    # Opción 3: Crear nuevo archivo
    st.subheader("Crear Nuevo Archivo")
    nuevo_nombre = st.text_input("Nombre del nuevo archivo:")
    campos_nuevo = st.text_input("Campos (separados por coma):", placeholder="ej: id,nombre,edad")
    
    if st.button("Crear Nuevo Archivo"):
        if nuevo_nombre and campos_nuevo:
            campos_lista = [campo.strip() for campo in campos_nuevo.split(',')]
            crear_nuevo_archivo(nuevo_nombre, campos_lista)
        else:
            st.error("Debe ingresar nombre y campos para crear un nuevo archivo")
    
    st.markdown("---")
    # Información del archivo actual
    if st.session_state.archivo_actual:
        st.success(f"**Archivo actual:** {st.session_state.archivo_actual}")
        st.info(f"**Registros:** {len(st.session_state.datos)}")
        st.info(f"**Campos:** {', '.join(st.session_state.campos)}")
    else:
        st.warning("No hay archivo cargado")

# Contenido principal
if st.session_state.archivo_actual:
    # Pestañas para diferentes operaciones
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Ver Registros", 
        "➕ Agregar", 
        "✏️ Modificar", 
        "🗑️ Borrar"
    ])
    
    with tab1:
        mostrar_registros()
    
    with tab2:
        agregar_registro_interfaz()
    
    with tab3:
        modificar_registro_interfaz()
    
    with tab4:
        borrar_registro_interfaz()

else:
    # Pantalla de bienvenida cuando no hay archivo cargado
    st.markdown("""
    ## 👋 ¡Bienvenido al Gestor de Archivos CSV!
    
    ### Para comenzar:
    1. **Carga un archivo CSV existente** usando las opciones en la barra lateral, o
    2. **Crea un nuevo archivo CSV** especificando nombre y campos
    
    ### Funcionalidades disponibles:
    - 📋 **Ver y explorar** registros en formato tabla
    - ➕ **Agregar** nuevos registros
    - ✏️ **Modificar** registros existentes  
    - 🗑️ **Borrar** registros seleccionados
    
    ### Instrucciones:
    - Usa la barra lateral para gestionar archivos
    - Una vez cargado un archivo, podrás acceder a todas las funcionalidades
    """)
    
    # Mostrar archivos disponibles localmente
    archivos_csv = [f for f in os.listdir('.') if f.endswith('.csv')]
    if archivos_csv:
        st.subheader("Archivos CSV disponibles localmente:")
        for archivo in archivos_csv:
            st.write(f"- `{archivo}`")

# Footer
st.markdown("---")
st.caption("Gestor de Archivos CSV - Desarrollado con Streamlit")