from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)

# =========================================================
# CONFIGURACIÓN DE CONEXIÓN A POSTGRESQL
# =========================================================
DATABASE_URL = os.environ.get("DATABASE_URL")

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
DB_NAME = os.environ.get("DB_NAME", "practica_db")
DB_PORT = int(os.environ.get("DB_PORT", 5432))

def obtener_conexion():
    url = os.environ.get("DATABASE_URL")
    
    # Si existe la URL completa (proporcionada por Clever Cloud o Render)
    if url:
        # Reemplazar la sintaxis obsoleta 'postgres://' por 'postgresql://'
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        
        # Forzar el parámetro sslmode
        if "sslmode" not in url:
            conector = "&" if "?" in url else "?"
            url = f"{url}{conector}sslmode=require"
            
        return psycopg2.connect(url, cursor_factory=RealDictCursor, connect_timeout=3)
    
    # Si se usan variables de entorno separadas
    return psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME,
        port=DB_PORT,
        sslmode="require",
        cursor_factory=RealDictCursor,
        connect_timeout=3
    )

def crear_tabla_clientes():
    conexion = None
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id SERIAL PRIMARY KEY,
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
                    limite_credito NUMERIC(10,2),
                    observaciones TEXT
                );
            """)
        conexion.commit()
    except Exception as e:
        print(f"Error al verificar/crear la tabla PostgreSQL: {e}")
    finally:
        if conexion:
            conexion.close()

# Intentar crear la tabla al arrancar el contexto de la aplicación
with app.app_context():
    crear_tabla_clientes()

# =========================================================
# RUTAS DE LA APLICACIÓN
# =========================================================
@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/mostrar_cliente", methods=["GET", "POST"])
def mostrar_cliente():
    # Si intentan acceder directamente por GET, redirige al formulario
    if request.method == "GET":
        return redirect(url_for("inicio"))

    # Garantizar que la tabla exista antes de intentar insertar
    crear_tabla_clientes()

    # Recolección y formateo de datos del formulario
    nombre = request.form.get("nombre")
    apellido_paterno = request.form.get("apellido_paterno")
    apellido_materno = request.form.get("apellido_materno")
    
    # Si la fecha viene vacía, asigna None para insertar NULL en PostgreSQL
    fecha_nacimiento_raw = request.form.get("fecha_nacimiento")
    fecha_nacimiento = fecha_nacimiento_raw if fecha_nacimiento_raw else None

    genero = request.form.get("genero", "")
    correo = request.form.get("correo")
    telefono = request.form.get("telefono")
    estado = request.form.get("estado")
    ciudad = request.form.get("ciudad")
    codigo_postal = request.form.get("codigo_postal")
    tipo_cliente = request.form.get("tipo_cliente")
    intereses = request.form.getlist("intereses")
    intereses_texto = ", ".join(intereses)
    
    # Sanitización del valor numérico
    limite_credito_raw = request.form.get("limite_credito")
    try:
        limite_credito = float(limite_credito_raw) if limite_credito_raw else 0.0
    except ValueError:
        limite_credito = 0.0

    observaciones = request.form.get("observaciones")

    conexion = None
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            sql = """
                INSERT INTO clientes 
                (nombre, apellido_paterno, apellido_materno, fecha_nacimiento, genero, correo, telefono, estado, ciudad, codigo_postal, tipo_cliente, intereses, limite_credito, observaciones)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                nombre, apellido_paterno, apellido_materno,
                fecha_nacimiento, genero,
                correo, telefono, estado, ciudad, codigo_postal, tipo_cliente,
                intereses_texto, limite_credito, observaciones
            ))
        conexion.commit()
    except Exception as e:
        print(f"Error en la BD: {e}")
        return f"<h3>Error al guardar en PostgreSQL:</h3><p>{e}</p>", 500
    finally:
        if conexion:
            conexion.close()  # Libera la conexión de forma inmediata

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
    # Garantizar que la tabla exista antes de listar los registros
    crear_tabla_clientes()

    conexion = None
    clientes = []
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            sql = """
                SELECT 
                    id,
                    COALESCE(nombre, '') AS nombre,
                    COALESCE(apellido_paterno, '') AS apellido_paterno,
                    COALESCE(apellido_materno, '') AS apellido_materno,
                    COALESCE(TO_CHAR(fecha_nacimiento, 'YYYY-MM-DD'), '') AS fecha_nacimiento,
                    COALESCE(genero, '') AS genero,
                    COALESCE(correo, '') AS correo,
                    COALESCE(telefono, '') AS telefono,
                    COALESCE(estado, '') AS estado,
                    COALESCE(ciudad, '') AS ciudad,
                    COALESCE(codigo_postal, '') AS codigo_postal,
                    COALESCE(tipo_cliente, '') AS tipo_cliente,
                    COALESCE(intereses, '') AS intereses,
                    COALESCE(limite_credito, 0) AS limite_credito,
                    COALESCE(observaciones, '') AS observaciones
                FROM clientes
                ORDER BY id ASC
            """
            cursor.execute(sql)
            clientes = cursor.fetchall()
    except Exception as e:
        return f"<h3>Error al consultar PostgreSQL:</h3><p>{e}</p>", 500
    finally:
        if conexion:
            conexion.close()  # Libera la conexión de forma inmediata

    return render_template("listar_clientes.html", clientes=clientes)

# =========================================================
# EJECUCIÓN DEL SERVIDOR LOCAL
# =========================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)