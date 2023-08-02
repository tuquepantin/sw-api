"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite
#from models import character

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    user = User.query.all()
    user = list(map (lambda item: item.serialize(), user ))

    return jsonify(user), 200

@app.route('/character', methods=['GET'])
def list_character(): 
    if request.method == 'GET':
        character = Character()
        character = character.query.all()
        character = list(map (lambda item: item.serialize(), character ))
        return jsonify(character) ,200

@app.route('/planet', methods=['GET'])
def planet():
    if request.method == 'GET':
        planet = Planet()
        planet = planet.query.all()
        planet = list(map (lambda item: item.serialize(), planet ))
        return jsonify(planet) ,200


@app.route('/character/<int:character_id>', methods=['GET'])
def get_character(character_id):
    if request.method == 'GET':
        character = Character()
        character = character.query.get(character_id)
        character = character.serialize()
        return jsonify(character), 200


@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    if request.method == 'GET':
        planet = Planet()
        planet = planet.query.get(planet_id)
        planet = planet.serialize()
        return jsonify(planet), 200

@app.route('/user/favorites/<int:user_id>', methods=['GET'])
def list_user_fav(user_id):
    
    favorite = Favorite.query.filter_by(user_id=user_id).all()
    favorite = list(map (lambda item: item.serialize(), favorite ))
    return jsonify(favorite), 200



@app.route('/favorite/character/<int:character_id>', methods=['POST'])
def add_favorite_character(character_id, user_id):

    favorite = Favorite.query.filter_by(character_id = character_id, user_id = user_id).first()
    
    if favorite is not None:
        return jsonify({"msg": "Character it is already added"}), 400
    favorite = Favorite(character_id = character_id, user_id = user_id)
    db.session.add(favorite)
    try:
        db.session.commit()
        return jsonify(favorite.serialize()), 201
    except Exception as error:
        return jsonify({"msg": error.args}), 500


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planets(planet_id, user_id):

    favorite = Favorite.query.filter_by(planet_id = planet_id, user_id = user_id).first()

    if favorite is not None:
        return jsonify({"msg": "Planet it is already added"}), 400
    favorite = Favorite(planet_id = planet_id, user_id = user_id)
    db.session.add(favorite)
    try:
        db.session.commit()
        return jsonify(favorite.serialize()), 201
    except Exception as error:
        return jsonify({"msg": error.args}), 500 


@app.route('/favorite/character/<int:character_id>', methods=['DELETE'])
def delete_favorite_character(character_id, user_id):

    favorite = Favorite.query.filter_by(character_id = character_id, user_id = user_id).first()

    if favorite is None:
        return jsonify({"msg": "Character does not exist"}), 400
    db.session.delete(favorite)
    try:
        db.session.commit()
        return jsonify(favorite.serialize()), 200 
    except Exception as error:
        return jsonify({"msg": error.args}), 500


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planets(planet_id, user_id):

    favorite = Favorite.query.filter_by(planet_id = planet_id, user_id = user_id).first()

    if favorite is None:
        return jsonify({"msg": "Planet does not exist"}), 400
    db.session.delete(favorite)
    try:
        db.session.commit()
        return jsonify(favorite.serialize()), 200
    except Exception as error:
        return jsonify({"msg": error.args}), 500









# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
