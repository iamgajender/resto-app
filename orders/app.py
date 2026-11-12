import json
import os
import threading
import urllib.request
import uuid
from contextlib import closing
from datetime import datetime, timezone

import psycopg2
from psycopg2.extras import Json
from flask import Flask, jsonify, request

app = Flask(__name__)

# ---- configuration (set these as env vars / Kubernetes Secret + ConfigMap) ----
DB = dict(
    host=os.getenv("DB_HOST", "postgres"),
    port=os.getenv("DB_PORT", "5432"),
    dbname=os.getenv("DB_NAME", "restaurant"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "postgres"),
)
# The orders service asks the other services for the real prices
MEALS_URL = os.getenv("MEALS_URL", "http://meals-service:5000/meals/api")
BEVERAGES_URL = os.getenv("BEVERAGES_URL", "http://beverages-service:5000/beverages/api")
KAFKA_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "192.168.1.213:9092,192.168.1.139:9092,192.168.1.133:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "orders")

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0b0706">
<title>My Orders | Quick Bites</title>
<style>
  :root {
    color-scheme: dark light;
    --bg:#0b0706; --ink:#fff4e8; --muted:#b9a79b;
    --glass:rgba(255,255,255,.05); --glass-2:rgba(255,255,255,.08); --line:rgba(255,255,255,.1);
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
      --navbg:rgba(255,250,242,.74); --shadow:0 30px 70px rgba(160,90,30,.2); --ok:#14a34f;
    }
    .orb { opacity:.25 !important; }
    .st { color:#b45309 !important; } .st-completed, .st-ready { color:#0f8a4b !important; }
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
  .btn { position:relative; overflow:hidden; display:inline-flex; align-items:center; justify-content:center; gap:10px; padding:12px 24px; border-radius:999px; border:1px solid transparent; font-weight:700; font-size:15px; cursor:pointer; transition:transform .2s, box-shadow .2s, opacity .2s; }
  .btn:hover { transform:translateY(-3px); }
  .btn:disabled { opacity:.45; cursor:not-allowed; transform:none; box-shadow:none; }
  .btn-primary { background:var(--grad); color:var(--on-grad); box-shadow:0 12px 30px rgba(255,100,50,.38), inset 0 1px 0 rgba(255,255,255,.45); }
  .btn-primary:not(:disabled):hover { box-shadow:0 18px 40px rgba(255,100,50,.5), inset 0 1px 0 rgba(255,255,255,.45); }
  .btn-primary::after { content:""; position:absolute; top:0; bottom:0; width:60%; left:-80%; background:linear-gradient(100deg,transparent,rgba(255,255,255,.55),transparent); transform:skewX(-20deg); transition:left .7s; }
  .btn-primary:not(:disabled):hover::after { left:130%; }
  .btn-glass { background:var(--glass); border-color:var(--line); color:var(--ink); backdrop-filter:blur(12px); }
  .btn-glass:hover { background:var(--glass-2); }
  .btn-sm { padding:10px 18px; }
  .badge { display:inline-grid; place-items:center; min-width:22px; height:22px; padding:0 6px; border-radius:999px; background:var(--on-grad); color:var(--gold); font-size:13px; font-weight:800; }

  /* page head */
  .hero2 { padding:54px 0 6px; }
  .eyebrow-pill { display:inline-flex; align-items:center; gap:10px; padding:8px 16px 8px 12px; border-radius:999px; background:var(--glass); border:1px solid var(--line); font-weight:600; font-size:13px; letter-spacing:.04em; backdrop-filter:blur(10px); }
  .eyebrow-pill i { width:9px; height:9px; border-radius:50%; background:var(--ok); animation:ping 2s infinite; }
  @keyframes ping { 0% { box-shadow:0 0 0 0 rgba(61,220,132,.6); } 70%,100% { box-shadow:0 0 0 10px rgba(61,220,132,0); } }
  h1 { margin:22px 0 16px; font-size:clamp(46px,8vw,104px); line-height:.94; letter-spacing:-.05em; font-weight:800; }
  h1 .em { display:inline-block; padding-right:.08em; font-family:var(--serif); font-style:italic; font-weight:600; letter-spacing:-.03em; background:var(--grad); -webkit-background-clip:text; background-clip:text; color:transparent; }
  .lead { max-width:540px; color:var(--muted); font-size:19px; }

  /* layout */
  .cols { display:grid; grid-template-columns:1fr 1.12fr; gap:24px; padding:34px 0 90px; align-items:start; }
  .panel { position:relative; border-radius:var(--r); background:var(--glass); border:1px solid var(--line); backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px); padding:28px; }
  .cart-panel { position:sticky; top:96px; }
  .panel h2 { display:flex; align-items:baseline; justify-content:space-between; gap:10px; margin-bottom:16px; font-size:26px; letter-spacing:-.03em; }
  .panel h2 small { font-size:13px; font-weight:700; letter-spacing:.04em; color:var(--muted); }

  /* cart lines */
  .line { display:grid; grid-template-columns:56px 1fr auto; gap:14px; align-items:center; padding:14px 0; border-bottom:1px solid var(--line); animation:pop .45s cubic-bezier(.2,.9,.3,1.2); }
  .line .e { display:grid; place-items:center; width:56px; height:56px; border-radius:18px; font-size:30px; background:radial-gradient(circle at 30% 25%,rgba(255,200,87,.3),rgba(255,77,61,.1)); }
  .line .n b { display:block; font-size:16px; line-height:1.25; }
  .line .n small { color:var(--muted); font-size:13px; }
  .line .gone { display:block; margin-top:2px; color:var(--red); font-size:12px; font-weight:700; }
  .line .r { display:flex; flex-direction:column; align-items:flex-end; gap:8px; }
  .line .sub { font-family:var(--serif); font-weight:600; font-size:20px; }
  .stepper { display:inline-flex; align-items:center; gap:12px; padding:4px; border-radius:999px; background:var(--glass-2); border:1px solid var(--line); }
  .stepper button { width:30px; height:30px; border-radius:50%; border:0; background:var(--grad); color:var(--on-grad); font-size:17px; font-weight:800; cursor:pointer; line-height:1; transition:transform .15s, opacity .2s; }
  .stepper button:active { transform:scale(.88); }
  .stepper button:disabled { opacity:.35; cursor:not-allowed; }
  .stepper b { min-width:18px; text-align:center; font-size:15px; }
  .emptycart { padding:30px 10px 14px; text-align:center; }
  .emptycart .big { font-size:64px; line-height:1; filter:drop-shadow(0 14px 14px rgba(0,0,0,.35)); }
  .emptycart p { margin:10px 0 18px; color:var(--muted); }
  .emptycart .row { display:flex; flex-wrap:wrap; justify-content:center; gap:10px; }

  .sum { margin-top:14px; }
  .sum-row { display:flex; justify-content:space-between; color:var(--muted); font-size:15px; }
  .sum-total { display:flex; justify-content:space-between; align-items:baseline; margin-top:10px; padding-top:14px; border-top:1px dashed var(--line); }
  .sum-total span { font-weight:700; }
  .sum-total b { font-family:var(--serif); font-size:42px; font-weight:600; letter-spacing:-.02em; line-height:1; }
  label.fl { display:block; margin:22px 0 8px; font-size:12px; font-weight:800; letter-spacing:.14em; text-transform:uppercase; color:var(--muted); }
  input[type=text] { width:100%; padding:15px 18px; border-radius:16px; border:1px solid var(--line); background:var(--glass); color:var(--ink); font-size:16px; transition:border-color .2s, box-shadow .2s; }
  input[type=text]::placeholder { color:var(--muted); }
  input[type=text]:focus { outline:0; border-color:var(--orange); box-shadow:0 0 0 4px rgba(255,138,61,.18); }
  .btn-place { width:100%; margin-top:18px; padding:18px 24px; font-size:17px; }
  .btn.busy::before { content:""; width:16px; height:16px; border:2px solid currentColor; border-right-color:transparent; border-radius:50%; animation:spin .7s linear infinite; }
  @keyframes spin { to { transform:rotate(360deg); } }
  #result { margin-top:16px; }
  .res { display:flex; align-items:center; gap:14px; padding:16px 18px; border-radius:20px; animation:pop .5s cubic-bezier(.2,.9,.3,1.3); }
  @keyframes pop { from { opacity:0; transform:scale(.94) translateY(8px); } }
  .res.ok { background:color-mix(in srgb, var(--ok) 14%, transparent); border:1px solid color-mix(in srgb, var(--ok) 40%, transparent); }
  .res.bad { background:color-mix(in srgb, var(--red) 12%, transparent); border:1px solid color-mix(in srgb, var(--red) 40%, transparent); color:var(--red); font-weight:700; }
  .res .tick { display:grid; place-items:center; flex:none; width:44px; height:44px; border-radius:50%; background:var(--ok); color:#06210f; font-size:22px; font-weight:800; }
  .res b { display:block; font-size:18px; }
  .res small { color:var(--muted); font-size:14px; }

  /* order history */
  .olist { display:flex; flex-direction:column; gap:12px; max-height:700px; overflow-y:auto; padding-right:6px; scrollbar-width:thin; }
  .ord { padding:18px 20px; border-radius:22px; background:var(--glass-2); border:1px solid var(--line); transition:transform .25s, border-color .25s; }
  .ord:hover { transform:translateY(-3px); border-color:rgba(255,160,80,.5); }
  .ord.new { animation:pop .6s cubic-bezier(.2,.9,.3,1.3); }
  .oh { display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
  .oid { font-family:var(--serif); font-size:24px; font-weight:600; }
  .st { padding:4px 12px; border-radius:999px; font-size:11px; font-weight:800; letter-spacing:.1em; text-transform:uppercase; background:rgba(255,200,87,.18); color:var(--gold); }
  .st-preparing { background:rgba(255,138,61,.2); color:var(--orange); }
  .st-completed, .st-ready { background:rgba(61,220,132,.18); color:var(--ok); }
  .oh time { margin-left:auto; color:var(--muted); font-size:13px; }
  .oc { margin:4px 0 10px; color:var(--muted); font-weight:600; overflow-wrap:anywhere; }
  .oi { display:flex; flex-wrap:wrap; gap:6px; }
  .oi span { padding:5px 12px; border-radius:999px; background:var(--glass); border:1px solid var(--line); font-size:13px; font-weight:600; }
  .ot { margin-top:12px; text-align:right; font-family:var(--serif); font-size:26px; font-weight:600; }
  .noord { padding:44px 16px; text-align:center; color:var(--muted); border:2px dashed var(--line); border-radius:22px; }
  .noord.bad { color:var(--red); border-color:var(--red); font-weight:700; }

  .confetti { position:fixed; z-index:100; width:0; height:0; pointer-events:none; }
  .confetti i { position:absolute; width:9px; height:14px; border-radius:3px; background:var(--c); animation:burst 1.1s cubic-bezier(.1,.7,.2,1) forwards; }
  @keyframes burst { from { transform:translate(0,0) rotate(0); opacity:1; } to { transform:translate(var(--x),var(--y)) rotate(var(--r)); opacity:0; } }

  footer { border-top:1px solid var(--line); padding:34px 0 46px; color:var(--muted); font-size:14px; }
  footer .wrap { display:flex; justify-content:space-between; flex-wrap:wrap; gap:12px; }
  footer a:hover { color:var(--gold); }

  @media (max-width:980px) { .cols { grid-template-columns:1fr; } .cart-panel { position:static; } }
  @media (max-width:760px) {
    .nav { padding:10px 12px; }
    .burger { display:grid; place-items:center; width:42px; height:42px; border-radius:50%; border:1px solid var(--line); background:var(--glass); cursor:pointer; font-size:19px; }
    .links { position:absolute; top:62px; left:0; right:0; flex-direction:column; align-items:stretch; gap:4px; padding:14px; border-radius:26px; background:var(--navbg); border:1px solid var(--line); backdrop-filter:blur(22px); -webkit-backdrop-filter:blur(22px); box-shadow:var(--shadow); display:none; }
    .mt:checked ~ .links { display:flex; }
    .links a.l { text-align:center; }
    .btn-sm { justify-content:center; }
  }
  @media (max-width:520px) { .panel { padding:22px 18px; } .line { grid-template-columns:48px 1fr auto; gap:10px; } .line .e { width:48px; height:48px; font-size:26px; } }
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
      <a class="l" href="/meals">Meals</a>
      <a class="l" href="/beverages">Beverages</a>
      <a class="l on" href="/orders">My Orders</a>
      <a class="btn btn-primary btn-sm" href="/orders">&#128722; Cart <span class="badge cartCount">0</span></a>
    </nav>
  </div>
</header>

<main class="wrap">
  <section class="hero2">
    <span class="eyebrow-pill"><i></i>Checkout &middot; review and place your order</span>
    <h1>Your <span class="em">order</span></h1>
    <p class="lead">Review your cart and place the order. Every order is saved in our database.</p>
  </section>

  <div class="cols">
    <section class="panel cart-panel" aria-labelledby="ch">
      <h2 id="ch">Your cart <small id="cItems">0 items</small></h2>
      <div id="cartList"></div>
      <div class="sum">
        <div class="sum-row"><span>Items</span><span id="sItems">0</span></div>
        <div class="sum-total"><span>Total</span><b id="total">&#8377;0</b></div>
      </div>
      <label class="fl" for="name">Your name</label>
      <input type="text" id="name" maxlength="60" placeholder="e.g. Gajender" autocomplete="name">
      <button class="btn btn-primary btn-place" id="placeBtn" disabled>Place order</button>
      <div id="result" role="status" aria-live="polite"></div>
    </section>

    <section class="panel" aria-labelledby="oh2">
      <h2 id="oh2">Recent orders <small id="oCount"></small></h2>
      <div class="olist" id="olist"><div class="noord">Loading orders...</div></div>
    </section>
  </div>
</main>

<footer>
  <div class="wrap">
    <span>&copy; Quick Bites. Served fresh, built as microservices.</span>
    <span><a href="/">Home</a> &middot; <a href="/meals">Meals</a> &middot; <a href="/beverages">Beverages</a> &middot; <a href="/orders">Orders</a></span>
  </div>
</footer>

<script>
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const KEY = "qb_cart", NAME_KEY = "qb_name", MAX_QTY = 20;
const inr = n => new Intl.NumberFormat("en-IN", {style: "currency", currency: "INR", minimumFractionDigits: 0, maximumFractionDigits: 2}).format(Number(n));
const esc = s => String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

/* ---------- cart (shared with the meals and beverages pages) ---------- */
function getCart(){ try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) { return []; } }
function setCart(c){ try { localStorage.setItem(KEY, JSON.stringify(c)); } catch (e) {} paintCart(); }
function changeQty(item, d){
  const c = getCart(), i = c.find(x => x.id === item.id);
  if (!i) return;
  i.qty = Math.min(MAX_QTY, i.qty + d);
  if (i.qty <= 0) c.splice(c.indexOf(i), 1);
  setCart(c);
}

const cartList = $("#cartList"), placeBtn = $("#placeBtn"), nameEl = $("#name"), result = $("#result");
let busy = false;
const gone = new Set();          // cart items that are no longer on the menu

function lineHtml(i){
  const missing = gone.has(i.id);
  return `<div class="line"><span class="e">${esc(i.emoji || "")}</span>
    <div class="n"><b>${esc(i.name)}</b><small>${inr(i.price)} each</small>${missing ? '<span class="gone">No longer on the menu. Remove it to continue.</span>' : ""}</div>
    <div class="r"><span class="stepper"><button data-act="dec" data-id="${i.id}" aria-label="Remove one">&minus;</button><b>${i.qty}</b><button data-act="inc" data-id="${i.id}" aria-label="Add one" ${i.qty >= MAX_QTY ? "disabled" : ""}>+</button></span>
    <span class="sub">${inr(i.price * i.qty)}</span></div></div>`;
}
function paintCart(){
  const c = getCart();
  const n = c.reduce((s, x) => s + x.qty, 0), t = c.reduce((s, x) => s + x.qty * x.price, 0);
  $$(".cartCount").forEach(e => e.textContent = n);
  cartList.innerHTML = c.length ? c.map(lineHtml).join("")
    : '<div class="emptycart"><div class="big">&#128722;</div><p>Your cart is empty. Add something tasty first.</p><div class="row"><a class="btn btn-primary btn-sm" href="/meals">Browse meals</a><a class="btn btn-glass btn-sm" href="/beverages">Explore drinks</a></div></div>';
  $("#cItems").textContent = n === 1 ? "1 item" : n + " items";
  $("#sItems").textContent = n;
  $("#total").textContent = inr(t);
  placeBtn.disabled = busy || !c.length || c.some(i => gone.has(i.id));
}
cartList.addEventListener("click", e => {
  const b = e.target.closest("button[data-act]"); if (!b) return;
  const item = getCart().find(x => String(x.id) === b.dataset.id);
  if (item) changeQty(item, b.dataset.act === "inc" ? 1 : -1);
});

// refresh names and prices of the cart items from the menu services
async function syncCart(){
  try {
    const grab = u => fetch(u).then(r => r.ok ? r.json() : []).catch(() => []);
    const [m, b] = await Promise.all([grab("/meals/api"), grab("/beverages/api")]);
    const menu = [...m, ...b];
    if (!menu.length) return;
    const c = getCart(); let changed = false;
    c.forEach(ci => {
      const mi = menu.find(x => x.id === ci.id);
      if (mi && (mi.price !== ci.price || mi.name !== ci.name || mi.emoji !== ci.emoji)) { ci.price = mi.price; ci.name = mi.name; ci.emoji = mi.emoji; changed = true; }
      if (!mi && m.length && b.length) gone.add(ci.id);         // only when both menus answered
    });
    if (changed) setCart(c); else paintCart();
  } catch (e) {}
}

/* ---------- placing an order ---------- */
function showOk(d){
  const note = d.kafka_status === "PUBLISHED" ? "The kitchen has been notified and will start preparing it."
    : d.kafka_status === "PENDING" ? "Your order is saved. The kitchen notification is delayed, we will pick it up shortly."
    : "Your order is saved.";
  result.innerHTML = `<div class="res ok"><span class="tick">&#10003;</span><div><b>Order #${esc(d.order_id)} placed</b><small>${inr(d.total)} &middot; ${note}</small></div></div>`;
}
function showBad(msg){ result.innerHTML = `<div class="res bad">${esc(msg)}</div>`; }
function confetti(){
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const r = placeBtn.getBoundingClientRect(), box = document.createElement("div");
  box.className = "confetti"; box.style.left = (r.left + r.width / 2) + "px"; box.style.top = (r.top + r.height / 2) + "px";
  const cols = ["#ff4d3d", "#ff8a3d", "#ffc857", "#3ddc84", "#fff4e8"];
  for (let k = 0; k < 26; k++) {
    const p = document.createElement("i"), a = Math.random() * Math.PI * 2, d = 90 + Math.random() * 150;
    p.style.cssText = `--c:${cols[k % 5]};--x:${Math.cos(a) * d}px;--y:${Math.sin(a) * d - 40}px;--r:${Math.random() * 720 - 360}deg;animation-delay:${Math.random() * 0.1}s`;
    box.appendChild(p);
  }
  document.body.appendChild(box); setTimeout(() => box.remove(), 1400);
}
placeBtn.addEventListener("click", async () => {
  if (busy) return;
  busy = true; placeBtn.classList.add("busy"); placeBtn.disabled = true; placeBtn.textContent = "Placing order...";
  result.innerHTML = "";
  const name = nameEl.value.trim();
  try { localStorage.setItem(NAME_KEY, name); } catch (e) {}
  try {
    const r = await fetch("/orders/api", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({customer_name: name, items: getCart().map(i => ({id: i.id, qty: i.qty}))})
    });
    const d = await r.json().catch(() => ({}));
    if (r.ok) { setCart([]); showOk(d); confetti(); loadOrders(); }
    else showBad(d.error || "Could not place the order.");
  } catch (e) { showBad("The orders service is not available right now."); }
  busy = false; placeBtn.classList.remove("busy"); placeBtn.textContent = "Place order"; paintCart();
});

/* ---------- order history ---------- */
const olist = $("#olist");
let seen = null, lastSig = "";
function ago(iso){
  const s = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
  if (s < 45) return "just now";
  if (s < 3600) return Math.round(s / 60) + " min ago";
  if (s < 86400) return Math.round(s / 3600) + " h ago";
  return new Date(iso).toLocaleDateString("en-IN", {day: "numeric", month: "short"});
}
function ordHtml(o, fresh){
  const st = String(o.status || "PLACED");
  return `<article class="ord ${fresh ? "new" : ""}"><div class="oh"><span class="oid">#${esc(o.id)}</span><span class="st st-${esc(st.toLowerCase())}">${esc(st)}</span>
    <time data-t="${esc(o.created_at)}" title="${esc(new Date(o.created_at).toLocaleString("en-IN"))}">${esc(ago(o.created_at))}</time></div>
    <div class="oc">${esc(o.customer_name)}</div>
    <div class="oi">${o.items.map(i => `<span>${esc(i.qty)}&times; ${esc(i.name)}</span>`).join("")}</div>
    <div class="ot">${inr(o.total)}</div></article>`;
}
function loadOrders(){
  fetch("/orders/api").then(r => { if (!r.ok) throw 0; return r.json(); }).then(list => {
    const sig = JSON.stringify(list);
    if (sig === lastSig) { $$("time[data-t]").forEach(t => t.textContent = ago(t.dataset.t)); return; }
    lastSig = sig;
    const fresh = seen ? list.filter(o => !seen.has(o.id)).map(o => o.id) : [];
    seen = new Set(list.map(o => o.id));
    $("#oCount").textContent = list.length ? list.length + " latest" : "";
    olist.innerHTML = list.length ? list.map(o => ordHtml(o, fresh.includes(o.id))).join("")
      : '<div class="noord">No orders yet. Be the first!</div>';
  }).catch(() => { olist.innerHTML = '<div class="noord bad">The orders service is not available right now.</div>'; lastSig = ""; });
}

/* header shadow after scrolling */
const nav = $(".nav");
const onScroll = () => nav.classList.toggle("scrolled", window.scrollY > 8);
addEventListener("scroll", onScroll, {passive: true}); onScroll();

try { nameEl.value = localStorage.getItem(NAME_KEY) || ""; } catch (e) {}
paintCart();
syncCart();
loadOrders();
setInterval(() => { if (!document.hidden) loadOrders(); }, 15000);
</script>
</body>
</html>"""

_table_ready = False


def run(sql, params=None, fetch=None):
    """Run one SQL statement in its own connection and transaction."""
    global _table_ready
    with closing(psycopg2.connect(connect_timeout=5, **DB)) as conn:
        with conn, conn.cursor() as cur:
            if not _table_ready:
                cur.execute(
                    """CREATE TABLE IF NOT EXISTS orders (
                           id            SERIAL PRIMARY KEY,
                           customer_name TEXT          NOT NULL,
                           items         JSONB         NOT NULL,
                           total         NUMERIC(10,2) NOT NULL,
                           status        TEXT          NOT NULL DEFAULT 'PLACED',
                           created_at    TIMESTAMPTZ   NOT NULL DEFAULT now()
                       )"""
                )
                _table_ready = True
            cur.execute(sql, params)
            if fetch == "one":
                return cur.fetchone()
            if fetch == "all":
                return cur.fetchall()


def fetch_menu():
    """Return {item_id: item} from the meals and beverages services."""
    menu = {}
    for url in (MEALS_URL, BEVERAGES_URL):
        with urllib.request.urlopen(url, timeout=3) as resp:
            for item in json.load(resp):
                menu[item["id"]] = item
    return menu


_producer = None
_producer_lock = threading.Lock()


def get_producer():
    """Created on first use, so the orders service still starts when Kafka is down."""
    global _producer
    with _producer_lock:
        if _producer is None:
            from kafka import KafkaProducer
            _producer = KafkaProducer(
                bootstrap_servers=[s.strip() for s in KAFKA_SERVERS.split(",")],
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: str(k).encode("utf-8"),
                acks="all",
                retries=5,
                bootstrap_timeout_ms=5000,
                max_block_ms=5000,
            )
        return _producer


def publish_order_event(order_id, customer_name, items, total):
    """Tell the other services (kitchen, ...) that an order was placed."""
    global _producer
    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": "ORDER_PLACED",
        "order_id": order_id,
        "customer_name": customer_name,
        "items": items,
        "total": float(total),
        "status": "PLACED",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        meta = get_producer().send(KAFKA_TOPIC, key=order_id, value=event).get(timeout=10)
    except Exception:
        with _producer_lock:
            _producer = None             # build a fresh producer for the next order
        raise
    app.logger.info("Order event published: topic=%s partition=%s offset=%s",
                    meta.topic, meta.partition, meta.offset)


@app.route("/orders", strict_slashes=False)
def page():
    return PAGE


@app.route("/orders/api", methods=["POST"])
def create_order():
    data = request.get_json(silent=True) or {}
    cart = data.get("items")
    if not isinstance(cart, list) or not cart:
        return jsonify(error="Your cart is empty."), 400

    try:
        menu = fetch_menu()
    except Exception:
        return jsonify(error="Menu services are not reachable. Please try again."), 503

    lines, total = [], 0.0
    for entry in cart:
        try:
            item_id, qty = int(entry["id"]), int(entry["qty"])
        except (KeyError, TypeError, ValueError):
            return jsonify(error="Invalid cart item."), 400
        item = menu.get(item_id)
        if item is None or not 1 <= qty <= 20:
            return jsonify(error="Invalid item or quantity in cart."), 400
        lines.append({"id": item_id, "name": item["name"], "price": item["price"], "qty": qty})
        total += item["price"] * qty
    total = round(total, 2)

    name = str(data.get("customer_name") or "").strip()[:60] or "Guest"
    try:
        row = run(
            "INSERT INTO orders (customer_name, items, total) VALUES (%s, %s, %s) RETURNING id",
            (name, Json(lines), total),
            fetch="one",
        )
    except psycopg2.Error:
        return jsonify(error="Could not save the order. Database not reachable."), 503
    order_id = row[0]
    try:
        publish_order_event(order_id, name, lines, total)
        kafka_status = "PUBLISHED"
    except Exception:
        app.logger.exception("Order %s was saved but its Kafka event was NOT published", order_id)
        kafka_status = "PENDING"
    return jsonify(order_id=order_id, total=total, status="PLACED", kafka_status=kafka_status), 201


@app.route("/orders/api", methods=["GET"])
def list_orders():
    try:
        rows = run(
            "SELECT id, customer_name, items, total, status, created_at "
            "FROM orders ORDER BY id DESC LIMIT 50",
            fetch="all",
        )
    except psycopg2.Error:
        return jsonify(error="Database not reachable."), 503
    return jsonify([
        {"id": r[0], "customer_name": r[1], "items": r[2], "total": float(r[3]),
         "status": r[4], "created_at": r[5].isoformat()}
        for r in rows
    ])


@app.route("/healthz")
def healthz():
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
