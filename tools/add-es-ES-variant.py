"""Optional business decision (M6): add a dedicated es-ES edition.

The site currently ships ONE Spanish edition, explicitly labelled
"Espanol (Latinoamerica)" in the language menu. That is a valid choice: it
avoids near-duplicate hreflang clusters and preserves the 88-page sitemap
scope. If the business later wants a Spain-specific URL set, run:

    python tools/add-es-ES-variant.py            # dry run, prints the plan
    python tools/add-es-ES-variant.py --apply   # actually writes

IMPORTANT: the generated pages inherit the Mexican/Latin-American Spanish
copy. Before advertising them as es-ES, have a native Peninsular Spanish
speaker revise the wording; otherwise Google may treat them as duplicates.
Applying this script changes the sitemap from 88 to 96 URLs and the hreflang
count from 12 to 13 per cluster, so the "88 formal pages / n*12 hreflang"
constants in full-site-audit.py and google-crawl-score.py must be updated in
the same release (the script prints those exact follow-up steps).
"""
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ["index.html", "product/10032.html", "product/smart-camera.html",
         "productlist/10029.html", "productlist/10030.html",
         "productlist/10034.html", "productlist/10036.html",
         "productlist/10039.html"]
APPLY = "--apply" in sys.argv


def variant(base, lang):
    p = Path(base)
    return str(p.with_name(p.stem + "." + lang + ".html")).replace("\\", "/")


def main():
    targets = [(variant(b, "es-MX"), variant(b, "es-ES")) for b in PAGES]
    plan = []
    for src, dst in targets:
        s, d = ROOT / src, ROOT / dst
        if not s.exists():
            plan.append(f"SKIP (missing source): {src}")
            continue
        t = s.read_bytes().decode("utf-8")
        t = t.replace('lang="es-MX"', 'lang="es-ES"')
        t = t.replace("https://www.maibida.com/" + src,
                      "https://www.maibida.com/" + dst)
        t = t.replace('hreflang="es-MX" aria-current',
                      'hreflang="es-MX"')  # current-page marker belongs to es-ES now
        t = t.replace('>Español (Latinoamérica)</a>',
                      '>Español (Latinoamérica)</a>\n'
                      '<a href="' + dst.split('/')[-1] + '" hreflang="es-ES" lang="es-ES">Español (España)</a>')
        plan.append(f"WRITE {dst} ({len(t.encode('utf-8'))} bytes)")
        if APPLY:
            d.write_bytes(t.encode("utf-8"))
    print("\n".join(plan))
    print(f"\nmode: {'APPLY' if APPLY else 'DRY RUN'} | pages: {len(targets)}")
    print("""
Follow-up steps required after --apply (do NOT skip, or the 100/100 score
and the 0-error site audit will regress):
  1. sitemap.xml: add 8 <url> blocks for the es-ES pages and one
     <xhtml:link rel="alternate" hreflang="es-ES" .../> to each of the
     8 existing clusters (88 -> 96 URLs, 12 -> 13 hreflang per cluster).
  2. full-site-audit.py: append "es-ES" to LOCALES and add the 8 es-ES
     pages to the formal page set.
  3. google-crawl-score.py: change n * 12 to n * 13 and update the
     "88 formal pages" wording in notes.
  4. Have a native Peninsular Spanish speaker revise the copy.
  5. Re-run full-site-audit.py, google-crawl-score.py and
     verify-message-feature.py; then rebuild the reports.
""")
    if APPLY:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        print("Applied at", stamp, "- no backup was needed: only new files were written.")


if __name__ == "__main__":
    main()
