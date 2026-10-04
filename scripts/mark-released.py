#!/usr/bin/env python3
"""App Store 에 새 버전이 나오면 새소식(docs/changelog.md)의 「애플은 심사 중」을 「출시」로 바꾼다.

App Store 공개 조회(itunes lookup — 키 · 토큰 없음)가 돌려주는 버전이 새소식 줄의 버전과 같고, 그 줄이 아직
「(Android · 애플은 심사 중)」이면 「(애플 · Android)」로 고친다. 바꾼 게 있으면 0 이 아닌 값으로 끝내지 않고
바뀐 파일만 남긴다 — 커밋은 워크플로가 한다(.github/workflows/mark-released.yml).
조회는 iPhone 판을 본다. 맥은 같은 날 함께 심사에 넣으므로 따로 보지 않는다.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import urllib.request

APP_ID = "6797157864"  # 골고루(공개판). 앱 식별자일 뿐 비밀이 아니다.
CHANGELOG = pathlib.Path(__file__).resolve().parents[1] / "docs" / "changelog.md"


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
        print("ok")
        raise SystemExit(0)
    raise SystemExit(main())
