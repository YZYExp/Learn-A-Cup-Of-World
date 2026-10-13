# SPDX-License-Identifier: MIT
"""Prepare chapter Markdown and navigation metadata without chapter PDFs or ZIPs."""
from collections import defaultdict
from pathlib import Path
import json
import re
import shutil

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'output'
DEST = OUT / '逐章阅读'
PUBLICATION = json.loads((ROOT / 'publication.json').read_text(encoding='utf-8'))


def export():
    # Remove obsolete generated chapter PDFs when rebuilding an old checkout.
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True)
    (OUT / '杯中世界逐章阅读.zip').unlink(missing_ok=True)
    layout = json.loads((OUT / 'layout-check.json').read_text(encoding='utf-8'))
    chunks = re.split(r'\n---\n', (OUT / '杯中世界可编辑稿.md').read_text(encoding='utf-8'))[1:]
    assert len(chunks) == len(layout['pages'])
    groups = defaultdict(list)
    for page, text in zip(layout['pages'], chunks):
        groups[page['chapter']].append((page, text.strip()))
    manifest = []
    for ident, items in groups.items():
        raw = (ROOT / 'chapters' / f'{ident}.md').read_text(encoding='utf-8')
        match = re.search(r'^# (.+)$', raw, re.M)
        title = match.group(1) if match else '读前的话'
        filename = re.sub(r'\s+', '', title)
        if ident == '00':
            filename = '00-' + filename
        text = '\n\n---\n\n'.join(chunk for _, chunk in items).replace('](assets/', '](../assets/')
        credit = ('> ' + PUBLICATION['credit'] + '。' + PUBLICATION['ai_disclosure'] + '\n>\n'
                  '> 许可：[' + PUBLICATION['content_license'] + ']('
                  + PUBLICATION['content_license_url'] + ')；[作品出处]('
                  + PUBLICATION['source_url'] + ')。分享或改编时保留署名与许可链接，并注明改动；仅对有权许可且依法受保护的部分适用，第三方材料除外。\n\n')
        if text.startswith('# '):
            heading, _, remainder = text.partition('\n')
            text = heading + '\n\n' + credit + remainder.lstrip()
        else:
            text = '# ' + title + '\n\n' + credit + text
        (DEST / (filename + '.md')).write_text(text + '\n', encoding='utf-8')
        manifest.append(dict(id=ident, title=title, markdown=filename + '.md',
                             pages=len(items), full_book_pages=[page['page'] for page, _ in items]))
    (OUT / 'chapter-manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'chapters': len(manifest), 'chapter_pdfs': 0, 'archives': 0}, ensure_ascii=False))


if __name__ == '__main__':
    export()
