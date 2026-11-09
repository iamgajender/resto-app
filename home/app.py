from flask import Flask

app = Flask(__name__)

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Quick Bites - fresh meals and cold drinks, ordered in seconds.">
<meta name="theme-color" content="#0b0706">
<title>Quick Bites | Big taste. Zero wait.</title>
<script>document.documentElement.classList.add("js")</script>
<style>
  :root {
    color-scheme: dark light;
    --bg:#0b0706; --ink:#fff4e8; --muted:#b9a79b;
    --glass:rgba(255,255,255,.05); --glass-2:rgba(255,255,255,.1); --line:rgba(255,255,255,.1);
    --navbg:rgba(24,14,10,.6);
    --red:#ff4d3d; --orange:#ff8a3d; --gold:#ffc857; --ok:#3ddc84; --on-grad:#1d0c05;
    --grad:linear-gradient(135deg,#ff4d3d 0%,#ff8a3d 55%,#ffc857 100%);
    --shadow:0 30px 70px rgba(0,0,0,.55); --r:28px;
    --sans:"Inter",ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
    --serif:"Playfair Display",ui-serif,Georgia,"Times New Roman",serif;
  }
  @media (prefers-color-scheme: light) {
    :root {
      --bg:#fff8ee; --ink:#2a160e; --muted:#7c6558;
      --glass:rgba(255,255,255,.72); --glass-2:#ffffff; --line:rgba(120,70,30,.16);
      --navbg:rgba(255,250,242,.74); --shadow:0 30px 70px rgba(160,90,30,.2);
    }
    .orb { opacity:.25 !important; }
  }
  * { box-sizing:border-box; }
  html { scroll-behavior:smooth; }
  body { margin:0; font-family:var(--sans); background:var(--bg); color:var(--ink); line-height:1.55; overflow-x:hidden; -webkit-font-smoothing:antialiased; }
  body::after { content:""; position:fixed; inset:0; z-index:90; pointer-events:none; opacity:.05; mix-blend-mode:overlay;
    background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E"); }
  a { color:inherit; text-decoration:none; }
  h1, h2, h3, p { margin:0; }
  a:focus-visible, button:focus-visible { outline:3px solid var(--gold); outline-offset:3px; border-radius:12px; }
  .wrap { max-width:1180px; margin:0 auto; padding:0 24px; }

  /* ---------- ambient background ---------- */
  .bg { position:fixed; inset:0; z-index:-1; overflow:hidden; pointer-events:none; }
  .orb { position:absolute; border-radius:50%; filter:blur(90px); }
  .o1 { width:560px; height:560px; left:-160px; top:-140px; background:#ff4d3d; opacity:.45; animation:drift 18s ease-in-out infinite alternate; }
  .o2 { width:520px; height:520px; right:-160px; top:140px; background:#ffb347; opacity:.3; animation:drift 22s ease-in-out infinite alternate-reverse; }
  .o3 { width:640px; height:640px; left:28%; bottom:-340px; background:#ff7a2e; opacity:.28; animation:drift 26s ease-in-out infinite alternate; }
  @keyframes drift { to { transform:translate(70px,40px) scale(1.12); } }

  /* ---------- header ---------- */
  .nav { position:sticky; top:0; z-index:50; padding:14px 20px; }
  .nav-in { max-width:1180px; margin:0 auto; display:flex; align-items:center; justify-content:space-between; gap:16px; padding:10px 12px 10px 18px; border-radius:999px; background:var(--navbg); border:1px solid var(--line); backdrop-filter:blur(18px) saturate(1.5); -webkit-backdrop-filter:blur(18px) saturate(1.5); transition:box-shadow .3s; }
  .nav.scrolled .nav-in { box-shadow:var(--shadow); }
  .logo { display:flex; align-items:center; gap:10px; font-weight:800; font-size:20px; letter-spacing:-.02em; }
  .logo .mark { display:grid; place-items:center; width:38px; height:38px; border-radius:12px; background:var(--grad); font-size:20px; box-shadow:0 6px 18px rgba(255,100,50,.4); }
  .logo em { font-family:var(--serif); font-style:italic; font-weight:600; color:var(--gold); }
  .links { display:flex; align-items:center; gap:4px; }
  .links a.l { padding:9px 16px; border-radius:999px; font-weight:600; font-size:15px; color:var(--muted); transition:.2s; }
  .links a.l:hover { color:var(--ink); background:var(--glass-2); }
  .mt, .burger { display:none; }

  .btn { position:relative; overflow:hidden; display:inline-flex; align-items:center; justify-content:center; gap:10px; padding:14px 26px; border-radius:999px; border:1px solid transparent; font-family:inherit; font-weight:700; font-size:16px; cursor:pointer; transition:transform .2s, box-shadow .2s, background .2s; }
  .btn:hover { transform:translateY(-3px); }
  .btn-primary { background:var(--grad); color:var(--on-grad); box-shadow:0 12px 30px rgba(255,100,50,.38), inset 0 1px 0 rgba(255,255,255,.45); }
  .btn-primary:hover { box-shadow:0 18px 40px rgba(255,100,50,.5), inset 0 1px 0 rgba(255,255,255,.45); }
  .btn-primary::after { content:""; position:absolute; top:0; bottom:0; width:60%; left:-80%; background:linear-gradient(100deg,transparent,rgba(255,255,255,.55),transparent); transform:skewX(-20deg); transition:left .7s; }
  .btn-primary:hover::after { left:130%; }
  .btn-glass { background:var(--glass); border-color:var(--line); color:var(--ink); backdrop-filter:blur(12px); }
  .btn-glass:hover { background:var(--glass-2); }
  .btn-sm { padding:10px 20px; font-size:15px; }

  /* ---------- hero ---------- */
  .hero { padding:56px 0 30px; }
  .hero-grid { display:grid; grid-template-columns:1.05fr .95fr; gap:48px; align-items:center; }
  .eyebrow-pill { display:inline-flex; align-items:center; gap:10px; padding:8px 16px 8px 12px; border-radius:999px; background:var(--glass); border:1px solid var(--line); font-weight:600; font-size:13px; letter-spacing:.04em; backdrop-filter:blur(10px); }
  .eyebrow-pill i { width:9px; height:9px; border-radius:50%; background:var(--ok); box-shadow:0 0 0 0 rgba(61,220,132,.6); animation:ping 2s infinite; }
  @keyframes ping { 70% { box-shadow:0 0 0 10px rgba(61,220,132,0); } 100% { box-shadow:0 0 0 0 rgba(61,220,132,0); } }
  h1 { margin:24px 0 22px; font-size:clamp(46px,7.4vw,96px); line-height:.96; letter-spacing:-.045em; font-weight:800; }
  h1 .em { display:inline-block; padding-right:.08em; font-family:var(--serif); font-style:italic; font-weight:600; letter-spacing:-.03em; background:var(--grad); -webkit-background-clip:text; background-clip:text; color:transparent; }
  .lead { max-width:480px; color:var(--muted); font-size:19px; margin-bottom:34px; }
  .cta { display:flex; flex-wrap:wrap; gap:14px; }
  .facts { display:flex; flex-wrap:wrap; gap:0; margin-top:46px; }
  .fact { padding:0 28px; border-left:1px solid var(--line); }
  .fact:first-child { padding-left:0; border-left:0; }
  .fact b { display:block; font-size:30px; letter-spacing:-.03em; line-height:1.1; }
  .fact span { color:var(--muted); font-size:14px; }

  .stage { position:relative; width:min(100%,500px); aspect-ratio:1; margin-inline:auto; }
  .ring { position:absolute; inset:0; border-radius:50%; background:conic-gradient(from 0deg,var(--red),var(--gold),transparent 35%,var(--orange) 65%,transparent 85%,var(--red)); -webkit-mask:radial-gradient(farthest-side,transparent calc(100% - 3px),#000 calc(100% - 2px)); mask:radial-gradient(farthest-side,transparent calc(100% - 3px),#000 calc(100% - 2px)); animation:spin 16s linear infinite; }
  @keyframes spin { to { transform:rotate(360deg); } }
  .disc { position:absolute; inset:7%; border-radius:50%; background:radial-gradient(circle at 30% 25%,var(--glass-2),var(--glass) 55%,transparent 100%); border:1px solid var(--line); box-shadow:inset 0 0 80px rgba(255,138,61,.16), var(--shadow); }
  .glow { position:absolute; inset:20%; border-radius:50%; background:radial-gradient(circle,rgba(255,138,61,.55),transparent 70%); filter:blur(34px); }
  .burger-art { position:absolute; inset:10% 9% 8%; animation:float 6s ease-in-out infinite; filter:drop-shadow(0 28px 28px rgba(0,0,0,.45)); }
  .burger-art svg { width:100%; height:100%; display:block; }
  @keyframes float { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-14px); } }
  .chip { position:absolute; display:flex; align-items:center; gap:12px; padding:10px 18px 10px 10px; border-radius:20px; background:var(--glass); border:1px solid var(--line); backdrop-filter:blur(16px); -webkit-backdrop-filter:blur(16px); box-shadow:var(--shadow); font-weight:700; font-size:14px; line-height:1.25; animation:float 7s ease-in-out infinite; }
  .chip i { display:grid; place-items:center; width:38px; height:38px; border-radius:12px; background:var(--grad); font-style:normal; font-size:18px; }
  .chip small { display:block; font-weight:500; font-size:12px; color:var(--muted); }
  .c1 { top:9%; left:-3%; }
  .c2 { bottom:13%; left:-7%; animation-delay:-2.4s; }
  .c3 { top:24%; right:-5%; animation-delay:-4.6s; }

  /* ---------- marquee ---------- */
  .marquee { margin-top:46px; overflow:hidden; border-block:1px solid var(--line); padding:20px 0; -webkit-mask-image:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent); mask-image:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent); }
  .track { display:flex; gap:44px; width:max-content; }
  .js .track { animation:slide 38s linear infinite; }
  .track span { display:inline-flex; align-items:center; gap:44px; white-space:nowrap; font-size:15px; font-weight:700; letter-spacing:.14em; text-transform:uppercase; color:var(--muted); }
  .track span::after { content:"\\2726"; color:var(--orange); }
  @keyframes slide { to { transform:translateX(-50%); } }

  /* ---------- sections ---------- */
  .block { padding:92px 0 0; }
  .sec-head { display:flex; align-items:flex-end; justify-content:space-between; flex-wrap:wrap; gap:18px; margin-bottom:38px; }
  .eyebrow { display:block; margin-bottom:12px; font-size:13px; font-weight:800; letter-spacing:.18em; text-transform:uppercase; background:var(--grad); -webkit-background-clip:text; background-clip:text; color:transparent; }
  .sec-head h2 { font-size:clamp(32px,4.8vw,56px); line-height:1.02; letter-spacing:-.04em; font-weight:800; }
  .sec-head h2 .em { font-family:var(--serif); font-style:italic; font-weight:600; letter-spacing:-.02em; }
  .more { font-weight:700; color:var(--gold); }
  .more:hover { text-decoration:underline; text-underline-offset:5px; }

  .js .reveal { opacity:0; transform:translateY(30px); transition:opacity .9s cubic-bezier(.2,.7,.2,1), transform .9s cubic-bezier(.2,.7,.2,1); transition-delay:var(--d,0s); }
  .js .reveal.in { opacity:1; transform:none; }

  /* bento categories */
  .bento { display:grid; grid-template-columns:repeat(12,1fr); gap:20px; }
  .card { position:relative; overflow:hidden; display:flex; flex-direction:column; justify-content:flex-end; grid-column:span 6; min-height:320px; padding:32px; border-radius:var(--r); background:var(--glass); border:1px solid var(--line); backdrop-filter:blur(12px); -webkit-backdrop-filter:blur(12px); transition:transform .35s cubic-bezier(.2,.7,.2,1), border-color .3s, box-shadow .3s; }
  .c7 { grid-column:span 7; } .c5 { grid-column:span 5; }
  .card::before { content:""; position:absolute; inset:0; background:radial-gradient(460px circle at var(--mx,70%) var(--my,0%),rgba(255,138,61,.24),transparent 60%); opacity:0; transition:opacity .35s; pointer-events:none; }
  .card:hover { transform:translateY(-8px); border-color:rgba(255,160,80,.5); box-shadow:var(--shadow); }
  .card:hover::before { opacity:1; }
  .card .tag { position:absolute; top:24px; left:28px; padding:5px 12px; border-radius:999px; background:var(--grad); color:var(--on-grad); font-size:12px; font-weight:800; letter-spacing:.06em; text-transform:uppercase; }
  .card .art { position:absolute; top:22px; right:26px; display:flex; align-items:flex-start; }
  .card .art b { font-size:clamp(56px,7vw,92px); font-weight:400; line-height:1; filter:drop-shadow(0 14px 14px rgba(0,0,0,.35)); transition:transform .5s cubic-bezier(.2,.7,.2,1); }
  .card .art b:nth-child(2) { margin:26px -12px 0; } .card .art b:nth-child(3) { margin-top:6px; }
  .card:hover .art b:nth-child(1) { transform:rotate(-10deg) translateY(-6px); }
  .card:hover .art b:nth-child(2) { transform:rotate(8deg) translateY(-10px); }
  .card:hover .art b:nth-child(3) { transform:rotate(-6deg) translateY(-6px); }
  .card h3 { font-size:34px; letter-spacing:-.03em; margin-bottom:8px; }
  .card p { max-width:360px; color:var(--muted); }
  .card .go { position:absolute; right:26px; bottom:26px; display:grid; place-items:center; width:52px; height:52px; border-radius:50%; background:var(--grad); color:var(--on-grad); font-size:22px; font-weight:800; transition:transform .35s; }
  .card:hover .go { transform:rotate(-45deg) scale(1.08); }

  /* popular now */
  .pop { display:grid; grid-template-columns:repeat(4,1fr); gap:18px; }
  .pitem { position:relative; display:flex; flex-direction:column; gap:6px; padding:22px; border-radius:24px; background:var(--glass); border:1px solid var(--line); backdrop-filter:blur(12px); transition:transform .3s, border-color .3s, box-shadow .3s; }
  .pitem:hover { transform:translateY(-6px); border-color:rgba(255,160,80,.5); box-shadow:var(--shadow); }
  .pe { display:grid; place-items:center; width:84px; height:84px; margin-bottom:10px; border-radius:24px; background:radial-gradient(circle at 30% 25%,rgba(255,200,87,.35),rgba(255,77,61,.12)); font-size:46px; }
  .pc { font-size:12px; font-weight:800; letter-spacing:.12em; text-transform:uppercase; color:var(--orange); }
  .pitem h3 { font-size:20px; letter-spacing:-.02em; line-height:1.2; flex:1; }
  .pf { display:flex; align-items:center; justify-content:space-between; margin-top:14px; }
  .pf b { font-size:24px; letter-spacing:-.02em; }
  .pf span { font-weight:700; font-size:14px; color:var(--gold); }
  .pitem.sk { min-height:236px; background:linear-gradient(90deg,var(--glass),var(--glass-2),var(--glass)); background-size:200% 100%; animation:sh 1.3s linear infinite; }
  @keyframes sh { to { background-position:-200% 0; } }

  /* how it works */
  .steps { display:grid; grid-template-columns:repeat(4,1fr); gap:18px; }
  .step { position:relative; padding:30px 26px; border-radius:var(--r); background:var(--glass); border:1px solid var(--line); backdrop-filter:blur(12px); }
  .step .n { display:block; margin-bottom:14px; font-family:var(--serif); font-style:italic; font-size:58px; line-height:1; font-weight:600; background:var(--grad); -webkit-background-clip:text; background-clip:text; color:transparent; }
  .step b { display:block; font-size:20px; letter-spacing:-.02em; margin-bottom:6px; }
  .step span { color:var(--muted); font-size:15px; }
  .step::after { content:"\\2192"; position:absolute; right:-17px; top:50%; z-index:2; display:grid; place-items:center; width:32px; height:32px; margin-top:-16px; border-radius:50%; background:var(--bg); border:1px solid var(--line); color:var(--orange); font-weight:800; }
  .step:last-child::after { display:none; }

  /* call to action */
  .banner { position:relative; overflow:hidden; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:28px; padding:68px 56px; border-radius:36px; background:linear-gradient(120deg,#ff4d3d 0%,#ff7a2e 52%,#ffb347 100%); color:var(--on-grad); box-shadow:0 40px 90px rgba(255,90,40,.3); }
  .banner::before, .banner::after { content:""; position:absolute; border-radius:50%; border:2px solid rgba(255,255,255,.25); pointer-events:none; }
  .banner::before { width:420px; height:420px; right:-120px; top:-190px; }
  .banner::after { width:260px; height:260px; right:120px; bottom:-170px; }
  .banner h2 { position:relative; font-size:clamp(34px,5vw,60px); line-height:1; letter-spacing:-.045em; font-weight:800; margin-bottom:12px; }
  .banner h2 .em { font-family:var(--serif); font-style:italic; font-weight:600; }
  .banner p { position:relative; font-size:19px; font-weight:500; opacity:.85; }
  .banner .btn { position:relative; background:#1a0a04; color:#fff; box-shadow:0 14px 34px rgba(0,0,0,.35); }

  /* footer */
  footer { margin-top:100px; border-top:1px solid var(--line); padding:56px 0 40px; color:var(--muted); }
  .f-grid { display:grid; grid-template-columns:1.6fr 1fr 1fr 1fr; gap:36px; }
  .f-grid p { max-width:300px; margin-top:14px; font-size:15px; }
  .f-grid h4 { margin:0 0 14px; font-size:13px; letter-spacing:.14em; text-transform:uppercase; color:var(--ink); }
  .f-grid a { display:block; padding:4px 0; font-size:15px; }
  .f-grid a:hover { color:var(--gold); }
  .f-bot { display:flex; justify-content:space-between; flex-wrap:wrap; gap:10px; margin-top:44px; padding-top:24px; border-top:1px solid var(--line); font-size:14px; }

  /* ---------- responsive ---------- */
  @media (max-width:1000px) {
    .hero-grid { grid-template-columns:1fr; gap:34px; }
    .stage { width:min(100%,440px); }
    .c1 { left:0; } .c2 { left:-2%; } .c3 { right:0; }
    .c7, .c5, .card { grid-column:span 12; }
    .pop, .steps { grid-template-columns:repeat(2,1fr); }
    .step::after { display:none; }
    .f-grid { grid-template-columns:1fr 1fr; }
  }
  @media (max-width:760px) {
    .nav { padding:10px 12px; }
    .burger { display:grid; place-items:center; width:42px; height:42px; border-radius:50%; border:1px solid var(--line); background:var(--glass); cursor:pointer; font-size:19px; }
    .links { position:absolute; top:72px; left:12px; right:12px; flex-direction:column; align-items:stretch; gap:4px; padding:14px; border-radius:26px; background:var(--navbg); border:1px solid var(--line); backdrop-filter:blur(22px); -webkit-backdrop-filter:blur(22px); box-shadow:var(--shadow); display:none; }
    .mt:checked ~ .links { display:flex; }
    .links a.l { text-align:center; }
    .nav-in { position:relative; }
  }
  @media (max-width:560px) {
    .block { padding-top:72px; }
    .pop, .steps, .f-grid { grid-template-columns:1fr; }
    .fact { padding:0 18px; } .fact b { font-size:26px; }
    .banner { padding:44px 28px; }
    .card { padding:26px; min-height:290px; }
    .chip { transform:scale(.9); }
  }
  @media (prefers-reduced-motion:reduce) {
    *, *::before, *::after { animation:none !important; transition:none !important; }
    html { scroll-behavior:auto; }
    .js .reveal { opacity:1; transform:none; }
  }
</style>
</head>
<body>

<div class="bg" aria-hidden="true"><span class="orb o1"></span><span class="orb o2"></span><span class="orb o3"></span></div>

<header class="nav">
  <div class="nav-in">
    <a class="logo" href="/" aria-label="Quick Bites home"><span class="mark">&#127828;</span>Quick <em>Bites</em></a>
    <input type="checkbox" id="mt" class="mt" aria-hidden="true">
    <label class="burger" for="mt" aria-label="Toggle menu">&#9776;</label>
    <nav class="links">
      <a class="l" href="/meals">Meals</a>
      <a class="l" href="/beverages">Beverages</a>
      <a class="l" href="/orders">My Orders</a>
      <a class="l" href="/kitchen">Kitchen</a>
      <a class="btn btn-primary btn-sm" href="/meals">Order now &rarr;</a>
    </nav>
  </div>
</header>

<main>
  <section class="hero">
    <div class="wrap hero-grid">
      <div>
        <span class="eyebrow-pill"><i></i>Now serving &middot; fresh &amp; hot every day</span>
        <h1>Big taste.<br><span class="em">Zero wait.</span></h1>
        <p class="lead">Pick your favourite burger meal, add an ice-cold drink and place your order in seconds. Every order is saved, so you can track it anytime.</p>
        <div class="cta">
          <a class="btn btn-primary" href="/meals">Order now &rarr;</a>
          <a class="btn btn-glass" href="/beverages">Explore drinks</a>
        </div>
        <div class="facts">
          <div class="fact"><b>10 min</b><span>avg. prep time</span></div>
          <div class="fact"><b>16+</b><span>menu items</span></div>
          <div class="fact"><b>4.9 &#9733;</b><span>customer rating</span></div>
        </div>
      </div>

      <div class="stage" aria-hidden="true">
        <div class="ring"></div>
        <div class="disc"></div>
        <div class="glow"></div>
        <div class="burger-art"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 20 400 400" role="img" aria-label="Burger">
  <defs>
    <linearGradient id="bunTop" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffd98a"/><stop offset=".45" stop-color="#f3a640"/><stop offset="1" stop-color="#c8701a"/>
    </linearGradient>
    <linearGradient id="bunBot" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#eaa23c"/><stop offset="1" stop-color="#b9631a"/>
    </linearGradient>
    <linearGradient id="patty" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#7a4228"/><stop offset="1" stop-color="#3a1a0e"/>
    </linearGradient>
    <linearGradient id="cheese" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffe066"/><stop offset="1" stop-color="#ffb300"/>
    </linearGradient>
    <linearGradient id="leaf" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#8be37a"/><stop offset="1" stop-color="#2f9e44"/>
    </linearGradient>
    <linearGradient id="tom" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ff7a68"/><stop offset="1" stop-color="#d62828"/>
    </linearGradient>
    <radialGradient id="shine" cx=".35" cy=".25" r=".7">
      <stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="shadow" cx=".5" cy=".5" r=".5">
      <stop offset="0" stop-color="#000" stop-opacity=".55"/><stop offset="1" stop-color="#000" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <ellipse cx="200" cy="394" rx="150" ry="16" fill="url(#shadow)"/>
  <g transform="translate(0 30)">
  <path d="M62 282 H338 Q338 332 296 344 H104 Q62 332 62 282 Z" fill="url(#bunBot)"/>
  <path d="M80 296 Q200 312 320 296" stroke="#fff" stroke-opacity=".18" stroke-width="4" fill="none" stroke-linecap="round"/>
  </g>
  <g transform="translate(0 26)">
  <rect x="54" y="226" width="292" height="62" rx="31" fill="url(#patty)"/>
  <g stroke="#1f0c05" stroke-opacity=".5" stroke-width="3" stroke-linecap="round">
    <path d="M96 246 l14 8"/><path d="M150 238 l12 10"/><path d="M214 248 l14 8"/><path d="M274 240 l12 10"/><path d="M120 268 l12 6"/><path d="M246 270 l14 6"/>
  </g>
  <path d="M74 236 Q200 222 326 236" stroke="#fff" stroke-opacity=".14" stroke-width="4" fill="none" stroke-linecap="round"/>
  <path d="M60 220 H340 L326 236 L300 236 L292 266 Q288 276 282 266 L276 236 L204 236 L196 254 Q192 262 187 254 L182 236 L74 236 Z" fill="url(#cheese)"/>
  <path d="M70 224 H330" stroke="#fff" stroke-opacity=".45" stroke-width="3" stroke-linecap="round"/>
  </g>
  <g transform="translate(0 26)">
  <rect x="64" y="200" width="272" height="26" rx="13" fill="url(#tom)"/>
  <g fill="#fff" fill-opacity=".3"><ellipse cx="120" cy="210" rx="14" ry="3"/><ellipse cx="200" cy="209" rx="18" ry="3"/><ellipse cx="282" cy="210" rx="14" ry="3"/></g>
  </g>
  <g transform="translate(0 12)">
  <rect x="54" y="190" width="288" height="34" fill="#3fae52"/>
  <path d="M50 196 q22 -26 44 0 t44 0 t44 0 t44 0 t44 0 t44 0 t44 0 v26 H50 Z" fill="url(#leaf)"/>
  <path d="M66 204 q18 -14 36 0 t36 0 t36 0 t36 0 t36 0 t36 0" stroke="#d7ffd0" stroke-opacity=".5" stroke-width="3" fill="none" stroke-linecap="round"/>
  </g>
  <path d="M52 192 C52 96 120 40 200 40 C280 40 348 96 348 192 Q348 204 332 204 H68 Q52 204 52 192 Z" fill="url(#bunTop)"/>
  <path d="M52 192 C52 96 120 40 200 40 C280 40 348 96 348 192 Q348 204 332 204 H68 Q52 204 52 192 Z" fill="url(#shine)"/>
  <g fill="#fff3d0">
    <ellipse cx="150" cy="92" rx="9" ry="4.5" transform="rotate(-28 150 92)"/>
    <ellipse cx="208" cy="74" rx="9" ry="4.5" transform="rotate(8 208 74)"/>
    <ellipse cx="262" cy="104" rx="9" ry="4.5" transform="rotate(34 262 104)"/>
    <ellipse cx="116" cy="136" rx="9" ry="4.5" transform="rotate(-48 116 136)"/>
    <ellipse cx="186" cy="124" rx="9" ry="4.5" transform="rotate(-6 186 124)"/>
    <ellipse cx="244" cy="148" rx="9" ry="4.5" transform="rotate(22 244 148)"/>
    <ellipse cx="300" cy="150" rx="9" ry="4.5" transform="rotate(52 300 150)"/>
    <ellipse cx="150" cy="170" rx="9" ry="4.5" transform="rotate(-20 150 170)"/>
    <ellipse cx="214" cy="178" rx="9" ry="4.5" transform="rotate(14 214 178)"/>
  </g>
  <g fill="#ffd36b">
    <path d="M338 60 l4 12 12 4 -12 4 -4 12 -4 -12 -12 -4 12 -4 z"/>
    <path d="M52 110 l3 9 9 3 -9 3 -3 9 -3 -9 -9 -3 9 -3 z" opacity=".8"/>
    <path d="M356 262 l3 8 8 3 -8 3 -3 8 -3 -8 -8 -3 8 -3 z" opacity=".7"/>
  </g>
</svg></div>
        <div class="chip c1"><i>&#128293;</i><div>Fresh &amp; hot<small>made to order</small></div></div>
        <div class="chip c2"><i>&#9201;&#65039;</i><div>10 min<small>average prep</small></div></div>
        <div class="chip c3"><i>&#11088;</i><div>4.9 rating<small>customer score</small></div></div>
      </div>
    </div>

    <div class="marquee" aria-hidden="true">
      <div class="track">
        <span>Big Burger Meal</span><span>Crispy Nuggets</span><span>Golden Fries</span><span>Onion Rings</span><span>Chocolate Shake</span><span>Fresh Lemonade</span><span>Iced Coffee</span><span>Apple Pie</span>
      </div>
    </div>
  </section>

  <section class="block" id="menu">
    <div class="wrap">
      <div class="sec-head reveal">
        <div><span class="eyebrow">The menu</span><h2>What are you <span class="em">craving?</span></h2></div>
        <a class="more" href="/meals">See everything &rarr;</a>
      </div>
      <div class="bento">
        <a class="card c7 reveal" href="/meals">
          <span class="tag">Popular</span>
          <div class="art" aria-hidden="true"><b>&#127828;</b><b>&#127839;</b><b>&#127831;</b></div>
          <h3>Meals</h3>
          <p>Burgers, nuggets and crispy fries &mdash; the classics, made fresh to order.</p>
          <span class="go" aria-hidden="true">&rarr;</span>
        </a>
        <a class="card c5 reveal" style="--d:.08s" href="/beverages">
          <div class="art" aria-hidden="true"><b>&#129380;</b><b>&#127846;</b></div>
          <h3>Beverages</h3>
          <p>Cold drinks, shakes, juices and iced coffee for every bite.</p>
          <span class="go" aria-hidden="true">&rarr;</span>
        </a>
        <a class="card c5 reveal" href="/orders">
          <div class="art" aria-hidden="true"><b>&#129534;</b></div>
          <h3>My Orders</h3>
          <p>Every order is stored safely. Check your past orders and totals in one place.</p>
          <span class="go" aria-hidden="true">&rarr;</span>
        </a>
        <a class="card c7 reveal" style="--d:.08s" href="/kitchen">
          <span class="tag">Staff</span>
          <div class="art" aria-hidden="true"><b>&#127859;</b><b>&#9201;&#65039;</b></div>
          <h3>Kitchen</h3>
          <p>See new orders as they arrive, set the preparation time and follow the countdown.</p>
          <span class="go" aria-hidden="true">&rarr;</span>
        </a>
      </div>
    </div>
  </section>

  <section class="block">
    <div class="wrap">
      <div class="sec-head reveal">
        <div><span class="eyebrow">Fresh from the menu</span><h2>Popular <span class="em">right now</span></h2></div>
        <a class="more" href="/meals">Full menu &rarr;</a>
      </div>
      <div class="pop reveal" id="pop" aria-live="polite">
        <div class="pitem sk"></div><div class="pitem sk"></div><div class="pitem sk"></div><div class="pitem sk"></div>
      </div>
    </div>
  </section>

  <section class="block">
    <div class="wrap">
      <div class="sec-head reveal">
        <div><span class="eyebrow">How it works</span><h2>From hungry to <span class="em">happy</span></h2></div>
      </div>
      <div class="steps">
        <div class="step reveal"><span class="n">01</span><b>Pick a meal</b><span>Choose from our menu</span></div>
        <div class="step reveal" style="--d:.08s"><span class="n">02</span><b>Add a drink</b><span>Cold, sweet or classic</span></div>
        <div class="step reveal" style="--d:.16s"><span class="n">03</span><b>Place order</b><span>Enter your name and confirm</span></div>
        <div class="step reveal" style="--d:.24s"><span class="n">04</span><b>Enjoy</b><span>Your order is saved and on its way</span></div>
      </div>
    </div>
  </section>

  <section class="block">
    <div class="wrap">
      <div class="banner reveal">
        <div>
          <h2>Hungry <span class="em">already?</span></h2>
          <p>Your meal is only a few clicks away.</p>
        </div>
        <a class="btn" href="/meals">Start your order &rarr;</a>
      </div>
    </div>
  </section>
</main>

<footer>
  <div class="wrap">
    <div class="f-grid">
      <div>
        <a class="logo" href="/" aria-label="Quick Bites home"><span class="mark">&#127828;</span>Quick <em>Bites</em></a>
        <p>Fresh meals and cold drinks, ordered in seconds and prepared with care.</p>
      </div>
      <div><h4>Menu</h4><a href="/meals">Meals</a><a href="/beverages">Beverages</a></div>
      <div><h4>Orders</h4><a href="/orders">My Orders</a><a href="/meals">Order now</a></div>
      <div><h4>Staff</h4><a href="/kitchen">Kitchen display</a></div>
    </div>
    <div class="f-bot"><span>&copy; Quick Bites. Served fresh, built as microservices.</span><span>Made with &#10084;&#65039; and a lot of fries</span></div>
  </div>
</footer>

<script>
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = s => String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

// reveal on scroll
if (reduce || !("IntersectionObserver" in window)) {
  $$(".reveal").forEach(e => e.classList.add("in"));
} else {
  const io = new IntersectionObserver(entries => entries.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
  }), {threshold: 0.12, rootMargin: "0px 0px -40px 0px"});
  $$(".reveal").forEach(e => io.observe(e));
}

// header shadow after scrolling
const nav = document.querySelector(".nav");
const onScroll = () => nav.classList.toggle("scrolled", window.scrollY > 8);
addEventListener("scroll", onScroll, {passive: true}); onScroll();

// spotlight that follows the pointer on the cards
$$(".card").forEach(c => c.addEventListener("pointermove", e => {
  const r = c.getBoundingClientRect();
  c.style.setProperty("--mx", (e.clientX - r.left) + "px");
  c.style.setProperty("--my", (e.clientY - r.top) + "px");
}));

// endless marquee: duplicate the items once
const track = document.querySelector(".track");
if (track) track.innerHTML += track.innerHTML;

// popular items come live from the meals and beverages services
const FALLBACK = [
  {name:"Big Burger Meal", category:"Burgers", emoji:"🍔", price:7.99, href:"/meals"},
  {name:"Chicken Nuggets (9 pc)", category:"Snacks", emoji:"🍗", price:5.49, href:"/meals"},
  {name:"Chocolate Shake", category:"Shakes", emoji:"🍫", price:3.49, href:"/beverages"},
  {name:"Iced Coffee", category:"Coffee", emoji:"☕", price:2.99, href:"/beverages"}
];
const pop = document.getElementById("pop");
function paintPop(list){
  pop.innerHTML = list.map(i =>
    `<a class="pitem" href="${i.href}"><span class="pe">${esc(i.emoji)}</span><span class="pc">${esc(i.category)}</span>
      <h3>${esc(i.name)}</h3><div class="pf"><b>$${Number(i.price).toFixed(2)}</b><span>Add &rarr;</span></div></a>`).join("");
}
const grab = (url, href) => fetch(url).then(r => r.ok ? r.json() : []).then(l => l.slice(0, 2).map(x => ({...x, href}))).catch(() => []);
Promise.all([grab("/meals/api", "/meals"), grab("/beverages/api", "/beverages")])
  .then(([m, b]) => { const all = [...m, ...b]; paintPop(all.length === 4 ? all : FALLBACK); })
  .catch(() => paintPop(FALLBACK));
</script>
</body>
</html>"""


@app.route("/")
def home():
    return PAGE


@app.route("/healthz")
def healthz():
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
