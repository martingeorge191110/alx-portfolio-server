#!/usr/bin/env python3
"""authintication validation for each process"""
from middlewares.error_handler import Api_Errors
import validators
from password_strength import PasswordStats
from models.user import User
from werkzeug.security import check_password_hash
from datetime import datetime
from engine.db_storage import db


class AuthValidator:
    """Class to validate authintication routes"""

    @staticmethod
    def register_valid(data_body):
        """Static method to validate register body"""
        items = ['f_n', 'l_n', 'email', 'password', 'confirm_password', 'user_type', 'nationality']
        for i in items:
            if i not in data_body or type(data_body[i]) is not str or data_body[i].strip() == '':
                raise (Api_Errors.create_error(400, f"{i} is required and must be String!"))

        if not validators.email(data_body['email']):
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


    @staticmethod
    def login_valid(data_body):
        """Static method to validate login request body"""
        items = ['email', 'password']
        for i in items:
            if i not in data_body or type(data_body[i]) is not str or data_body[i].strip() == '':
                raise (Api_Errors.create_error(400, f"{i} is required and must be String!"))

        if not validators.email(data_body['email']):
            raise (Api_Errors.create_error(400, f"email address is not valid!"))

        user = User.query.filter_by(email = data_body['email']).first()
        if not user:
            raise (Api_Errors.create_error(404, f"email address is not exists, register first!"))

        check_pass = check_password_hash(user.password, data_body['password'])
        if not check_pass:
            raise (Api_Errors.create_error(400, f"Password or Email address is not true!"))

        return (user)


    @staticmethod
    def request_code_valid(data_body):
        """Static method to validate requesting code valid body"""
        if 'email' not in data_body or type(data_body['email']) is not str or data_body['email'].strip() == '':
            raise (Api_Errors.create_error(400, f"email address is required and must be String!"))

        if not validators.email(data_body['email']):
            raise (Api_Errors.create_error(400, f"email address is not valid!"))

        user = User.query.filter_by(email = data_body['email']).first()
        if not user:
            raise (Api_Errors.create_error(404, f"email address is not exists, register first!"))

        return (user)


    @staticmethod
    def reset_pass_code_valid(data_body):
        """Static method to validate reseting password code valid body"""
        items = ['email', 'code']
        for i in items:
            if i not in data_body or type(data_body[i]) is not str or data_body[i].strip() == '':
                raise (Api_Errors.create_error(400, f"{i} is required and must be String!"))

        if not validators.email(data_body['email']):
            raise (Api_Errors.create_error(400, f"email address is not valid!"))

        user = User.query.filter_by(email = data_body['email']).first()
        if not user:
            raise (Api_Errors.create_error(404, f"email address is not exists, register first!"))

        check_time = user.expired_date_gen_code and datetime.now() > user.expired_date_gen_code
        if check_time:
            user.gen_code = None
            user.expired_date_gen_code = None
            db.session.commit()
            raise (Api_Errors.create_error(400, f"code is expired, please request another!"))

        check_code = check_password_hash(user.gen_code, data_body['code'])
        if not check_code:
            raise (Api_Errors.create_error(400, f"Generated code is not true!"))

        return (user)

    @staticmethod
    def reset_password_valid(data_body):
        """Static method to validate new password"""
        items = ['email', 'password', 'confirm_password']
        for i in items:
            if i not in data_body or type(data_body[i]) is not str or data_body[i].strip() == '':
                raise (Api_Errors.create_error(400, f"{i} is required and must be String!"))

        if not validators.email(data_body['email']):
            raise (Api_Errors.create_error(400, f"email address is not valid!"))

        user = User.query.filter_by(email = data_body['email']).first()
        if not user:
            raise (Api_Errors.create_error(404, f"email address is not exists, register first!"))

        strong_pwd = PasswordStats(data_body['password']).strength() > 0.5
        if not strong_pwd:
            raise (Api_Errors.create_error(400, f"Password is not strong enough!"))

        if data_body['password'] != data_body['confirm_password']:
            raise (Api_Errors.create_error(400, f"Passwords deosnot match each other!"))

        return (user)
