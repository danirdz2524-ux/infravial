from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
from werkzeug.utils import secure_filename
from config import supabase, Config
import os
from datetime import datetime
import pandas as pd
from io import StringIO, BytesIO
import csv

app = Flask(__name__)
app.config.from_object(Config)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =========================
# FUNCIONES AUXILIARES
# =========================

def get_user_by_username(username):
    response = supabase.table("users").select("*").eq("username", username).execute()
    return response.data[0] if response.data else None

def registrar_actividad(user_id, username, accion, detalles=""):
    try:
        supabase.table("auditoria").insert({
            "user_id": user_id,
            "username": username,
            "accion": accion,
            "detalles": detalles,
            "ip_address": request.remote_addr
        }).execute()
    except:
        pass

def obtener_fichas_usuario(user_id):
    return supabase.table("alcantarillas").select("*").eq("user_id", user_id).order("ficha_numero", desc=True).execute()

def obtener_todas_fichas():
    return supabase.table("alcantarillas").select("*").order("ficha_numero", desc=True).execute()

def obtener_todos_usuarios():
    return supabase.table("users").select("*").order("id", desc=True).execute()

# =========================
# LOGIN
# =========================

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = get_user_by_username(username)
        
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            registrar_actividad(user['id'], username, "login", "Inicio de sesión exitoso")
            flash(f"Bienvenido {username}", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Usuario o contraseña incorrectos", "danger")
    
    return render_template('login.html')

# =========================
# DASHBOARD
# =========================

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if session['role'] == 'admin':
        fichas = obtener_todas_fichas()
        usuarios = obtener_todos_usuarios()
        total_fichas = len(fichas.data)
        total_usuarios = len(usuarios.data)
        
        auditoria = supabase.table("auditoria").select("*").order("created_at", desc=True).limit(10).execute()
        
        return render_template('dashboard_admin.html',
                             user=session['username'],
                             total_fichas=total_fichas,
                             total_usuarios=total_usuarios,
                             auditoria=auditoria.data)
    else:
        fichas = obtener_fichas_usuario(session['user_id'])
        total = len(fichas.data)
        return render_template('dashboard_user.html',
                             user=session['username'],
                             total=total)

# =========================
# NUEVA FICHA
# =========================

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        imagen = request.files.get('imagen')
        filename = ""
        
        if imagen and imagen.filename:
            filename = secure_filename(imagen.filename)
            imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        muro_ala_solera = True if request.form.get('muro_ala_solera') == 'on' else False
        pozo_recoleccion = True if request.form.get('pozo_recoleccion') == 'on' else False
        
        data = {
            "user_id": session['user_id'],
            "fecha": request.form.get('fecha'),
            "provincia": request.form.get('provincia'),
            "canton": request.form.get('canton'),
            "parroquia": request.form.get('parroquia'),
            "tramo_vial": request.form.get('tramo_vial'),
            
            "muro_ala_longitud": request.form.get('muro_ala_longitud'),
            "muro_ala_espesor": request.form.get('muro_ala_espesor'),
            "muro_ala_solera": muro_ala_solera,
            "muro_ala_material": request.form.get('muro_ala_material'),
            "muro_ala_estado": request.form.get('muro_ala_estado'),
            
            "tuberia_material": request.form.get('tuberia_material'),
            "tuberia_longitud": request.form.get('tuberia_longitud'),
            "tuberia_diametro": request.form.get('tuberia_diametro'),
            "tuberia_estado": request.form.get('tuberia_estado'),
            
            "muro_cabezal_longitud": request.form.get('muro_cabezal_longitud'),
            "muro_cabezal_espesor": request.form.get('muro_cabezal_espesor'),
            "muro_cabezal_estado": request.form.get('muro_cabezal_estado'),
            
            "pozo_recoleccion": pozo_recoleccion,
            "pozo_ancho": request.form.get('pozo_ancho'),
            "pozo_largo": request.form.get('pozo_largo'),
            "pozo_estado": request.form.get('pozo_estado'),
            
            "utm_este": request.form.get('utm_este'),
            "utm_norte": request.form.get('utm_norte'),
            "observaciones": request.form.get('observaciones'),
            "imagen": filename,
            "updated_at": datetime.now().isoformat()
        }
        
        supabase.table("alcantarillas").insert(data).execute()
        
        registrar_actividad(session['user_id'], session['username'], "crear_ficha", f"Creó ficha técnica")
        flash("Registro guardado correctamente", "success")
        return redirect(url_for('registros'))
    
    return render_template('formulario.html')

# =========================
# EDITAR FICHA
# =========================

@app.route('/editar_ficha/<int:ficha_id>', methods=['GET', 'POST'])
def editar_ficha(ficha_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    ficha = supabase.table("alcantarillas").select("*").eq("id", ficha_id).execute()
    
    if not ficha.data:
        flash("Ficha no encontrada", "danger")
        return redirect(url_for('registros'))
    
    ficha = ficha.data[0]
    
    if session['role'] != 'admin' and ficha['user_id'] != session['user_id']:
        flash("No tienes permiso para editar esta ficha", "danger")
        return redirect(url_for('registros'))
    
    if request.method == 'POST':
        imagen = request.files.get('imagen')
        filename = ficha['imagen']
        
        if imagen and imagen.filename:
            filename = secure_filename(imagen.filename)
            imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        muro_ala_solera = True if request.form.get('muro_ala_solera') == 'on' else False
        pozo_recoleccion = True if request.form.get('pozo_recoleccion') == 'on' else False
        
        data = {
            "fecha": request.form.get('fecha'),
            "provincia": request.form.get('provincia'),
            "canton": request.form.get('canton'),
            "parroquia": request.form.get('parroquia'),
            "tramo_vial": request.form.get('tramo_vial'),
            "muro_ala_longitud": request.form.get('muro_ala_longitud'),
            "muro_ala_espesor": request.form.get('muro_ala_espesor'),
            "muro_ala_solera": muro_ala_solera,
            "muro_ala_material": request.form.get('muro_ala_material'),
            "muro_ala_estado": request.form.get('muro_ala_estado'),
            "tuberia_material": request.form.get('tuberia_material'),
            "tuberia_longitud": request.form.get('tuberia_longitud'),
            "tuberia_diametro": request.form.get('tuberia_diametro'),
            "tuberia_estado": request.form.get('tuberia_estado'),
            "muro_cabezal_longitud": request.form.get('muro_cabezal_longitud'),
            "muro_cabezal_espesor": request.form.get('muro_cabezal_espesor'),
            "muro_cabezal_estado": request.form.get('muro_cabezal_estado'),
            "pozo_recoleccion": pozo_recoleccion,
            "pozo_ancho": request.form.get('pozo_ancho'),
            "pozo_largo": request.form.get('pozo_largo'),
            "pozo_estado": request.form.get('pozo_estado'),
            "utm_este": request.form.get('utm_este'),
            "utm_norte": request.form.get('utm_norte'),
            "observaciones": request.form.get('observaciones'),
            "imagen": filename,
            "updated_at": datetime.now().isoformat()
        }
        
        supabase.table("alcantarillas").update(data).eq("id", ficha_id).execute()
        registrar_actividad(session['user_id'], session['username'], "editar_ficha", f"Editó ficha ID: {ficha_id}")
        flash("Ficha actualizada correctamente", "success")
        return redirect(url_for('registros'))
    
    return render_template('editar_ficha.html', ficha=ficha)

# =========================
# ELIMINAR FICHA
# =========================

@app.route('/eliminar_ficha/<int:ficha_id>')
def eliminar_ficha(ficha_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    ficha = supabase.table("alcantarillas").select("*").eq("id", ficha_id).execute()
    
    if ficha.data:
        if session['role'] != 'admin' and ficha.data[0]['user_id'] != session['user_id']:
            flash("No tienes permiso para eliminar esta ficha", "danger")
            return redirect(url_for('registros'))
        
        if ficha.data[0].get('imagen'):
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], ficha.data[0]['imagen'])
            if os.path.exists(img_path):
                os.remove(img_path)
        
        supabase.table("alcantarillas").delete().eq("id", ficha_id).execute()
        registrar_actividad(session['user_id'], session['username'], "eliminar_ficha", f"Eliminó ficha ID: {ficha_id}")
        flash("Ficha eliminada correctamente", "success")
    
    return redirect(url_for('registros'))

# =========================
# REGISTROS (CON PAGINACIÓN)
# =========================

@app.route('/registros')
def registros():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    busqueda = request.args.get('busqueda', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    if session['role'] == 'admin':
        if busqueda:
            registros = supabase.table("alcantarillas").select("*").or_(
                f"ficha_numero::text.ilike.%{busqueda}%,provincia.ilike.%{busqueda}%,canton.ilike.%{busqueda}%,tramo_vial.ilike.%{busqueda}%"
            ).order("ficha_numero", desc=True).execute()
        else:
            registros = obtener_todas_fichas()
    else:
        if busqueda:
            registros = supabase.table("alcantarillas").select("*").eq("user_id", session['user_id']).or_(
                f"ficha_numero::text.ilike.%{busqueda}%,provincia.ilike.%{busqueda}%,canton.ilike.%{busqueda}%,tramo_vial.ilike.%{busqueda}%"
            ).order("ficha_numero", desc=True).execute()
        else:
            registros = obtener_fichas_usuario(session['user_id'])
    
    datos = registros.data
    total = len(datos)
    total_pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    datos_paginados = datos[start:end]
    
    return render_template('registros.html', 
                         registros=datos_paginados, 
                         busqueda=busqueda, 
                         role=session['role'],
                         page=page,
                         total_pages=total_pages,
                         total=total)

# =========================
# EXPORTAR A CSV
# =========================

@app.route('/exportar')
def exportar_menu():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    flash("📥 Utiliza el botón 'Exportar' en la página de Registros para elegir el tipo de exportación", "info")
    return redirect(url_for('registros'))

@app.route('/exportar_csv')
def exportar_csv():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    tipo = request.args.get('tipo', 'todas')
    busqueda = request.args.get('busqueda', '')
    
    if tipo == 'mis_fichas':
        registros = obtener_fichas_usuario(session['user_id'])
    elif tipo == 'filtradas' and busqueda:
        if session['role'] == 'admin':
            registros = supabase.table("alcantarillas").select("*").or_(
                f"ficha_numero::text.ilike.%{busqueda}%,provincia.ilike.%{busqueda}%,canton.ilike.%{busqueda}%,tramo_vial.ilike.%{busqueda}%"
            ).order("ficha_numero", desc=True).execute()
        else:
            registros = supabase.table("alcantarillas").select("*").eq("user_id", session['user_id']).or_(
                f"ficha_numero::text.ilike.%{busqueda}%,provincia.ilike.%{busqueda}%,canton.ilike.%{busqueda}%,tramo_vial.ilike.%{busqueda}%"
            ).order("ficha_numero", desc=True).execute()
    else:
        if session['role'] == 'admin':
            registros = obtener_todas_fichas()
        else:
            registros = obtener_fichas_usuario(session['user_id'])
    
    datos = registros.data
    
    if not datos:
        flash("No hay datos para exportar", "warning")
        return redirect(url_for('registros'))
    
    export_data = []
    for r in datos:
        export_data.append({
            'ID_FICHA': r.get('ficha_numero', ''),
            'FECHA': r.get('fecha', ''),
            'PROVINCIA': r.get('provincia', ''),
            'CANTON': r.get('canton', ''),
            'PARROQUIA': r.get('parroquia', ''),
            'TRAMO_VIAL': r.get('tramo_vial', ''),
            'COORD_X_ESTE': r.get('utm_este', ''),
            'COORD_Y_NORTE': r.get('utm_norte', ''),
            'OBSERVACIONES': r.get('observaciones', '').replace('\n', ' ').replace('\r', ' '),
            'M_ALA_LONGITUD_m': r.get('muro_ala_longitud', ''),
            'M_ALA_ESPESOR_m': r.get('muro_ala_espesor', ''),
            'M_ALA_MATERIAL': r.get('muro_ala_material', ''),
            'M_ALA_ESTADO': r.get('muro_ala_estado', ''),
            'M_ALA_SOLERA': 'SI' if r.get('muro_ala_solera') else 'NO',
            'TUB_MATERIAL': r.get('tuberia_material', ''),
            'TUB_LONGITUD_m': r.get('tuberia_longitud', ''),
            'TUB_DIAMETRO_m': r.get('tuberia_diametro', ''),
            'TUB_ESTADO': r.get('tuberia_estado', ''),
            'M_CABEZAL_LONGITUD_m': r.get('muro_cabezal_longitud', ''),
            'M_CABEZAL_ESPESOR_m': r.get('muro_cabezal_espesor', ''),
            'M_CABEZAL_ESTADO': r.get('muro_cabezal_estado', ''),
            'POZO_EXISTE': 'SI' if r.get('pozo_recoleccion') else 'NO',
            'POZO_ANCHO_m': r.get('pozo_ancho', ''),
            'POZO_LARGO_m': r.get('pozo_largo', ''),
            'POZO_ESTADO': r.get('pozo_estado', ''),
            'FECHA_REGISTRO': r.get('created_at', '')[:19] if r.get('created_at') else '',
        })
    
    df = pd.DataFrame(export_data)
    output = StringIO()
    
    output.write("# ================================================================\n")
    output.write("# ARCHIVO EXPORTADO DEL SISTEMA INFRAVIAL\n")
    output.write("# FECHA: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")
    output.write("# TOTAL REGISTROS: " + str(len(datos)) + "\n")
    output.write("# ================================================================\n")
    output.write("# INSTRUCCIONES PARA QGIS:\n")
    output.write("# 1. Capa -> Añadir capa -> Añadir capa de texto delimitado\n")
    output.write("# 2. Seleccionar este archivo\n")
    output.write("# 3. Separador: Coma (,)\n")
    output.write("# 4. Codificacion: UTF-8\n")
    output.write("# 5. CRS: EPSG:32717 (UTM zona 17S para Ecuador)\n")
    output.write("# ================================================================\n")
    output.write("\n")
    
    df.to_csv(output, index=False, encoding='utf-8-sig', sep=',', quoting=csv.QUOTE_ALL)
    csv_data = output.getvalue()
    output.close()
    
    filename = f"INFRAVIAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    
    registrar_actividad(session['user_id'], session['username'], "exportar_csv", 
                        f"Exportó {len(datos)} registros a CSV")
    
    flash(f"✅ Se exportaron {len(datos)} registros a CSV", "success")
    return response

# =========================
# EXPORTAR A EXCEL
# =========================

@app.route('/exportar_excel')
def exportar_excel():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    tipo = request.args.get('tipo', 'todas')
    busqueda = request.args.get('busqueda', '')
    
    if tipo == 'mis_fichas':
        registros = obtener_fichas_usuario(session['user_id'])
    elif tipo == 'filtradas' and busqueda:
        if session['role'] == 'admin':
            registros = supabase.table("alcantarillas").select("*").or_(
                f"ficha_numero::text.ilike.%{busqueda}%,provincia.ilike.%{busqueda}%,canton.ilike.%{busqueda}%,tramo_vial.ilike.%{busqueda}%"
            ).order("ficha_numero", desc=True).execute()
        else:
            registros = supabase.table("alcantarillas").select("*").eq("user_id", session['user_id']).or_(
                f"ficha_numero::text.ilike.%{busqueda}%,provincia.ilike.%{busqueda}%,canton.ilike.%{busqueda}%,tramo_vial.ilike.%{busqueda}%"
            ).order("ficha_numero", desc=True).execute()
    else:
        if session['role'] == 'admin':
            registros = obtener_todas_fichas()
        else:
            registros = obtener_fichas_usuario(session['user_id'])
    
    datos = registros.data
    
    if not datos:
        flash("No hay datos para exportar", "warning")
        return redirect(url_for('registros'))
    
    export_data = []
    for r in datos:
        export_data.append({
            'ID Ficha': r.get('ficha_numero', ''),
            'Fecha': r.get('fecha', ''),
            'Provincia': r.get('provincia', ''),
            'Cantón': r.get('canton', ''),
            'Parroquia': r.get('parroquia', ''),
            'Tramo Vial': r.get('tramo_vial', ''),
            'UTM Este (X)': r.get('utm_este', ''),
            'UTM Norte (Y)': r.get('utm_norte', ''),
            'Observaciones': r.get('observaciones', '').replace('\n', ' '),
            'Muro Ala Longitud (m)': r.get('muro_ala_longitud', ''),
            'Muro Ala Espesor (m)': r.get('muro_ala_espesor', ''),
            'Muro Ala Material': r.get('muro_ala_material', ''),
            'Muro Ala Estado': r.get('muro_ala_estado', ''),
            'Muro Ala Solera': 'Sí' if r.get('muro_ala_solera') else 'No',
            'Tubería Material': r.get('tuberia_material', ''),
            'Tubería Longitud (m)': r.get('tuberia_longitud', ''),
            'Tubería Diámetro (m)': r.get('tuberia_diametro', ''),
            'Tubería Estado': r.get('tuberia_estado', ''),
            'Muro Cabezal Longitud (m)': r.get('muro_cabezal_longitud', ''),
            'Muro Cabezal Espesor (m)': r.get('muro_cabezal_espesor', ''),
            'Muro Cabezal Estado': r.get('muro_cabezal_estado', ''),
            'Pozo Recolección': 'Sí' if r.get('pozo_recoleccion') else 'No',
            'Pozo Ancho (m)': r.get('pozo_ancho', ''),
            'Pozo Largo (m)': r.get('pozo_largo', ''),
            'Pozo Estado': r.get('pozo_estado', ''),
        })
    
    df = pd.DataFrame(export_data)
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Alcantarillas', index=False)
    
    output.seek(0)
    
    filename = f"INFRAVIAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    
    registrar_actividad(session['user_id'], session['username'], "exportar_excel", 
                        f"Exportó {len(datos)} registros a Excel")
    
    flash(f"✅ Se exportaron {len(datos)} registros a Excel", "success")
    return response

# =========================
# EXPORTAR A QGIS WKT (GEOMETRÍA)
# =========================

@app.route('/exportar_qgis_wkt')
def exportar_qgis_wkt():
    """Exporta a CSV con geometría WKT para QGIS (puntos)"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    tipo = request.args.get('tipo', 'todas')
    
    if tipo == 'mis_fichas':
        registros = obtener_fichas_usuario(session['user_id'])
    else:
        if session['role'] == 'admin':
            registros = obtener_todas_fichas()
        else:
            registros = obtener_fichas_usuario(session['user_id'])
    
    datos = registros.data
    
    export_data = []
    for r in datos:
        wkt_geom = ""
        if r.get('utm_este') and r.get('utm_norte'):
            wkt_geom = f"POINT({r.get('utm_este')} {r.get('utm_norte')})"
        
        export_data.append({
            'id': r.get('ficha_numero', ''),
            'provincia': r.get('provincia', ''),
            'canton': r.get('canton', ''),
            'parroquia': r.get('parroquia', ''),
            'tramo_vial': r.get('tramo_vial', ''),
            'WKT': wkt_geom,
            'observaciones': r.get('observaciones', '').replace('\n', ' ')
        })
    
    df = pd.DataFrame(export_data)
    output = StringIO()
    
    output.write("# ARCHIVO CON GEOMETRÍA WKT PARA QGIS\n")
    output.write("# La columna WKT contiene los puntos geográficos\n")
    output.write("# CRS recomendado: EPSG:32717 (UTM zona 17S)\n")
    output.write("\n")
    
    df.to_csv(output, index=False, encoding='utf-8-sig', sep=',', quoting=csv.QUOTE_ALL)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
    response.headers['Content-Disposition'] = 'attachment; filename=INFRAVIAL_QGIS_WKT.csv'
    
    registrar_actividad(session['user_id'], session['username'], "exportar_qgis_wkt", 
                        f"Exportó {len(datos)} registros a QGIS WKT")
    
    return response

# =========================
# PLANTILLA QGIS
# =========================

@app.route('/exportar_template_qgis')
def exportar_template_qgis():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    template_data = [
        {
            'ID_FICHA': '1',
            'FECHA': '2024-01-15',
            'PROVINCIA': 'Santo Domingo de los Tsáchilas',
            'CANTON': 'Santo Domingo',
            'PARROQUIA': 'Puerto Limón',
            'TRAMO_VIAL': 'Vía Quevedo - Puerto Limón',
            'COORD_X_ESTE': '697499',
            'COORD_Y_NORTE': '9966673',
            'OBSERVACIONES': 'Alcantarilla obstruida al 50%',
            'M_ALA_LONGITUD_m': '5.50',
            'M_ALA_ESPESOR_m': '0.30',
            'M_ALA_MATERIAL': 'H.Simple',
            'M_ALA_ESTADO': 'Regular',
            'TUB_MATERIAL': 'M.Corrugado',
            'TUB_LONGITUD_m': '11.00',
            'TUB_DIAMETRO_m': '1.40',
            'TUB_ESTADO': 'Regular',
            'POZO_EXISTE': 'SI',
            'POZO_ANCHO_m': '1.20',
            'POZO_LARGO_m': '1.60',
            'POZO_ESTADO': 'Bueno'
        }
    ]
    
    df = pd.DataFrame(template_data)
    output = StringIO()
    
    output.write("# PLANTILLA PARA QGIS - INFRAVIAL\n")
    output.write("# Separador: coma (,), Codificacion: UTF-8\n")
    output.write("# CRS recomendado: EPSG:32717 (UTM zona 17S)\n")
    output.write("\n")
    
    df.to_csv(output, index=False, encoding='utf-8-sig', sep=',', quoting=csv.QUOTE_ALL)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
    response.headers['Content-Disposition'] = 'attachment; filename=INFRAVIAL_PLANTILLA_QGIS.csv'
    
    return response

# =========================
# ADMIN - USUARIOS
# =========================

@app.route('/admin/usuarios')
def admin_usuarios():
    if 'user_id' not in session or session['role'] != 'admin':
        flash("Acceso denegado", "danger")
        return redirect(url_for('dashboard'))
    
    usuarios = obtener_todos_usuarios()
    return render_template('admin_usuarios.html', usuarios=usuarios.data)

@app.route('/admin/crear_usuario', methods=['POST'])
def admin_crear_usuario():
    if 'user_id' not in session or session['role'] != 'admin':
        return jsonify({"error": "No autorizado"}), 403
    
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role', 'user')
    
    existe = supabase.table("users").select("*").eq("username", username).execute()
    if existe.data:
        flash("El usuario ya existe", "danger")
        return redirect(url_for('admin_usuarios'))
    
    supabase.table("users").insert({
        "username": username,
        "password": password,
        "role": role
    }).execute()
    
    registrar_actividad(session['user_id'], session['username'], "crear_usuario", f"Creó usuario: {username}")
    flash("Usuario creado correctamente", "success")
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/eliminar_usuario/<int:user_id>')
def admin_eliminar_usuario(user_id):
    if 'user_id' not in session or session['role'] != 'admin':
        flash("Acceso denegado", "danger")
        return redirect(url_for('dashboard'))
    
    if user_id == session['user_id']:
        flash("No puedes eliminarte a ti mismo", "danger")
        return redirect(url_for('admin_usuarios'))
    
    usuario = supabase.table("users").select("*").eq("id", user_id).execute()
    if usuario.data:
        username = usuario.data[0]['username']
        supabase.table("users").delete().eq("id", user_id).execute()
        registrar_actividad(session['user_id'], session['username'], "eliminar_usuario", f"Eliminó usuario: {username}")
        flash("Usuario eliminado correctamente", "success")
    
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/actividad')
def admin_actividad():
    if 'user_id' not in session or session['role'] != 'admin':
        flash("Acceso denegado", "danger")
        return redirect(url_for('dashboard'))
    
    actividad = supabase.table("auditoria").select("*").order("created_at", desc=True).execute()
    return render_template('admin_actividad.html', actividad=actividad.data)

# =========================
# LOGOUT
# =========================

@app.route('/logout')
def logout():
    if 'user_id' in session:
        registrar_actividad(session['user_id'], session['username'], "logout", "Cierre de sesión")
    session.clear()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)