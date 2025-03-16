#!/usr/bin/env python3
"""routes for notification handling"""

from flask import request, g, Blueprint, jsonify
from middlewares.error_handler import Api_Errors
from middlewares.verify_token import verify_token_middleware
from models.user import User
from models.notification import Notification
from models import db
import uuid
from sqlalchemy.sql import label
from models.company import Company
from models.company_owners import CompanyOwner
from models.investment_deal import InvestmentDeal, DealStatus


notification_route = Blueprint("notification", __name__, url_prefix="/notification")


@notification_route.route("/", methods=["GET"])
@verify_token_middleware
def get_notification():
    """retrieve notification with pagination"""
    try:
        user_id = g.user_id

        user = User.query.filter_by(id = user_id).first()
        if not user:
            raise Api_Errors.create_error(404, "User is not found!")

        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 10, type=int)

        owner_notifications = (
            db.session.query(CompanyOwner, User, Company)
            .join(User, CompanyOwner.user_id == User.id)
            .join(Company, CompanyOwner.company_id == Company.id)
            .filter(CompanyOwner.user_id == user_id, CompanyOwner.active == False)
            .all()
        )

        result = [
            {
                "rel_id": owner.rel_id,
                "user_id": user.id,
                "f_n": user.f_n,
                "avatar": user.avatar,
                "company_id": company.id,
                "company_name": company.name,
                "company_avatar": company.avatar,
                "user_role": owner.user_role,
                "active": owner.active,
            }
            for owner, user, company in owner_notifications
        ]

        unseen_notifications = (
            Notification.query
            .join(User, User.id == Notification.from_user_id)
            .filter(Notification.to_user_id == user_id, Notification.is_seen == False)
            .order_by(Notification.created_at.desc())
            .add_columns(
                Notification.id ,
                Notification.content, 
                Notification.created_at,
                Notification.is_seen,
                User.f_n, 
                User.l_n, 
                User.avatar,
                User.email
            )
        )

        # Get seen notifications after unseen
        seen_notifications = (
            Notification.query
            .join(User, User.id == Notification.from_user_id)
            .filter(Notification.to_user_id == user_id, Notification.is_seen == True)
            .order_by(Notification.created_at.desc())
            .add_columns(
                Notification.id,
                Notification.content, 
                Notification.created_at,
                Notification.is_seen,
                User.f_n, 
                User.l_n, 
                User.avatar,
                User.email
            )
        )

        # Merge unseen and seen notifications
        all_notifications = unseen_notifications.union_all(seen_notifications)

        # Apply pagination
        notifications = all_notifications.paginate(page=page, per_page=limit, error_out=False)

        notifications_data = [
        {
            "id": n.id,
            "content": n.content,
            "is_seen": n.is_seen,
            "created_at": n.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "user": {
                "email": n.email,
                "f_n": n.f_n,
                "l_n": n.l_n,
                "avatar": n.avatar
            }
        }
        for n in notifications
        ]

        return jsonify({
            "success": True,
            "notifications": notifications_data,
            "owner_notifications": result,
            "page": page,
            "total_pages": notifications.pages,
            "total_notifications": notifications.total
        }), 200

    except Exception as err:
        db.session.rollback()
        raise Api_Errors.create_error(getattr(err, "status_code", 500), str(err))

@notification_route.route("/<string:to_user_id>", methods=["POST"])
@verify_token_middleware
def create_notification(to_user_id):
    """Create a new notification"""
    try:
        data = request.get_json()
        user_id = g.user_id

        content = data.get("content")
        notif_type = data.get("type", "general")

        if not all([to_user_id, content, notif_type]):
            raise Api_Errors.create_error(400, "Missing required fields!")

        sender = User.query.filter_by(id=user_id).first()
        if not sender:
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

        return (jsonify(
            {
                "message": "Notification created successfully!",
                "success": True,
                "notification": new_notification.auth_dict()
            }), 201)

    except Exception as err:
        db.session.rollback()
        raise Api_Errors.create_error(getattr(err, "status_code", 500), str(err))

@notification_route.route("/<string:notification_id>", methods=["PUT"])
@verify_token_middleware
def update_notification(notification_id):
    """Update the content of an existing notification"""
    try:
        user_id = g.user_id

        notification = Notification.query.filter_by(id=notification_id).first()
        if not notification:
            raise Api_Errors.create_error(404, "Notification not found!")

        if notification.to_user_id != user_id:
            raise Api_Errors.create_error(403, "Unauthorized: You can only update your own notifications!")

        notification.is_seen = True

        db.session.commit()

        return (jsonify({
            "message": "Notification updated successfully!",
            "success": True
        }), 200)

    except Exception as err:
        db.session.rollback()
        raise Api_Errors.create_error(getattr(err, "status_code", 500), str(err))


@notification_route.route("/<string:notification_id>", methods=["DELETE"])
@verify_token_middleware
def delete_notification(notification_id):
    """Delete a notification"""
    try:
        user_id = g.user_id
        
        notification = Notification.query.filter_by(id=notification_id).first()
        if not notification:
            raise Api_Errors.create_error(404, "Notification not found!")

        if notification.from_user_id != user_id and notification.to_user_id != user_id:
            raise Api_Errors.create_error(403, "Unauthorized: You can only delete your own notifications!")

        db.session.delete(notification)
        db.session.commit()

        return {"message": "Notification deleted successfully!"}, 200

    except Exception as err:
        return Api_Errors.create_error(getattr(err, "status_code", 500), str(err))
