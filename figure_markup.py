# SPDX-License-Identifier: MIT
"""Shared Markdown figure syntax; caption prose stays in the manuscript."""
from pathlib import Path
import re

IMAGE_PATTERN = r'^!\[(?P<alt>[^\]]+)\]\((?P<path>\.\./assets/figures/(?P<key>[\w-]+)\.png)\)$'
IMAGE_RE = re.compile(IMAGE_PATTERN, re.M)


def frontmatter_captions(root):
    raw = (Path(root) / 'frontmatter/illustrations.md').read_text(encoding='utf-8')
    parts = re.split(r'<!-- figure: (\w+) -->\s*', raw)
    return {parts[i]: parts[i+1].strip() for i in range(1, len(parts), 2)}
