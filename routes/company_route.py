#!/usr/bin/env python3

from models.company import Company
from flask import Blueprint, jsonify, request
from middlewares.error_handler import Api_Errors
from models import db
from middlewares.verify_token import verify_token_middleware
from utilies.company_utils import get_filtered_companies

company_route = Blueprint('company', __name__, url_prefix='/company')


@company_route.route('/search/', methods=['GET'])
@verify_token_middleware
def search_company_by_name():
    """search by company name"""
    try:
        company_name = request.args.get('name').strip()

        if not company_name:
            raise(Api_Errors.create_error(400, "company name is required!"))
        
        companies = Company.query.filter(Company.name.ilike(f"%{company_name}%").all())

        if not companies:
            raise(Api_Errors.create_error(404, "No matching companines found!"))
        
        result = [companies.to_dict() for company in companies]

        return ((jsonify({
            "message": "User Profile Retreived successfully",
            "success": True,
            "companies": result
        }), 200))
    except Exception as err:
        raise (Api_Errors.create_error(getattr(err, "status_code", 500), str(err)))

@company_route.route('/filter/', method=["GET"])
@verify_token_middleware
def filter_companies():
    """Filters companies based on specified criteria"""
    response = get_filtered_companies()
    return jsonify(response), 200 if response.get('success') else 500

