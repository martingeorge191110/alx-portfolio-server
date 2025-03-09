#!/usr/bin/env python3

from models import db
import uuid


class CompanyDocs(db.Model):
    """company docs structured table"""
    __tablename__ = 'company_docs'

    id = db.Column(db.String(191), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = db.Column(db.String(191), db.ForeignKey('companies.id'), nullable=False)
    doc_url = db.Column(db.String(191), nullable=False)
    description = db.Column(db.Text, nullable=True)
    title = db.Column(db.String(191), nullable=False)

    company = db.relationship('Company', backref=db.backref('company_docs', lazy=True))

    def __repr__(self):
        return f"<CompanyGrowthRates company_id={self.company_id}, doc_url={self.doc_url}>"
