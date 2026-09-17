// 랜딩의 갤러리(가로 스와이프 + 점 + 화살표). 한국어와 영문판이 같은 파일을 쓴다.
// 화살표의 읽어 주는 이름만 문서 언어를 따라간다 — 나머지는 글자가 없다.

// 갤러리: 프레임 수만큼 점을 만들고, 스크롤 위치에 따라 현재 점을 칠한다.
// 스크롤 스냅이 스와이프를 담당한다. 다만 마우스에는 가로로 끌 수단이 없어
// 화살표와 점 클릭으로도 넘길 수 있게 한다.
document.querySelectorAll('[data-gallery]').forEach(function (gallery) {
  var frames = gallery.querySelector('.frames');
  var dots = gallery.querySelector('.dots');
  var images = frames.querySelectorAll('img');
  if (images.length < 2) { dots.remove(); return; }

  function go(index) {
    frames.scrollTo({ left: frames.clientWidth * index, behavior: 'smooth' });
  }

  images.forEach(function (_, index) {
    var dot = document.createElement('i');
    if (index === 0) dot.className = 'on';
    dot.addEventListener('click', function () { go(index); });
    dots.appendChild(dot);
  });

  var hint = document.createElement('div');
  hint.className = 'hint';
  hint.textContent = images.length + '개 화면 — 옆으로 밀거나 화살표를 누르세요';
  gallery.appendChild(hint);

  var prev = document.createElement('button');
  prev.className = 'arrow prev';
  prev.type = 'button';
  prev.setAttribute('aria-label', (document.documentElement.lang === 'en' ? 'Previous screen' : '이전 화면'));
  prev.textContent = '‹';
  var next = document.createElement('button');
  next.className = 'arrow next';
  next.type = 'button';
  next.setAttribute('aria-label', (document.documentElement.lang === 'en' ? 'Next screen' : '다음 화면'));
  next.textContent = '›';
  gallery.appendChild(prev);
  gallery.appendChild(next);

  function current() {
    return Math.round(frames.scrollLeft / frames.clientWidth);
  }
  prev.addEventListener('click', function () { go(current() - 1); });
  next.addEventListener('click', function () { go(current() + 1); });

  function sync() {
    var index = current();
    dots.querySelectorAll('i').forEach(function (dot, i) {
      dot.classList.toggle('on', i === index);
    });
    prev.disabled = index <= 0;
    next.disabled = index >= images.length - 1;
  }
  frames.addEventListener('scroll', sync, { passive: true });
  sync();
});
