"""Themes. `style:` picks a preset over DEFAULT_THEME (`reference`, the default, follows the look of
public cloud reference architectures; `card` draws boxed cards). `theme:` deep-merges over both."""
import copy

INK, MUTED, LINE = "#102D46", "#4D6475", "#B9CBD6"
BLUE, TEAL, ORANGE, PURPLE, GRAY, RED = "#125FA9", "#007364", "#B54708", "#6941C6", "#62727F", "#B42318"

DEFAULT_THEME = {
    "font_family": "'Malgun Gothic', 'Apple SD Gothic Neo', 'Noto Sans KR', 'Noto Sans CJK KR', "
                   "'Segoe UI', sans-serif",
    "drawio_font": "Malgun Gothic",
    "min_font": 10,
    "scale": 1,
    "node_type": "card",
    "colors": {
        "ink": INK, "muted": MUTED, "line": LINE, "paper": "#FFFFFF", "accent": TEAL,
        "blue": BLUE, "teal": TEAL, "orange": ORANGE, "purple": PURPLE, "gray": GRAY, "red": RED,
    },
    "card": {"h": 62, "radius": 8, "icon": 36, "fill": "#FFFFFF", "stroke": LINE, "title": 15,
             "detail": 12.5, "chip_h": 30, "chip_fill": "#F1F6F9", "chip_stroke": "#D3E0E8"},
    "glyph": {"h": 44, "icon": 32, "title": 14, "detail": 12},
    "tile": {"h": 100, "icon": 48, "title": 14, "detail": 12},
    # Icon nodes: an icon (or a framed cluster) with its label below; the reference-style node.
    "icon": {"size": 56, "label_w": 140, "title": 14, "detail": 12.5, "gap": 8, "line_h": 18,
             "detail_line_h": 16, "max_lines": 3, "title_bold": False, "frame_pad": 10, "cluster_gap": 12,
             "item_scale": 1},
    "group": {"radius": 10, "icon": 20, "label": 13.5, "sublabel": 12, "dash": "7 5",
              "pad": [16, 44, 16, 16], "sw": 1.5, "tile": 0, "label_bold": True},
    "edge": {"width": 2.6, "label": 12.5, "gap": 6, "arrow": 9, "head": "filled", "label_bold": True},
    "badge": {"r": 13, "size": 14, "color": None, "on_line": True},
    # Every flow kind has its own line pattern, so the legend does not rely on color alone.
    "edge_kinds": {
        "data": {"color": TEAL, "dash": "16 6", "label": "데이터 수집 · 적재"},
        "request": {"color": BLUE, "dash": None, "label": "요청 · 질의"},
        "action": {"color": PURPLE, "dash": "8 4", "label": "업무 액션 · 도구 호출"},
        "feedback": {"color": ORANGE, "dash": "10 4 2 4", "label": "피드백 · 결과 반영"},
        "egress": {"color": RED, "dash": "10 4 2 4 2 4", "label": "인터넷 송신"},
        "control": {"color": GRAY, "dash": "3 4", "label": "운영 · 인증"},
    },
    # Frame strokes reach 3:1 against white, their own fill and the darkest group fill (#F4F1FB).
    "group_kinds": {
        "azure": {"fill": "#F6F9FC", "stroke": "#6890AB", "dash": False, "label": INK},
        "region": {"fill": "#F6F9FC", "stroke": "#6890AB", "dash": False, "label": INK},
        "vnet": {"fill": "#EEF5FA", "stroke": "#566A7A", "dash": True, "label": INK},
        "subnet": {"fill": "#FFFFFF", "stroke": "#698FA9", "dash": True, "label": INK},
        "fabric": {"fill": "#F1F8F6", "stroke": "#559588", "dash": False, "label": TEAL},
        "foundry": {"fill": "#F4F1FB", "stroke": "#8E7CC3", "dash": False, "label": "#5B3FA8"},
        "m365": {"fill": "#F2F6FE", "stroke": "#6289D8", "dash": False, "label": "#1F4FB4"},
        "powerplatform": {"fill": "#F9F3FA", "stroke": "#AB77BE", "dash": False, "label": "#742774"},
        "onprem": {"fill": "#F5F6F7", "stroke": "#7C8D9A", "dash": False, "label": INK},
        "external": {"fill": "#FFF8F1", "stroke": "#C9762B", "dash": True, "label": "#8A3B00"},
        "users": {"fill": "#FFFFFF", "stroke": "#6C8FA8", "dash": False, "label": INK},
        "plain": {"fill": "#FFFFFF", "stroke": "#6C8FA8", "dash": False, "label": INK},
        "band": {"fill": "#FFFFFF", "stroke": "#6C8FA8", "dash": True, "label": INK},
    },
    "panel": {"fill": "#F4F7FA", "title": 21, "note": 13, "step_title": 16, "step_text": 13.5,
              "line_h": 19, "step_gap": 16, "radius": 10, "pad": 24, "top": 42, "badge_dx": 37, "text_dx": 62,
              "legend_title": 15, "legend_text": 13, "legend_note": 12.5, "legend_row": 26, "legend_note_h": 19},
    "header": {"title": 34, "title_line_h": 42, "max_lines": 2, "desc": 16, "desc_line_h": 23, "top": 62,
               "desc_gap": 36, "rule": 2, "rule_gap": 22, "rule_color": "#3F4650", "desc_max_em": 0},
    "footer": {"size": 12, "line_h": 16, "center": 15},
}

R_INK, R_MUTED, R_GRAY = "#16191F", "#5F6B7A", "#7D8998"


def _gk(stroke, tile, dash=False, align="left", fill="none"):
    return {"fill": fill, "stroke": stroke, "dash": dash, "label": R_INK, "tile": tile, "label_align": align}


# Thin square frames with a corner icon tile and a faint tint, icons with labels below, thin black
# orthogonal lines, black numbered badges and a full-height gray workflow column. Sizes suit a canvas
# about 1920 px wide; on wider canvases raise theme.scale instead of resizing parts one by one.
REFERENCE = {
    "node_type": "icon",
    "colors": {"ink": R_INK, "muted": R_MUTED, "line": "#8D99A6", "accent": "#0078D4", "blue": "#0078D4",
               "gray": R_GRAY},
    "icon": {"size": 64, "label_w": 170, "title": 16, "detail": 13.5, "line_h": 20, "detail_line_h": 17,
             "item_scale": 1.12},
    "group": {"radius": 0, "sw": 1.5, "tile": 40, "icon": 28, "label": 16, "sublabel": 13.5, "dash": "6 4",
              "label_bold": True, "pad": [28, 64, 28, 24], "tint": True},
    "edge": {"width": 1.6, "label": 13, "gap": 5, "arrow": 10, "head": "open", "label_bold": False},
    "badge": {"r": 12, "size": 13, "color": R_INK, "on_line": False},
    "edge_kinds": {
        "data": {"color": R_INK, "dash": None}, "request": {"color": R_INK, "dash": None},
        "action": {"color": R_INK, "dash": "7 4"}, "feedback": {"color": R_INK, "dash": "10 4 2 4"},
        "egress": {"color": R_INK, "dash": "7 4"}, "control": {"color": R_GRAY, "dash": "2 3"},
    },
    # Top-level boundaries carry a faint tint of their frame color; nested network frames stay clear.
    "group_kinds": {
        "azure": _gk("#243A5E", "#E8EEF6", fill="#F7FAFD"), "region": _gk("#0E8A7D", "#E3F3F1", True),
        "vnet": _gk("#7D4CDB", "#EFE9FB"), "subnet": _gk("#5A8F29", "#EDF4E6"),
        "fabric": _gk("#117865", "#E3F1EE", fill="#F5FBF9"),
        "foundry": _gk("#6A4CC2", "#EEEAF9", fill="#F8F6FD"),
        "m365": _gk("#2F5BD3", "#E8EEFB", fill="#F5F8FE"),
        "powerplatform": _gk("#742774", "#F3E8F3", fill="#FBF6FB"),
        "onprem": _gk(R_MUTED, "#EEF0F2", fill="#F7F8F9"), "external": _gk(R_GRAY, "#F1F3F5", True),
        "users": _gk(R_GRAY, "#F1F3F5"), "plain": _gk(R_GRAY, "#F1F3F5", fill="#FFFFFF"),
        "workflow": _gk(R_GRAY, "#F1F3F5", align="center", fill="#FFFFFF"),
        "band": _gk(R_GRAY, "#F1F3F5", True),
    },
    "panel": {"fill": "#EFF1F3", "radius": 0, "step_text": 16.5, "line_h": 23, "step_gap": 14, "max_gap": 48,
              "top": 64, "pad": 28, "badge_dx": 40, "text_dx": 66, "grow_max": 1.12, "lead_max": 1.6},
    "header": {"title": 40, "title_line_h": 48, "desc": 17, "desc_line_h": 23, "desc_max_em": 80},
}
PRESETS = {"reference": REFERENCE, "card": {}}

# theme.scale multiplies every size in these sections after all merges (not per-node overrides).
SCALED = ("icon", "group", "edge", "badge", "panel", "header", "footer", "card", "glyph", "tile")
UNSCALED = {"max_lines", "desc_max_em", "item_scale", "grow_max", "lead_max"}


def _scale(d, k):
    for key, v in d.items():
        if key in UNSCALED or isinstance(v, bool):
            continue
        if isinstance(v, (int, float)):
            d[key] = round(v * k, 2)
        elif isinstance(v, list) and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v):
            d[key] = [round(x * k, 2) for x in v]


def merge(base, over):
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            merge(base[k], v)
        else:
            base[k] = v
    return base


def make_theme(spec_theme=None, style=None):
    style = style or "reference"
    if style not in PRESETS:
        raise ValueError(f"unknown style '{style}' (use {', '.join(PRESETS)})")
    th = merge(copy.deepcopy(DEFAULT_THEME), copy.deepcopy(PRESETS[style]))
    th = merge(th, copy.deepcopy(spec_theme or {}))
    th["style"] = style
    k = th.get("scale", 1)
    if isinstance(k, bool) or not isinstance(k, (int, float)) or not 0.5 <= k <= 3:
        raise ValueError("theme.scale must be a number from 0.5 to 3")
    if k != 1:
        for sec in SCALED:
            _scale(th[sec], k)
        th["min_font"] = round(th["min_font"] * k, 2)
    return th


def color(theme, value, default="ink"):
    value = value or default
    return theme["colors"].get(value, value)


# WCAG 2.1 contrast minimums: text 4.5:1 (1.4.3), large text 3:1, lines and frames 3:1 (1.4.11).
LINE_CONTRAST = 3.0


def text_contrast(size, bold):
    """Minimum contrast for text: 3:1 from 24px, or from 18.66px when bold; else 4.5:1."""
    return 3.0 if size >= 24 or (bold and size >= 18.66) else 4.5


def _rgb(c):
    if not isinstance(c, str) or not c.startswith("#") or len(c) not in (4, 7):
        return None
    h = c[1:] if len(c) == 7 else "".join(ch * 2 for ch in c[1:])
    try:
        return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    except ValueError:
        return None


def contrast(a, b):
    """WCAG 2.1 contrast ratio of two '#rgb' or '#rrggbb' colors; None when either is something else."""
    ca, cb = _rgb(a), _rgb(b)
    if ca is None or cb is None:
        return None

    def lum(c):
        r, g, b = (v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    hi, lo = sorted((lum(ca), lum(cb)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def readable(theme, fg, bg, need):
    """fg when it reaches `need` contrast on bg (or cannot be measured); else the theme's muted or ink
    color, whichever reaches it first. Keeps line labels in their line's color only when legible."""
    for c in (fg, color(theme, "muted"), color(theme, "ink")):
        r = contrast(c, bg)
        if r is None or r >= need:
            return c
    return color(theme, "ink")
