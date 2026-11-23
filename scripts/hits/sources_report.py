#!/usr/bin/env python3
"""방문 카운터(wrangler d1 --json 출력)를 대시보드용 두 표로 바꾼다.

  npx wrangler d1 execute golgoru-hits --remote --json --config scripts/hits/wrangler.toml \
    --command "SELECT path, ref, SUM(n) AS n FROM hits WHERE day >= date('now','+9 hours','-6 days') GROUP BY path, ref" \
    | python3 scripts/hits/sources_report.py <출력 폴더>

→ <출력 폴더>/sources.json  [{source, views, blog_views}]   들어온 곳별(사이트 안 이동은 뺌)
  <출력 폴더>/blog.json     [{post, views, search, sns, direct, inside, installs}]  블로그 글별
  installs = 그 글에서 설치 버튼(앱스토어 · 플레이 · 테스트 참여)을 누른 수 — site.js 가 「/_store/<종류>-<앱>/<페이지>」로 센다.
  <출력 폴더>/installs.json [{app, apple, play, test, total}]  앱별 설치 버튼 누름(홈페이지 전체)
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


# 앱 — 앱스토어 id · 플레이 패키지 끝 · 테스트 안내 #조각, 없으면(11/20 첫 버전) 페이지 경로로 짐작.
APPS = {"골고루": ("6797157864", "golgoru"), "뭐타지": ("6828151139", "mwotaji"),
        "복지비 청구": ("6803049427", "medicalclaim", "medical-claim"), "메트로놈": ("6823171086", "metronome")}


def app_of(key, page):
    for name, keys in APPS.items():
        if key in keys:
            return name
    m = re.match(r"/apps/([\w-]+)/", page)
    return next((n for n, k in APPS.items() if m and m.group(1) in k), "골고루" if not m else "기타")


def is_post(path):
    return "/blog/" in path and not path.endswith("/blog/") and not path.endswith("/index.html")


def build(rows):
    src = defaultdict(lambda: [0, 0])
    posts = defaultdict(lambda: defaultdict(int))
    installs = defaultdict(lambda: defaultdict(int))
    for r in rows:
        g, n, p = group(r["ref"]), int(r["n"]), r["path"]
        if p.startswith("/_store/"):  # 방문이 아니라 설치 버튼 누름
            _, _, tag, rest = p.split("/", 3)
            kind, _, key = tag.partition("-")
            page = "/" + rest
            # 테스터 그룹 가입 버튼은 앱이 따로 없다 — 「테스터 그룹」 줄의 테스트 참여 칸으로 센다.
            a = installs["테스터 그룹" if kind == "group" else app_of(key, page)]
            kind = "test" if kind == "group" else kind
            a[kind] += n
            a["total"] += n
            if is_post(page):
                posts[page]["installs"] += n
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
    label = lambda p: re.sub(r"^/apps/([\w-]+)/blog/", lambda m: app_of(m.group(1), m.group(0)) + " › ", p).replace("/blog/", "").replace(".html", "")
    blog = [{"post": label(p),
             **{k: d.get(k, 0) for k in ("views", "search", "sns", "direct", "inside", "installs")}}
            for p, d in sorted(posts.items(), key=lambda kv: -kv[1]["views"])]
    inst = [{"app": k, **{f: d.get(f, 0) for f in ("apple", "play", "test", "total")}}
            for k, d in sorted(installs.items(), key=lambda kv: -kv[1]["total"])]
    return sources, blog, inst


if __name__ == "__main__":
    if len(sys.argv) == 1:  # 자체 확인
        s, b, i = build([{"path": "/blog/a.html", "ref": "t.co", "n": 2}, {"path": "/blog/a.html", "ref": "(사이트 안)", "n": 1},
                      {"path": "/", "ref": "www.google.com", "n": 3}, {"path": "/blog/", "ref": "m.facebook.com", "n": 1},
                      {"path": "/_store/play/blog/a.html", "ref": "(직접)", "n": 1},
                      {"path": "/_store/apple-6823171086/apps/", "ref": "(직접)", "n": 2},
                      {"path": "/_store/test-medical-claim/apps/medical-claim/blog/x.html", "ref": "(직접)", "n": 1},
                      {"path": "/apps/medical-claim/blog/x.html", "ref": "(직접)", "n": 1},
                      {"path": "/_store/group/apps/android-test.html", "ref": "(직접)", "n": 3}])
        assert s[0] == {"source": "구글 검색", "views": 3, "blog_views": 0}, s
        assert {"source": "X", "views": 2, "blog_views": 2} in s and all(x["source"] != "사이트 안" for x in s)
        assert b[0] == {"post": "a", "views": 3, "search": 0, "sns": 2, "direct": 0, "inside": 1, "installs": 1}, b
        assert s[0]["views"] == 3  # 버튼 누름은 방문에 안 섞인다
        assert i[0] == {"app": "테스터 그룹", "apple": 0, "play": 0, "test": 3, "total": 3}, i
        assert {"app": "메트로놈", "apple": 2, "play": 0, "test": 0, "total": 2} in i, i
        assert {"app": "골고루", "apple": 0, "play": 1, "test": 0, "total": 1} in i and any(x["app"] == "복지비 청구" for x in i), i
        assert any(x["post"] == "복지비 청구 › x" and x["installs"] == 1 for x in b), b
        print("ok")
        sys.exit()
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    rows = json.load(sys.stdin)[0]["results"]
    s, b, i = build(rows)
    (out / "sources.json").write_text(json.dumps(s, ensure_ascii=False))
    (out / "blog.json").write_text(json.dumps(b, ensure_ascii=False))
    (out / "installs.json").write_text(json.dumps(i, ensure_ascii=False))
    print(json.dumps({"sources": s, "blog": b, "installs": i}, ensure_ascii=False, indent=1))
