import os
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for
import psycopg2
from psycopg2.extras import RealDictCursor

# Cargar variables de entorno del archivo .env
load_dotenv()

app = Flask(__name__)


# =========================================================
# CONFIGURACIÓN DE CONEXIÓN A POSTGRESQL
# =========================================================
def obtener_conexion():
    url = os.environ.get("DATABASE_URL")

    # Si existe la URL completa (proporcionada por Render o Aiven)
    if url:
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)

        if "sslmode" not in url:
            conector = "&" if "?" in url else "?"
            url = f"{url}{conector}sslmode=require"

        return psycopg2.connect(
            url, cursor_factory=RealDictCursor, connect_timeout=5
        )

    # Conexión local usando las variables con prefijo DB_LOCAL_
    return psycopg2.connect(
        host=os.getenv("DB_LOCAL_HOST"),
        port=os.getenv("DB_LOCAL_PORT", "13040"),
        database=os.getenv("DB_LOCAL_NAME"),
        user=os.getenv("DB_LOCAL_USER"),
        password=os.getenv("DB_LOCAL_PASSWORD"),
        sslmode="require",
        cursor_factory=RealDictCursor,
        connect_timeout=10,
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
    if request.method == "GET":
        return redirect(url_for("inicio"))

    crear_tabla_clientes()

    nombre = request.form.get("nombre")
    apellido_paterno = request.form.get("apellido_paterno")
    apellido_materno = request.form.get("apellido_materno")

    fecha_nacimiento_raw = request.form.get("fecha_nacimiento")
    fecha_nacimiento = (
        fecha_nacimiento_raw if fecha_nacimiento_raw else None
    )

    genero = request.form.get("genero", "")
    correo = request.form.get("correo")
    telefono = request.form.get("telefono")
    estado = request.form.get("estado")
    ciudad = request.form.get("ciudad")
    codigo_postal = request.form.get("codigo_postal")
    tipo_cliente = request.form.get("tipo_cliente")
    intereses = request.form.getlist("intereses")
    intereses_texto = ", ".join(intereses)

    limite_credito_raw = request.form.get("limite_credito")
    try:
        limite_credito = (
            float(limite_credito_raw) if limite_credito_raw else 0.0
        )
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
            cursor.execute(
                sql,
                (
                    nombre,
                    apellido_paterno,
                    apellido_materno,
                    fecha_nacimiento,
                    genero,
                    correo,
                    telefono,
                    estado,
                    ciudad,
                    codigo_postal,
                    tipo_cliente,
                    intereses_texto,
                    limite_credito,
                    observaciones,
                ),
            )
        conexion.commit()
    except Exception as e:
        print(f"Error en la BD: {e}")
        return f"<h3>Error al guardar en PostgreSQL:</h3><p>{e}</p>", 500
    finally:
        if conexion:
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
        observaciones=observaciones,
    )


@app.route("/clientes")
def listar_clientes():
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
            conexion.close()

    return render_template("listar_clientes.html", clientes=clientes)


# =========================================================
# EJECUCIÓN DEL SERVIDOR LOCAL
# =========================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)