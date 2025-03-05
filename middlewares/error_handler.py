#!/usr/bin/env python3
"""Error Handling Script for handling errors"""


class Api_Errors(Exception):
    """Api errors class"""
    def __init__(self, status_code, message):
        super().__init__(message)
        self.status_code = status_code if status_code else 500
        self.status = "Failure" if 400 <= status_code <= 500 else "Server Error"
        self.message = message

    @staticmethod
    def create_error(status_code, message):
        return (Api_Errors(status_code, message))

    @staticmethod
    def response_error(error):
        err = {
            "success": False,
            "message": error.message,
            "status": error.status,
        }
        return (err)
