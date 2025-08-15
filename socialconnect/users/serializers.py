# users/serializers.py
from rest_framework import serializers
from .models import User, Follow

class UserSerializer(serializers.ModelSerializer):
    followers_count = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()
    posts_count = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = ("id", "username", "email", "role", "bio", "avatar_url", "website", "location", "is_email_verified", "privacy_setting", "followers_count", "following_count", "posts_count", "date_joined")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Handle potential URL validation issues
        if data.get('website') and not data['website'].startswith(('http://', 'https://')):
            data['website'] = 'https://' + data['website']
        if data.get('avatar_url') and not data['avatar_url'].startswith(('http://', 'https://')):
            data['avatar_url'] = 'https://' + data['avatar_url']
        
        # Ensure date_joined is in a consistent format
        if data.get('date_joined'):
            try:
                from django.utils import timezone
                # Convert to UTC and format as ISO string
                if hasattr(instance.date_joined, 'isoformat'):
                    data['date_joined'] = instance.date_joined.isoformat()
                else:
                    # Fallback for string dates
                    data['date_joined'] = str(instance.date_joined)
            except Exception as e:
                # If there's any error, keep the original value
                pass
        
        return data

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    website = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "role", "bio", "avatar_url", "website", "location")

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def validate_website(self, value):
        if value:
            # If the URL doesn't start with a protocol, add https://
            if not value.startswith(('http://', 'https://')):
                value = 'https://' + value
            # Basic URL validation
            if not value.startswith(('http://', 'https://')) or len(value) < 10:
                raise serializers.ValidationError("Enter a valid URL.")
        return value

    def create(self, validated_data):
        username = validated_data.get("username")
        email = validated_data["email"]
        if not username:
            username = email.split("@")[0]
        
        # Extract password and other fields
        password = validated_data.pop("password")
        username = validated_data.pop("username", username)
        email = validated_data.pop("email", email)
        
        # Create user with all provided fields
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **validated_data
        )
        return user

class ProfileUpdateSerializer(serializers.ModelSerializer):
    website = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = User
        fields = ("bio", "avatar_url", "website", "location", "privacy_setting")
        extra_kwargs = {
            'bio': {'required': False},
            'avatar_url': {'required': False},
            'location': {'required': False},
            'privacy_setting': {'required': False},
        }

    def validate_website(self, value):
        if value:
            # If the URL doesn't start with a protocol, add https://
            if not value.startswith(('http://', 'https://')):
                value = 'https://' + value
            # Basic URL validation
            if not value.startswith(('http://', 'https://')) or len(value) < 10:
                raise serializers.ValidationError("Enter a valid URL.")
        return value

class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ("id", "follower", "following", "created_at")
