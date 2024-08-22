from django.urls import path

from . import views

urlpatterns = [
    path('', views.URLCreateView.as_view(), name='home'),
    path('<str:short_url>/', views.redirect_to_long_url, name='redirect_to_long_url'),
    path('url/expired/', views.link_expired, name='link_expired'),
    path('url/user_urls/', views.URLListView.as_view(), name='user_urls'),
    path('deactivate/<str:short_url>/', views.deactivate_url, name='deactivate_url'),
    path('extend/<str:short_url>/', views.extend_url_validity, name='extend_url_validity'),
    path('url/delete/<str:short_url>/', views.delete_url, name='delete_url'),
]
