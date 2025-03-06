#!/usr/bin/env python3
from flask import Blueprint, request

auth_route = Blueprint('auth', __name__, url_prefix='/auth')



@auth_route.route('/register', methods=['POST'], strict_slashes=False)
def login():
    return ('register')
