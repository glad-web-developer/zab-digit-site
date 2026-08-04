from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

from .models import Project, ProjectImage


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ['image', 'caption', 'order_index', 'preview']
    readonly_fields = ['preview']

    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-height:60px;max-width:100px;object-fit:cover;border-radius:4px;">',
                obj.image.url
            )
        return '—'
    preview.short_description = 'Превью'


@admin.register(Project)
class ProjectAdmin(ImportExportModelAdmin):
    list_display = ['id', 'name', 'category', 'order_index', 'show_in_main', 'thumbnail_preview']
    list_display_links = ['id', 'name']
    list_filter = ['show_in_main', 'category']
    list_editable = ['order_index', 'show_in_main']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    save_on_top = True
    save_as = True
    inlines = [ProjectImageInline]

    fieldsets = (
        ('Основное', {
            'fields': ('name', 'slug', 'category', 'thumbnail', 'show_in_main', 'order_index')
        }),
        ('Описание', {
            'fields': ('description',),
            'description': 'Поддерживает форматирование (жирный, списки, заголовки)'
        }),
    )

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="max-height:40px;max-width:60px;object-fit:cover;border-radius:3px;">',
                obj.thumbnail.url
            )
        return '—'
    thumbnail_preview.short_description = 'Превью'
