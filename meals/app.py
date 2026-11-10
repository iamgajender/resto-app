from flask import Flask, jsonify

app = Flask(__name__)

# Prices are in Indian rupees (INR). "veg" drives the veg / non-veg marker and the "Veg only" filter.
MEALS = [
    {"id": 101, "name": "Big Burger Meal", "category": "Burgers", "emoji": "🍔", "price": 249, "veg": False, "tag": "Signature", "desc": "Beef patty, cheese, lettuce and our special sauce."},
    {"id": 102, "name": "Chicken Burger Meal", "category": "Burgers", "emoji": "🐔", "price": 219, "veg": False, "desc": "Crispy chicken fillet with mayo and fresh lettuce."},
    {"id": 103, "name": "Veggie Burger Meal", "category": "Burgers", "emoji": "🥬", "price": 189, "veg": True, "desc": "Garden veggie patty, tomato and a toasted bun."},
    {"id": 104, "name": "Cheese Burger", "category": "Burgers", "emoji": "🧀", "price": 149, "veg": False, "desc": "The classic: beef, melted cheese, pickles."},
    {"id": 105, "name": "Chicken Nuggets (9 pc)", "category": "Snacks", "emoji": "🍗", "price": 179, "veg": False, "desc": "Golden and crunchy, served with dipping sauce."},
    {"id": 106, "name": "Large Fries", "category": "Sides", "emoji": "🍟", "price": 99, "veg": True, "desc": "Hot, salty and crispy. Always."},
    {"id": 107, "name": "Onion Rings", "category": "Sides", "emoji": "🧅", "price": 119, "veg": True, "desc": "Thick-cut rings in a crunchy batter."},
    {"id": 108, "name": "Apple Pie", "category": "Desserts", "emoji": "🥧", "price": 79, "veg": True, "tag": "Sweet finish", "desc": "Warm pie with a flaky crust and cinnamon apples."},
]

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0b0706">
<title>Meals | Quick Bites</title>
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
  button, input { font-family:inherit; }
  a:focus-visible, button:focus-visible, input:focus-visible { outline:3px solid var(--gold); outline-offset:3px; border-radius:12px; }
  .wrap { max-width:1180px; margin:0 auto; padding:0 24px; }

  /* ambient background */
  .bg { position:fixed; inset:0; z-index:-1; overflow:hidden; pointer-events:none; }
  .orb { position:absolute; border-radius:50%; filter:blur(90px); }
  .o1 { width:560px; height:560px; left:-160px; top:-140px; background:#ff4d3d; opacity:.42; animation:drift 18s ease-in-out infinite alternate; }
  .o2 { width:520px; height:520px; right:-160px; top:160px; background:#ffb347; opacity:.28; animation:drift 22s ease-in-out infinite alternate-reverse; }
  .o3 { width:640px; height:640px; left:30%; bottom:-360px; background:#ff7a2e; opacity:.26; animation:drift 26s ease-in-out infinite alternate; }
  @keyframes drift { to { transform:translate(70px,40px) scale(1.12); } }

  /* header */
  .nav { position:sticky; top:0; z-index:50; padding:14px 20px; }
  .nav-in { position:relative; max-width:1180px; margin:0 auto; display:flex; align-items:center; justify-content:space-between; gap:16px; padding:10px 12px 10px 18px; border-radius:999px; background:var(--navbg); border:1px solid var(--line); backdrop-filter:blur(18px) saturate(1.5); -webkit-backdrop-filter:blur(18px) saturate(1.5); transition:box-shadow .3s; }
  .nav.scrolled .nav-in { box-shadow:var(--shadow); }
  .logo { display:flex; align-items:center; gap:10px; font-weight:800; font-size:20px; letter-spacing:-.02em; }
  .logo .mark { display:grid; place-items:center; width:38px; height:38px; border-radius:12px; background:var(--grad); font-size:20px; box-shadow:0 6px 18px rgba(255,100,50,.4); }
  .logo em { font-family:var(--serif); font-style:italic; font-weight:600; color:var(--gold); }
  .links { display:flex; align-items:center; gap:4px; }
  .links a.l { padding:9px 16px; border-radius:999px; font-weight:600; font-size:15px; color:var(--muted); transition:.2s; }
  .links a.l:hover, .links a.l.on { color:var(--ink); background:var(--glass-2); }
  .mt, .burger { display:none; }
  .btn { position:relative; overflow:hidden; display:inline-flex; align-items:center; justify-content:center; gap:10px; padding:12px 24px; border-radius:999px; border:1px solid transparent; font-weight:700; font-size:15px; cursor:pointer; transition:transform .2s, box-shadow .2s; }
  .btn:hover { transform:translateY(-3px); }
  .btn-primary { background:var(--grad); color:var(--on-grad); box-shadow:0 12px 30px rgba(255,100,50,.38), inset 0 1px 0 rgba(255,255,255,.45); }
  .btn-primary:hover { box-shadow:0 18px 40px rgba(255,100,50,.5), inset 0 1px 0 rgba(255,255,255,.45); }
  .btn-primary::after { content:""; position:absolute; top:0; bottom:0; width:60%; left:-80%; background:linear-gradient(100deg,transparent,rgba(255,255,255,.55),transparent); transform:skewX(-20deg); transition:left .7s; }
  .btn-primary:hover::after { left:130%; }
  .btn-sm { padding:10px 18px; }
  .badge { display:inline-grid; place-items:center; min-width:22px; height:22px; padding:0 6px; border-radius:999px; background:var(--on-grad); color:var(--gold); font-size:13px; font-weight:800; }

  /* page head */
  .hero2 { padding:54px 0 10px; }
  .eyebrow-pill { display:inline-flex; align-items:center; gap:10px; padding:8px 16px 8px 12px; border-radius:999px; background:var(--glass); border:1px solid var(--line); font-weight:600; font-size:13px; letter-spacing:.04em; backdrop-filter:blur(10px); }
  .eyebrow-pill i { width:9px; height:9px; border-radius:50%; background:var(--ok); animation:ping 2s infinite; }
  @keyframes ping { 0% { box-shadow:0 0 0 0 rgba(61,220,132,.6); } 70%,100% { box-shadow:0 0 0 10px rgba(61,220,132,0); } }
  h1 { margin:22px 0 16px; font-size:clamp(46px,8vw,104px); line-height:.94; letter-spacing:-.05em; font-weight:800; }
  h1 .em { display:inline-block; padding-right:.08em; font-family:var(--serif); font-style:italic; font-weight:600; letter-spacing:-.03em; background:var(--grad); -webkit-background-clip:text; background-clip:text; color:transparent; }
  .lead { max-width:540px; color:var(--muted); font-size:19px; }

  /* tools: search, veg switch, categories */
  .tools { display:flex; flex-wrap:wrap; align-items:center; gap:14px; margin:36px 0 18px; }
  .search { position:relative; flex:1 1 280px; max-width:420px; }
  .search svg { position:absolute; left:18px; top:50%; width:20px; height:20px; margin-top:-10px; stroke:var(--muted); fill:none; stroke-width:2; stroke-linecap:round; }
  .search input { width:100%; padding:15px 20px 15px 50px; border-radius:999px; border:1px solid var(--line); background:var(--glass); color:var(--ink); font-size:16px; backdrop-filter:blur(12px); transition:border-color .2s, box-shadow .2s; }
  .search input::placeholder { color:var(--muted); }
  .search input:focus { outline:0; border-color:var(--orange); box-shadow:0 0 0 4px rgba(255,138,61,.18); }
  .switch { display:inline-flex; align-items:center; gap:12px; padding:9px 18px 9px 10px; border-radius:999px; border:1px solid var(--line); background:var(--glass); font-weight:600; font-size:15px; cursor:pointer; user-select:none; backdrop-filter:blur(12px); }
  .switch input { position:absolute; opacity:0; pointer-events:none; }
  .knob { position:relative; width:46px; height:26px; border-radius:999px; background:var(--glass-2); border:1px solid var(--line); transition:background .3s; }
  .knob::after { content:""; position:absolute; top:2px; left:2px; width:20px; height:20px; border-radius:50%; background:var(--ink); transition:transform .3s cubic-bezier(.2,.9,.3,1.3); }
  .switch input:checked + .knob { background:#1fa855; border-color:#1fa855; }
  .switch input:checked + .knob::after { transform:translateX(20px); background:#fff; }
  .switch input:focus-visible + .knob { outline:3px solid var(--gold); outline-offset:3px; }
  .vm { display:inline-grid; place-items:center; width:18px; height:18px; border-radius:4px; border:2px solid; background:#fff; flex:none; }
  .vm::after { content:""; width:8px; height:8px; border-radius:50%; background:currentColor; }
  .vm.v { color:#1fa855; border-color:#1fa855; } .vm.n { color:#e23744; border-color:#e23744; }

  .seg { max-width:100%; overflow-x:auto; padding:6px; border-radius:999px; border:1px solid var(--line); background:var(--glass); backdrop-filter:blur(12px); display:inline-block; scrollbar-width:none; }
  .seg::-webkit-scrollbar { display:none; }
  #chips { position:relative; display:flex; gap:4px; }
  .ind { position:absolute; top:0; bottom:0; left:0; width:0; border-radius:999px; background:var(--grad); box-shadow:0 8px 22px rgba(255,100,50,.35); transition:transform .4s cubic-bezier(.3,.9,.3,1.1), width .4s cubic-bezier(.3,.9,.3,1.1); }
  .chip { position:relative; z-index:1; padding:11px 22px; border:0; border-radius:999px; background:transparent; color:var(--muted); font-weight:700; font-size:15px; cursor:pointer; white-space:nowrap; transition:color .25s; }
  .chip:hover { color:var(--ink); }
  .chip.on { color:var(--on-grad); }
  .count { min-height:24px; margin:20px 2px 18px; color:var(--muted); font-size:14px; font-weight:600; letter-spacing:.04em; }

  /* dish cards */
  .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:22px; padding-bottom:150px; }
  .dish { position:relative; overflow:hidden; display:flex; flex-direction:column; border-radius:var(--r); background:var(--glass); border:1px solid var(--line); backdrop-filter:blur(12px); -webkit-backdrop-filter:blur(12px);
    transform:perspective(900px) rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg)); transition:transform .25s ease-out, box-shadow .3s; animation:rise .8s cubic-bezier(.2,.7,.2,1) backwards; animation-delay:calc(var(--i,0) * 70ms); }
  @keyframes rise { from { opacity:0; transform:translateY(34px) scale(.97); } }
  .dish:hover { transform:perspective(900px) rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg)) translateY(-8px); box-shadow:var(--shadow); }
  .dish::before { content:""; position:absolute; inset:0; z-index:0; background:radial-gradient(420px circle at var(--mx,50%) var(--my,0%),rgba(255,138,61,.26),transparent 60%); opacity:0; transition:opacity .3s; pointer-events:none; }
  .dish::after { content:""; position:absolute; inset:0; border-radius:inherit; padding:1.5px; background:var(--grad); -webkit-mask:linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0); -webkit-mask-composite:xor; mask:linear-gradient(#000 0 0) content-box exclude, linear-gradient(#000 0 0); opacity:0; transition:opacity .3s; pointer-events:none; }
  .dish:hover::before, .dish:hover::after { opacity:1; }
  .media { position:relative; z-index:1; display:grid; place-items:center; height:200px; background:radial-gradient(circle at 50% 60%,rgba(255,200,87,.22),rgba(255,77,61,.06) 60%,transparent 80%); }
  .halo { position:absolute; width:150px; height:150px; border-radius:50%; border:1px dashed rgba(255,200,87,.35); animation:spin 24s linear infinite; }
  @keyframes spin { to { transform:rotate(360deg); } }
  .emoji { position:relative; font-size:92px; line-height:1; filter:drop-shadow(0 18px 18px rgba(0,0,0,.4)); transition:transform .5s cubic-bezier(.2,.9,.3,1.3); }
  .dish:hover .emoji { transform:scale(1.14) rotate(-6deg) translateY(-4px); }
  .media .vm { position:absolute; top:18px; left:18px; }
  .tagb { position:absolute; top:16px; right:16px; padding:5px 12px; border-radius:999px; background:var(--grad); color:var(--on-grad); font-size:11px; font-weight:800; letter-spacing:.08em; text-transform:uppercase; }
  .body { position:relative; z-index:1; display:flex; flex-direction:column; gap:6px; padding:6px 24px 24px; flex:1; }
  .cat { font-size:12px; font-weight:800; letter-spacing:.14em; text-transform:uppercase; color:var(--orange); }
  .dish h3 { font-size:23px; letter-spacing:-.03em; line-height:1.15; }
  .dish p { color:var(--muted); font-size:15px; flex:1; }
  .foot { display:flex; align-items:center; justify-content:space-between; gap:10px; margin-top:16px; min-height:48px; }
  .price { font-family:var(--serif); font-weight:600; font-size:32px; letter-spacing:-.02em; }
  .add { padding:11px 22px; }
  .stepper { display:inline-flex; align-items:center; gap:14px; padding:5px; border-radius:999px; background:var(--glass-2); border:1px solid var(--line); }
  .stepper button { width:38px; height:38px; border-radius:50%; border:0; background:var(--grad); color:var(--on-grad); font-size:20px; font-weight:800; cursor:pointer; line-height:1; transition:transform .15s; }
  .stepper button:active { transform:scale(.88); }
  .stepper b { min-width:20px; text-align:center; font-size:17px; }
  .skeleton { height:420px; border-radius:var(--r); background:linear-gradient(90deg,var(--glass),var(--glass-2),var(--glass)); background-size:200% 100%; animation:sh 1.3s linear infinite; }
  @keyframes sh { to { background-position:-200% 0; } }
  .errorbox, .empty { grid-column:1/-1; padding:44px 24px; border-radius:var(--r); border:1px dashed var(--line); background:var(--glass); text-align:center; }
  .errorbox { border-color:var(--red); color:var(--red); font-weight:700; }
  .empty b { display:block; font-size:22px; margin-bottom:6px; }
  .empty span { color:var(--muted); }

  /* floating cart bar */
  .cartbar { position:fixed; left:50%; bottom:22px; z-index:60; width:min(640px,calc(100% - 28px)); display:flex; align-items:center; justify-content:space-between; gap:14px; padding:12px 12px 12px 18px; border-radius:999px; background:rgba(20,12,9,.84); color:#fff; border:1px solid rgba(255,255,255,.14); backdrop-filter:blur(22px) saturate(1.4); -webkit-backdrop-filter:blur(22px) saturate(1.4); box-shadow:0 24px 60px rgba(0,0,0,.5); transform:translate(-50%,180%); transition:transform .5s cubic-bezier(.2,.9,.3,1.15); }
  .cartbar.show { transform:translate(-50%,0); }
  .cb-l { display:flex; align-items:center; gap:14px; }
  .cb-n { display:grid; place-items:center; min-width:44px; height:44px; padding:0 8px; border-radius:50%; background:var(--grad); color:var(--on-grad); font-weight:800; font-size:18px; }
  .cb-n.bump { animation:bump .45s cubic-bezier(.2,.9,.3,1.5); }
  @keyframes bump { 40% { transform:scale(1.28); } }
  .cb-t small { display:block; color:rgba(255,255,255,.66); font-size:12px; letter-spacing:.04em; }
  .cb-t b { font-family:var(--serif); font-size:24px; font-weight:600; letter-spacing:-.01em; }
  .cartbar a.go { display:inline-flex; align-items:center; gap:8px; padding:14px 26px; border-radius:999px; background:var(--grad); color:var(--on-grad); font-weight:800; transition:transform .2s; }
  .cartbar a.go:hover { transform:translateX(3px); }

  footer { border-top:1px solid var(--line); padding:34px 0 46px; color:var(--muted); font-size:14px; }
  footer .wrap { display:flex; justify-content:space-between; flex-wrap:wrap; gap:12px; }
  footer a:hover { color:var(--gold); }

  @media (max-width:760px) {
    .nav { padding:10px 12px; }
    .burger { display:grid; place-items:center; width:42px; height:42px; border-radius:50%; border:1px solid var(--line); background:var(--glass); cursor:pointer; font-size:19px; }
    .links { position:absolute; top:62px; left:0; right:0; flex-direction:column; align-items:stretch; gap:4px; padding:14px; border-radius:26px; background:var(--navbg); border:1px solid var(--line); backdrop-filter:blur(22px); -webkit-backdrop-filter:blur(22px); box-shadow:var(--shadow); display:none; }
    .mt:checked ~ .links { display:flex; }
    .links a.l { text-align:center; }
    .btn-sm { justify-content:center; }
  }
  @media (max-width:520px) {
    .grid { grid-template-columns:1fr; }
    .search { max-width:none; }
    .cb-t b { font-size:21px; }
    .cartbar a.go { padding:13px 20px; }
  }
  @media (prefers-reduced-motion:reduce) {
    *, *::before, *::after { animation:none !important; transition:none !important; }
    html { scroll-behavior:auto; }
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
      <a class="l on" href="/meals">Meals</a>
      <a class="l" href="/beverages">Beverages</a>
      <a class="l" href="/orders">My Orders</a>
      <a class="btn btn-primary btn-sm" href="/orders">&#128722; Cart <span class="badge cartCount">0</span></a>
    </nav>
  </div>
</header>

<main class="wrap">
  <section class="hero2">
    <span class="eyebrow-pill"><i></i>Fresh off the grill &middot; cooked to order</span>
    <h1>Our <span class="em">Meals</span></h1>
    <p class="lead">Burgers, nuggets, fries and more. Tap add and we will keep your cart ready for checkout.</p>
  </section>

  <div class="tools">
    <label class="search">
      <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
      <input type="search" id="q" placeholder="Search burgers, fries, desserts..." autocomplete="off" aria-label="Search meals">
    </label>
    <label class="switch"><input type="checkbox" id="veg"><span class="knob"></span><span class="vm v" aria-hidden="true"></span>Veg only</label>
  </div>

  <div class="seg"><div id="chips" aria-label="Categories"><i class="ind" id="ind"></i></div></div>
  <div class="count" id="count" aria-live="polite"></div>
  <div class="grid" id="grid"></div>
</main>

<div class="cartbar" id="cartbar" role="status">
  <div class="cb-l">
    <span class="cb-n" id="cbN">0</span>
    <div class="cb-t"><small id="cbL">0 items</small><b id="cbT">&#8377;0</b></div>
  </div>
  <a class="go" href="/orders">Checkout &rarr;</a>
</div>

<footer>
  <div class="wrap">
    <span>&copy; Quick Bites. Served fresh, built as microservices.</span>
    <span><a href="/">Home</a> &middot; <a href="/meals">Meals</a> &middot; <a href="/beverages">Beverages</a> &middot; <a href="/orders">Orders</a></span>
  </div>
</footer>

<script>
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const KEY = "qb_cart";
const inr = n => new Intl.NumberFormat("en-IN", {style: "currency", currency: "INR", minimumFractionDigits: 0, maximumFractionDigits: 2}).format(Number(n));
const esc = s => String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

/* ---------- cart (shared with the beverages and orders pages) ---------- */
function getCart(){ try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) { return []; } }
function setCart(c){ try { localStorage.setItem(KEY, JSON.stringify(c)); } catch (e) {} paintCart(); }
function cartQty(id){ const i = getCart().find(x => x.id === id); return i ? i.qty : 0; }
function changeQty(item, d){
  const c = getCart(); const i = c.find(x => x.id === item.id);
  if (i) { i.qty += d; if (i.qty <= 0) c.splice(c.indexOf(i), 1); }
  else if (d > 0) { c.push({id: item.id, name: item.name, price: item.price, emoji: item.emoji, qty: 1}); }
  setCart(c);
}
let lastN = -1;
function paintCart(){
  const c = getCart();
  const n = c.reduce((s, x) => s + x.qty, 0), t = c.reduce((s, x) => s + x.qty * x.price, 0);
  $$(".cartCount").forEach(e => e.textContent = n);
  $("#cartbar").classList.toggle("show", n > 0);
  $("#cbL").textContent = n === 1 ? "1 item" : n + " items";
  $("#cbT").textContent = inr(t);
  const nb = $("#cbN"); nb.textContent = n;
  if (lastN !== -1 && n !== lastN) { nb.classList.remove("bump"); void nb.offsetWidth; nb.classList.add("bump"); }
  lastN = n;
  refreshCtls();
}
// prices may have changed since the cart was saved: refresh them from the menu
function syncCart(){
  const c = getCart(); let changed = false;
  c.forEach(ci => {
    const m = items.find(x => x.id === ci.id);
    if (m && (m.price !== ci.price || m.name !== ci.name || m.emoji !== ci.emoji)) { ci.price = m.price; ci.name = m.name; ci.emoji = m.emoji; changed = true; }
  });
  if (changed) setCart(c);
}

/* ---------- menu ---------- */
const grid = $("#grid"), chips = $("#chips"), ind = $("#ind"), count = $("#count");
let items = [], cat = "All", vegOnly = false, term = "";

function ctlHtml(id, q){
  return q
    ? `<span class="stepper"><button data-act="dec" data-id="${id}" aria-label="Remove one">&minus;</button><b>${q}</b><button data-act="inc" data-id="${id}" aria-label="Add one">+</button></span>`
    : `<button class="btn btn-primary add" data-act="inc" data-id="${id}">+ Add</button>`;
}
function refreshCtls(){
  $$(".ctl").forEach(el => {
    const id = Number(el.dataset.id), q = cartQty(id);
    if (el.dataset.q !== String(q)) { el.dataset.q = q; el.innerHTML = ctlHtml(id, q); }
  });
}
function card(i, n){
  const q = cartQty(i.id);
  return `<article class="dish" style="--i:${n}">
    <div class="media"><span class="vm ${i.veg ? "v" : "n"}" title="${i.veg ? "Vegetarian" : "Non-vegetarian"}"></span>${i.tag ? `<span class="tagb">${esc(i.tag)}</span>` : ""}<div class="halo"></div><div class="emoji">${esc(i.emoji)}</div></div>
    <div class="body"><span class="cat">${esc(i.category)}</span><h3>${esc(i.name)}</h3><p>${esc(i.desc)}</p>
      <div class="foot"><div class="price">${inr(i.price)}</div><div class="ctl" data-id="${i.id}" data-q="${q}">${ctlHtml(i.id, q)}</div></div></div></article>`;
}
function renderGrid(){
  const list = items.filter(i =>
    (cat === "All" || i.category === cat) && (!vegOnly || i.veg) &&
    (!term || (i.name + " " + i.desc + " " + i.category).toLowerCase().includes(term)));
  count.textContent = list.length ? `Showing ${list.length} of ${items.length} dishes` : "";
  grid.innerHTML = list.length ? list.map(card).join("")
    : '<div class="empty"><b>No dishes found</b><span>Try another category or clear the search.</span></div>';
}
function moveInd(){
  const b = $(".chip.on", chips); if (!b) return;
  ind.style.width = b.offsetWidth + "px";
  ind.style.transform = `translateX(${b.offsetLeft}px)`;
}
function buildChips(){
  $$(".chip", chips).forEach(e => e.remove());
  const cats = ["All", ...new Set(items.map(i => i.category))];
  chips.insertAdjacentHTML("beforeend", cats.map(c => `<button class="chip ${c === cat ? "on" : ""}" data-cat="${esc(c)}">${esc(c)}</button>`).join(""));
  moveInd();
}

grid.addEventListener("click", e => {
  const b = e.target.closest("button[data-act]"); if (!b) return;
  const item = items.find(x => String(x.id) === b.dataset.id);
  if (item) changeQty(item, b.dataset.act === "inc" ? 1 : -1);
});
chips.addEventListener("click", e => {
  const b = e.target.closest("button[data-cat]"); if (!b) return;
  cat = b.dataset.cat;
  $$(".chip", chips).forEach(x => x.classList.toggle("on", x === b));
  moveInd(); renderGrid();
});
$("#q").addEventListener("input", e => { term = e.target.value.trim().toLowerCase(); renderGrid(); });
$("#veg").addEventListener("change", e => { vegOnly = e.target.checked; renderGrid(); });
addEventListener("resize", moveInd);

/* 3D tilt + moving spotlight on the cards (mouse devices only) */
if (matchMedia("(hover: hover)").matches && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
  grid.addEventListener("pointermove", e => {
    const d = e.target.closest(".dish"); if (!d) return;
    const r = d.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top;
    d.style.setProperty("--mx", x + "px"); d.style.setProperty("--my", y + "px");
    d.style.setProperty("--ry", ((x / r.width - 0.5) * 9) + "deg");
    d.style.setProperty("--rx", ((0.5 - y / r.height) * 9) + "deg");
  });
  grid.addEventListener("pointerout", e => {
    const d = e.target.closest(".dish");
    if (d && !d.contains(e.relatedTarget)) { d.style.setProperty("--rx", "0deg"); d.style.setProperty("--ry", "0deg"); }
  });
}

/* header shadow after scrolling */
const nav = $(".nav");
const onScroll = () => nav.classList.toggle("scrolled", window.scrollY > 8);
addEventListener("scroll", onScroll, {passive: true}); onScroll();

grid.innerHTML = '<div class="skeleton"></div>'.repeat(6);
fetch("/meals/api").then(r => { if (!r.ok) throw 0; return r.json(); })
  .then(d => { items = d; buildChips(); renderGrid(); syncCart(); })
  .catch(() => { grid.innerHTML = '<div class="errorbox">The Meals service is not available right now. Please try again in a moment.</div>'; });
paintCart();
</script>
</body>
</html>"""


@app.route("/meals", strict_slashes=False)
def page():
    return PAGE


@app.route("/meals/api")
def api():
    return jsonify(MEALS)


@app.route("/healthz")
def healthz():
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
