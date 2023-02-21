from django.contrib import admin

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'campaign', 'cost', 'meta_field_one', 'meta_field_two', 'sort_order']
    list_filter = ['campaign']
    search_fields = ['name']
    ordering = ['sort_order']
