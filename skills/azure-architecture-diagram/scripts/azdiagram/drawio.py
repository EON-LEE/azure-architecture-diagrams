"""draw.io writer: one <diagram> per page. Logical node and group ids double as cell ids, so
containers keep their children and edges stay attached when the diagram is edited."""
import base64
from html import escape
from xml.etree import ElementTree as ET

from .scene import Badge, Edge, Image, Rect, Swatch, Text
from .svgout import num

ALIGN = {"start": "left", "middle": "center", "end": "right"}
ARROWS = {"end": "startArrow=none;endArrow=block;endFill=1;",
          "start": "startArrow=block;startFill=1;endArrow=none;",
          "both": "startArrow=block;startFill=1;endArrow=block;endFill=1;",
          "none": "startArrow=none;endArrow=none;"}


def _arrows(kind, head):
    s = ARROWS[kind]
    return s.replace("=block;", "=open;").replace("Fill=1;", "Fill=0;") if head == "open" else s


def _geom(cell, **kw):
    g = ET.SubElement(cell, "mxGeometry", **kw)
    g.set("as", "geometry")
    return g


def _page(mx, sc, lib):
    th, font = sc.theme, sc.theme["drawio_font"]
    d = ET.SubElement(mx, "diagram", id=sc.page_id, name=sc.name)
    model = ET.SubElement(d, "mxGraphModel", dx=num(sc.width), dy=num(sc.height), grid="0", gridSize="10",
                          guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1",
                          pageScale="1", pageWidth=num(sc.width), pageHeight=num(sc.height),
                          background="#FFFFFF", math="0", shadow="0")
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")
    origin, size = {"1": (0.0, 0.0)}, {}

    def vertex(cid, x, y, w, h, style, value="", parent="1"):
        px, py = origin[parent]
        c = ET.SubElement(root, "mxCell", id=cid, value=value, style=style, vertex="1", parent=parent)
        _geom(c, x=num(x - px), y=num(y - py), width=num(w), height=num(h))
        origin[cid], size[cid] = (x, y), (w, h)

    for it in sc.items:
        if isinstance(it, Rect):
            if it.role == "paper":
                continue
            s = (f"rounded={1 if it.radius else 0};absoluteArcSize=1;arcSize={num(it.radius * 2)};"
                 f"html=1;fillColor={it.fill};strokeColor={it.stroke};strokeWidth={num(it.sw)};")
            if it.dash:
                s += f"dashed=1;dashPattern={it.dash};fixDash=1;"
            if it.container:
                s += "container=1;collapsible=0;recursiveResize=0;"
            vertex(it.id, it.x, it.y, it.w, it.h, s, "", it.parent)
        elif isinstance(it, Text):
            w = it.width + 4  # slack so draw.io never wraps a fitted label
            x = it.x - w if it.anchor == "end" else it.x - w / 2 if it.anchor == "middle" else it.x
            value = it.text
            if it.runs:  # mixed weights need an HTML label
                value = "".join(f"<b>{escape(t)}</b>" if b else escape(t) for t, b in it.runs)
            s = (f"text;html={1 if it.runs else 0};whiteSpace=nowrap;strokeColor=none;fillColor=none;"
                 f"align={ALIGN[it.anchor]};"
                 f"verticalAlign=middle;spacing=0;fontFamily={font};fontSize={num(it.size)};"
                 f"fontColor={it.color};fontStyle={1 if it.bold else 0};connectable=0;")
            if it.halo:
                s += f"labelBackgroundColor={it.halo if isinstance(it.halo, str) else '#FFFFFF'};"
            vertex(it.id, x, it.y - it.size, w, it.size * 1.35, s, value, it.parent)
        elif isinstance(it, Image):
            data = base64.b64encode(lib.get(it.key)).decode("ascii")
            vertex(it.id, it.x, it.y, it.size, it.size,
                   f"shape=image;aspect=fixed;imageAspect=1;connectable=0;image=data:image/svg+xml,{data};",
                   "", it.parent)
        elif isinstance(it, Edge):
            (x0, y0), (x1, y1) = it.points[0], it.points[-1]
            (sx, sy), (sw, sh) = origin[it.src], size[it.src]
            (tx, ty), (tw, tht) = origin[it.dst], size[it.dst]
            s = (f"edgeStyle=none;rounded=0;html=1;strokeColor={it.color};strokeWidth={num(it.width)};"
                 + _arrows(it.arrow, th["edge"].get("head"))
                 + (f"dashed=1;dashPattern={it.dash};fixDash=1;" if it.dash else "")
                 + ("jumpStyle=gap;jumpSize=12;" if it.gaps else "")
                 + f"exitX={(x0 - sx) / sw:.4f};exitY={(y0 - sy) / sh:.4f};exitDx=0;exitDy=0;exitPerimeter=0;"
                 + f"entryX={(x1 - tx) / tw:.4f};entryY={(y1 - ty) / tht:.4f};entryDx=0;entryDy=0;"
                 + "entryPerimeter=0;")
            c = ET.SubElement(root, "mxCell", id=it.id, value="", style=s, edge="1", parent="1",
                              source=it.src, target=it.dst)
            g = _geom(c, relative="1")
            if len(it.points) > 2:
                arr = ET.SubElement(g, "Array")
                arr.set("as", "points")
                for x, y in it.points[1:-1]:
                    ET.SubElement(arr, "mxPoint", x=num(x), y=num(y))
        elif isinstance(it, Badge):
            s = (f"ellipse;html=1;fillColor={it.color};strokeColor={it.ring};strokeWidth=2;fontColor=#FFFFFF;"
                 f"fontStyle=1;fontSize={num(it.size)};fontFamily=Segoe UI;align=center;"
                 "verticalAlign=middle;connectable=0;")
            vertex(it.id, it.cx - it.r, it.cy - it.r, it.r * 2, it.r * 2, s, it.n, it.parent)
        elif isinstance(it, Swatch):
            px, py = origin[it.parent]
            s = (f"endArrow=none;html=1;strokeColor={it.color};strokeWidth={num(it.width)};"
                 + (f"dashed=1;dashPattern={it.dash};fixDash=1;" if it.dash else ""))
            c = ET.SubElement(root, "mxCell", id=it.id, value="", style=s, edge="1", parent=it.parent)
            g = _geom(c, relative="1")
            for k, x in (("sourcePoint", it.x1), ("targetPoint", it.x2)):
                p = ET.SubElement(g, "mxPoint", x=num(x - px), y=num(it.y - py))
                p.set("as", k)


def write(scenes, lib, path):
    mx = ET.Element("mxfile", host="azure-architecture-diagram", type="device")
    for sc in scenes:
        _page(mx, sc, lib)
    ET.ElementTree(mx).write(path, encoding="utf-8", xml_declaration=True)
