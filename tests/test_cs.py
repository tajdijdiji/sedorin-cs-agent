import os, sys, subprocess, csv, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import cs
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestCS(unittest.TestCase):
    def setUp(self): self.p = cs.products()
    def test_floor_keeps_margin(self):
        for p in self.p.values():
            self.assertGreaterEqual(cs.profit_at(p, cs.floor_price(p)), cs.POLICY["min_margin_after_discount_yen"])
            self.assertGreaterEqual(cs.floor_price(p), int(int(p["price"]) * (1 - cs.POLICY["max_discount_rate"])))
    def test_lowball_refused_or_counter(self):
        v, price, _ = cs.judge_offer(self.p["A001"], 3000)
        self.assertIn(v, ("逆提案", "断る"))
        self.assertGreaterEqual(price, cs.floor_price(self.p["A001"]))
    def test_reasonable_offer(self):
        p = self.p["A001"]; fl = cs.floor_price(p)
        self.assertEqual(cs.judge_offer(p, fl)[0], "応じる")
    def test_classify(self):
        self.assertEqual(cs.classify("LINEで直接やり取りできますか"), "外部取引")
        self.assertEqual(cs.classify("壊れていました。返品したい"), "トラブル")
        self.assertEqual(cs.classify("4300円でお願いできませんか"), "値下げ")
    def test_triage(self):
        out = os.path.join(tempfile.mkdtemp(), "t.csv")
        subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "cs.py"), "triage",
                        os.path.join(ROOT, "workspace", "inbox", "sample_messages.txt"), "--out", out], check=True)
        rows = list(csv.DictReader(open(out, encoding="utf-8-sig")))
        self.assertEqual(len(rows), 6)
        self.assertEqual(sum(1 for r in rows if r["urgent"]), 2)

if __name__ == "__main__":
    unittest.main()
