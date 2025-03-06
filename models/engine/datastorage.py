
#!/usr/bin/python3
""" Database Storage"""

import models
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(server):
    db.init_app(server)
    with server.app_context():
        db.create_all()
