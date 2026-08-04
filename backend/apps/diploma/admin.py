from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

from .models import Award, Diploma


@admin.register(Diploma)
class DiplomaAdmin(ImportExportModelAdmin):
    list_display = ['id', 'name', 'preview', 'order_index']
    list_display_links = ['id', 'name']
    list_editable = ['order_index']
    search_fields = ['name']
    save_on_top = True

    def preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="max-height:80px;max-width:80px;'
                'object-fit:contain;border-radius:4px;">',
                obj.avatar.url
            )
        return '—'
    preview.short_description = 'Превью'


@admin.register(Award)
class AwardAdmin(ImportExportModelAdmin):
    list_display = ['id', 'name', 'preview', 'order_index']
    list_display_links = ['id', 'name']
    list_editable = ['order_index']
    search_fields = ['name']
    save_on_top = True

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:80px;max-width:80px;'
                'object-fit:contain;border-radius:4px;">',
                obj.image.url
            )
        return '—'
    preview.short_description = 'Превью'
