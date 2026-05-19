#!/usr/bin/env python3
"""
write_svg.py - Reliable UTF-8 SVG writer for ppt-master

On Windows, the AI's Write tool can inconsistently write GBK/CP936 instead
of UTF-8 when content contains certain CJK characters. This thin wrapper
guarantees UTF-8 output by always using explicit `encoding='utf-8'` in open().

Usage:
    python write_svg.py <output_path>
    # reads SVG from stdin

    python write_svg.py <output_path> <svg_content>
    # writes svg_content to output_path as UTF-8

    # Inline mode — pass SVG content as second argument:
    python write_svg.py "path/to/01_cover.svg" '<svg ...>...</svg>'

    # Or use with heredoc via Python -c:
    python -c "
import sys
svg = '''<svg>...</svg>'''
with open(sys.argv[1], 'w', encoding='utf-8') as f:
    f.write(svg)
print('Written:', sys.argv[1])
" "path/to/file.svg"
"""

import sys
import os

def write_svg(path: str, content: str = None) -> None:
    """
    Write SVG content to path using explicit UTF-8 encoding.
    On Windows, always prefer this over the AI's Write tool for SVG files.
    """
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    if content is None:
        # Read SVG content from stdin
        content = sys.stdin.read()
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[write_svg] Written (UTF-8): {path}")


def verify_utf8(path: str) -> bool:
    """
    Verify that a file is valid UTF-8. Returns True if read succeeds.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            f.read()
        return True
    except UnicodeDecodeError as e:
        print(f"[write_svg] ERROR: {path} is NOT UTF-8: {e}")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python write_svg.py <output_path> [svg_content]")
        sys.exit(1)

    output_path = sys.argv[1]

    if len(sys.argv) >= 3:
        svg_content = sys.argv[2]
    else:
        svg_content = sys.stdin.read()

    write_svg(output_path, svg_content)

    # Auto-verify after write
    if not verify_utf8(output_path):
        sys.exit(1)
