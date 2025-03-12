#!/usr/bin/env python3
"""routes for notification handling"""

from flask import request, g, Blueprint
from middlewares.error_handler import Api_Errors
from middlewares.verify_token import verify_token_middleware
from models.user import User
from models.notification import Notification
from models import db
import uuid

notification_route = Blueprint("notification", __name__, url_prefix="/notification")


@notification_route.route("/<string:receiver_id>", methods=["GET"])
@verify_token_middleware
def get_notification(receiver_id):
    """retrieve notification with pagination"""
    try:
        user_id = g.user_id
        
        user = User.query.filter_by(id = user_id).first()
        if not user:
            raise Api_Errors.create_error(404, "User is not found!")

        if user_id != receiver_id:
            raise Api_Errors.create_error(403, "Unauthorized person!")

        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 10, type=int)

        notifications = Notification.query.filter_by(to_user_id=receiver_id).order_by(
            Notification.created_at.desc()).paginate(page=page, per_page=limit, error_out=False)

        if not notifications.items:
            raise Api_Errors.create_error(404, "No Notification found!")

        return {
            "notifications": [notif.auth_dict() for notif in notifications.items],
            "page": page,
            "total_pages": notifications.pages,
            "total_notifications": notifications.total
        }, 200

    except Exception as err:
        return Api_Errors.create_error(getattr(err, "status_code", 500), str(err))

@notification_route.route("/", methods=["POST"])
@verify_token_middleware
def create_notification():
    """Create a new notification"""
    try:
        data = request.get_json()
        user_id = g.user_id

        to_user_id = data.get("to_user_id")
        content = data.get("content")
        notif_type = data.get("type")
        gen_code = data.get("gen_code")
        email = data.get("email")

        if not all([to_user_id, content, notif_type]):
            raise Api_Errors.create_error(400, "Missing required fields!")

        authorization = User.query.filter_by(user_id=user_id, gen_code=gen_code, email=email).first()
        
        if not authorization:
            raise Api_Errors.create_error(403, "Unauthorized: Invalid credentials!")

        recipient = User.query.filter_by(id=to_user_id).first()
        if not recipient:
            raise Api_Errors.create_error(404, "Recipient not found!")

        new_notification = Notification(
            id=str(uuid.uuid4()),
            from_user_id=user_id,
            to_user_id=to_user_id,
            content=content,
            type=notif_type,
            is_seen=False
        )
        db.session.add(new_notification)
        db.session.commit()

        return {"message": "Notification created successfully!",
                "notification": new_notification.auth_dict()}, 201

    except Exception as err:
        return Api_Errors.create_error(getattr(err, "status_code", 500), str(err))


