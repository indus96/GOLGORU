#!/usr/bin/env python3
"""blog/queue/ 의 맨 앞 글 하나를 오늘 날짜(한국 시각)로 blog/ 에 내놓는다.

대기 글은 `blog/queue/01-주소.md` 처럼 번호로 순서를 정한다. 내놓을 때 번호는 떼고 날짜를 붙인다.
대기 글이 없으면 아무것도 하지 않는다 — 그날은 건너뛴다.
"""
import datetime
import pathlib
import re
import sys

queue = sorted(pathlib.Path("blog/queue").glob("*.md"))
if not queue:
    print("대기 글 없음")
    sys.exit(0)

source = queue[0]
slug = re.sub(r"^\d+-", "", source.stem)
today = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).date().isoformat()
target = pathlib.Path("blog") / f"{today}-{slug}.md"
if any(pathlib.Path("blog").glob(f"*-{slug}.md")):
    sys.exit(f"이미 같은 주소의 글이 있다: {slug}")
source.rename(target)
print(f"게시 {target} · 대기 {len(queue) - 1}편 남음")
