#!/usr/bin/env python3

from models import db
import uuid


class CompanyOwner(db.Model):
    """company owner table"""
    __tablename__ = 'company_owners'

    rel_id = db.Column(db.String(291), unique=True, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(191), db.ForeignKey('users.id'), nullable=False)
    company_id = db.Column(db.String(191), db.ForeignKey('companies.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('owned_companies', lazy=True))
    company = db.relationship('Company', backref=db.backref('owners', lazy=True))

    def __repr__(self):
        return f"<Companyowner user_id={self.user_id}, company_id={self.company_id}>"
