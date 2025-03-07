#!/usr/bin/env python3
"""For creating the db engine variable"""
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

from models.user import User
from models.company import Company
from models.notification import Notification
from models.investment_deal import InvestmentDeal
from models.company_owners import CompanyOwner
from models.company_growth_rate import CompanyGrowthRate
from models.company_docs import CompanyDocs
