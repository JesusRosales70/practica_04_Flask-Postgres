# ==========================================================
# PRÁCTICA 0
# HOLA MUNDO CON FLASK + JINJA
# ==========================================================
from flask import Flask, render_template, request

# Crear la aplicación Flask
app = Flask(__name__)

# Ruta principal
@app.route("/")
def inicio():
    return render_template("index.html")

# Ruta que recibe el nombre enviado por el formulario
@app.route("/saludar", methods=["POST"])
def saludar():
    # Recuperar los datos cuyo name en HTML coincida
    nombre = request.form["nombre"]
    pasatiempos = request.form.getlist("pasatiempos")
    me_gusta = request.form["me_gusta"]
    
    # Enviar las variables hacia saludar.html
    return render_template(
        "saludar.html",
        nombre=nombre,
        pasatiempos=pasatiempos,
        me_gusta=me_gusta
    )

# Iniciar el servidor de desarrollo
if __name__ == "__main__":
    app.run(debug=True)
    #app.run(host="0.0.0.0", port=5000, debug=True)