# users/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import RegisterSerializer, UserSerializer, ProfileUpdateSerializer, FollowSerializer
from .models import User, EmailVerificationToken, PasswordResetToken, Follow
from .utils.email import send_verification_email, send_password_reset_email
from .utils.avatar import process_avatar_upload
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # create verification token
        token_obj = EmailVerificationToken.objects.create(user=user)
        send_verification_email(user, token_obj.token)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        token = request.query_params.get("token")
        if not token:
            return Response({"detail": "Token required."}, status=400)
        try:
            obj = EmailVerificationToken.objects.get(token=token)
        except EmailVerificationToken.DoesNotExist:
            return Response({"detail": "Invalid token"}, status=400)
        if obj.expires_at < timezone.now():
            return Response({"detail": "Token expired."}, status=400)
        u = obj.user
        u.is_email_verified = True
        u.save()
        obj.delete()
        return Response({"detail": "Email verified."})

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        identifier = request.data.get("identifier") or request.data.get("email") or request.data.get("username")
        password = request.data.get("password")
        if not identifier or not password:
            return Response({"detail": "Provide identifier and password"}, status=400)
        try:
            if "@" in identifier:
                user = User.objects.get(email__iexact=identifier)
            else:
                user = User.objects.get(username__iexact=identifier)
        except User.DoesNotExist:
            return Response({"detail": "Invalid credentials"}, status=401)
        if not user.check_password(password):
            return Response({"detail": "Invalid credentials"}, status=401)
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data
        })

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token required."}, status=400)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return Response({"detail": "Invalid token."}, status=400)
        return Response(status=status.HTTP_205_RESET_CONTENT)

# Password reset request
class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"detail": "Email required."}, status=400)
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # don't reveal existence
            return Response({"detail": "If an account exists we sent an email."})
        token = PasswordResetToken.objects.create(user=user)
        send_password_reset_email(user, token.token)
        return Response({"detail": "If an account exists we sent an email."})

class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        token = request.data.get("token")
        new_password = request.data.get("new_password")
        if not token or not new_password:
            return Response({"detail": "Token and new_password required."}, status=400)
        try:
            obj = PasswordResetToken.objects.get(token=token)
        except PasswordResetToken.DoesNotExist:
            return Response({"detail": "Invalid token."}, status=400)
        if obj.expires_at < timezone.now():
            return Response({"detail": "Token expired."}, status=400)
        user = obj.user
        user.set_password(new_password)
        user.save()
        obj.delete()
        return Response({"detail": "Password updated."})

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        old = request.data.get("old_password")
        new = request.data.get("new_password")
        if not user.check_password(old):
            return Response({"detail": "Old password incorrect."}, status=400)
        user.set_password(new)
        user.save()
        return Response({"detail": "Password changed."})

class UserProfileView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Check privacy settings
        if user.privacy_setting == "private":
            if not request.user.is_authenticated or request.user.id != user.id:
                return Response({"detail": "Profile is private."}, status=status.HTTP_403_FORBIDDEN)
        elif user.privacy_setting == "followers_only":
            if not request.user.is_authenticated:
                return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
            if request.user.id != user.id and not Follow.objects.filter(follower=request.user, following=user).exists():
                return Response({"detail": "Profile is only visible to followers."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = UserSerializer(user)
        return Response(serializer.data)

class MyProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)
    
    def patch(self, request):
        return self.put(request)

class FollowUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        if request.user.id == user_id:
            return Response({"detail": "Cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_to_follow = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )
        
        if created:
            return Response({"detail": f"You are now following {user_to_follow.username}."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": f"You are already following {user_to_follow.username}."}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, user_id):
        try:
            follow = Follow.objects.get(follower=request.user, following_id=user_id)
            follow.delete()
            return Response({"detail": "Unfollowed successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            return Response({"detail": "You are not following this user."}, status=status.HTTP_400_BAD_REQUEST)

class FollowersListView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Check privacy settings
        if user.privacy_setting == "private":
            if not request.user.is_authenticated or request.user.id != user.id:
                return Response({"detail": "Profile is private."}, status=status.HTTP_403_FORBIDDEN)
        elif user.privacy_setting == "followers_only":
            if not request.user.is_authenticated:
                return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
            if request.user.id != user.id and not Follow.objects.filter(follower=request.user, following=user).exists():
                return Response({"detail": "Profile is only visible to followers."}, status=status.HTTP_403_FORBIDDEN)
        
        followers = user.followers.all()
        serializer = FollowSerializer(followers, many=True)
        return Response(serializer.data)

class FollowingListView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Check privacy settings
        if user.privacy_setting == "private":
            if not request.user.is_authenticated or request.user.id != user.id:
                return Response({"detail": "Profile is private."}, status=status.HTTP_403_FORBIDDEN)
        elif user.privacy_setting == "followers_only":
            if not request.user.is_authenticated:
                return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
            if request.user.id != user.id and not Follow.objects.filter(follower=request.user, following=user).exists():
                return Response({"detail": "Profile is only visible to followers."}, status=status.HTTP_403_FORBIDDEN)
        
        following = user.following.all()
        serializer = FollowSerializer(following, many=True)
        return Response(serializer.data)

class DiscoverUsersView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Get all users to discover with follow status (privacy is enforced at profile level)
        """
        try:
            # Get users that the current user follows
            following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
            
            # Get all users except current user
            all_users = User.objects.filter(
                is_active=True
            ).exclude(
                id=request.user.id
            ).order_by('-date_joined')[:20]  # Limit to 20 users
            
            # Create response with follow status
            users_data = []
            for user in all_users:
                user_data = UserSerializer(user).data
                user_data['is_following'] = user.id in following_users
                users_data.append(user_data)
            
            return Response(users_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AvatarUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if 'avatar' not in request.FILES:
            return Response({"detail": "Avatar file is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        avatar_file = request.FILES['avatar']
        
        try:
            # Process avatar upload
            avatar_url = process_avatar_upload(avatar_file, request.user.id)
            
            # Update user's avatar_url
            request.user.avatar_url = avatar_url
            request.user.save()
            
            return Response({
                "detail": "Avatar uploaded successfully.",
                "avatar_url": avatar_url
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
