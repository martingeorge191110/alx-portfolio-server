#!/usr/bin/env python3
"""Flask Application"""
from flask import Flask, jsonify
from dotenv import load_dotenv
from os import getenv
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from middlewares.error_handler import Api_Errors
from datastorage import db, init_db


load_dotenv()

server = Flask(__name__)

MYSQL_USER = getenv('MYSQL_USER')
MYSQL_PWD = getenv('MYSQL_PWD')
MYSQL_HOST = getenv('MYSQL_HOST')
MYSQL_DB = getenv('MYSQL_DB')

server.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}/{}'.format(
    MYSQL_USER, MYSQL_PWD, MYSQL_HOST, MYSQL_DB)
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

cors = CORS(server)

init_db(server)


@server.route("/")
def errors():
    err = Api_Errors.create_error(404, 'Please wait for building the project, server not built yet!')
    raise (err)

@server.errorhandler(Api_Errors)
def not_found(err):
    response_error = jsonify(Api_Errors.response_error(error=err))
    status_code = err.status_code
    return (response_error, status_code)


if __name__ == '__main__':
    """Running the Application"""
    PORT = PORT = int(getenv('PORT', 5000))
    HOST = getenv('HOST', '0.0.0.0')
    server.run(port=PORT, host=HOST, debug=True)
