"""Check real build outputs before uploading or deploying them."""
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output'
SITE = ROOT / 'site'


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ('href', 'src') and value:
                self.links.append(value)


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
    require(len(html_files) == len(manifest) + 1, 'Unexpected number of web pages')
    for page in html_files:
        parser = Links()
        parser.feed(page.read_text(encoding='utf-8'))
        for link in parser.links:
            url = urlsplit(link)
            if url.scheme or url.netloc or not url.path:
                continue
            require(not url.path.startswith('/'), f'Link breaks project Pages base path: {link}')
            target = (page.parent / unquote(url.path)).resolve()
            require(target.is_relative_to(SITE.resolve()) and target.is_file(),
                    f'Broken local link in {page.relative_to(SITE)}: {link}')
    print(f'Validated {len(book.pages)} PDF pages, {len(manifest)} chapters, '
          f'{len(html_files)} web pages and all local links.')


if __name__ == '__main__':
    check()
