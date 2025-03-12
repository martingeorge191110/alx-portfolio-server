# #!/usr/bin/env python3
# """routes for notification handling"""

# from flask import request, g, Blueprint
# from middlewares.error_handler import Api_Errors
# from middlewares.verify_token import verify_token_middleware
# from models.user import User
# from models import db
# import uuid

# notification_route = Blueprint("notification", __name__, url_prefix="/notification")


# @notification_route.route("/", methods=["GET"])
# def get_notification():
#     """retrieve notification"""
#     try:
#         user_id = g.user_id
#         data = request.get_json()
#         from_user_id = data.get("from_user_id")
#         to_user_id = data.get("to_user_id")


# /api/notification: 
# GET: Retrieves notifications with lazy loading.
# POST: Creates a new notification from one user to another.
# PUT: Updates the content of an existing notification.
# DELETE: Deletes an existing notification.
