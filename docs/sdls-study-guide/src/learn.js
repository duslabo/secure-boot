(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  function h(tag, attrs, html) {
    var e = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) { if (k === 'cls') e.className = attrs[k]; else e.setAttribute(k, attrs[k]); });
    if (html != null) e.innerHTML = html;
    return e;
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  // ---------------------------------------------------------------- progress store
  var KEY = 'sdls-study-v1';
  var state = { ans: {} };
  try { var raw = localStorage.getItem(KEY); if (raw) state = JSON.parse(raw) || state; if (!state.ans) state.ans = {}; } catch (e) {}
  function save() { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} }

  var BANK = JSON.parse($('#qbank').textContent);
  var ALL = [];
  Object.keys(BANK).forEach(function (m) { BANK[m].forEach(function (q) { q.mod = m; ALL.push(q); }); });

  function updateProgress() {
    ['s', 'f'].forEach(function (t) {
      var qs = ALL.filter(function (q) { return q.t === t; });
      var good = qs.filter(function (q) { return state.ans[q.id] && state.ans[q.id].first; }).length;
      var pct = Math.round(good / qs.length * 100);
      $('#ms-' + t).textContent = pct + '%';
      $('#mb-' + t).style.width = pct + '%';
    });
    $$('.toc a').forEach(function (a) {
      var qs = BANK[a.dataset.mod] || [];
      var ok = qs.filter(function (q) { return state.ans[q.id] && state.ans[q.id].ok; }).length;
      var any = qs.filter(function (q) { return state.ans[q.id]; }).length;
      a.classList.toggle('done', qs.length > 0 && ok === qs.length);
      a.classList.toggle('part', any > 0 && ok < qs.length);
    });
    var ex = BANK.exam || [];
    var first = ex.filter(function (q) { return state.ans[q.id] && state.ans[q.id].first; }).length;
    var answered = ex.filter(function (q) { return state.ans[q.id]; }).length;
    var sc = $('#exam-score');
    if (sc) sc.textContent = answered ? (first + ' of ' + ex.length + ' correct on the first try' +
      (answered === ex.length ? (first >= 10 ? '. Passed.' : '. Review the modules behind the misses and try the checks again.') : '')) : '';
  }

  // ---------------------------------------------------------------- quizzes
  function renderQuestion(q, n) {
    var wrap = h('div', { cls: 'qi', id: 'q-' + q.id });
    var tag = q.t === 's' ? '<span class="tag s qt">Security</span>' : '<span class="tag f qt">Functional</span>';
    wrap.appendChild(h('p', { cls: 'qp' }, '<span>' + n + '. ' + esc(q.q) + '</span>' + tag));
    var opts = h('div', { cls: 'qo' });
    var fb = h('div', { 'aria-live': 'polite' });
    q.o.forEach(function (o, i) {
      var b = h('button', { type: 'button' }, esc(o));
      b.addEventListener('click', function () { answer(q, i, opts, fb); });
      opts.appendChild(b);
    });
    wrap.appendChild(opts); wrap.appendChild(fb);
    var st = state.ans[q.id];
    if (st && st.ok) showResult(q, q.a, opts, fb, false);
    return wrap;
  }
  function answer(q, i, opts, fb) {
    var right = i === q.a;
    if (!state.ans[q.id]) state.ans[q.id] = { first: right, ok: false };
    if (right) state.ans[q.id].ok = true;
    save(); updateProgress();
    showResult(q, i, opts, fb, true);
  }
  function showResult(q, i, opts, fb) {
    var right = i === q.a;
    var bs = $$('button', opts);
    bs.forEach(function (b, k) { b.disabled = true; b.classList.remove('right', 'wrong'); if (k === i) b.classList.add(right ? 'right' : 'wrong'); if (right && k === q.a) b.classList.add('right'); });
    fb.innerHTML = '';
    var e = h('p', { cls: 'qe' + (right ? '' : ' no') }, (right ? '<b>Correct.</b> ' + esc(q.e) : '<b>Not quite.</b> Think again about what the standard requires, then retry.') +
      '<span class="ref">§ ' + esc(q.r) + '</span>');
    fb.appendChild(e);
    if (!right) {
      var r = h('button', { type: 'button', cls: 'btn small retry' }, 'Try again');
      r.addEventListener('click', function () { bs.forEach(function (b) { b.disabled = false; b.classList.remove('wrong'); }); fb.innerHTML = ''; bs[0].focus(); });
      fb.appendChild(r);
    }
  }
  $$('.quiz').forEach(function (qz) {
    var qs = BANK[qz.dataset.quiz] || [];
    var box = $('.qs', qz);
    qs.forEach(function (q, k) { box.appendChild(renderQuestion(q, k + 1)); });
  });
  $('#reset-all').addEventListener('click', function () {
    state = { ans: {} }; save();
    $$('.quiz').forEach(function (qz) { var box = $('.qs', qz); box.innerHTML = ''; (BANK[qz.dataset.quiz] || []).forEach(function (q, k) { box.appendChild(renderQuestion(q, k + 1)); }); });
    updateProgress();
  });

  // current-section marker in the rail
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) $$('.toc a').forEach(function (a) { a.classList.toggle('cur', a.getAttribute('href') === '#' + e.target.id); });
      });
    }, { rootMargin: '-40% 0px -55% 0px' });
    $$('.mod').forEach(function (s) { io.observe(s); });
  }

  // ---------------------------------------------------------------- frame bars
  function frame(el, segs) {
    el.innerHTML = '';
    segs.forEach(function (s) {
      var w = Math.max(5, Math.min(s.o, 40));
      if (s.data) w = 48;
      var d = h('div', { cls: 'fseg ' + (s.c || ''), style: 'flex:' + w + ' 1 0' }, '<b>' + esc(s.n) + '</b><i>' + esc(s.t || (s.o + ' oct')) + '</i>');
      d.title = s.n;
      el.appendChild(d);
    });
  }
  (function () {
    var on = $('#f1-on'), bar = $('#f1-bar'), note = $('#f1-note');
    function draw() {
      var segs = [{ n: 'Primary Header', o: 6, c: 'macp' }];
      if (on.checked) segs.push({ n: 'Security Header', o: 14, c: 'sdls mac' });
      segs.push({ n: 'Frame Data Field', o: 0, data: 1, t: on.checked ? 'encrypted + MAC' : 'user data', c: on.checked ? 'enc mac' : '' });
      if (on.checked) segs.push({ n: 'Security Trailer', o: 16, c: 'sdls' });
      segs.push({ n: 'OCF', o: 4, c: 'never' }, { n: 'FECF', o: 2, c: 'never' });
      frame(bar, segs);
      note.textContent = on.checked ? 'TM frame with the GCM baseline: 14 octets of header and 16 of trailer now share the fixed frame length with your data. Header formats are unchanged.'
        : 'Plain TM frame: the data field holds user data in clear, with nothing proving who sent it or whether it is fresh.';
    }
    on.addEventListener('change', draw); draw();
  })();

  // ---------------------------------------------------------------- builder
  (function () {
    var P = $('#b-proto'), S = $('#b-svc'), IV = $('#b-iv'), SN = $('#b-sn'), PL = $('#b-pl'), MAC = $('#b-mac');
    var bar = $('#b-bar'), msgs = $('#b-msgs');
    function v(x) { var n = parseInt(x.value, 10); return isNaN(n) ? 0 : n; }
    function draw() {
      var p = P.value, s = S.value, iv = v(IV), sn = v(SN), pl = v(PL), mac = v(MAC);
      var auth = s !== 'enc', enc = s !== 'auth';
      var hdr = 2 + iv + sn + pl;
      var out = [];
      function m(k, t) { out.push('<li class="' + k + '">' + t + '</li>'); }
      if (iv !== 0 && (iv < 1 || iv > 32)) m('bad', 'IV must be 0 or 1–32 octets.');
      if (sn !== 0 && (sn < 2 || sn > 8)) m('bad', 'Sequence Number must be 0 or 2–8 octets.');
      if (pl < 0 || pl > 2) m('bad', 'Pad Length must be 0–2 octets.');
      if (hdr > 64) m('bad', 'Security Header is ' + hdr + ' octets; the maximum is 64.');
      if (auth) {
        if (mac < 8 || mac > 64) m('bad', 'Authentication needs a MAC of 8–64 octets in the Security Trailer.');
        if (sn === 0 && iv === 0) m('bad', 'Authentication needs an anti-replay sequence number: give SN 2–8 octets, or use a counter IV.');
        else if (sn === 0 && s === 'ae') m('ok', 'The IV doubles as the sequence number (counter-mode IV), so the SN field is 0 octets.');
        else if (sn === 0) m('info', 'IV-as-sequence-number is meant for counter-mode authenticated encryption; for authentication only, carry an SN field.');
      } else {
        if (sn > 0) m('bad', 'Encryption-only SAs have no sequence number: SN must be 0 octets.');
        if (mac > 0) m('info', 'Encryption-only SAs compute no MAC; set MAC to 0 and drop the trailer.');
        m('info', 'Warning from the standard: encryption without authentication allows undetected substitution.');
      }
      if (enc && iv === 0) m('info', 'Most encryption modes need an IV; 0 octets only if the algorithm needs none.');
      if (!enc && iv > 0) m('info', 'No encryption: an IV is only needed if the MAC algorithm uses one.');
      if (out.filter(function (x) { return x.indexOf('bad') > -1; }).length === 0) m('ok', 'Valid configuration. Overhead: ' + hdr + ' + ' + (auth ? mac : 0) + ' = ' + (hdr + (auth ? mac : 0)) + ' octets per frame.');
      msgs.innerHTML = out.join('');
      var segs = [];
      var phl = { TM: 6, TC: 5, AOS: 6, USLP: 7 }[p];
      segs.push({ n: 'Primary Header', o: phl, c: auth ? 'macp' : '', t: p === 'USLP' ? '4–14 oct' : phl + ' oct' });
      if (p === 'TC') segs.push({ n: 'Segment Hdr', o: 1, c: auth ? 'mac' : '', t: 'optional' });
      if (p === 'AOS' || p === 'USLP') segs.push({ n: 'Insert Zone', o: 4, c: 'never', t: 'optional' });
      segs.push({ n: 'SPI', o: 2, c: 'sdls' + (auth ? ' mac' : '') });
      if (iv) segs.push({ n: 'IV', o: iv, c: 'sdls' });
      if (sn) segs.push({ n: 'SN', o: sn, c: 'sdls' + (auth ? ' mac' : '') });
      if (pl) segs.push({ n: 'Pad Len', o: pl, c: 'sdls' + (auth ? ' mac' : '') });
      segs.push({ n: 'Frame Data Field', o: 0, data: 1, t: enc ? 'encrypted' : 'clear', c: (enc ? 'enc ' : '') + (auth ? 'mac' : '') });
      if (auth && mac) segs.push({ n: 'MAC', o: mac, c: 'sdls never' });
      if (p !== 'TC') segs.push({ n: 'OCF', o: 4, c: 'never', t: 'optional' });
      segs.push({ n: 'FECF', o: 2, c: 'never', t: p === 'USLP' ? '2 or 4' : 'optional' });
      frame(bar, segs);
    }
    [P, S, IV, SN, PL, MAC].forEach(function (x) { x.addEventListener('input', draw); x.addEventListener('change', draw); });
    $('#b-base').addEventListener('click', function () {
      if (P.value === 'TC') { S.value = 'auth'; IV.value = 0; SN.value = 4; PL.value = 0; MAC.value = 16; }
      else { S.value = 'ae'; IV.value = 12; SN.value = 0; PL.value = 0; MAC.value = 16; }
      draw();
    });
    draw();
  })();

  // ---------------------------------------------------------------- SA database
  (function () {
    var SA = [
      { spi: 1, dir: 'Uplink', ch: 'TC · VC 0', st: 'Active', svc: 'Authentication', alg: 'AES-256-CMAC', key: 'key index K-07', len: 'IV 0 · SN 4 · PL 0 · MAC 16', mask: 'default', win: '32', why: 'Commands need authenticity and freshness more than secrecy, so this follows the TC baseline.' },
      { spi: 5, dir: 'Uplink', ch: 'TC · VC 0', st: 'Keyed, standby', svc: 'Authentication', alg: 'AES-256-CMAC', key: 'key index K-08', len: 'IV 0 · SN 4 · PL 0 · MAC 16', mask: 'default + Spacecraft ID', win: '32', why: 'Prepared for a key change. It cannot be active on VC 0 while SPI 1 is: only one active SA per GVCID at the sender.' },
      { spi: 2, dir: 'Downlink', ch: 'AOS · VC 1 science', st: 'Active', svc: 'Authenticated encryption', alg: 'AES-256-GCM', key: 'key index K-11', len: 'IV 12 · SN 0 · PL 0 · MAC 16', mask: 'default', win: '1024', why: 'Science data is confidential and must be authentic. The 96-bit counter IV doubles as the sequence number; a large window tolerates downlink gaps.' },
      { spi: 3, dir: 'Downlink', ch: 'AOS · VC 2 housekeeping', st: 'Active', svc: 'Authenticated encryption', alg: 'AES-256-GCM', key: 'key index K-12', len: 'IV 12 · SN 0 · PL 0 · MAC 16', mask: 'default', win: '1024', why: 'A separate SA per channel limits what one key protects and keeps counters independent.' },
      { spi: 6, dir: 'Downlink', ch: 'AOS · VC 63 idle', st: 'Not allowed', svc: '—', alg: '—', key: '—', len: '—', mask: '—', win: '—', bad: 1, why: 'Rejected: SAs are not created for virtual channels carrying Only Idle Data frames (4.2.2.2.3).' }
    ];
    var list = $('#sim-sadb .sa-list'), det = $('#sim-sadb .sa-detail');
    function show(k) {
      $$('button', list).forEach(function (b, i) { b.setAttribute('aria-selected', i === k ? 'true' : 'false'); });
      var s = SA[k];
      det.innerHTML = '<dl>' +
        [['SPI', s.spi], ['Direction', s.dir + ' (simplex)'], ['Bound to', s.ch], ['State', s.st], ['Service type', s.svc], ['Algorithm', s.alg], ['Key', s.key], ['Field lengths', s.len], ['Auth. mask', s.mask], ['SN window', s.win]]
          .map(function (r) { return '<dt>' + r[0] + '</dt><dd>' + esc(r[1]) + '</dd>'; }).join('') +
        '</dl><p class="why">' + esc(s.why) + '</p>';
    }
    SA.forEach(function (s, k) {
      var b = h('button', { type: 'button', role: 'tab' }, 'SPI ' + s.spi + '<span>' + esc(s.ch) + (s.bad ? ' ✕' : '') + '</span>');
      b.addEventListener('click', function () { show(k); });
      list.appendChild(b);
    });
    show(0);
  })();

  // ---------------------------------------------------------------- ApplySecurity stepper
  (function () {
    var svgEl = $('#sim-apply').previousElementSibling.querySelector('svg');
    var svc = 'ae', step = 0;
    var T = {
      0: function () { return 'The link protocol hands over the partial frame, Primary Header through Frame Data Field, with an empty Security Header. SDLS selects the SA from the GVCID (and GMAP_ID).'; },
      1: function () { return 'Encrypt the Frame Data Field with the SA\'s algorithm and IV. If the mode needs fill, record the number of pad bytes in Pad Length.'; },
      2: function (s) { return s === 'enc' ? 'Write the SPI, IV and Pad Length. There is no sequence number: encryption-only SAs have none.' : 'Increment the managed sequence number by one and place it in the Sequence Number field, or let the counter IV carry it. Add SPI and IV: the Security Header is complete, and it will be inside the MAC.'; },
      3: function () { return 'AND the frame with the SA\'s authentication bit mask. Masked bits become zero. The result is the Authentication Payload.'; },
      4: function () { return 'Compute the MAC over the Authentication Payload, drop least-significant bits down to the MAC length, and place it in the Security Trailer.'; },
      5: function (s) { return { ae: 'Return Security Header + encrypted data + Security Trailer. The link protocol then completes the frame: OCF, counters, FECF.', auth: 'Return Security Header + clear data + Security Trailer. The data is readable but tamper-evident.', enc: 'Return Security Header + encrypted data. No trailer: nothing proves who sent it.' }[s]; }
    };
    var USE = { ae: [0, 1, 2, 3, 4, 5], auth: [0, 2, 3, 4, 5], enc: [0, 1, 2, 5] };
    function draw() {
      var seq = USE[svc];
      if (step >= seq.length) step = seq.length - 1;
      svgEl.classList.add('tracing');
      $$('.hl', svgEl).forEach(function (n) { n.classList.remove('hot'); });
      for (var i = 0; i <= step; i++) {
        var id = seq[i];
        var n = svgEl.querySelector('#ap-n' + id); if (n) n.classList.add('hot');
        if (i > 0) for (var a = seq[i - 1]; a < id; a++) { var ar = svgEl.querySelector('#ap-a' + a); if (ar) ar.classList.add('hot'); }
      }
      $('#ap-no').textContent = 'Step ' + (step + 1) + ' of ' + seq.length;
      $('#ap-text').textContent = T[seq[step]](svc);
    }
    $$('#sim-apply [data-svc]').forEach(function (b) {
      b.addEventListener('click', function () {
        svc = b.dataset.svc; step = 0;
        $$('#sim-apply [data-svc]').forEach(function (x) { x.classList.toggle('on', x === b); });
        draw();
      });
    });
    $('#ap-next').addEventListener('click', function () { step = Math.min(step + 1, USE[svc].length - 1); draw(); });
    $('#ap-prev').addEventListener('click', function () { step = Math.max(step - 1, 0); draw(); });
    draw();
  })();

  // ---------------------------------------------------------------- ProcessSecurity scenarios
  (function () {
    var svgEl = $('#sim-process').previousElementSibling.querySelector('svg');
    var base = ['pr-n0', 'pr-a0', 'pr-d1'];
    var SC = {
      ok: { p: base.concat(['pr-a1', 'pr-d2', 'pr-a2', 'pr-d3', 'pr-a3', 'pr-n4', 'pr-a4', 'pr-n5', 'pr-a5', 'pr-n6']), k: 'ok', c: 'No failure', w: 'SPI matches the channel, MAC verifies, SN is above the stored value and inside the window. The receiver stores the new SN, decrypts, removes padding and returns the data.' },
      spi: { p: base.concat(['pr-x1', 'pr-f1']), k: 'bad', c: 'Invalid SPI', w: 'The SPI names an SA that is not associated with this GVCID / GMAP_ID. The frame is discarded and an exception reported, before any cryptography runs.' },
      mac: { p: base.concat(['pr-a1', 'pr-d2', 'pr-x2', 'pr-f2']), k: 'bad', c: 'MAC verification failure', w: 'One flipped bit in an authenticated field changes the MAC. The frame is discarded without decryption and may be archived for forensics.' },
      replay: { p: base.concat(['pr-a1', 'pr-d2', 'pr-a2', 'pr-d3', 'pr-x3', 'pr-f3']), k: 'bad', c: 'Anti-replay sequence number failure', w: 'The MAC is valid because this is a genuine old frame, but its SN is lower than or equal to the stored value. Discarded; the stored SN is unchanged.' },
      ahead: { p: base.concat(['pr-a1', 'pr-d2', 'pr-a2', 'pr-d3', 'pr-x3', 'pr-f3']), k: 'bad', c: 'Anti-replay sequence number failure', w: 'A genuine frame whose SN is more than the window above the stored value, for example after a long outage. Discarded and the stored SN is not moved, so the link stays rejected until resynchronised.' }
    };
    $$('#sim-process [data-sc]').forEach(function (b) {
      b.addEventListener('click', function () {
        var s = SC[b.dataset.sc];
        $$('#sim-process [data-sc]').forEach(function (x) { x.classList.toggle('on', x === b); });
        svgEl.classList.add('tracing');
        $$('.hl', svgEl).forEach(function (n) { n.classList.toggle('hot', s.p.indexOf(n.id) > -1); });
        var st = $('#pr-status');
        st.className = 'status ' + s.k;
        st.innerHTML = '<span class="code">Status: ' + esc(s.c) + '</span><span class="why">' + esc(s.w) + '</span>';
      });
    });
  })();

  // ---------------------------------------------------------------- authentication mask
  (function () {
    function F(n, st, lock, why) { return { n: n, st: st, lock: lock, why: why }; }
    var cfg = 'Not mandated. Zero (excluded) by default; a mission may include it (4.2.2.6.2 j).';
    var SH = F('Security Header: SPI, SN, PL', 'on', 1, 'Always all ones, except the IV (4.2.2.6.2 h). The sequence number is therefore authenticated.');
    var IV = F('IV', 'off', 0, 'Not mandated by the mask. AEAD modes such as GCM take the IV as an input, so a changed IV breaks the tag anyway.');
    var DATA = F('Frame Data Field', 'on', 1, 'Always all ones (4.2.2.6.2 i). With authenticated encryption, the MAC covers the ciphertext.');
    var MAC = F('MAC', 'never', 1, 'The MAC cannot cover itself.');
    var OCF = F('OCF', 'never', 1, 'Always excluded (2.3.2.2). It carries the CLCW / PLCW, which is therefore unauthenticated.');
    var FECF = F('FECF', 'never', 1, 'Always excluded: added after security processing for error detection.');
    var IZ = F('Insert Zone', 'never', 1, 'Always zero (4.2.2.6.2 g). The Insert Service is unprotected.');
    var VCID = F('Virtual Channel ID', 'on', 1, 'Always all ones (4.2.2.6.2 b). A frame cannot be moved to another virtual channel without failing the MAC.');
    var SCID = F('Spacecraft ID', 'off', 0, 'Excluded by default. Include it if a frame must not be re-targeted to another spacecraft sharing the key (note 1 to 4.2.2.6.2).');
    var DEF = {
      TM: [F('Version', 'off', 0, cfg), SCID, VCID, F('OCF flag', 'off', 0, cfg),
        F('MC Frame Count', 'off', 1, 'Always zero for TM (4.2.2.6.2 d). It is set when virtual channels are multiplexed onto the master channel, after ApplySecurity.'),
        F('VC Frame Count', 'off', 0, cfg), F('Data Field Status', 'off', 0, cfg),
        F('Frame Secondary Header', 'off', 0, 'VC_FSH may be authenticated by mission choice but is never encrypted. If the MC_FSH service is used, it stays excluded (note 2).'),
        SH, IV, DATA, MAC, OCF, FECF],
      TC: [F('Version', 'off', 0, cfg), F('Bypass flag', 'off', 0, cfg + ' Worth reviewing: it selects sequence-controlled or expedited handling.'), F('Control Command flag', 'off', 0, cfg),
        SCID, VCID, F('Frame Length', 'off', 0, cfg), F('Frame Sequence Number', 'off', 0, cfg),
        F('Segment Header', 'on', 1, 'Always all ones for TC (4.2.2.6.2 f), so the MAP ID is authenticated.'), SH, IV, DATA, MAC, FECF],
      AOS: [F('Version', 'off', 0, cfg), SCID, VCID, F('VC Frame Count', 'off', 0, cfg), F('Signaling Field', 'off', 0, cfg),
        F('Frame Header Error Control', 'off', 1, 'Always zero for AOS (4.2.2.6.2 e).'), IZ, SH, IV, DATA, MAC, OCF, FECF],
      USLP: [F('Version', 'off', 0, cfg), SCID, F('Source / Destination flag', 'off', 0, cfg), VCID,
        F('MAP ID', 'on', 1, 'Always all ones for USLP (4.2.2.6.2 c).'), F('End of Primary Header flag', 'off', 0, cfg), F('Frame Length', 'off', 0, cfg),
        F('Other primary header fields', 'off', 0, cfg + ' Covers bypass, protocol control, OCF flag and VC frame count.'), IZ, SH, IV, DATA, MAC, OCF, FECF]
    };
    var cur, sel = -1;
    var row = $('#mk-row'), info = $('#mk-info'), P = $('#mk-proto');
    function load() { cur = DEF[P.value].map(function (f) { return Object.assign({}, f); }); sel = -1; draw(); info.textContent = 'Select a field to see its rule. Unlocked fields toggle between in and out of the MAC.'; }
    function draw() {
      row.innerHTML = '';
      cur.forEach(function (f, i) {
        var lab = f.st === 'on' ? 'mask 1' : f.st === 'off' ? 'mask 0' : 'excluded';
        var b = h('button', { type: 'button', cls: 'mf ' + f.st + (f.lock ? ' lock' : '') + (i === sel ? ' sel' : ''), 'aria-pressed': f.st === 'on' ? 'true' : 'false' }, esc(f.n) + '<small>' + lab + '</small>');
        b.addEventListener('click', function () {
          sel = i;
          if (!f.lock && f.st !== 'never') f.st = f.st === 'on' ? 'off' : 'on';
          var inMac = cur.filter(function (x) { return x.st === 'on'; }).map(function (x) { return x.n; });
          info.innerHTML = '<b>' + esc(f.n) + '.</b> ' + esc(f.why) + (f.lock ? '' : ' <i>(toggled)</i>') + '<br><span class="note">MAC now covers: ' + esc(inMac.join(', ')) + '.</span>';
          draw();
          var nb = row.children[i]; if (nb) nb.focus();
        });
        row.appendChild(b);
      });
    }
    P.addEventListener('change', load); $('#mk-reset').addEventListener('click', load); load();
  })();

  // ---------------------------------------------------------------- replay window
  (function () {
    var W = $('#rp-w'), tx, rx, sent, log = $('#rp-log');
    function reset() { tx = 1; rx = 0; sent = []; log.innerHTML = ''; draw(); }
    function w() { var n = parseInt(W.value, 10); return n > 0 ? n : 1; }
    function note(k, tag, t) { var li = h('li', { cls: k }, '<span class="k">' + tag + '</span><span>' + t + '</span>'); log.appendChild(li); }
    function receive(sn, how) {
      if (sn <= rx) { note('bad', 'REJECT', how + ' SN ' + sn + ' ≤ stored ' + rx + ': replay. Stored SN unchanged.'); }
      else if (sn > rx + w()) { note('bad', 'REJECT', how + ' SN ' + sn + ' > ' + rx + ' + ' + w() + ': outside the window. Stored SN unchanged.'); }
      else { note('ok', 'ACCEPT', how + ' SN ' + sn + ' is in ' + (rx + 1) + '–' + (rx + w()) + '. Stored SN → ' + sn + '.'); rx = sn; }
      draw();
    }
    function draw() {
      $('#rp-tx').textContent = tx; $('#rp-rx').textContent = rx; $('#rp-rng').textContent = (rx + 1) + '–' + (rx + w());
      var line = $('#rp-line'); line.innerHTML = '';
      var lo = Math.max(0, rx - 4), hi = Math.max(rx + w() + 4, tx + 2);
      for (var i = lo; i <= hi && i - lo < 60; i++) {
        var c = 'nc' + (i < rx ? ' used' : '') + (i === rx ? ' stored' : '') + (i > rx && i <= rx + w() ? ' win' : '') + (i === tx ? ' tx' : '');
        line.appendChild(h('span', { cls: c, title: i === tx ? 'next SN the sender will use' : '' }, String(i)));
      }
    }
    $('#rp-send').addEventListener('click', function () { var sn = tx++; sent.push(sn); receive(sn, 'Genuine frame'); });
    $('#rp-lose').addEventListener('click', function () { var a = tx; tx += 3; note('lost', 'LOST', 'Frames ' + a + '–' + (tx - 1) + ' never reached the receiver.'); draw(); });
    $('#rp-replay').addEventListener('click', function () {
      if (!sent.length) { note('lost', 'NOTHING', 'Send a frame first so the attacker has something to capture.'); return; }
      receive(sent[sent.length - 1], 'Replayed copy of');
    });
    $('#rp-ahead').addEventListener('click', function () { receive(rx + w() + 10, 'Frame with valid MAC,'); });
    $('#rp-reset').addEventListener('click', reset);
    W.addEventListener('input', draw);
    reset();
  })();

  // ---------------------------------------------------------------- coverage table
  (function () {
    var D = {
      TM: [['Packet (VCP)', 'p', 'p', 'p'], ['VC Access', 'p', 'p', 'p'], ['VC Frame Secondary Header', 'p', 'n', 'a'], ['VC OCF', 'n', 'n', 'n'], ['VC Frame (external)', 'n', 'n', 'n'], ['MC Frame Secondary Header', 'n', 'n', 'n'], ['MC OCF', 'n', 'n', 'n'], ['MC Frame (external)', 'n', 'n', 'n']],
      TC: [['MAP Packet', 'p', 'p', 'p'], ['MAP Access', 'p', 'p', 'p'], ['VC Packet', 'p', 'p', 'p'], ['VC Access', 'p', 'p', 'p'], ['COP Management', 'n', 'n', 'n'], ['VC Frame (external)', 'n', 'n', 'n'], ['MC Frame (external)', 'n', 'n', 'n']],
      AOS: [['Packet', 'p', 'p', 'p'], ['Bitstream', 'p', 'p', 'p'], ['VC Access', 'p', 'p', 'p'], ['VC OCF', 'n', 'n', 'n'], ['VC Frame (external)', 'n', 'n', 'n'], ['MC Frame (external)', 'n', 'n', 'n'], ['Insert', 'n', 'n', 'n']],
      USLP: [['MAP Packet', 'p', 'p', 'p'], ['MAP Access', 'p', 'p', 'p'], ['MAP Octet Stream', 'p', 'p', 'p'], ['MC OCF', 'n', 'n', 'n'], ['VC Frame (external)', 'n', 'n', 'n'], ['MC Frame (external)', 'n', 'n', 'n'], ['Insert', 'n', 'n', 'n'], ['COPs Management', 'n', 'n', 'n']]
    };
    var L = { p: '<span class="chip p">Protected</span>', n: '<span class="chip n">Not protected</span>', a: '<span class="chip a">Authentication only</span>' };
    var NOTE = { TM: 'Encryption covers the data field only; VC_FSH can join the MAC but is never encrypted.', TC: 'Each SA serves exactly one VC. COP-1 control frames are unprotected.', AOS: 'The Insert Zone is always masked out.', USLP: 'With COPs in use, each SA serves one VC. COP-1 / COP-P control is unprotected.' };
    function show(p) {
      $$('#sim-cover [data-p]').forEach(function (b) { b.classList.toggle('on', b.dataset.p === p); b.setAttribute('aria-selected', b.dataset.p === p ? 'true' : 'false'); });
      $('#cv-tbl').innerHTML = '<table><thead><tr><th>' + p + ' service</th><th>Authentication</th><th>Encryption</th><th>Auth. encryption</th></tr></thead><tbody>' +
        D[p].map(function (r) { return '<tr><td>' + esc(r[0]) + '</td><td>' + L[r[1]] + '</td><td>' + L[r[2]] + '</td><td>' + L[r[3]] + '</td></tr>'; }).join('') +
        '</tbody></table><p class="note">' + esc(NOTE[p]) + ' Source: table 5-1.</p>';
    }
    $$('#sim-cover [data-p]').forEach(function (b) { b.setAttribute('role', 'tab'); b.addEventListener('click', function () { show(b.dataset.p); }); });
    show('TM');
  })();

  // ---------------------------------------------------------------- overhead
  (function () {
    var B = $('#ov-b'), N = $('#ov-n'), out = $('#ov-out');
    function draw() {
      var hd = B.value === 'gcm' ? 14 : 6, tr = 16, n = parseInt(N.value, 10) || 0, x = hd + tr;
      if (n <= x) { out.innerHTML = 'A data field of ' + n + ' octets cannot hold the <b>' + x + '</b> octets of SDLS overhead.'; return; }
      out.innerHTML = 'SDLS adds <b>' + x + '</b> octets (header ' + hd + ' + trailer ' + tr + '). Of ' + n + ' octets, <b>' + (n - x) + '</b> remain for user data: <b>' + (x / n * 100).toFixed(1) + '%</b> overhead.';
    }
    B.addEventListener('change', draw); N.addEventListener('input', draw); draw();
  })();

  // ---------------------------------------------------------------- PICS builder
  (function () {
    var boxes = $$('#sim-pics input'), out = $('#pc-out');
    function draw() {
      var p = boxes.filter(function (b) { return b.dataset.p && b.checked; }).map(function (b) { return b.dataset.p; });
      var s = boxes.filter(function (b) { return b.dataset.s && b.checked; }).map(function (b) { return b.dataset.s; });
      var auth = s.indexOf('auth') > -1 || s.indexOf('ae') > -1, enc = s.indexOf('enc') > -1 || s.indexOf('ae') > -1;
      var issues = [];
      if (!p.length) issues.push('O.1 not met: support at least one link protocol.');
      if (!s.length) issues.push('O.2 not met: support at least one security service.');
      var mand = ['GVCID', 'SPI', 'SA_service_type', 'SA_length_SN, _IV, _PL, _MAC', 'ApplySecurity (sender) / ProcessSecurity (receiver)', 'Discard and report frames with the wrong SA'];
      if (p.indexOf('TC') > -1) mand.push('GMAP_ID (C.1, because TC is supported)');
      if (auth) mand.push('Authentication algorithm, key, mask, sequence number, window (C.2)', 'Increment SN, apply mask, compute and place MAC; verify MAC and SN, update SN (C.2)');
      if (enc) mand.push('Encryption algorithm and key (C.3)', 'Initialization vector (C.4)', 'Encrypt and decrypt frame data (C.3)');
      if (s.indexOf('ae') > -1) mand.push('AEAD plaintext / AAD split (C.8)');
      var opt = ['Truncate MAC', 'Put pad length in header', 'Archive rejected frames'];
      if (!enc) opt.push('Initialization vector (C.4 optional without encryption)');
      out.innerHTML = (issues.length ? '<p class="verdict bad">Not conformant yet.</p><ul>' + issues.map(function (x) { return '<li>' + x + '</li>'; }).join('') + '</ul>'
        : '<p class="verdict ok">Conformance possible with these choices.</p>') +
        '<p class="mono" style="margin-top:10px">Mandatory</p><ul>' + mand.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>' +
        '<p class="mono" style="margin-top:10px">Optional</p><ul>' + opt.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>';
    }
    boxes.forEach(function (b) { b.addEventListener('change', draw); });
    draw();
  })();

  updateProgress();
})();
