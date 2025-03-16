#!/usr/bin/env python3
"""Flask Application"""
from flask import Flask, jsonify, Blueprint
from dotenv import load_dotenv
from os import getenv
from flask_cors import CORS
from middlewares.error_handler import Api_Errors
from engine.db_storage import DBStorage
from routes.auth_route import auth_route
from routes.user_route import user_route
from routes.company_route import company_route
from routes.company_rates import company_rates_route
from routes.company_docs import company_docs_route
from routes.notification_route import notification_route
from routes.investment_route import investment_route

load_dotenv()


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = getenv("JWT_KEY")
app.config['JWT_ALG'] = getenv("JWT_ALG")
app.config['GMAIL_USER'] = getenv("GMAIL_USER")
app.config['GMAIL_APP_PASSWORD'] = getenv("GMAIL_PASS")
app.config['FERNET_KEY'] = getenv("FERNET_KEY")
app.config['STRIPE_PUPLISH_KEY'] = getenv("STRIPE_PUPLISH_KEY")
app.config['STRIPE_SECRET_KEY'] = getenv("STRIPE_SECRET_KEY")
app.config['STRIPE_WEBHOOK_SECRET'] = getenv("STRIPE_WEBHOOK_SECRET")

cors = CORS(app, supports_credentials=True, origins=["*"])

db_storage = DBStorage(app)

app_bp = Blueprint('api', __name__, url_prefix='/api')
app_bp.register_blueprint(auth_route)
app_bp.register_blueprint(user_route)
app_bp.register_blueprint(company_route)
app_bp.register_blueprint(company_rates_route)
app_bp.register_blueprint(company_docs_route)
app_bp.register_blueprint(notification_route)
app_bp.register_blueprint(investment_route)
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
