#!/usr/bin/env python3

from flask import request, jsonify
from middlewares.error_handler import Api_Errors
from models.company_owners import CompanyOwner
from models.company import Company
from models.user import User
from models import db
import uuid


def get_filtered_companies():
    """Filters companies based on specified criteria"""

    try:
        industry = request.args.get("industry", "").strip()
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

        query = Company.query

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
            query = query.filter(Company.valuation >= valuation_min)
        if valuation_max is not None:
            query = query.filter(Company.valuation <= valuation_max)

        sort_column = getattr(Company, sort_by)
        query = query.order_by(sort_column.desc() if order == "desc" else sort_column.asc())

        companies = query.paginate(page=page, per_page=limit, error_out=False)

        return {
            "message": "Companies filtered successfully",
            "success": True,
            "total_results": companies.total,
            "total_pages": companies.pages,
            "current_page": page,
            "companies": [company.to_dict() for company in companies.items]
        }

    except Exception as err:
        return Api_Errors.create_error(500, str(err))


def invite_owner():
    """Invite a user to be an owner of a specific company"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        company_id = data.get('company_id')
        user_role = data.get('user_role', 'Owner')

        if not user_id or not company_id:
            raise Api_Errors.create_error(400, "User ID and Company ID are required!")

        user = User.query.get(user_id)
        company = Company.query.get(company_id)

        if not user or not company:
            raise Api_Errors.create_error(404, "User or Company not found!")

        existing_invite = CompanyOwner.query.filter_by(user_id=user_id, company_id=company_id).first()
        if existing_invite:
            raise Api_Errors.create_error(400, "User is already invited or an owner!")

        new_invite = CompanyOwner(
            rel_id=str(uuid.uuid4()),
            user_id=user_id,
            company_id=company_id,
            user_role=user_role,
            active=False
        )
        db.session.add(new_invite)
        db.session.commit()

        return jsonify({"message": "Invitation sent successfully", "success": True}), 201
    except Exception as err:
        db.session.rollback()
        raise Api_Errors.create_error(getattr(err, "status_code", 500), str(err))


def accept_invitation(rel_id):
    """Accept an invitation to become an owner of a company"""
    try:
        invite = CompanyOwner.query.filter_by(rel_id=rel_id, active=False).first()
        if not invite:
            raise Api_Errors.create_error(404, "Invitation not found or already accepted!")
        
        invite.active = True
        db.session.commit()

        return jsonify({"message": "Invitation accepted successfully", "success": True}), 200
    except Exception as err:
        db.session.rollback()
        raise Api_Errors.create_error(getattr(err, "status_code", 500), str(err))
