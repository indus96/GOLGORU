#!/usr/bin/env python3
"""docs/*.md → docs/*.html (랜딩과 같은 톤의 정적 문서 페이지).
마크다운은 소스로 두고, 문서를 고치면 `python3 build-docs.py`로 재생성한다."""
import re, html, glob, os

DOCS = {
    "dashboard":            dict(eyebrow="대시보드",   hero="../images/app/phone-dashboard.png", cls="phone"),
    "portfolio-analysis":   dict(eyebrow="자산 분석",  hero="../images/app/phone-analysis.png",  cls="phone"),
    "asset-ranking":        dict(eyebrow="자산순위",   hero="../images/app/phone-stock.png",     cls="phone"),
    "allocation-rebalancing":dict(eyebrow="자산배분",  hero="../images/app/phone-allocation.png", cls="phone"),
    "news-reports":         dict(eyebrow="뉴스·리포트", hero="../images/app/phone-news.png",     cls="phone"),
    "ai-review":            dict(eyebrow="AI 점검",    hero="../images/news-ai.svg",             cls="wide"),
    "broker-connection":    dict(eyebrow="증권사 연결", hero="../images/app/phone-broker.png",    cls="phone"),
    "data-security":        dict(eyebrow="데이터·보안", hero="../images/data-flow.svg",           cls="wide",
                                 lead="자산 데이터는 기기 안이나 내 시트에만 있고, 자격증명은 기기 Keychain에만 둡니다."),
    "getting-started":      dict(eyebrow="시작하기",   hero="../images/data-flow.svg",           cls="wide",
                                 lead="둘러보기 · 앱에 직접 입력 · Google Sheets 연동 — 세 가지 중에서 고릅니다."),
    "privacy":              dict(eyebrow="개인정보",   hero="", cls="wide",
                                 lead="앱은 자산 데이터를 제공자 서버에 저장하지 않습니다."),
}

NAV = """<nav><div class="wrap nav-in">
  <!-- 앱 이름은 "골고루" 하나다. 로마자를 붙여 쓰면 텍스트로 읽을 때
       "골고루GOLGORU"가 되어, OAuth 동의 화면 이름과 자동 비교에서 어긋난다. -->
  <a class="brand" href="../index.html">골고루</a>
  <div class="nav-links">
    <a href="../index.html#dashboard">대시보드</a>
    <a href="../index.html#analysis">자산 분석</a>
    <a href="../index.html#rebalance">자산배분</a>
    <a href="../index.html#broker">증권사</a>
  </div>
  <a class="cta" href="https://github.com/indus96/GOLGORU">GitHub ↗</a>
</div></nav>"""

FOOTER = """<footer><div class="wrap foot-in">
  <div>© 2026 골고루 · 내 자산을 골고루.</div>
  <div><a href="../index.html">홈</a> · <a href="getting-started.html">시작하기</a> · <a href="privacy.html">개인정보처리방침</a> · <a href="https://github.com/indus96/GOLGORU">GitHub</a></div>
</div></footer>"""


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1">', t)
    def link(m):
        url = re.sub(r"\.md(#|$)", r".html\1", m.group(2))
        return f'<a href="{url}">{m.group(1)}</a>'
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t


def cells(row):
    return [c.strip() for c in row.strip().strip("|").split("|")]


def render_table(rows):
    head = "".join(f"<th>{inline(c)}</th>" for c in cells(rows[0]))
    body = ""
    for r in rows[2:]:
        body += "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells(r)) + "</tr>"
    return f'<div class="tablewrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


SPECIAL = re.compile(r"^(#{1,3}\s|\||\d+\.\s|-\s|```)")


def convert(md, hero):
    lines = md.split("\n")
    n = len(lines)
    out, title, lead = [], None, None
    seen_h2 = False
    i = 0
    while i < n:
        s = lines[i].strip()
        if not s:
            i += 1; continue
        # fenced code
        if s.startswith("```"):
            i += 1; buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            out.append("<pre><code>" + html.escape("\n".join(buf)) + "</code></pre>")
            continue
        # heading
        m = re.match(r"^(#{1,3})\s+(.*)$", s)
        if m:
            lvl, txt = len(m.group(1)), m.group(2)
            if lvl == 1 and title is None:
                title = txt
            elif lvl == 1:
                out.append(f"<h1>{inline(txt)}</h1>")
            else:
                if lvl == 2: seen_h2 = True
                out.append(f"<h{lvl}>{inline(txt)}</h{lvl}>")
            i += 1; continue
        # standalone image
        im = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", s)
        if im:
            if im.group(2) != hero:
                out.append(f'<figure><img src="{im.group(2)}" alt="{inline(im.group(1))}"></figure>')
            i += 1; continue
        # table
        if s.startswith("|"):
            tbl = []
            while i < n and lines[i].strip().startswith("|"):
                tbl.append(lines[i]); i += 1
            out.append(render_table(tbl)); continue
        # lists
        for tag, pat in (("ol", r"^\d+\.\s+(.*)$"), ("ul", r"^-\s+(.*)$")):
            if re.match(pat, s):
                items = []
                while i < n:
                    ls = lines[i].strip()
                    mm = re.match(pat, ls)
                    if mm:
                        items.append(mm.group(1))
                    elif ls and not SPECIAL.match(ls) and not ls.startswith("!["):
                        if items: items[-1] += " " + ls
                        else: break
                    else:
                        break
                    i += 1
                out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
                break
        else:
            # paragraph
            buf = []
            while i < n:
                ls = lines[i].strip()
                if not ls or SPECIAL.match(ls) or ls.startswith("!["):
                    break
                buf.append(ls); i += 1
            para = " ".join(buf)
            if lead is None and not seen_h2:
                lead = para  # 첫 문단(제목 뒤·첫 ## 앞)은 히어로 리드로
            else:
                out.append(f"<p>{inline(para)}</p>")
            continue
    return title, lead, "\n".join(out)


def build(slug, meta):
    md = open(f"docs/{slug}.md", encoding="utf-8").read()
    title, lead, body = convert(md, meta["hero"])
    lead = lead or meta.get("lead", "")
    lead_html = inline(lead) if lead else ""
    lead_plain = re.sub(r"<[^>]+>", "", lead_html)
    page = f"""<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>골고루 · {title}</title>
<meta property="og:site_name" content="골고루">
<meta name="application-name" content="골고루">
<meta name="description" content="{lead_plain}">
<link rel="stylesheet" href="doc.css">
</head><body>
{NAV}
<header class="doc-hero"><div class="wrap">
  <a class="back" href="../index.html">← 골고루 홈</a>
  <div class="eyebrow">{meta['eyebrow']}</div>
  <h1>{inline(title)}</h1>
  {f'<p class="lead">{lead_html}</p>' if lead_html else ''}
  {f'''<div class="hero-img {meta['cls']}"><img src="{meta['hero']}" alt="{inline(title)} 화면"></div>''' if meta['hero'] else ''}
</div></header>
<main class="doc-body"><div class="wrap narrow">
{body}
</div></main>
{FOOTER}
</body></html>
"""
    open(f"docs/{slug}.html", "w", encoding="utf-8").write(page)
    print(f"built docs/{slug}.html  (title={title})")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    for slug, meta in DOCS.items():
        build(slug, meta)
