#!/usr/bin/env python3

from models.company import Company
from flask import Blueprint, jsonify, request, g
from middlewares.error_handler import Api_Errors
from models import db
from middlewares.verify_token import verify_token_middleware
import json
import stripe.error
from validation.company_validation import CompanyValidation
from models.user import User
from models.company_owners import CompanyOwner
from models.company_docs import CompanyDocs
from utilies.stripe_utilies import create_stripe_session
import stripe
from os import getenv
import uuid
from datetime import datetime, timedelta
from utilies.company_utils import get_filtered_companies, invite_owner, accept_invitation
from models.investment_deal import InvestmentDeal


company_route = Blueprint('company', __name__, url_prefix='/company')


@company_route.route('/search/', methods=['GET'])
@verify_token_middleware
def search_company_by_name():
    """search by company name"""
    try:
        company_name = request.args.get('name').strip()

        if not company_name:
            raise(Api_Errors.create_error(400, "company name is required!"))

        companies = Company.query.filter(Company.name.ilike(f"%{company_name}%")).all()

        if not companies:
            raise(Api_Errors.create_error(404, "No matching companines found!"))

        result = [company.to_dict() for company in companies]

        return ((jsonify({
            "message": "User Profile Retreived successfully",
            "success": True,
            "companies": result
        }), 200))
    except Exception as err:
        raise (Api_Errors.create_error(getattr(err, "status_code", 500), str(err)))

@company_route.route('/filter/', methods=["GET"])
@verify_token_middleware
def filter_companies():
    """Filters companies based on specified criteria"""
    response = get_filtered_companies()
    return jsonify(response), 200 if response.get('success') else 500

@company_route.route('/invite/<string:company_id>', methods=['POST'])
@verify_token_middleware
def invite_owner_route(company_id):
    user_id = g.user_id
    return invite_owner(user_id, company_id)

@company_route.route('/accept/<string:rel_id>', methods=['PUT'])
@verify_token_middleware
def accept_invitation_route(rel_id):
    return accept_invitation(rel_id)

@company_route.route('/reject/<string:rel_id>', methods=['DELETE'])
@verify_token_middleware
def reject_invitation_route(rel_id):
    user_id = g.user_id

    if not rel_id or rel_id == 'null' or str(rel_id).strip() == '':
        raise (Api_Errors.create_error(400, "relation id is required!"))

    try:
        # check user is exists or not
        user = User.query.filter_by(id = user_id).first()
        if not user:
            raise (Api_Errors.create_error(404, "User is not found!"))
        # check the relationship between the user and compnay
        # 
        relationship = CompanyOwner.query.filter_by(rel_id = rel_id).first()
        if not relationship:
            raise (Api_Errors.create_error(404, "No one invited you to his company!"))
        
        db.session.delete(relationship)
        db.session.commit()

        return (jsonify(
            {"message": "Invitation Canceled successfully", "success": True}
            ), 200)
    except Exception as err:
        db.session.rollback()
        raise (Api_Errors.create_error(getattr(err, "status_code", 500), str(err)))

@company_route.route('/register', methods=["POST"])
@verify_token_middleware
def register_new_company():
    user_id = g.user_id
    data = request.data.decode()
    data_body = json.loads(data)

    try:
        # check user exists, validate the company registering required data
        user = User.query.filter_by(id = user_id).first()
        if not user:
            raise (Api_Errors.create_error(404, "User is not found!"))

        CompanyValidation.register_validation(data_body)

        # creating the company with unpaid info in DB.
        new_company = Company.create_company_db(data_body)

        db.session.add(new_company)
        db.session.flush()

        relationship = CompanyOwner()

        relationship.user_id = user_id
        relationship.company_id = new_company.id
        relationship.user_role = data_body['user_role']
        relationship.active = True

        db.session.add(relationship)
        db.session.commit()

        # create a stripe session with meta data
        meta_data = {
            "company_id": new_company.company_card_dict().get('id'), "user_id": user.id, "company_name": new_company.name, "duration": 12, "amount": 100
        }
        stripe_session = create_stripe_session(meta_data, request.url_root.rstrip('/'))

        return ((jsonify({
            "message": "New company has been created, stripe session created successfully!",
            "success": True,
            "company": new_company.company_card_dict(),
            "url": stripe_session.url
        }), 200))

    except Exception as err:
        raise (Api_Errors.create_error(getattr(err, "status_code", 500), str(err)))

@company_route.route("/webhook", methods=["POST"])
def stripe_webhook():
    """WebHook for listing to the payment event!"""
    sig = request.headers.get("Stripe-Signature")
    payload = request.data

    try:
        event = stripe.Webhook.construct_event(
            payload, sig, getenv("STRIPE_WEBHOOK_SECRET_TWO")
        )
    except Exception as e:
        return jsonify({"error": f"Webhook error: {str(e)}"}), 500

    # after complete the payment process
    if event["type"] == "checkout.session.completed":
        try:
            metadata = event["data"]["object"].get("metadata")

            if not metadata:
                raise (Api_Errors.create_error(400, "Meta Data should be included!"))

            # get the data from mete after process
            company_id = metadata.get("company_id")
            user_id = metadata.get("user_id")
            amount_paid = int(metadata.get("amount"))
            duration = int(metadata.get("duration"))

            expiration_date = datetime.utcnow() + timedelta(days=duration * 30)

            # get the company info and submit the payment to DB
            company = Company.query.filter_by(id = company_id).first()
            company.paid = True
            company.subis_end_date = expiration_date
            company.subis_start_date = datetime.utcnow()

            db.session.commit()

            payment_info = {
                "company_id": company_id,
                "agent_id": user_id,
                "amount_paid": amount_paid,
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

@company_route.route("/<string:id>", methods=['GET'])
@verify_token_middleware
def retreive_company_dashboard(id):
    """Retreiving the company Dashboard"""
    user_id = g.user_id

    try:
        # check user exists.
        user = User.query.filter_by(id = user_id).first()
        if not user:
            raise (Api_Errors.create_error(404, "User is not found!"))

        # check the company data is valid or not
        data_result = {}
        user_data = user.auth_dict()
        company = CompanyValidation.company_id_validation(id)

        data_result['user'] = user_data
        data_result['company'] = company

        # check the relationship between user and comapny
        relationship = CompanyOwner.query.filter_by(user_id = user_id, company_id = id, active = True).first()
        if relationship:
            data_result['isOwner'] = True
        else:
            data_result['isOwner'] = False

        # retreiving the company owners
        company_owners = db.session.query(User, CompanyOwner.user_role).join(CompanyOwner).filter(CompanyOwner.company_id == id, CompanyOwner.active == True).all()
        company_owners_list = []
        for user, user_role in company_owners:
            company_owners_list.append({
                "id": user.id,
                "f_n": user.f_n,
                "l_n": user.l_n,
                "avatar": user.avatar,
                "role": user_role
            })
        
        # all invetsment deals
        investments = InvestmentDeal.query.filter_by(company_id=id).join(User).add_columns(
            InvestmentDeal.id,
            InvestmentDeal.amount,
            InvestmentDeal.equity_percentage,
            InvestmentDeal.deal_status,
            InvestmentDeal.created_at,
            InvestmentDeal.updated_at,
            User.f_n,
            User.l_n,
            User.avatar
        ).all()

        deals_list = [
            {
                "deal_id": deal.id,
                "amount": deal.amount,
                "equity_percentage": deal.equity_percentage,
                "deal_status": deal.deal_status.name,
                "created_at": deal.created_at,
                "updated_at": deal.updated_at,
                "user": {
                    "f_n": deal.f_n,
                    "l_n": deal.l_n,
                    "avatar": deal.avatar
                }
            }
            for deal in investments
        ]
        data_result['owners'] = company_owners_list
        data_result['investments'] = deals_list

        return (jsonify({
            "success": True,
            "message": "successfully Retreived company data and owners data!",
            "data_result": data_result
        }), 200)

    except Exception as err:
        db.session.rollback()
        raise (Api_Errors.create_error(getattr(err, "status_code", 500), str(err)))

@company_route.route('/<string:company_id>/avatar', methods=["PUT"])
@verify_token_middleware
def change_company_avatar(company_id):
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

        company = Company.query.filter_by(id = company_id).first()
        if not company:
            raise (Api_Errors.create_error(404, "Company is not found!"))
        
        relationship = CompanyOwner.query.filter_by(user_id = user_id, company_id = company_id, active = True)
        if not relationship:
            raise (Api_Errors.create_error(403, "You are not authirezed to to this action"))
        
        company.avatar = data_body['secure_url']

        db.session.commit()

        company_data = company.to_dict()

        return ((jsonify({
            "message": "User Profile picture Changed successfully!",
            "success": True,
            "secure_url": company_data['avatar']
        }), 200))

    except Exception as err:
        db.session.rollback()
        raise (Api_Errors.create_error(getattr(err, "status_code", 500), str(err)))
