#!/usr/bin/env python3

from models import db
import uuid
from cryptography.fernet import Fernet
from os import getenv


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
    valuation = db.Column(db.Float, nullable=False)
    paid = db.Column(db.Boolean, default=False)
    subis_end_date = db.Column(db.DateTime, nullable=True)
    subis_start_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    def __repr__(self):
        return f"<Company {self.contact_email}>"

    def to_dict(self):
        """Convert Company object to a dictionary"""
        return {
            "id": self.id,
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
        f = Fernet(getenv('FERNET_KEY'))

        return {
            "id": self.id,
            "name": self.name,
            "contact email": self.contact_email,
            "industry": self.industry,
            "avatar":  self.avatar if self.avatar else None,
            "founder_year": self.founder_year,
            "valuation":  self.valuation,
            "location": self.location
        }

    def company_investment_card_dict(self, investment_deal=None):
        """Function that retreive card of company info"and deal"""
        data = {}
        data['company'] = self.company_card_dict()
        data['deal'] = investment_deal.to_dict() if investment_deal else None

        return (data)

    def create_company_db(data_body):
        """Function creates a new company db in Company class"""

        new_company = Company()

        new_company.name = data_body['name']
        new_company.description = data_body['description']
        new_company.contact_email = data_body['contact_email']
        new_company.contact_number = data_body['contact_number']
        new_company.industry = data_body['industry']
        new_company.location = data_body['location']
        new_company.stock_market = data_body['stock_market']
        new_company.founder_year = data_body['founder_year']
        new_company.valuation = data_body['valuation']

        return (new_company)
