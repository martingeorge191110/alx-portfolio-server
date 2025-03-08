#!/usr/bin/env python3

from models import db
import uuid


class CompanyGrowthRate(db.Model):
    """company growth rates structured table"""
    __tablename__ = 'company_growth_ratees'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = db.Column(db.String(191), db.ForeignKey('companies.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    profit = db.Column(db.String(191), nullable=False)

    company = db.relationship('Company', backref=db.backref('growth_rates', Lazy=True))

    def __repr__(self):
        return f"<CompanyGrowthRates company_id={self.company_id}, year={self.year}, profit={self.profit}>"
