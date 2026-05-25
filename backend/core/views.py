from django.shortcuts import render

from apps.client.models import Client
from apps.diploma.models import Diploma
from apps.project.models import Project


def render_home(request):
    diplomas = Diploma.objects.all().order_by('order_index')
    clients = Client.objects.all()
    projects = Project.objects.filter(show_in_main=True)
    return render(request, 'home.html',
                  {'diplomas':diplomas, 'projects':projects, 'clients':clients})

def render_404(request):
    return render(request, '404.html',
                  {})


def render_gratitude(request):
    return render(request, 'gratitude.html',
                  {})

def error_404(request, exception):
    return render(request,'404.html', status=404)
