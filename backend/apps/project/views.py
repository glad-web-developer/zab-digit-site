from django.shortcuts import render

from .models import CATEGORY_CHOICES, Project


def render_project_lv(request):
    category = request.GET.get('category', '')
    all_projects = Project.objects.all().order_by('-order_index')
    if category:
        projects = all_projects.filter(category=category)
    else:
        projects = all_projects
    return render(request, 'project/project_lv.html', {
        'projects': projects,
        'all_projects': all_projects,
        'active_category': category,
        'categories': CATEGORY_CHOICES,
        'active_page': 'project',
    })


def render_project_dv(request, slug_or_id):
    try:
        project = Project.objects.get(slug=slug_or_id)
    except Exception:
        try:
            project = Project.objects.get(id=slug_or_id)
        except Exception:
            return render(request, '404.html', {}, status=404)

    gallery = project.images.all().order_by('order_index')
    return render(request, 'project/project_dv.html', {
        'project': project,
        'gallery': gallery,
        'active_page': 'project',
    })
