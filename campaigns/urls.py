from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.degree_registration_new, name='degree_new'),
    url(r'^degree/new/$', views.degree_registration_new, name='degree_new'),
    url(r'^degree/thankyou/(?P<pk>\d+)$', views.degree_thank_you, name='degree_thank_you'),
]
