#!/usr/bin/env python3
"""Flask Application"""
from flask import Flask, jsonify
from dotenv import load_dotenv
from os import getenv
from flask_cors import CORS
from middlewares.error_handler import Api_Errors
from engine.db_storage import DBStorage

load_dotenv()


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

cors = CORS(app)

db_storage = DBStorage(app)


@app.route("/")
def errors():
    err = Api_Errors.create_error(404, 'Please wait for building the project, server not built yet!')
    raise (err)

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