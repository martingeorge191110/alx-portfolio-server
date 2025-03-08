#!/usr/bin/env python3

from models import db
import uuid


class Company(db.Model):
    """company data structure table"""
    __tablename__ = 'companies'

    id = db.Column(db.String(291), unique=True, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(191), nullable=False)
    description = db.Column(db.Text, nullable=False)
    contact_number = db.Column(db.String(191), nullable=False)
    contact_email = db.Column(db.String(191), unique=True, nullable=False)
    industry = db.Column(db.String(191), nullable=False)
    location = db.Column(db.String(191), nullable=False)
    web_link = db.Column(db.String(191), nullable=True)
    avatar = db.Column(db.String(500), nullable=True)
    stock_market = db.Column(db.Boolean, default=False, nullable=False)
    founder_year = db.Column(db.Integer, nullable=False)
    valuation = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    def __repr__(self):
        return f"<Company {self.contact_email}>"

    def to_dict(self):
        """Convert Company object to a dictionary"""
        return {
            "id": self.company_id,
            "name": self.name,
            "description": self.description,
            "contact number": self.contact_number,
            "contact email": self.contact_email,
            "industry": self.industry,
            "location": self.location,
            "web_link": self.web_link,
            "avatar":  self.avatar if self.avatar else None,
            "stock_market": self.stock_market,
            "founder_year": self.founder_year,
            "valuation": self.valuation,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def company_card_dict(self):
        """Function that retreive card of company info"""
        return {
            "id": self.company_id,
            "name": self.name,
            "contact email": self.contact_email,
            "industry": self.industry,
            "avatar":  self.avatar if self.avatar else None,
            "founder_year": self.founder_year,
            "valuation": self.valuation
        }
    
    def company_investment_card_dict(self, investment_deal=None):
        """Function that retreive card of company info"and deal"""
        data = {}
        data['company'] = self.company_card_dict()
        data['deal'] = investment_deal

        return (data)
