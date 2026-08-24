#!/usr/bin/env python3
"""docs/*.md → docs/*.html (랜딩과 같은 톤의 정적 문서 페이지).
마크다운은 소스로 두고, 문서를 고치면 `python3 build-docs.py`로 재생성한다."""
import re, html, glob, os, datetime, pathlib, unicodedata, hashlib

# `back`은 랜딩에서 이 문서로 들어오는 섹션이다. 돌아갈 때 그 자리로 보낸다.
# (JS가 되면 history.back()으로 정확한 스크롤 위치를 복원하고, 이건 그 대비책이다.)
# 정본 도메인. 색인은 이 주소 하나만 본다 — http·www 로 들어온 것은 여기로 접힌다.
SITE = "https://golgoru.app"

DOCS = {
    # eyebrow 는 2.0 화면 이름이다. **파일 이름(주소)은 안 바꾼다** — 밖에서 걸어 둔
    # 링크와 앱 안 도움말이 이 주소를 쓴다.
    "dashboard":            dict(eyebrow="홈",        hero="../images/app/phone-dashboard.png", cls="phone", back="dashboard"),
    "portfolio-analysis":   dict(eyebrow="구성 리포트", hero="../images/app/phone-analysis.png",  cls="phone", back="analysis"),
    "asset-ranking":        dict(eyebrow="자산",      hero="../images/app/stock-analysis.png",     cls="phone", back="analysis"),
    "allocation-rebalancing":dict(eyebrow="조정안",   hero="../images/app/phone-allocation.png", cls="phone", back="rebalance"),
    "news-reports":         dict(eyebrow="뉴스·리포트", hero="../images/app/phone-news.png",     cls="phone", back="rebalance"),
    # 2.0에서 화면은 뺐지만 주소는 살려 둔다 — 밖에서 걸어 둔 링크가 깨지지 않게.
    "ai-review":            dict(eyebrow="계획",      hero="",                                  cls="wide", back="rebalance",
                                 lead="2.0에서 뺀 화면입니다. 짜보기 탭과 자산 탭이 나눠 맡습니다."),
    "portfolio-draft":      dict(eyebrow="짜보기",    hero="../images/app/phone-draft.png",     cls="phone", back="rebalance",
                                 lead="사기 전에 구성을 짜 보고, 남이 짜 본 조합도 봅니다."),
    # 2.0에서 기능은 뺐지만 주소는 살려 둔다 — 밖에서 걸어 둔 링크가 깨지지 않게.
    "broker-connection":    dict(eyebrow="증권사 연결", hero="",                                  cls="wide", back="about",
                                 lead="2.0에서 뺀 기능입니다. 캡처로 가져오기가 대신합니다."),
    "data-security":        dict(eyebrow="데이터·보안", hero="../images/data-flow.svg",           cls="wide", back="about",
                                 lead="자산 데이터는 기기 안이나 내 시트에만 있고, 자격증명은 기기 Keychain에만 둡니다."),
    "getting-started":      dict(eyebrow="시작하기",   hero="../images/data-flow.svg",           cls="wide", back="download",
                                 lead="둘러보기와 앱에 직접 입력 중에서 고르고, 증권사 화면 캡처로 종목을 채웁니다."),
    "privacy":              dict(eyebrow="개인정보",   hero="", cls="wide", back="about",
                                 lead="앱은 자산 데이터를 제공자 서버에 저장하지 않습니다."),
    "changelog":            dict(eyebrow="버전 기록",  hero="", cls="wide", back="download",
                                 lead="어떤 기능이 어느 버전에 들어갔는지 적어 둡니다."),
}

# 홈은 `../`로만 건다. `../index.html`은 같은 내용을 다른 주소로 200을 주는
# 중복 주소여서, 색인이 "표준 태그가 있는 대체 페이지"로 잡고 크롤링을 낭비한다.
# **헤더는 여기 한 곳에서만 정의한다.** 예전에는 index.html·p/·c/·이 파일 넷이
# 각자 같은 목록을 들고 있어서, 링크를 하나 더하면 어딘가는 빠졌다(2026-08-21
# 「나눔터」가 실제로 그렇게 빠졌다). 아래 `render_nav` 가 페이지 깊이에 맞는
# 상대 경로로 찍어 주고, `inject_shared` 가 정적 파일들의 마커 사이를 갈아 끼운다.
#
# 빌드 시점에 넣는 것이지 자바스크립트로 그리는 것이 아니다 — JS 로 그리면
# 스크립트가 막힌 브라우저와 크롤러에 헤더가 통째로 사라진다.
NAV_LINKS = [
    ("{root}#about", "앱 소개"),
    # 기능 항목은 드롭다운 하나로 접는다. 펼쳐 두면 링크가 11개가 되어 한 줄을
    # 넘겼고, 「맥·아이패드」처럼 최상위에 있을 무게가 아닌 것도 섞여 있었다.
    ("기능", [
        ("{root}#dashboard", "대시보드"),
        ("{root}#analysis", "자산 분석"),
        ("{root}#rebalance", "자산배분"),
        ("{root}#capture", "계좌 채우기"),
        ("{root}docs/portfolio-draft.html", "짜보기"),
        ("{root}#mac", "맥·아이패드"),
    ]),
    ("{root}#principles", "원칙"),
    ("{root}c/", "나눔터"),
    ("{root}#download", "다운로드"),
    # 「버전 기록」은 푸터에만 둔다 — 헤더에 있을 만큼 자주 보는 문서가 아니다.
]


def render_nav_item(href, label, root):
    if isinstance(label, list):
        subs = "\n".join(
            f'      <a href="{h.format(root=root)}">{t}</a>' for h, t in label
        )
        return (
            f'    <div class="nav-group">\n'
            f'      <button class="nav-group-btn" type="button" aria-expanded="false">{href}</button>\n'
            f'      <div class="nav-sub">\n{subs}\n      </div>\n'
            f'    </div>'
        )
    return f'    <a href="{href.format(root=root)}">{label}</a>'


def render_nav(root, cta="다운로드"):
    """`root` 는 사이트 루트까지의 상대 경로("" 또는 "../")."""
    links = "\n".join(render_nav_item(href, label, root) for href, label in NAV_LINKS)
    return f"""<nav><div class="wrap nav-in">
  <!-- 앱 이름은 "골고루" 하나다. 로마자를 붙여 쓰면 텍스트로 읽을 때
       "골고루GOLGORU"가 되어, OAuth 동의 화면 이름과 자동 비교에서 어긋난다. -->
  <a class="brand" href="{root or './'}"><img src="{root}images/app-icon.png" alt="" width="26" height="26">골고루</a>
  <div class="menu">
    <button class="menu-btn" type="button" aria-expanded="false">메뉴</button>
  <div class="nav-links">
{links}
  </div>
  </div>
  <a class="cta" href="{root}#download" data-cta="1">{cta}</a>
</div></nav>"""


NAV = render_nav("../")

# 공유 자원 캐시 무효화.
#
# GitHub Pages 가 site.js·doc.css 를 max-age=14400(4시간)으로 준다. 헤더 구조를
# 바꾼 날 다시 온 사람은 새 HTML 에 4시간 묵은 CSS/JS 를 받아서, 드롭다운이
# 스타일 없이 통째로 펼쳐진 헤더를 본다. 내용 해시를 주소에 붙여 파일이 실제로
# 바뀐 날에만, 바뀐 파일만 새로 받게 한다.
SHARED_ASSETS = ["site.js", "docs/doc.css"]


def stamp_assets(path):
    text = pathlib.Path(path).read_text(encoding="utf-8")
    before = text
    for asset in SHARED_ASSETS:
        digest = hashlib.sha256(pathlib.Path(asset).read_bytes()).hexdigest()[:8]
        name = re.escape(os.path.basename(asset))
        text = re.sub(rf'((?:\.\./)*(?:docs/)?{name})(\?v=[0-9a-f]+)?"',
                      rf'\g<1>?v={digest}"', text)
    if text != before:
        pathlib.Path(path).write_text(text, encoding="utf-8")


def inject_shared(path, root, cta="다운로드"):
    """정적 파일의 `<!-- nav:start -->`~`<!-- nav:end -->` 사이를 헤더로 채운다.

    마커가 없으면 아무것도 안 한다 — 손으로 쓴 페이지를 조용히 망가뜨리지 않는다.
    """
    text = pathlib.Path(path).read_text(encoding="utf-8")
    begin, close = "<!-- nav:start -->", "<!-- nav:end -->"
    if begin not in text or close not in text:
        print(f"skip {path} (마커 없음)")
        return
    head, rest = text.split(begin, 1)
    _, tail = rest.split(close, 1)
    pathlib.Path(path).write_text(
        head + begin + "\n" + render_nav(root, cta) + "\n" + close + tail, encoding="utf-8"
    )
    print(f"nav  {path}")


FOOTER = """<footer><div class="wrap foot-in">
  <div>© 2026 골고루 · 내 자산을 골고루.</div>
  <div><a href="../">홈</a> · <a href="getting-started.html">시작하기</a> · <a href="privacy.html">개인정보처리방침</a> · <a href="https://github.com/indus96/GOLGORU">GitHub</a></div>
</div></footer>"""


# 랜딩에서 들어왔다면 뒤로 가기로 돌려보낸다 — 브라우저가 보던 스크롤 위치를
# 그대로 복원하므로 섹션 앵커보다 정확하다. 직접 들어온 경우(검색·북마크·다른
# 문서에서 온 경우)에는 링크의 앵커가 그대로 쓰인다.
BACK_SCRIPT = """<script>
function golgoruBack(event) {
  try {
    var from = document.referrer ? new URL(document.referrer) : null;
    if (from && from.origin === location.origin && /\\/(index\\.html)?$/.test(from.pathname)) {
      event.preventDefault();
      history.back();
      return false;
    }
  } catch (e) {}
  return true;
}
</script>"""


def more_docs(current):
    """문서 사이를 오갈 수 있게 하단에 목록을 붙인다.

    상단 내비게이션은 랜딩 앵커로만 가서, 문서에 들어오면 다른 문서로
    넘어갈 방법이 없었다. 문서가 10개라 상단에 다 넣을 수는 없다.
    """
    items = []
    for slug, meta in DOCS.items():
        label = meta["eyebrow"]
        if slug == current:
            items.append(f'<span class="doc-card current">{label}</span>')
        else:
            items.append(f'<a class="doc-card" href="{slug}.html">{label}</a>')
    return f"""<section class="more-docs"><div class="wrap narrow">
  <h2>다른 문서</h2>
  <div class="doc-cards">{''.join(items)}</div>
</div></section>"""


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


SPECIAL = re.compile(r"^(#{1,3}\s|\||\d+\.\s|-\s|```|>)")


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
        # blockquote — "지원 방식" 같은 머리 주석이다. 문단으로 처리하면 이게
        # 리드·meta description을 차지해서, 여러 문서가 같은 설명을 갖게 된다.
        if s.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip()); i += 1
            out.append(f"<blockquote>{inline(' '.join(buf))}</blockquote>")
            continue
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


def open_external_in_new_tab(html):
    """바깥으로 나가는 링크만 새 창으로 연다.

    문서 안을 오가는 링크는 같은 창이라야 뒤로가기가 자연스럽다. noopener 없이
    _blank를 쓰면 열린 쪽에서 window.opener로 이 페이지를 조작할 수 있다.
    """
    return re.sub(
        r'<a (?![^>]*target=)([^>]*href="https?://[^"]*")',
        r'<a \1 target="_blank" rel="noopener"',
        html,
    )


def build(slug, meta):
    md = open(f"docs/{slug}.md", encoding="utf-8").read()
    title, lead, body = convert(md, meta["hero"])
    lead = lead or meta.get("lead", "")
    lead_html = inline(lead) if lead else ""
    # meta description은 태그도 엔티티도 없는 평문이어야 한다. 검색결과에서
    # 잘리지 않게 155자로 자르고, 자를 때는 단어(어절) 경계에서 끊는다.
    lead_plain = html.unescape(re.sub(r"<[^>]+>", "", lead_html))
    lead_plain = unicodedata.normalize("NFC", " ".join(lead_plain.split()))
    if len(lead_plain) > 155:
        lead_plain = lead_plain[:155].rsplit(" ", 1)[0] + "…"
    # 색인은 주소 하나만 봐야 한다 — 여기서 정본 주소를 못 박는다.
    canonical = f"{SITE}/docs/{slug}.html"
    page = f"""<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>골고루 · {title}</title>
<meta property="og:site_name" content="골고루">
<meta name="application-name" content="골고루">
<meta name="description" content="{html.escape(lead_plain, quote=True)}">
<meta property="og:title" content="골고루 · {title}">
<meta property="og:description" content="{html.escape(lead_plain, quote=True)}">
<meta property="og:type" content="article">
<link rel="canonical" href="{canonical}">
<meta property="og:url" content="{canonical}">
<link rel="stylesheet" href="doc.css">
</head><body>
{NAV}
<header class="doc-hero"><div class="wrap">
  <a class="back" href="../#{meta.get('back', 'top')}"
     onclick="return golgoruBack(event)">← 골고루 홈</a>
  <div class="eyebrow">{meta['eyebrow']}</div>
  <h1>{inline(title)}</h1>
  {f'<p class="lead">{lead_html}</p>' if lead_html else ''}
  {f'''<div class="hero-img {meta['cls']}"><img src="{meta['hero']}" alt="{inline(title)} 화면"></div>''' if meta['hero'] else ''}
</div></header>
<main class="doc-body"><div class="wrap narrow">
{body}
</div></main>
{more_docs(slug)}
{FOOTER}
{BACK_SCRIPT}
<script src="../site.js" defer></script>
</body></html>
"""
    open(f"docs/{slug}.html", "w", encoding="utf-8").write(open_external_in_new_tab(page))
    print(f"built docs/{slug}.html  (title={title})")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    for slug, meta in DOCS.items():
        build(slug, meta)


def write_sitemap():
    """색인 대상 주소를 한 곳에 모아 준다.

    리디렉션·중복으로 떨어진 주소들이 계속 크롤링되는 것보다, 정본 목록을 주고
    거기만 보게 하는 편이 빠르다. 문서 목록에서 만들므로 문서가 늘어도 빠지지 않는다.
    """
    today = datetime.date.today().isoformat()
    # `/c/`(나눔터 둘러보기)는 문서가 아니라 손으로 쓴 페이지라 DOCS 에 없다 —
    # 여기 직접 넣는다. 실제 내용이 있고 색인될 값이 있는 유일한 비문서 페이지다.
    # `/p/`(공유 코드 보기)는 넣지 않는다: 내용이 URL 조각(#) 뒤에만 있어 코드마다
    # 다른 페이지를 색인할 수 없고, 코드 없는 상태로는 안내문 몇 줄뿐이다(noindex).
    urls = (
        [f"{SITE}/", f"{SITE}/c/"]
        + [f"{SITE}/docs/{name}.html" for name in sorted(DOCS)]
    )
    body = "\n".join(
        f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>" for u in urls)
    pathlib.Path("sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n</urlset>\n")
    pathlib.Path("robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")


write_sitemap()

# 손으로 쓴 페이지 셋도 같은 헤더를 받는다. 이 줄이 "헤더가 네 곳에 흩어져 있다"는
# 문제의 답이다 — 링크를 더하려면 위 NAV_LINKS 하나만 고치고 이 스크립트를 돌린다.
inject_shared("index.html", "", cta="앱 받기")
inject_shared("p/index.html", "../")
inject_shared("c/index.html", "../", cta="앱 받기")

for page in ["index.html", "p/index.html", "c/index.html"] + glob.glob("docs/*.html"):
    stamp_assets(page)
print("asset stamp  " + ", ".join(SHARED_ASSETS))
