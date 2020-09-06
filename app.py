from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import bcrypt, io, os

app = Flask(__name__)
app.secret_key = "appLogin"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/task1.db'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
semilla = bcrypt.gensalt()
db = SQLAlchemy(app)
db1 = SQLAlchemy(app)
db2 = SQLAlchemy(app)

class personajes(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    nombre = db.Column(db.String(20))
    informacion = db.Column(db.String(200))
    hecho = db.Column(db.String(100))
    pro = db.Column(db.Integer)
    fuente = db.Column(db.String(50))
    foto = db.Column("foto")
    partido = db.Column(db.String(50))
    reportado = db.Column(db.Boolean, default = False)

class usuarios(db1.Model):
    __tablename__ = 'login'
    id = db1.Column(db.Integer,primary_key=True)
    nombre = db1.Column(db.String(20))
    apellido = db1.Column(db.String(20))
    correo = db1.Column(db.String(50))
    contraseña = db1.Column(db.String(50))
    telefono = db1.Column(db.Integer)
    foto = db1.Column("foto")
    rol = db1.Column(db.String(20))

class publicaciones(db2.Model):
    __tablename__ = 'publicaciones'
    id = db2.Column(db.Integer,primary_key=True)
    username = db2.Column(db.String(20))
    personaje = db2.Column(db.String(20))
    titulo = db2.Column(db.String(50))
    fecha = db2.Column(db.String(20))
    contenido = db2.Column(db.String(450))
    fuente = db2.Column(db.String(200))
    reportado = db2.Column(db.Boolean, default = False)
    foto = db2.Column("foto")

@app.route('/index')
@app.route('/')  
@app.route('/<int:page>')
def index(page=1):
    tasks1 = personajes.query.all() 
    #tasks = publicaciones.query.filter(publicaciones.id != 0).order_by(desc(publicaciones.id)).all()
    tasks = publicaciones.query.all()
    #crea las fotos desde la db2 s
    for task in tasks:
        foto = task.foto
        if(os.path.isfile('static/img/foto_{}.jpg'.format(task.personaje)) == False):
            with open('static/img/foto_{}.jpg'.format(task.personaje), 'wb') as f:
                f.write(foto)
    tasks = publicaciones.query.order_by(publicaciones.id.desc()).paginate(page,2,False)
    next_url = url_for('index', page = tasks.next_num) \
        if tasks.has_next else None
    prev_url = url_for('index', page = tasks.prev_num) \
        if tasks.has_prev else None
    return render_template('index.html', tasks = tasks.items, tasks1 = tasks1, next_url = next_url,prev_url = prev_url, paginacion = tasks)

@app.route('/search', methods = ['POST','GET'])
def search():
    opcion = request.form['opc']
    textoBuscar = "%"+request.form['buscar']+"%"
    post = personajes.query.filter(personajes.nombre.like(textoBuscar))
    publis = publicaciones.query.filter(publicaciones.personaje.like(textoBuscar))
    return render_template('search.html', posts = post, publis = publis, opcion = opcion)

@app.route('/report', methods = ['POST','GET'])
def report():
    action = request.args.get('action') # report/ignore/delete
    postType = request.args.get('postType')
    postId = request.args.get('postId')
    if (postType == 'post'):
        rPost = publicaciones.query.filter_by(id = postId).first()
        if (action == 'report'):
            rPost.reportado = True
        elif (action == 'ignore'):
            rPost.reportado = False
        elif (action == 'delete'):
            db2.session.delete(rPost)
        db2.session.commit()
    elif (postType == 'character'):
        rCharacter = personajes.query.filter_by(id = postId).first()
        if (action == 'report'):
            rCharacter.reportado = True
        elif (action == 'ignore'):
            rCharacter.reportado = False
        elif (action == 'delete'):
            charPosts = publicaciones.query.filter(publicaciones.personaje == rCharacter.nombre)
            db.session.delete(rCharacter)
            for charPost in charPosts:
                db2.session.delete(charPost)
            db2.session.commit()
        db.session.commit()
    if (action == 'report'):
        return '''
        <script> window.alert("Publicación reportada"); </script>
        <script> window.history.back(); </script>'''
    else:
        return '''<script> window.location=document.referrer; </script>'''

@app.route('/postspersonaje', methods = ['POST','GET'])
def characterPosts():
    name = request.args.get('name')
    postId = request.args.get('id')
    personaje = personajes.query.filter_by(id = postId).first()
    post = publicaciones.query.filter_by(personaje = name)
    return render_template('personaj.html', posts = post, personaje = personaje)

@app.route('/login',methods = ['POST','GET'])
def login():
    if(request.method == "GET"):
        if 'name' in session:
            return redirect(url_for('editor'))
    else:
        #obtiene datos 
        correo = request.form['username']
        password = request.form['password']
        password_encode = password.encode("utf-8")
        usuario = usuarios.query.filter_by(correo = correo).first()
        if(usuario != None):
            #obtiene el password encriptado encode
            password_encriptado_encode = usuario.contraseña
            #verifica el password
            if(bcrypt.checkpw(password_encode,password_encriptado_encode)):
                #registra la sesion
                session['name'] = usuario.nombre      
                session['rol'] = usuario.rol
                session['logged_in'] = True
                return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/editor-usuario', methods = ['POST','GET'])
def editor():
    if(request.method == "GET"):
        if 'name' in session:
            tasks = usuarios.query.filter_by(nombre = session['name']).first()
            return render_template('editor-usuario.html', tasks = tasks)
        else:
            return redirect(url_for('ingresar'))
    else:
        if 'name' in session:
            tasks = usuarios.query.filter_by(nombre = session['name']).first()
            if(request.form['nombre']!=''):
                nombre =request.form['nombre']
                tasks.nombre = nombre
                if(tasks.foto != None):
                    f = tasks.foto
                    with open('static/img/foto_{}.jpg'.format(tasks.nombre), 'wb') as archivo:
                        archivo.write(f)
                        tasks.foto = f 
                session['name']=nombre
            if(request.form['apellido']!=''):
                apellido =request.form['apellido']
                tasks.apellido = apellido
            if(request.form['telf']!=''):
                telefono =request.form['telf']
                tasks.telefono = telefono
            
            arch = request.files['imagen-usuario']
            #si el usuar
            if(arch.filename!=""):
                print(request.files['imagen-usuario'])
                foto = request.files['imagen-usuario']
                f = foto.read()
                with open('static/img/foto_{}.jpg'.format(tasks.nombre), 'wb') as archivo:
                    archivo.write(f)
                    tasks.foto = f 
            db1.session.commit()
            return render_template('editor-usuario.html', tasks = tasks)

# funcion que registra los datos en la bd uusuarios
@app.route('/sign-up', methods = ['POST','GET'])
def registro():
    if(request.method == "GET"):
        if 'name' in session:
            return redirect(url_for('editor'))
        return render_template('sign-up.html')

    nombre = request.form['name']
    apellido = request.form['apellido']
    correo = request.form['email']
    contraseña = request.form['password']
    password_encode = contraseña.encode("utf-8")
    password_ecriptado = bcrypt.hashpw(password_encode,semilla)
    task = usuarios(nombre = nombre, apellido = apellido, correo = correo, contraseña = password_ecriptado)
    db.session.add(task)
    db.session.commit()
    #registra la sesion 
    session['name'] = nombre
    session['logged_in'] = True
    return render_template('login.html')        

@app.route('/crear', methods = ['POST'])
def creaPersonaje():
    if 'name' in session:
        foto = request.files['imagen-personaje']
        f = foto.read()
        task = personajes(nombre = request.form['personaje'],informacion= request.form['descripcion'], partido = request.form['partido'])
        with open('static/img/foto_{}.jpg'.format(task.nombre), 'wb') as archivo:
            archivo.write(f)
            task.foto = f  
        db.session.add(task)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/crear/<nombre>', methods = ['POST'])
def editaPersonaje(nombre):
    task =  personajes.query.filter_by(nombre = nombre).first()
    task1 = publicaciones.query.filter_by(personaje = nombre).all()
    if(request.form['personaje']!=''):
        archi = 'static/img/foto_{}.jpg'.format(task.nombre)
        os.rename(archi, 'static/img/foto_{}.jpg'.format(request.form['personaje']))
        task.nombre = request.form['personaje']
        for o in task1:
            o.personaje = request.form['personaje']
            o.foto = task.foto
    if(request.form['descripcion']!=''):
        task.informacion =  request.form['descripcion']
    if(request.form['partido']!=''):
        task.partido =  request.form['partido']
    arch = request.files['imagen-personaje']
    #si el usuar
    if(arch.filename!=""):
        foto = request.files['imagen-personaje']
        f = foto.read()
        with open('static/img/foto_{}.jpg'.format(task.nombre), 'wb') as archivo:
            archivo.write(f)
            task.foto = f 
            for o in task1:
                o.foto = f
    db.session.commit()
    db2.session.commit()
    return redirect(url_for('index'))

@app.route('/crearPublicacion', methods = ['POST'])
def newPost():
    if 'name' in session:
        username = session['name']
        personaje = request.form['personaje']
        titulo = request.form['titulo']
        fecha = request.form['fecha']
        contenido = request.form['descripcion']
        fuente = request.form['referencias']
        task = publicaciones(username = username, personaje = personaje, titulo = titulo, fecha = fecha, contenido = contenido, fuente = fuente)
        personaje = personajes.query.filter_by(nombre = task.personaje).first()
        task.foto = personaje.foto
        db.session.add(task)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/salir')
def logout():
    session.clear()
    session['logged_in'] = False
    return redirect(url_for('index'))

@app.route('/personajes')
@app.route('/personajes/<int:page>')
def Personaje(page=1):
    tasks1 = personajes.query.order_by(personajes.nombre.asc()).paginate(page,3,False)
    next_url = url_for('Personaje', page=tasks1.next_num) \
        if tasks1.has_next else None
    prev_url = url_for('Personaje', page=tasks1.prev_num) \
        if tasks1.has_prev else None
    return render_template('personajes.html',  tasks1 = tasks1.items, next_url=next_url,prev_url=prev_url, paginacion = tasks1)

@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')

@app.route('/crear-perso')
def crearPerso():
    return render_template('crear-perso.html')

@app.route('/editor-personaje/crear-referencia', methods = ['POST'])
def referenica():
    task = personajes.query.filter_by(id=int(request.form['PS'])).first()
    task.informacion = request.form['descripcion']+" "
    db.session.commit()
    return redirect(url_for('editor'))

@app.route('/admin-reportes', methods = ['POST','GET'])
def adminReportes():
    reportedPost = publicaciones.query.filter(publicaciones.reportado)
    reportedCharacter = personajes.query.filter(personajes.reportado)
    users = usuarios.query.all()
    return render_template('admin-reportes.html', reportedPosts = reportedPost, reportedCharacters = reportedCharacter, users = users)

@app.route('/role', methods = ['POST','GET'])
def role():
    userId = request.args.get('id')
    newRole = request.args.get('role')
    user = usuarios.query.filter_by(id = userId).first()
    user.rol = newRole
    db1.session.commit()
    return '''<script> window.location=document.referrer; </script>'''

if __name__=='__main__':
    app.run(debug=True, port=5000)