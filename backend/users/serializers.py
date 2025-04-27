# users/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'username', 'role', 'role_display', 'bio', 'avatar', 'is_blocked']
        # Редактировать можно только bio и avatar через этот сериализатор
        read_only_fields = ['id', 'username', 'role', 'role_display', 'is_blocked']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, label='Confirm Password', style={'input_type': 'password'})
    role = serializers.ChoiceField(choices=Profile.Role.choices, write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'email', 'role']
        extra_kwargs = {
            # email делаем обязательным
            'email': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        if User.objects.filter(email=attrs['email']).exists():
             raise serializers.ValidationError({"email": "Email already exists."})

        if User.objects.filter(username=attrs['username']).exists():
             raise serializers.ValidationError({"username": "Username already exists."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email']
            # Не передаем first_name и last_name
        )
        user.set_password(validated_data['password'])
        user.save()

        # Устанавливаем роль в профиле
        # Профиль создается автоматически сигналом post_save
        user.profile.role = validated_data['role']
        user.profile.save()

        return user