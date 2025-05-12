# users/serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(
        source="user.email", read_only=True
    )  # Добавлено email
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    avatar_url = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField() 

    class Meta:
        model = Profile
        fields = [
            'id', 'username',
            'role', 'email',
            'role_display',
            'bio', 'avatar',
            'avatar_url',
            'is_blocked',
            'can_monetize_posts',
            'level_score',
            'levels_last_calculated_at',
            'followers_count',
            'following_count'
        ]
        read_only_fields = [
            'id', 'username',
            'role', 'email',
            'role_display',
            'is_blocked',
            'avatar_url',
            'followers_count',
            'following_count'
            ]
        # Сделаем 'avatar' write_only, если отдаем только 'avatar_url'
        extra_kwargs = {"avatar": {"write_only": True}}

    def get_avatar_url(self, obj):
        request = self.context.get("request")
        if obj.avatar and hasattr(obj.avatar, "url") and request:
            try:
                return request.build_absolute_uri(obj.avatar.url)
            except ValueError:
                return obj.avatar.url
        return "https://fitness-platform-media.s3.eu-north-1.amazonaws.com/media/default/default-avatar-icon.jpg"
    
    def get_followers_count(self, obj):
        if hasattr(obj.user, 'followers'):
            return obj.user.followers.count()
        return 0

    def get_following_count(self, obj):
        if hasattr(obj.user, 'following'):
            return obj.user.following.count()
        return 0

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'profile']
        read_only_fields = ['id', 'username', 'email'] # Email тоже лучше сделать read_only здесь

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        label="Confirm Password",
        style={"input_type": "password"},
    )
    role = serializers.ChoiceField(
        choices=Profile.Role.choices, write_only=True, required=True
    )

    class Meta:
        model = User
        fields = ["username", "password", "password2", "email", "role"]
        extra_kwargs = {
            # email делаем обязательным
            "email": {"required": True}
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError({"email": "Email already exists."})

        if User.objects.filter(username=attrs["username"]).exists():
            raise serializers.ValidationError({"username": "Username already exists."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            # Не передаем first_name и last_name
        )
        user.set_password(validated_data["password"])
        user.save()

        # Устанавливаем роль в профиле
        # Профиль создается автоматически сигналом post_save
        user.profile.role = validated_data["role"]
        user.profile.save()

        return user