from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from powtoon.permissions import UserPermission, ADMIN_GROUP, check_group_permission
from powtoon.models import Powtoon
from powtoon.serializers import PowtoonSerializer, SharePowtoonWithUserSerializer


def get_shared_powtoons(user_pk):
    powtoon_qs = Powtoon.objects.prefetch_related("shared_with_users")
    powtoons = set()
    for powtoon in powtoon_qs:
        users = [user.pk for user in powtoon.shared_with_users.all()]
        if user_pk in users:
            powtoons.add(powtoon)
    return powtoons


class PowtoonListView(generics.ListCreateAPIView):
    permission_classes = [UserPermission]
    serializer_class = PowtoonSerializer

    def get_queryset(self):
        if self.request.method == "GET":
            shared_powtoons = get_shared_powtoons(self.request.user.id)
            own_powtoons = set(Powtoon.objects.filter(user=self.request.user))
            return own_powtoons.union(shared_powtoons)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PowtoonDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Powtoon.objects.all()
    serializer_class = PowtoonSerializer
    permission_classes = [UserPermission]


class SharePowtoonView(generics.CreateAPIView):
    queryset = Powtoon.objects.all()
    serializer_class = SharePowtoonWithUserSerializer
    permission_classes = [UserPermission]

    def check_object_permissions(self, request, obj):
        return check_group_permission(obj.user, ADMIN_GROUP)

    def post(self, request, *args, **kwargs):
        powtoon = self.get_object()
        self.check_object_permissions(request, powtoon)
        if int(request.data['user_id']) == powtoon.user.pk:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User.objects.filter(
            pk=self.kwargs['user_id']))
        powtoon.shared_with_users.add(user)
        return Response(status=status.HTTP_201_CREATED)


class SharedPowtoonList(generics.ListAPIView):
    serializer_class = PowtoonSerializer
    permission_classes = [UserPermission]

    def get_queryset(self):
        return get_shared_powtoons(self.request.user.id)
