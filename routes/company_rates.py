#!/usr/bin/env python3
from flask import Blueprint, request, g, jsonify
from middlewares.verify_token import verify_token_middleware
from models.user import User
from middlewares.error_handler import Api_Errors
from models import db
from validation.company_validation import CompanyValidation
from models.company_growth_rate import CompanyGrowthRate
from routes.company_route import company_route
import json
from models.company_owners import CompanyOwner


company_rates_route = company_route = Blueprint('company_rates', __name__, url_prefix='/company/rates')


@company_route.route("/<string:company_id>", methods=['GET'])
@verify_token_middleware
def growth_rates_information(company_id):
    """"""
    user_id = g.user_id

    try:
        user = User.query.filter_by(id = user_id).first()
        if not user:
            raise (Api_Errors.create_error(404, "User is not found!"))

        company = CompanyValidation.company_id_validation(company_id)

        rates = CompanyGrowthRate.query.filter_by(company_id = company_id).order_by(CompanyGrowthRate.year.asc()).all()
        rates_list = []
        for rate in rates:
            rates_list.append(rate.to_dict())

        return ((jsonify({
            "message": "successfully retreived company growth rates!",
            "success": True,
            "company_id": company['id'],
            "growthRates": rates_list
        }), 200))
    except Exception as err:
        db.session.rollback()
        raise (Api_Errors.create_error(getattr(err, "status_code", 500), str(err)))

@company_route.route("/<string:company_id>", methods=['POST'])
@verify_token_middleware
def create_growth_rates(company_id):
    user_id = g.user_id
    data = request.data.decode()
    data_body = json.loads(data)

    try:
        user = User.query.filter_by(id = user_id).first()
        if not user:
            raise Api_Errors.create_error(404, "User is not found!")

        company = CompanyValidation.company_id_validation(company_id)

        CompanyValidation.growth_rates_validation(data_body)

        relationship = CompanyOwner.query.filter_by(user_id = user_id, company_id = company_id, active = True)
        if not relationship:
            raise (Api_Errors.create_error(403, "You are not authirezed to to this action"))

        rates_list = []
        for ele in data_body:
            rate = CompanyGrowthRate()
            rate.company_id = company['id']
            rate.year = ele['year']
            rate.profit = ele['profit']

            rates_list.append(rate.to_dict())
            db.session.add(rate)

        db.session.commit()

        return ((jsonify({
            "message": "successfully posted new company growth rates!",
            "success": True,
            "company_id": company['id'],
            "growthRates": rates_list
        }), 200))
    except Exception as err:
        db.session.rollback()
        raise (Api_Errors.create_error(getattr(err, "status_code", 500), str(err)))

@company_route.route("/<string:company_id>", methods=['DELETE'])
@verify_token_middleware
def delete_all_company_rates(company_id):
    user_id = g.user_id

    try:
        user = User.query.filter_by(id = user_id).first()
        if not user:
            raise (Api_Errors.create_error(404, "User is not found!"))


        company = CompanyValidation.company_id_validation(company_id)

        relationship = CompanyOwner.query.filter_by(user_id = user_id, company_id = company_id, active = True)
        if not relationship:
            raise (Api_Errors.create_error(403, "You are not authirezed to to this action"))

        company_rates = CompanyGrowthRate.query.filter_by(company_id = company_id).all()

        for rate in company_rates:
            db.session.delete(rate)

        db.session.commit()
        return ((jsonify({
            "message": "successfully Deleted Old company growth rates!",
            "success": True,
        }), 200))
    except Exception as err:
        print(err)
        db.session.rollback()
        raise (Api_Errors.create_error(getattr(err, "status_code", 500), str(err)))
