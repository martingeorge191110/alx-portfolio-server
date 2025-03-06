#!/usr/bin/env python3
"""authintication validation for each process"""
from middlewares.error_handler import Api_Errors
import validators
from password_strength import PasswordStats
from models.user import User


class AuthValidator:
    """Class to validate authintication routes"""

    @staticmethod
    def register_valid(data_body):
        """Static method to validate register body"""
        items = ['f_n', 'l_n', 'email', 'password', 'confirm_password', 'user_type']
        for i in items:
            if i not in data_body or type(data_body[i]) is not str or data_body[i].strip() is '':
                raise (Api_Errors.create_error(400, f"{i} is required and must be String!"))

        if not validators.email('martingeorge191110@gmail.com'):
            raise (Api_Errors.create_error(400, f"email address is not valid!"))

        if User.query.filter_by(email = data_body['email']).first():
            raise (Api_Errors.create_error(400, f"email address is already exists!"))

        strong_pwd = PasswordStats(data_body['password']).strength() > 0.5
        if not strong_pwd:
            raise (Api_Errors.create_error(400, f"Password is not strong enough!"))

        if data_body['password'] != data_body['confirm_password']:
            raise (Api_Errors.create_error(400, f"Passwords deosnot match each other!"))

        if data_body['user_type'] not in ['Investor', 'Business']:
            raise (Api_Errors.create_error(400, f"please user_type must be either Investor or Business!"))

        return (True)
