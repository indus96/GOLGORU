#!/usr/bin/env python3
"""방문 카운터(wrangler d1 --json 출력)를 대시보드용 두 표로 바꾼다.

  npx wrangler d1 execute golgoru-hits --remote --json --config scripts/hits/wrangler.toml \
    --command "SELECT path, ref, SUM(n) AS n FROM hits WHERE day >= date('now','+9 hours','-6 days') GROUP BY path, ref" \
    | python3 scripts/hits/sources_report.py <출력 폴더>

→ <출력 폴더>/sources.json  [{source, views, blog_views}]   들어온 곳별(사이트 안 이동은 뺌)
  <출력 폴더>/blog.json     [{post, views, search, sns, direct, inside, installs}]  블로그 글별
  installs = 그 글에서 설치 버튼(앱스토어 · 플레이 · 테스트 참여)을 누른 수 — site.js 가 「/_store/<종류>/<글>」로 센다.
"""
import json, re, sys
from collections import defaultdict
from pathlib import Path

# ponytail: 호스트 이름으로만 나눈다. X · 인스타 앱 안 브라우저는 출처를 안 남기는 일이 많아 「직접」에 섞인다.
GROUPS = [
    (r"(^|\.)google\.", "구글 검색"),
    (r"naver\.com$", "네이버"),
    (r"bing\.com$|daum\.net$|duckduckgo", "기타 검색"),
    (r"^(t\.co|x\.com|twitter\.com)$", "X"),
    (r"instagram\.com$|facebook\.com$", "인스타 · 페이스북"),
    (r"youtube\.com$|youtu\.be$", "유튜브"),
    (r"threads\.net$", "스레드"),
]
SEARCH = {"구글 검색", "네이버", "기타 검색"}
SNS = {"X", "인스타 · 페이스북", "유튜브", "스레드"}


def group(ref):
    if ref in ("(직접)", "(사이트 안)"):
        return {"(직접)": "직접 · 앱 안 브라우저", "(사이트 안)": "사이트 안"}[ref]
    for pat, name in GROUPS:
        if re.search(pat, ref):
            return name
    return "기타 사이트"


def is_post(path):
    return "/blog/" in path and not path.endswith("/blog/") and not path.endswith("/index.html")


def build(rows):
    src = defaultdict(lambda: [0, 0])
    posts = defaultdict(lambda: defaultdict(int))
    for r in rows:
        g, n, p = group(r["ref"]), int(r["n"]), r["path"]
        if p.startswith("/_store/"):  # 방문이 아니라 설치 버튼 누름
            post = "/" + p.split("/", 3)[3]
            if is_post(post):
                posts[post]["installs"] += n
            continue
        if g != "사이트 안":
            src[g][0] += n
            if "/blog/" in p:
                src[g][1] += n
        if is_post(p):
            kind = "search" if g in SEARCH else "sns" if g in SNS else "inside" if g == "사이트 안" else "direct"
            posts[p][kind] += n
            posts[p]["views"] += n
    posts = {p: d for p, d in posts.items() if d["views"] or d["installs"]}
    sources = [{"source": k, "views": v[0], "blog_views": v[1]} for k, v in sorted(src.items(), key=lambda kv: -kv[1][0])]
    blog = [{"post": p.replace("/apps/mwotaji/blog/", "뭐타지 › ").replace("/blog/", "").replace(".html", ""),
             **{k: d.get(k, 0) for k in ("views", "search", "sns", "direct", "inside", "installs")}}
            for p, d in sorted(posts.items(), key=lambda kv: -kv[1]["views"])]
    return sources, blog


if __name__ == "__main__":
    if len(sys.argv) == 1:  # 자체 확인
        s, b = build([{"path": "/blog/a.html", "ref": "t.co", "n": 2}, {"path": "/blog/a.html", "ref": "(사이트 안)", "n": 1},
                      {"path": "/", "ref": "www.google.com", "n": 3}, {"path": "/blog/", "ref": "m.facebook.com", "n": 1},
                      {"path": "/_store/play/blog/a.html", "ref": "(직접)", "n": 1}])
        assert s[0] == {"source": "구글 검색", "views": 3, "blog_views": 0}, s
        assert {"source": "X", "views": 2, "blog_views": 2} in s and all(x["source"] != "사이트 안" for x in s)
        assert b == [{"post": "a", "views": 3, "search": 0, "sns": 2, "direct": 0, "inside": 1, "installs": 1}], b
        assert s[0]["views"] == 3  # 버튼 누름은 방문에 안 섞인다
        print("ok")
        sys.exit()
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    rows = json.load(sys.stdin)[0]["results"]
    s, b = build(rows)
    (out / "sources.json").write_text(json.dumps(s, ensure_ascii=False))
    (out / "blog.json").write_text(json.dumps(b, ensure_ascii=False))
    print(json.dumps({"sources": s, "blog": b}, ensure_ascii=False, indent=1))
