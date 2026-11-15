// 블로그 예약 게시 방아쇠 — 매일 한국 06:45 · 07:15 에 GitHub 의 blog-publish 워크플로를 부른다.
// 게시할지(요일 · 하루 한 편)는 워크플로 안의 스크립트가 정하므로 매일 불러도 된다.
// GitHub 자체 예약은 이 저장소에서 몇 시간씩 늦어서 시각을 맞추려고 둔다(2026-11-16).
//
// 시크릿 GITHUB_TOKEN: 이 저장소(indus96/GOLGORU)만, 권한 Actions: Read and write 인 fine-grained 토큰.
export default {
  async scheduled(_event, env) {
    const res = await fetch(
      "https://api.github.com/repos/indus96/GOLGORU/actions/workflows/blog-publish.yml/dispatches",
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${env.GITHUB_TOKEN}`,
          Accept: "application/vnd.github+json",
          "User-Agent": "golgoru-blog-cron",
        },
        body: JSON.stringify({ ref: "master" }),
      },
    );
    if (res.status !== 204) throw new Error(`dispatch ${res.status}: ${await res.text()}`);
  },
};
