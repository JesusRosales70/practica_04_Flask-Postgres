from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

# Ruta absoluta de la base de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_BD = os.path.join(BASE_DIR, "database", "practica.db")

def crear_base_datos():
    # Se añade la sangría correcta dentro de la función
    os.makedirs(os.path.join(BASE_DIR, "database"), exist_ok=True)
    conexion = sqlite3.connect(RUTA_BD)
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alumnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            pasatiempos TEXT,
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
    nombre = request.form["nombre"]
    pasatiempos = request.form.getlist("pasatiempos")
    me_gusta = request.form["me_gusta"]
    pasatiempos_texto = ", ".join(pasatiempos)

    conexion = sqlite3.connect(RUTA_BD)
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO alumnos
        (nombre, pasatiempos, me_gusta)
        VALUES (?, ?, ?)
    """, (nombre, pasatiempos_texto, me_gusta))
    conexion.commit()
    conexion.close()

    return render_template(
        "saludar.html",
        nombre=nombre,
        pasatiempos=pasatiempos,
        me_gusta=me_gusta
    )

@app.route("/alumnos")
def listar_alumnos():
    conexion = sqlite3.connect(RUTA_BD)
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM alumnos ORDER BY id")
    alumnos = cursor.fetchall()
    conexion.close()
    
    return render_template(
        "listar_alumnos.html",
        alumnos=alumnos
    )

# Inicializar la base de datos al arrancar
crear_base_datos()

if __name__ == "__main__":
    app.run(debug=True)
    # app.run(host="0.0.0.0", port=5000, debug=True)