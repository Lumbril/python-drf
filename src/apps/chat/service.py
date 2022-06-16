from rest_framework.authtoken.models import Token


def get_user_by_token(token):
    return Token.objects.get(pk=token).user if Token.objects.filter(pk=token).exists() else None
