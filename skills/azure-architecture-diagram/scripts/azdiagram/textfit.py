"""Font discovery and text measurement used for fitting, wrapping and validation."""
import os
from functools import lru_cache

from PIL import ImageFont

_REGULAR = ["C:/Windows/Fonts/malgun.ttf", "/System/Library/Fonts/AppleSDGothicNeo.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansKR-Regular.ttf"]
_BOLD = ["C:/Windows/Fonts/malgunbd.ttf", "/System/Library/Fonts/AppleSDGothicNeo.ttc",
         "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
         "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
         "/usr/share/fonts/truetype/noto/NotoSansKR-Bold.ttf"]
_REF = 100  # measure once at 100px and scale linearly


@lru_cache(None)
def _font(bold):
    env = os.environ.get("AZDIAGRAM_FONT_BOLD" if bold else "AZDIAGRAM_FONT")
    for path in [env] + (_BOLD if bold else _REGULAR):
        if path and os.path.exists(path):
            return ImageFont.truetype(path, _REF)
    raise RuntimeError("No CJK-capable font found. Set AZDIAGRAM_FONT and AZDIAGRAM_FONT_BOLD "
                       "to .ttf/.ttc files (the same family the SVG uses).")


def width(text, size, bold=False):
    return _font(bold).getlength(text) * size / _REF


def ink_box(text, x, y, size, bold=False, anchor="start", runs=None):
    """Visible ink box (x, y, w, h) of `text` (or of mixed-weight `runs`) drawn with its baseline at y."""
    k = size / _REF
    if runs:
        boxes = [_font(b).getbbox(t, anchor="ls") for t, b in runs if t.strip()] or [(0, 0, 0, 0)]
        left, top, bottom = boxes[0][0], min(b[1] for b in boxes), max(b[3] for b in boxes)
        w = runs_width(runs, size)
        x0 = x - w if anchor == "end" else x - w / 2 if anchor == "middle" else x
        return (x0 + left * k, y + top * k, w - left * k, (bottom - top) * k)
    left, top, right, bottom = _font(bold).getbbox(text, anchor="ls")
    w = width(text, size, bold)
    x0 = x - w if anchor == "end" else x - w / 2 if anchor == "middle" else x
    return (x0 + left * k, y + top * k, (right - left) * k, (bottom - top) * k)


def fit(text, size, bold, max_width, min_size):
    """Shrink in 0.5px steps until the text fits. Returns (size, fits)."""
    s = float(size)
    while s > min_size and width(text, s, bold) > max_width:
        s -= 0.5
    return s, width(text, s, bold) <= max_width + 0.5


# A wrapped line must not start with a lone separator or closing mark ("정제 · 변환" breaks after "·").
_NO_LINE_START = frozenset("·/|→←↔-–—)]},.:;")


def wrap(text, size, bold, max_width):
    """Greedy word wrap on spaces (Korean prose wraps between words)."""
    words = []
    for word in text.split():
        if words and word in _NO_LINE_START:
            words[-1] += " " + word
        else:
            words.append(word)
    lines, cur = [], ""
    for word in words:
        cand = f"{cur} {word}" if cur else word
        if not cur or width(cand, size, bold) <= max_width:
            cur = cand
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def parse_runs(s):
    """'**APIM**으로 전달' -> [('APIM', True), ('으로 전달', False)]."""
    return [(p, i % 2 == 1) for i, p in enumerate(str(s).split("**")) if p]


def runs_width(runs, size):
    return sum(width(t, size, b) for t, b in runs)


def _words(runs):
    """Space-separated words; one word may mix weights, e.g. **Fabric IQ**로. A lone separator is
    kept with the previous word so no line starts with it."""
    words, cur = [], []
    for t, b in runs:
        for k, piece in enumerate(t.split(" ")):
            if k and cur:
                words.append(cur)
                cur = []
            if piece:
                cur.append((piece, b))
    if cur:
        words.append(cur)
    glued = []
    for w in words:
        if glued and "".join(t for t, _ in w) in _NO_LINE_START:
            glued[-1] = glued[-1] + [(" ", glued[-1][-1][1] and w[0][1])] + w
        else:
            glued.append(w)
    return glued


def _join(words):
    out = []
    for w in words:
        if out:
            out.append((" ", out[-1][1] and w[0][1]))  # the space is bold only inside a bold phrase
        out.extend(w)
    merged = []
    for t, b in out:
        if merged and merged[-1][1] == b:
            merged[-1] = (merged[-1][0] + t, b)
        else:
            merged.append((t, b))
    return merged


def wrap_rich(s, size, max_width):
    """Greedy word wrap of text with **bold** markup. Returns one run list per line."""
    lines, cur = [], []
    for w in _words(parse_runs(s)):
        if not cur or runs_width(_join(cur + [w]), size) <= max_width:
            cur.append(w)
        else:
            lines.append(_join(cur))
            cur = [w]
    if cur:
        lines.append(_join(cur))
    return lines
