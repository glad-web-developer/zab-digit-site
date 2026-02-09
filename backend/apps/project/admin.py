from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import Project




@admin.register(Project)
class ProjectAdmin(ImportExportModelAdmin):
    list_display = [
        'id',
        'name',

        'order_index',
        'show_in_main',
    ]

    list_display_links = [
        'id',
        'name',
    ]

    list_filter = [
        'show_in_main',
    ]
    search_fields = [
        'name',

    ]



    save_on_top = True
    save_as = True

    prepopulated_fields = {"slug": ("name",)}

