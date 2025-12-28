from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'(?P<report_type>\w+)/(?P<campaign>\w+)', views.generic_report, name='report'),
]
