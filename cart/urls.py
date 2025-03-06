from django.urls import path
from .views import (
    CartCreateView,
    CartListView,
    CartDetailView,
    CartItemListCreateView,
    CartItemDetailView,
    CustomerCartView
)

urlpatterns = [
    # Cart URLs
    path('create/', CartCreateView.as_view(), name='cart-create'),
    path('', CartListView.as_view(), name='cart-list'),
    path('<int:id>/', CartDetailView.as_view(), name='cart-detail'),

    # Customer-specific cart URLs
    path('<str:customer_id>/carts/', CustomerCartView.as_view(), name='customer-carts'),

    # Cart Item URLs
    path('<int:cart_id>/items/', CartItemListCreateView.as_view(), name='cart-item-list-create'),
    path('items/<int:id>/', CartItemDetailView.as_view(), name='cart-item-detail'),
]