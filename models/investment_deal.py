#!/usr/bin/env python3

from models import db
from enum import Enum as PyEnum
import uuid


class DealStatus(PyEnum):
    Rejected = 'Rejected'
    Pending = 'Pending'
    Accepted = 'Accepted'

class InvestmentDeal(db.Model):
    """investment deals structure table"""
    __tablename__ = 'investment_deals'

    id = db.Column(db.String(291), unique=True, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = db.Column(db.String(191), db.ForeignKey('companies.id'), nullable=False)
    user_id = db.Column(db.String(191), db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    equity_percentage = db.Column(db.Float, nullable=True)
    deal_status = db.Column(db.Enum(DealStatus), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    user = db.relationship('User', backref=db.backref('investment_deals', lazy=True))
    company = db.relationship('Company', backref=db.backref('investment_deals', lazy=True))

    def __repr__(self):
        return f"<Investment_Id={self.id}>"

    def to_dict(self):
        """Convert investment deals object to a dictionary"""
        return {
            "id": self.id,
            "company_id": self.company_id,
            "user_id": self.user_id,
            "amount": self.amount,
            "equity_percentage": self.equity_percentage,
            "deal_status": self.deal_status if isinstance(self.deal_status, str) else self.deal_status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
