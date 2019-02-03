from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from powtoon.permissions import PowToonDetailPermission, SharePermission
from powtoon.models import Powtoon
from powtoon.serializers import PowtoonSerializer, SharePowtoonWithUserSerializer


def get_shared_powtoons(user_pk):
    return Powtoon.objects.filter(shared_with_users__pk=user_pk)


class PowtoonListView(generics.ListCreateAPIView):
    serializer_class = PowtoonSerializer

    def get_queryset(self):
        if self.request.method == "GET":
            shared_powtoons = get_shared_powtoons(user_pk=self.request.user.id)
            own_powtoons = Powtoon.objects.filter(user=self.request.user)
            return (own_powtoons | shared_powtoons).distinct()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PowtoonDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Powtoon.objects.all()
    serializer_class = PowtoonSerializer
    permission_classes = [IsAuthenticated, PowToonDetailPermission]


class SharePowtoonView(generics.CreateAPIView):
    queryset = Powtoon.objects.all()
    serializer_class = SharePowtoonWithUserSerializer
    permission_classes = [IsAuthenticated, SharePermission]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        powtoon = self.get_object()
        serializer.is_valid(raise_exception=True)
        if serializer["user_id"] == powtoon.user.pk:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User.objects.filter(
            pk=serializer.data["user_id"]))
        powtoon.shared_with_users.add(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SharedPowtoonList(generics.ListAPIView):
    serializer_class = PowtoonSerializer

    def get_queryset(self):
        return get_shared_powtoons(self.request.user.id)
