from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.crawfish_order, name='crawfish_orders'),
    url(r'^degree/new/$', views.degree_registration_new, name='degree_new'),
    url(r'^degree/thankyou/(?P<pk>\d+)$', views.degree_thank_you, name='degree_thank_you'),
    url(r'^nuts/order/(?P<pk>[\w+-]+)?$', views.nuts_order, name='nut_orders'),
    url(r'^fishfry/order/(?P<pk>[\w+-]+)?$', views.fishfry_closed, name='fishfry_orders'),
    url(r'^crawfish/order/(?P<pk>[\w+-]+)?$', views.crawfish_order, name='crawfish_orders'),
    url(r'^(?P<campaign>[\w+]+)/order/(?P<pk>[\w+-]+)?$', views.generic_order, name='order'),
    url(r'^checkout/$', views.checkout_view, name='checkout'),
    url(r'^payment_confirmation/$', views.payment_confirmation_view, name='payment_confirmation'),
]
