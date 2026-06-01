#!/usr/bin/env python3
"""Build a self-contained prototype/index.html from prototype/reference.svg.

The SVG is inlined (not <img>-referenced) so the page works straight from
file:// and so pause/replay can drive SMIL via the live <svg> element.
Re-run this whenever reference.svg changes:  python3 prototype/build.py
"""
from pathlib import Path

HERE = Path(__file__).parent
svg = (HERE / "reference.svg").read_text(encoding="utf-8").strip()
placeholder = "PLACEHOLDER" in svg or "no coin" in svg or len(svg) < 4000

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Animated SVG header — prototype</title>
<style>
  :root { --w: 240px; }
  * { box-sizing: border-box; }
  body {
    margin: 0; font: 15px/1.5 -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1f2328; background: #ffffff; transition: background .2s, color .2s;
  }
  body.gh-light { background: #f6f8fa; color: #1f2328; }
  body.gh-dark  { background: #0d1117; color: #e6edf3; }
  body.white    { background: #ffffff; color: #1f2328; }
  header.bar {
    position: sticky; top: 0; display: flex; flex-wrap: wrap; gap: 8px; align-items: center;
    padding: 10px 16px; border-bottom: 1px solid rgba(127,127,127,.25);
    background: inherit; backdrop-filter: blur(6px);
  }
  .bar strong { margin-right: 8px; }
  button {
    font: inherit; padding: 5px 10px; border-radius: 8px; cursor: pointer;
    border: 1px solid rgba(127,127,127,.4); background: transparent; color: inherit;
  }
  button.active { background: #2f81f7; border-color: #2f81f7; color: #fff; }
  .group { display: inline-flex; gap: 4px; align-items: center; }
  .group + .group { margin-left: 14px; padding-left: 14px; border-left: 1px solid rgba(127,127,127,.25); }
  main { display: grid; place-items: center; padding: 56px 16px; }
  .composition { display: flex; align-items: center; gap: 28px; flex-wrap: wrap; justify-content: center; }
  #stage { width: var(--w); }
  #stage svg { width: 100%; height: auto; display: block; }
  .tagline { max-width: 360px; }
  .tagline h1 { margin: 0 0 6px; font-size: 30px; }
  .tagline p  { margin: 0; opacity: .8; font-style: italic; }
  .tagline.hidden { display: none; }
  .note {
    margin: 0 16px 24px; padding: 10px 14px; border-radius: 8px;
    background: #fff8c5; color: #5b4d00; border: 1px solid #e6d27a; max-width: 760px;
  }
  body.gh-dark .note { background: #2d2a1a; color: #f0e6a6; border-color: #5a5020; }
  .meta { margin-top: 40px; opacity: .6; font-size: 13px; text-align: center; }
</style>
</head>
<body class="white">
<header class="bar">
  <div class="group">
    <strong>Background</strong>
    <button data-bg="white" class="active">White</button>
    <button data-bg="gh-light">GitHub light</button>
    <button data-bg="gh-dark">GitHub dark</button>
  </div>
  <div class="group">
    <strong>Size</strong>
    <button data-size="180">180</button>
    <button data-size="240" class="active">240</button>
    <button data-size="320">320</button>
  </div>
  <div class="group">
    <strong>Animation</strong>
    <button id="replay">Replay</button>
    <button id="pause">Pause</button>
  </div>
  <div class="group">
    <strong>Layout</strong>
    <button id="toggle-tagline" class="active">Name + tagline</button>
  </div>
</header>

__NOTE__

<main>
  <div class="composition">
    <div id="stage">__SVG__</div>
    <div class="tagline" id="tagline">
      <h1>Hi, I'm Tanel</h1>
      <p>Software engineer, with data driven results.</p>
    </div>
  </div>
  <div class="meta">Reference loops ~4.03s · viewBox 1272×1283 · rounded squircle (r=244)</div>
</main>

<script>
  const body = document.body;
  const stage = document.getElementById('stage');
  function svgEl() { return stage.querySelector('svg'); }

  document.querySelectorAll('[data-bg]').forEach(b => b.onclick = () => {
    body.className = b.dataset.bg;
    setActive('[data-bg]', b);
  });
  document.querySelectorAll('[data-size]').forEach(b => b.onclick = () => {
    document.documentElement.style.setProperty('--w', b.dataset.size + 'px');
    setActive('[data-size]', b);
  });
  function setActive(sel, el) {
    document.querySelectorAll(sel).forEach(x => x.classList.remove('active'));
    el.classList.add('active');
  }

  let paused = false;
  document.getElementById('pause').onclick = (e) => {
    const s = svgEl(); if (!s) return;
    paused = !paused;
    if (paused) { s.pauseAnimations(); e.target.textContent = 'Resume'; e.target.classList.add('active'); }
    else { s.unpauseAnimations(); e.target.textContent = 'Pause'; e.target.classList.remove('active'); }
  };
  document.getElementById('replay').onclick = () => {
    const s = svgEl(); if (!s) return;
    s.setCurrentTime(0); s.unpauseAnimations();
    paused = false;
    const p = document.getElementById('pause'); p.textContent = 'Pause'; p.classList.remove('active');
  };
  document.getElementById('toggle-tagline').onclick = (e) => {
    document.getElementById('tagline').classList.toggle('hidden');
    e.target.classList.toggle('active');
  };
</script>
</body>
</html>
"""

note_html = ""
if placeholder:
    note_html = (
        '<div class="note"><strong>Placeholder asset.</strong> '
        "prototype/reference.svg currently holds a stub (just the rounded card). "
        "Replace it with your real coin SVG and re-run "
        "<code>python3 prototype/build.py</code> to preview the true animation.</div>"
    )

out = TEMPLATE.replace("__SVG__", svg).replace("__NOTE__", note_html)
(HERE / "index.html").write_text(out, encoding="utf-8")
print(f"Wrote index.html ({len(out)} bytes). placeholder={placeholder}")
