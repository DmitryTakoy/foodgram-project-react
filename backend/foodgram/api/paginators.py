from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)


class CustomPagination(
        LimitOffsetPagination, PageNumberPagination):

    def paginate_queryset(self, queryset, request, view=None):
        if 'offset' in request.query_params or 'limit' in request.query_params:
            return LimitOffsetPagination.paginate_queryset(self, queryset, request, view)
        else:
            return PageNumberPagination.paginate_queryset(
                self, queryset, request, view)

    def get_paginated_response(self, data):
        if 'offset' in self.request.query_params or 'limit' in self.request.query_params:
            return LimitOffsetPagination.get_paginated_response(self, data)
        else:
            return PageNumberPagination.get_paginated_response(self, data)
