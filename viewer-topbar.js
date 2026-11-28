// Horní lišta pro splatviewer.html: Zpět · název scény · přepínač nebe.
// Do exportu z LichtFeld Studia se vkládá jediným řádkem před </body>:
//   <script src="viewer-topbar.js"></script>
// Pro viewer v podsložce (viewer2/) se přidá data-root="../": odkaz Zpět i nebe se berou
// z kořene webu a pravidla pro canvas starého vieweru se nepoužijí (nový viewer má vlastní #stage).
(() => {
  const ROOT = document.currentScript?.dataset.root ?? '';
  const BAR = 48;                 // výška lišty v px
  const SKYBOX = ROOT + 'nebe_4k.jpg';   // stejná panorama jako v indexu
  const KEY = 'skybox';           // sdílené s indexem (localStorage)

  const params = new URLSearchParams(location.search);
  const file = params.get('content') || '';
  const fileName = file.split('/').pop();
  const title = params.get('title') || fileName.replace(/\.sog$/i, '').replace(/_/g, ' ');
  const skyOn = params.has('skybox');
  // jazyk: ?lang= (předává index), jinak volba z indexu (localStorage), jinak jazyk prohlížeče
  const lang = (() => {
    const p = params.get('lang');
    if (p === 'cs' || p === 'en') return p;
    try { const s = localStorage.getItem('lang'); if (s === 'cs' || s === 'en') return s; } catch (e) {}
    return (navigator.languages || [navigator.language || '']).some(l => /^(cs|sk)/i.test(l)) ? 'cs' : 'en';
  })();
  const L = lang === 'en'
    ? { back: 'Back', backTitle: 'Back to the list of splats', sky: 'Sky', skyTitle: 'Sky background', site: 'Drone Gaussian Splats' }
    : { back: 'Zpět', backTitle: 'Zpět na seznam splatů', sky: 'Nebe', skyTitle: 'Zobrazení nebe', site: 'Gaussian Splaty z dronu' };

  const css = `
    :root { --topbar:${BAR}px; }
    #topbar { position:fixed; top:0; left:0; right:0; height:var(--topbar); z-index:1000;
      display:flex; align-items:center; gap:14px; padding:0 max(14px, env(safe-area-inset-right)) 0 max(14px, env(safe-area-inset-left));
      background:#000; border-bottom:1px solid #1f2125; color:#e6e3e0;
      font-family:system-ui,-apple-system,"Segoe UI",sans-serif; font-size:14px; }
    #topbar * { pointer-events:auto; touch-action:manipulation; }
    #topbar .back { display:inline-flex; align-items:center; gap:6px; color:#e6e3e0; text-decoration:none;
      padding:6px 12px 6px 9px; border:1px solid #2a2d32; border-radius:8px; flex:none; transition:border-color .15s, color .15s; }
    #topbar .back:hover { border-color:#ffaf50; color:#ffaf50; }
    #topbar .title { min-width:0; flex:1; display:flex; flex-direction:column; line-height:1.2; }
    #topbar .title b { font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    #topbar .title small { color:#8a8f96; font-size:11px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    #topbar .switch { display:inline-flex; align-items:center; gap:9px; cursor:pointer; color:#8a8f96; user-select:none; flex:none; }
    #topbar .switch input { position:absolute; opacity:0; width:0; height:0; }
    #topbar .track { width:38px; height:22px; border-radius:11px; background:#26292e; position:relative; transition:background .15s; }
    #topbar .track::after { content:''; position:absolute; top:3px; left:3px; width:16px; height:16px; border-radius:50%;
      background:#8a8f96; transition:transform .15s, background .15s; }
    #topbar .switch input:checked + .track { background:rgba(255,175,80,.35); }
    #topbar .switch input:checked + .track::after { transform:translateX(16px); background:#ffaf50; }
    #topbar .switch input:focus-visible + .track { outline:2px solid #ffaf50; outline-offset:2px; }
    @media (max-width:520px) { #topbar .back .lbl, #topbar .switch .lbl, #topbar .title small { display:none; } }

    html, body { height:100%; background:#000; }
  ` + (ROOT ? '' : `
    /* scéna a UI vieweru začínají pod lištou (velikost renderu se bere z canvas.clientWidth/Height) */
    pc-app canvas { position:fixed; top:var(--topbar); left:0;
      width:100vw !important; height:calc(100% - var(--topbar)) !important; }
    #ui, #infoPanel { top:var(--topbar) !important; height:calc(100% - var(--topbar)) !important; }
  `);
  const style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);

  const esc = s => s.replace(/[&<>"]/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]));
  const bar = document.createElement('div');
  bar.id = 'topbar';
  bar.innerHTML = `
    <a class="back" href="${ROOT || './'}" title="${L.backTitle}">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
      <span class="lbl">${L.back}</span>
    </a>
    <div class="title"><b>${esc(title)}</b>${fileName ? `<small>${esc(fileName)}</small>` : ''}</div>
    <label class="switch" title="${L.skyTitle}">
      <span class="lbl">${L.sky}</span>
      <input type="checkbox" ${skyOn ? 'checked' : ''}>
      <span class="track"></span>
    </label>`;
  document.body.appendChild(bar);
  document.title = `${title} – ${L.site}`;

  // Přepnutí nebe = znovunačtení s/bez parametru skybox (model se většinou vezme z cache prohlížeče)
  bar.querySelector('input').addEventListener('change', e => {
    const on = e.target.checked;
    try { localStorage.setItem(KEY, on ? '1' : '0'); } catch (err) {}
    const p = new URLSearchParams(location.search);
    if (on) p.set('skybox', SKYBOX); else p.delete('skybox');
    location.replace(`${location.pathname}?${p.toString()}`);
  });

  window.dispatchEvent(new Event('resize'));
})();
