from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class StandardResultsSetPagination(PageNumberPagination):
    """
    Lớp phân trang tùy chỉnh cho các kết quả tiêu chuẩn.
    Mặc định sẽ có 10 mục trên mỗi trang.
    Người dùng có thể yêu cầu số lượng mục trên mỗi trang bằng cách sử dụng tham số 'page_size'.
    Số lượng tối đa mục trên mỗi trang có thể được giới hạn bằng 'max_page_size'.
    """
    page_size = 12  # Số lượng mục mặc định trên mỗi trang
    page_size_query_param = 'page_size'  # Tham số truy vấn để thay đổi page_size
    max_page_size = 100  # Số lượng mục tối đa mà người dùng có thể yêu cầu trên mỗi trang

    def get_paginated_response(self, data):
        """
        Tùy chỉnh định dạng phản hồi phân trang.
        Bao gồm các thông tin về trang hiện tại, tổng số trang, tổng số mục,
        và các liên kết next/previous.
        """
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })



class AllMajorPagination(PageNumberPagination):
    # Số lượng dữ liệu mặc định trên mỗi trang
    page_size = 9

    # Tên tham số query parameter để người dùng có thể tùy chỉnh page size
    # Ví dụ: /api/all_major/?field_id=1&page_size=15
    page_size_query_param = 'page_size'

    # Giới hạn tối đa cho page size mà người dùng có thể yêu cầu
    max_page_size = 100



class MajorPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        Tùy chỉnh định dạng phản hồi phân trang.
        Bao gồm các thông tin về trang hiện tại, tổng số trang, tổng số mục,
        và các liên kết next/previous.
        """
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })



