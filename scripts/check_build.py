"""Check real build outputs before uploading or deploying them."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile

from pypdf import PdfReader
from PIL import Image
from yaml import safe_load

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output'
SITE = ROOT / 'site'
SITE_BASE = urlsplit(safe_load((ROOT / 'mkdocs.yml').read_text(encoding='utf-8'))['site_url']).path


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []
        self.art = []
        self.compositions = 0
        self.figures = []
        self.heading = ''
        self.heading_text = None
        self.in_figure = False
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if 'id' in attributes:
            self.ids.add(attributes['id'])
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self.heading_text = []
        if tag == 'figure':
            self.in_figure = True
            key = attributes.get('data-art', 'composition-coffee')
            self.figures.append((key, self.heading))
        if tag == 'img' and self.in_figure:
            self.images.append(attributes)
        if tag == 'figure' and 'data-art' in attributes:
            self.art.append(attributes['data-art'])
        if tag == 'figure' and 'composition' in attributes.get('class', '').split():
            self.compositions += 1
        for key, value in attrs:
            if key in ('href', 'src') and value:
                self.links.append(value)

    def handle_data(self, data):
        if self.heading_text is not None:
            self.heading_text.append(data)

    def handle_endtag(self, tag):
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6') and self.heading_text is not None:
            self.heading = ''.join(self.heading_text).strip().rstrip('¶').strip()
            self.heading_text = None
        if tag == 'figure':
            self.in_figure = False


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check():
    layout = json.loads((OUT / 'layout-check.json').read_text(encoding='utf-8'))
    manifest = json.loads((OUT / 'chapter-manifest.json').read_text(encoding='utf-8'))
    book = PdfReader(OUT / '杯中世界.pdf')
    require(len(book.pages) == layout['total_pages'], 'Full PDF page count differs from layout')
    require(bool(book.outline), 'Full PDF has no chapter navigation')
    require(bool(manifest), 'Chapter manifest is empty')
    expected_ids = {p.stem for p in (ROOT / 'chapters').glob('*.md')}
    actual_ids = {c['id'] for c in manifest}
    require(actual_ids == expected_ids and len(actual_ids) == len(manifest),
            'Missing or duplicate exported chapters')
    require(all(p['gap'] >= -0.1 for p in layout['pages']), 'PDF body overlaps footnotes')
    require(sum(c['pages'] for c in manifest) == len(layout['pages']),
            'Chapter exports do not cover all content pages')

    with ZipFile(OUT / '杯中世界逐章阅读.zip') as archive:
        require(archive.testzip() is None, 'Chapter ZIP is corrupt')
        for chapter in manifest:
            reader = PdfReader(OUT / '逐章阅读' / chapter['pdf'])
            require(len(reader.pages) == chapter['pages'], f'Chapter page count: {chapter["id"]}')
            require(bool(reader.outline), f'Chapter has no bookmark: {chapter["id"]}')
            require(len(chapter['full_book_pages']) == chapter['pages'] and
                    all(1 <= p <= len(book.pages) for p in chapter['full_book_pages']),
                    f'Invalid chapter page mapping: {chapter["id"]}')
            for key in ('pdf', 'markdown'):
                require('逐章阅读/' + chapter[key] in archive.namelist(),
                        f'Chapter missing from ZIP: {chapter[key]}')
            require((SITE / 'chapters' / f'{chapter["id"]}.html').is_file(),
                    f'Chapter missing from website: {chapter["id"]}')

    require((SITE / 'index.html').is_file(), 'Website has no entrypoint')
    require((SITE / '.nojekyll').is_file(), 'Website has no .nojekyll marker')
    html_files = list(SITE.rglob('*.html'))
    require(len(html_files) == len(manifest) + 2 and (SITE / '404.html').is_file(),
            'Unexpected number of Material web pages')
    for page in html_files:
        parser = Links()
        html = page.read_text(encoding='utf-8')
        parser.feed(html)
        require('见 PDF 与写作工程中的图像资源' not in html,
                f'Unrendered illustration placeholder: {page.relative_to(SITE)}')
        require('art-viewport' not in html, 'Legacy positioned image viewport remains')
        if page.parent.name == 'chapters':
            raw = (ROOT / 'chapters' / (page.stem + '.md')).read_text(encoding='utf-8')
            expected_figures = []
            heading = ''
            for line in raw.splitlines():
                title = re.match(r'^#{1,6} (.+)$', line)
                if title:
                    heading = title.group(1)
                marker = re.match(r'^@(art|leaf|composition) (\w+)', line)
                if marker:
                    kind, key = marker.groups()
                    if kind != 'art':
                        key = kind + '-' + key
                    expected_figures.append((key, heading))
            opener = {'04': 'wine', '13': 'tea', '16': 'coffee'}.get(page.stem)
            if opener:
                expected_figures.insert(0, (opener, re.search(r'^# (.+)$', raw, re.M).group(1)))
            require(parser.compositions == len(re.findall(r'^@composition coffee$', raw, re.M)),
                    f'Missing coffee composition diagram: {page.relative_to(SITE)}')
        elif page.name == 'index.html':
            expected_figures = [('cover', '杯中世界')]
        else:
            expected_figures = []
        require(parser.figures == expected_figures,
                f'Illustration order or section differs from manuscript: {page.relative_to(SITE)}; '
                f'expected {expected_figures}, got {parser.figures}')
        require(len(parser.images) == len(expected_figures),
                f'Missing image element: {page.relative_to(SITE)}')
        for image in parser.images:
            require(bool(image.get('alt', '').strip()) and bool(image.get('src')),
                    f'Image missing source or alt text: {page.relative_to(SITE)}')
        for (key, _), image in zip(parser.figures, parser.images):
            require(Path(urlsplit(image['src']).path).stem == key,
                    f'Wrong image for {key}: {page.relative_to(SITE)}')
        for link in parser.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            if not url.path:
                require(not url.fragment or unquote(url.fragment) in parser.ids,
                        f'Broken section or footnote anchor: {page.relative_to(SITE)}: {link}')
                continue
            if url.path.startswith('/'):
                require(page.name == '404.html' and url.path.startswith(SITE_BASE),
                        f'Link breaks project Pages base path: {link}')
                target = (SITE / unquote(url.path.removeprefix(SITE_BASE))).resolve()
            else:
                target = (page.parent / unquote(url.path)).resolve()
            if target.is_dir():
                target = target / 'index.html'
            require(target.is_relative_to(SITE.resolve()) and target.is_file(),
                    f'Broken local link in {page.relative_to(SITE)}: {link}')
    for image in (SITE / 'assets').glob('*.webp'):
        with Image.open(image) as asset:
            asset.verify()
    print(f'Validated {len(book.pages)} PDF pages, {len(manifest)} chapters, '
          f'{len(html_files)} web pages and all local links.')


if __name__ == '__main__':
    check()
