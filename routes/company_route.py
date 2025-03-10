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
from utilies.stripe_utilies import create_stripe_session
import stripe
from cryptography.fernet import Fernet
from os import getenv
from datetime import datetime, timedelta
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

@company_route.route('/filter/', methods=["GET"])
@verify_token_middleware
def filter_companies():
    """Filters companies based on specified criteria"""
    response = get_filtered_companies()
    return jsonify(response), 200 if response.get('success') else 500


@company_route.route('/register', methods=["POST"])
@verify_token_middleware
def register_new_company():
    user_id = g.user_id
    data = request.data.decode()
    data_body = json.loads(data)

    try:
        user = User.query.filter_by(id = user_id).first()
        if not user:
            raise (Api_Errors.create_error(404, "User is not found!"))

        CompanyValidation.register_validation(data_body)

        secret_key = getenv('FERNET_KEY')

        if not secret_key:
            raise (Api_Errors.create_error(500, "FERNET_KEY is missing from environment variables!"))

        f = Fernet(secret_key)

        new_company = Company.create_company_db(data_body, f)

        db.session.add(new_company)
        db.session.flush()

        relationship = CompanyOwner()

        relationship.user_id = user_id
        relationship.company_id = new_company.id
        relationship.user_role = data_body['user_role']

        db.session.add(relationship)
        db.session.commit()

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
    sig = request.headers.get("Stripe-Signature")
    payload = request.data

    try:
        event = stripe.Webhook.construct_event(
            payload, sig, getenv("STRIPE_WEBHOOK_SECRET")
        )
    except Exception as e:
        print(e)
        return jsonify({"error": f"Webhook error: {str(e)}"}), 500

    if event["type"] == "checkout.session.completed":
        try:
            metadata = event["data"]["object"].get("metadata")

            if not metadata:
                raise (Api_Errors.create_error(400, "Meta Data should be included!"))

            company_id = metadata.get("company_id")
            user_id = metadata.get("user_id")
            amount_paid = int(metadata.get("amount"))
            duration = int(metadata.get("duration"))

            expiration_date = datetime.utcnow() + timedelta(days=duration * 30)

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