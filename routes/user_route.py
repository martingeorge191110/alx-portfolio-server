#!/usr/bin/env python3
from models.user import User
import json
from flask import Blueprint, request, jsonify, g
from middlewares.verify_token import verify_token_middleware
from middlewares.error_handler import Api_Errors
from models import db
from models.company import Company
from models.company_owners import CompanyOwner
from models.investment_deal import InvestmentDeal
import re


user_route = Blueprint('user', __name__, url_prefix='/user')


@user_route.route("/token-valid", methods=["GET"])
@verify_token_middleware
def verify_token():
    """Function to chek token validation"""
    try:
        user_id = g.user_id
        user = User.query.filter_by(id = user_id).first()

        if not user:
            raise (Api_Errors.create_error(404, "User not found!"))
    
        return (jsonify({
            "message": "User Token is still valid successfully",
                "success": True,
            "user": user.auth_dict(),
        }), 200)
    except Exception as err:
        raise (Api_Errors.create_error(getattr(err, "status_code", 500), str(err)))


@user_route.route("/profile", methods=["GET"])
@verify_token_middleware
def user_profile():
    try:
        user_id = g.user_id

        if not user_id or str(user_id).strip() == '':
            raise (Api_Errors.create_error(400, "User id not found!"))

        user = User.query.filter_by(id = user_id).first()
        if not user:
            raise (Api_Errors.create_error(404, "User not found!"))
        
        user_companies = db.session.query(Company).join(CompanyOwner).filter(CompanyOwner.user_id == user_id).all()

        user_companies_list = []
        for company in user_companies:
            user_companies_list.append(company.company_card_dict())

        if user.user_type == 'Business':
            return ((jsonify({
                "message": "User Profile Retreived successfully",
                "success": True,
                "user": user.auth_dict(),
                "companies": user_companies_list
            }), 200))

        investments = (
            db.session.query(Company, InvestmentDeal)
            .join(InvestmentDeal, Company.id == InvestmentDeal.company_id)
            .filter(InvestmentDeal.user_id == user_id)
            .all()
            )
        
        user_deals = []
        for company, investment_deal in investments:
            user_deals.append(company.company_investment_card_dict(investment_deal))

        return ((jsonify({
            "message": "User Profile Retreived successfully",
            "success": True,
            "user": user.auth_dict(),
            "companies": user_companies_list,
            "deals": user_deals
        }), 200))
    except Exception as err:
        db.session.rollback()
        raise (Api_Errors.create_error(getattr(err, "status_code", 500), str(err)))

@user_route.route("/avatar", methods=["PUT"])
@verify_token_middleware
def change_user_avatar():
    user_id = g.user_id

    data = request.data.decode()
    data_body = json.loads(data)

    try:
        if 'secure_url' not in data_body or type(data_body['secure_url']) is not str:
            raise (Api_Errors.create_error(400, "Secure url is required and string!"))

        if not str(data_body['secure_url']).startswith('https://res.cloudinary.com/daghpnbz3/image/upload/') and str(data_body['secure_url']).endswith('.jpg'):
            raise (Api_Errors.create_error(400, "File uploaded is not valid!!"))

        user = User.query.filter_by(id = user_id).first()
        if not user:
            raise (Api_Errors.create_error(404, "User is not found!"))

        user.avatar = data_body['secure_url']

        user_data = user.auth_dict()
        db.session.commit()

        return ((jsonify({
            "message": "User Profile picture Changed successfully!",
            "success": True,
            "secure_url": user_data['avatar']
        }), 200))
    except Exception as err:
        db.session.rollback()
        raise (Api_Errors.create_error(getattr(err, "status_code", 500), str(err)))