#!/usr/bin/env python3
"""docs/*.md → docs/*.html (랜딩과 같은 톤의 정적 문서 페이지).
마크다운은 소스로 두고, 문서를 고치면 `python3 build-docs.py`로 재생성한다."""
import re, html, glob, os, datetime, pathlib, unicodedata, hashlib

# `back`은 랜딩에서 이 문서로 들어오는 섹션이다. 돌아갈 때 그 자리로 보낸다.
# (JS가 되면 history.back()으로 정확한 스크롤 위치를 복원하고, 이건 그 대비책이다.)
# 정본 도메인. 색인은 이 주소 하나만 본다 — http·www 로 들어온 것은 여기로 접힌다.
SITE = "https://golgoru.app"

# 영문판은 `/en/` 하위에 둔다. **한국어는 루트 그대로다** — 밖에서 걸어 둔 링크와
# 앱 안 도움말, OAuth 브랜드 검증이 전부 그 주소를 본다(2026-09-17).
#
# `home` 은 그 언어의 랜딩까지, `assets` 는 사이트 루트까지의 상대 경로다. 문서가
# `/docs/x.html`(한국어)과 `/en/docs/x.html`(영어)로 깊이가 달라 둘을 갈라 둔다.
LANGS = {
    "ko": dict(
        src="docs", out="docs", url="docs", home="../", assets="../",
        brand="골고루", back="← 골고루 홈", more="다른 문서", cta="다운로드",
        title_sep="골고루 · ",
    ),
    "en": dict(
        src="docs/en", out="en/docs", url="en/docs", home="../", assets="../../",
        brand="Golgoru", back="← Golgoru home", more="Other pages", cta="Get the app",
        title_sep="Golgoru · ",
    ),
}

DOCS = {
    # eyebrow 는 2.0 화면 이름이다. **파일 이름(주소)은 안 바꾼다** — 밖에서 걸어 둔
    # 링크와 앱 안 도움말이 이 주소를 쓴다.
    "dashboard":            dict(en=dict(eyebrow="Home"), eyebrow="홈",        hero="../images/app/phone-dashboard.png", cls="phone", back="dashboard"),
    "portfolio-analysis":   dict(en=dict(eyebrow="Portfolio report"), eyebrow="구성 리포트", hero="../images/app/phone-analysis.png",  cls="phone", back="analysis"),
    "asset-ranking":        dict(en=dict(eyebrow="Assets"), eyebrow="자산",      hero="../images/app/stock-analysis.png",     cls="phone", back="analysis"),
    "allocation-rebalancing":dict(en=dict(eyebrow="Adjustment plan"), eyebrow="조정안",   hero="../images/app/phone-allocation.png", cls="phone", back="rebalance"),
    "news-reports":         dict(en=dict(eyebrow="News · reports"), eyebrow="뉴스·리포트", hero="../images/app/phone-news.png",     cls="phone", back="rebalance"),
    # 2.0에서 화면은 뺐지만 주소는 살려 둔다 — 밖에서 걸어 둔 링크가 깨지지 않게.
    "ai-review":            dict(eyebrow="계획",      hero="",                                  cls="wide", back="rebalance",
                                 lead="2.0에서 뺀 화면입니다. 짜보기 탭과 자산 탭이 나눠 맡습니다."),
    "portfolio-draft":      dict(en=dict(eyebrow="Build", lead="Try a mix before you buy it, and look at what other people put together."), eyebrow="짜보기",    hero="../images/app/phone-draft.png",     cls="phone", back="rebalance",
                                 lead="사기 전에 구성을 짜 보고, 남이 짜 본 조합도 봅니다."),
    # 2.0에서 뺐다가 3.0 에 한투 조회 연동으로 돌아왔다. 주소는 그대로다.
    "broker-connection":    dict(en=dict(eyebrow="Brokerage connection", lead="Read your Korea Investment balances to fill your accounts. Golgoru never places orders."), eyebrow="증권사 연결", hero="",                                  cls="wide", back="about",
                                 lead="한국투자증권 잔고를 읽어 계좌를 채웁니다. 주문은 내지 않습니다."),
    "data-security":        dict(en=dict(eyebrow="Data · security", lead="Your asset data stays on your device or in your own sheet, and credentials live only in the device keychain."), eyebrow="데이터·보안", hero="../images/data-flow.svg",           cls="wide", back="about",
                                 lead="자산 데이터는 기기 안이나 내 시트에만 있고, 자격증명은 기기 Keychain에만 둡니다."),
    "getting-started":      dict(en=dict(eyebrow="Getting started", lead="Pick between looking around and entering your own assets, then fill in holdings from a brokerage screenshot."), eyebrow="시작하기",   hero="../images/data-flow.svg",           cls="wide", back="download",
                                 lead="둘러보기와 앱에 직접 입력 중에서 고르고, 증권사 화면 캡처로 종목을 채웁니다."),
    # 나눔터 주제 페이지 — 검색으로 들어오는 입구다(성장 문서 1-2). 조합을 시딩할
    # 때마다 표에 줄을 더한다. 조합 상세는 /c/?id= 로 연결된다.
    "portfolio-pension":    dict(eyebrow="나눔터",    hero="../images/app/phone-community.png", cls="phone", back="rebalance",
                                 lead="연금저축·퇴직연금 DC·IRP 에서 ETF 로 굴리는 조합 예시 모음입니다."),
    "portfolio-isa":        dict(eyebrow="나눔터",    hero="../images/app/phone-community.png", cls="phone", back="rebalance",
                                 lead="ISA 계좌에서 국내 상장 ETF 로 굴리는 조합 예시 모음입니다."),
    "portfolio-monthly-dividend": dict(eyebrow="나눔터", hero="../images/app/phone-community.png", cls="phone", back="rebalance",
                                 lead="매달 분배금이 들어오는 월배당 ETF 조합 예시 모음입니다."),
    "portfolio-us-index":   dict(eyebrow="나눔터",    hero="../images/app/phone-community.png", cls="phone", back="rebalance",
                                 lead="S&P500·나스닥100 을 국내 상장 ETF 로 담는 조합 예시 모음입니다."),
    "portfolio-kr-index":   dict(eyebrow="나눔터",    hero="../images/app/phone-community.png", cls="phone", back="rebalance",
                                 lead="코스피200 중심의 국내지수 ETF 조합 예시 모음입니다."),
    # 안내 글 — 연금 · IRP 에 적립하는 자산배분 투자자가 검색하는 질문에 답한다(2026-10-02).
    "guide-irp-risk-70":    dict(eyebrow="안내",      hero="../images/app/phone-allocation.png", cls="phone", back="rebalance",
                                 lead="IRP · DC 는 위험자산을 70%까지만 담습니다. 무엇이 위험자산인지, 넘으면 어떻게 되는지, 목표 비중으로 미리 맞추는 법."),
    "guide-pension-rebalancing": dict(eyebrow="안내",  hero="../images/app/phone-allocation.png", cls="phone", back="rebalance",
                                 lead="연금계좌 ETF 리밸런싱을 언제, 얼마나 할지 — 날짜 · 차이 기준, 적립금으로 팔지 않고 맞추기, 주수 계산."),
    "privacy":              dict(en=dict(eyebrow="Privacy", lead="The app does not store your asset data on our servers."), eyebrow="개인정보",   hero="", cls="wide", back="about",
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
# 영문판 내비게이션. 한국어와 **항목이 같지 않다** — 나눔터 주제 페이지와 영상은
# 한국어 검색으로 들어오는 입구라 영문판에 없다. 없는 페이지로 보내면 안 된다.
NAV_LINKS_EN = [
    ("{home}#about", "About"),
    ("Features", [
        ("{home}#dashboard", "Home"),
        ("{home}#analysis", "Portfolio report"),
        ("{home}#rebalance", "Adjustment plan"),
        ("{home}#capture", "Screenshot import"),
        ("{home}docs/portfolio-draft.html", "Build"),
        ("{home}#mac", "Mac · iPad"),
    ]),
    ("{home}#principles", "Principles"),
    ("{home}#download", "Download"),
]

NAV_LINKS = [
    ("{home}#about", "앱 소개"),
    # 기능 항목은 드롭다운 하나로 접는다. 펼쳐 두면 링크가 11개가 되어 한 줄을
    # 넘겼고, 「맥·아이패드」처럼 최상위에 있을 무게가 아닌 것도 섞여 있었다.
    ("기능", [
        ("{home}#dashboard", "홈"),
        ("{home}#analysis", "구성 리포트"),
        ("{home}#rebalance", "조정안"),
        ("{home}#capture", "캡처로 채우기"),
        ("{home}docs/portfolio-draft.html", "짜보기"),
        ("{home}#mac", "맥·아이패드"),
    ]),
    ("{home}#principles", "원칙"),
    ("{home}c/", "나눔터"),
    ("{home}v/", "영상"),
    ("{home}#download", "다운로드"),
    # 「버전 기록」은 푸터에만 둔다 — 헤더에 있을 만큼 자주 보는 문서가 아니다.
]


def render_nav_item(href, label, home):
    if isinstance(label, list):
        subs = "\n".join(
            f'      <a href="{h.format(home=home)}">{t}</a>' for h, t in label
        )
        return (
            f'    <div class="nav-group">\n'
            f'      <button class="nav-group-btn" type="button" aria-expanded="false">{href}</button>\n'
            f'      <div class="nav-sub">\n{subs}\n      </div>\n'
            f'    </div>'
        )
    return f'    <a href="{href.format(home=home)}">{label}</a>'


def render_nav(home, cta="다운로드", lang="ko", assets=None, pair=None):
    """`home` 은 그 언어 랜딩까지, `assets` 는 사이트 루트까지의 상대 경로다.

    영문판은 `/en/` 아래라 둘이 다르다 — 아이콘·이미지는 사이트 루트에 하나만 둔다.
    """
    assets = home if assets is None else assets
    strings = LANGS[lang]
    table = NAV_LINKS_EN if lang == "en" else NAV_LINKS
    links = "\n".join(render_nav_item(href, label, home) for href, label in table)
    return f"""<nav><div class="wrap nav-in">
  <!-- 앱 이름은 "골고루" 하나다. 로마자를 붙여 쓰면 텍스트로 읽을 때
       "골고루GOLGORU"가 되어, OAuth 동의 화면 이름과 자동 비교에서 어긋난다. -->
  <a class="brand" href="{home or './'}"><img src="{assets}images/app-icon.png" alt="" width="26" height="26">{strings["brand"]}</a>
  <div class="menu">
    <button class="menu-btn" type="button" aria-expanded="false">{"Menu" if lang == "en" else "메뉴"}</button>
  <div class="nav-links">
{links}
  </div>
  </div>
  <a class="cta" href="{home}#download" data-cta="1">{cta}</a>
  <a class="lang" href="{pair or other_home(lang, home, assets)}" hreflang="{"ko" if lang == "en" else "en"}"
     >{"한국어" if lang == "en" else "English"}</a>
</div></nav>"""


def other_home(lang, home, assets):
    """언어 전환 링크의 기본값 — 같은 깊이의 다른 언어 랜딩이다.

    짝이 있는 문서는 `build` 가 그 문서를 직접 넘긴다(`pair`). 짝이 없는 문서에서
    문서 주소를 만들어 보내면 404 라, 그때만 랜딩으로 보낸다."""
    return assets if lang == "en" else f"{assets}en/"


def doc_pair(slug, meta, lang):
    """같은 문서의 다른 언어판 주소. 영문판을 낸 문서에만 있다."""
    if "en" not in meta:
        return None
    return f"../../docs/{slug}.html" if lang == "en" else f"../en/docs/{slug}.html"


NAV = render_nav("../")

# 공유 자원 캐시 무효화.
#
# GitHub Pages 가 site.js·doc.css 를 max-age=14400(4시간)으로 준다. 헤더 구조를
# 바꾼 날 다시 온 사람은 새 HTML 에 4시간 묵은 CSS/JS 를 받아서, 드롭다운이
# 스타일 없이 통째로 펼쳐진 헤더를 본다. 내용 해시를 주소에 붙여 파일이 실제로
# 바뀐 날에만, 바뀐 파일만 새로 받게 한다.
SHARED_ASSETS = ["site.js", "docs/doc.css", "landing.css", "landing.js"]


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


def inject_shared(path, root, cta="다운로드", lang="ko", assets=None):
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
        head + begin + "\n" + render_nav(root, cta, lang, assets) + "\n" + close + tail,
        encoding="utf-8"
    )
    print(f"nav  {path}")


def footer(lang="ko"):
    if lang == "en":
        return """<footer><div class="wrap foot-in">
  <div>© 2026 Golgoru · spread it evenly.</div>
  <div><a href="../">Home</a> · <a href="getting-started.html">Getting started</a> · <a href="privacy.html">Privacy policy</a> · <a href="https://github.com/indus96/GOLGORU">GitHub</a></div>
  <div class="foot-sns"><a href="https://www.instagram.com/golgoru.app/" target="_blank" rel="noopener">Instagram</a> · <a href="https://www.youtube.com/@golgoru_app" target="_blank" rel="noopener">YouTube</a> · <a href="https://x.com/golgoru_app" target="_blank" rel="noopener">X</a></div>
</div></footer>"""
    return """<footer><div class="wrap foot-in">
  <div>© 2026 골고루 · 내 자산을 골고루.</div>
  <div><a href="../">홈</a> · <a href="getting-started.html">시작하기</a> · <a href="../v/">영상</a> · <a href="privacy.html">개인정보처리방침</a> · <a href="https://github.com/indus96/GOLGORU">GitHub</a></div>
  <div class="foot-sns"><a href="https://www.instagram.com/golgoru.app/" target="_blank" rel="noopener">인스타그램</a> · <a href="https://www.youtube.com/@golgoru_app" target="_blank" rel="noopener">유튜브</a> · <a href="https://x.com/golgoru_app" target="_blank" rel="noopener">X</a></div>
</div></footer>"""


FOOTER = footer("ko")


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


def more_docs(current, lang="ko"):
    """문서 사이를 오갈 수 있게 하단에 목록을 붙인다.

    상단 내비게이션은 랜딩 앵커로만 가서, 문서에 들어오면 다른 문서로
    넘어갈 방법이 없었다. 문서가 10개라 상단에 다 넣을 수는 없다.
    """
    items = []
    for slug, meta in DOCS.items():
        if lang == "en" and "en" not in meta:
            continue  # 영문판에 없는 문서는 목록에도 안 세운다 — 404 로 보낸다.
        label = meta["en"]["eyebrow"] if lang == "en" else meta["eyebrow"]
        if slug == current:
            items.append(f'<span class="doc-card current">{label}</span>')
        else:
            items.append(f'<a class="doc-card" href="{slug}.html">{label}</a>')
    return f"""<section class="more-docs"><div class="wrap narrow">
  <h2>{LANGS[lang]["more"]}</h2>
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


def build(slug, meta, lang="ko"):
    strings = LANGS[lang]
    if lang == "en" and "en" not in meta:
        return
    source = pathlib.Path(strings["src"]) / f"{slug}.md"
    if not source.exists():
        print(f"skip {source} (아직 안 옮김)")
        return
    md = source.read_text(encoding="utf-8")
    hero = meta["hero"]
    # 영문판 문서는 한 칸 더 깊다(`/en/docs/`) — 이미지 경로도 그만큼 올라간다.
    if lang == "en" and hero.startswith("../"):
        hero = "../" + hero
    title, lead, body = convert(md, hero)
    lead = lead or (meta["en"].get("lead", "") if lang == "en" else meta.get("lead", ""))
    lead_html = inline(lead) if lead else ""
    # meta description은 태그도 엔티티도 없는 평문이어야 한다. 검색결과에서
    # 잘리지 않게 155자로 자르고, 자를 때는 단어(어절) 경계에서 끊는다.
    lead_plain = html.unescape(re.sub(r"<[^>]+>", "", lead_html))
    lead_plain = unicodedata.normalize("NFC", " ".join(lead_plain.split()))
    if len(lead_plain) > 155:
        lead_plain = lead_plain[:155].rsplit(" ", 1)[0] + "…"
    # 색인은 주소 하나만 봐야 한다 — 여기서 정본 주소를 못 박는다.
    canonical = f"{SITE}/{strings['url']}/{slug}.html"
    # 두 언어가 서로를 가리킨다 — 색인이 같은 내용의 다른 언어판으로 알아본다.
    alternates = "\n".join(
        f'<link rel="alternate" hreflang="{code}" href="{SITE}/{LANGS[code]["url"]}/{slug}.html">'
        for code in ("ko", "en") if code == "ko" or "en" in meta
    ) + f'\n<link rel="alternate" hreflang="x-default" href="{SITE}/docs/{slug}.html">'
    eyebrow = meta["en"]["eyebrow"] if lang == "en" else meta["eyebrow"]
    page = f"""<!doctype html>
<html lang="{lang}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{strings["title_sep"]}{title}</title>
<meta property="og:site_name" content="{strings["brand"]}">
<meta name="application-name" content="{strings["brand"]}">
<meta name="description" content="{html.escape(lead_plain, quote=True)}">
<meta property="og:title" content="{strings["title_sep"]}{title}">
<meta property="og:description" content="{html.escape(lead_plain, quote=True)}">
<meta property="og:type" content="article">
<link rel="canonical" href="{canonical}">
<meta property="og:url" content="{canonical}">
{alternates}
<link rel="stylesheet" href="{strings['assets']}docs/doc.css">
</head><body>
{render_nav(strings["home"], cta=strings["cta"], lang=lang, assets=strings["assets"], pair=doc_pair(slug, meta, lang))}
<header class="doc-hero"><div class="wrap">
  <a class="back" href="../#{meta.get('back', 'top')}"
     onclick="return golgoruBack(event)">{strings["back"]}</a>
  <div class="eyebrow">{eyebrow}</div>
  <h1>{inline(title)}</h1>
  {f'<p class="lead">{lead_html}</p>' if lead_html else ''}
  {f'''<div class="hero-img {meta['cls']}"><img src="{hero}" alt="{inline(title)}{' 화면' if lang == 'ko' else ' screen'}"></div>''' if hero else ''}
</div></header>
<main class="doc-body"><div class="wrap narrow">
{body}
</div></main>
{more_docs(slug, lang)}
{footer(lang)}
{BACK_SCRIPT}
<script src="{strings["assets"]}site.js" defer></script>
</body></html>
"""
    out = pathlib.Path(strings["out"]) / f"{slug}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(open_external_in_new_tab(page), encoding="utf-8")
    print(f"built {out}  (title={title})")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    for slug, meta in DOCS.items():
        build(slug, meta)
        build(slug, meta, "en")


# ── 나눔터 조합 정적 페이지(/c/d/<id>.html) ─────────────────────────────────────
#
# 나눔터(/c/)는 JS 로 목록을 불러오는 한 장짜리라, 조합 하나하나가 검색에 따로 걸리지 않는다
# (주소가 `?id=` 이고 내용이 늦게 그려진다 — 네이버는 거의 못 읽는다). 조합마다 **내용이 HTML 에
# 들어 있는** 페이지를 만들어 둔다. 「올린 뒤 성과 · 지수 비교」는 매일 바뀌는 값이라 여기 굳히지 않고
# 살아 있는 나눔터로 넘긴다. 백테스트(지난 1년)는 싣지 않는다 — 고른 뒤 돌아본 값이라 부풀려진다
# (25건 평균 +151% · 올린 뒤 −1.3%, 2026-09-06). 지워진 · 숨겨진 조합은 다시 만들 때 파일도 지운다.
# `python3 build-docs.py --commons` 로 공개 API 를 읽어 다시 만든다(키 · 토큰 없음).
COMMONS_API = "https://asset-management-community.indus96-asset-management.workers.dev"
COMMONS_TOPICS = {"pension": "연금", "isa": "ISA", "monthly": "월배당", "us": "미국지수", "kr": "국내지수"}


def fetch_commons(limit=500):
    import json, urllib.request, urllib.parse
    drafts, cursor = [], None
    while len(drafts) < limit:
        url = f"{COMMONS_API}/drafts?sort=hot" + (f"&cursor={urllib.parse.quote(cursor)}" if cursor else "")
        req = urllib.request.Request(url, headers={"User-Agent": "golgoru-site-build"})
        page = json.load(urllib.request.urlopen(req, timeout=20))
        drafts += page.get("drafts", [])
        cursor = page.get("cursor")
        if not cursor or not page.get("drafts"):
            break
    return drafts


def commons_lines(draft):
    """`code` 끝 마디가 `종목:비중,…` 이다. 이름은 워커가 붙여 준 `names` 에서."""
    names = dict(pair.split("=", 1) for pair in (draft.get("names") or "").split("|") if "=" in pair)
    lines = []
    for item in draft["code"].rsplit(".", 1)[-1].split(","):
        symbol, _, weight = item.rpartition(":")  # 미국은 `NASDAQ:QQQ:40` — 비중은 끝 마디
        if symbol and weight:
            lines.append((symbol, names.get(symbol, symbol), float(weight)))
    return sorted(lines, key=lambda line: -line[2])


def commons_exposure(draft):
    """`한국:51,미국:43|주식:70,채권:30|정보기술:56,…` → [(국가, …), (자산, …), (업종, …)]."""
    labels = ["국가", "자산", "업종"]
    parts = (draft.get("exposure") or "").split("|")
    return [(labels[i], part.replace(",", " · ").replace(":", " ") + "%") for i, part in enumerate(parts[:3]) if part]


def esc(text):
    return html.escape(str(text), quote=True)


def commons_page(draft):
    lines = commons_lines(draft)
    topic = COMMONS_TOPICS.get(draft.get("topic") or "", "")
    market = "한국 상장" if draft.get("market") == "KR" else "미국 상장"
    name = draft["name"]
    top = " · ".join(f"{n} {w:g}%" for _, n, w in lines[:3])
    more = f" 외 {len(lines) - 3}종목" if len(lines) > 3 else ""
    desc = f"{topic + ' ' if topic else ''}{market} ETF {len(lines)}종목 조합 — {top}{more}. 골고루 사용자가 짜 본 조합으로, 종목과 비중만 공개됩니다."
    canonical = f"{SITE}/c/d/{draft['id']}.html"
    rows = "\n".join(
        f"<tr><td>{esc(n)}</td><td>{esc(s)}</td><td style=\"text-align:right\">{w:g}%</td></tr>" for s, n, w in lines)
    exposure = "".join(f"<li><strong>{k}</strong> {esc(v)}</li>" for k, v in commons_exposure(draft))
    live = f"../?id={draft['id']}"
    return f"""<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(name)} — ETF 구성 · 비중 | 골고루 나눔터</title>
<meta property="og:site_name" content="골고루">
<meta name="application-name" content="골고루">
<meta name="description" content="{esc(desc)}">
<meta property="og:title" content="{esc(name)} — ETF 구성 · 비중">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="article">
<link rel="canonical" href="{canonical}">
<meta property="og:url" content="{canonical}">
<link rel="stylesheet" href="../../docs/doc.css">
</head><body>
{render_nav("../../", assets="../../")}
<header class="doc-hero"><div class="wrap">
  <a class="back" href="./">← 나눔터 조합 모음</a>
  <div class="eyebrow">나눔터{' · ' + topic if topic else ''} · {market}</div>
  <h1>{esc(name)}</h1>
  <p class="lead">{esc(draft.get('nick') or '익명')} 님이 짜 본 ETF {len(lines)}종목 조합 · 추천 {draft.get('up', 0)} · 가져간 사람 {draft.get('taken', 0)}</p>
</div></header>
<main class="doc-body"><div class="wrap narrow">
<h2>구성</h2>
<div class="tablewrap"><table><thead><tr><th>종목</th><th>코드</th><th style="text-align:right">비중</th></tr></thead>
<tbody>
{rows}
</tbody></table></div>
{f'<h2>어디에 담겼나</h2><ul>{exposure}</ul>' if exposure else ''}
<h2>이 조합으로 해 볼 수 있는 것</h2>
<ul>
<li><a href="{live}">나눔터에서 보기</a> — 올린 뒤 성과, 지수와 비교, 추천 · 비추천.</li>
<li>골고루 앱에서 가져오면 투자금을 넣어 <strong>종목별 몇 주</strong>를 살지 계산하고, 내 계좌의 목표 비중으로 쓸 수 있습니다.</li>
</ul>
<p><a class="cta" href="../../#download">골고루 받기</a></p>
<p style="color:var(--hint);font-size:13px">사용자가 올린 조합이며 투자 권유가 아닙니다. 투자금 · 평가액은 올라가지 않고 종목과 비중만 공개됩니다.</p>
</div></main>
<footer><div class="wrap foot-in">
  <div>© 2026 골고루 · 고루 나눠 담기</div>
  <div><a href="../../">홈</a> · <a href="../">나눔터</a> · <a href="../../docs/portfolio-draft.html">짜보기 안내</a> · <a href="../../docs/privacy.html">개인정보처리방침</a></div>
</div></footer>
<script src="../../site.js" defer></script>
</body></html>
"""


def commons_index(drafts):
    groups = {}
    for draft in drafts:
        groups.setdefault(COMMONS_TOPICS.get(draft.get("topic") or "", "그 밖의 조합"), []).append(draft)
    order = list(COMMONS_TOPICS.values()) + ["그 밖의 조합"]
    sections = []
    for label in [o for o in order if o in groups]:
        items = "\n".join(
            f'<li><a href="{d["id"]}.html">{esc(d["name"])}</a> — '
            f'{esc(" · ".join(f"{n} {w:g}%" for _, n, w in commons_lines(d)[:3]))}</li>'
            for d in groups[label])
        sections.append(f"<h2>{label}</h2>\n<ul>\n{items}\n</ul>")
    canonical = f"{SITE}/c/d/"
    desc = "연금저축 · IRP · ISA · 월배당 · 미국지수 · 국내지수 — 골고루 사용자들이 짜 본 ETF 조합의 구성과 비중을 주제별로 모았습니다."
    return f"""<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>ETF 조합 모음 — 연금 · ISA · 배당 | 골고루 나눔터</title>
<meta property="og:site_name" content="골고루">
<meta name="description" content="{esc(desc)}">
<meta property="og:title" content="ETF 조합 모음 — 골고루 나눔터">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<link rel="canonical" href="{canonical}">
<meta property="og:url" content="{canonical}">
<link rel="stylesheet" href="../../docs/doc.css">
</head><body>
{render_nav("../../", assets="../../")}
<header class="doc-hero"><div class="wrap">
  <a class="back" href="../">← 나눔터</a>
  <div class="eyebrow">나눔터</div>
  <h1>ETF 조합 모음</h1>
  <p class="lead">{esc(desc)}</p>
</div></header>
<main class="doc-body"><div class="wrap narrow">
{chr(10).join(sections)}
<p style="color:var(--hint);font-size:13px">사용자가 올린 조합이며 투자 권유가 아닙니다.</p>
</div></main>
<footer><div class="wrap foot-in">
  <div>© 2026 골고루 · 고루 나눠 담기</div>
  <div><a href="../../">홈</a> · <a href="../">나눔터</a> · <a href="../../docs/privacy.html">개인정보처리방침</a></div>
</div></footer>
<script src="../../site.js" defer></script>
</body></html>
"""


def build_commons():
    out = pathlib.Path("c/d")
    out.mkdir(parents=True, exist_ok=True)
    drafts = [d for d in fetch_commons() if d.get("id") and d.get("code") and d.get("name")]
    keep = {f"{d['id']}.html" for d in drafts} | {"index.html"}
    for old in out.glob("*.html"):
        if old.name not in keep:
            old.unlink()
    for draft in drafts:
        (out / f"{draft['id']}.html").write_text(commons_page(draft), encoding="utf-8")
    (out / "index.html").write_text(commons_index(drafts), encoding="utf-8")
    print(f"built c/d/ — 조합 {len(drafts)}개")


if __name__ == "__main__" and "--commons" in __import__("sys").argv:
    build_commons()


def write_sitemap():
    """색인 대상 주소를 한 곳에 모아 준다.

    리디렉션·중복으로 떨어진 주소들이 계속 크롤링되는 것보다, 정본 목록을 주고
    거기만 보게 하는 편이 빠르다. 문서 목록에서 만들므로 문서가 늘어도 빠지지 않는다.
    """
    today = datetime.date.today().isoformat()
    # `/c/`(나눔터)와 `/v/`(영상)는 문서가 아니라 손으로 쓴 페이지라 DOCS 에 없다 —
    # 여기 직접 넣는다. 색인될 값이 있는 비문서 페이지는 이 둘뿐이다.
    # `/p/`(공유 코드 보기)는 넣지 않는다: 내용이 URL 조각(#) 뒤에만 있어 코드마다
    # 다른 페이지를 색인할 수 없고, 코드 없는 상태로는 안내문 몇 줄뿐이다(noindex).
    urls = (
        [f"{SITE}/", f"{SITE}/c/", f"{SITE}/v/"]
        + [f"{SITE}/docs/{name}.html" for name in sorted(DOCS)]
        # 나눔터 조합 페이지(`--commons` 로 만든 것) — 있는 파일만.
        + ([f"{SITE}/c/d/"] if pathlib.Path("c/d/index.html").exists() else [])
        + [f"{SITE}/c/d/{p.name}" for p in sorted(pathlib.Path("c/d").glob("*.html")) if p.name != "index.html"]
        # 영문판 — 낸 문서만 넣는다. 안 낸 것을 적으면 색인이 404 를 물고 온다.
        + [f"{SITE}/en/"]
        + [f"{SITE}/en/docs/{name}.html"
           for name in sorted(DOCS) if "en" in DOCS[name]]
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
# 영문판 랜딩. `/en/` 아래라 사이트 루트까지 한 칸 더 올라간다(이미지·스크립트).
inject_shared("en/index.html", "", cta="Get the app", lang="en", assets="../")
inject_shared("p/index.html", "../")
inject_shared("c/index.html", "../", cta="앱 받기")
inject_shared("v/index.html", "../", cta="앱 받기")

for page in ["index.html", "en/index.html", "p/index.html", "c/index.html", "v/index.html"] \
    + glob.glob("docs/*.html") + glob.glob("en/docs/*.html"):
    if not os.path.exists(page):
        continue
    stamp_assets(page)
print("asset stamp  " + ", ".join(SHARED_ASSETS))
