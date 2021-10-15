from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


def get_paginated_response(
    *, pagination_class, serializer_class, queryset, request, view
):
    paginator = pagination_class()

    page = paginator.paginate_queryset(queryset, request, view=view)

    if page is not None:
        serializer = serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    serializer = serializer_class(queryset, many=True)

    return Response(data=serializer.data)


class HeaderLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 40

    def get_paginated_response(self, data):
        next_url = self.get_next_link()
        previous_url = self.get_previous_link()
        link_template = '<{url}>; rel="{rel}"'

        links = []

        if next_url is not None:
            links.append(link_template.format(url=next_url, rel='next'))
        if previous_url is not None:
            links.append(link_template.format(url=previous_url, rel='prev'))

        headers = {'Link': ', '.join(links)} if links else {}
        headers['X-Total-Count'] = self.count

        return Response(data, headers=headers)
