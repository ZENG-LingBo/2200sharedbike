#!/usr/bin/env python3
"""
Build slide 4 (Diagram 1 · User Journey) by:
  1. Reading layout geometry from d1-journey.svg (rendered by D2 + ELK)
  2. Re-emitting a deck-styled SVG that uses the existing CSS classes
     (.layer-band, .component, .user-arrow, .user-step*) so it matches
     slides 3/5 visually
  3. Wrapping each step in <g class="fragment" data-fragment-index="N">
     so the deck's stroke-dashoffset reveal animation fires per →
  4. Adding the step-1 self-action callout on Mobile App
  5. Anchoring red numbered step badges to each arrow's start

Run after editing d1-journey.d2:
  d2 --layout=elk --pad=24 d1-journey.d2 d1-journey.svg
  python3 build-slide4.py        # writes slide4.svg
"""
import base64
import html
import re
from pathlib import Path

SRC = Path(__file__).parent / "d1-journey.svg"
OUT = Path(__file__).parent / "slide4.svg"

src = SRC.read_text()

# ---------------------------------------------------------------
# 1. Extract container + component rects from D2 output
# ---------------------------------------------------------------
boxes = {}
for m in re.finditer(
    r'<g class="([A-Za-z0-9+/=]+)">\s*<g class="shape"[^>]*>'
    r'<rect x="([\d.]+)" y="([\d.]+)" '
    r'width="([\d.]+)" height="([\d.]+)"',
    src,
):
    cls, x, y, w, h = m.groups()
    try:
        name = base64.b64decode(cls + "==").decode("utf-8", errors="replace")
    except Exception:
        name = cls
    # D2 wraps quoted names in &#34; — strip them
    name = name.replace("&#34;", "").strip()
    boxes[name] = (float(x), float(y), float(w), float(h))

# ---------------------------------------------------------------
# 2. Extract edges (path + endpoints + label position)
# ---------------------------------------------------------------
edges = []
for m in re.finditer(
    r'<path d="M ([\d.]+) ([\d.]+) L ([\d.]+) ([\d.]+)"'
    r'[^>]*stroke="#C8553D"',
    src,
):
    x1, y1, x2, y2 = (float(v) for v in m.groups())
    edges.append((x1, y1, x2, y2))

# Edge order in d1-journey.d2 — matches the order ELK emits them
# (ELK preserves declaration order for same-source edges).
# Map edges by (start_box, end_box) for explicit assignment.
EDGE_SPECS = [
    ("Mobile App",     "QR Code",         2, "scan QR code"),
    ("Backend Server", "Smart Lock",      3, "validate · send unlock"),
    ("GPS / IoT",      "Backend Server",  4, "stream GPS during ride"),
    ("Backend Server", "Geofencing",      5, "geofence-gated park & lock"),
    ("Backend Server", "Payment Gateway", 6, "fare → payment gateway"),
    ("Mobile App",     "Field Operators", 7, "report fault → field operators dispatched"),
]


def box_center(name):
    x, y, w, h = boxes[name]
    return x + w / 2, y + h / 2


def match_edge(src_name, dst_name):
    """Pick the extracted edge whose endpoints best match these two boxes."""
    sx, sy = box_center(src_name)
    dx, dy = box_center(dst_name)
    best, best_score = None, 1e18
    for x1, y1, x2, y2 in edges:
        # squared distance: (start near src) + (end near dst)
        score = (x1 - sx) ** 2 + (y1 - sy) ** 2 + (x2 - dx) ** 2 + (y2 - dy) ** 2
        if score < best_score:
            best_score = score
            best = (x1, y1, x2, y2)
    return best


# ---------------------------------------------------------------
# 3. Determine viewBox (use D2's outer bounding box, with margin)
# ---------------------------------------------------------------
vb_match = re.search(r'<svg [^>]*viewBox="([^"]+)"', src)
vb = [float(v) for v in vb_match.group(1).split()]
VB_X, VB_Y, VB_W, VB_H = vb  # 0 0 933 676

# ---------------------------------------------------------------
# 4. Emit deck-styled SVG
# ---------------------------------------------------------------
out = []
out.append(
    f'<svg class="diagram arch-svg" '
    f'viewBox="{VB_X:g} {VB_Y:g} {VB_W:g} {VB_H:g}" '
    f'preserveAspectRatio="xMidYMid meet">'
)
out.append(
    '  <defs>'
    '<marker id="arrow-red-2" viewBox="0 0 10 10" refX="9" refY="5"'
    ' markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
    '<path d="M0,0 L10,5 L0,10 z" fill="#C8553D"/>'
    '</marker>'
    '</defs>'
)

# --- Layer bands ---
LAYER_CLASS = {"PHYSICAL": "physical", "DIGITAL": "digital", "OPERATIONAL": "ops"}
for layer_label, layer_key in [
    ("PHYSICAL",    "arch.physical"),
    ("DIGITAL",     "arch.digital"),
    ("OPERATIONAL", "arch.operational"),
]:
    x, y, w, h = boxes[layer_key]
    cls = LAYER_CLASS[layer_label]
    out.append(
        f'  <rect class="layer-band {cls}" x="{x:g}" y="{y:g}" '
        f'width="{w:g}" height="{h:g}"/>'
    )
    out.append(
        f'  <text class="layer-label" x="{x + 12:g}" y="{y + 22:g}">{layer_label}</text>'
    )

# --- Components ---
COMPONENT_NAMES = [
    "Frame", "Smart Lock", "GPS / IoT", "QR Code", "Battery",
    "Mobile App", "Backend Server", "Payment Gateway", "Geofencing",
    "Rebal. Trucks", "Maintenance Depot", "Field Operators",
]
COMPONENT_KEYS = {
    "Frame":             "arch.physical.Frame",
    "Smart Lock":        "arch.physical.Smart Lock",
    "GPS / IoT":         "arch.physical.GPS / IoT",
    "QR Code":           "arch.physical.QR Code",
    "Battery":           "arch.physical.Battery",
    "Mobile App":        "arch.digital.Mobile App",
    "Backend Server":    "arch.digital.Backend Server",
    "Payment Gateway":   "arch.digital.Payment Gateway",
    "Geofencing":        "arch.digital.Geofencing",
    "Rebal. Trucks":     "arch.operational.Rebal. Trucks",
    "Maintenance Depot": "arch.operational.Maintenance Depot",
    "Field Operators":   "arch.operational.Field Operators",
}
out.append('  <g class="components">')
for name in COMPONENT_NAMES:
    x, y, w, h = boxes[COMPONENT_KEYS[name]]
    cx, cy = x + w / 2, y + h / 2 + 5
    out.append(
        f'    <g transform="translate({x:g},{y:g})">'
        f'<rect class="component" width="{w:g}" height="{h:g}"/>'
        f'<text class="component-label" x="{w/2:g}" y="{h/2 + 5:g}">{html.escape(name)}</text>'
        f'</g>'
    )
out.append('  </g>')

# Map the simple component name to its box for edge endpoint lookup
SIMPLE_TO_KEY = {n: COMPONENT_KEYS[n] for n in COMPONENT_NAMES}


def edge_for(src_name, dst_name):
    return match_edge(SIMPLE_TO_KEY[src_name], SIMPLE_TO_KEY[dst_name])


# --- Step 1: self-action callout on Mobile App. Sits high up in
# gap-A (above the digital row) on the left, separate from the
# step 2/3/4 label band that sits lower down in the same gap.
ma_x, ma_y, _, _ = boxes[SIMPLE_TO_KEY["Mobile App"]]
step1_cx = ma_x + 13
step1_cy = ma_y - 100
out.append('  <g class="fragment" data-fragment-index="0">')
out.append(
    f'    <circle cx="{step1_cx:g}" cy="{step1_cy:g}" r="11" class="user-step-bg"/>'
)
out.append(
    f'    <text class="user-step" x="{step1_cx:g}" y="{step1_cy + 4:g}" '
    f'text-anchor="middle">1</text>'
)
out.append(
    f'    <text class="user-step-label" x="{step1_cx + 18:g}" y="{step1_cy + 4:g}">'
    f'open app · map shows nearby bikes</text>'
)
out.append('  </g>')

# --- Steps 2–7: edges from D2's layout ---
# Per-step overrides: some edges need manual routing because D2's
# straight-line edge would cross through another box, or because two
# edges share a start point and their badges would overlap.
#
#   path:        SVG <path d="..."> override (skips D2's geometry).
#   badge_xy:    explicit (x, y) for the step number circle.
#   label_xy:    explicit (x, y) for the step text.
#   src_anchor:  ("right" | "bottom" | ...) — pick a different edge of
#                the source box for D2's straight line to start from.
#   dst_anchor:  same, for the destination box.
#   length:      override the --len for the stroke-dashoffset reveal.
# Per-step overrides — explicit (badge, label) placement for every step
# so labels land in distinct empty zones (inter-layer gaps, edges of the
# physical band) instead of stacking on top of each other inside the
# narrow digital row.
#
# Layer band y-bounds:
#   physical:    y=58…224       gap-A (above digital):   y=224…252
#   digital:     y=252…418      gap-B (below digital):   y=418…446
#   operational: y=446…612
#
#   path:       optional SVG path override (skips D2's geometry).
#   length:     stroke-dashoffset --len for the override path.
#   badge_xy:   (x, y) for the step number circle.
#   label_xy:   (x, y) for the step text (text-anchor:start).
STEP_OVERRIDES = {
    # Step 2: arrow Mobile App → QR Code. Label in gap-A lower band.
    2: {"badge_xy": (272, 388), "label_xy": (470, 320)},
    # Step 3: arrow Backend → Smart Lock. Label in gap-A lower, left.
    3: {"badge_xy": (382, 388), "label_xy": (200, 320)},
    # Step 4: arrow GPS/IoT → Backend. Label in gap-A lower, right.
    4: {"badge_xy": (495, 222), "label_xy": (700, 320)},
    # Step 5: U-route through gap-B (below digital row) so Backend's
    # connection to Geofencing skips over Payment Gateway. Label sits
    # under the horizontal segment, right side of gap-B.
    5: {
        "path": "M 393 454 V 540 H 808 V 454",
        "length": 587,
        "badge_xy": (400, 470),
        "label_xy": (700, 558),
    },
    # Step 6: short Backend → Payment Gateway. Label above the arrow,
    # in the unused band between digital top and component tops.
    6: {"badge_xy": (495, 421), "label_xy": (495, 365)},
    # Step 7: long diagonal Mobile App → Field Operators. Label in
    # gap-B left side, separated from step 5's label on the right.
    7: {"badge_xy": (272, 460), "label_xy": (260, 558)},
}

# Step-6 label is centered (text-anchor:middle); the rest are left-anchored.
STEP_LABEL_ANCHOR = {6: "middle"}


def emit_step(idx, src_name, dst_name, n, label):
    """Emit a step. Labels sit immediately next to the step badge
    (text-anchor:start) — readers parse "n · label" as a unit at the
    arrow's origin point, avoiding mid-arrow label collisions."""
    over = STEP_OVERRIDES.get(n, {})

    if "path" in over:
        d_attr = over["path"]
        length = over["length"]
    else:
        x1, y1, x2, y2 = edge_for(src_name, dst_name)
        d_attr = f"M {x1:.1f} {y1:.1f} L {x2:.1f} {y2:.1f}"
        length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        dx, dy = x2 - x1, y2 - y1
        norm = max((dx ** 2 + dy ** 2) ** 0.5, 1)
        # Default badge: nudge from arrow start toward destination.
        default_bx = x1 + (dx / norm) * 14
        default_by = y1 + (dy / norm) * 14

    if "badge_xy" in over:
        bx, by = over["badge_xy"]
    else:
        bx, by = default_bx, default_by

    if "label_xy" in over:
        label_x, label_y = over["label_xy"]
    else:
        # Right of badge (15px padding past r=11 circle).
        label_x = bx + 15
        label_y = by + 4

    out.append(f'  <g class="fragment" data-fragment-index="{idx}">')
    out.append(
        f'    <path class="user-arrow" style="--len:{length:.0f}" '
        f'marker-end="url(#arrow-red-2)" d="{d_attr}"/>'
    )
    out.append(
        f'    <circle cx="{bx:.1f}" cy="{by:.1f}" r="11" class="user-step-bg"/>'
    )
    out.append(
        f'    <text class="user-step" x="{bx:.1f}" y="{by + 4:.1f}" '
        f'text-anchor="middle">{n}</text>'
    )
    anchor = STEP_LABEL_ANCHOR.get(n, "start")
    anchor_attr = f' text-anchor="{anchor}"' if anchor != "start" else ""
    out.append(
        f'    <text class="user-step-label" x="{label_x:.1f}" y="{label_y:.1f}"'
        f'{anchor_attr}>{html.escape(label)}</text>'
    )
    out.append('  </g>')


for i, (src_name, dst_name, n, label) in enumerate(EDGE_SPECS, start=1):
    emit_step(i, src_name, dst_name, n, label)

out.append('</svg>')

OUT.write_text("\n".join(out) + "\n")
print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")
print(f"  viewBox: {VB_X:g} {VB_Y:g} {VB_W:g} {VB_H:g}")
print(f"  {len(boxes)} boxes, {len(edges)} edges")
