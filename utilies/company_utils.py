#!/usr/bin/env python3

from models import Company
from flask import request
from middlewares.error_handler import Api_Errors
from models.companyagentinvitation import CompanyAgentInvitaion
from models import db

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




def invite_agent():
    """Invites a user to be an agent in a company"""
    try:
        data = request.get_json()
        
        inviter_id = data.get("inviter_id") 
        invitee_id = data.get("invitee_id")
        company_id = data.get("company_id")

        if not invitee_id or not inviter_id or not company_id:
            raise(Api_Errors.create_error(400, "Missing required fields"))

        existing_invitation = CompanyAgentInvitaion.query.filter_by(
            invitee_id=invitee_id, company_id=company_id, status="pending").first()

        if existing_invitation:
            raise(Api_Errors.create_error(400, "An active invitation already exists"))

        new_invitation = CompanyAgentInvitaion(
            inviter_id=inviter_id,
            invitee_id=invitee_id,
            company_id=company_id
            )

        db.session.add(new_invitation)
        db.session.c

        return {"message": "Invitation sent successfully", 
                        "invite_id": new_invitation.id}

    except Exception as err:
        return Api_Errors.create_error(500, str(err))


def invite_action():
    """Handles the acceptance or rejection of an invitation"""
    try:
        data = request.get_json()

        invite_id = data.get("id")
        action = data.get("action")  # Expected: "accept" or "reject"

        if not invite_id or action not in ["accept", "reject"]:
            raise Api_Errors.create_error(400, "Missing required fields or invalid action")

        invitation = CompanyAgentInvitaion.query.filter_by(id=invite_id).first()

        if not invitation:
            raise Api_Errors.create_error(404, "Invitation not found")

        if invitation.invite_status != "pending":
            raise Api_Errors.create_error(400, "Invitation is already processed")

        if invitation.is_expired():
            raise Api_Errors.create_error(400, "Invitation has expired")

        if action == "accept":
            invitation.invite_status = "accepted"
        elif action == "reject":
            invitation.invite_status = "rejected"

        db.session.commit()

        return {
            "message": f"Invitation {action}ed successfully",
            "success": True
        }

    except Exception as err:
        return Api_Errors.create_error(500, str(err))
