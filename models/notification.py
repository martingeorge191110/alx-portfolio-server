#!/usr/bin/env python3
from models import db
from enum import Enum as PyEnum
import uuid


class NotificationType(PyEnum):
    Investment_update = 'Investment_update'
    deal_status = 'deal_status'
    subscription = 'subscription'
    general = 'general'

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.String(291), primary_key=True, default=lambda: str(uuid.uuid4()))
    from_user_id = db.Column(db.String(291), db.ForeignKey('users.id'), nullable=False)
    to_user_id = db.Column(db.String(291), db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.Enum(NotificationType), nullable=False)
    is_seen = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    from_user = db.relationship('User', foreign_keys=[from_user_id],
                                backref=db.backref('sent_notifications', lazy=True))
    to_user = db.relationship('User', foreign_keys=[to_user_id],
                              backref=db.backref('received_notifications', lazy=True))

    def __repr__(self):
        return f"<notifcation_id {self.id}>"

    def auth_dict(self):
        """Convert the notifications object to a dictionary for auth process"""
        return {
            "id": self.id,
            "from_user_id": self.from_user_id,
            "to_user_id": self.to_user_id,
            "type": self.type.value,
            "content": self.content,
            "is_seen": self.is_seen,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
