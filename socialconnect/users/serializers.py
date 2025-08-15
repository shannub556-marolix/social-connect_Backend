# users/serializers.py
from rest_framework import serializers
from .models import User, Follow

class UserSerializer(serializers.ModelSerializer):
    followers_count = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()
    posts_count = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = ("id", "username", "email", "role", "bio", "avatar_url", "website", "location", "is_email_verified", "privacy_setting", "followers_count", "following_count", "posts_count")

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "role", "bio", "avatar_url")

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def create(self, validated_data):
        username = validated_data.get("username")
        email = validated_data["email"]
        if not username:
            username = email.split("@")[0]
        user = User(username=username, email=email, role=validated_data.get("role", "user"))
        user.set_password(validated_data["password"])
        user.save()
        return user

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("bio", "avatar_url", "website", "location", "privacy_setting")
        extra_kwargs = {
            'bio': {'required': False},
            'avatar_url': {'required': False},
            'website': {'required': False},
            'location': {'required': False},
            'privacy_setting': {'required': False},
        }

class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ("id", "follower", "following", "created_at")
