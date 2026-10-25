# SPDX-License-Identifier: MIT
"""Refresh the source-reading catalog from the canonical book manifest."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from book_structure import CHAPTERS, chapter_title, validate_structure

START = '<!-- chapter-catalog:start -->'
END = '<!-- chapter-catalog:end -->'


def catalog():
    rows = [START, '', '| 阅读顺序 | 章节源稿 |', '| --- | --- |']
    for chapter in CHAPTERS:
        number = str(chapter['number']) if chapter['number'] else '—'
        rows.append(f'| {number} | [{chapter_title(chapter)}]({chapter["source"]}) |')
    return '\n'.join(rows + ['', END])


if __name__ == '__main__':
    validate_structure()
    path = ROOT / 'README.md'
    text = path.read_text(encoding='utf-8')
    if START not in text:
        text = text.replace('## 开放许可', '## 分章目录\n\n' + START + '\n' + END + '\n\n## 开放许可', 1)
    before, rest = text.split(START, 1)
    _, after = rest.split(END, 1)
    path.write_text(before + catalog() + after, encoding='utf-8')
    print(f'Refreshed {len(CHAPTERS)} source-reading entries.')
