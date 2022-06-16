from rest_framework.response import Response


class Successful(Response):

    def __init__(self, data={'successful': True}, status=None):
        super().__init__(data=data, status=status)
