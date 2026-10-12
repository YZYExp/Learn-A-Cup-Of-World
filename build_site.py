"""Build a portable static reader from freshly exported book chapters."""
from html import escape
import json
from pathlib import Path
import re
import shutil
from urllib.parse import quote

import markdown

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'output'
SITE = ROOT / 'site'

CSS = """
:root { color-scheme: light; --ink: #222; --muted: #626762; --accent: #526852; }
* { box-sizing: border-box; }
body { margin: 0; color: var(--ink); background: #f8f5ee;
  font: 17px/1.85 system-ui, -apple-system, "Noto Sans SC", sans-serif; }
a { color: var(--accent); text-underline-offset: .2em; overflow-wrap: anywhere; }
a:hover { color: #263c26; }
header, main, footer { max-width: 900px; margin: auto; padding: 24px; }
header { display: flex; flex-wrap: wrap; gap: 16px; align-items: center; }
header a { text-decoration: none; }
header .brand { font-weight: 700; margin-right: auto; }
h1, h2, h3 { line-height: 1.5; }
h1 { font-size: 2rem; }
h2 { margin-top: 2em; font-size: 1.4rem; }
.intro, footer, .note { color: var(--muted); }
.downloads, .pager { display: flex; flex-wrap: wrap; gap: 16px; margin: 24px 0; }
.downloads a { padding: 8px 16px; border: 1px solid #ccd5cc; border-radius: 6px; }
.contents { padding-left: 1.5em; }
.contents li { margin: 12px 0; padding-left: 8px; }
.contents .pdf { margin-left: 12px; font-size: .85em; }
article { padding: 24px; background: #fff; border-radius: 8px; }
article p { overflow-wrap: anywhere; }
article ul { padding-left: 1.5em; }
.table-scroll { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: .9em; }
th, td { padding: 10px; border: 1px solid #d9d9d9; min-width: 100px; text-align: left; }
th { background: #e9eeea; }
hr { border: 0; border-top: 1px solid #d9d9d9; margin: 36px 0; }
.pager { justify-content: space-between; }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 4px; }
@media (max-width: 600px) { header, main, footer { padding: 16px; }
  article { padding: 16px; } h1 { font-size: 1.6rem; } }
@media print { header, .downloads, .pager, footer { display: none; }
  body, article { background: white; } main { max-width: none; padding: 0; } }
"""


def document(title, content, prefix=''):
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="杯中世界：酒、茶、咖啡的起源、发展、制作与风味。">
<title>{escape(title)} · 杯中世界</title>
<link rel="stylesheet" href="{prefix}style.css">
</head>
<body>
<header><a class="brand" href="{prefix}index.html">杯中世界</a>
<a href="{prefix}index.html#contents">章节目录</a>
<a href="{prefix}downloads/{quote('杯中世界.pdf')}">全书 PDF</a></header>
<main>{content}</main>
<footer>个人兴趣读本 · AI 辅助写作与插画 · 资料出处见正文。
完整插画、当页排版与参考资料总目见全书 PDF。</footer>
</body>
</html>
'''


def chapter_html(text, sources):
    # Link numbered citations as well as the existing page-local source lists.
    def citation(match):
        ident = match.group(1)
        if ident not in sources:
            return match.group(0)
        url = sources[ident]['url']
        return f'<sup><a href="{escape(url, quote=True)}">[{ident}]</a></sup>'

    text = re.sub(r'\[(\d{2})\](?!\()', citation, text)
    body = markdown.markdown(text, extensions=['tables', 'sane_lists'])
    return body.replace('<table>', '<div class="table-scroll"><table>').replace(
        '</table>', '</table></div>')


def build():
    manifest = json.loads((OUT / 'chapter-manifest.json').read_text(encoding='utf-8'))
    sources = {s['id']: s for s in json.loads(
        (ROOT / 'research/sources.json').read_text(encoding='utf-8'))}
    # Rebuild from scratch so deleted/renamed chapters cannot remain on the site.
    if SITE.exists():
        shutil.rmtree(SITE)
    (SITE / 'chapters').mkdir(parents=True)
    downloads = SITE / 'downloads'
    downloads.mkdir()
    for filename in ('杯中世界.pdf', '杯中世界可编辑稿.md', '杯中世界逐章阅读.zip'):
        shutil.copy2(OUT / filename, downloads / filename)
    shutil.copytree(OUT / '逐章阅读', downloads / '逐章阅读')
    (SITE / '.nojekyll').touch()
    (SITE / 'style.css').write_text(CSS, encoding='utf-8')

    entries = []
    for index, chapter in enumerate(manifest):
        ident, title = chapter['id'], chapter['title']
        pdf_url = 'downloads/' + quote('逐章阅读/' + chapter['pdf'], safe='/')
        entries.append(f'<li><a href="chapters/{ident}.html">{escape(title)}</a>'
                       f'<a class="pdf" href="{pdf_url}">PDF</a></li>')
        text = (OUT / '逐章阅读' / chapter['markdown']).read_text(encoding='utf-8')
        heading = '' if re.search(r'^# ', text, re.M) else f'<h1>{escape(title)}</h1>'
        previous = (f'<a href="{manifest[index - 1]["id"]}.html">← 上一章</a>'
                    if index else '<a href="../index.html">← 返回目录</a>')
        following = (f'<a href="{manifest[index + 1]["id"]}.html">下一章 →</a>'
                     if index + 1 < len(manifest) else '<a href="../index.html">返回目录 →</a>')
        content = (f'<div class="downloads"><a href="../{pdf_url}">下载本章 PDF</a></div>'
                   f'<article>{heading}{chapter_html(text, sources)}</article>'
                   f'<nav class="pager" aria-label="章节翻页">{previous}{following}</nav>')
        (SITE / 'chapters' / f'{ident}.html').write_text(
            document(title, content, '../'), encoding='utf-8')

    links = ''.join(f'<a href="downloads/{quote(filename)}">{label}</a>' for filename, label in (
        ('杯中世界.pdf', '全书 PDF'), ('杯中世界逐章阅读.zip', '逐章阅读 ZIP'),
        ('杯中世界可编辑稿.md', '可编辑 Markdown')))
    content = f'''<h1>杯中世界</h1>
<p class="intro">酒、茶、咖啡的起源与风味 · 个人兴趣阅读与学习</p>
<p>从原料与加工开始，读懂一杯饮料。可以顺读，也可以先挑喜欢的一章。</p>
<div class="downloads">{links}</div>
<p class="note">网页版提供完整文字、表格和原文引用链接；图解阅读请下载 PDF。</p>
<h2 id="contents">章节目录</h2>
<ol class="contents">{''.join(entries)}</ol>'''
    (SITE / 'index.html').write_text(document('酒、茶、咖啡的起源与风味', content), encoding='utf-8')
    print(json.dumps({'site': str(SITE), 'chapters': len(manifest)}, ensure_ascii=False))


if __name__ == '__main__':
    build()
