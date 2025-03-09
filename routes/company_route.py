#!/usr/bin/env python3

from models.company import Company
from flask import Blueprint, jsonify, request
from middlewares.error_handler import Api_Errors
from models import db
from middlewares.verify_token import verify_token_middleware


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
    try:
        industry = request.args.get("indusrty", "").strip()
        location = request.args.get("location", "").strip()
        stock_market = request.args.get("stock_market", "").lower()
        founded_min = request.args.get("founded_min", type=int)
        founded_max = request.args.get("founded_max", type=int)
        valuation_min = request.args.get("valuation_min", type=int)
        valuation_max = request.args.get("valuation_max", type=int)
        sort_by = request.args.get("sort_by", "name")
        order = request.args.get("order", "asc").lower()
        limit = request.args.get("limit", 10, type=int)
        page = request.args.get("page", 1, type=int)

        valid_sort_fields = ["name", "industry", "location", "founder_year", "valuation"]
        if sort_by not in valid_sort_fields:
            raise Api_Errors.create_error(400, f"Invalid sort field. Choose from {valid_sort_fields}")
        
        query = Company.query()

        if industry:
            query = query.filter(Company.industry.ilike(f"%{industry}%"))
        if location:
            query = query.filter(Company.location.ilike(f"%{location}%"))
        if stock_market == "true":
            query = query.filter(Company.stock_market == True)
        elif stock_market == "false":
            query = query.filter(Company.stock_market == False)
        if founded_min is not None:
            query = query.filter(Company.founder_year >= founded_min)
        if founded_max is not None:
            query = query.filter(Company.founder_year <= founded_max)
        if valuation_min is not None:
            query = query.filter(Company.founder_year >= founded_min)
        if valuation_max is not None:
            query = query.filter(Company.founder_year <= founded_max)
        
        sort_column = getattr(Company, sort_by)

        if order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        companies = query.paginate(page=page, per_page=limit, error_out=False)

        result = [company.to_dict() for company in companies.items]

        return jsonify({
            "message": "Companies filtered successfully",
            "success": True,
            "total_results": companies.total,
            "total_pages": companies.pages,
            "current_page": page,
            "companies": result
        }), 200

    except Exception as err:
        return Api_Errors.create_error(500, str(err))
