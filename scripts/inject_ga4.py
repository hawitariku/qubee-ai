"""
Inject Google Analytics GA4 tag into all HTML templates.
Run once:  python scripts/inject_ga4.py
To update the Measurement ID replace G-XXXXXXXXXX with your real ID.
"""
import os

GA4_ID = "G-XXXXXXXXXX"   # <-- replace with your real GA4 Measurement ID

GA4_SNIPPET = (
    "\n    <!-- Google Analytics GA4 -->\n"
    f"    <script async src=\"https://www.googletagmanager.com/gtag/js?id={GA4_ID}\"></script>\n"
    "    <script>\n"
    "      window.dataLayer = window.dataLayer || [];\n"
    "      function gtag(){dataLayer.push(arguments);}\n"
    "      gtag('js', new Date());\n"
    f"      gtag('config', '{GA4_ID}');\n"
    "    </script>\n"
)

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")

injected, skipped = [], []

for fname in sorted(os.listdir(TEMPLATES_DIR)):
    if not fname.endswith(".html"):
        continue
    path = os.path.join(TEMPLATES_DIR, fname)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if "googletagmanager" in content:
        skipped.append(f"{fname} (already has GA4)")
        continue
    if "</head>" not in content:
        skipped.append(f"{fname} (no </head> found)")
        continue

    # Inject just before </head>
    new_content = content.replace("</head>", GA4_SNIPPET + "</head>", 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    injected.append(fname)

print(f"\nGA4 ({GA4_ID}) injected into {len(injected)} templates:")
for f in injected:
    print(f"  + {f}")
if skipped:
    print(f"\nSkipped ({len(skipped)}):")
    for f in skipped:
        print(f"  - {f}")
print("\nDone. Remember to replace G-XXXXXXXXXX with your real Measurement ID.")
print("Get it from: https://analytics.google.com -> Admin -> Data Streams -> your stream")
