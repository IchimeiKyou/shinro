import json
import html
from pathlib import Path
from enrichments import ENRICHMENTS


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "universities.json"
OUTPUT_DIR = BASE_DIR / "universities"
CSS_PATH = "../shared.css"
FONT_LINK = '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;600;700&display=swap" rel="stylesheet">'
GUIDE_LINK = "../shinro-guide.html"


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def tier_label(tier: str) -> str:
    mapping = {
        "CHALLENGE": "チャレンジ校",
        "MATCH": "実力相応校",
        "SAFE": "安全校",
    }
    return mapping.get(tier, tier)


def type_badge(univ_type: str) -> str:
    if univ_type == "国立":
        return '<span class="badge national">国立</span>'
    if univ_type == "公立":
        return '<span class="badge national">公立</span>'
    return '<span class="badge private">私立</span>'


def tier_badge(tier: str) -> str:
    cls = tier.lower()
    return f'<span class="badge {esc(cls)}">{esc(tier_label(tier))}</span>'


def koromodai_subtitle(univ: dict) -> str:
    rec = univ.get("koromodai_record")
    if rec and rec.get("total", 0) > 0:
        return f"先輩{rec['total']}名/3年"
    return ""


def uni_link_subtitle(uid: str, univ: dict | None = None) -> str:
    parts = []
    r = ENRICHMENTS.get(uid, {}).get("rankings", {})
    if r.get("the_japan"):
        parts.append(f"THE日本{r['the_japan']}")
    elif r.get("qs_japan"):
        parts.append(r["qs_japan"])
    if univ:
        extra = koromodai_subtitle(univ)
        if extra:
            parts.append(extra)
    if not parts:
        return ""
    return f'<span class="sub">{esc("｜".join(parts))}</span>'


def update_shinro_guide(universities: list[dict]) -> None:
    import re

    guide_path = BASE_DIR / "shinro-guide.html"
    if not guide_path.exists():
        return

    text = guide_path.read_text(encoding="utf-8")
    for univ in universities:
        uid = univ["id"]
        url = f"universities/{uid}.html"
        sub = uni_link_subtitle(uid, univ)
        pattern = (
            rf'(<a class="uni-link" href="{re.escape(url)}">)'
            rf'([^<]+)'
            rf'(?:<span class="sub">[^<]*</span>)?'
            rf'(</a>)'
        )
        text = re.sub(pattern, rf"\1\2{sub}\3", text, count=1)

    guide_path.write_text(text, encoding="utf-8")


def koromodai_html(record):
    if not record:
        return "<p>進路資料（令和5〜7年度）に当該大学の合格者記載はありません。</p>"
    return (
        "<div class=\"table-wrap\"><table>"
        "<thead><tr><th>年度</th><th>人数</th></tr></thead><tbody>"
        f"<tr><td>R7</td><td class=\"num\">{record['r7']}</td></tr>"
        f"<tr><td>R6</td><td class=\"num\">{record['r6']}</td></tr>"
        f"<tr><td>R5</td><td class=\"num\">{record['r5']}</td></tr>"
        f"<tr><td><strong>合計</strong></td><td class=\"num\"><strong>{record['total']}</strong></td></tr>"
        "</tbody></table></div>"
    )


def science_faculties_html(faculties):
    blocks = []
    for f in faculties:
        depts = "、".join(esc(d) for d in f["departments"])
        blocks.append(
            "<div class=\"card\">"
            f"<h3>{esc(f['name'])}</h3>"
            f"<p><strong>主な学科:</strong> {depts}</p>"
            f"<p>{esc(f['description'])}</p>"
            "</div>"
        )
    return "".join(blocks)


def exam_methods_html(methods):
    items = []
    for m in methods:
        items.append(f"<li><strong>{esc(m['name'])}</strong>：{esc(m['description'])}</li>")
    return "<ul>" + "".join(items) + "</ul>"


def references_html(refs):
    items = []
    for r in refs:
        title = esc(r["title"])
        url = esc(r["url"])
        items.append(f"<li><a href=\"{url}\" target=\"_blank\" rel=\"noopener noreferrer\">{title}</a></li>")
    return "<ul class=\"ref-list\">" + "".join(items) + "</ul>"


RANK_LABELS = {
    "the_japan": "THE日本大学ランキング2025",
    "the_world": "THE世界大学ランキング",
    "qs_world": "QS世界大学ランキング",
    "qs_japan": "QS国内順位",
    "deviation": "偏差値目安",
}

DOMESTIC_KEYS = ("the_japan", "qs_japan", "deviation")
DETAIL_KEYS = ("the_world", "qs_world")


def ranking_header_badge(uid: str) -> str:
    e = ENRICHMENTS.get(uid, {})
    r = e.get("rankings", {})
    if r.get("the_japan"):
        return f' <span class="header-rank">THE日本 {esc(r["the_japan"])}</span>'
    if r.get("qs_japan"):
        return f' <span class="header-rank">{esc(r["qs_japan"])}</span>'
    return ""


def domestic_ranking_hero(uid: str) -> str:
    e = ENRICHMENTS.get(uid)
    if not e:
        return ""

    rank = e.get("rankings", {})
    stats = e.get("stats", {})
    the_japan = rank.get("the_japan")
    qs_japan = rank.get("qs_japan")
    deviation = rank.get("deviation") or stats.get("deviation")

    if not the_japan and not qs_japan:
        return ""

    if the_japan:
        label = RANK_LABELS["the_japan"]
        value = the_japan
    else:
        label = RANK_LABELS["qs_japan"]
        value = qs_japan

    extras = []
    if the_japan and qs_japan:
        extras.append(f"QS国内 {qs_japan}")
    if deviation:
        extras.append(f"偏差値 {deviation}")

    extra_html = (
        f'<p class="rank-hero-sub">{esc(" ｜ ".join(extras))}</p>'
        if extras
        else ""
    )

    return f"""
    <section class="rank-hero card">
      <div class="rank-hero-label">{esc(label)}</div>
      <div class="rank-hero-value">{esc(value)}</div>
      {extra_html}
      <p class="rank-hero-note">THE世界・QS世界など詳細ランキングはページ下部を参照</p>
    </section>
    """


def detailed_ranking_html(uid: str) -> str:
    e = ENRICHMENTS.get(uid)
    if not e:
        return ""

    rank = e.get("rankings", {})
    rows = []
    for key in DETAIL_KEYS:
        if rank.get(key):
            rows.append(
                f"<tr><td>{esc(RANK_LABELS[key])}</td>"
                f"<td><strong>{esc(rank[key])}</strong></td></tr>"
            )

    if not rows:
        return ""

    table = (
        '<div class="table-wrap"><table><thead><tr><th>ランキング種別</th><th>順位</th></tr></thead>'
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )
    return f"""
    <section class="card">
      <h2>世界ランキング・詳細（参考）</h2>
      <p style="font-size:.85rem;color:var(--text-sub)">THE/QS等の国際比較用指標。年度・評価方法により変動します。</p>
      {table}
    </section>
    """


def enrichment_html(uid: str) -> str:
    e = ENRICHMENTS.get(uid)
    if not e:
        return "<p class=\"insight insight-warn\">定量データは準備中です。公式サイト・パスナビで最新情報を確認してください。</p>"

    stats = e.get("stats", {})
    stat_labels = {
        "students": "学生数",
        "employment_rate": "就職率",
        "grad_school_rate": "大学院進学率",
        "tuition_annual": "年間学費",
        "deviation": "偏差値目安",
    }
    stat_rows = "".join(
        f"<tr><td>{esc(stat_labels.get(k, k))}</td><td>{esc(str(v))}</td></tr>"
        for k, v in stats.items()
    )
    stat_table = (
        f'<div class="table-wrap"><table><thead><tr><th>指標</th><th>数値・目安</th></tr></thead>'
        f"<tbody>{stat_rows}</tbody></table></div>"
        if stat_rows else ""
    )

    pros = e.get("pros", [])
    cons = e.get("cons", [])
    pros_html = "<ul>" + "".join(f"<li>{esc(p)}</li>" for p in pros) + "</ul>" if pros else ""
    cons_html = "<ul>" + "".join(f"<li>{esc(c)}</li>" for c in cons) + "</ul>" if cons else ""

    return f"""
    <section class="card">
      <h2>定量データ</h2>
      {stat_table}
    </section>
    <section class="card">
      <h2>長所・短所（志望校選びの観点）</h2>
      <h3 style="color:#059669">メリット</h3>{pros_html}
      <h3 style="color:#dc2626;margin-top:1rem">デメリット</h3>{cons_html}
    </section>
    <section class="card">
      <h2>カリキュラム・育成方針の特色</h2>
      <p>{esc(e.get("curriculum", ""))}</p>
    </section>
    <section class="card">
      <h2>社会的認知度・就職評価</h2>
      <p>{esc(e.get("recognition", ""))}</p>
    </section>
    """


def university_page(univ: dict) -> str:
    exam = univ["exam_general"]
    uid = univ["id"]
    enrich = enrichment_html(uid)
    rank_hero = domestic_ranking_hero(uid)
    rank_detail = detailed_ranking_html(uid)
    rank_badge = ranking_header_badge(uid)
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(univ["name"])} | 進路ガイド</title>
  {FONT_LINK}
  <link rel="stylesheet" href="{CSS_PATH}">
</head>
<body>
  <header class="site-header">
    <h1>{esc(univ["name"])}</h1>
    <div class="subtitle">{tier_badge(univ["tier"])}{type_badge(univ["type"])}{esc(univ["location"])}{rank_badge}</div>
    <div class="breadcrumb"><a href="{GUIDE_LINK}">進路ガイド</a> / <a href="./index.html">大学一覧</a></div>
  </header>

  <main class="container">
    <a class="nav-back" href="{GUIDE_LINK}">← 進路ガイドに戻る</a> <a class="nav-back" href="./index.html" style="margin-left:1rem">大学一覧</a>

    {rank_hero}

    <section class="card">
      <h2>基本情報</h2>
      <p><strong>大学名:</strong> {esc(univ["name"])}</p>
      <p><strong>英語名:</strong> {esc(univ.get("name_en", "未設定"))}</p>
      <p><strong>所在地:</strong> {esc(univ["location"])}</p>
      <p><strong>公式:</strong> <a href="{esc(univ["official_url"])}" target="_blank" rel="noopener noreferrer">{esc(univ["official_url"])}</a></p>
      <p><strong>入試情報:</strong> <a href="{esc(univ["admissions_url"])}" target="_blank" rel="noopener noreferrer">{esc(univ["admissions_url"])}</a></p>
      <p><strong>パスナビ:</strong> <a href="{esc(univ["passnavi_url"])}" target="_blank" rel="noopener noreferrer">{esc(univ["passnavi_url"])}</a></p>
    </section>

    <section>
      <h2>進路資料における実績（令和5〜7年度）</h2>
      {koromodai_html(univ.get("koromodai_record"))}
    </section>

    <section>
      <h2>理系学部情報</h2>
      {science_faculties_html(univ["science_faculties"])}
    </section>

    {enrich}

    <section class="card">
      <h2>一般選抜の目安</h2>
      <p><strong>共通テスト:</strong> {esc(exam["common_test"])}</p>
      <p><strong>個別試験:</strong> {esc(exam["second_exam"])}</p>
      <p><strong>配点比率:</strong> {esc(exam["ratio"])}</p>
      <p class="insight insight-warn"><strong>注意:</strong> {esc(exam["notes"])}</p>
    </section>

    <section class="card">
      <h2>主な入試方式</h2>
      {exam_methods_html(univ["exam_methods"])}
    </section>

    <section class="card">
      <h2>大学の特徴（理系向け）</h2>
      <p>{esc(univ["features"])}</p>
    </section>

    <section class="card">
      <h2>進路傾向</h2>
      <p>{esc(univ["career"])}</p>
    </section>

    {rank_detail}

    <section class="card">
      <h2>参考リンク</h2>
      {references_html(univ["references"])}
    </section>
  </main>

  <footer class="site-footer">
    受験情報は必ず最新の募集要項で最終確認してください。
  </footer>
</body>
</html>
"""


def index_page(universities: list[dict]) -> str:
    grouped = {"CHALLENGE": [], "MATCH": [], "SAFE": []}
    for univ in universities:
        grouped.setdefault(univ["tier"], []).append(univ)

    sections = []
    for tier in ("CHALLENGE", "MATCH", "SAFE"):
        links = []
        for u in grouped.get(tier, []):
            e = ENRICHMENTS.get(u["id"], {})
            r = e.get("rankings", {})
            rank_txt = r.get("the_japan") or r.get("qs_japan") or "ランキング未掲載"
            links.append(
                f'<a class="uni-link" href="./{esc(u["id"])}.html">{esc(u["name"])}'
                f'<span class="sub">THE日本 {esc(rank_txt)} ｜ {esc(u["location"])} / {esc(u["type"])}</span></a>'
            )
        section = (
            f"<section><h2>{esc(tier_label(tier))}</h2>"
            f"<div class=\"uni-grid\">{''.join(links)}</div></section>"
        )
        sections.append(section)

    total = len(universities)
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>大学一覧 | 進路ガイド</title>
  {FONT_LINK}
  <link rel="stylesheet" href="{CSS_PATH}">
</head>
<body>
  <header class="site-header">
    <h1>理系進路向け 大学データ一覧</h1>
    <div class="subtitle">登録大学数: {total}校</div>
    <div class="breadcrumb"><a href="{GUIDE_LINK}">← 進路ガイドに戻る</a></div>
  </header>

  <main class="container">
    <section class="card">
      <p>このページは <code>universities.json</code> から自動生成されています。各大学ページには理系学部、入試目安、参考リンクを掲載しています。</p>
      <p class="insight">最終的な出願判断は必ず大学公式の募集要項で確認してください。</p>
    </section>
    {''.join(sections)}
  </main>

  <footer class="site-footer">
    生成スクリプト: generate_universities.py
  </footer>
</body>
</html>
"""


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"{DATA_PATH} が見つかりません。")

    with DATA_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    universities = data.get("universities", [])
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    index_html = index_page(universities)
    (OUTPUT_DIR / "index.html").write_text(index_html, encoding="utf-8")

    for univ in universities:
        page = university_page(univ)
        filename = f"{univ['id']}.html"
        (OUTPUT_DIR / filename).write_text(page, encoding="utf-8")

    update_shinro_guide(universities)


if __name__ == "__main__":
    main()
