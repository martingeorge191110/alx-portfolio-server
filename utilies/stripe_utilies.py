#!/usr/bin/env python3
import stripe
import datetime
from dateutil.relativedelta import relativedelta
from os import getenv
from middlewares.error_handler import Api_Errors


stripe.api_key = getenv('STRIPE_SECRET_KEY')

def create_stripe_session(meta_data, base_url):
    """Create a new Stripe Checkout session using provided metadata.
    """
    try:
        duration = int(meta_data.get('duration', 12))
        start_date = datetime.date.today()
        expiration_date = start_date + relativedelta(months=duration)
        start_date_str = start_date.strftime('%m/%d/%Y')
        expiration_date_str = expiration_date.strftime('%m/%d/%Y')

        description = f"""Subscription Details:
- Amount: $100.00
- Duration: {duration} months
- Start Date: {start_date_str}
- Expiration Date: {expiration_date_str}""".strip()

        success_url = f"{base_url}/api/company/payment/success"
        cancel_url = f"{base_url}/api/company/payment/cancel"

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "System Subscription",
                        "description": description,
                    },
                    "unit_amount": int(meta_data.get('amount', 100)) * 100,
                },
                "quantity": 1,
            }],
            mode="payment",
            metadata={
                "company_id": meta_data.get('company_id'),
                "company_name": meta_data.get('company_name'),
                "owner_id": meta_data.get('user_id'),
                "duration": str(duration),
                "amount": str(meta_data.get('amount', '')),
            },
            success_url=success_url,
            cancel_url=cancel_url
        )

        return (session)
    except Exception as err:
        raise (Api_Errors.create_error(getattr(err, "status_code", 500), str(err)))
