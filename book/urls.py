from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, BookDetailView, BookListView, BookCreateView

router = DefaultRouter()
router.register(r'search', BookViewSet, basename='book')

urlpatterns = [
    # ViewSet URLs
    path('create/', BookCreateView.as_view(), name='book-create'),
    # path('', include(router.urls)),
    # Optional: class-based view URLs if you need them separately
    path('list/', BookListView.as_view(), name='book-list'),
    path('detail/<str:id>/', BookDetailView.as_view(), name='book-detail'),
]