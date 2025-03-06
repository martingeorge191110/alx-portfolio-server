#!/usr/bin/env python3
from models import db
from datetime import datetime
from enum import Enum as PyEnum
import uuid


class UsersTypes(PyEnum):
    Investor = 'Investor'
    Business = 'Business'

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(291), primary_key=True, default=lambda: str(uuid.uuid4()))
    f_n = db.Column(db.String(291), nullable=False)
    l_n = db.Column(db.String(291), nullable=False)
    email = db.Column(db.String(291), unique=True, nullable=False)
    password = db.Column(db.String(291), nullable=False)
    gen_code = db.Column(db.String(291), nullable=True)
    expired_date_gen_code = db.Column(db.DateTime, nullable=True)
    avatar = db.Column(db.String(291), nullable=True)
    nationality = db.Column(db.String(291), nullable=True)
    user_type = db.Column(db.Enum(UsersTypes), nullable=False)
    paid = db.Column(db.Boolean, default=False, nullable=False)
    subis_end_date = db.Column(db.DateTime, nullable=True)
    subis_start_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    def __repr__(self):
        return f"<User {self.email}>"

    def auth_dict(self):
        """Convert the User object to a dictionary for auth process"""
        return {
            "id": self.id,
            "f_n": self.f_n,
            "l_n": self.l_n,
            "email": self.email,
            "user_type": self.user_type.value,
            "avatar": self.avatar,
            "nationality": self.nationality,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
