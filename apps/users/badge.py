# apps/users/badge.py
# Fonctions de badge pour la sidebar Unfold

def user_count(request):
    from apps.users.models import User
    return User.objects.count()