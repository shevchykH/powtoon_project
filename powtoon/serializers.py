from rest_framework import serializers
from models import Powtoon


class PowtoonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Powtoon
        fields = ('id', 'name', 'content_json')
        read_only_fields = ['user']


class SharePowtoonWithUserSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(min_value=1)

    class Meta:
        model = Powtoon
        fields = ('user_id',)
