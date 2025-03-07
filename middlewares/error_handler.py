#!/usr/bin/env python3
"""Error Handling Script for handling errors"""


class Api_Errors(Exception):
    """Api errors class"""
    def __init__(self, status_code, message):
        super().__init__(message)
        self.status_code = int(status_code) if isinstance(status_code, int) or str(status_code).isdigit() else 500
        self.status = "Failure" if 400 <= self.status_code <= 500 else "Server Error"
        self.message = message

    @staticmethod
    def create_error(status_code, message):
        if not isinstance(status_code, int):
            status_code = 500
        return (Api_Errors(status_code, message))

    @staticmethod
    def response_error(error):
        err = {
            "success": False,
            "message": error.message,
            "status": error.status,
        }
        return (err)
