from django.shortcuts import render, redirect, get_object_or_404

from apps.client.models import Client
from apps.contact.models import ContactRequest
from apps.diploma.models import Award, Diploma
from apps.pages.models import SitePage, TechStack
from apps.project.models import Project
from core.models import SiteSettings


def render_home(request):
    diplomas = Diploma.objects.all().order_by('order_index')
    awards = Award.objects.all().order_by('order_index')
    clients = Client.objects.all().order_by('order_index')
    projects_main = Project.objects.filter(show_in_main=True).order_by('-order_index')
    site_settings = SiteSettings.load()
    tech_stack = TechStack.objects.all()
    return render(request, 'home.html', {
        'diplomas': diplomas,
        'awards': awards,
        'projects': projects_main,
        'clients': clients,
        'site_settings': site_settings,
        'tech_stack': tech_stack,
        'active_page': 'home',
    })


def render_404(request):
    return render(request, '404.html', {})


def render_gratitude(request):
    return render(request, 'gratitude.html', {})


def render_contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        message = request.POST.get('message', '').strip()
        source = request.POST.get('source', 'Главная').strip()
        consent = request.POST.get('consent', '')

        # Все обязательные поля + чекбокс
        if not name or not phone or not consent:
            referer = request.META.get('HTTP_REFERER', '/')
            return redirect(referer)

        ContactRequest.objects.create(
            name=name,
            phone=phone,
            message=message,
            source=source,
        )
        return redirect('/gratitude/')
    return redirect('/')


def render_site_page(request, slug):
    page = get_object_or_404(SitePage, slug=slug)
    return render(request, 'site_page.html', {'page': page})


def error_404(request, exception):
    return render(request, '404.html', status=404)
