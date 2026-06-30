from rest_framework.pagination import PageNumberPagination


# ==========================================================
# INVENTORY PAGINATION
# ==========================================================

class InventoryPagination(PageNumberPagination):
    """
    Standard pagination for all Inventory list APIs.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100