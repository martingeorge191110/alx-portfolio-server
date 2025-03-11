#!/usr/bin/env python3
from middlewares.error_handler import Api_Errors
from datetime import datetime
import validators
from models.company import Company
from models import db


class CompanyValidation:
    """Class is holding company validation functions"""

    @staticmethod
    def register_validation(data_body):
        """"""
        items = ['name', 'description', 'contact_number', 'contact_email', 'industry', 'location'
                 , 'user_role']
        for i in items:
            if i not in data_body or type(data_body[i]) is not str or data_body[i].strip() == '':
                raise (Api_Errors.create_error(400, f"{i} is required and must be String!"))

        if not validators.email(data_body['contact_email']):
            raise (Api_Errors.create_error(400, "contact_email address is not valid!"))

        if Company.query.filter_by(contact_email = data_body['contact_email']).first():
            raise (Api_Errors.create_error(400, f"contact_email address is already exists!"))

        if 'founder_year' not in data_body or type(data_body['founder_year']) is not int:
            raise (Api_Errors.create_error(400, "founder_year is required and must be Integer founder_year!"))

        if 'valuation' not in data_body or type(data_body['valuation']) is not int:
            raise (Api_Errors.create_error(400, "valuation is required and must be Integer!"))

        data_body['valuation'] = float(data_body['valuation'])

        if 'stock_market' not in data_body or type(data_body['stock_market']) is not bool:
            raise (Api_Errors.create_error(400, "stock_market is required and must be datetime!"))

        return (True)

    @staticmethod
    def company_id_validation(company_id):
        try:
            if not company_id or str(company_id).strip() == '':
                raise (Api_Errors.create_error(400, "company_id is not defined!"))
            
            company = Company.query.filter_by(id = company_id).first()
            if not company:
                raise (Api_Errors.create_error(404, "company is not found!"))

            return (company.to_dict())
        except Exception as err:
            raise (Api_Errors.create_error(getattr(err, "status_code", 500), str(err)))
        

    @staticmethod
    def growth_rates_validation(data_body):
        """"""
        if type(data_body) is not list:
            raise (Api_Errors.create_error(400, "DaTa must be an array of dicts!"))

        for ele in data_body:
            if 'year' not in ele or 'profit' not in ele:
                raise (Api_Errors.create_error(400, "Profit and year must be included!"))
            if type(ele['year']) is not int or type(ele['profit']) is not int:
                raise (Api_Errors.create_error(400, "Profit and year must be float!"))
            ele['profit'] = float(ele['profit'])

        return (True)
