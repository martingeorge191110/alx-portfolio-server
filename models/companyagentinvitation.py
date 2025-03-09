#!/usr/bin/env python3
"""model for implementation of invitation system"""


from middlewares.error_handler import Api_Errors
from models import db
from datetime import datetime, timedelta
import uuid

class CompanyAgentInvitaion(db.Model):
    
    __tablename__ = "company_agent_invitation"
    
    id = db.Column(db.String(291), unique=True, primary_key=True, default=lambda: str(uuid.uuid4()))
    inviter_id = db.Column(db.String(291), db.ForignKey('users.id'), nullable=False)
    invitee_id = db.Column(db.String(291), db.ForignKey('users.id'), nullable=False)
    company_id = db.Column(db.String(291), db.ForignKey('companies.id'), nullable=False)
    invite_status = db.Column(db.String(20), default="pending")
    created_at = created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def is_expired(self):
        """return invitation expiry date"""
        return datetime.utcnow() > self.expire_at
    
    def to_dict(self):
        """return convert stored data to dictionary"""
        return {
            "id": self.id,
            "inviter_id": self.inviter_id,
            "invitee_id": self.invitee_id,
            "company_id": self.company_id,
            "status": self.invite_status,
            "created_at": self.created_at,
            "expires_at": self.expires_at
        }
