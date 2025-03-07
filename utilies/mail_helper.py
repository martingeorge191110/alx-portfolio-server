#!/usr/bin/env python3
import yagmail
import os
from engine.db_storage import db
from middlewares.error_handler import Api_Errors
from os import getenv


def send_code_mail(email, code, exp_date):
    GMAIL_USER = getenv('GMAIL_USER')
    GMAIL_PASS = getenv('GMAIL_PASS')

    yag = yagmail.SMTP(GMAIL_USER, GMAIL_PASS)

    subject = "Password Reset Request"
    html_content = f"""
        <h1>Password Reset</h1>
        <p>Generated Code</p>
        <h2>{code}</h2>
        <h3>Expire Date: {str(exp_date)}</h3>
    """

    try:
        yag.send(to=email, subject=subject, contents=html_content)
        return (True)
    except Exception as err:
        db.session.rollback()
        raise (Api_Errors.create_error(500, str(err)))
