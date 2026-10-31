#!/usr/bin/env python3
"""App Store 에 새 버전이 나오면 새소식(docs/changelog.md)의 「애플은 심사 중」을 「출시」로 바꾼다.

App Store 공개 조회(itunes lookup — 키 · 토큰 없음)가 돌려주는 버전이 새소식 줄의 버전과 같고, 그 줄이 아직
「(Android · 애플은 심사 중)」이면 「(애플 · Android)」로 고친다. 바꾼 게 있으면 0 이 아닌 값으로 끝내지 않고
바뀐 파일만 남긴다 — 커밋은 워크플로가 한다(.github/workflows/mark-released.yml).
조회는 iPhone 판을 본다. 맥은 같은 날 함께 심사에 넣으므로 따로 보지 않는다.

앱 소개(apps/index.html · en/apps/index.html)도 같이 본다 — 아직 안 나온 앱은 `data-appstore="앱 ID"` 를 단
「준비 중」 자리로 두고, 그 ID 가 App Store 에 뜨면 App Store 버튼으로 바꾸고 `data-appstore-tag` 알약을 지운다.
Play 도 같다 — `data-play="패키지"` 자리는 Play 공개 페이지가 열리면(비공개 테스트에서는 404) Google Play 버튼이 된다.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import urllib.error
import urllib.request

APP_ID = "6797157864"  # 골고루(공개판). 앱 식별자일 뿐 비밀이 아니다.
ROOT = pathlib.Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "docs" / "changelog.md"
APP_PAGES = {ROOT / "apps" / "index.html": "https://apps.apple.com/kr/app/id{id}",
             ROOT / "en" / "apps" / "index.html": "https://apps.apple.com/app/id{id}"}
SOON = re.compile(r'<span class="soon" data-appstore="(\d+)">[^<]*</span>')
TAG = r'<span class="tag" data-appstore-tag="{id}">[^<]*</span>'
PLAY_SOON = re.compile(r'<span class="soon" data-play="([\w.]+)">[^<]*</span>')


def is_live(app_id: str) -> bool:
    with urllib.request.urlopen(f"https://itunes.apple.com/lookup?id={app_id}&country=kr", timeout=20) as response:
        return bool(json.load(response).get("results"))


def is_on_play(package: str) -> bool:
    request = urllib.request.Request(f"https://play.google.com/store/apps/details?id={package}&hl=ko&gl=KR",
                                     headers={"user-agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status == 200
    except urllib.error.HTTPError:
        return False


def release_play(text: str, on_play) -> str:
    """「Google Play 준비 중」 자리 중 프로덕션에 나간 앱을 버튼으로 바꾼다."""
    for package in set(PLAY_SOON.findall(text)):
        if not on_play(package):
            continue
        button = (f'<a href="https://play.google.com/store/apps/details?id={package}" '
                  f'target="_blank" rel="noopener">Google Play</a>')
        text = re.sub(r'<span class="soon" data-play="' + re.escape(package) + r'">[^<]*</span>', button, text)
    return text


def release_apps(text: str, link: str, live) -> str:
    """「준비 중」 자리 중 App Store 에 뜬 앱을 버튼으로 바꾼다. [live] 는 ID → 공개됐는지."""
    for app_id in set(SOON.findall(text)):
        if not live(app_id):
            continue
        button = f'<a href="{link.format(id=app_id)}" target="_blank" rel="noopener">App Store</a>'
        text = re.sub(r'<span class="soon" data-appstore="' + app_id + r'">[^<]*</span>', button, text)
        text = re.sub(TAG.format(id=app_id), "", text)
    return text


def store_version() -> str | None:
    url = f"https://itunes.apple.com/lookup?id={APP_ID}&country=kr"
    with urllib.request.urlopen(url, timeout=20) as response:
        results = json.load(response).get("results") or []
    return results[0].get("version") if results else None


def mark(text: str, version: str) -> str:
    # 「**3.2.0** — 2026년 10월 4일(Android · 애플은 심사 중)」 → 「…(애플 · Android)」
    pattern = re.compile(r"(\*\*" + re.escape(version) + r"\*\* — [^(\n]*)\(Android · 애플은 심사 중\)")
    return pattern.sub(r"\1(애플 · Android)", text)


def main() -> int:
    for page, link in APP_PAGES.items():
        if not page.exists():
            continue
        html = page.read_text()
        try:
            updated = release_play(release_apps(html, link, is_live), is_on_play)
        except Exception as error:  # 조회 실패는 다음 시각에 다시
            print(f"앱 소개 조회 실패 — {error}")
            continue
        if updated != html:
            page.write_text(updated)
            print(f"앱 소개 — App Store 버튼으로 바꿈 ({page.relative_to(ROOT)})")
    version = store_version()
    if not version:
        print("App Store 조회 실패 — 다음에 다시")
        return 0
    text = CHANGELOG.read_text()
    updated = mark(text, version)
    if updated == text:
        print(f"App Store {version} — 바꿀 줄 없음")
        return 0
    CHANGELOG.write_text(updated)
    print(f"App Store {version} 출시 — 새소식 고침")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sample = "**3.2.0** — 2026년 10월 4일(Android · 애플은 심사 중)\n**3.1.1** — 2026년 10월 3일(애플 · Android)\n"
        assert mark(sample, "3.2.0").startswith("**3.2.0** — 2026년 10월 4일(애플 · Android)")
        assert mark(sample, "3.1.1") == sample
        page = '<h2>뭐타지<span class="tag" data-appstore-tag="123">출시 준비 중</span></h2>' \
               '<span class="soon" data-appstore="123">곧</span>'
        assert release_apps(page, "https://x/id{id}", lambda _: False) == page
        done = release_apps(page, "https://x/id{id}", lambda _: True)
        assert 'href="https://x/id123"' in done and "data-appstore" not in done, done
        play = '<a href="a">App Store</a><span class="soon" data-play="com.x.y">준비 중</span>'
        assert release_play(play, lambda _: False) == play
        assert 'details?id=com.x.y' in release_play(play, lambda _: True) and "data-play" not in release_play(play, lambda _: True)
        print("ok")
        raise SystemExit(0)
    raise SystemExit(main())
