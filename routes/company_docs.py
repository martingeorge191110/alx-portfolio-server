#!/usr/bin/env python3
"""routes for documents handling"""
from flask import Blueprint, request, g, jsonify
from middlewares.verify_token import verify_token_middleware
from middlewares.error_handler import Api_Errors
from models.user import User
from models.company_docs import CompanyDocs
from models.company_owners import CompanyOwner
from models import db
from routes.company_route import company_route
import uuid
from models.company import Company
from datetime import datetime

company_docs_route = company_route = Blueprint('company_docs', __name__, url_prefix='/company/document')


@company_docs_route.route("/<string:company_id>", methods=["POST"])
@verify_token_middleware
def document_upload(company_id):
    """upload documents API"""
    user_id = g.user_id

    try:
        data = request.get_json()
        doc_url = data.get("doc_url")
        title = data.get("title")
        description = data.get("description", "")
        
        user = User.query.filter_by(id = user_id).first()
        if not user:
            raise (Api_Errors.create_error(404, "User is not found!"))

        authorization = CompanyOwner.query.filter_by(user_id=user_id, company_id=company_id, active=True).first()
        
        if not authorization:
            raise Api_Errors.create_error(403, "Unauthorized to manage documents for this company")

        if not company_id or not doc_url or not title:
            raise Api_Errors.create_error(400, "Company ID, document URL, and title are required!")

        new_document = CompanyDocs(
            id=str(uuid.uuid4()),
            company_id=company_id,
            doc_url=doc_url,
            title=title,
            description=description
        )

        db.session.add(new_document)
        db.session.commit()

        return jsonify({"message": "Document uploaded successfully", "success": True, "document": new_document.to_dict()}), 201
    except Exception as err:
        db.session.rollback()
        raise Api_Errors.create_error(getattr(err, "status_code", 500), str(err))

@company_docs_route.route('/<string:document_id>', methods=['DELETE'])
@verify_token_middleware
def delete_company_document(document_id):
    """Deletes a specific company document."""
    try:
        user_id = g.user_id
        data = request.get_json()
        company_id = data.get("company_id")

        document = CompanyDocs.query.filter_by(id=document_id).first()
        
        authorization = CompanyOwner.query.filter_by(user_id=user_id, company_id=company_id, active=True).first()
        if not authorization:
            raise Api_Errors.create_error(403, "Unauthorized to manage documents for this company")        

        if not document:
            raise Api_Errors.create_error(404, "Document not found!")

        db.session.delete(document)
        db.session.commit()

        return jsonify({"message": "Document deleted successfully", "success": True}), 200
    except Exception as err:
        db.session.rollback()
        raise Api_Errors.create_error(getattr(err, "status_code", 500), str(err))

@company_docs_route.route('/<string:company_id>', methods=['GET'])
@verify_token_middleware
def get_specific_company_doc(company_id):
    user_id = g.user_id

    try:
        user = User.query.filter_by(id = user_id).first()
        if not user:
            raise (Api_Errors.create_error(404, "User is not found!"))
        
        company = Company.query.filter_by(id = company_id).first()
        if not company:
            raise (Api_Errors.create_error(404, "Company is not found!"))
        
        relationship = CompanyOwner.query.filter_by(user_id = user_id, company_id = company_id, active = True).first()
        user_data = user.auth_dict()
        if not relationship and (not user_data['paid'] or (user_data['paid'] and user_data['subis_end_date'] < datetime.utcnow())):
            raise (Api_Errors.create_error(403, "You have not authorization to retreive the data!"))

        all_docs = CompanyDocs.query.filter_by(company_id = company_id).all()
        docs_list = []
        for doc in all_docs:
            docs_list.append(doc.to_dict())

        return jsonify({"message": "Documents Retreived successfully", "success": True, "documents": docs_list}), 200
    except Exception as err:
        db.session.rollback()
        raise Api_Errors.create_error(getattr(err, "status_code", 500), str(err))
