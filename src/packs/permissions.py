from rest_framework.permissions import BasePermission

from rest_framework import exceptions

from collections import ChainMap


class IsAuthenticated(BasePermission):
    """
    Allows access to authenticated users or method authenticate
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated or view.action == 'create')


class IsEnoughBalance(BasePermission):
    """
    Allows access to authenticated users with enought balance
    """

    def get_balance(self, request):
        from broker import RpcClient

        client = RpcClient()

        try:
            balance = client.call('auth', 'get_balance', {
                'key': request.user.auth_token.key
            }).get('balance',)
        except exceptions.PermissionDenied as e: raise e
        except exceptions.ValidationError as e:
            raise exceptions.AuthenticationFailed(e.detail)
        except Exception as e:
            raise exceptions.AuthenticationFailed(e)

        return balance

    def has_permission(self, request, view):
        if is_anonymous := request.user.is_anonymous:
            return not is_anonymous

        if view.basename == 'auction':
            currency, amount = view.get_object().get_cost().values()
        elif view.basename == 'cards':
            currency, amount = view.get_object().content_object.get_cost().values()

        balance = list(filter(lambda d: currency.system_name in d.values(), self.get_balance(request)))

        if enought := dict(ChainMap(*balance)).get('amount',) >= amount:
            setattr(request, 'cost', dict(
                user=request.user.auth_id,
                currencies=[dict(
                    currency=currency.system_name,
                    amount=amount
                )]
            ))
        return enought
