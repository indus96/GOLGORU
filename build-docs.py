#!/usr/bin/env python3
"""docs/*.md → docs/*.html (랜딩과 같은 톤의 정적 문서 페이지).
마크다운은 소스로 두고, 문서를 고치면 `python3 build-docs.py`로 재생성한다."""
import re, html, glob, os

# `back`은 랜딩에서 이 문서로 들어오는 섹션이다. 돌아갈 때 그 자리로 보낸다.
# (JS가 되면 history.back()으로 정확한 스크롤 위치를 복원하고, 이건 그 대비책이다.)
DOCS = {
    "dashboard":            dict(eyebrow="대시보드",   hero="../images/app/phone-dashboard.png", cls="phone", back="dashboard"),
    "portfolio-analysis":   dict(eyebrow="자산 분석",  hero="../images/app/phone-analysis.png",  cls="phone", back="analysis"),
    "asset-ranking":        dict(eyebrow="자산순위",   hero="../images/app/stock-analysis.png",     cls="phone", back="analysis"),
    "allocation-rebalancing":dict(eyebrow="자산배분",  hero="../images/app/phone-allocation.png", cls="phone", back="rebalance"),
    "news-reports":         dict(eyebrow="뉴스·리포트", hero="../images/app/phone-news.png",     cls="phone", back="rebalance"),
    "ai-review":            dict(eyebrow="AI 점검",    hero="../images/app/phone-ai.png",        cls="phone", back="rebalance"),
    "broker-connection":    dict(eyebrow="증권사 연결", hero="../images/app/phone-broker.png",    cls="phone", back="about"),
    "data-security":        dict(eyebrow="데이터·보안", hero="../images/data-flow.svg",           cls="wide", back="about",
                                 lead="자산 데이터는 기기 안이나 내 시트에만 있고, 자격증명은 기기 Keychain에만 둡니다."),
    "getting-started":      dict(eyebrow="시작하기",   hero="../images/data-flow.svg",           cls="wide", back="download",
                                 lead="둘러보기 · 앱에 직접 입력 · Google Sheets 연동 — 세 가지 중에서 고릅니다."),
    "privacy":              dict(eyebrow="개인정보",   hero="", cls="wide", back="about",
                                 lead="앱은 자산 데이터를 제공자 서버에 저장하지 않습니다."),
    "changelog":            dict(eyebrow="버전 기록",  hero="", cls="wide", back="download",
                                 lead="어떤 기능이 어느 버전에 들어갔는지 적어 둡니다."),
}

NAV = """<nav><div class="wrap nav-in">
  <!-- 앱 이름은 "골고루" 하나다. 로마자를 붙여 쓰면 텍스트로 읽을 때
       "골고루GOLGORU"가 되어, OAuth 동의 화면 이름과 자동 비교에서 어긋난다. -->
  <a class="brand" href="../index.html">골고루</a>
  <!-- 랜딩과 같은 항목을 같은 순서로 둔다 — 문서로 들어오면 헤더가 달라져
       다른 사이트처럼 보였다. -->
  <div class="menu">
    <button class="menu-btn" type="button" aria-expanded="false">메뉴</button>
  <div class="nav-links">
    <a href="../index.html#about">앱 소개</a>
    <a href="../index.html#principles">원칙</a>
    <a href="../index.html#dashboard">대시보드</a>
    <a href="../index.html#analysis">자산 분석</a>
    <a href="../index.html#rebalance">자산배분</a>
    <a href="../index.html#capture">계좌 채우기</a>
    <a href="../index.html#mac">맥·아이패드</a>
    <a href="../index.html#download">다운로드</a>
    <a href="changelog.html">버전 기록</a>
  </div>
  </div>
  <a class="cta" href="../index.html#download" data-cta="1">다운로드</a>
</div></nav>"""

FOOTER = """<footer><div class="wrap foot-in">
  <div>© 2026 골고루 · 내 자산을 골고루.</div>
  <div><a href="../index.html">홈</a> · <a href="getting-started.html">시작하기</a> · <a href="privacy.html">개인정보처리방침</a> · <a href="https://github.com/indus96/GOLGORU">GitHub</a></div>
</div></footer>"""


# 랜딩에서 들어왔다면 뒤로 가기로 돌려보낸다 — 브라우저가 보던 스크롤 위치를
# 그대로 복원하므로 섹션 앵커보다 정확하다. 직접 들어온 경우(검색·북마크·다른
# 문서에서 온 경우)에는 링크의 앵커가 그대로 쓰인다.
CTA_SCRIPT = """<script>
// 헤더 버튼은 접속한 기기에 맞춰 바뀐다.
//
// 기본 상태는 "다운로드 → #download" 다. 스크립트가 없거나 기기를 못 가려도
// 모든 플랫폼이 보이는 자리로 가므로 항상 맞는 답이 된다.
// 받을 수 있는 기기에서만 스토어 링크로 올린다 — 아직 안 나온 플랫폼(맥·안드로이드)에서
// 스토어로 보내면 "찾을 수 없음"을 만나게 된다.
(function () {
  var ua = navigator.userAgent;
  // 아이패드는 데스크톱 모드에서 UA 가 Macintosh 로 나온다. 터치 지점 수로 가른다 —
  // 이걸 빼면 아이패드 사용자가 맥으로 잡혀 스토어 대신 다운로드 자리로 간다.
  var touch = navigator.maxTouchPoints > 1;
  var isIOS = /iPhone|iPod|iPad/.test(ua) || (/Macintosh/.test(ua) && touch);

  var APPLE = 'https://apps.apple.com/kr/app/id6797157864';
  // 맥 심사가 끝나면 아래에 { test: /Macintosh/ && !touch, url: APPLE } 를 더한다.
  var target = isIOS ? APPLE : null;
  if (!target) return;

  document.querySelectorAll('[data-cta]').forEach(function (cta) {
    cta.href = target;
    cta.textContent = '앱 받기';
    cta.setAttribute('data-store', 'apple');
    cta.setAttribute('rel', 'noopener');
  });
})();
</script>"""

STORE_SCRIPT = """<script>
// 스토어 링크를 기기에서는 스토어 **앱**으로 바로 연다.
// https 주소도 애플 기기에서는 대개 앱으로 열리지만, 인앱 브라우저에서는 웹으로 빠진다.
// 반대로 itms-apps://·market:// 를 처음부터 박으면 데스크톱에서 아무 반응이 없다.
// 그래서 기기를 확인한 뒤에만 바꿔친다.
(function () {
  var ua = navigator.userAgent;
  var rules = [
    { os: 'apple', test: /iPhone|iPad|iPod|Macintosh/, from: /^https:\/\//, to: 'itms-apps://' },
    { os: 'android', test: /Android/, from: /^https:\/\/play\.google\.com\/store\/apps\/details\?id=/, to: 'market://details?id=' }
  ];
  document.querySelectorAll('[data-store]').forEach(function (link) {
    var rule = rules.filter(function (r) { return r.os === link.dataset.store; })[0];
    if (!rule || !rule.test.test(ua)) return;
    link.href = link.href.replace(rule.from, rule.to);
    // 스킴 링크는 새 탭에서 열면 빈 탭이 남는다.
    link.removeAttribute('target');
  });
})();
</script>"""

MENU_SCRIPT = """<script>
// 모바일 헤더 메뉴. 좁은 화면에서는 링크를 접어 두고 버튼으로 편다.
document.querySelectorAll('.menu').forEach(function (menu) {
  var button = menu.querySelector('.menu-btn');
  if (!button) return;
  button.addEventListener('click', function () {
    var open = menu.classList.toggle('open');
    button.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  // 링크를 고르면 닫는다 — 같은 페이지 앵커로 이동할 때 메뉴가 덮고 있으면 안 된다.
  menu.querySelectorAll('.nav-links a').forEach(function (link) {
    link.addEventListener('click', function () {
      menu.classList.remove('open');
      button.setAttribute('aria-expanded', 'false');
    });
  });
});
</script>"""

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
  <a class="back" href="../index.html#{meta.get('back', 'top')}"
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
{MENU_SCRIPT}
{CTA_SCRIPT}
{STORE_SCRIPT}
</body></html>
"""
    open(f"docs/{slug}.html", "w", encoding="utf-8").write(open_external_in_new_tab(page))
    print(f"built docs/{slug}.html  (title={title})")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    for slug, meta in DOCS.items():
        build(slug, meta)
