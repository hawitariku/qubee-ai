"""Add <link rel="icon"> to all HTML templates that don't already have one."""
import os
import glob

FAVICON_TAG = '    <link rel="icon" href="/favicon.ico" type="image/svg+xml">\n'

templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
files = glob.glob(os.path.join(templates_dir, "*.html"))

injected, skipped = [], []

for path in sorted(files):
    with open(path, encoding="utf-8") as f:
        content = f.read()
    if 'rel="icon"' in content:
        skipped.append(os.path.basename(path))
        continue
    if "</head>" not in content:
        skipped.append(os.path.basename(path) + " (no </head>)")
        continue
    new_content = content.replace("</head>", FAVICON_TAG + "</head>", 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    injected.append(os.path.basename(path))

print(f"Favicon link added to {len(injected)} templates:")
for f in injected:
    print(f"  + {f}")
if skipped:
    print(f"Skipped {len(skipped)}: {skipped}")
