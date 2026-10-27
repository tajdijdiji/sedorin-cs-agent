#!/usr/bin/env python3
"""せどりん式 接客AIエージェント - 値下げ判断・メッセージ仕分けエンジン（外部ライブラリ不要）

使い方:
  # 値下げ交渉：その金額に応じてよいか判定
  python3 scripts/cs.py offer A001 4500

  # 商品ごとの値下げ下限を一覧
  python3 scripts/cs.py floors

  # 貼り付けたメッセージをまとめて仕分け（workspace/inbox/messages.txt → approval）
  python3 scripts/cs.py triage workspace/inbox/messages.txt
"""
import argparse, csv, json, os, re, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def jload(n): return json.load(open(os.path.join(ROOT, "config", n), encoding="utf-8"))
FEES, SHIP, POLICY = jload("fees.json"), jload("shipping.json"), jload("policy.json")

def products():
    return {r["sku"]: r for r in csv.DictReader(open(os.path.join(ROOT, "config", "products.csv"), encoding="utf-8-sig"))}

def profit_at(p, price):
    f, s = FEES[p["market"]], SHIP[p["ship"]]
    return price - round(price * f["rate"]) - f["fixed"] - s["fee"] - s["box"] - 50 - int(p["buy"])

def floor_price(p):
    """利益が最低マージンを下回らない、かつ最大値下げ率以内の最安価格（10円単位）。"""
    price = int(p["price"])
    lo_rate = int(price * (1 - POLICY["max_discount_rate"]))
    x = price
    while x - 10 >= lo_rate and profit_at(p, x - 10) >= POLICY["min_margin_after_discount_yen"]:
        x -= 10
    return x

def judge_offer(p, offer):
    price, fl = int(p["price"]), floor_price(p)
    if offer >= price:
        return "OK", price, "出品価格以上なのでそのまま購入してもらう"
    if offer >= fl:
        return "応じる", offer, f"下限{fl:,}円以上・利益{profit_at(p, offer):,}円残る"
    # 段階的な逆提案
    for step in POLICY["discount_steps_yen"][::-1]:
        c = price - step
        if c >= fl:
            return "逆提案", c, f"希望{offer:,}円は下限{fl:,}円未満。{c:,}円なら可"
    return "断る", price, f"下限{fl:,}円＝これ以上は下げられない"

CATS = [
    ("トラブル", "|".join(POLICY["escalate_keywords"])),
    ("外部取引", r"LINE|ライン|メアド|メール|直接|振込|外で"),
    ("値下げ", r"値下げ|お値引|値引|安く|[0-9０-９,]+\s*円で|即決|まとめ"),
    ("発送", r"発送|いつ届|届きません|到着|追跡|配送|日時指定"),
    ("状態", r"状態|傷|汚れ|擦れ|動作|使用感|付属|箱"),
    ("サイズ", r"サイズ|寸法|cm|大きさ|重さ"),
    ("真贋", r"正規|本物|純正"),
    ("取り置き", r"専用|取り置|取置"),
    ("評価", r"評価|受取"),
]

def classify(text):
    for name, pat in CATS:
        if re.search(pat, text):
            return name
    return "その他"

def cmd_offer(a):
    p = products()[a.sku]
    v, price, why = judge_offer(p, a.amount)
    print(f"{p['name']}（出品{int(p['price']):,}円）への希望 {a.amount:,}円")
    print(f"判定: {v} / 提示価格: {price:,}円 / 理由: {why}")

def cmd_floors(a):
    for sku, p in products().items():
        fl = floor_price(p)
        print(f"{sku} {p['name']}: 出品{int(p['price']):,}円 → 値下げ下限 {fl:,}円（その時の利益 {profit_at(p, fl):,}円）")

def cmd_triage(a):
    raw = open(a.file, encoding="utf-8").read().strip()
    msgs = [m.strip() for m in re.split(r"\n\s*---+\s*\n|\n{2,}", raw) if m.strip()]
    prods = products()
    out = []
    for i, m in enumerate(msgs, 1):
        cat = classify(m)
        sku = next((s for s in prods if s in m), "")
        amt = re.search(r"([0-9,]{3,})\s*円", m)
        hint = ""
        if cat == "値下げ" and sku and amt:
            v, price, why = judge_offer(prods[sku], int(amt.group(1).replace(",", "")))
            hint = f"{v}（{price:,}円）{why}"
        urgent = cat in ("トラブル", "外部取引")
        out.append({"no": i, "category": cat, "urgent": "★要注意" if urgent else "", "sku": sku,
                    "offer_hint": hint, "message": m.replace("\n", " ")})
    day = datetime.date.today().isoformat()
    dst = a.out or os.path.join(ROOT, "workspace", "approval", f"{day}_triage.csv")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    print(f"{len(out)}件を仕分け（要注意 {sum(1 for o in out if o['urgent'])}件）→ {dst}")

def main():
    ap = argparse.ArgumentParser(description="せどりん式 接客エンジン")
    sp = ap.add_subparsers(dest="cmd", required=True)
    o = sp.add_parser("offer"); o.add_argument("sku"); o.add_argument("amount", type=int)
    sp.add_parser("floors")
    t = sp.add_parser("triage"); t.add_argument("file"); t.add_argument("--out", default=None)
    a = ap.parse_args()
    {"offer": cmd_offer, "floors": cmd_floors, "triage": cmd_triage}[a.cmd](a)

if __name__ == "__main__":
    main()
