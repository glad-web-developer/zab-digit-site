from django.contrib import admin
from django.utils.html import format_html

from .models import SitePage, TechStack


@admin.register(SitePage)
class SitePageAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'slug', 'updated_at']
    list_display_links = ['id', 'title']
    prepopulated_fields = {'slug': ('title',)}
    save_on_top = True

    fieldsets = (
        (None, {
            'fields': ('title', 'slug')
        }),
        ('Содержание (поддерживает форматирование)', {
            'fields': ('content',)
        }),
    )


@admin.register(TechStack)
class TechStackAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'icon_preview', 'order_index']
    list_display_links = ['id', 'name']
    list_editable = ['order_index']
    save_on_top = True

    def icon_preview(self, obj):
        if obj.icon:
            return format_html(
                '<img src="{}" style="height:28px;width:28px;object-fit:contain;">',
                obj.icon.url
            )
        return '—'
    icon_preview.short_description = 'Иконка'
