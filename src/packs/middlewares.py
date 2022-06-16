from django.db import connection
from django.utils.deprecation import MiddlewareMixin


class SqlPrintMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        sql_time = sum([float(query["time"]) for query in connection.queries])
        if (request.path == '/api/v1/players/0'):
            queries = connection.queries
            a = 1

        print("Page {page_path} render: {sql_time} sec for {connetcions_count} queries".format(
            page_path=request.path,
            sql_time=str(sql_time),
            connetcions_count=str(len(connection.queries))))

        return response
