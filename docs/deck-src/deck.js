(function () {
  var slides = Array.prototype.slice.call(document.querySelectorAll('.slide'));
  var deck = document.getElementById('deck');
  var stage = document.getElementById('stage');
  var ctr = document.getElementById('ctr');
  var bar = document.getElementById('progbar');
  var panel = document.getElementById('npanel');
  var ntext = document.getElementById('ntext');
  var ntoggle = document.getElementById('ntoggle');
  var narrow = window.matchMedia('(max-width: 820px)');
  var cur = 0;

  function store(k, v) {
    try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; }
  }

  function fit() {
    if (narrow.matches) { deck.style.transform = ''; return; }
    var s = Math.min(stage.clientWidth / 1280, stage.clientHeight / 720);
    deck.style.transform = 'translate(-50%, -50%) scale(' + s + ')';
  }

  function show(n) {
    cur = Math.max(0, Math.min(slides.length - 1, n));
    slides.forEach(function (s, k) { s.classList.toggle('active', k === cur); });
    ctr.textContent = (cur + 1) + ' / ' + slides.length;
    bar.style.width = ((cur + 1) / slides.length * 100) + '%';
    var nb = slides[cur].querySelector('.nb');
    ntext.innerHTML = nb ? nb.innerHTML : '';
    try { history.replaceState(null, '', '#' + slides[cur].id); } catch (e) {}
  }

  function setNotes(on) {
    panel.hidden = !on;
    ntoggle.setAttribute('aria-pressed', on ? 'true' : 'false');
    store('tc4xx-notes', on ? '1' : '0');
    fit();
  }

  document.getElementById('prev').addEventListener('click', function () { show(cur - 1); });
  document.getElementById('next').addEventListener('click', function () { show(cur + 1); });
  ntoggle.addEventListener('click', function () { setNotes(panel.hidden); });

  document.addEventListener('keydown', function (e) {
    if (narrow.matches || e.altKey || e.ctrlKey || e.metaKey) return;
    var t = e.target && e.target.tagName;
    if (t === 'INPUT' && (e.key === ' ' || e.key === 'Enter')) return;
    if (['ArrowRight', 'PageDown', ' '].indexOf(e.key) > -1) { e.preventDefault(); show(cur + 1); }
    else if (['ArrowLeft', 'PageUp'].indexOf(e.key) > -1) { e.preventDefault(); show(cur - 1); }
    else if (e.key === 'Home') { e.preventDefault(); show(0); }
    else if (e.key === 'End') { e.preventDefault(); show(slides.length - 1); }
    else if (e.key === 'n' || e.key === 'N') { setNotes(panel.hidden); }
  });

  // checklist: per-viewer ticks
  var boxes = Array.prototype.slice.call(document.querySelectorAll('.checklist input[type=checkbox]'));
  var count = document.getElementById('chk-count');
  var saved = {};
  try { saved = JSON.parse(store('tc4xx-checks') || '{}') || {}; } catch (e) { saved = {}; }
  function tally() {
    var n = boxes.filter(function (b) { return b.checked; }).length;
    count.textContent = n + ' of ' + boxes.length + ' done';
  }
  boxes.forEach(function (b) {
    b.checked = !!saved[b.id];
    b.addEventListener('change', function () {
      saved[b.id] = b.checked;
      store('tc4xx-checks', JSON.stringify(saved));
      tally();
    });
  });
  tally();

  var start = 0;
  var m = /^#(s\d+)$/.exec(location.hash || '');
  if (m) { slides.forEach(function (s, k) { if (s.id === m[1]) start = k; }); }
  show(start);
  if (store('tc4xx-notes') === '1') setNotes(true);
  fit();
  if (window.ResizeObserver) new ResizeObserver(fit).observe(stage);
  window.addEventListener('resize', fit);
  if (narrow.addEventListener) narrow.addEventListener('change', fit);
})();
