// 랜딩과 문서 페이지가 함께 쓰는 스크립트.
//
// 예전에는 index.html 과 build-docs.py 에 같은 코드를 복사해 뒀다. 한쪽만 고치는 일이
// 실제로 일어났고(맥 CTA 분기가 문서 페이지에만 빠졌다), 고친 사람은 알아채지 못했다.
// 파일 하나로 두면 그 실수가 불가능해진다.

// 모바일 헤더 메뉴. 좁은 화면에서는 링크를 접어 두고 버튼으로 편다.
document.querySelectorAll('.menu').forEach(function (menu) {
  var button = menu.querySelector('.menu-btn');
  if (!button) return;
  button.addEventListener('click', function () {
    var open = menu.classList.toggle('open');
    button.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  // 링크를 고르면 닫는다 — 같은 페이지 앵커로 이동할 때 메뉴가 덮고 있으면 안 된다.
  menu.querySelectorAll('.nav-links a').forEach(function (link) {
    link.addEventListener('click', function () {
      menu.classList.remove('open');
      button.setAttribute('aria-expanded', 'false');
    });
  });
});

// 헤더 드롭다운(「기능」). 넓은 화면에서는 :hover 로도 열리지만, 그것만 두면
// 키보드와 터치에서 못 연다. 좁은 화면에서는 접힌 메뉴 안에 이미 펼쳐져 있으므로
// 버튼이 아무 일도 하지 않는 게 맞다 — CSS 가 그 상태를 만든다.
document.querySelectorAll('.nav-group').forEach(function (group) {
  var button = group.querySelector('.nav-group-btn');
  if (!button) return;
  function close() {
    group.classList.remove('open');
    button.setAttribute('aria-expanded', 'false');
  }
  button.addEventListener('click', function (event) {
    event.stopPropagation();
    var open = group.classList.toggle('open');
    button.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  group.querySelectorAll('.nav-sub a').forEach(function (link) {
    link.addEventListener('click', close);
  });
  document.addEventListener('click', function (event) {
    if (!group.contains(event.target)) close();
  });
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') close();
  });
});

// 헤더 버튼은 접속한 기기에 맞춰 바뀐다.
//
// 기본 상태는 "다운로드 → #download" 다. 스크립트가 없거나 기기를 못 가려도
// 모든 플랫폼이 보이는 자리로 가므로 항상 맞는 답이 된다.
// 받을 수 있는 기기에서만 스토어 링크로 올린다 — 아직 안 나온 플랫폼(맥·안드로이드)에서
// 스토어로 보내면 "찾을 수 없음"을 만나게 된다.
(function () {
  var ua = navigator.userAgent;
  // 아이패드는 데스크톱 모드에서 UA 가 Macintosh 로 나온다. 터치 지점 수로 가른다 —
  // 이걸 빼면 아이패드 사용자가 맥으로 잡혀 스토어 대신 다운로드 자리로 간다.
  var touch = navigator.maxTouchPoints > 1;
  var isIOS = /iPhone|iPod|iPad/.test(ua) || (/Macintosh/.test(ua) && touch);

  var APPLE = 'https://apps.apple.com/kr/app/id6797157864';
  // 맥도 같은 앱 레코드다(Catalyst) — 주소가 같아서 스토어 앱이 알아서 맥 버전을 연다.
  var isMac = /Macintosh/.test(ua) && !touch;
  var target = (isIOS || isMac) ? APPLE : null;
  if (!target) return;

  document.querySelectorAll('[data-cta]').forEach(function (cta) {
    cta.href = target;
    cta.textContent = '앱 받기';
    cta.setAttribute('data-store', 'apple');
    cta.setAttribute('rel', 'noopener');
  });
})();

// 스토어 링크를 기기에서는 스토어 **앱**으로 바로 연다.
// https 주소도 애플 기기에서는 대개 앱으로 열리지만, 인앱 브라우저에서는 웹으로 빠진다.
// 반대로 itms-apps://·market:// 를 처음부터 박으면 데스크톱에서 아무 반응이 없다.
// 그래서 기기를 확인한 뒤에만 바꿔친다.
(function () {
  var ua = navigator.userAgent;
  var rules = [
    { os: 'apple', test: /iPhone|iPad|iPod|Macintosh/, from: /^https:\/\//, to: 'itms-apps://' },
    { os: 'android', test: /Android/, from: /^https:\/\/play\.google\.com\/store\/apps\/details\?id=/, to: 'market://details?id=' }
  ];
  document.querySelectorAll('[data-store]').forEach(function (link) {
    var rule = rules.filter(function (r) { return r.os === link.dataset.store; })[0];
    if (!rule || !rule.test.test(ua)) return;
    link.href = link.href.replace(rule.from, rule.to);
    // 스킴 링크는 새 탭에서 열면 빈 탭이 남는다.
    link.removeAttribute('target');
  });
})();
