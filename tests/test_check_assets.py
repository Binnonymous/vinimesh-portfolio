import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import check_assets  # noqa: E402

FIXTURE = """
<meta property="og:image" content="https://example.github.io/site/photo-round.jpg">
<img src="photo-round.jpg" alt="">
<a href="decks/resume.pdf" target="_blank">Resume</a>
<a href="https://www.linkedin.com/in/someone">LinkedIn</a>
<a href="mailto:someone@example.com">Email</a>
<a href="#work">Work</a>
<script>
var PROJECTS=[
{
  slug:'alpha',slides:2,
  title:'Alpha'
},
{
  slug:'beta-case',slides:3,
  title:'Beta'
}];
</script>
"""


class ExtractAssetsTest(unittest.TestCase):
    def setUp(self):
        self.assets = check_assets.extract_assets(FIXTURE)

    def test_finds_local_src_and_href_files(self):
        self.assertIn("photo-round.jpg", self.assets)
        self.assertIn("decks/resume.pdf", self.assets)

    def test_ignores_external_mailto_and_hash_links(self):
        for asset in self.assets:
            self.assertFalse(asset.startswith(("http", "mailto:", "#")), asset)

    def test_expands_every_slide_of_every_project(self):
        expected = {"slides/alpha-01.jpg", "slides/alpha-02.jpg",
                    "slides/beta-case-01.jpg", "slides/beta-case-02.jpg", "slides/beta-case-03.jpg"}
        self.assertTrue(expected.issubset(self.assets))
        self.assertNotIn("slides/alpha-03.jpg", self.assets)

    def test_adds_one_deck_pdf_per_project(self):
        self.assertIn("decks/alpha.pdf", self.assets)
        self.assertIn("decks/beta-case.pdf", self.assets)

    def test_reads_og_image_as_absolute_url(self):
        self.assertEqual(check_assets.extract_og_image(FIXTURE),
                         "https://example.github.io/site/photo-round.jpg")


class ExpectedTypeTest(unittest.TestCase):
    def test_maps_extensions_to_content_types(self):
        self.assertEqual(check_assets.expected_type("a/b.pdf"), "application/pdf")
        self.assertEqual(check_assets.expected_type("a/b.jpg"), "image/jpeg")
        self.assertEqual(check_assets.expected_type("index.html"), "text/html")


if __name__ == "__main__":
    unittest.main()
