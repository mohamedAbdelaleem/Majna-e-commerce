from rest_framework.permissions import BasePermission


class IsSameUser(BasePermission):

    def has_permission(self, request, view):
        
        if request.user and request.user.is_authenticated:
            pk =  view.kwargs["pk"]
            return request.user.pk == pk


