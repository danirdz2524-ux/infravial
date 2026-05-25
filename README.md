# 🛣️ InfraVial - Sistema de Fichas Técnicas de Alcantarillas

![Versión](https://img.shields.io/badge/versión-2.0-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![Flask](https://img.shields.io/badge/Flask-3.0.2-red)
![Render](https://img.shields.io/badge/Deploy-Render-purple)
![Supabase](https://img.shields.io/badge/Database-Supabase-orange)

---

## 📖 ¿QUÉ ES INFRAVIAL?

**InfraVial** es un sistema completo para la gestión de fichas técnicas de alcantarillas, diseñado especialmente para ingenieros civiles y de infraestructura vial. Permite:

- 📝 **Crear fichas técnicas** con todos los datos de campo
- 🖼️ **Subir fotografías** de cada alcantarilla
- 🔍 **Buscar y filtrar** registros
- ✏️ **Editar y eliminar** fichas existentes
- 📤 **Exportar datos** a CSV (compatible con Excel y QGIS)
- 🗺️ **Generar archivos WKT** para importar directamente en QGIS
- 👥 **Gestionar usuarios** con diferentes roles (Admin/Usuario)
- 📊 **Auditoría completa** de todas las acciones

---

## 🚀 ¿CÓMO USAR INFRAVIAL?

### 🌐 **OPCIÓN 1: USO EN LA NUBE (RECOMENDADA)**

**¡No necesitas instalar nada!** Solo abre tu navegador y ve a:
https://infravial-knex.onrender.com

text

**Credenciales de acceso:**
| Tipo | Usuario | Contraseña |
|------|---------|-------------|
| Administrador | `coil` | `coil123` |

**Ventajas:**
- ✅ No necesitas instalar nada
- ✅ Funciona en cualquier computadora con internet
- ✅ Todos los usuarios ven los mismos datos
- ✅ Acceso desde cualquier lugar

**⚠️ Nota:** Si la página tarda en cargar (30-60 segundos), es normal. La aplicación se "duerme" después de 15 minutos sin uso y necesita despertarse.

---

### 💻 **OPCIÓN 2: INSTALACIÓN LOCAL**

Si prefieres ejecutar la aplicación en tu propia computadora (sin internet), sigue estos pasos:

#### 📋 Requisitos previos

| Requisito | Especificación |
|-----------|----------------|
| Sistema operativo | Windows 10/11, macOS, o Linux |
| Python | Versión 3.11 o superior |
| Espacio en disco | 500 MB |
| Internet | Solo para la instalación inicial |

#### 🔧 Paso 1: Instalar Python

**Windows:**
1. Ve a [python.org](https://www.python.org/downloads/)
2. Descarga Python 3.11 o superior
3. **IMPORTANTE:** Marca "Add Python to PATH"
4. Haz clic en "Install Now"

**Mac:**
brew install python
**Linux (Ubuntu/Debian):**
sudo apt update
sudo apt install python3 python3-pip

📦 Paso 2: Clonar o descargar el proyecto
git clone https://github.com/danirdz2524-ux/infravial.git
cd infravial
O descarga el ZIP desde GitHub.

🔧 Paso 3: Crear entorno virtual e instalar dependencias
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
🚀 Paso 4: Configurar variables de entorno
Crea un archivo .env en la raíz del proyecto con:

env
SECRET_KEY=tu_clave_secreta_aqui
SUPABASE_URL=https://tusupabase.supabase.co
SUPABASE_KEY=tu_api_key_de_supabase
▶️ Paso 5: Ejecutar la aplicación
python app.py
Abre tu navegador y ve a: http://127.0.0.1:5000

📋 FUNCIONALIDADES COMPLETAS
🏠 Dashboard (Pantalla principal)
Para Administradores	Para Usuarios Normales
Total de fichas registradas	Mis fichas registradas
Total de usuarios del sistema	Acceso rápido a nueva ficha
Última actividad de usuarios	
📝 Nueva Ficha Técnica
El formulario incluye todas las secciones necesarias:

Sección	Campos
Ubicación General	Parroquia, Cantón, Provincia, Fecha, Tramo vial
Muros de Ala	Material, Longitud, Espesor, Estado (Bueno/Regular/Malo)
Tubería	Material, Longitud, Diámetro, Estado
Muro Cabezal	Longitud, Espesor, Estado
Pozo de Recolección	Existencia, Ancho, Largo, Estado
Coordenadas UTM	ESTE (X), NORTE (Y)
Observaciones	Texto libre
Fotografía	Subir imagen (arrastrar o seleccionar)
💡 Tip: Presiona la tecla Enter para saltar rápidamente al siguiente campo.

🔍 Ver Registros
Función	Descripción
Búsqueda	Buscar por número de ficha, provincia, cantón o tramo vial
Paginación	10 registros por página
Editar	✏️ Modificar cualquier ficha
Eliminar	🗑️ Borrar ficha (con confirmación)
Ver imagen	🖼️ Abrir la foto en nueva pestaña
📤 Exportar Datos
Opción	Formato	Uso
CSV - Todas las fichas	CSV	Compatible con Excel y QGIS
CSV - Mis fichas	CSV	Solo tus registros
QGIS WKT	CSV con geometría	Importar directamente como puntos en QGIS
Plantilla QGIS	CSV	Ejemplo de estructura
👥 Gestión de Usuarios (Solo Admin)
Función	Descripción
Crear usuario	Nombre, contraseña y rol (Admin/Usuario)
Eliminar usuario	Eliminar usuarios (no puedes eliminarte a ti mismo)
Ver actividad	Bitácora completa de todas las acciones
🗺️ CÓMO IMPORTAR DATOS A QGIS
Exporta los datos desde InfraVial (opción CSV o QGIS WKT)

Abre QGIS en tu computadora

Ve a: Capa → Añadir capa → Añadir capa de texto delimitado

Selecciona el archivo CSV exportado

Configura:

Separador: Coma ,

Codificación: UTF-8

Haz clic en "Añadir"

Para crear puntos en el mapa (opción CSV normal):

Usa COORD_X_ESTE como coordenada X

Usa COORD_Y_NORTE como coordenada Y

CRS: EPSG:32717 (UTM zona 17S para Ecuador)

Si usaste la opción QGIS WKT: La geometría ya viene incluida en la columna WKT.

📁 ESTRUCTURA DEL PROYECTO
text
infravial/
│
├── app.py                 ← Aplicación principal (Flask)
├── config.py              ← Configuración de Supabase
├── requirements.txt       ← Dependencias del proyecto
├── runtime.txt            ← Versión de Python (para Render)
├── README.md              ← Este archivo
├── MANUAL_DE_USUARIO - LOCAL.pdf  ← Manual completo para usuarios
├── MANUAL_DE_USUARIO - GLOBAL.pdf  ← Manual completo para usuarios
│
├── SCRIPTS_BD/
│   └── database.sql       ← Script para crear la base de datos
│
├── static/
│   ├── css/
│   │   └── styles.css     ← Estilos de la aplicación
│   ├── js/
│   │   └── app.js         ← JavaScript (drag & drop, etc.)
│   └── uploads/           ← Carpeta donde se guardan las imágenes
│
└── templates/
    ├── login.html              ← Pantalla de inicio de sesión
    ├── dashboard_admin.html    ← Panel de administrador
    ├── dashboard_user.html     ← Panel de usuario normal
    ├── formulario.html         ← Formulario para crear/editar fichas
    ├── registros.html          ← Lista de registros con paginación
    ├── admin_usuarios.html     ← Gestión de usuarios (solo admin)
    └── admin_actividad.html    ← Bitácora de actividad (solo admin)
    
🛠️ TECNOLOGÍAS UTILIZADAS
Tecnología	¿Para qué sirve?
Python 3.11	Lenguaje principal del backend
Flask	Framework web para crear la aplicación
Supabase	Base de datos en la nube (PostgreSQL)
Render	Plataforma de despliegue (hosting gratuito)
Bootstrap 5	Estilos y diseño responsive
HTML/CSS/JS	Interfaz de usuario

⚠️ SOLUCIÓN DE PROBLEMAS COMUNES
Problema	Solución
La página no carga en Render	Espera 1 minuto y recarga. Es el "cold start".
Error "Internal Server Error"	Revisa que las variables de entorno estén configuradas.
No puedo iniciar sesión	Usa admin / admin123 o contacta al administrador.
La exportación no descarga nada	Asegúrate de tener registros en la tabla.
Las imágenes no se ven	Revisa que la carpeta static/uploads/ exista y tenga permisos.
"No module named 'flask'"	Ejecuta pip install -r requirements.txt

📞 DESPLIEGUE EN LA NUBE (PARA ADMINISTRADORES)
La aplicación está desplegada en Render (plan gratuito):

URL: https://infravial-knex.onrender.com

Características del plan gratuito:

750 horas de actividad al mes (suficiente para 24/7)

La app se "duerme" después de 15 minutos sin uso

Al despertar tarda ~30-60 segundos

Para mantener la app siempre despierta: Usa UptimeRobot (gratis) configurando un monitor que haga ping cada 5 minutos.

👥 CRÉDITOS
Desarrollador: CRUZ RODRIGUEZ DAVID DANIEL - GARCIA ROSALES ALEJANDRO - GRACIA VENTURA ANGEL

Plataforma: Render + Supabase + Flask

Año: 2025

📄 LICENCIA
Proyecto educativo - Uso académico.

🎉 ¡FELICITACIONES!
Ahora sabes usar InfraVial. Guarda información de alcantarillas, exporta a QGIS o Excel, y ayuda a mantener las carreteras en buen estado. 🛣️
