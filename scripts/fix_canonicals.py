"""Fix relative canonical and og:url tags in all templates."""
import os
import re
import glob

BASE = "https://qubeessaa-ai.up.railway.app"

patterns = [
    "templates/blog_*.html",
    "templates/blog.html",
    "templates/about.html",
    "templates/help.html",
    "templates/privacy.html",
]

files = []
for p in patterns:
    files.extend(glob.glob(p))

changed = 0
for path in sorted(files):
    with open(path, encoding="utf-8") as f:
        content = f.read()
    new = re.sub(
        r'(rel="canonical" href=")(/[^"]+)(")',
        lambda m: m.group(1) + BASE + m.group(2) + m.group(3),
        content,
    )
    new = re.sub(
        r'(property="og:url" content=")(/[^"]+)(")',
        lambda m: m.group(1) + BASE + m.group(2) + m.group(3),
        new,
    )
    if new != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
        print("Fixed:", path)
        changed += 1
    else:
        print("Skip:", path)

print(f"\nTotal fixed: {changed}/{len(files)} templates")
