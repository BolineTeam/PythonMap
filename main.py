from flask import Flask, render_template

app = Flask(__name__)

@app.route("/mapa/<string:lat>/<string:long>/<string:nombre>")
def mapa(lat, long, nombre):
    return render_template("mapa.html", lat=lat, long=long, nombre=nombre)

if __name__ == "__main__":
    app.run()