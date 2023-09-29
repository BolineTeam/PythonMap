from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:CM3JfG8ClzgM5cpzK5YJ@containers-us-west-152.railway.app:7016/railway'
db = SQLAlchemy(app)

app.debug = True

# Definir el modelo Store
class Store(db.Model):
    idStore = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    lat = db.Column(db.Float)
    long = db.Column(db.Float)

# Definir el modelo DistanceStore
class DistanceStore(db.Model):
    idDistanceStore = db.Column(db.Integer, primary_key=True)
    idStore1 = db.Column(db.Integer, db.ForeignKey('store.idStore'))
    idStore2 = db.Column(db.Integer, db.ForeignKey('store.idStore'))
    distance = db.Column(db.Float)

# Variable global para almacenar los datos de las tiendas
stores_data = None

# Define una función para cargar los datos de las tiendas al iniciar la aplicación
def load_stores_data():
    global stores_data
    with app.app_context():
        stores_data = (
            db.session.query(
                Store.idStore,
                Store.name,
                Store.lat,
                Store.long
            )
            .all()
        )

# Llama a la función para cargar los datos de las tiendas al iniciar la aplicación
load_stores_data()

@app.route("/")
def index():
    return "¡Bienvenido a tu aplicación!"

@app.route("/mapa/<float:lat>/<float:long>/<string:nombre>")
def mapa(lat, long, nombre):
    return render_template("mapa.html", lat=lat, long=long, nombre=nombre)

@app.route("/tiendas_mas_cercanas", methods=["POST"])
def tiendas_mas_cercanas():
   
    data = request.json

    if "lat" not in data or "long" not in data:
        return jsonify({"error": "Los campos 'lat' y 'long' son requeridos"}), 400

    lat = float(data["lat"])
    long = float(data["long"])

    
    num_tiendas = int(data.get("num_store", 5))

    if num_tiendas > len(stores_data):
       
        return jsonify({"error": "No hay suficientes tiendas disponibles"}), 400

    # Calcular las tiendas más cercanas en memoria
    tiendas_cercanas = calcular_tiendas_cercanas(lat, long, num_tiendas)

    if not tiendas_cercanas:
        
        return jsonify({"There are not enough stores available"})


    return jsonify(tiendas_cercanas)

def calcular_tiendas_cercanas(lat, long, num_tiendas):
    # Calcular las tiendas más cercanas en memoria
    if stores_data:
        tiendas_cercanas = sorted(
            stores_data,
            key=lambda store: ((store.lat - lat) ** 2 + (store.long - long) ** 2) ** 0.5
        )[:num_tiendas]
        return [
            {
                "idStore": tienda.idStore,
                "name": tienda.name,
                "lat": tienda.lat,
                "long": tienda.long,
                "distancia": ((tienda.lat - lat) ** 2 + (tienda.long - long) ** 2) ** 0.5
            }
            for tienda in tiendas_cercanas
        ]
    else:
        return []

if __name__ == "__main__":
    app.run()
