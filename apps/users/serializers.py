from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Profile, Role


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


class ProfileSerializer(serializers.ModelSerializer):
    # URL CDN Cloudinary de l'avatar
    avatar = serializers.SerializerMethodField()

    class Meta:
        model  = Profile
        fields = ["avatar", "city", "address", "bio"]

    def get_avatar(self, obj):
        return obj.avatar.url if obj.avatar else None


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer d'écriture — accepte un fichier image pour l'avatar."""
    class Meta:
        model  = Profile
        fields = ["avatar", "city", "address", "bio"]


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model  = User
        fields = ["id", "phone", "full_name", "role",
                  "phone_verified", "date_joined", "profile"]
        read_only_fields = ["id", "phone", "phone_verified", "date_joined"]


class RegisterSerializer(serializers.ModelSerializer):
    password         = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    role             = serializers.ChoiceField(choices=Role.choices, default=Role.BUYER)

    class Meta:
        model  = User
        fields = ["phone", "full_name", "role", "password", "password_confirm"]

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Ce numéro est déjà utilisé.")
        return value

    def validate(self, data):
        if data["password"] != data.pop("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Les mots de passe ne correspondent pas."})
        return data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    phone    = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["phone"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Numéro ou mot de passe incorrect.")
        if not user.is_active:
            raise serializers.ValidationError("Compte désactivé.")
        data["user"] = user
        return data


class UserUpdateSerializer(serializers.ModelSerializer):
    # Utilise le serializer d'écriture pour accepter les fichiers
    profile = ProfileUpdateSerializer()

    class Meta:
        model  = User
        fields = ["full_name", "profile"]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", {})
        for attr, value in profile_data.items():
            setattr(instance.profile, attr, value)
        instance.profile.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    old_password     = serializers.CharField(write_only=True)
    new_password     = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("Ancien mot de passe incorrect.")
        return value

    def validate(self, data):
        if data["new_password"] != data["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Les mots de passe ne correspondent pas."})
        return data

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
