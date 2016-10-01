from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.registrant_list, name='registrant_list'),
    url(r'^registrant/(?P<pk>\d+)/$', views.registrant_detail, name='registrant_detail'),
    url(r'^registrant/new/$', views.registrant_new, name='registrant_new'),
    url(r'^degree/new/$', views.degree_registration_new, name='degree_new'),
]
