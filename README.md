# 🛣️ InfraVial - Sistema de Fichas Técnicas de Alcantarillas

![Versión](https://img.shields.io/badge/versión-1.0-blue)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![Flask](https://img.shields.io/badge/Flask-3.0.2-red)

---

## 📖 ¿QUÉ ES INFRAVIAL?

**InfraVial** es un programa que ayuda a los ingenieros a guardar información sobre alcantarillas (tuberías grandes que van debajo de las carreteras).

Imagina que tienes una libreta donde apuntas datos de muchas alcantarillas: dónde están, de qué material son, si están rotas o no, y hasta puedes guardar fotos. **InfraVial** es esa libreta pero en la computadora, mucho más ordenada y fácil de usar.

---

## 👤 ¿QUIÉNES USAN ESTE PROGRAMA?

- **Ingenieros de campo**: Van a las alcantarillas, toman fotos y apuntan datos.
- **Administradores**: Pueden ver todo lo que hacen los ingenieros y crear nuevos usuarios.

---

## 🖥️ ¿QUÉ NECESITO PARA USARLO?

| Requisito | ¿Qué es? |
|-----------|----------|
| Una computadora con Windows, Mac o Linux | Cualquier computadora moderna |
| Tener instalado Python | Es el motor que hace funcionar el programa |
| Conexión a Internet | Solo la primera vez y para conectarse a la base de datos |
| Un navegador web (Chrome, Edge, Firefox) | Para abrir el programa |

---

## 📦 PASO 1: INSTALAR PYTHON (SI NO LO TIENES)

### Para Windows:
1. Ve a https://www.python.org/downloads/
2. Haz clic en el botón amarillo **"Download Python"**
3. Abre el archivo que se descargó
4. **IMPORTANTE**: Marca la casilla que dice **"Add Python to PATH"** (abajo de todo)
5. Haz clic en **"Install Now"**
6. Espera a que termine

### Para Mac:
1. Abre la Terminal (búscala con lupa 🔍)
2. Escribe: `brew install python` (si tienes Homebrew)
3. O descarga desde python.org

### Para Linux (Ubuntu):
```bash
sudo apt update
sudo apt install python3 python3-pip
📦 PASO 2: INSTALAR EL PROGRAMA
1. Descomprimir el proyecto
Si te dieron un archivo .zip, haz clic derecho y selecciona "Extraer aquí".

2. Abrir la terminal (ventana negra de comandos)
En Windows:

Presiona Windows + R

Escribe cmd y presiona Enter

Escribe: cd ruta/donde/esta/tu/proyecto (ejemplo: cd C:\Users\TuNombre\Escritorio\infravial)

En Mac:

Abre la aplicación Terminal

Escribe: cd ruta/donde/esta/tu/proyecto

3. Instalar todo lo necesario (SOLO UNA VEZ)
Copia y pega este comando en la terminal:

bash
pip install Flask python-dotenv supabase httpx Werkzeug pandas openpyxl
¿Qué instalamos?

Paquete	¿Para qué sirve?
Flask	Crea el sitio web del programa
supabase	Conecta con la base de datos en la nube
pandas	Ayuda a exportar datos a Excel y CSV
openpyxl	Permite crear archivos de Excel
🚀 PASO 3: EJECUTAR EL PROGRAMA
Cada vez que quieras usar el programa:
Abre la terminal (ventana negra)

Ve a la carpeta del proyecto:

bash
cd ruta/donde/esta/tu/proyecto
Ejecuta el programa:

bash
python app.py
Verás un mensaje como este:

text
* Running on http://127.0.0.1:5000
Abre tu navegador (Chrome, Edge, Firefox)

Escribe esta dirección:

text
http://127.0.0.1:5000
¡El programa está listo! 🎉

🔑 PASO 4: INICIAR SESIÓN
Al abrir el programa, verás una pantalla de login:

Si eres...	Usuario	Contraseña
Administrador	admin	admin123
Ingeniero normal	(te lo dará el administrador)	(te lo dará el administrador)
📋 PASO 5: CÓMO USAR EL PROGRAMA
🏠 PANTALLA PRINCIPAL (DASHBOARD)
Muestra:

Cuántas fichas has guardado

Accesos rápidos

📝 CREAR UNA NUEVA FICHA
Haz clic en "Nueva Ficha" en el menú de la izquierda

Llena todos los campos:

Ubicación: Parroquia, Cantón, Provincia, Fecha, Tramo vial

Muros de ala: Material, longitud, espesor, estado (Bueno/Regular/Malo)

Tubería: Material, longitud, diámetro, estado

Muro cabezal: Longitud, espesor, estado

Pozo de recolección: Si existe, ancho, largo, estado

Coordenadas UTM: Este (X) y Norte (Y)

Observaciones: Escribe cualquier detalle importante

Fotografía: Arrastra una foto o haz clic en "Subir Foto"

TIP: Presiona la tecla Enter para saltar al siguiente campo más rápido

Haz clic en "GUARDAR FICHA" (botón azul)

📋 VER REGISTROS
Haz clic en "Ver Registros" en el menú

Verás una tabla con todas las fichas guardadas

Puedes:

Buscar por provincia, cantón o número de ficha

Editar ✏️: Modificar una ficha

Eliminar 🗑️: Borrar una ficha (con confirmación)

Ver imagen 🖼️: Si tiene foto, se abrirá en otra pestaña

📤 EXPORTAR DATOS (Para QGIS o Excel)
Ve a "Ver Registros"

Haz clic en el botón VERDE "Exportar Datos"

Elige:

CSV - Todas las fichas: Guarda en formato CSV (para QGIS)

CSV - Mis fichas: Solo las que tú creaste

Excel - Todas las fichas: Guarda en Excel (más fácil de leer)

Excel - Mis fichas: Solo las tuyas

QGIS WKT: Para importar directamente como puntos en QGIS

Plantilla QGIS: Un ejemplo para aprender

El archivo se descargará automáticamente a tu carpeta de Descargas

🗺️ CÓMO IMPORTAR A QGIS (Para hacer mapas)
Abre QGIS

Ve a Capa → Añadir capa → Añadir capa de texto delimitado

Selecciona el archivo CSV que exportaste

Configura:

Separador: Coma ,

Codificación: UTF-8

Haz clic en Añadir

Para crear puntos en el mapa:

Usa COORD_X_ESTE como coordenada X

Usa COORD_Y_NORTE como coordenada Y

CRS: EPSG:32717 (UTM zona 17S para Ecuador)

👥 ADMINISTRADOR: GESTIONAR USUARIOS
SOLO el usuario admin puede hacer esto:

Ve a "Usuarios" en el menú

Puedes:

Crear usuario: Escribe nombre y contraseña, elige si es Admin o Usuario

Eliminar usuario: Borrar un usuario (no puedes borrarte a ti mismo)

Ve a "Actividad" para ver:

Quién inició sesión y cuándo

Quién creó, editó o eliminó fichas

Quién exportó datos

❓ BOTÓN DE AYUDA (MANUAL)
En todas las pantallas, en la esquina inferior derecha hay un botón redondo azul con un signo ?. Haz clic allí para abrir este manual dentro del programa.

🛑 CÓMO CERRAR EL PROGRAMA
En la terminal (ventana negra), presiona Ctrl + C

O haz clic en "Cerrar sesión" en el menú y luego cierra la ventana del navegador

⚠️ SOLUCIÓN DE PROBLEMAS COMUNES
Problema	¿Qué hago?
No se abre el programa	Asegúrate de estar en la carpeta correcta con cd
Error "pip no se reconoce"	No instalaste Python correctamente. Revisa el Paso 1
Error "No module named 'flask'"	Ejecuta pip install Flask
Error de conexión a Supabase	Revisa que tengas internet
La imagen no se guarda	La carpeta uploads se crea sola, revisa permisos
El botón Exportar no hace nada	Asegúrate de tener instalado pandas y openpyxl
Los números de ficha no son 1,2,3...	Es normal, los números no se reutilizan aunque borres


📁 ESTRUCTURA DEL PROYECTO (PARA CURIOSOS)
proyecto/
│
├── app.py                 ← El corazón del programa
├── config.py              ← Configuración (no tocar)
├── requirements.txt       ← Lista de cosas que necesita
├── .env                   ← Secretos (no compartir)
│
├── static/
│   ├── css/styles.css     ← Los colores y diseños
│   ├── js/app.js          ↑ Funciones especiales
│   └── uploads/           ← Aquí se guardan las fotos
│
└── templates/
    ├── login.html         ← Pantalla de entrada
    ├── dashboard_admin.html ← Pantalla del jefe
    ├── dashboard_user.html ← Pantalla del ingeniero
    ├── formulario.html    ← Formulario para crear fichas
    ├── editar_ficha.html  ← Formulario para modificar
    ├── registros.html     ← Lista de todas las fichas
    ├── admin_usuarios.html ← Gestionar usuarios
    └── admin_actividad.html ← Ver actividad

    
📞 ¿NECESITAS AYUDA?
Si algo no funciona, revisa:

¿Tienes internet? (el programa necesita conexión a Supabase)

¿Ejecutaste pip install? (solo la primera vez)

¿Estás en la carpeta correcta? (usa dir en Windows o ls en Mac/Linux para ver los archivos)

🎉 ¡FELICITACIONES!
Ahora sabes usar InfraVial. Guarda información de alcantarillas, exporta a Excel o QGIS, y ayuda a mantener las carreteras en buen estado. 🛣️