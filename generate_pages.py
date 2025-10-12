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
</body>
</html>"""

# Load tracks
with open("tracks.json", "r", encoding="utf-8") as f:
    tracks = json.load(f)

out_dir = Path("")
out_dir.mkdir(exist_ok=True)

for i, track in enumerate(tracks, 1):
    html = template.format(
        title=track.get("title", ""),
        file=track.get("file", ""),
        pages=track.get("pages", ""),  # <- this is the new string caption
    )

    stem = Path(track["file"]).stem
    (out_dir / f"{i:02d}_{stem}.html").write_text(html, encoding="utf-8")
    print(f"✓ Generated {i:02d}_{stem}.html")
