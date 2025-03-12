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
