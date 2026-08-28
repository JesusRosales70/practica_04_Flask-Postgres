from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_BD = os.path.join(BASE_DIR, "database", "practica.db")

def crear_base_datos():
    os.makedirs(os.path.join(BASE_DIR, "database"), exist_ok=True)
    conexion = sqlite3.connect(RUTA_BD)
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alumnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            carrera TEXT,
            semestre INTEGER,
            turno TEXT,
            pasatiempos TEXT,
            nivel_prog TEXT,
            me_gusta TEXT
        )
    """)
    conexion.commit()
    conexion.close()

@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/saludar", methods=["POST"])
def f_saludar():
    nombre = request.form.get("nombre")
    carrera = request.form.get("carrera")
    semestre = request.form.get("semestre")
    turno = request.form.get("turno")
    pasatiempos = request.form.getlist("pasatiempos")
    nivel_prog = request.form.get("nivel_prog")
    me_gusta = request.form.get("me_gusta")

    pasatiempos_texto = ", ".join(pasatiempos)

    conexion = sqlite3.connect(RUTA_BD)
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO alumnos
        (nombre, carrera, semestre, turno, pasatiempos, nivel_prog, me_gusta)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nombre, carrera, semestre, turno, pasatiempos_texto, nivel_prog, me_gusta))
    conexion.commit()
    conexion.close()

    return render_template(
        "saludar.html",
        nombre=nombre,
        carrera=carrera,
        semestre=semestre,
        turno=turno,
        pasatiempos=pasatiempos,
        nivel_prog=nivel_prog,
        me_gusta=me_gusta
    )

@app.route("/alumnos")
def listar_alumnos():
    conexion = sqlite3.connect(RUTA_BD)
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, carrera, semestre, turno, pasatiempos, nivel_prog, me_gusta FROM alumnos ORDER BY id")
    alumnos = cursor.fetchall()
    conexion.close()

    return render_template(
        "listar_alumnos.html",
        alumnos=alumnos
    )

crear_base_datos()

if __name__ == "__main__":
    app.run(debug=True)