from rest_framework import serializers
from django.conf import settings


class UserRegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256, required=True)
    email = serializers.EmailField(required=True)
    phone_number = serializers.CharField(required=True, max_length=11)
    password = serializers.CharField(required=True, write_only=True, style={"input_type": "password"}, max_length=30)

    def validate_email(self, value):
        if settings.USER_COLLECTION.find_one({"email": value}):
            raise serializers.ValidationError("email is duplicate")
        return value

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, style={"input_type": "password"})

class UserDetailSerializer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    phone_number = serializers.CharField()
    _id = serializers.CharField()