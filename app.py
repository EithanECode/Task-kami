import os
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Configuración de Flask
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuración de la base de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'db.db')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Mapeado de la base de datos con clases mediante el ORM 

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable= False)
    password = db.Column(db.String(50))
    tasks = db.relationship("Tasks", backref="user", lazy=True)

class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

#Algunas funciones auxiliares para validar el formulario, registrar el usuario, verificar datos

def validarFormulario(name, password):
    if not name or not password:
        return "Error, por favor vuelva a intentarlo."
    elif len(password) < 8:
        return "Error, la contraseña debe tener mínimo 8 caracteres."
    return None

def registrarUser(name, password):
    new_user = Users(name=name, password=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()

def verificarUser(name, password):
    user = Users.query.filter_by(name=name).first()

    if user:
        return check_password_hash(user.password, password)
    
    registrarUser(name=name, password=password)
    return True

#Ruta principal:

@app.route("/", methods=["GET", "POST"])
def index():
    tasks = []
    user = None

    if "user" in session:
        user = Users.query.filter_by(name=session["user"]).first()
        if user:
            tasks = Tasks.query.filter_by(user_id=user.id).all()

    if request.method == "POST":
        user_name_form = request.form.get("user")
        user_password_form = request.form.get("password")

        error = validarFormulario(user_name_form, user_password_form)
        if error:
            return render_template("index.html", error=error, tasks=tasks)

        if verificarUser(user_name_form, user_password_form):
            session["user"] = user_name_form
            return redirect("/")

        return render_template("index.html", error="Contraseña incorrecta", tasks=tasks)

    return render_template("index.html", tasks=tasks)

@app.route("/add_task", methods=["POST"])
def agregarTareas():
    if "user" not in session:
        return redirect("/")

    description = request.form.get("description_task")
    if description:
        user = Users.query.filter_by(name=session["user"]).first()
        if user:
            new_task = Tasks(description=description, user_id=user.id)
            db.session.add(new_task)
            db.session.commit()

    return redirect("/")

@app.route("/delete_task", methods=["POST"])
def eliminarTareas():
    if "user" not in session:
        return redirect("/")

    task_id = request.form.get("task_id")
    if task_id:
        user = Users.query.filter_by(name=session["user"]).first()
        task = Tasks.query.filter_by(id=task_id, user_id=user.id).first()
        if task:
            db.session.delete(task)
            db.session.commit()

    return redirect("/")

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return redirect("/")

# Esto sirve para ejecutar la aplicación:

if __name__ == "__main__":
    app.run(debug=True)
