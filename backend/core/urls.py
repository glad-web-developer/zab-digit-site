

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

from django.urls import path

from apps.project.views import render_project_lv, render_project_dv
from core.views import render_home, render_404, render_gratitude

urlpatterns = [
       path('admin/', admin.site.urls),
       path('', render_home),
       path('404/', render_404),
       path('gratitude/', render_gratitude,),
       path('project/', render_project_lv),
       path('project/<id>', render_project_dv),


]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

