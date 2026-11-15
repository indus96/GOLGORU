#!/usr/bin/env python3
"""<블로그 폴더>/queue/ 의 맨 앞 글 하나를 오늘 날짜(한국 시각)로 그 블로그에 내놓는다.

    python3 scripts/publish-next-post.py --scheduled            # 예약: 게시 요일 · 시각이 된 블로그만, 하루 한 편
    python3 scripts/publish-next-post.py apps/mwotaji/blog      # 손으로: 그 블로그에 지금 바로 한 편

예약 실행은 몇 번 불려도 안전하다 — 게시 요일이 아니거나, 06:45 전이거나, 오늘 이미 한 편 냈으면
아무것도 하지 않는다. GitHub 예약 실행이 몇 시간씩 늦거나 빠지는 일이 잦아서(2026-11-16 첫 게시가
빠졌다) 바깥(클라우드플레어 크론)과 GitHub 예약 양쪽에서 부르고, 먼저 온 쪽이 낸다.

대기 글은 `queue/01-주소.md` 처럼 번호로 순서를 정한다. 내놓을 때 번호는 떼고 날짜를 붙인다.
대기 글이 없으면 아무것도 하지 않는다 — 그날은 건너뛴다.
"""
import datetime
import pathlib
import re
import sys

# 블로그별 게시 요일(월=0). 바꾸면 여기 한 곳만.
SCHEDULE = {"blog": {0, 2, 4}, "apps/mwotaji/blog": {3}}
EARLIEST = datetime.time(6, 45)


def now_kst():
    return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)


def publish(folder, now):
    blog = pathlib.Path(folder)
    today = now.date().isoformat()
    queue = sorted((blog / "queue").glob("*.md"))
    if not queue:
        print(f"{folder}: 대기 글 없음")
        return False
    source = queue[0]
    slug = re.sub(r"^\d+-", "", source.stem)
    if any(blog.glob(f"*-{slug}.md")):
        sys.exit(f"{folder}: 이미 같은 주소의 글이 있다: {slug}")
    target = blog / f"{today}-{slug}.md"
    source.rename(target)
    print(f"{folder}: 게시 {target.name} · 대기 {len(queue) - 1}편 남음")
    return True


def main(argv):
    now = now_kst()
    if argv and argv[0] == "--scheduled":
        for folder, days in SCHEDULE.items():
            if now.weekday() not in days or now.time() < EARLIEST:
                print(f"{folder}: 오늘은 게시 시각이 아님")
                continue
            if any(pathlib.Path(folder).glob(f"{now.date().isoformat()}-*.md")):
                print(f"{folder}: 오늘 이미 게시함")
                continue
            publish(folder, now)
        return
    publish(argv[0] if argv else "blog", now)


if __name__ == "__main__":
    main(sys.argv[1:])
