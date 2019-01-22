from django.contrib.auth.models import User
from rest_framework import permissions

ADMIN_GROUP = 'admin_group'


def check_permission(user, permission):
    pass


def check_group_permission(user, group_permission):
    user_groups = [group.name for group in user.groups.all()]
    return group_permission in user_groups


class UserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated():
            return False
        return True

    def has_object_permission(self, request, view, obj):
        user = User.objects.get(pk=request.user.id)
        if request.method == "GET" and check_group_permission(user=user, group_permission=ADMIN_GROUP):
            return True

        if request.method == "GET":
            return obj.user == request.user or \
                   request.user.id in [user.pk for user in obj.shared_with_users.all()]

        if request.method in ['PUT', 'DELETE']:
            return obj.user == request.user
