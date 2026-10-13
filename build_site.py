# SPDX-License-Identifier: MIT
"""Prepare source-order illustrations and build the reader with MkDocs Material."""
from html import escape
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil

from mkdocs.commands.build import build as mkdocs_build
from mkdocs.config import load_config
from PIL import Image

from illustration_data import FRONT_ART, ART_LABELS
from figure_markup import IMAGE_RE, frontmatter_captions

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'output'
SITE = ROOT / 'site'
DOCS = ROOT / 'work' / 'web-docs'
PUBLICATION = json.loads((ROOT / 'publication.json').read_text(encoding='utf-8'))
FRONT_CAPTIONS = frontmatter_captions(ROOT)

# Navigation, tables, search and responsive layout use Material.
CSS = """
:root { --md-text-font: system-ui, -apple-system, "Noto Sans SC", sans-serif; }
.md-typeset { font-size: .85rem; line-height: 1.9; }
.md-typeset figure { width: 100%; margin: 1.5em 0 .5em; }
.md-typeset figure img { display: block; width: 100%; height: auto; margin: 0 auto; }
.md-typeset .downloads { display: flex; flex-wrap: wrap; gap: 1em; }
"""

DIAGRAMS = {
    'kinship': '饮品|材料与主要变化|饮用前的呈现\n酒|糖的准备 发酵 部分再蒸馏熟成|温度 稀释或调配\n茶|叶子加工 控制氧化及其他变化|以水冲泡或煮饮\n咖啡|果实处理 种子干燥与烘焙|研磨后冲煮',
    'evidence': '年代线索|地点与研究解释\n约一万三千年前|Raqefet 洞穴 石臼遗存与谷物酿造解释 [04]\n约公元前第七千纪|河南贾湖 米 蜂蜜与水果混合饮品 [02]\n约公元前 6000—5800 年|格鲁吉亚 葡萄酒相关证据 [03]',
    'tea': '茶类|入门观察方向\n绿茶|较早控制酶相关变化\n白茶 黄茶|分别关注萎凋干燥与闷黄\n乌龙 红茶|关注氧化与其他工序的安排\n黑茶|关注微生物相关加工过程',
}


def export_image(key, filename, rect):
    """Export a self-contained web asset from the PDF's source region."""
    with Image.open(ROOT / 'assets' / filename) as source:
        iw, ih = source.size
        box = tuple(round(value * scale) for value, scale in zip(
            rect, (iw / 1536, ih / 1024, iw / 1536, ih / 1024)))
        image = source.crop(box).convert('RGB')
        image.thumbnail((1400, 1400), Image.Resampling.LANCZOS)
        image.save(DOCS / 'assets' / f'{key}.webp', quality=92, method=6)


def illustration(key, prefix='../', eager=False):
    label = ART_LABELS[key]
    with Image.open(DOCS / 'assets' / f'{key}.webp') as image:
        width, height = image.size
    return (f'<figure data-art="{key}">'
            f'<img src="{prefix}assets/{key}.webp" alt="{escape(label, quote=True)}" '
            f'width="{width}" height="{height}" loading="{"eager" if eager else "lazy"}" '
            f'decoding="async"></figure>\n\n' + FRONT_CAPTIONS[key])


def chapter_figure(match):
    key, label = match.group('key'), match.group('alt')
    with Image.open(DOCS / 'assets/figures' / f'{key}.png') as image:
        width, height = image.size
    css = ' class="composition"' if key == 'composition-coffee' else ''
    return (f'<figure data-art="{key}"{css}>'
            f'<img src="../assets/figures/{key}.png" alt="{escape(label, quote=True)}" '
            f'width="{width}" height="{height}" loading="lazy" decoding="async"></figure>')


def table(text):
    rows = [row.strip() for row in text.strip().splitlines()]
    columns = len(rows[0].split('|'))
    return '\n'.join(['| ' + rows[0] + ' |',
                      '| ' + ' | '.join(['---'] * columns) + ' |']
                     + ['| ' + row + ' |' for row in rows[1:]])


def chapter_markdown(chapter, sources):
    raw = (ROOT / 'chapters' / f'{chapter["id"]}.md').read_text(encoding='utf-8')
    pieces = re.split(r'<!-- page: ([^|]+)\|([^|]+)\|(.+?) -->\s*', raw)
    bodies = [pieces[i + 3].strip() for i in range(1, len(pieces), 4)]
    text = '\n\n'.join(bodies)
    text = re.sub(r'^@table\n(.*?)\n@endtable$', lambda m: table(m.group(1)),
                  text, flags=re.S | re.M)
    text = re.sub(r'^@diagram (\w+)$', lambda m: table(DIAGRAMS[m.group(1)]), text, flags=re.M)
    text = IMAGE_RE.sub(chapter_figure, text)
    refs = set(re.findall(r'\[(\d{2})\]', text))
    extra_refs = {'15', '34', '37'} - refs if '@diagram kinship' in raw else set()
    text = re.sub(r'\[(\d{2})\]', r'[^\1]', text)
    if extra_refs:
        text += '\n\n补充资料：' + ' '.join(f'[^{ident}]' for ident in sorted(extra_refs))
    refs |= extra_refs
    if refs:
        text += '\n\n## 资料与原文\n\n'
        for ident in sorted(refs):
            source = sources[ident]
            text += (f'[^{ident}]: {source["publisher"]}，《{source["title"]}》，'
                     f'{source["year"]}。[原文]({source["url"]})\n\n')
    heading = re.search(r'^# .+$', text, re.M)
    if not heading:
        text = f'# {chapter["title"]}\n\n' + text
        heading = re.search(r'^# .+$', text, re.M)
    releases = PUBLICATION['source_url'].rstrip('/') + '/releases'
    intro = (f'\n\n<p class="downloads"><a href="{escape(releases, quote=True)}">'
             '下载全书 PDF（Release）</a></p>\n\n')
    opener = {'04': 'wine', '13': 'tea', '16': 'coffee'}.get(chapter['id'])
    if opener:
        intro += illustration(opener, eager=True) + '\n\n'
    text = text[:heading.end()] + intro + text[heading.end():]
    return text, pieces[2]


def build():
    manifest = json.loads((OUT / 'chapter-manifest.json').read_text(encoding='utf-8'))
    sources = {s['id']: s for s in json.loads((ROOT / 'research/sources.json').read_text(encoding='utf-8'))}
    if DOCS.exists():
        shutil.rmtree(DOCS)
    for directory in ('chapters', 'assets', 'stylesheets'):
        (DOCS / directory).mkdir(parents=True, exist_ok=True)
    stylesheet = f'stylesheets/reader.{sha256(CSS.encode()).hexdigest()[:12]}.css'
    (DOCS / stylesheet).write_text(CSS, encoding='utf-8')
    for key, (filename, rect) in FRONT_ART.items():
        export_image(key, filename, rect)
    (DOCS / 'assets/figures').mkdir()
    for image in (ROOT / 'assets/figures').glob('*.png'):
        shutil.copy2(image, DOCS / 'assets/figures' / image.name)

    groups = {}
    contents = []
    for chapter in manifest:
        path = f'chapters/{chapter["id"]}.md'
        text, part = chapter_markdown(chapter, sources)
        (DOCS / path).write_text(text, encoding='utf-8')
        groups.setdefault(part, []).append({chapter['title']: path})
        contents.append(f'- [{chapter["title"]}]({path})')
    releases = PUBLICATION['source_url'].rstrip('/') + '/releases'
    links = f'<a href="{escape(releases, quote=True)}">下载全书 PDF（Release）</a>'
    index = ('# 杯中世界\n\n酒、茶、咖啡的起源与风味 · 个人兴趣阅读与学习\n\n'
             '从原料与加工开始，读懂一杯饮料。可以顺读，也可以先挑喜欢的一章。\n\n'
             + illustration('cover', prefix='', eager=True)
             + f'\n\n<p class="downloads">{links}</p>\n\n'
             '网页版提供完整文字、插画、图解、表格和原文引用链接；需要分页阅读可在 Release 下载全书 PDF。\n\n'
             '## 章节目录\n\n' + '\n'.join(contents))
    (DOCS / 'index.md').write_text(index, encoding='utf-8')
    credit = (escape(PUBLICATION['credit'])
              + f' <a href="{PUBLICATION["content_license_url"]}">{PUBLICATION["content_license"]}</a>'
              + f' · <a href="{PUBLICATION["source_url"]}/blob/main/NOTICE.md">署名与许可说明</a>')
    config = load_config(str(ROOT / 'mkdocs.yml'), docs_dir=str(DOCS), site_dir=str(SITE),
                         nav=[{'阅读首页': 'index.md'}] + [{part: entries} for part, entries in groups.items()],
                         copyright=credit, extra_css=[stylesheet], strict=True)
    mkdocs_build(config)
    (SITE / '.nojekyll').touch()
    print(json.dumps({'site': str(SITE), 'chapters': len(manifest),
                      'renderer': 'MkDocs Material', 'illustrations': len(FRONT_ART) + sum(len(IMAGE_RE.findall(p.read_text())) for p in (ROOT / 'chapters').glob('*.md'))},
                     ensure_ascii=False))


if __name__ == '__main__':
    build()
