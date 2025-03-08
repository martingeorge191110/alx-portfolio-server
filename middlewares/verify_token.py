#!/usr/bin/env python3
"""Verify user token script middleware"""
import jwt
from os import getenv
from functools import wraps
from flask import request, jsonify, g
from middlewares.error_handler import Api_Errors


def verify_token_middleware(f):
    """Function midlleware to verify user tokens"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            raise (Api_Errors.create_error(400, "Authorization must be included in headers!"))

        parts = auth_header.split(" ")
        if len(parts) != 2 or parts[0] != "Bearer":
            raise (Api_Errors.create_error(400, "Invalid authorization format!"))

        token = parts[1]

        try:
            payload = jwt.decode(token, getenv("JWT_KEY", ""), algorithms=[getenv('JWT_ALG')])
            print(payload)
            g.user_id = payload.get("user_id")
        except jwt.ExpiredSignatureError:
            raise (Api_Errors.create_error(401, "Token has expired!"))
        except jwt.InvalidTokenError:
            raise (Api_Errors.create_error(401, "Token is not valid!"))

        return f(*args, **kwargs)

    return (decorated_function)
