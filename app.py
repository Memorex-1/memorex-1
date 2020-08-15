from flask import Flask,render_template,redirect,request,url_for,session,flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import bcrypt
import os
import io

app = Flask(__name__)
app.secret_key = "appLogin"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/task1.db'
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

class usuarios(db1.Model):
    __tablename__ = 'login'
    id = db1.Column(db.Integer,primary_key=True)
    nombre = db1.Column(db.String(20))
    apellido = db1.Column(db.String(20))
    correo = db1.Column(db.String(50))
    contraseña = db1.Column(db.String(50))

class publicaciones(db2.Model):
    __tablename__ = 'publicaciones'
    id = db2.Column(db.Integer,primary_key=True)
    username = db2.Column(db.String(20))
    personaje = db2.Column(db.String(20))
    titulo = db2.Column(db.String(50))
    fecha = db2.Column(db.String(20))
    contenido = db2.Column(db.String(450))
    fuente = db2.Column(db.String(200))
    foto = db2.Column("foto")

@app.route('/')
@app.route('/index')
def index():
    tasks1 = personajes.query.all()
    #invertir orden, from flask_sqlalchemy import desc
    #tasks = publicaciones.query.filter(publicaciones.id != 0).order_by(desc(publicaciones.id)).all()
    tasks = publicaciones.query.all()
    #crea las fotos desde la db2 s
    for task in tasks:
        foto = task.foto
        if(os.path.isfile('static/img/foto_{}.jpg'.format(task.personaje)) == False):
            with open('static/img/foto_{}.jpg'.format(task.personaje), 'wb') as f:
                f.write(foto)
    return render_template('index.html', tasks = tasks, tasks1 = tasks1)
    
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
        if(usuario !=None):
            #obtiene el password encriptado encode
            password_encriptado_encode = usuario.contraseña
            #verifica el password
            if(bcrypt.checkpw(password_encode,password_encriptado_encode)):
                #registra la sesion
                session['name'] = usuario.nombre
                session['logged_in'] = True
                return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/editor-personaje', methods = ['POST','GET'])
def editor():
    if(request.method == "GET"):
        if 'name' in session:
            tasks = personajes.query.all()
            return render_template('editor-personaje.html', tasks = tasks)
        else:
            return redirect(url_for('ingresar'))
    

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
    task = usuarios(nombre = nombre, apellido = apellido, correo = correo, contraseña = password_ecriptado )
    db.session.add(task)
    db.session.commit()
    #registra la sesion 
    session['name'] = nombre
    #session['firstname'] = apellido
    #session['email'] = correo
    return render_template('login.html')        

@app.route('/crear', methods = ['POST'])
def pagina():
    foto = request.files['imagen-personaje']
    f = foto.read()
    task = personajes(nombre = request.form['personaje'], foto = f, informacion= request.form['descripcion'])
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/crearPublicacion', methods = ['POST'])
def pagina1():
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
def salir():
    session.clear()
    session['logged_in'] = False
    return redirect(url_for('index'))

@app.route('/personajes')
def Personaje():
    tasks1 = personajes.query.all()
    return render_template('personajes.html',  tasks1 = tasks1)

# Creando rutas para cada personaje
@app.route('/personaj/<per_id>')
def personaj(per_id=0):
    person = personajes.query.filter_by(id=per_id).first()
    return render_template('personaj.html',  personaje = person)

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

if __name__=='__main__':
    app.run(debug=True, port=5000)