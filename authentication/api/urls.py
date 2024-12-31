from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from authentication.api.views import MyUserCreateView, LoginAPIView, UserDetailView

urlpatterns = [
    path('register/', MyUserCreateView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('<int:pk>/', UserDetailView.as_view(), name='user_detail'),

    path('token-refresh/', TokenRefreshView.as_view())
]
