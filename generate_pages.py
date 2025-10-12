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
  <main class="page">
    <h1 class="title">{title}</h1>
    <figure class="player">
      <audio controls preload="metadata">
        <source src="assets/audio/{file}" type="audio/mpeg" />
        Your browser does not support the audio element.
      </audio>
    </figure>
  </main>
</body>
</html>"""

tracks = json.load(open("tracks.json"))

out_dir = Path("")
out_dir.mkdir(exist_ok=True)

for i, track in enumerate(tracks, 1):
    html = template.format(**track)
    print(track)
    (out_dir / f"{i:02d}_{track["file"][:-4]}.html").write_text(html, encoding="utf-8")
    print(f"✓ Generated track-{i:02d}.html")
