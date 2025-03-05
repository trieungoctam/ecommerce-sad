from django.urls import path
from .views import UserRegisterView, UserProfilesView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('profile/', UserProfilesView.as_view(), name='user-profile'),
]
