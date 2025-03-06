#!/usr/bin/env python3
"""db_storage Script"""
from models import db
from flask_migrate import Migrate


class DBStorage:
    """Database Storage Engine"""
    
    def __init__(self, app):
        """Initialize db storage, with migrations
        for any changes in development"""
        self.app = app
        db.init_app(app)
        self.migrate = Migrate(app, db)

    def create_tables(self):
        """Create tables if they don’t exist"""
        with self.app.app_context():
            db.create_all()
