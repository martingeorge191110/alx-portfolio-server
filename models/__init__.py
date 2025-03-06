#!/usr/bin/env python3
"""For creating the db engine variable"""
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

from models.user import User
