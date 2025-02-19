from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('list/', views.UserListView.as_view(), name='user-list'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('me/', views.UserDetailView.as_view(), name='user-detail'),
]