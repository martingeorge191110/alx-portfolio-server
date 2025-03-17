#!/usr/bin/env python3
"""API for invesments route"""

from flask import request, g, Blueprint, jsonify
from engine.db_storage import db
from middlewares.error_handler import Api_Errors
from middlewares.verify_token import verify_token_middleware
from models.investment_deal import InvestmentDeal
from models.user import User
from models.company import Company
import uuid

investment_route = Blueprint("investment",  __name__, url_prefix='/investment')


@investment_route.route("/company/<string:company_id>/deal", methods=["POST"])
@verify_token_middleware
def investor_send_request_to_company(company_id):
    """Investor sends an investment request to a company"""
    user_id = g.user_id
    try:
        data = request.get_json()
        amount = float(data.get("amount"))
        equity_percentage = float(data.get("equity_percentage"))

        if not all([company_id, amount, equity_percentage]):
            raise Api_Errors.create_error(400, "Missing required fields!")

        user = User.query.filter_by(id=user_id).first()
        user_dict = user.auth_dict()
        if not user or user_dict['user_type'] != "Investor" or not user_dict['paid']:
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

        investment_request_dict = investment_request.to_dict()
        db.session.add(investment_request)
        db.session.commit()

        new_deal = {
                "deal_id": investment_request_dict['id'],
                "amount": investment_request_dict['amount'],
                "equity_percentage": investment_request_dict['equity_percentage'],
                "deal_status": investment_request_dict['deal_status'],
                "created_at": investment_request_dict['created_at'],
                "updated_at": investment_request_dict['updated_at'],
                "user": {
                    "f_n": user.f_n,
                    "l_n": user.l_n,
                    "avatar": user.avatar
                }
            }

        return (jsonify({
            "message": "Investment request created successfully!",
            "success": True,
            "investment_deal": new_deal}
                ), 201)

    except Exception as err:
        db.session.rollback()
        raise (Api_Errors.create_error(getattr(err, "status_code", 500), str(err)))


@investment_route.route("/investor/<string:company_id>",methods=["GET"])
@verify_token_middleware
def get_the_investment_request(company_id):
    """Investor retrieves investment requests sent to a specific company"""
    user_id = g.user_id
    try:
        investment_requests = InvestmentDeal.query.filter_by(company_id=company_id, user_id=user_id).all()
        
        if not investment_requests:
            raise Api_Errors.create_error(404, "No investment requests found!")

        return {
            "investment_requests": [deal.to_dict() for deal in investment_requests]
        }, 200

    except Exception as err:
        return Api_Errors.create_error(getattr(err, "status_code", 500), str(err))


@investment_route.route("/investor/<string:deal_id>", methods=["PUT"])
@verify_token_middleware
def update_investment_request(deal_id):
    """Investor modifies an existing investment request"""
    user_id = g.user_id
    try:
        data = request.get_json()
        amount = data.get("amount")
        equity_percentage = data.get("equity_percentage")
        
        investment_request = InvestmentDeal.query.filter_by(id=deal_id, user_id=user_id).first()
        if not investment_request:
            raise Api_Errors.create_error(404, "Investment request not found or unauthorized!")
        
        if amount:
            investment_request.amount = amount
        if equity_percentage:
            investment_request.equity_percentage = equity_percentage
        
        db.session.commit()

        return {
            "message": "Investment request updated successfully!",
            "Updated details": investment_request.to_dict()
        }, 200

    except Exception as err:
        return Api_Errors.create_error(getattr(err, "status_code", 500), str(err))


@investment_route.route("/investor/deals", methods=["GET"])
@verify_token_middleware
def get_all_investor_deals():
    """Retrieve all investment deals for the logged-in investor"""
    user_id = g.user_id
    try:
        investment_deals = InvestmentDeal.query.filter_by(user_id=user_id).all()
        
        if not investment_deals:
            raise Api_Errors.create_error(404, "No investment deals found for this investor!")

        return {
            "investment_deals": [deal.to_dict() for deal in investment_deals]
        }, 200

    except Exception as err:
        return Api_Errors.create_error(getattr(err, "status_code", 500), str(err))


@investment_route.route("/company/<string:deal_id>", methods=["GET"])
@verify_token_middleware
def get_specific_investment_deal(deal_id):
    """Retrieve a specific investment deal for a company"""
    try:
        user_id = g.user_id
        user = User.query.filter_by(id=user_id).first()
        
        if not user or user.user_type.value != "Business":
            raise Api_Errors.create_error(403, "Unauthorized: Only company owners can view investment deals!")

        investment_deal = InvestmentDeal.query.filter_by(id=deal_id).first()

        if not investment_deal:
            raise Api_Errors.create_error(404, "Investment deal not found!")

        return {"investment_deal": investment_deal.to_dict()}, 200

    except Exception as err:
        return Api_Errors.create_error(getattr(err, "status_code", 500), str(err))


@investment_route.route("/company/<string:deal_id>", methods=["PUT"])
@verify_token_middleware
def respond_to_investment_deal(deal_id):
    """Accept or Reject an investment deal"""
    try:
        user_id = g.user_id
        user = User.query.filter_by(id=user_id).first()
        
        if not user:
            raise Api_Errors.create_error(403, "Unauthorized: Only company owners can respond to investment deals!")

        data = request.get_json()
        new_status = data.get("deal_status")

        if new_status not in ["Accepted", "Rejected"]:
            raise Api_Errors.create_error(400, "Invalid status! Must be 'Accepted' or 'Rejected'.")

        investment_deal = InvestmentDeal.query.filter_by(id=deal_id).first()

        if not investment_deal:
            raise Api_Errors.create_error(404, "Investment deal not found!")

        investment_deal.deal_status = new_status
        db.session.commit()

        return (jsonify(
            {
            "message": f"Investment deal {new_status.lower()} successfully!",
            "success": True,
            "updated_deal": investment_deal.to_dict(),
        }), 200)

    except Exception as err:
        db.session.rollback()
        raise Api_Errors.create_error(getattr(err, "status_code", 500), str(err))
