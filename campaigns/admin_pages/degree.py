from django.contrib import admin
from ..models import Attendee


class AttendeeInline(admin.TabularInline):
    model = Attendee

class DegreeRegistrationAdmin(admin.ModelAdmin):
    inlines = [
        AttendeeInline
    ]

