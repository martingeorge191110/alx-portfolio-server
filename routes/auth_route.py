#!/usr/bin/env python3
from flask import Blueprint, request, jsonify
import json
from validation.auth_validator import AuthValidator
from middlewares.error_handler import Api_Errors
from werkzeug.security import generate_password_hash
from models.user import User
from engine.db_storage import db
from datetime import datetime, timedelta
import jwt
from os import getenv


auth_route = Blueprint('auth', __name__, url_prefix='/auth')


@auth_route.route('/register', methods=['POST'], strict_slashes=False)
def register():
    try:
        data = request.data.decode()
        data_body = json.loads(data)

        AuthValidator.register_valid(data_body)

        new_user = User()
        new_user.f_n = data_body.get('f_n')
        new_user.l_n = data_body.get('l_n')
        new_user.email = data_body.get('email').strip().lower()
        new_user.password = generate_password_hash(data_body.get('password'))
        new_user.user_type = data_body.get('user_type')

        db.session.add(new_user)
        db.session.commit()

        token_payload = {
            "user_id": str(new_user.id),
            "exp": datetime.utcnow() + timedelta(days=3)
        }

        token = jwt.encode(token_payload, getenv('JWT_KEY'), algorithm=getenv('JWT_ALG'))

        return (jsonify({
            "message": "User registered successfully",
            "user": new_user.auth_dict(),
            "token": token
        }), 201)

    except Exception as e:
        db.session.rollback()
        raise (Api_Errors.create_error(500, str(e)))
