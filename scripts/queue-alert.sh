#!/usr/bin/env bash
# 블로그 대기 글이 3편 이하로 줄면 이슈를 하나 연다(GitHub 가 저장소 주인에게 메일 · 앱 알림을 보낸다).
# 이미 열린 알림 이슈가 있으면 새로 만들지 않고, 다시 넉넉해지면(4편 이상) 닫는다.
# blog-publish 워크플로가 실행될 때마다 부른다 — 컴퓨터와 무관하게 GitHub 에서 돈다.
set -euo pipefail
THRESHOLD=3
LABEL="blog-queue"
golgoru=$(ls blog/queue/*.md 2>/dev/null | wc -l | tr -d ' ')
mwotaji=$(ls apps/mwotaji/blog/queue/*.md 2>/dev/null | wc -l | tr -d ' ')
echo "대기 글 — 골고루 ${golgoru}편 · 뭐타지 ${mwotaji}편"

gh label create "$LABEL" --color C9A227 --description "블로그 대기 글 보충 알림" --force >/dev/null
open=$(gh issue list --label "$LABEL" --state open --json number --jq '.[0].number // empty')

low=""
[ "$golgoru" -le "$THRESHOLD" ] && low="${low}골고루(${golgoru}편) "
[ "$mwotaji" -le "$THRESHOLD" ] && low="${low}뭐타지(${mwotaji}편) "

if [ -n "$low" ]; then
  if [ -z "$open" ]; then
    gh issue create --label "$LABEL" \
      --title "블로그 대기 글 보충 필요 — ${low% }" \
      --body "@indus96 블로그 대기 글이 ${THRESHOLD}편 이하로 줄었습니다.

| 블로그 | 남은 대기 글 | 게시 요일 |
|---|---|---|
| 골고루 (\`blog/queue/\`) | ${golgoru}편 | 월 · 수 · 금 |
| 뭐타지 (\`apps/mwotaji/blog/queue/\`) | ${mwotaji}편 | 목 |

Claude 에게 「다음 글 묶음 준비해」라고 하면 됩니다. 넉넉해지면(4편 이상) 이 이슈는 저절로 닫힙니다."
  else
    echo "알림 이슈 #$open 이 이미 열려 있음"
  fi
elif [ -n "$open" ]; then
  gh issue close "$open" --comment "대기 글 보충됨 — 골고루 ${golgoru}편 · 뭐타지 ${mwotaji}편"
fi
