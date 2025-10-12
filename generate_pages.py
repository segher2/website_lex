import json
from pathlib import Path

template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <link rel="preload" href="assets/audio/{file}" as="audio">
  <link rel="stylesheet" href="assets/styles.css" />
</head>
<body>
  <header class="topbar">
    <span class="site-title">As One – Lex ter Braak</span>
    <nav class="menu">
      <button class="menu-button" aria-label="Menu">☰</button>
      <ul class="menu-list">
        {options}
      </ul>
    </nav>
  </header>

  <main class="page">
    <h1 class="title">{title}</h1>
    <figure class="player">
      <audio controls preload="metadata">
        <source src="assets/audio/{file}" type="audio/mpeg" />
        Your browser does not support the audio element.
      </audio>
      <figcaption class="pages">{pages}</figcaption>
    </figure>
  </main>

  <script>
    const btn = document.querySelector('.menu-button');
    const menu = document.querySelector('.menu-list');
    btn.addEventListener('click', () => menu.classList.toggle('open'));
  </script>
</body>
</html>"""

# Load tracks
with open("tracks.json", "r", encoding="utf-8") as f:
    tracks = json.load(f)

out_dir = Path("")
out_dir.mkdir(exist_ok=True)

options_html = "\n".join(
    f'<li><a href="{i:02d}_{Path(t["file"]).stem}.html">{t["title"].split(" - ")[0].strip()}</a></li>'
    for i, t in enumerate(tracks, 1)
)

for i, track in enumerate(tracks, 1):
    html = template.format(
        title=track.get("title", ""),
        file=track.get("file", ""),
        pages=track.get("pages", ""),
        options=options_html,
    )

    stem = Path(track["file"]).stem
    (Path(f"{i:02d}_{stem}.html")).write_text(html, encoding="utf-8")
    print(f"✓ Generated {i:02d}_{stem}.html")

