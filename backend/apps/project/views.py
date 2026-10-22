
from django.shortcuts import render

from .models import CATEGORY_CHOICES, Project, ProjectCategory


def render_project_lv(request):
    category = request.GET.get('category', '')

    all_projects = Project.objects.all().order_by('-order_index')

    if category:
        projects = all_projects.filter(
            categories__slug=category
        ).distinct()
    else:
        projects = all_projects

    categories = ProjectCategory.objects.all()

    return render(request, 'project/project_lv.html', {
        'projects': projects,
        'all_projects': all_projects,
        'active_category': category,
        'categories': categories,
        'active_page': 'project',
    })


def render_project_dv(request, slug_or_id):
    project = Project.objects.filter(slug=slug_or_id).first()

    if project is None and str(slug_or_id).isdigit():
        project = Project.objects.filter(id=int(slug_or_id)).first()

    if project is None:
        return render(request, '404.html', {}, status=404)

    gallery = project.images.all().order_by('-order_index')

    return render(request, 'project/project_dv.html', {
        'project': project,
        'gallery': gallery,
        'active_page': 'project',
    })
