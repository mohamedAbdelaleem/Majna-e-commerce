from rest_framework.exceptions import APIException


class Conflict(APIException):
    status_code = 409
    default_code = "Conflict"
    default_detail = "Request conflicts with the current state of the resource"


class ServerError(APIException):
    status_code = 500
    default_detail = 'Server error. Please try again later.'
    default_code = 'Server Error'
