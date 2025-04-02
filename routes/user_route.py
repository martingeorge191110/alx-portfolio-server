#!/usr/bin/env python3
from models.user import User
import json
from flask import Blueprint, request, jsonify, g
from middlewares.verify_token import verify_token_middleware
from middlewares.error_handler import Api_Errors
from models import db
from models.company import Company
from models.company_owners import CompanyOwner
from models.investment_deal import InvestmentDeal, DealStatus
from utilies.stripe_utilies import create_stripe_session_investor
import stripe
from os import getenv
from datetime import datetime, timedelta
from sqlalchemy import func


user_route = Blueprint('user', __name__, url_prefix='/user')


@user_route.route("/token-valid", methods=["GET"])
@verify_token_middleware
def verify_token():
    """Function to chek token validation"""
    try:
        # GET user info from DB ther response with him in case of every thing is valid
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
    """Retreiving the user profile (his own data, companies and investment deals)"""
    try:
        user_id = g.user_id

        if not user_id or str(user_id).strip() == '':
            raise (Api_Errors.create_error(400, "User id not found!"))

        # get user info from DB
        user = User.query.filter_by(id = user_id).first()
        if not user:
            raise (Api_Errors.create_error(404, "User not found!"))
        
        # get user companies
        user_companies = (
            db.session.query(
                Company,
                func.count(InvestmentDeal.id).label("updates")
            )
            .join(CompanyOwner)
            .filter(CompanyOwner.user_id == user_id, CompanyOwner.active == True)
            .outerjoin(InvestmentDeal, (InvestmentDeal.company_id == Company.id) & (InvestmentDeal.deal_status == DealStatus.Pending))
            .group_by(Company.id)
            .all()
        )

        user_companies_list = []
        for company, pending_count in user_companies:
            company_data = company.company_card_dict()
            company_data["updates"] = pending_count
            user_companies_list.append(company_data)

        if user.user_type == 'Business':
            return ((jsonify({
                "message": "User Profile Retreived successfully",
                "success": True,
                "user": user.auth_dict(),
                "companies": user_companies_list
            }), 200))

        # all of user investment deals then response
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
    """Route to change the avatar"""
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

@user_route.route("/subiscripe", methods=["POST"])
@verify_token_middleware
def subiscription_investor():
    """Route to make account a premium"""
    user_id = g.user_id

    try:
        # check whether user exists or not, and his account type
        user = User.query.filter_by(id = user_id).first()
        if not user:
            raise (Api_Errors.create_error(404, "User is not found!"))
        
        user_data = user.auth_dict()
        if user_data['user_type'] is not 'Investor':
            raise (Api_Errors.create_error(403, "You have not the permission to have subiscription, Update your account to be investor account!"))

        # in case of every thing is valid, creating a stripe session
        meta_data = {
            "user_id": user_id, "duration": 12, "amount": 25
        }
        session = create_stripe_session_investor(meta_data, request.url_root.rstrip('/'))

        return ((jsonify({
            "message": "stripe session created successfully!",
            "success": True,
            "url": session.url
        }), 200))
    except Exception as err:
        db.session.rollback()
        raise (Api_Errors.create_error(getattr(err, "status_code", 500), str(err)))

@user_route.route("/webhook", methods=["POST"])
def stripe_webhook():
    sig = request.headers.get("Stripe-Signature")
    payload = request.data

    try:
        event = stripe.Webhook.construct_event(
            payload, sig, getenv("STRIPE_WEBHOOK_SECRET")
        )
    except Exception as e:
        return jsonify({"error": f"Webhook error: {str(e)}"}), 500

    if event["type"] == "checkout.session.completed":
        try:
            metadata = event["data"]["object"].get("metadata")

            if not metadata:
                raise (Api_Errors.create_error(400, "Meta Data should be included!"))

            user_id = metadata.get("user_id")
            amount_paid = int(metadata.get("amount"))
            duration = int(metadata.get("duration"))

            expiration_date = datetime.utcnow() + timedelta(days=duration * 30)

            user = User.query.filter_by(id = user_id).first()
            if not user:
                raise (Api_Errors.create_error(404, "User is not found!"))

            user.paid = True
            user.subis_start_date = datetime.utcnow()
            user.subis_end_date = expiration_date
            db.session.commit()

            payment_info = {
                "user_id": user_id,
                "duration_months": duration,
                "account_expiration_date": expiration_date.isoformat(),
            }

            return (jsonify({
                "success": True,
                "payment_info": payment_info
            }), 201)

        except Exception as err:
            return jsonify({"error": str(err)}), 500

    return jsonify({"message": "Webhook received but no action taken."}), 200

@user_route.route("/search/", methods=["GET"])
@verify_token_middleware
def users_searching():
    user_id = g.user_id
    f_name = request.args.get('f_n').strip()
    l_name = request.args.get('l_n').strip() if request.args.get('l_n') else None
    page = request.args.get('page', 1)

    if not f_name or f_name == 'null':
        raise(Api_Errors.create_error(400, "At least user first name is required!"))

    try:
        if not User.query.filter_by(id = user_id).first():
            raise (Api_Errors.create_error(404, "Users is not found!"))

        users = User.query

        if f_name:
            users = users.filter(User.f_n.ilike(f"%{f_name}%"))

        if l_name != 'null':
            users = users.filter(User.l_n.ilike(f"%{l_name}%"))

        pagination = users.paginate(page=int(page), per_page=10, error_out=False)
        users = pagination.items
        if not users:
            raise(Api_Errors.create_error(404, "No matching Users found!"))

        result = [user.auth_dict() for user in users]

        return ((jsonify({
            "message": "Users searching successfully!",
            "success": True,
            "users": result
        }), 200))
    except Exception as err:
        raise (Api_Errors.create_error(getattr(err, "status_code", 500), str(err)))