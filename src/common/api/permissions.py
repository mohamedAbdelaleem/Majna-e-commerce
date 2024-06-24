from rest_framework import permissions


class DistributorsOnly(permissions.BasePermission):

    message = "Only Distributors can perform this action"

    def has_permission(self, request, view):

        return request.user.is_distributor 


class ReviewersOnly(permissions.BasePermission):

    message = "Only Reviewers can perform this action"

    def has_permission(self, request, view):

        return request.user.is_reviewer

class CustomersOnly(permissions.BasePermission):

    message = "Only Customers can perform this action"

    def has_permission(self, request, view):

        return request.user.is_customer

      