# 3트랙 전환 문구 수정 대상

작업용 메모. P0 Task 10에서 삭제한다.

공개 앱은 **조회 전용**이고, 원장은 **둘러보기 / 앱 직접 입력 / 시트 연동** 세 갈래다.
따라서 아래 두 전제가 깨졌다.

1. "내 Google Sheets를 원장으로" — 시트는 이제 세 갈래 중 하나다.
2. "증권사 리밸런싱 주문까지" — 공개 앱에 주문 기능이 없다.

## README.md

| 위치 | 현재 | 조치 |
| --- | --- | --- |
| L5-6 | "내 Google Sheets를 원장으로, 자산 현황부터 증권사 리밸런싱 주문까지." | 3트랙 + 조회 중심으로 교체 |
| L11-12 | "증권사 API로 리밸런싱 주문까지 실행합니다" / "승인된 주문만" | 삭제 |
| L19 | 원칙 "시트가 원장" | "데이터는 사용자 것"으로 |
| L21 | 원칙 "승인 기반 주문" | "읽기 전용 연동"으로 |
| L30 | 표 "자산배분 · 리밸런싱 … 3단계 리밸런싱 실행" | "자산배분"으로, 실행 문구 삭제 |
| L33 | 표 "증권사 연결 … 계좌 동기화" | 잔고 조회 중심으로 |
| L39 | "Google 계정과 정규화된 App_Data_* 시트 (생성 스크립트 제공)" | 3트랙 준비물로 |
| L40 | "한국투자증권(모의·실전) … 키 저장과 연결 확인" | 잔고 조회로 |
| L44-45 | "모의투자로 … 실전 계좌 전환을 준비하는 단계" | "App Store 공개 준비"로 |
| L49 | "✅ 모의투자 리밸런싱" | 삭제 |
| L51 | "🔜 실전 계좌 주문 전환, 업비트 실주문, 일반 공개" | "🔜 App Store 공개"로 |
| 표 맨 위 | — | "시작하기" 행 추가 |

## index.html

| 위치 | 현재 | 조치 |
| --- | --- | --- |
| L9 | og:description "…리밸런싱 주문까지" | 교체 |
| L132-133 | 히어로 lead "…승인된 주문만 대신 넣습니다" | 3트랙으로 교체 |
| L140 | CTA "저장소 보기(GitHub)" | App Store 배지로 |
| L151 | "주문은 승인한 것만" | 교체 |
| L153 | 원칙 카드 "시트가 원장" | "데이터는 사용자 것" |
| L157-158 | 원칙 카드 "승인 기반 주문" | "읽기 전용 연동" |
| L206-215 | `#rebalance` 절 — `phone-rebalance.png`(주문 실행 화면), "선택→계획→실행 3단계", "실시간 체결통보" | **스크린샷 교체 필요**(`phone-allocation.png`), 절 제목 "자산배분"으로, 실행 관련 항목 삭제 |
| L238 | "한투·토스·업비트·바이낸스 키 저장 + 연결 확인" | 잔고 조회 중심 |
| L264 | "모의투자 검증을 마치고, 실전 전환을 준비합니다" | "App Store 공개 준비"로 |
| L268 | "모의투자 리밸런싱(분할·예약·휴장일·실시간 체결)" | 삭제 |
| L270-271 | "실전 계좌 주문 전환" / "업비트 실주문 · 일반 공개" | "App Store 공개"로 |
| nav | — | "다운로드" 링크 추가 |
| head | — | OG 태그 보강(og:image·twitter:card) |

## docs/*.md

| 파일 | 조치 |
| --- | --- |
| `data-security.md` | L5·L10·L14 — Apps Script 언급 삭제, 로컬 원장 저장 설명 추가, 스코프를 `spreadsheets.readonly`로 |
| `allocation-rebalancing.md` | L3·L12-30·L43·L47 — 주문 실행 3단계·예약·휴장일·기록 전부 삭제. 제목을 "자산배분"으로 |
| `broker-connection.md` | L23-32·L49-52 — 주문 열 삭제, 잔고 조회 중심으로. "주문을 넣지 않습니다" 명시 |
| `portfolio-analysis.md` | L69 — "실제 종목·수량 주문은 …에서 이어집니다" 삭제 |
| `ai-review.md` | L48 — 이미 면책 문구 있음. 앱의 `InvestmentDisclaimer`와 톤 맞추기 |
| `dashboard.md`, `asset-ranking.md`, `news-reports.md` | 모의투자 계좌 제외 설명은 유지(사실). 지원 방식 배지만 추가 |
| 전 파일 | 상단에 "지원 방식" 배지 추가 |

## build-docs.py

- `DOCS` 딕셔너리가 하드코딩 — `privacy`, `getting-started` 항목 추가 필요
- `data-security`의 `lead`가 "앱은 내 Google Sheets를 원장으로 읽고…" — 교체 필요

## 신규 파일

- `docs/privacy.md` — OAuth 검증 필수
- `docs/getting-started.md` — 3트랙 온보딩
- `docs/oauth-verification-notes.md` — 제출 기록
- `images/og-cover.png` — 사용자 제공
- `images/app/ipad-ranking.png`, `ipad-allocation.png`, `phone-allocation.png` — 사용자 제공
