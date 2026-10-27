---
description: inbox に貼ったメッセージをまとめて処理（仕分け→返信案→チェック）
---
1. `triage` で `workspace/inbox/` の最新メッセージファイルを仕分け
2. 担当ごとにサブエージェントへ振り分けて返信案を作る
3. `reviewer` で全件チェック
4. `workspace/approval/YYYY-MM-DD_replies.md` に、対応する順番で全件まとめる（★要注意を先頭に）
5. 最後に「今すぐ対応すべき件数」と、ファイルのパスを出力する
送信はしないこと。
