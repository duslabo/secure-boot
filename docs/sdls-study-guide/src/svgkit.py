#!/usr/bin/env python3
"""Inline-SVG diagram helpers (4px grid, diagram-design skin)."""
import math, html as H


def c4(v):
    return int(math.ceil(v / 4.0) * 4)

def esc(s):
    return H.escape(s, quote=True)

# ---------------------------------------------------------------- svg helpers
def node(x, y, w, h, kind="box", name="", sub=None, kick=None, rx=6):
    """Paper mask + styled box + centred text block (kicker, name lines, sub lines)."""
    names = name if isinstance(name, list) else ([name] if name else [])
    subs = sub if isinstance(sub, list) else ([sub] if sub else [])
    items = []
    if kick:
        items.append(("kk", 12, kick))
    for n in names:
        items.append(("nm", 16, n))
    for s in subs:
        items.append(("sl", 12, s))
    gaps = []
    for a, b in zip(items, items[1:]):
        if a[0] == "kk":
            gaps.append(10)
        elif a[0] == "nm" and b[0] == "nm":
            gaps.append(5)
        elif a[0] == "nm" and b[0] == "sl":
            gaps.append(9)
        else:
            gaps.append(6)
    total = sum(i[1] for i in items) + sum(gaps)
    top = y + (h - total) / 2.0
    cx = x + w / 2.0
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="pm"/>',
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{kind}"/>']
    cur = top
    for k, (cls, size, txt) in enumerate(items):
        base = cur + size * 0.78
        out.append(f'<text x="{cx}" y="{base:.1f}" class="{cls}" text-anchor="middle">{esc(txt)}</text>')
        cur += size + (gaps[k] if k < len(gaps) else 0)
    return "\n".join(out)

def arrow(d, kind="", dashed=False, marker=True):
    cls = "ar" + (" acc" if kind == "acc" else "") + (" dsh" if dashed else "")
    mk = ""
    if marker:
        mk = ' marker-end="url(#mk-acc)"' if kind == "acc" else ' marker-end="url(#mk)"'
    return f'<path d="{d}" class="{cls}"{mk}/>'

def lbl_w(text):
    return c4(len(text) * 7.9 + 16)

def label(cx, line_y, text):
    """Masked label centred above a horizontal segment, 6px clear of the stroke."""
    w = lbl_w(text)
    x = cx - w / 2.0
    y = line_y - 6 - 16
    return (f'<rect x="{x}" y="{y}" width="{w}" height="16" rx="2" class="mk"/>'
            f'<text x="{cx}" y="{y + 12}" class="al" text-anchor="middle">{esc(text)}</text>')

def vlabel(line_x, cy, text, side="right"):
    w = lbl_w(text)
    x = line_x + 8 if side == "right" else line_x - 8 - w
    y = cy - 8
    return (f'<rect x="{x}" y="{y}" width="{w}" height="16" rx="2" class="mk"/>'
            f'<text x="{x + w / 2.0}" y="{y + 12}" class="al" text-anchor="middle">{esc(text)}</text>')

def zone(x, y, w, h, text, sec=False):
    cls = "zone sec-z" if sec else "zone"
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" class="{cls}"/>'
            f'<text x="{x + 16}" y="{y + 24}" class="eb">{esc(text)}</text>')

def text(x, y, s, cls="sl", anchor="start"):
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{esc(s)}</text>'

def callout(x, y, lines, anchor="start", step=20):
    return "\n".join(text(x, y + i * step, l, "co", anchor) for i, l in enumerate(lines))

def legend(y, w, items):
    out = [f'<line x1="0" y1="{y - 12}" x2="{w}" y2="{y - 12}" class="hair"/>',
           f'<text x="0" y="{y + 10}" class="eb">LEGEND</text>']
    x = 96
    for kind, name in items:
        if kind == "arrow-acc":
            out.append(f'<path d="M{x},{y + 6} H{x + 24}" class="ar acc" marker-end="url(#mk-acc)"/>')
        elif kind == "forbid":
            out.append(f'<path d="M{x},{y + 6} H{x + 24}" class="ar acc dsh"/>')
        else:
            out.append(f'<rect x="{x}" y="{y}" width="24" height="12" rx="2" class="pm"/>'
                       f'<rect x="{x}" y="{y}" width="24" height="12" rx="2" class="{kind}"/>')
        out.append(text(x + 36, y + 10, name, "lg"))
        x += 64 + int(len(name) * 7.4)
        x = c4(x)
    return "\n".join(out)

def svg(slug, w, h, title, desc, body, cls="fig-svg"):
    return (f'<svg class="{cls}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="{slug}-title {slug}-desc" '
            f'xmlns="http://www.w3.org/2000/svg">\n<title id="{slug}-title">{esc(title)}</title>\n'
            f'<desc id="{slug}-desc">{esc(desc)}</desc>\n{body}\n</svg>')

