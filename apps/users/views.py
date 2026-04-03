from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from core.utils.response import success, created, error
from .models import User
from .serializers import (RegisterSerializer, LoginSerializer, UserSerializer,
                           UserUpdateSerializer, ChangePasswordSerializer,
                           get_tokens_for_user)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        s = RegisterSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.save()
        return created(
            data={"user": UserSerializer(user).data, "tokens": get_tokens_for_user(user)},
            message="Compte créé avec succès.",
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        s = LoginSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.validated_data["user"]
        return success(
            data={"user": UserSerializer(user).data, "tokens": get_tokens_for_user(user)},
            message="Connexion réussie.",
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("refresh")
        if not token:
            return error("Le refresh token est requis.")
        try:
            RefreshToken(token).blacklist()
        except TokenError:
            return error("Token invalide.")
        return success(message="Déconnexion réussie.")


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return success(data=UserSerializer(request.user).data)

    def patch(self, request):
        s = UserUpdateSerializer(request.user, data=request.data,
                                 partial=True, context={"request": request})
        s.is_valid(raise_exception=True)
        return success(data=UserSerializer(s.save()).data, message="Profil mis à jour.")


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        s = ChangePasswordSerializer(data=request.data, context={"request": request})
        s.is_valid(raise_exception=True)
        s.save()
        return success(message="Mot de passe mis à jour.")