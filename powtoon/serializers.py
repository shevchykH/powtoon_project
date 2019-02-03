from rest_framework import serializers
from models import Powtoon


class PowtoonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Powtoon
        fields = ('id', 'name', 'content_json', 'owner')
        read_only_fields = ['user']


class SharePowtoonWithUserSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()

    class Meta:
        model = Powtoon
        fields = ('user_id',)
