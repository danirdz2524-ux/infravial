from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
from werkzeug.utils import secure_filename
from config import supabase, Config
import os
from datetime import datetime
import csv
from io import StringIO

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
# EXPORTAR A CSV (SIN PANDAS - NATIVO PYTHON)
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
    
    # Crear CSV manualmente (sin pandas)
    output = StringIO()
    writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_ALL)
    
    # Escribir encabezados
    headers = [
        'NRO_FICHA', 'FECHA', 'PROVINCIA', 'CANTON', 'PARROQUIA', 'TRAMO_VIAL',
        'UTM_ESTE', 'UTM_NORTE', 'OBSERVACIONES', 'MURO_ALA_LONGITUD_m',
        'MURO_ALA_ESPESOR_m', 'MURO_ALA_MATERIAL', 'MURO_ALA_ESTADO', 'MURO_ALA_SOLERA',
        'TUBERIA_MATERIAL', 'TUBERIA_LONGITUD_m', 'TUBERIA_DIAMETRO_m', 'TUBERIA_ESTADO',
        'MURO_CABEZAL_LONGITUD_m', 'MURO_CABEZAL_ESPESOR_m', 'MURO_CABEZAL_ESTADO',
        'POZO_EXISTE', 'POZO_ANCHO_m', 'POZO_LARGO_m', 'POZO_ESTADO'
    ]
    writer.writerow(headers)
    
    # Escribir datos
    for r in datos:
        row = [
            r.get('ficha_numero', ''),
            r.get('fecha', ''),
            r.get('provincia', ''),
            r.get('canton', ''),
            r.get('parroquia', ''),
            r.get('tramo_vial', ''),
            r.get('utm_este', ''),
            r.get('utm_norte', ''),
            r.get('observaciones', '').replace('\n', ' ').replace('\r', ' '),
            r.get('muro_ala_longitud', ''),
            r.get('muro_ala_espesor', ''),
            r.get('muro_ala_material', ''),
            r.get('muro_ala_estado', ''),
            'SI' if r.get('muro_ala_solera') else 'NO',
            r.get('tuberia_material', ''),
            r.get('tuberia_longitud', ''),
            r.get('tuberia_diametro', ''),
            r.get('tuberia_estado', ''),
            r.get('muro_cabezal_longitud', ''),
            r.get('muro_cabezal_espesor', ''),
            r.get('muro_cabezal_estado', ''),
            'SI' if r.get('pozo_recoleccion') else 'NO',
            r.get('pozo_ancho', ''),
            r.get('pozo_largo', ''),
            r.get('pozo_estado', ''),
        ]
        writer.writerow(row)
    
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


@app.route('/exportar_qgis_wkt')
def exportar_qgis_wkt():
    """Exporta a CSV con geometría WKT para QGIS (puntos) - SIN PANDAS"""
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
    
    output = StringIO()
    writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_ALL)
    
    # Encabezados
    writer.writerow(['id', 'provincia', 'canton', 'parroquia', 'tramo_vial', 'WKT', 'observaciones'])
    
    # Datos
    for r in datos:
        wkt_geom = ""
        if r.get('utm_este') and r.get('utm_norte'):
            wkt_geom = f"POINT({r.get('utm_este')} {r.get('utm_norte')})"
        
        writer.writerow([
            r.get('ficha_numero', ''),
            r.get('provincia', ''),
            r.get('canton', ''),
            r.get('parroquia', ''),
            r.get('tramo_vial', ''),
            wkt_geom,
            r.get('observaciones', '').replace('\n', ' ')
        ])
    
    csv_data = output.getvalue()
    output.close()
    
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
    response.headers['Content-Disposition'] = 'attachment; filename=INFRAVIAL_QGIS_WKT.csv'
    
    registrar_actividad(session['user_id'], session['username'], "exportar_qgis_wkt", 
                        f"Exportó {len(datos)} registros a QGIS WKT")
    
    return response


@app.route('/exportar_template_qgis')
def exportar_template_qgis():
    """Exporta plantilla de ejemplo para QGIS"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    output = StringIO()
    writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_ALL)
    
    writer.writerow(['NRO_FICHA', 'PROVINCIA', 'CANTON', 'PARROQUIA', 'TRAMO_VIAL', 'UTM_ESTE', 'UTM_NORTE', 'OBSERVACIONES'])
    writer.writerow(['1', 'Santo Domingo de los Tsáchilas', 'Santo Domingo', 'Puerto Limón', 'Vía Quevedo - Puerto Limón', '697499', '9966673', 'Alcantarilla obstruida al 50%'])
    writer.writerow(['2', 'Pichincha', 'Quito', 'Calderón', 'Vía Calacalí', '785234', '10023456', 'Alcantarilla en buen estado'])
    
    csv_data = output.getvalue()
    output.close()
    
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
    response.headers['Content-Disposition'] = 'attachment; filename=plantilla_qgis.csv'
    
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
