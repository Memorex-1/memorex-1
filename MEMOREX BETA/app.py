from flask import Flask, render_template,redirect,request,url_for
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/task1.db'

db = SQLAlchemy(app)
class personajes(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    nombre = db.Column(db.String(20))
    informacion = db.Column(db.String(200))
    hecho = db.Column(db.String(100))
    pro = db.Column(db.Integer)
    fuente = db.Column(db.String(50))

@app.route('/')
def home():
    tasks = personajes.query.all()
    return render_template('PaginadePersonaje.html', tasks = tasks)
@app.route('/login.html/')
def login():
    return render_template('login.html')
@app.route('/crear', methods = ['POST'])
def pagina():
    task = personajes(nombre = request.form['nombre'])
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('home'))
@app.route('/crear-referencia/<id>', methods = ['POST'])
def referencia():
    task = personajes.query.filter_by(id=int(id)).first()
    task = personajes(informacion = request.form['descripcion'])
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('home'))
if __name__ == '__main__':
    app.run(debug=True)