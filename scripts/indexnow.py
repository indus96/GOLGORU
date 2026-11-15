#!/usr/bin/env python3
"""방금 커밋에서 새로 생긴 블로그 글 주소를 IndexNow 로 알린다(빙 · 네이버 등 참여 검색엔진이 나눠 받는다).

구글은 IndexNow 를 받지 않는다 — 구글은 사이트맵(lastmod)을 다시 읽어 찾아온다.
키 파일(루트의 <키>.txt)은 공개가 원칙이다 — 이 사이트가 주인임을 보이는 표식일 뿐 비밀이 아니다.
"""
import json
import pathlib
import subprocess
import sys
import urllib.request

SITE = "https://golgoru.app"
KEY = "36e19700b3c07f5b7b5d6880a554bdb6"
ENDPOINTS = ["https://api.indexnow.org/indexnow", "https://searchadvisor.naver.com/indexnow"]

added = subprocess.run(["git", "diff", "--name-only", "--diff-filter=A", "HEAD~1", "HEAD"],
                       capture_output=True, text=True, check=True).stdout.split()
urls = [f"{SITE}/{p}" for p in added if p.endswith(".html") and "/blog/" in f"/{p}"]
if not urls:
    print("알릴 새 글 없음")
    sys.exit(0)
urls += sorted({u.rsplit("/", 1)[0] + "/" for u in urls})  # 그 블로그 목록 페이지도
body = json.dumps({"host": "golgoru.app", "key": KEY, "keyLocation": f"{SITE}/{KEY}.txt",
                   "urlList": urls}).encode()
for endpoint in ENDPOINTS:
    req = urllib.request.Request(endpoint, data=body, headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            print(endpoint, res.status, len(urls), "개")
    except Exception as e:  # 알림이 실패해도 게시는 이미 끝났다 — 실패로 만들지 않는다.
        print(endpoint, "실패:", e)
