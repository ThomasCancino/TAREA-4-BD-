from flask import Flask,redirect
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
#importo una biblioteca para los passwords y la seguridad
from werkzeug.security import  generate_password_hash
from werkzeug.security import check_password_hash

import os

dbdir= "sqlite:///" + os.path.abspath(os.getcwd()) + "/database.db"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]=dbdir
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= False
db = SQLAlchemy(app)
num_cta = 3584026713 #establece un numero para iniciar las autoasignaciones de numero de cuenta

#Sql me permite cominicarme con el por medio de clases en python
class personas(db.Model):
    apodo = db.Column(db.String(50), primary_key=True)
    #ojo que no necesitamos que las claves sean unicas
    password = db.Column(db.String(80), nullable=False)
    nativo = db.Column(db.String(80), nullable=False)
    contacto = db.Column(db.Integer, nullable=False)
    ventas = db.Column(db.Integer, nullable=True)
    compras = db.Column(db.Integer, nullable=False)
    id_c = db.Column(db.Integer,db.ForeignKey('cuenta.id'))

class cuenta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    saldo = db.Column(db.Integer, nullable=False)
    gastado = db.Column(db.Integer, nullable=False)
    historial = db.Column(db.String(255), nullable=True) #cambie el nombre del atributo de 'saldo' a 'historial', y cambie su nulabilidad, para que pueda ser nulo

class objeto(db.Model):
    nombre = db.Column(db.String(126), primary_key=True)
    legalidad = db.Column(db.Boolean, nullable=False)
    codigo = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Integer, nullable=False)
    duenos = db.Column(db.Integer, nullable=False)
    dueno_act = db.Column(db.String(50),db.ForeignKey('personas.apodo'))

class policia(db.Model):
    placa = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(126), nullable=False)
    soborno = db.Column(db.Date, nullable=False)
    num_s= db.Column(db.Integer,db.ForeignKey('sector.numero'))

class sector(db.Model):
    numero = db.Column(db.Integer, primary_key=True)
    ubicacion = db.Column(db.String(126), nullable=False)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/base")
def base():
    myUser = personas.query.all()
    return render_template('/base.html', myUser=myUser)

@app.route("/search")
def search():
    nombre = request.args.get("nickname")
    user = personas.query.filter_by(apodo=nombre).first()
    if user:
        return render_template("cuenta.html", nombre=nombre)
    else:
        return "El usuario no existe"

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        #hashed_pw = generate_password_hash(request.form["password"], method="sha256")
        new_user = personas(apodo=request.form["username"], password=request.form["password"], nativo=request.form["native"], contacto=request.form["contact"], ventas=0, compras=0, id_c=num_cta)
        #agregue el atributo de la llave foranea (el numero de cuenta, o id de ella, el que es asignado automaticamente)
        db.session.add(new_user)
        db.session.commit()
        #nos confirma cadad uno de los cambios
        new_cta = cuenta(id=num_cta, saldo=0, gastado=0) #crea cuenta
        db.session.add(new_cta) #agrega la cta a la bd
        db.session.commit() #"confirma" la agregacion
        num_cta = num_cta + 1 #cambia el numero de cuenta para que al auto asignarse no se repitan
        #return "ya te has registrado exitosamente "
        return redirect("http://localhost:3000")
    return  render_template("signup.html")

@app.route("/login",methods=["GET","POST"])
def login():
#request es una solicitud, query es una consulta
    if request.method == "POST":
        usuario = personas.query.filter_by(apodo=request.form["username"]).first()
        passwords = personas.query.filter_by(password=request.form["password"]).first()

        #si usuario y el password del hash es igual al passwor del usuario return
        if usuario and passwords:
            #return "Estas loggeado"
            user = personas.query.filter_by(apodo = usuario).first()
            return render_template("user_menu.html", user=user) #cambie el return para que abriera el menu de usuario
        return "tus credenciales son invalidas, revisa he intenta de nuevo "
    #si es de tipo GET que renderice la plantilla
    return render_template("login.html")

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True,port=3000)
