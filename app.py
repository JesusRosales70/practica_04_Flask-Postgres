from flask import Flask, render_template, request
import pymysql
import os

app = Flask(__name__)

# =========================================================
# CONFIGURACIÓN DE CONEXIÓN A MYSQL
# En local usa valores por defecto; en la nube toma las variables de entorno.
# =========================================================
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
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

def crear_tabla_clientes():
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                apellido_paterno VARCHAR(100),
                apellido_materno VARCHAR(100),
                fecha_nacimiento DATE,
                genero VARCHAR(20),
                correo VARCHAR(100),
                telefono VARCHAR(20),
                estado VARCHAR(50),
                ciudad VARCHAR(50),
                codigo_postal VARCHAR(10),
                tipo_cliente VARCHAR(50),
                intereses TEXT,
                limite_credito DECIMAL(10,2),
                observaciones TEXT
            )
        """)
    conexion.commit()
    conexion.close()

# Ejecuta la verificación de la tabla al iniciar la app
with app.app_context():
    try:
        crear_tabla_clientes()
    except Exception as e:
        print(f"Error al verificar la tabla: {e}")

# =========================================================
# RUTAS DE LA APLICACIÓN
# =========================================================
@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/mostrar_cliente", methods=["POST"])
def mostrar_cliente():
    # Recepción de datos del formulario
    nombre = request.form.get("nombre")
    apellido_paterno = request.form.get("apellido_paterno")
    apellido_materno = request.form.get("apellido_materno")
    fecha_nacimiento = request.form.get("fecha_nacimiento")
    genero = request.form.get("genero", "")
    correo = request.form.get("correo")
    telefono = request.form.get("telefono")
    estado = request.form.get("estado")
    ciudad = request.form.get("ciudad")
    codigo_postal = request.form.get("codigo_postal")
    tipo_cliente = request.form.get("tipo_cliente")
    intereses = request.form.getlist("intereses")
    intereses_texto = ", ".join(intereses)
    limite_credito = request.form.get("limite_credito")
    observaciones = request.form.get("observaciones")

    # Guardar en MySQL
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        sql = """
            INSERT INTO clientes 
            (nombre, apellido_paterno, apellido_materno, fecha_nacimiento, genero, correo, telefono, estado, ciudad, codigo_postal, tipo_cliente, intereses, limite_credito, observaciones)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            nombre, apellido_paterno, apellido_materno, fecha_nacimiento, genero,
            correo, telefono, estado, ciudad, codigo_postal, tipo_cliente,
            intereses_texto, limite_credito, observaciones
        ))
    conexion.commit()
    conexion.close()

    return render_template(
        "mostrar_cliente.html",
        nombre=nombre,
        apellido_paterno=apellido_paterno,
        apellido_materno=apellido_materno,
        fecha_nacimiento=fecha_nacimiento,
        genero=genero,
        correo=correo,
        telefono=telefono,
        estado=estado,
        ciudad=ciudad,
        codigo_postal=codigo_postal,
        tipo_cliente=tipo_cliente,
        intereses=intereses,
        limite_credito=limite_credito,
        observaciones=observaciones
    )

@app.route("/clientes")
def listar_clientes():
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Trae todos los campos de clientes
            cursor.execute("SELECT * FROM clientes ORDER BY 1")
            clientes = cursor.fetchall()
    finally:
        conexion.close()

    return render_template("listar_clientes.html", clientes=clientes)

# =========================================================
# EJECUCIÓN DEL SERVIDOR LOCAL
# =========================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)