from django.urls import path, re_path
from . import views

urlpatterns = [
    path(r'', views.redirect_to_official, name='redirect'),
    path(r'checkout/', views.checkout_view, name='checkout'),
    path(r'payment_confirmation/', views.payment_confirmation_view, name='payment_confirmation'),
    re_path(r'^(?P<campaign>[A-Za-z]+)(?:/order)?/(?P<pk>[\w+-]+)?', views.generic_order, name='order'),
]
