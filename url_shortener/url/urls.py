from django.urls import path

from . import views

urlpatterns = [
    path('', views.URLCreateView.as_view(), name='home'),
    path('<str:short_url>/', views.redirect_to_long_url, name='redirect_to_long_url'),
    path('url/expired/', views.link_expired, name='link_expired'),
]
