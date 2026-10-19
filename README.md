# Vinimesh's Portfolio

Product management portfolio for Vinimesh Yadav.

Live site: https://binnonymous.github.io/vinimesh-portfolio/

## Layout

- `docs/` is the published site (GitHub Pages serves this folder from `main`).
  - `index.html` holds the whole page, including the project data (`PROJECTS`).
  - `slides/` has one JPEG per deck slide, named `<slug>-NN.jpg`.
  - `decks/` has the original PDFs, named `<slug>.pdf`.
- `tools/check_assets.py` checks that every image, slide and PDF is served with status 200 and the right type.
- `tests/` has unit tests for the checker.

## Check before and after each deploy

```sh
python3 -m unittest discover -s tests
python3 -m http.server 8081 --directory docs   # in another terminal
python3 tools/check_assets.py http://127.0.0.1:8081/
python3 tools/check_assets.py https://binnonymous.github.io/vinimesh-portfolio/
```

## Add a project

1. Add an entry to `PROJECTS` in `docs/index.html` with its `slug` and `slides` count.
2. Add `docs/decks/<slug>.pdf` and `docs/slides/<slug>-01.jpg` … one image per slide.
3. Run the asset check, then commit and push.
