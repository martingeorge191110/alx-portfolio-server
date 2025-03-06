#!/usr/bin/env python3
"""Flask Application"""
from flask import Flask, jsonify, Blueprint
from dotenv import load_dotenv
from os import getenv
from flask_cors import CORS
from middlewares.error_handler import Api_Errors
from engine.db_storage import DBStorage
from routes.auth_route import auth_route

load_dotenv()


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = getenv("JWT_KEY")

cors = CORS(app)

db_storage = DBStorage(app)

app_bp = Blueprint('api', __name__, url_prefix='/api')
app_bp.register_blueprint(auth_route)
app.register_blueprint(app_bp)


@app.errorhandler(Api_Errors)
def not_found(err):
    response_error = jsonify(Api_Errors.response_error(error=err))
    status_code = err.status_code
    return (response_error, status_code)


if __name__ == '__main__':
    """Running the Application"""
    PORT = PORT = int(getenv('PORT', 5000))
    HOST = getenv('HOST', '0.0.0.0')
    db_storage.create_tables()
    app.run(port=PORT, host=HOST, debug=True)