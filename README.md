# 大学進学ガイド（理系）

愛知県立衣台高等学校 向け進路・受験対策ガイドサイト。  
HTML + CSS のみで構成された静的サイトです。

---

## 🚀 GitHub Pages で公開する手順

### 1. リポジトリを作成する

```
https://github.com/new
```

- Repository name: `shinro-guide`（または任意）  
- Public を選択  
- 「Create repository」をクリック

### 2. ファイルをアップロードする

```bash
# ローカルで git を使う場合
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/あなたのユーザー名/shinro-guide.git
git push -u origin main
```

または GitHub の「Add file → Upload files」から `workspace/shinro/` フォルダ内を全選択してドラッグ&ドロップ。

### 3. GitHub Pages を有効にする

1. リポジトリの **Settings** タブを開く  
2. 左メニューの **Pages** をクリック  
3. Source: **Deploy from a branch** → branch: `main` / folder: `/(root)` を選択  
4. 「Save」をクリック  
5. 数十秒後に `https://あなたのユーザー名.github.io/shinro-guide/` で公開される

---

## 💬 意見・フィードバックを収集する（Google フォーム）

### フォームを作成する

1. [Google フォーム](https://forms.google.com/) を開く（Googleアカウントで）
2. 「新しいフォームを作成」→ 以下の質問を追加する：

| 質問 | 形式 | 選択肢 |
|------|------|--------|
| どのページについての意見ですか？ | プルダウン | トップページ / 受験対策 / 学部選び / 大学情報 / 大学生活 / その他 |
| 種類 | ラジオボタン | 内容の誤り・記述追加希望・わかりにくかった・その他 |
| 詳しく教えてください | 段落（自由記述） | - |
| お名前（任意） | 短文 | - |

3. 右上の「送信」→「リンクをコピー」で URL を取得  
4. 「事前入力済みリンクを取得」ではなく通常のリンクを使う

### フォームURLをサイトに反映する

取得した URL（例：`https://docs.google.com/forms/d/e/1FAIpQLSxxxxx/viewform`）で以下を検索・置換：

```
検索: https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform
置換: あなたのフォームURL
```

**PowerShell で一括置換する場合：**
```powershell
$OLD = "https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform"
$NEW = "https://docs.google.com/forms/d/e/実際のフォームID/viewform"

Get-ChildItem -Recurse *.html | ForEach-Object {
    (Get-Content $_.FullName -Raw -Encoding UTF8) -replace [regex]::Escape($OLD), $NEW |
    Set-Content $_.FullName -Encoding UTF8
}
```

### 回答を確認する

Google フォームの「回答」タブ、または「スプレッドシートにリンク」ボタンで Google スプレッドシートに自動集計。

---

## 📁 ファイル構成

```
shinro/
├── shinro-guide.html      # メインページ（5タブ）
├── shared.css             # 全ページ共通スタイル
├── universities/          # 大学別詳細（37ページ）
├── majors/                # 学部別ガイド（11ページ）
└── prep/                  # 受験対策（9ページ）
    ├── nyushi-qa.html     # 共通テスト仕組み・Q&A
    ├── schedule.html      # 高3向けスケジュール
    ├── mathematics.html
    ├── physics.html
    ├── chemistry.html
    ├── english.html
    ├── kokugo.html
    ├── niji-shiken.html
    └── index.html
```

---

## 🔄 継続的な改善のフロー

1. **意見が届く** → Google フォームのスプレッドシートを確認  
2. **修正が必要** → 対象の HTML ファイルを編集  
3. **反映する** → `git add . && git commit -m "fix: xxx" && git push`  
4. **GitHub Pages に自動反映** → 数十秒後に公開URLが更新される  

GitHub Issues を使う場合は「Issues タブ → New Issue」でバグ・改善案を管理できます。

---

## ⚠️ 注意事項

- 大学・試験情報は年度により変わります。必ず最新の募集要項で確認してください。
- 年収・進路データは統計に基づく参考値です。
- 令和8年度（2026年度）版として作成。次年度は入試センター公式の日程を更新してください。
