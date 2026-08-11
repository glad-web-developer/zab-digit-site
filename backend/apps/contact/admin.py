from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import ContactRequest


@admin.register(ContactRequest)
class ContactRequestAdmin(ImportExportModelAdmin):
    list_display = ['id', 'name', 'phone', 'source', 'created_at', 'is_processed']
    list_display_links = ['id', 'name']
    list_filter = ['is_processed', 'source', 'created_at']
    search_fields = ['name', 'phone', 'message']
    readonly_fields = ['name', 'phone', 'message', 'source', 'created_at']
    list_editable = ['is_processed']
    date_hierarchy = 'created_at'
    save_on_top = True

    fieldsets = (
        ('Контактные данные', {
            'fields': ('name', 'phone', 'source', 'created_at')
        }),
        ('Сообщение', {
            'fields': ('message',)
        }),
        ('Статус', {
            'fields': ('is_processed',)
        }),
    )
