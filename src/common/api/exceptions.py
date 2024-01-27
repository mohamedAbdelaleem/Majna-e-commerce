from rest_framework.exceptions import APIException


class Conflict(APIException):
    status_code = 409
    default_code = "Conflict"
    default_detail = "Request conflicts with the current state of the resource"
