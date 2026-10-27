# セットアップ手順（はじめての方向け・約10分）

## 必要なもの
- パソコン（Mac推奨。Windowsは WSL で動きます）
- Claude の有料プラン（Pro 以上）または Anthropic API キー
- Python 3（`python3 --version` で確認）

## 1. Claude Code を入れる
```bash
curl -fsSL https://claude.ai/install.sh | bash
claude --version
```

## 2. ダウンロード
```bash
cd ~
git clone https://github.com/tajdijdiji/sedorin-cs-agent.git
cd sedorin-cs-agent
python3 -m unittest discover -s tests     # OK と出れば準備完了
```

## 3. 自分のお店の情報を入れる（ここが一番大事）
1. `config/products.csv` … 出品中の商品（SKU・出品価格・仕入れ値・販路・発送方法・状態メモ）
2. `config/policy.json` … 値下げのルール（最低限残したい利益・最大値下げ率）
3. `kb/shop_rules.md` / `kb/faq.md` … お店のルールとよくある質問の答え

```bash
python3 scripts/cs.py floors    # 商品ごとの値下げ下限が出ればOK
```

## ★最初に1回だけ：フォルダを信頼する
ダウンロードしたフォルダで一度 `claude` を起動し、「このフォルダを信頼しますか？」と聞かれたら **はい** を選んでください。
これをしないと、`.claude/settings.json` の許可設定が使われず、計算のたびに確認が出ます（自動実行も止まります）。
計算スクリプトの実行を聞かれたら「今後も許可」を選べばOKです。

## 4. 使う
```bash
claude
```
- `/reply A001 4300円でお願いできませんか？` … 1件だけ返信案
- `/offer A001 4300` … 値下げに応じてよいかだけ判定
- `/floors` … 全商品の値下げ下限
- `/inbox` … `workspace/inbox/` に貼ったメッセージをまとめて処理

### まとめて処理するとき
届いたメッセージを `workspace/inbox/messages.txt` に貼り、1件ごとに `---` の行で区切って `/inbox`。
`workspace/approval/` に「対応する順番つき」の返信案ができるので、確認してコピペで送るだけ。

## 1日の使い方（目安5分）
1. 昼と夜の2回、届いたメッセージを inbox に貼る
2. `/inbox`
3. ★要注意から順に、返信案をコピペして送信
4. 送ったファイルを `workspace/sent/` に移す
