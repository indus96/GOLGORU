// golgoru.app 방문 수 — 날짜 · 페이지 · 들어온 곳(도메인)별 숫자만 센다(2026-11-16).
// 쿠키 · IP · 기기 정보는 저장하지 않는다. User-Agent 는 봇을 거르는 데만 보고 버린다.
// ponytail: 요청 제한 없음 — 방문이 적은 사이트라. 부풀리기가 보이면 RATE_LIMITER 를 붙인다.
const ORIGIN = "https://golgoru.app";
const BOT = /bot|crawl|spider|slurp|preview|headless|lighthouse|monitor/i;
const cors = { "Access-Control-Allow-Origin": ORIGIN, "Access-Control-Allow-Methods": "POST", "Access-Control-Allow-Headers": "Content-Type" };

export default {
  async fetch(req, env) {
    if (req.method === "OPTIONS") return new Response(null, { headers: cors });
    if (req.method !== "POST" || new URL(req.url).pathname !== "/hit") return new Response("not found", { status: 404 });
    if (BOT.test(req.headers.get("User-Agent") || "")) return new Response(null, { status: 204, headers: cors });
    let body;
    try { body = JSON.parse(await req.text()); } catch { return new Response("bad", { status: 400, headers: cors }); }
    const path = String(body.p || "").split(/[?#]/)[0];
    if (!/^\/[\w\-./%]{0,180}$/.test(path)) return new Response("bad", { status: 400, headers: cors });
    let ref = "";
    try { ref = body.r ? new URL(body.r).hostname.replace(/^www\./, "").slice(0, 80) : ""; } catch {}
    if (ref === "golgoru.app") ref = "(사이트 안)";
    const day = new Date(Date.now() + 9 * 3600e3).toISOString().slice(0, 10); // 한국 날짜
    await env.DB.prepare(
      "INSERT INTO hits (day, path, ref, n) VALUES (?1, ?2, ?3, 1) ON CONFLICT(day, path, ref) DO UPDATE SET n = n + 1"
    ).bind(day, path, ref || "(직접)").run();
    return new Response(null, { status: 204, headers: cors });
  },
};
