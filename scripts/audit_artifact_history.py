# SPDX-License-Identifier: MIT
"""Measure generated artifacts in one Git ref without rewriting any history."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def git(*args, input=None):
    return subprocess.check_output(['git', *args], cwd=ROOT, input=input)


def category(path):
    if path.startswith('books/'):
        return 'books'
    if path.startswith('assets/figures/') and path.endswith('.pdf'):
        return 'figure_pdf_masters'
    if path == 'history/cup-world-original.bundle':
        return 'redundant_history_bundle'
    return None


def audit(ref):
    sha = git('rev-parse', '--verify', ref + '^{commit}').decode().strip()
    tree = []
    for record in git('ls-tree', '-rlz', sha).decode().split('\0'):
        if record:
            info, path = record.split('\t', 1)
            _, kind, oid, size = info.split()
            if kind == 'blob':
                tree.append(dict(path=path, oid=oid, size=int(size)))
    names = defaultdict(set)
    for record in git('rev-list', '--objects', sha).decode().splitlines():
        oid, _, path = record.partition(' ')
        if category(path):
            names[oid].add(path)
    payload = ''.join(oid + '\n' for oid in names).encode()
    blobs = []
    for line in git('cat-file', '--batch-check=%(objectname) %(objecttype) %(objectsize)', input=payload).decode().splitlines():
        oid, kind, size = line.split()
        if kind == 'blob':
            blobs.append(dict(oid=oid, size=int(size), paths=sorted(names[oid])))
    groups = {}
    for key in ('books', 'figure_pdf_masters', 'redundant_history_bundle'):
        current = [f for f in tree if category(f['path']) == key]
        historic = [b for b in blobs if any(category(p) == key for p in b['paths'])]
        groups[key] = dict(current_files=len(current), current_bytes=sum(f['size'] for f in current),
                           historical_unique_blobs=len(historic),
                           historical_uncompressed_blob_bytes=sum(b['size'] for b in historic))
    return dict(ref=ref, commit=sha, scope='The selected ref and its ancestors, excluding other branches',
                size_units='bytes; blob sizes are uncompressed, not clone traffic or Git pack size',
                tracked_tree_bytes=sum(f['size'] for f in tree), categories=groups,
                historical_artifact_unique_blobs=len(blobs),
                historical_artifact_uncompressed_blob_bytes=sum(b['size'] for b in blobs),
                largest_historical_artifacts=sorted(blobs, key=lambda b:b['size'], reverse=True)[:10])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ref', default='HEAD')
    args = parser.parse_args()
    print(json.dumps(audit(args.ref), ensure_ascii=False, indent=2))
