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
import random
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
        new_user.nationality = data_body.get('nationality')

        db.session.add(new_user)
        db.session.commit()

        token_payload = {
            "user_id": str(new_user.id),
            "exp": datetime.utcnow() + timedelta(days=3)
        }

        token = jwt.encode(token_payload, getenv('JWT_KEY'), algorithm=getenv('JWT_ALG'))

        return (jsonify({
            "message": "User registered successfully",
            "success": True,
            "user": new_user.auth_dict(),
            "token": token
        }), 201)

    except Exception as err:
        db.session.rollback()
        raise (Api_Errors.create_error(getattr(err, "status_code", 500), str(err)))


@auth_route.route('/login', methods=['POST'], strict_slashes=False)
def login():
    """Login Route controller"""
    try:
        data = request.data.decode()
        data_body = json.loads(data)

        user = AuthValidator.login_valid(data_body)

        token_payload = {
            "user_id": str(user.id),
            "exp": datetime.utcnow() + timedelta(days=3)
        }

        token = jwt.encode(token_payload, getenv('JWT_KEY'), algorithm=getenv('JWT_ALG'))

        return (jsonify({
            "message": "User Login successfully",
            "success": True,
            "user": user.auth_dict(),
            "token": token
        }), 200)
    except Exception as err:
        db.session.rollback()
        raise (Api_Errors.create_error(getattr(err, "status_code", 500), str(err)))


@auth_route.route('/request-code', methods=['POST'], strict_slashes=False)
def request_code():
    from utilies.mail_helper import send_code_mail

    try:
        data = request.data.decode()
        data_body = json.loads(data)

        user = AuthValidator.request_code_valid(data_body)

        code = str(random.randint(100000, 999999))
        hashed_code = generate_password_hash(code)
        expiration_time = datetime.now() + timedelta(hours=1)

        user.gen_code = hashed_code
        user.expired_date_gen_code = expiration_time

        db.session.commit()

        send_code_mail(user.email, code, expiration_time)

        return (jsonify({
            "message": "Code has been sent successfully",
            "success": True
        }), 200)
    except Exception as err:
        db.session.rollback()
        raise (Api_Errors.create_error(getattr(err, "status_code", 500), str(err)))


@auth_route.route('/reset-pass', methods=['POST'], strict_slashes=False)
def reset_pass_code():
    try:
        data = request.data.decode()
        data_body = json.loads(data)

        AuthValidator.reset_pass_code_valid(data_body)

        return (jsonify({
            "message": "Now you can successfully reset your password",
            "success": True
        }), 200)
    except Exception as err:
        db.session.rollback()
        raise (Api_Errors.create_error(getattr(err, "status_code", 500), str(err)))


@auth_route.route('/reset-pass', methods=['PUT'], strict_slashes=False)
def reset_password():
    try:
        data = request.data.decode()
        data_body = json.loads(data)

        user = AuthValidator.reset_password_valid(data_body)

        user.gen_code = None
        user.expired_date_gen_code = None
        user.password = generate_password_hash(data_body.get('password'))

        db.session.commit()

        return (jsonify({
            "message": "successfully, new Password has been generated!",
            "success": True
        }), 200)
    except Exception as err:
        db.session.rollback()
        raise (Api_Errors.create_error(getattr(err, "status_code", 500), str(err)))
