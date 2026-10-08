import json
import os
import urllib.request
from contextlib import closing

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
MEALS_URL = os.getenv("MEALS_URL", "http://meals:5000/meals/api")
BEVERAGES_URL = os.getenv("BEVERAGES_URL", "http://beverages:5000/beverages/api")

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>My Orders | Quick Bites</title>
<style>
  :root {
    --bg:#fff7e6; --surface:#ffffff; --ink:#2b1a14; --muted:#7a655b; --line:#f1dfc7;
    --red:#d62828; --red-dark:#a61e1e; --gold:#ffb703; --gold-soft:#ffe8a3; --ok:#1b8a4b;
    --shadow:0 10px 30px rgba(120,60,20,.12); --radius:18px;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg:#1b1210; --surface:#271a17; --ink:#fff1e3; --muted:#c9ad9c; --line:#3d2a24;
      --red:#ff5a4f; --red-dark:#e04137; --gold:#ffc83d; --gold-soft:#4a3513; --ok:#46c27a;
      --shadow:0 10px 30px rgba(0,0,0,.45);
    }
  }
  * { box-sizing:border-box; }
  html { scroll-behavior:smooth; }
  body { margin:0; font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; background:var(--bg); color:var(--ink); line-height:1.5; }
  a { color:inherit; text-decoration:none; }
  .wrap { max-width:1100px; margin:0 auto; padding:0 24px; }
  a:focus-visible, button:focus-visible, input:focus-visible { outline:3px solid var(--gold); outline-offset:3px; }

  /* header */
  header { position:sticky; top:0; z-index:20; background:color-mix(in srgb, var(--bg) 82%, transparent); backdrop-filter:blur(10px); border-bottom:1px solid var(--line); }
  .bar { display:flex; align-items:center; justify-content:space-between; height:68px; }
  .logo { display:flex; align-items:center; gap:10px; font-weight:800; font-size:21px; letter-spacing:-.3px; }
  .logo .mark { display:grid; place-items:center; width:38px; height:38px; border-radius:12px; background:var(--red); font-size:20px; box-shadow:0 4px 12px rgba(214,40,40,.35); }
  .logo b { color:var(--red); }
  nav { display:flex; align-items:center; gap:6px; }
  nav a.link { padding:8px 14px; border-radius:999px; font-weight:600; font-size:15px; color:var(--muted); transition:.2s; }
  nav a.link:hover, nav a.link.active { background:var(--gold-soft); color:var(--ink); }
  .btn { display:inline-flex; align-items:center; gap:8px; padding:12px 22px; border-radius:999px; font-weight:700; font-size:16px; border:2px solid transparent; transition:transform .15s, box-shadow .15s, background .2s; cursor:pointer; font-family:inherit; }
  .btn:hover { transform:translateY(-2px); }
  .btn:disabled { opacity:.5; cursor:not-allowed; transform:none; }
  .btn-red { background:var(--red); color:#fff; box-shadow:0 8px 20px rgba(214,40,40,.3); }
  .btn-red:hover { background:var(--red-dark); }
  .badge { display:inline-grid; place-items:center; min-width:22px; height:22px; padding:0 6px; border-radius:999px; background:#fff; color:var(--red-dark); font-size:13px; font-weight:800; }
  #menu-toggle, .burger { display:none; }

  /* page head */
  .pagehead { padding:44px 0 8px; }
  .pill { display:inline-block; padding:6px 14px; border-radius:999px; background:var(--gold-soft); font-weight:700; font-size:13px; letter-spacing:.4px; text-transform:uppercase; }
  .pagehead h1 { margin:14px 0 8px; font-size:clamp(34px,5vw,52px); line-height:1.05; letter-spacing:-1.2px; }
  .pagehead h1 span { color:var(--red); }
  .pagehead p { margin:0; color:var(--muted); max-width:560px; font-size:17px; }

  /* shared bits */
  .stepper { display:inline-flex; align-items:center; gap:10px; background:var(--gold-soft); border-radius:999px; padding:4px; }
  .stepper button { width:32px; height:32px; border-radius:50%; border:0; background:var(--red); color:#fff; font-size:18px; font-weight:800; cursor:pointer; line-height:1; }
  .stepper b { min-width:18px; text-align:center; }
  .errorbox { padding:22px; border-radius:var(--radius); background:var(--surface); border:1px dashed var(--red); color:var(--red); font-weight:600; text-align:center; grid-column:1/-1; }

  /* menu pages */
  .chips { display:flex; flex-wrap:wrap; gap:10px; margin:26px 0 22px; }
  .chip { padding:9px 18px; border-radius:999px; border:1px solid var(--line); background:var(--surface); color:var(--ink); font-weight:600; font-size:14px; cursor:pointer; font-family:inherit; transition:.2s; }
  .chip:hover { border-color:var(--gold); }
  .chip.on { background:var(--red); border-color:var(--red); color:#fff; }
  .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(250px,1fr)); gap:20px; padding-bottom:130px; }
  .dish { display:flex; flex-direction:column; background:var(--surface); border:1px solid var(--line); border-radius:var(--radius); box-shadow:var(--shadow); overflow:hidden; transition:transform .2s, border-color .2s; }
  .dish:hover { transform:translateY(-5px); border-color:var(--gold); }
  .dish .pic { display:grid; place-items:center; height:130px; font-size:68px; background:linear-gradient(135deg,var(--gold-soft),transparent); }
  .dish .body { display:flex; flex-direction:column; gap:6px; padding:16px 18px 18px; flex:1; }
  .dish .cat { font-size:12px; font-weight:700; color:var(--red); text-transform:uppercase; letter-spacing:.5px; }
  .dish h3 { margin:0; font-size:18px; }
  .dish p { margin:0; color:var(--muted); font-size:14px; flex:1; }
  .dish .foot { display:flex; align-items:center; justify-content:space-between; margin-top:10px; min-height:42px; }
  .price { font-weight:800; font-size:20px; }
  .add { padding:8px 18px; font-size:14px; }
  .skeleton { height:290px; border-radius:var(--radius); background:linear-gradient(90deg,var(--line),var(--surface),var(--line)); background-size:200% 100%; animation:sh 1.2s linear infinite; }
  @keyframes sh { to { background-position:-200% 0; } }
  .cartbar { position:fixed; left:50%; bottom:20px; transform:translate(-50%,160%); width:min(560px,calc(100% - 32px)); display:flex; align-items:center; justify-content:space-between; gap:12px; padding:12px 14px 12px 22px; border-radius:999px; background:var(--ink); color:var(--bg); box-shadow:0 14px 34px rgba(0,0,0,.35); transition:transform .3s; z-index:30; font-weight:600; }
  .cartbar.show { transform:translate(-50%,0); }
  .cartbar a { background:var(--red); color:#fff; padding:10px 20px; border-radius:999px; font-weight:700; }

  footer { padding:36px 0 48px; border-top:1px solid var(--line); color:var(--muted); font-size:14px; }
  footer .wrap { display:flex; justify-content:space-between; flex-wrap:wrap; gap:12px; }
  footer a:hover { color:var(--red); }

  @media (max-width:720px) {
    .burger { display:grid; place-items:center; width:42px; height:42px; border-radius:12px; border:1px solid var(--line); background:var(--surface); cursor:pointer; font-size:20px; }
    nav { position:absolute; top:68px; left:0; right:0; flex-direction:column; align-items:stretch; padding:12px 24px 20px; background:var(--bg); border-bottom:1px solid var(--line); display:none; }
    #menu-toggle:checked ~ nav { display:flex; }
    nav a.link { text-align:center; } nav .btn { justify-content:center; margin-top:6px; }
  }
  @media (prefers-reduced-motion:reduce) { * { animation:none !important; transition:none !important; } html { scroll-behavior:auto; } }

  .cols { display:grid; grid-template-columns:1fr 1.3fr; gap:24px; padding:26px 0 70px; align-items:start; }
  .box { background:var(--surface); border:1px solid var(--line); border-radius:var(--radius); padding:24px; box-shadow:var(--shadow); }
  .box h2 { margin:0 0 14px; font-size:22px; }
  .line { display:grid; grid-template-columns:auto 1fr auto auto; gap:12px; align-items:center; padding:12px 0; border-bottom:1px solid var(--line); }
  .line .e { font-size:30px; }
  .line .n small { display:block; color:var(--muted); }
  .line .sub { font-weight:800; min-width:64px; text-align:right; }
  .empty { padding:28px 10px; text-align:center; color:var(--muted); }
  .empty a { color:var(--red); font-weight:700; }
  .total { display:flex; justify-content:space-between; font-size:20px; padding:16px 0 6px; }
  label { display:block; margin:14px 0 6px; font-size:14px; font-weight:600; color:var(--muted); }
  input[type=text] { width:100%; padding:12px 14px; border:1px solid var(--line); border-radius:12px; background:var(--bg); color:var(--ink); font-size:16px; font-family:inherit; }
  .wide { width:100%; justify-content:center; margin-top:16px; }
  #result { margin-top:14px; padding:0; font-weight:600; }
  #result.ok { padding:14px 16px; border-radius:12px; background:color-mix(in srgb, var(--ok) 16%, transparent); color:var(--ok); }
  #result.bad { padding:14px 16px; border-radius:12px; background:color-mix(in srgb, var(--red) 14%, transparent); color:var(--red); }
  .scroll { overflow-x:auto; }
  table { width:100%; border-collapse:collapse; font-size:14px; min-width:520px; }
  th { text-align:left; color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.5px; padding:8px 10px; }
  td { padding:12px 10px; border-top:1px solid var(--line); vertical-align:top; }
  .st { display:inline-block; padding:3px 10px; border-radius:999px; font-size:12px; font-weight:700; background:var(--gold-soft); }
  @media (max-width:900px) { .cols { grid-template-columns:1fr; } }
</style>
</head>
<body>
<header>
  <div class="wrap bar">
    <a class="logo" href="/" aria-label="Quick Bites home"><span class="mark">&#127828;</span>Quick<b>Bites</b></a>
    <input type="checkbox" id="menu-toggle" aria-hidden="true">
    <label class="burger" for="menu-toggle" aria-label="Toggle menu">&#9776;</label>
    <nav>
      <a class="link" href="/meals">Meals</a>
      <a class="link" href="/beverages">Beverages</a>
      <a class="link active" href="/orders">My Orders</a>
      <a class="btn btn-red" href="/orders">&#128722; Cart <span class="badge cartCount">0</span></a>
    </nav>
  </div>
</header>
<main class="wrap">
  <div class="pagehead">
    <span class="pill">&#129534; Checkout</span>
    <h1>Your <span>order</span></h1>
    <p>Review your cart and place the order. Every order is saved in our database.</p>
  </div>
  <div class="cols">
    <section class="box">
      <h2>Cart</h2>
      <div id="cartList"></div>
      <div class="total"><span>Total</span><b id="total">$0.00</b></div>
      <label for="name">Your name</label>
      <input type="text" id="name" maxlength="60" placeholder="e.g. Gajender" autocomplete="name">
      <button class="btn btn-red wide" id="placeBtn" disabled>Place order</button>
      <div id="result" role="status"></div>
    </section>
    <section class="box">
      <h2>Recent orders</h2>
      <div class="scroll">
        <table>
          <thead><tr><th>#</th><th>Customer</th><th>Items</th><th>Total</th><th>Status</th><th>Placed</th></tr></thead>
          <tbody id="rows"><tr><td colspan="6">Loading...</td></tr></tbody>
        </table>
      </div>
    </section>
  </div>
</main>
<footer>
  <div class="wrap">
    <span>&copy; Quick Bites. Served fresh, built as microservices.</span>
    <span><a href="/meals">Meals</a> &middot; <a href="/beverages">Beverages</a> &middot; <a href="/orders">Orders</a></span>
  </div>
</footer>
<script>
const KEY = "qb_cart";
const money = n => "$" + Number(n).toFixed(2);
const esc = s => String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
function getCart(){ try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch(e) { return []; } }
function setCart(c){ try { localStorage.setItem(KEY, JSON.stringify(c)); } catch(e) {} paintCart(); }
function cartQty(id){ const i = getCart().find(x => x.id === id); return i ? i.qty : 0; }
function changeQty(item, d){
  const c = getCart(); const i = c.find(x => x.id === item.id);
  if (i) { i.qty += d; if (i.qty <= 0) c.splice(c.indexOf(i), 1); }
  else if (d > 0) { c.push({id:item.id, name:item.name, price:item.price, emoji:item.emoji, qty:1}); }
  setCart(c);
}
function paintCart(){
  const c = getCart();
  const n = c.reduce((s,x) => s + x.qty, 0), t = c.reduce((s,x) => s + x.qty * x.price, 0);
  document.querySelectorAll(".cartCount").forEach(e => e.textContent = n);
  const bar = document.getElementById("cartbar");
  if (bar) { bar.classList.toggle("show", n > 0); document.getElementById("barText").textContent = n + (n === 1 ? " item" : " items") + " \u00b7 " + money(t); }
  if (window.onCart) window.onCart();
}

const cartList = document.getElementById("cartList"), totalEl = document.getElementById("total");
const placeBtn = document.getElementById("placeBtn"), nameEl = document.getElementById("name"), result = document.getElementById("result");

function renderCart(){
  const c = getCart();
  cartList.innerHTML = c.length ? c.map(i =>
    `<div class="line"><span class="e">${esc(i.emoji || "")}</span>
      <div class="n"><b>${esc(i.name)}</b><small>${money(i.price)} each</small></div>
      <span class="stepper"><button data-act="dec" data-id="${i.id}" aria-label="Remove one">&minus;</button><b>${i.qty}</b><button data-act="inc" data-id="${i.id}" aria-label="Add one">+</button></span>
      <span class="sub">${money(i.price * i.qty)}</span></div>`).join("")
    : '<div class="empty">Your cart is empty.<br><a href="/meals">Browse meals</a> or <a href="/beverages">drinks</a></div>';
  totalEl.textContent = money(c.reduce((s,x) => s + x.price * x.qty, 0));
  placeBtn.disabled = !c.length;
}
cartList.addEventListener("click", e => {
  const b = e.target.closest("button[data-act]"); if (!b) return;
  const item = getCart().find(x => String(x.id) === b.dataset.id);
  if (item) changeQty(item, b.dataset.act === "inc" ? 1 : -1);
});
window.onCart = renderCart;

placeBtn.addEventListener("click", async () => {
  result.className = ""; result.textContent = ""; placeBtn.disabled = true;
  try {
    const r = await fetch("/orders/api", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({customer_name: nameEl.value, items: getCart().map(i => ({id: i.id, qty: i.qty}))})
    });
    const d = await r.json().catch(() => ({}));
    if (r.ok) {
      setCart([]);
      result.className = "ok";
      result.innerHTML = "&#9989; Order <b>#" + d.order_id + "</b> placed! Total " + money(d.total);
      loadOrders();
    } else { result.className = "bad"; result.textContent = d.error || "Could not place the order."; }
  } catch (e) { result.className = "bad"; result.textContent = "The orders service is not available right now."; }
  placeBtn.disabled = !getCart().length;
});

function loadOrders(){
  const rows = document.getElementById("rows");
  fetch("/orders/api").then(r => { if (!r.ok) throw 0; return r.json(); }).then(list => {
    rows.innerHTML = list.length ? list.map(o =>
      `<tr><td><b>#${o.id}</b></td><td>${esc(o.customer_name)}</td>
        <td>${o.items.map(i => esc(i.name) + " x" + i.qty).join(", ")}</td>
        <td><b>${money(o.total)}</b></td><td><span class="st">${esc(o.status)}</span></td>
        <td>${esc(new Date(o.created_at).toLocaleString())}</td></tr>`).join("")
      : '<tr><td colspan="6">No orders yet. Be the first!</td></tr>';
  }).catch(() => { rows.innerHTML = '<tr><td colspan="6" style="color:var(--red);font-weight:600">The orders service is not available right now.</td></tr>'; });
}
paintCart();
loadOrders();
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
    return jsonify(order_id=row[0], total=total, status="PLACED"), 201


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
