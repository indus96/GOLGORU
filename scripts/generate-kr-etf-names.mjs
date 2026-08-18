#!/usr/bin/env node
// 국내 ETF 심볼→이름 표를 만든다. p/index.html(구성안 공유 페이지)이 이 표를
// 정적으로 실어 쓴다 — 공유 코드에는 종목 이름이 없어(코드 길이를 줄이려는
// 설계) 심볼만 보이는데, 이름을 보이게 하려고 심볼을 서버에 물어보면
// "코드는 브라우저 밖으로 안 보낸다"던 그 페이지의 약속이 깨진다. 그래서
// 표를 페이지와 함께 정적으로 실어 브라우저 안에서만 해결한다.
//
// 원천은 asset-management 저장소의 market-indicators-worker.mjs가 ETF 후보
// 검색에 쓰는 것과 같다(fetchKoreanETFList) — 네이버 모바일 API가 국내 ETF
// 전량(약 1163종목)을 페이지네이션으로 준다. 워커를 거치지 않고 같은 원천을
// 직접 불러 쓴다 — 이 스크립트는 사람이 손으로 실행하는 빌드 도구라 워커
// 인증 토큰이 필요 없다.
//
// 실행:
//   node scripts/generate-kr-etf-names.mjs
//
// 갱신 주기: 정해진 자동 스케줄은 없다 — ETF 상장·상장폐지·개명이 있을 때
// 사람이 수동으로 다시 돌린다(연 몇 회 수준). 이름이 안 바뀌는 표라 급하게
// 갱신할 이유가 거의 없고, 표에 없는 신규 상장 심볼은 페이지가 코드 그대로
// 보여주도록 이미 설계되어 있어(아래 p/index.html 쪽 처리) 당장 깨지지 않는다.

import { writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const PAGE_SIZE = 100;
const MAX_PAGES = 20; // 1163 / 100 ≈ 12페이지. 20은 안전 여유이자 무한 루프 방지선.
const OUT_PATH = fileURLToPath(new URL("../p/kr-etf-names.json", import.meta.url));

function clean(value) {
  return typeof value === "string" ? value.trim() : "";
}

async function fetchPage(page) {
  const url = `https://m.stock.naver.com/api/stocks/etf?page=${page}&pageSize=${PAGE_SIZE}`;
  const response = await fetch(url, {
    headers: { accept: "application/json", "user-agent": "Mozilla/5.0" },
  });
  if (!response.ok) {
    throw new Error(`네이버 ETF 목록 페이지 ${page} 요청 실패: HTTP ${response.status}`);
  }
  return response.json();
}

async function fetchAllRows() {
  const rows = [];
  for (let page = 1; page <= MAX_PAGES; page += 1) {
    const body = await fetchPage(page);
    const stocks = Array.isArray(body?.stocks) ? body.stocks : [];
    rows.push(...stocks);
    const total = Number.isFinite(body?.totalCount) ? body.totalCount : null;
    if (!stocks.length || (total !== null && rows.length >= total)) break;
  }
  return rows;
}

async function main() {
  const rows = await fetchAllRows();
  const table = {};
  for (const row of rows) {
    const symbol = clean(row?.itemCode);
    const name = clean(row?.stockName);
    if (!symbol || !name) continue;
    table[symbol] = name;
  }

  const count = Object.keys(table).length;
  if (count < 500) {
    // 원천이 잘못 응답했을 때(빈 페이지 하나만 받고 끝나는 등) 표를 반토막
    // 낸 채로 덮어쓰지 않는다 — 갱신 실패를 갱신 성공처럼 커밋하는 게 더 나쁘다.
    throw new Error(`받은 종목 수가 너무 적다(${count}개) — 원천 응답을 확인해라.`);
  }

  const json = JSON.stringify(table, Object.keys(table).sort(), 0);
  // 위 stable-order 트릭(JSON.stringify replacer로 키 배열을 주면 그 순서로
  // 찍힌다)으로 diff 를 줄인다 — 매번 다시 받아도 새로 생긴/없어진 심볼만
  // git diff 에 걸리게 한다.
  await writeFile(OUT_PATH, json + "\n", "utf8");
  console.log(`${OUT_PATH} 에 ${count}개 종목을 썼다.`);
}

main().catch((error) => {
  console.error(error.message || error);
  process.exit(1);
});
