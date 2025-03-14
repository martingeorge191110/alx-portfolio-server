#!/usr/bin/env python3
"""API for invesments route"""

from flask import request, g, Blueprint
from engine.db_storage import db
from middlewares.error_handler import Api_Errors
from middlewares.verify_token import verify_token_middleware
from models.investment_deal import InvestmentDeal
from models.user import User
from models.company import Company
import uuid

investment_route = Blueprint("investment", __name__, "/investment")


@investment_route.route("/investor", methods=["POST"])
@verify_token_middleware
def investor_send_request_to_company():
    """Investor sends an investment request to a company"""
    user_id = g.user_id
    try:
        data = request.get_json()
        company_id = data.get("company_id")
        amount = data.get("amount")
        equity_percentage = data.get("equity_percentage")
        
        if not all([company_id, amount, equity_percentage]):
            raise Api_Errors.create_error(400, "Missing required fields!")
        
        user = User.query.filter_by(id=user_id).first()
        if not user or user.user_type.value != "Investor":
            raise Api_Errors.create_error(403, "Unauthorized: Invalid credentials!")
        
        company = Company.query.filter_by(id=company_id).first()
        if not company:
            raise Api_Errors.create_error(404, "company not found!")
        
        investment_request = InvestmentDeal(
            id=str(uuid.uuid4()),
            company_id=company_id,
            user_id=user_id,
            amount=amount,
            equity_percentage=equity_percentage,
            deal_status="Pending",
        )
        
        db.session.add(investment_request)
        db.session.commit()
        
        return {"message": "Investment request created successfully!",
                "Investment details": investment_request.to_dict()}, 201
    
    except Exception as err:
        return Api_Errors.create_error(getattr(err, "status_code", 500), str(err))
