# SPDX-License-Identifier: MIT
"""One ordered chapter and figure manifest for PDF, Markdown and web readers."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent
BOOK = json.loads((ROOT / 'book.json').read_text(encoding='utf-8'))
CHAPTERS = BOOK['chapters']
BY_ID = {c['id']: c for c in CHAPTERS}
BY_FILENAME = {Path(c['source']).name: c for c in CHAPTERS}
FIGURES = {f['asset']: f for f in BOOK['figures']}
FIGURES_BY_ID = {f['id']: f for f in BOOK['figures']}


def chapter_title(chapter):
    number = chapter.get('number')
    return f'{number:02} {chapter["title"]}' if number else chapter['title']


def chapter_text(chapter):
    text = (ROOT / chapter['source']).read_text(encoding='utf-8')
    if re.search(r'^# ', text, re.M):
        text = re.sub(r'^# .+$', '# ' + chapter_title(chapter), text, count=1, flags=re.M)
    return text


def chapter_link_id(target):
    """Resolve a relative Markdown chapter link to its stable PDF bookmark."""
    path = target.split('#', 1)[0]
    chapter = BY_FILENAME.get(path)
    if chapter is None:
        raise ValueError(f'Unknown chapter link: {target}')
    return chapter['id']


def figure_number(stable_id):
    return FIGURES_BY_ID[stable_id]['display_id']


def validate_structure():
    assert len(BY_ID) == len(CHAPTERS) == len(BY_FILENAME), 'Duplicate chapter identity'
    assert len({c['slug'] for c in CHAPTERS}) == len(CHAPTERS), 'Duplicate chapter URL'
    assert [c['order'] for c in CHAPTERS] == list(range(len(CHAPTERS))), 'Invalid reading order'
    main = [c for c in CHAPTERS if c['kind'] == 'chapter']
    assert [c['number'] for c in main] == list(range(1, len(main) + 1)), 'Invalid display numbers'
    expected = {c['source'] for c in CHAPTERS}
    assert expected == {p.relative_to(ROOT).as_posix() for p in (ROOT / 'chapters').glob('*.md')}, 'Chapter files differ from manifest'
    assert len(FIGURES) == len(FIGURES_BY_ID) == len(BOOK['figures']), 'Duplicate illustration identity'
    assert len({f['display_id'] for f in BOOK['figures']}) == len(BOOK['figures']), 'Duplicate figure number'
    for chapter in CHAPTERS:
        assert Path(chapter['source']).stem == chapter['id'] == chapter['slug'], chapter['id']
        raw = (ROOT / chapter['source']).read_text(encoding='utf-8')
        identities = re.findall(r'<!-- page: ([^|]+)\|([^|]+)\|', raw)
        assert identities and all(pair == (chapter['id'], chapter['part']) for pair in identities), chapter['id']
        headings = re.findall(r'^# (.+)$', raw, re.M)
        assert headings == ([chapter['title']] if chapter['kind'] != 'frontmatter' else []), chapter['id']
        for target in re.findall(r'\[[^\]]+\]\(([^)]+\.md)\)', raw):
            chapter_link_id(target)
    for figure in BOOK['figures']:
        assert figure['chapter'] in BY_ID and (ROOT / figure['asset']).is_file(), figure['id']


if __name__ == '__main__':
    validate_structure()
    print(f'{len(CHAPTERS)} chapter files; {len(BOOK["figures"])} chapter illustrations; structure valid.')
