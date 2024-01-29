from rest_framework import permissions


class DistributorsOnly(permissions.BasePermission):

    message = "Only Distributors can perform this action"

    def has_permission(self, request, view):

        return request.user.is_distributor        