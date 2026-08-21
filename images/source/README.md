# 앱 아이콘 원본

`ㄱ ㅗ ㄹ` 세 자모를 같은 간격으로 세운 마크(2026-08-22 확정). 「골」을 셋으로
나눠 고르게 놓은 것 — 브랜드 뜻 그대로다.

| 파일 | 쓰는 곳 |
| --- | --- |
| `app-icon-square.svg` | iOS·맥 앱 아이콘, Play 스토어 아이콘. **모서리를 안 깎는다** — OS 가 자기 마스크로 깎는다 |
| `app-icon-rounded.svg` | 공홈에 그림으로 보여줄 때 (`images/app-icon.png`) |
| `app-icon-round.svg` | 안드로이드 `ic_launcher_round` — 원형 런처 |

## 다시 뽑기

```bash
rsvg-convert -w 1024 -h 1024 app-icon-square.svg -o icon-1024.png
```

**iOS 아이콘에는 알파 채널이 있으면 안 된다** — 위 SVG 는 배경 사각형이 캔버스를
꽉 채워서 알파가 안 남는다(`sips -g hasAlpha` 로 확인한다).

## 건드리면 안 되는 것

`images/app-icon-512.png` 는 **Google OAuth 동의 화면에 올라간 로고**다. 그 화면을
바꾸면 브랜드 재검증에 다시 들어가고 수 주 걸린다(승인 메일 명시). 앱·스토어
아이콘만 새것으로 가고 이 파일은 그대로 둔다.
