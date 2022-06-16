from rest_framework.authentication import BaseAuthentication, get_authorization_header

from django.contrib.auth import get_user_model

from django.db.utils import IntegrityError

from datetime import datetime, timedelta

from rest_framework import exceptions

from broker import RpcClient


UserModel = get_user_model()


class TokenAuthentication(BaseAuthentication):
    """
    Simple token based authentication.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:

        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """

    keyword = 'Token'
    model = None

    def get_model(self):
        if self.model is not None:
            return self.model
        from rest_framework.authtoken.models import Token
        return Token

    """
    A custom token model may be used, but must have the following properties.

    * key -- The string identifying the token
    * user -- The user to which the token belongs
    """

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            token = self.authenticate_external(model, key)

        if datetime.now() >= token.created + timedelta(weeks=1):
            model.delete(token)
            raise exceptions.AuthenticationFailed('Token is expired.')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')

        return (token.user, token)

    def authenticate_external(self, model, key):
        client = RpcClient()

        try:
            user_id = client.call('auth', 'auth', {
                'key': key
            }).get('user_id',)
        except exceptions.PermissionDenied as e: raise e
        except exceptions.ValidationError as e:
            raise exceptions.AuthenticationFailed(e.detail)
        except Exception as e:
            raise exceptions.AuthenticationFailed(e)

        user = UserModel.objects.filter(auth_id=user_id).first()
        if not user:
            raise exceptions.AuthenticationFailed('User is not found.')

        old_token = user.auth_token if hasattr(user, 'auth_token') else None
        try:
            token = model.objects.create(user=user, key=key)
        except IntegrityError:
            old_token.delete()
            token = model.objects.create(user=user, key=key)

        return token

    def authenticate_header(self, request):
        return self.keyword
