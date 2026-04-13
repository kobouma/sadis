# apps/users/serializers.py
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, Profile, DeliveryAgent


# ── Helper JWT ────────────────────────────────────────────────
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "access":  str(refresh.access_token),
        "refresh": str(refresh),
    }


# ── Profil ────────────────────────────────────────────────────
class ProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model  = Profile
        fields = ["avatar", "city", "address", "bio"]

    def get_avatar(self, obj):
        return obj.avatar.url if obj.avatar else None


# ── User lecture ──────────────────────────────────────────────
class UserSerializer(serializers.ModelSerializer):
    profile   = ProfileSerializer(read_only=True)
    is_seller = serializers.BooleanField(read_only=True)
    has_shop  = serializers.BooleanField(read_only=True)

    class Meta:
        model  = User
        fields = ["id", "phone", "full_name", "email",
                  "is_delivery", "is_seller", "has_shop",
                  "phone_verified", "profile", "date_joined"]
        read_only_fields = ["id", "date_joined", "is_seller", "has_shop"]


# ── Inscription ───────────────────────────────────────────────
class RegisterSerializer(serializers.ModelSerializer):
    password         = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model  = User
        fields = ["phone", "full_name", "password", "password_confirm"]

    def validate(self, data):
        if data["password"] != data.pop("password_confirm"):
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


# ── Connexion ─────────────────────────────────────────────────
class LoginSerializer(serializers.Serializer):
    phone    = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(phone=data["phone"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Identifiants incorrects.")
        if not user.is_active:
            raise serializers.ValidationError("Compte désactivé.")
        data["user"] = user
        return data


# ── Mise à jour profil ────────────────────────────────────────
class UserUpdateSerializer(serializers.ModelSerializer):
    city    = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    bio     = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model  = User
        fields = ["full_name", "email", "city", "address", "bio"]

    def update(self, instance, validated_data):
        # Champs du profil
        profile_fields = ["city", "address", "bio"]
        profile_data   = {k: validated_data.pop(k)
                          for k in profile_fields if k in validated_data}

        # Mettre à jour User
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Mettre à jour Profile
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance


# ── Changement de mot de passe ────────────────────────────────
class ChangePasswordSerializer(serializers.Serializer):
    old_password     = serializers.CharField(write_only=True)
    new_password     = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = self.context["request"].user
        if not user.check_password(data["old_password"]):
            raise serializers.ValidationError("Mot de passe actuel incorrect.")
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("Les nouveaux mots de passe ne correspondent pas.")
        return data

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])


# ── Livreur ───────────────────────────────────────────────────
class DeliveryAgentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    phone     = serializers.CharField(source="user.phone",     read_only=True)
    avatar    = serializers.SerializerMethodField()

    class Meta:
        model  = DeliveryAgent
        fields = ["id", "user_name", "phone", "avatar",
                  "vehicle_type", "vehicle_plate", "city",
                  "status", "rating", "total_deliveries",
                  "is_online", "created_at"]
        read_only_fields = ["id", "status", "rating",
                            "total_deliveries", "created_at"]

    def get_avatar(self, obj):
        try:
            return obj.user.profile.avatar.url
        except Exception:
            return None


class DeliveryAgentRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DeliveryAgent
        fields = ["vehicle_type", "vehicle_plate", "city", "id_document"]

    def create(self, validated_data):
        user  = self.context["request"].user
        return DeliveryAgent.objects.create(user=user, **validated_data)