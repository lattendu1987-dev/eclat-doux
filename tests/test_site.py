import tempfile
import unittest
from pathlib import Path

from eclat import config
from eclat.affiliate import AffiliateScenario, run
from eclat.site import DISCLOSURE, amazon_url, build, e


class SiteTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()) / "public"
        self.out = build(self.tmp)
        self.guides = config.load_toml("site.toml")["guide"]

    def test_all_pages_exist(self):
        for g in self.guides:
            self.assertTrue((self.out / f"{g['slug']}.html").exists())
        for name in ["index.html", "divulgation.html", "confidentialite.html", "a-propos.html",
                     "404.html", "mentions-legales.html", "sitemap.xml", "robots.txt", "style.css", "app.js"]:
            self.assertTrue((self.out / name).exists(), name)

    def test_disclosure_on_every_page(self):
        for page in self.out.glob("*.html"):
            if page.name.startswith("google"):
                continue  # fichier de validation Google, pas une page du site
            self.assertIn(e(DISCLOSURE), page.read_text(encoding="utf-8"), page.name)

    def test_affiliate_links_are_marked_sponsored(self):
        html = (self.out / f"{self.guides[0]['slug']}.html").read_text(encoding="utf-8")
        self.assertIn("amazon.fr/s?k=", html)
        self.assertIn('rel="sponsored nofollow noopener"', html)

    def test_no_prices_shown(self):
        # Le contrat Amazon interdit d'afficher des prix hors API officielle.
        for page in self.out.glob("*.html"):
            text = page.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"\d+[,.]\d{2}\s?[$€]", page.name)


class AmazonUrlTest(unittest.TestCase):
    def test_tag_added(self):
        self.assertEqual(amazon_url("bottes chien", "abc-21"), "https://www.amazon.fr/s?k=bottes+chien&tag=abc-21")

    def test_no_tag(self):
        self.assertEqual(amazon_url("bottes chien", ""), "https://www.amazon.fr/s?k=bottes+chien")


class AffiliateTest(unittest.TestCase):
    def test_run(self):
        r = run(AffiliateScenario("t", 1000, 0.1, 0.1, 50, 0.04))
        self.assertEqual(r.orders, 10)
        self.assertEqual(r.commission, 20)


if __name__ == "__main__":
    unittest.main()


class FeedTest(unittest.TestCase):
    def test_feed_valid_and_skips_manual_pins(self):
        import xml.etree.ElementTree as ET
        out = build(Path(tempfile.mkdtemp()) / "public")
        root = ET.parse(out / "feed.xml").getroot()
        links = [i.findtext("link") for i in root.iter("item")]
        self.assertTrue(links)
        self.assertFalse(any("bottes-chien-hiver" in l for l in links))
        for item in root.iter("item"):
            self.assertIsNotNone(item.find("enclosure"))


class EnglishSiteTest(unittest.TestCase):
    def test_english_pages_and_disclosure(self):
        out = build(Path(tempfile.mkdtemp()) / "public")
        en = out / "en"
        self.assertTrue((en / "index.html").exists())
        guides = config.load_toml("site_en.toml")["guide"]
        for g in guides:
            html = (en / f"{g['slug']}.html").read_text(encoding="utf-8")
            self.assertIn("As an Amazon Associate I earn from qualifying purchases", html)
            self.assertIn("amazon.com/s?k=", html)
            self.assertNotRegex(html, r"\d+[,.]\d{2}\s?[$€£]")
        self.assertIn("/en/", (out / "sitemap.xml").read_text(encoding="utf-8"))


class BestSellersTest(unittest.TestCase):
    def test_pages_and_tags(self):
        out = build(Path(tempfile.mkdtemp()) / "public")
        fr = (out / "meilleures-ventes.html").read_text(encoding="utf-8")
        en = (out / "en" / "best-sellers.html").read_text(encoding="utf-8")
        self.assertIn("amazon.fr/gp/bestsellers/beauty/?tag=pattesauchaud-21", fr)
        self.assertIn("amazon.com/gp/bestsellers/beauty/?tag=warmpaws-20", en)
        self.assertIn('rel="sponsored nofollow noopener"', fr)
        self.assertLess(fr.index("amazon.fr/gp"), fr.index("amazon.com/gp"))
        self.assertLess(en.index("amazon.com/gp"), en.index("amazon.fr/gp"))


class StoresTest(unittest.TestCase):
    def test_stores_js_only_tagged(self):
        out = build(Path(tempfile.mkdtemp()) / "public")
        js = (out / "stores.js").read_text(encoding="utf-8")
        self.assertIn('"GB":{"d":"www.amazon.co.uk","t":"warmpawsuk-21"}', js)
        self.assertIn('"US"', js)
        self.assertIn("warmpawsuk06-21", js)


class PolishSiteTest(unittest.TestCase):
    def test_polish_pages(self):
        from eclat.site_pl import DISCLOSURE as PL, aliexpress_url
        out = build(Path(tempfile.mkdtemp()) / "public")
        pl = out / "pl"
        for g in config.load_toml("site_pl.toml")["guide"]:
            html = (pl / f"{g['slug']}.html").read_text(encoding="utf-8")
            self.assertIn(e(PL), html)
            self.assertIn("aliexpress", html)
            self.assertIn('rel="sponsored nofollow noopener"', html)
            self.assertNotRegex(html, r"\d+[,.]\d{2}\s?(zł|PLN|[$€])")
        self.assertIn("/pl/", (out / "sitemap.xml").read_text(encoding="utf-8"))

    def test_awin_link(self):
        from eclat.site_pl import aliexpress_url
        self.assertEqual(aliexpress_url("dog boots", "", "1"), "https://pl.aliexpress.com/w/wholesale-dog-boots.html")
        u = aliexpress_url("dog boots", "123", "3138840")
        self.assertTrue(u.startswith("https://www.awin1.com/cread.php?awinmid=123&awinaffid=3138840&ued=https%3A%2F%2Fpl.aliexpress.com"))


class CosmeticClaimsTest(unittest.TestCase):
    def test_no_medical_claims(self):
        # Cosmétiques : aucune allégation thérapeutique.
        import re
        for name in ["site.toml", "site_en.toml", "site_pl.toml", "promo.toml"]:
            text = "\n".join(l for l in (config.CONFIG_DIR / name).read_text(encoding="utf-8").lower().splitlines() if not l.startswith("#"))
            self.assertNotRegex(text, r"\b(guérit|guérir|traite|cures?|heals?|leczy|anti-âge garanti)\b", name)


class PinPlanTest(unittest.TestCase):
    def test_one_pin_per_day_and_no_repeat(self):
        from datetime import date
        from unittest import mock
        from eclat import pinplan
        guides = {"fr": [{"slug": f"g{i}", "date": f"2026-10-{10+i}"} for i in range(5)], "en": []}
        store = {"done": ["fr:g0:a"], "weeks": {}}
        with mock.patch.object(pinplan, "load", lambda: store), mock.patch.object(pinplan, "save", lambda p: None):
            key, items = pinplan.week_plan(guides, date(2026, 11, 2))
            self.assertEqual(key, "2026-11-07")
            self.assertEqual([d for *_, d in items], [f"2026-11-{d:02d}" for d in range(8, 15)])
            self.assertEqual(items[0][1]["slug"], "g4")  # le guide le plus récent d'abord
            _, nxt = pinplan.week_plan(guides, date(2026, 11, 8))
            first = {(g["slug"], v) for _, g, v, _ in items}
            self.assertFalse(first & {(g["slug"], v) for _, g, v, _ in nxt})
