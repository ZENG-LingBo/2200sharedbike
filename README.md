# Shared-Bike Systems · Slideshow

Animated HTML slideshow for the DESN2200 systems-mapping assignment video. Two diagrams: a technical architecture map (Diagram 1) and a social causal-loop diagram with embedded archetypes (Diagram 2), bound by a cross-system coupling slide.

## Open

```
open index.html        # macOS
xdg-open index.html    # Linux
start index.html       # Windows
```

No build step, no server, no network required. Drop the folder anywhere and open the file. Tested in Chrome, Safari, Firefox.

## Navigate

| Key | Action |
| --- | --- |
| `→` `Space` `↓` `PgDn` | Next fragment / slide |
| `←` `↑` `PgUp` | Previous fragment / slide |
| `Home` / `End` | Jump to first / last slide |
| `O` | Overview grid (click a thumbnail to jump) |
| `S` | Open speaker-notes window in a second tab (timer + script timestamp + notes) |
| `F` | Fullscreen |
| `?` | Toggle on-screen keyboard help |
| `Esc` | Close help / exit overview |

The URL hash (`#/3/2`) tracks slide and fragment, so you can deep-link or refresh without losing place.

## Record

For the 5-minute video:

1. Open `index.html` in a browser, press `F` for fullscreen.
2. In a second tab, press `S` to open the speaker-notes window (drag it to a second monitor or to your phone via screen-share — it shows the script timestamp range and notes for each slide, plus a running timer).
3. Use OBS, QuickTime (macOS), or Game Bar (Windows) to capture the slideshow window at **1920 × 1080 / 60 fps**.
4. Record the talking-head separately as a webcam track and composite afterward — keeping them as two streams gives full control of crop, position, and audio sync.
5. Advance with `→` at the timestamps marked in each slide's `data-timestamp`. Total expected runtime: **5:00**, with slide 14 (cross-system coupling) the easiest to compress if running long.

## Slide map

| # | Section | Timestamp | Slide |
| --: | --- | --- | --- |
|  1 | Intro | 0:00–0:15 | Title + hook stat |
|  2 | Intro | 0:15–0:25 | Two-lens framing |
|  3 | D1 Architecture | 0:25–0:50 | Three-layer skeleton |
|  4 | D1 Architecture | 0:50–1:25 | User-journey 1–7 |
|  5 | D1 Architecture | 1:25–1:50 | Guidance mechanism badges |
|  6 | D1 Architecture | 1:50–2:15 | Improvements |
|  7 | D2 CLD | 2:15–2:35 | Variables overview |
|  8 | D2 CLD | 2:35–2:50 | B1 Tragedy of the Commons |
|  9 | D2 CLD | 2:50–3:05 | R1 Damage Spiral |
| 10 | D2 CLD | 3:05–3:15 | R3 Trust Collapse |
| 11 | D2 CLD | 3:15–3:25 | B2 Regulatory Backlash |
| 12 | D2 CLD | 3:25–3:50 | Guidance loops B3 / B4 / R7 |
| 13 | D2 CLD | 3:50–4:15 | Improvements |
| 14 | Coupling | 4:15–4:50 | Three handoffs D1 ↔ D2 |
| 15 | Conclusion | 4:50–5:00 | Closing |

## Files

```
index.html                  # The deck
css/theme-academic.css      # Layout, typography, slide chrome
css/diagrams.css            # SVG styling + fragment animation
js/deck.js                  # Minimal slideshow framework (~180 lines)
README.md                   # This file
```

## Notes

- All diagrams are inline SVG so the deck is one self-contained artefact (the only external assets are the two CSS files and the JS file in the same folder).
- Loops are drawn with `stroke-dashoffset` animation when their fragment becomes visible, giving the pen-stroke effect on each `→` press.
- Colour semantics: oxide red `#C8553D` = reinforcing loops + forcing functions; slate `#3D5A6C` = balancing loops + feedback signals; gold `#A78A4D` = designed/guidance loops.
- Speaker notes use `data-timestamp` and `data-notes` on each `<section>` — edit those to refine your script without touching the visuals.
