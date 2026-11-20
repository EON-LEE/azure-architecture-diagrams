"""Renderer-neutral scene: absolute-coordinate primitives shared by the SVG and draw.io writers."""
from dataclasses import dataclass, field


@dataclass
class Rect:
    id: str
    x: float
    y: float
    w: float
    h: float
    fill: str = "none"
    stroke: str = "none"
    sw: float = 1.5
    radius: float = 0
    dash: str | None = None
    parent: str = "1"
    container: bool = False
    role: str = "shape"
    owner: str | None = None


@dataclass
class Text:
    id: str
    x: float
    y: float  # baseline
    text: str
    size: float
    color: str
    bold: bool = False
    anchor: str = "start"
    width: float = 0
    parent: str = "1"
    role: str = "text"
    owner: str | None = None
    halo: bool | str = False  # True: white; a color string: that fill
    fits: bool = True
    limited: bool = True  # False when the width is the natural width (no box to fit)
    runs: list | None = None  # [(text, bold)] for mixed-weight lines; `text` holds the plain string


@dataclass
class Image:
    id: str
    x: float
    y: float
    size: float
    key: str
    parent: str = "1"
    owner: str | None = None


@dataclass
class Edge:
    id: str
    points: list
    color: str
    width: float
    dash: str | None
    src: str
    dst: str
    kind: str = ""
    arrow: str = "end"
    bridge: bool = False
    gaps: list = field(default_factory=list)
    label_id: str | None = None


@dataclass
class Badge:
    id: str
    cx: float
    cy: float
    n: str
    color: str
    r: float = 13
    size: float = 14
    role: str = "flow"  # "flow" badges mark edges; "panel" badges number the workflow steps
    parent: str = "1"
    ring: str = "#FFFFFF"  # outline color; matches the fill behind the badge


@dataclass
class Swatch:
    id: str
    x1: float
    x2: float
    y: float
    color: str
    width: float
    dash: str | None = None
    parent: str = "1"


class Scene:
    """One diagram page. `boxes` holds node/group geometry (x1, y1, x2, y2) by logical id."""

    def __init__(self, page_id, name, width, height, theme, title="", desc=""):
        self.page_id, self.name, self.width, self.height = page_id, name, width, height
        self.theme, self.title, self.desc = theme, title, desc
        self.crossings = []
        self.items, self._ids, self._seq = [], set(), 0
        self.boxes, self.kind, self.parent = {}, {}, {}
        self.core = {}  # icon nodes: icon/cluster box; `boxes` also covers the label below it
        self.no_edges = set()  # logical ids that edges must not cross (panels, bands)
        self.steps = []
        self.findings = []  # layout problems found while building (reported by validate)
        self.fills = {}  # logical id -> fill color of filled groups and panels (for halos and rings)

    def add(self, item):
        if item.id in self._ids:
            raise ValueError(f"duplicate element id '{item.id}'")
        self._ids.add(item.id)
        self.items.append(item)
        return item

    def uid(self, prefix):
        self._seq += 1
        return f"{prefix}-{self._seq}"

    def ancestors(self, lid):
        out = []
        while lid in self.parent and self.parent[lid]:
            lid = self.parent[lid]
            out.append(lid)
        return out

    def of(self, cls):
        return [i for i in self.items if isinstance(i, cls)]
