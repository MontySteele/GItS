"""A tracked file carrying a git conflict marker is never right.

One shipped to docs/current/BACKLOG.md on 2026-08-30: a fold resolved a
register lint's DUPLICATE finding without reading the two lines above it,
and an explicit `git add` blessed the marker lines a piped merge output had
hidden. No gate looked. This one does: any tracked text file whose line
starts with '<<<<<<< ' or '>>>>>>> ' is a finding. The middle '=======' is
deliberately not matched alone -- setext headings use runs of equals signs,
and a real conflict always carries the other two markers.
"""
import subprocess, sys

TEXT_SUFFIXES = ('.md', '.py', '.yaml', '.yml', '.cs', '.ps1', '.tscn', '.tsv', '.txt')
SKIP_PREFIXES = ('review/qa/',)  # sealed transcripts may quote anything

def find_markers(text):
    return [i + 1 for i, line in enumerate(text.splitlines())
            if line.startswith('<<<<<<< ') or line.startswith('>>>>>>> ')]

def main():
    files = subprocess.run(['git', 'ls-files'], capture_output=True, text=True,
                           check=True).stdout.splitlines()
    findings = []
    for f in files:
        if not f.endswith(TEXT_SUFFIXES) or f.startswith(SKIP_PREFIXES):
            continue
        try:
            text = open(f, encoding='utf-8', errors='replace').read()
        except OSError:
            continue
        for ln in find_markers(text):
            findings.append(f'{f}:{ln}: conflict marker in a tracked file')
    for x in findings:
        print(x)
    if findings:
        print(f'{len(findings)} finding(s). Resolve the merge; never git add a file still carrying markers.')
        return 1
    print('conflict-markers: no tracked file carries one')
    return 0

if __name__ == '__main__':
    sys.exit(main())
