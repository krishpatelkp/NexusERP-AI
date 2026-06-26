from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from attendance.constants import DEFAULT_REPORT_PAGE_SIZE


# ==========================================================
# ATTENDANCE REPORT PAGINATION
# ==========================================================

class AttendanceReportPagination(PageNumberPagination):
    """
    Pagination for all attendance report endpoints.

    Default page size is read from constants.
    Client can override using ?page_size=N.
    Maximum allowed page size is 100.

    Response includes:
    - count       : total records
    - total_pages : total pages
    - page        : current page number
    - page_size   : records per page
    - next        : next page URL
    - previous    : previous page URL
    - results     : paginated data
    """

    page_size = DEFAULT_REPORT_PAGE_SIZE

    page_size_query_param = "page_size"

    max_page_size = 100

    page_query_param = "page"

    def get_paginated_response(self, data):
        return Response(
            {
                "count":       self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "page":        self.page.number,
                "page_size":   self.get_page_size(self.request),
                "next":        self.get_next_link(),
                "previous":    self.get_previous_link(),
                "results":     data,
            }
        )

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "count":       {"type": "integer"},
                "total_pages": {"type": "integer"},
                "page":        {"type": "integer"},
                "page_size":   {"type": "integer"},
                "next":        {"type": "string", "nullable": True},
                "previous":    {"type": "string", "nullable": True},
                "results":     schema,
            },
        }