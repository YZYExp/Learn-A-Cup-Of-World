"""Check real build outputs before uploading or deploying them."""
from html.parser import HTMLParser
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

from pypdf import PdfReader
from PIL import Image
from yaml import safe_load
import fitz

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from book_structure import CHAPTERS, BY_ID, BOOK, chapter_text, chapter_title, chapter_link_id, figure_number, validate_structure
from scripts.update_catalog import catalog as source_catalog
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


def check(book_only=False):
    validate_structure()
    require(source_catalog() in (ROOT / 'README.md').read_text(), 'Source-reading catalog differs from book manifest')
    if (ROOT / '.git').exists():
        tracked = subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
        artifacts = [p for p in tracked if p.startswith('books/') or p.endswith(('.pdf','.zip','.bundle'))]
        require(not artifacts, f'Generated artifacts must not be tracked: {artifacts}')
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
    require([c['id'] for c in manifest] == [c['id'] for c in CHAPTERS], 'Chapter order differs from book manifest')
    require(all(c['title'] == chapter_title(BY_ID[c['id']]) for c in manifest), 'Chapter display title differs from book manifest')
    require([entry['/Title'] for entry in book.outline] == ['署名与许可']+[chapter_title(c) for c in CHAPTERS],
            'PDF bookmarks differ from chapter reading order')
    for destination,chapter in zip(book.outline[1:], manifest):
        require(book.get_destination_page_number(destination)+1 == chapter['full_book_pages'][0],
                f'Chapter bookmark points to the wrong page: {chapter["id"]}')
    require(all(p['gap'] >= -0.1 for p in layout['pages']), 'PDF body overlaps footnotes')
    require(sum(c['pages'] for c in manifest) == len(layout['pages']),
            'Chapter exports do not cover all content pages')
    # Compare manuscript citations with each physical page, including 3-digit IDs.
    catalog = {s['id']: s for s in json.loads((ROOT / 'research/sources.json').read_text())}
    manuscript_pages = []
    chapter_links = {}
    for chapter in CHAPTERS:
        pieces = re.split(r'<!-- page: ([^|]+)\|([^|]+)\|(.+?) -->\s*', chapter_text(chapter))
        for index in range(1, len(pieces), 4):
            ident, _, title, body = pieces[index:index + 4]
            refs = set(re.findall(r'\[(\d{2,3})\]', body))
            manuscript_pages.append((ident, title, refs))
            chapter_links[(ident,title)] = [chapter_link_id(target) for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^)\s]+\.md)\)',body)]
    require(len(manuscript_pages) == len(layout['pages']), 'Manuscript page count differs from layout')
    for (ident, title, refs), page in zip(manuscript_pages, layout['pages']):
        require((ident, title) == (page['chapter'], page['title']), 'Manuscript page order differs from layout')
        require(refs <= set(page['refs']) and refs <= catalog.keys(),
                f'Missing page-local citations: {ident} / {title}')
        rendered = book.pages[page['page'] - 1].extract_text()
        for ref in refs:
            require(rendered.count(f'[{ref}]') >= 2,
                    f'Citation or footnote missing from PDF page {page["page"]}: [{ref}]')
    # Three-digit references must survive pagination and remain clickable.
    sources = {s['id']: s for s in json.loads((ROOT / 'research/sources.json').read_text())}
    chapter_destinations = {c['id']:c['full_book_pages'][0]-1 for c in manifest}
    with fitz.open(OUT / '杯中世界.pdf') as rendered:
        for item in layout['pages']:
            page = rendered[item['page'] - 1]
            visible = re.sub(r'\s+', '', page.get_text())
            destinations = {link.get('uri') for link in page.get_links()}
            internal_pages = {link.get('page') for link in page.get_links() if link['kind']==fitz.LINK_GOTO}
            # ReportLab /Fit destinations can be exposed as named, 1-based pages.
            internal_pages.update(int(link['page'])-1 for link in page.get_links()
                                  if link['kind']==fitz.LINK_NAMED and str(link.get('page','')).isdigit())
            for target in chapter_links[(item['chapter'],item['title'])]:
                require(chapter_destinations[target] in internal_pages,
                        f'Chapter link missing or misdirected on PDF page {item["page"]}: {target}')
            for ident in item['refs']:
                require(ident in sources, f'Unknown reference: {ident}')
                if len(ident) >= 3:
                    require(f'[{ident}]' in visible and sources[ident]['url'] in destinations,
                            f'Reference {ident} missing text or link on PDF page {item["page"]}')
    main_md=OUT / '杯中世界可编辑稿.md'
    chapter_mds=[OUT / '逐章阅读' / c['markdown'] for c in manifest]
    for md in [main_md]+chapter_mds:
        text=md.read_text(encoding='utf-8')
        require('配图见 PDF' not in text and '（配图 ' not in text,
                f'Image placeholder remains: {md.name}')
        for target in re.findall(r'!\[[^\]]*\]\(([^)]+)\)',text):
            require((md.parent/target).resolve().is_file(),
                    f'Broken Markdown figure: {md.name} -> {target}')
        for target in re.findall(r'(?<!!)\[[^\]]*\]\(([^)]+\.md)\)', text):
            if not urlsplit(target).scheme:
                require((md.parent/target).resolve().is_file(),
                        f'Broken Markdown chapter link: {md.name} -> {target}')
    require(sum(len(re.findall(r'!\[', (ROOT / c['source']).read_text())) for c in CHAPTERS) == len(BOOK['figures']),
            'Chapter illustration manifest differs from manuscripts')
    full_text=main_md.read_text(encoding='utf-8')
    for figure in BOOK['figures']:
        owner=(ROOT / BY_ID[figure['chapter']]['source']).read_text()
        require('../'+figure['asset'] in owner and f'**图 {figure["display_id"]}　' in owner and f'**图 {figure["display_id"]}　' in full_text,
                f'Illustration owner or displayed number differs from manifest: {figure["id"]}')
    figures=json.loads((ROOT/'assets/figure-plan.json').read_text(encoding='utf-8'))
    full_text=main_md.read_text(encoding='utf-8')
    for manuscript in (ROOT / 'chapters').glob('*.md'):
        raw = manuscript.read_text(encoding='utf-8')
        for body in re.split(r'<!-- page: [^>]+ -->\s*', raw)[1:]:
            for image in re.finditer(r'!\[[^\]]+\]\([^)]*\)', body):
                require(re.match(r'\s*\*\*图 ', body[image.end():]) is not None,
                        f'Image and caption are separated in {manuscript.name}: {image.group()}')
    for f in figures:
        display_id=figure_number(f['id'])
        require(f'**图 {display_id}　' in full_text,
                f'Figure has no Markdown caption: {f["id"]}')
        raw=(ROOT/'chapters'/f'{f["chapter"]}.md').read_text()
        image=re.search(r'!\[[^\]]+\]\(\.\./assets/figures/'+re.escape(f['id'])+r'\.png\)',raw)
        require(image is not None, f'Figure missing from manuscript: {f["id"]}')
        caption_block=raw[image.end():].split('<!-- page:')[0]
        require('**图例。**' in caption_block,f'Figure has no Markdown legend: {f["id"]}')
        require((ROOT/'assets/figures'/f'{f["id"]}.png').is_file(),
                f'Figure image is missing: {f["id"]}')
        if f['mode'] != 'scene':
            with fitz.open(ROOT/'assets/figures'/f'{f["id"]}.pdf') as master:
                visible=''.join(page.get_text() for page in master)
            normalized=re.sub(r'\s+','',visible)
            if f['mode'] == 'tea_adjustment':
                for row in f['steps']:
                    for label in row:
                        require(re.sub(r'\s+', '', label) in normalized,
                                f'Tea adjustment label clipped from figure {f["id"]}: {label}')
            for forbidden in (f'图{display_id}',f['title'],'本书绘制的教学示意','AI教学插画','含义与边界见图例'):
                require(re.sub(r'\s+','',forbidden) not in normalized,
                        f'Caption prose is baked into figure {f["id"]}: {forbidden}')

    pdfs = list(OUT.rglob('*.pdf'))
    require(pdfs == [OUT / '杯中世界.pdf'], 'Build must produce only one full-book PDF')
    require(not list(OUT.rglob('*.zip')), 'Obsolete chapter ZIP remains in build output')
    for chapter in manifest:
        require('pdf' not in chapter, 'Chapter manifest must not advertise a chapter PDF')
        require(len(chapter['full_book_pages']) == chapter['pages'] and
                all(1 <= p <= len(book.pages) for p in chapter['full_book_pages']),
                f'Invalid chapter page mapping: {chapter["id"]}')
        require((OUT / '逐章阅读' / chapter['markdown']).is_file(),
                f'Missing chapter Markdown: {chapter["id"]}')
        if not book_only:
            require((SITE / 'chapters' / f'{chapter["id"]}.html').is_file(),
                    f'Chapter missing from website: {chapter["id"]}')

    if book_only:
        print(f'Validated {len(book.pages)} PDF pages, {len(manifest)} chapters, '
              f'{len(figures)} teaching figures, legends and all Markdown image links; only one PDF.')
        return

    require(not (SITE / 'downloads').exists(), 'Website must use Release downloads')
    require(not list(SITE.rglob('*.pdf')) and not list(SITE.rglob('*.zip')),
            'Website includes generated PDFs or archives')
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
            raw = chapter_text(BY_ID[page.stem])
            expected_figures = []
            heading = ''
            for line in raw.splitlines():
                title = re.match(r'^#{1,6} (.+)$', line)
                if title:
                    heading = title.group(1)
                teaching = re.match(r'^!\[[^\]]+\]\(\.\./assets/figures/([\w-]+)\.png\)$', line)
                if teaching:
                    expected_figures.append((teaching.group(1), heading))
            opener = {'04': 'wine', '13': 'tea', '16': 'coffee'}.get(page.stem)
            if opener:
                expected_figures.insert(0, (opener, re.search(r'^# (.+)$', raw, re.M).group(1)))
            require(parser.compositions == len(re.findall(r'!\[[^\]]+\]\(\.\./assets/figures/composition-coffee\.png\)', raw)),
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
            require(Path(urlsplit(image['src']).path).stem == key.removeprefix('teaching-'),
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
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--book-only',action='store_true',help='Validate reading outputs without building HTML')
    check(book_only=parser.parse_args().book_only)
