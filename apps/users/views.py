import requests as http_requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from core.utils.response import success, created, error
from .models import User
from .serializers import (RegisterSerializer, LoginSerializer, UserSerializer,
                           UserUpdateSerializer, ChangePasswordSerializer,
                           get_tokens_for_user)

# ── Web Client ID Firebase (google_sign_in Android) ───────────
_GOOGLE_CLIENT_ID = (
    '764014399589-2t6qiko74jf1ab2fl524iassfjt6pr4h.apps.googleusercontent.com'
)


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


# ══════════════════════════════════════════════════════════════
# AUTH SOCIALE
# ══════════════════════════════════════════════════════════════

def _get_or_create_social_user(*, provider, social_id, email, full_name):
    """
    Retourne (user, created).
    Stratégie :
      1. Cherche par (social_provider, social_id)          → utilisateur connu
      2. Cherche par email non-vide                         → compte existant à lier
      3. Crée un nouvel utilisateur avec phone placeholder
    Le champ `phone` étant requis et unique, on génère un
    identifiant court mais garanti unique pour les comptes OAuth.
    """
    # 1 — compte OAuth déjà connu
    user = User.objects.filter(
        social_provider=provider, social_id=social_id
    ).first()
    if user:
        return user, False

    # 2 — email existant → lier le compte social
    if email:
        user = User.objects.filter(email=email).first()
        if user:
            updated = False
            if not user.social_id:
                user.social_provider = provider
                user.social_id       = social_id
                updated = True
            if not user.email:
                user.email = email
                updated = True
            if updated:
                user.save(update_fields=['social_provider', 'social_id', 'email'])
            return user, False

    # 3 — créer un nouveau compte
    #   phone placeholder : "g" + 18 chars de social_id (max 19 < 20)
    prefix       = 'g' if provider == 'google' else 'fb'
    max_id_len   = 20 - len(prefix)
    phone_placeholder = f"{prefix}{social_id[:max_id_len]}"

    user = User.objects.create_user(
        phone           = phone_placeholder,
        full_name       = full_name or 'Utilisateur',
        email           = email or '',
        password        = None,          # mot de passe inutilisable → OAuth only
        social_provider = provider,
        social_id       = social_id,
        phone_verified  = False,
        is_active       = True,
    )
    return user, True


class GoogleSocialLoginView(APIView):
    """POST /auth/social/google/  —  body: {"id_token": "<token>"}"""
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('id_token', '').strip()
        if not token:
            return error("Le champ 'id_token' est requis.")

        # ── Vérification du token via Google ──────────────────
        try:
            info = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                _GOOGLE_CLIENT_ID,
            )
        except ValueError as exc:
            return error(f"Token Google invalide : {exc}")

        social_id = info.get('sub', '')
        email     = info.get('email', '')
        full_name = info.get('name', '') or email or 'Utilisateur Google'

        if not social_id:
            return error("Identifiant Google introuvable dans le token.")

        user, _ = _get_or_create_social_user(
            provider  = 'google',
            social_id = social_id,
            email     = email,
            full_name = full_name,
        )
        return success(
            data    = {"user": UserSerializer(user).data,
                       "tokens": get_tokens_for_user(user)},
            message = "Connexion Google réussie.",
        )


class FacebookSocialLoginView(APIView):
    """POST /auth/social/facebook/  —  body: {"access_token": "<token>"}"""
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('access_token', '').strip()
        if not token:
            return error("Le champ 'access_token' est requis.")

        # ── Vérification via Graph API ────────────────────────
        try:
            resp = http_requests.get(
                'https://graph.facebook.com/me',
                params  = {'fields': 'id,name,email', 'access_token': token},
                timeout = 10,
            )
            data = resp.json()
        except Exception:
            return error("Impossible de joindre l'API Facebook.")

        if resp.status_code != 200 or 'error' in data:
            msg = data.get('error', {}).get('message', 'Token Facebook invalide.')
            return error(msg)

        social_id = data.get('id', '')
        email     = data.get('email', '')
        full_name = data.get('name', '') or 'Utilisateur Facebook'

        if not social_id:
            return error("Identifiant Facebook introuvable.")

        user, _ = _get_or_create_social_user(
            provider  = 'facebook',
            social_id = social_id,
            email     = email,
            full_name = full_name,
        )
        return success(
            data    = {"user": UserSerializer(user).data,
                       "tokens": get_tokens_for_user(user)},
            message = "Connexion Facebook réussie.",
        )