from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.conf.urls import handler404

from apps.project.views import render_project_lv, render_project_dv
from core.views import render_home, render_404, render_gratitude, render_contact, render_site_page

handler404 = 'core.views.error_404'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', render_home),
    path('404/', render_404),
    path('gratitude/', render_gratitude),
    path('contact/', render_contact),
    path('project/', render_project_lv),
    path('project/<slug_or_id>/', render_project_dv),
    path('page/<slug:slug>/', render_site_page),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
