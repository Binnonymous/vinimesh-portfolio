"""Check that every image, slide and PDF the portfolio uses is served correctly.

Usage: python3 tools/check_assets.py <base-url>
  e.g. python3 tools/check_assets.py http://127.0.0.1:8081/
       python3 tools/check_assets.py https://binnonymous.github.io/vinimesh-portfolio/

Exit code 0 when every asset returns HTTP 200 with the expected content type, 1 otherwise.
"""
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

TYPES = {".pdf": "application/pdf", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
         ".png": "image/png", ".html": "text/html", ".svg": "image/svg+xml"}

ATTR_RE = re.compile(r'\b(?:src|href)="([^"]+)"')
# Each project in the PROJECTS array: slug:'x',...,slides:N on its first line
PROJECT_RE = re.compile(r"slug:'([a-z0-9-]+)'[^\n]*?slides:(\d+)")
OG_IMAGE_RE = re.compile(r'<meta property="og:image" content="([^"]+)"')


def extract_assets(html):
    """Return the set of site-relative files the page loads or links to."""
    assets = set()
    for value in ATTR_RE.findall(html):
        if value.startswith(("http:", "https:", "mailto:", "tel:", "#", "data:")):
            continue
        # Skip JS string fragments such as href="decks/'+p.slug+'.pdf"
        if "'" in value or "+" in value:
            continue
        assets.add(value)
    for slug, count in PROJECT_RE.findall(html):
        assets.add("decks/%s.pdf" % slug)
        for n in range(1, int(count) + 1):
            assets.add("slides/%s-%02d.jpg" % (slug, n))
    return assets


def extract_og_image(html):
    match = OG_IMAGE_RE.search(html)
    return match.group(1) if match else None


def expected_type(path):
    for ext, ctype in TYPES.items():
        if path.lower().endswith(ext):
            return ctype
    return None


def fetch(url):
    """Return (status, content_type) for a GET request, reading only the headers."""
    req = urllib.request.Request(url, headers={"User-Agent": "portfolio-asset-check"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.headers.get_content_type()
    except urllib.error.HTTPError as err:
        return err.code, None
    except urllib.error.URLError as err:
        return "unreachable (%s)" % err.reason, None


def check(base):
    if not base.endswith("/"):
        base += "/"
    status, ctype = fetch(base)
    if status != 200:
        print("FAIL  page %s -> %s" % (base, status))
        return 1
    with urllib.request.urlopen(base, timeout=30) as resp:
        html = resp.read().decode("utf-8")

    urls = {path: urllib.parse.urljoin(base, path) for path in sorted(extract_assets(html))}
    og = extract_og_image(html)
    if og and og.startswith(base):  # only meaningful once deployed at its final URL
        urls["og:image"] = og

    failures = 0
    for name, url in urls.items():
        status, ctype = fetch(url)
        want = expected_type(url)
        ok = status == 200 and (want is None or ctype == want)
        if not ok:
            failures += 1
            print("FAIL  %-40s status=%s type=%s (want %s)" % (name, status, ctype, want))
    print("%d of %d assets OK" % (len(urls) - failures, len(urls)))
    return 1 if failures else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(check(sys.argv[1]))
