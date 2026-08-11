from django.contrib import admin
from django.utils.html import format_html

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    save_on_top = True

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def image_preview(self, obj):
        if obj.crm_section_image:
            return format_html('<img src="{}" style="max-height:120px;">', obj.crm_section_image.url)
        return '— не задано (используется стандартная)'
    image_preview.short_description = 'Текущая картинка'

    def get_fieldsets(self, request, obj=None):
        return (
            ('Контакты (шапка и подвал сайта)', {
                'fields': ('phone', 'telegram_url'),
            }),
            ('Блок «Мы разрабатываем CRM/ERP-системы»', {
                'fields': ('image_preview', 'crm_section_image'),
                'description': 'Декоративная картинка справа в карточке'
            }),
        )

    readonly_fields = ['image_preview']
