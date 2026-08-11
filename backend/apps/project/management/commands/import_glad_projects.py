import mimetypes
import os
import re
import ssl
import time
from html import unescape
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.project.models import Project, ProjectImage

BASE_URL = 'https://glad-dev.ru'
LIST_URL = f'{BASE_URL}/project/'
HOME_URL = f'{BASE_URL}/'
USER_AGENT = 'zab-digit-site-import/1.0 (+local management command)'
REQUEST_PAUSE = 0.4

CATEGORY_MAP = (
    (re.compile(r'crm\s*/\s*erp', re.I), 'erp'),
    (re.compile(r'многостраничн', re.I), 'site'),
    (re.compile(r'интернет\s*[-–—]?\s*магазин', re.I), 'site'),
    (re.compile(r'landing\s*page', re.I), 'site'),
)

SLUG_RE = re.compile(
    r'(?:https?://glad-dev\.ru)?/project/([a-z0-9][a-z0-9\-]*)/?',
    re.I,
)
CARD_SPLIT_RE = re.compile(
    r'<div class="row mb-5 mb-lg-4 project-card">',
    re.I,
)
NAME_RE = re.compile(
    r'<div class="mb-4 h1 fw-medium">(.*?)</div>',
    re.I | re.S,
)
CATEGORY_LINK_RE = re.compile(
    r'<a class="d-inline shadowButton[^"]*"\s*href="[^"]*"[^>]*>(.*?)</a>',
    re.I | re.S,
)
THUMB_RE = re.compile(
    r'<div class="projectVideo[^"]*"[^>]*>.*?<img[^>]+src="([^"]+)"',
    re.I | re.S,
)
DETAIL_BLOCK_RE = re.compile(
    r'<div class="container py-5 project">(.*?)(?:<div class="pohoj_project"|'
    r'<div class="fonovaia-kartinka|</div>\s*</div>\s*</div>\s*<div class="fonovaia)',
    re.I | re.S,
)
H1_RE = re.compile(r'<h1[^>]*>(.*?)</h1>', re.I | re.S)
PODROBNEE_RE = re.compile(
    r'<div class="podrobnee mb-3">(.*?)</div>',
    re.I | re.S,
)
SPECIALS_OPEN_RE = re.compile(
    r'<div class="specials mb-3">',
    re.I,
)
SCREENSHOT_RE = re.compile(
    r'<img class="screenshot[^"]*"\s+src="([^"]+)"',
    re.I,
)
HOME_PROJECTS_RE = re.compile(
    r'<div class="container projects">(.*?)</div>\s*<div class="row text-center',
    re.I | re.S,
)
TAG_RE = re.compile(r'<[^>]+>')
DIV_TOKEN_RE = re.compile(r'</?div\b[^>]*>', re.I)


def strip_tags(value):
    return unescape(TAG_RE.sub('', value or '')).strip()


def extract_balanced_div_inner(html, open_match):
    """Вернуть inner HTML div'а с учётом вложенных div."""
    start = open_match.end()
    depth = 1
    for token in DIV_TOKEN_RE.finditer(html, start):
        token_text = token.group(0)
        if token_text.startswith('</'):
            depth -= 1
            if depth == 0:
                return html[start:token.start()].strip()
        elif not token_text.endswith('/>'):
            depth += 1
    return html[start:].strip()


def normalize_description(html):
    """Убрать битые обёртки, гарантировать закрытые теги для карточек."""
    if not html:
        return ''
    text = html.strip()
    # частый мусор источника: <p> <div>...</div></p>
    text = re.sub(r'^<p>\s*', '', text, flags=re.I)
    text = re.sub(r'\s*</p>$', '', text, flags=re.I)
    plain = strip_tags(text)
    if not plain:
        return ''
    # для главной безопаснее короткое описание без незакрытой вёрстки
    if '<div' in text.lower() or text.count('<p') != text.count('</p>'):
        return f'<p>{plain}</p>'
    return text


def map_category(label):
    text = strip_tags(label or '')
    if not text:
        return None
    for pattern, code in CATEGORY_MAP:
        if pattern.search(text):
            return code
    return None


def slug_from_href(href):
    if not href:
        return None
    match = SLUG_RE.search(href)
    if not match:
        return None
    slug = match.group(1).lower().strip('-')
    if slug in {'category', ''}:
        return None
    return slug


def absolute_url(url):
    if not url:
        return None
    return urljoin(BASE_URL + '/', url)


def filename_from_url(url, prefix, index=None):
    path = urlparse(url).path
    base = os.path.basename(path) or 'image.bin'
    base = re.sub(r'[^\w.\-]+', '_', base)
    if len(base) > 120:
        name, ext = os.path.splitext(base)
        base = name[:100] + ext
    if index is None:
        return f'{prefix}_{base}'
    return f'{prefix}_{index}_{base}'


class Command(BaseCommand):
    help = 'Импорт проектов с glad-dev.ru в модели Project / ProjectImage'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Только парсинг и вывод, без записи в БД',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Ограничить число новых проектов (0 = без лимита)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit'] or 0

        self.stdout.write('Загрузка главной и списка проектов...')
        home_html = self.fetch_text(HOME_URL)
        list_html = self.fetch_text(LIST_URL)

        main_slugs = self.parse_home_main_slugs(home_html)
        cards = self.parse_list_cards(list_html)
        self.stdout.write(
            f'На главной (НАШИ ПРОЕКТЫ): {len(main_slugs)} | '
            f'В каталоге: {len(cards)}'
        )

        created = skipped = failed = 0
        total = len(cards)

        for position, card in enumerate(cards):
            slug = card['slug']
            order_index = total - position

            if Project.objects.filter(slug=slug).exists():
                skipped += 1
                self.stdout.write(f'  skip  [{slug}] уже есть')
                continue

            if limit and created >= limit:
                self.stdout.write(
                    f'Достигнут --limit={limit}, остальные новые пропущены'
                )
                break

            try:
                detail = self.fetch_detail(slug)
                name = detail.get('name') or card.get('name') or slug
                category_label = detail.get('category_label') or card.get('category_label')
                category = map_category(category_label)
                description = detail.get('description') or ''
                screenshots = detail.get('screenshots') or []
                thumbnail_url = card.get('thumbnail_url')
                show_in_main = slug in main_slugs

                self.stdout.write(
                    f'  {"dry" if dry_run else "new "} [{slug}] '
                    f'cat={category or "-"} main={show_in_main} '
                    f'imgs={len(screenshots)} | {name}'
                )

                if dry_run:
                    created += 1
                    continue

                self.save_project(
                    slug=slug,
                    name=name,
                    description=description,
                    category=category,
                    show_in_main=show_in_main,
                    order_index=order_index,
                    thumbnail_url=thumbnail_url,
                    screenshot_urls=screenshots,
                )
                created += 1
            except Exception as exc:
                failed += 1
                self.stderr.write(
                    self.style.ERROR(f'  fail [{slug}] {exc}')
                )

        self.stdout.write(self.style.SUCCESS(
            f'Готово: created={created} skipped={skipped} failed={failed}'
            + (' (dry-run)' if dry_run else '')
        ))

    def fetch_text(self, url):
        """Загрузка HTML с игнорированием SSL ошибок (для разработки)"""
        time.sleep(REQUEST_PAUSE)
        request = Request(url, headers={'User-Agent': USER_AGENT})

        # Создаем SSL контекст, который не проверяет сертификаты
        # ВНИМАНИЕ: Только для разработки! Для продакшена используйте сертификаты
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        try:
            with urlopen(request, timeout=60, context=ssl_context) as response:
                charset = response.headers.get_content_charset() or 'utf-8'
                return response.read().decode(charset, errors='replace')
        except URLError as e:
            self.stderr.write(
                self.style.ERROR(f'Ошибка при загрузке {url}: {e}')
            )
            raise

    def fetch_bytes(self, url):
        """Загрузка бинарных данных с игнорированием SSL ошибок (для разработки)"""
        time.sleep(REQUEST_PAUSE)
        request = Request(url, headers={'User-Agent': USER_AGENT})

        # Создаем SSL контекст, который не проверяет сертификаты
        # ВНИМАНИЕ: Только для разработки! Для продакшена используйте сертификаты
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        try:
            with urlopen(request, timeout=60, context=ssl_context) as response:
                content_type = response.headers.get_content_type()
                return response.read(), content_type
        except URLError as e:
            self.stderr.write(
                self.style.ERROR(f'Ошибка при загрузке {url}: {e}')
            )
            raise

    def fetch_detail(self, slug):
        url = f'{BASE_URL}/project/{slug}/'
        try:
            html = self.fetch_text(url)
        except (HTTPError, URLError) as exc:
            raise RuntimeError(f'не удалось открыть детальную страницу: {exc}') from exc

        block_match = DETAIL_BLOCK_RE.search(html)
        block = block_match.group(1) if block_match else html

        h1_match = H1_RE.search(block)
        name = strip_tags(h1_match.group(1)) if h1_match else None

        cat_match = PODROBNEE_RE.search(block)
        category_label = strip_tags(cat_match.group(1)) if cat_match else None

        specials_open = SPECIALS_OPEN_RE.search(block)
        description = ''
        if specials_open:
            description = normalize_description(
                extract_balanced_div_inner(block, specials_open)
            )
        screenshots = []
        for src in SCREENSHOT_RE.findall(block):
            abs_url = absolute_url(src)
            if abs_url and abs_url not in screenshots:
                screenshots.append(abs_url)

        if not name and not screenshots and not description:
            raise RuntimeError('пустая или невалидная детальная страница')

        return {
            'name': name,
            'category_label': category_label,
            'description': description,
            'screenshots': screenshots,
        }

    def parse_list_cards(self, html):
        cards = []
        seen = set()
        for chunk in CARD_SPLIT_RE.split(html)[1:]:
            # обрезаем хвост следующих секций страницы
            cut = re.search(
                r'<div class="(?:fonovaia|pohoj_project|footer|container py-5)',
                chunk,
                re.I,
            )
            if cut:
                chunk = chunk[:cut.start()]

            href_match = SLUG_RE.search(chunk)
            slug = slug_from_href(href_match.group(0)) if href_match else None
            if not slug or slug in seen:
                continue
            seen.add(slug)

            name_match = NAME_RE.search(chunk)
            name = strip_tags(name_match.group(1)) if name_match else slug

            cat_match = CATEGORY_LINK_RE.search(chunk)
            category_label = strip_tags(cat_match.group(1)) if cat_match else None

            thumb_match = THUMB_RE.search(chunk)
            thumbnail_url = absolute_url(thumb_match.group(1)) if thumb_match else None

            cards.append({
                'slug': slug,
                'name': name,
                'category_label': category_label,
                'thumbnail_url': thumbnail_url,
            })
        return cards

    def parse_home_main_slugs(self, html):
        section_match = HOME_PROJECTS_RE.search(html)
        section = section_match.group(1) if section_match else ''
        if not section:
            # fallback: между заголовками НАШИ ПРОЕКТЫ и НАМ ДОВЕРЯЮТ
            start = html.find('НАШИ')
            end = html.find('НАМ')
            if start != -1 and end != -1 and end > start:
                section = html[start:end]

        slugs = []
        for match in SLUG_RE.finditer(section):
            slug = slug_from_href(match.group(0))
            if slug and slug not in slugs:
                slugs.append(slug)
        return set(slugs)

    @transaction.atomic
    def save_project(
            self,
            *,
            slug,
            name,
            description,
            category,
            show_in_main,
            order_index,
            thumbnail_url,
            screenshot_urls,
    ):
        project = Project.objects.create(
            name=name[:255],
            slug=slug[:255],
            description=description or None,
            category=category,
            show_in_main=show_in_main,
            order_index=order_index,
        )

        if thumbnail_url:
            self.attach_image(
                instance=project,
                field_name='thumbnail',
                url=thumbnail_url,
                filename=filename_from_url(thumbnail_url, slug),
                label='thumbnail',
            )

        for index, url in enumerate(screenshot_urls):
            image = ProjectImage(project=project, order_index=index)
            ok = self.attach_image(
                instance=image,
                field_name='image',
                url=url,
                filename=filename_from_url(url, slug, index),
                label=f'gallery[{index}]',
                save_instance=True,
            )
            if not ok:
                continue

    def attach_image(self, instance, field_name, url, filename, label, save_instance=False):
        try:
            data, content_type = self.fetch_bytes(url)
        except Exception as exc:
            self.stderr.write(
                self.style.WARNING(f'    photo skip {label}: {exc}')
            )
            return False

        if not data:
            self.stderr.write(
                self.style.WARNING(f'    photo skip {label}: пустой ответ')
            )
            return False

        if '.' not in os.path.basename(filename):
            ext = mimetypes.guess_extension(content_type or '') or '.bin'
            if ext == '.jpe':
                ext = '.jpg'
            filename = f'{filename}{ext}'

        field = getattr(instance, field_name)
        try:
            field.save(filename, ContentFile(data), save=False)
            if save_instance or instance.pk:
                instance.save()
        except Exception as exc:
            self.stderr.write(
                self.style.WARNING(f'    photo skip {label}: {exc}')
            )
            return False
        return True