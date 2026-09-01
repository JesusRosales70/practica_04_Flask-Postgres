from flask import Flask, render_template, request
import pymysql
import os

app = Flask(__name__)

# =========================================================
# CONFIGURACIÓN DE CONEXIÓN A MYSQL
# En local usará los valores por defecto. En la nube tomará las variables de entorno.
# =========================================================
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")  # Agrega tu contraseña local si usas una
DB_NAME = os.environ.get("DB_NAME", "practica_db")
DB_PORT = int(os.environ.get("DB_PORT", 3306))

def obtener_conexion():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        cursorclass=pymysql.cursors.DictCursor
    )

def crear_base_datos():
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alumnos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                carrera VARCHAR(100),
                semestre INT,
                turno VARCHAR(20),
                pasatiempos VARCHAR(255),
                nivel_prog VARCHAR(50),
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

    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        # En MySQL los marcadores de posición son %s en lugar de ?
        sql = """
            INSERT INTO alumnos
            (nombre, carrera, semestre, turno, pasatiempos, nivel_prog, me_gusta)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (nombre, carrera, semestre, turno, pasatiempos_texto, nivel_prog, me_gusta))
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
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id, nombre, carrera, semestre, turno, pasatiempos, nivel_prog, me_gusta FROM alumnos ORDER BY id")
        alumnos_dict = cursor.fetchall()
    conexion.close()

    # Formatea los datos a tuplas para mantener compatibilidad con listar_alumnos.html
    alumnos = [
        (a["id"], a["nombre"], a["carrera"], a["semestre"], a["turno"], a["pasatiempos"], a["nivel_prog"], a["me_gusta"])
        for a in alumnos_dict
    ]

    return render_template(
        "listar_alumnos.html",
        alumnos=alumnos
    )

if __name__ == "__main__":
    try:
        crear_base_datos()
    except Exception as e:
        print(f"Aviso BD: Recuerda crear primero la base de datos en MySQL. Detalle: {e}")

    app.run(debug=True)