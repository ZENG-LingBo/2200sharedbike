// Minimal slideshow framework: slides with progressive fragments.
// Navigation: Right/Space/Down -> next; Left/Up -> prev; Home/End jump.
// Keys: O = overview grid; S = speaker notes window; F = fullscreen; ? = help.
// Slides are <section> elements. Fragments are any element with class="fragment".
// Fragments reveal in document order unless data-fragment-index overrides.

(function () {
  const root = document.querySelector('.deck');
  if (!root) return;
  const slidesContainer = root.querySelector('.slides');
  const slides = Array.from(slidesContainer.querySelectorAll(':scope > section'));

  let currentSlide = 0;
  let currentFragment = -1;
  let overviewMode = false;
  let notesWindow = null;

  // Build fragment index per slide.
  const fragmentsBySlide = slides.map((slide) => {
    const frags = Array.from(slide.querySelectorAll('.fragment'));
    frags.forEach((f, i) => {
      const explicit = f.dataset.fragmentIndex;
      f._idx = explicit !== undefined ? parseInt(explicit, 10) : i;
    });
    frags.sort((a, b) => a._idx - b._idx);
    return frags;
  });

  function applyState() {
    slides.forEach((slide, i) => {
      slide.classList.toggle('present', i === currentSlide);
      slide.classList.toggle('past', i < currentSlide);
      slide.classList.toggle('future', i > currentSlide);
    });
    const frags = fragmentsBySlide[currentSlide];
    frags.forEach((f, i) => {
      f.classList.toggle('visible', i <= currentFragment);
      f.classList.toggle('current-fragment', i === currentFragment);
    });
    updateProgress();
    updateNotes();
    writeHash();
  }

  function updateProgress() {
    const bar = document.querySelector('.deck-progress > .bar');
    if (bar) {
      const total = slides.length - 1;
      bar.style.width = (total ? (currentSlide / total) * 100 : 0) + '%';
    }
    const counter = document.querySelector('.deck-counter');
    if (counter) {
      counter.textContent = (currentSlide + 1) + ' / ' + slides.length;
    }
  }

  function next() {
    const frags = fragmentsBySlide[currentSlide];
    if (currentFragment + 1 < frags.length) {
      currentFragment++;
    } else if (currentSlide + 1 < slides.length) {
      currentSlide++;
      currentFragment = -1;
    } else {
      return;
    }
    applyState();
  }

  function prev() {
    if (currentFragment >= 0) {
      currentFragment--;
    } else if (currentSlide > 0) {
      currentSlide--;
      currentFragment = fragmentsBySlide[currentSlide].length - 1;
    } else {
      return;
    }
    applyState();
  }

  function jumpTo(slideIdx, fragIdx) {
    currentSlide = Math.max(0, Math.min(slides.length - 1, slideIdx));
    const frags = fragmentsBySlide[currentSlide];
    currentFragment = fragIdx === undefined
      ? frags.length - 1
      : Math.max(-1, Math.min(frags.length - 1, fragIdx));
    applyState();
  }

  function toggleOverview() {
    overviewMode = !overviewMode;
    root.classList.toggle('overview', overviewMode);
  }

  function openNotes() {
    if (notesWindow && !notesWindow.closed) { notesWindow.focus(); return; }
    notesWindow = window.open('', 'deck-notes', 'width=520,height=720');
    if (!notesWindow) return;
    notesWindow.document.write(`
      <!doctype html><html><head><meta charset="utf-8"><title>Speaker Notes</title>
      <style>
        body{font:14px/1.55 system-ui,-apple-system,sans-serif;margin:0;padding:20px;
             background:#1a1a1a;color:#eee}
        h1{font-size:14px;text-transform:uppercase;letter-spacing:.1em;color:#999;margin:0 0 4px}
        .ts{color:#C8553D;font-weight:600;font-size:13px;margin-bottom:12px}
        .pos{color:#999;font-size:12px;margin-bottom:18px}
        .notes{font-size:15px;white-space:pre-wrap}
        .timer{position:fixed;top:8px;right:12px;font-variant-numeric:tabular-nums;
               font-size:13px;color:#999}
      </style></head><body>
      <div class="timer" id="t">0:00</div>
      <h1>Slide</h1><div class="ts" id="ts"></div>
      <div class="pos" id="pos"></div>
      <div class="notes" id="n"></div>
      <script>
        const start=Date.now();
        setInterval(()=>{const s=Math.floor((Date.now()-start)/1000);
          document.getElementById('t').textContent=Math.floor(s/60)+':'+String(s%60).padStart(2,'0');},1000);
      <\/script>
      </body></html>`);
    notesWindow.document.close();
    updateNotes();
  }

  function updateNotes() {
    if (!notesWindow || notesWindow.closed) return;
    const slide = slides[currentSlide];
    const ts = slide.dataset.timestamp || '';
    const notes = slide.dataset.notes || (slide.querySelector('aside.notes') || {}).textContent || '';
    const doc = notesWindow.document;
    if (doc.getElementById('ts')) doc.getElementById('ts').textContent = ts;
    if (doc.getElementById('pos')) doc.getElementById('pos').textContent =
      'Slide ' + (currentSlide + 1) + ' of ' + slides.length +
      (fragmentsBySlide[currentSlide].length
        ? ' · fragment ' + (currentFragment + 1) + '/' + fragmentsBySlide[currentSlide].length
        : '');
    if (doc.getElementById('n')) doc.getElementById('n').textContent = notes.trim();
  }

  function toggleFullscreen() {
    if (!document.fullscreenElement) document.documentElement.requestFullscreen();
    else document.exitFullscreen();
  }

  document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    switch (e.key) {
      case 'ArrowRight': case ' ': case 'PageDown':
        e.preventDefault(); next(); break;
      case 'ArrowLeft': case 'PageUp':
        e.preventDefault(); prev(); break;
      case 'ArrowDown':
        e.preventDefault(); next(); break;
      case 'ArrowUp':
        e.preventDefault(); prev(); break;
      case 'Home':
        e.preventDefault(); jumpTo(0, -1); break;
      case 'End':
        e.preventDefault(); jumpTo(slides.length - 1); break;
      case 'o': case 'O':
        e.preventDefault(); toggleOverview(); break;
      case 's': case 'S':
        e.preventDefault(); openNotes(); break;
      case 'f': case 'F':
        e.preventDefault(); toggleFullscreen(); break;
      case '?':
        e.preventDefault(); document.querySelector('.deck-help').classList.toggle('show'); break;
      case 'Escape':
        if (overviewMode) { e.preventDefault(); toggleOverview(); }
        document.querySelector('.deck-help').classList.remove('show');
        break;
    }
  });

  slidesContainer.addEventListener('click', (e) => {
    if (overviewMode) {
      const sec = e.target.closest('section');
      if (sec) {
        const idx = slides.indexOf(sec);
        if (idx >= 0) { jumpTo(idx, -1); toggleOverview(); }
      }
      return;
    }
    if (e.target.closest('a, button, input, .no-advance')) return;
    const w = window.innerWidth;
    if (e.clientX > w / 2) next(); else prev();
  });

  // Hash routing: #/3 or #/3/2 (slide / fragment).
  function readHash() {
    const m = location.hash.match(/^#\/(\d+)(?:\/(-?\d+))?/);
    if (m) {
      currentSlide = Math.max(0, Math.min(slides.length - 1, parseInt(m[1], 10) - 1));
      const frags = fragmentsBySlide[currentSlide];
      currentFragment = m[2] !== undefined
        ? Math.max(-1, Math.min(frags.length - 1, parseInt(m[2], 10)))
        : -1;
    }
  }
  function writeHash() {
    const h = '#/' + (currentSlide + 1) + (currentFragment >= 0 ? '/' + currentFragment : '');
    if (location.hash !== h) history.replaceState(null, '', h);
  }

  readHash();
  applyState();
})();
