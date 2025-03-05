import requests
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from django.conf import settings

# Cấu hình các base URL cho các service sản phẩm.
# Lưu ý: URL này cần được cấu hình theo môi trường (ví dụ: qua API Gateway hoặc DNS nội bộ).
PRODUCT_SERVICE_URLS = {
    'book': 'http://product-service/api/books/',
    'mobile': 'http://product-service/api/mobile/',
    'shoes': 'http://product-service/api/shoes/',
    'clothes': 'http://product-service/api/clothes/',
}

def get_product_info(product_type, product_id):
    """
    Gọi API của Product Service dựa vào product_type và product_id.
    Trả về dữ liệu JSON của sản phẩm nếu thành công.
    """
    base_url = PRODUCT_SERVICE_URLS.get(product_type.lower())
    if not base_url:
        return None
    url = f"{base_url}{product_id}/"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error retrieving product info: {e}")
        return None

class CartViewSet(viewsets.ModelViewSet):
    """
    ViewSet quản lý Cart.
    Trong thực tế, bạn nên giới hạn hiển thị Cart của user hiện tại dựa trên token.
    """
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    lookup_field = 'id'
    permission_classes = []

class CartItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet quản lý CartItem.
    Khi tạo mới CartItem, API sẽ gọi Product Service để lấy thông tin sản phẩm cập nhật.
    """
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    lookup_field = 'id'

    def create(self, request, *args, **kwargs):
        product_type = request.data.get('product_type')
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        cart_id = request.data.get('cart')

        if not all([product_type, product_id, cart_id]):
            return Response(
                {"detail": "Missing required fields: product_type, product_id, cart."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Gọi API của Product Service để lấy thông tin sản phẩm
        product_data = get_product_info(product_type, product_id)
        if not product_data:
            return Response(
                {"detail": "Cannot retrieve product info."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Giả sử product_data trả về có các trường 'price' và 'name'
        price = product_data.get('price')
        product_name = product_data.get('name')
        if price is None or not product_name:
            return Response(
                {"detail": "Incomplete product info returned."},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item_data = {
            "cart": cart_id,
            "product_type": product_type,
            "product_id": product_id,
            "product_name": product_name,
            "quantity": quantity,
            "price": price,
        }

        serializer = self.get_serializer(data=cart_item_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def by_cart(self, request):
        """
        Lấy danh sách các mục trong giỏ hàng theo cart_id.
        Ví dụ: GET /api/cart/items/by_cart/?cart_id=1
        """
        cart_id = request.query_params.get('cart_id')
        if not cart_id:
            return Response(
                {"detail": "Please provide cart_id."},
                status=status.HTTP_400_BAD_REQUEST
            )
        items = self.queryset.filter(cart_id=cart_id)
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)
