#!/usr/bin/env python3
"""블로그별 게시 · 대기 글 수와 대기 글이 끝나는 날 — 주간 지표 대시보드의 「블로그 운영」 표.

    python3 scripts/blog_status.py <출력 폴더> [<hits.json>]   # hits.json 은 sources_report.py 와 같은 wrangler 출력(글 방문 수용)
"""
import collections, datetime, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from importlib import import_module
SCHEDULE = import_module("publish-next-post").SCHEDULE  # 게시 요일은 한 곳에서만 정한다
NAMES = {"blog": "골고루", "apps/mwotaji/blog": "뭐타지", "apps/medical-claim/blog": "복지비 청구", "apps/metronome/blog": "메트로놈"}


def status(today, views):
    out = []
    for folder, days in SCHEDULE.items():
        q = len(list((ROOT / folder / "queue").glob("*.md")))
        t, left, last = today, q, None
        while left:
            t += datetime.timedelta(days=1)
            if t.weekday() in days:
                left, last = left - 1, t
        out.append({"blog": NAMES.get(folder, folder), "days": "·".join("월화수목금토일"[i] for i in sorted(days)),
                    "published": len(list((ROOT / folder).glob("20*.md"))), "queued": q,
                    "queue_until": last.isoformat() if last else "", "post_views_7d": views[folder]})
    return out


if __name__ == "__main__":
    views = collections.Counter()
    if len(sys.argv) > 2:
        for r in json.load(open(sys.argv[2]))[0]["results"]:
            p = r["path"]
            if p.endswith(".html") and not p.startswith("/_store/"):
                for folder in SCHEDULE:
                    if p.startswith(f"/{folder}/"):
                        views[folder] += int(r["n"])
    today = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).date()
    rows = status(today, views)
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    (out / "blogs.json").write_text(json.dumps(rows, ensure_ascii=False))
    print(json.dumps(rows, ensure_ascii=False, indent=1))
