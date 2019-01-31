from django.contrib.auth.models import User
from rest_framework import permissions, status
from rest_framework.response import Response


CAN_GET_POWTOON = 'can_get_powtoon'
CAN_SHARE_POWTOON = "can_share_powtoon"
CAN_DELETE_OWN_POWTOON = "can_delete_own_powtoon"
CAN_VIEW_OWN_POWTOON_DETAIL = "can_view_own_powtoon_detail"
CAN_VIEW_SHARED_POWTOON_DETAIL = "can_view_shared_powtoon_detail"
CAN_UPDATE_OWN_POWTOON = "can_update_own_powtoon"
CAN_GET_LIST_OWN_POWTOONS = "can_get_list_own_powtoons"
CAN_GET_LIST_SHARED_WITH_HIM_POWTOONS = "can_get_list_shared_with_him_potoons"

CAN_VIEW_NOT_OWN_POWTOON = "can_view_not_own_powtoon"
CAN_VIEW_NOT_SHARED_POWTOON = "can_view_not_shared_powtoon"


ALL_PERMISSIONS = [
    CAN_SHARE_POWTOON,
    CAN_DELETE_OWN_POWTOON,
    CAN_VIEW_SHARED_POWTOON_DETAIL,
    CAN_UPDATE_OWN_POWTOON,
    CAN_GET_LIST_OWN_POWTOONS,
    CAN_GET_LIST_SHARED_WITH_HIM_POWTOONS,

    CAN_VIEW_NOT_OWN_POWTOON,
    CAN_VIEW_NOT_SHARED_POWTOON
]

USER_GROUP_PERMISSIONS = [
    CAN_SHARE_POWTOON,
    CAN_DELETE_OWN_POWTOON,
    CAN_VIEW_SHARED_POWTOON_DETAIL,
    CAN_UPDATE_OWN_POWTOON,
    CAN_GET_LIST_OWN_POWTOONS,
    CAN_GET_LIST_SHARED_WITH_HIM_POWTOONS,
]


ADMIN_GROUP_PERMISSIONS = [

    CAN_SHARE_POWTOON,
    CAN_DELETE_OWN_POWTOON,
    CAN_VIEW_SHARED_POWTOON_DETAIL,
    CAN_UPDATE_OWN_POWTOON,
    CAN_GET_LIST_OWN_POWTOONS,
    CAN_GET_LIST_SHARED_WITH_HIM_POWTOONS,

    CAN_VIEW_NOT_OWN_POWTOON,
    CAN_VIEW_NOT_SHARED_POWTOON
]


def check_permission(user, perm_code):
    if user.has_perm(perm_code):
        return True
    return Response(status=status.HTTP_403_FORBIDDEN)


class SharePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == "POST":
            return obj.user == request.user


class PowToonDetailPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == "GET":
            user = User.objects.get(pk=request.user.id)
            if obj.shared_with_users.filter(username=user.username).count():
                return check_permission(user, CAN_VIEW_SHARED_POWTOON_DETAIL)
            return check_permission(user, CAN_VIEW_NOT_SHARED_POWTOON) or \
                   check_permission(user, CAN_VIEW_NOT_OWN_POWTOON)

        if request.method in ["GET", "PUT", "DELETE"]:
            return request.user == obj.user

