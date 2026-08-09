# 안드로이드 공개 시 반영 순서

Play 스토어에 앱이 **공개된 뒤에** 이 브랜치를 반영한다. 공개 전에 올리면
받을 수 없는 링크가 랜딩에 걸린다.

## 1. Play 스토어 URL 채우기

`index.html` 두 곳의 `PLAY_STORE_URL` 을 실제 주소로 바꾼다.

```
https://play.google.com/store/apps/details?id=com.indus96.golgoru
```

```bash
cd ~/Claude/golgoru && sed -i '' 's|PLAY_STORE_URL|https://play.google.com/store/apps/details?id=com.indus96.golgoru|g' index.html && grep -c "play.google.com/store" index.html
```

## 2. 확인

`open index.html` 로 열어 히어로 버튼 두 개, 다운로드 카드 세 개(iPhone·Mac·Android),
현재 상태 목록을 눈으로 본다.

## 3. 반영

```bash
cd ~/Claude/golgoru && git checkout master && git merge android-release-ready && git push origin master
```

## 이 브랜치가 바꾸는 것

- 히어로: "Google Play에서 받기" 버튼 추가, 안내문을 `iPhone · iPad · Android 지원 · 무료 · 맥은 준비 중`으로
- 다운로드: Android 카드를 비활성("준비 중입니다") → 활성 링크로
- 현재 상태: `Android Google Play 공개` 추가, 예정 목록에서 `Android 버전` 제거
- 제목·메타 설명의 플랫폼 표기

## 아직 안 건드린 것

- `images/` 의 기기 목업은 아이폰 기준 그대로다. 안드로이드 스크린샷으로 교체할지는
  공개 후에 판단한다(`asset-management/android/store/screenshots/` 에 8장 있다).
- 문서(`docs/`)의 플랫폼 표기는 이미 안드로이드까지 반영돼 있다(2026-08-09).
