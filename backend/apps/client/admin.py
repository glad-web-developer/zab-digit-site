from django.contrib import admin
from django.template.defaultfilters import safe
from import_export.admin import ImportExportModelAdmin

from .models import Client




@admin.register(Client)
class ClientAdmin(ImportExportModelAdmin):
    list_display = [
        'id',
        'name',
        'avatar_preview',
        'order_index',
    ]

    list_display_links = [
        'id',
        'name',
    ]

    list_filter = ['order_index']


    save_on_top = True
    save_as = True

    # Превью аватарки
    def avatar_preview(self, obj):
        if obj.avatar:
            return safe(f'<img src="{obj.avatar.url}" style="max-height: 50px; max-width: 50px; margin-right:15px" />')
        return "-"

    avatar_preview.short_description = 'Аватар'


