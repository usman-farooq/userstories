from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from django.contrib.auth.views import LoginView
from application import views as api_views

urlpatterns = [
    path('', include(DefaultRouter().urls)),
    path('', include('rest_framework.urls')),
    path('login', LoginView.as_view(), name='login'),
    path('auth-token', views.obtain_auth_token, name='auth-token'),
    
    path('resources', api_views.ResourceMainView.as_view()),
    path('resources/<int:resource_id>', api_views.ResourceObjectView.as_view()),
    
    path('users', api_views.UserMainView.as_view()),
    path('users/<email>', api_views.UserObjectView.as_view()),
]