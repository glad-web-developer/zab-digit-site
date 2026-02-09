from django.shortcuts import render

from .models import Project


def render_project_lv(request):
    projects = Project.objects.all().order_by('-order_index')
    return render(request, 'project/project_lv.html',
                  {'projects': projects,
                   })


def render_project_dv(request, slug_or_id):
    try:
        project = Project.objects.get(slug=slug_or_id)
    except Exception:
        try:
            project = Project.objects.get(id=slug_or_id)
        except Exception:
            return render(request, '404.html', {})

    return render(request, 'project/project_dv.html',
                  {'project': project, })
