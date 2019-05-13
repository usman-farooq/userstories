'''
Created on May 12, 2019

@author: usman.farooq
'''
from rest_framework.permissions import BasePermission, IsAuthenticated

class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_superuser:
            return True
        return False

class IsOwnerOrSuperUser(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or request.user == obj.created_by