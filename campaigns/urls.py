from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.redirect_to_official, name='redirect'),
    url(r'^(?P<campaign>[\w+]+)/order/(?P<pk>[\w+-]+)?$', views.generic_order, name='order'),
    url(r'^checkout/$', views.checkout_view, name='checkout'),
    url(r'^payment_confirmation/$', views.payment_confirmation_view, name='payment_confirmation'),
]
