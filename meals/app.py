from flask import Flask, jsonify

app = Flask(__name__)

MEALS = [
    {"id": 101, "name": "Big Burger Meal", "category": "Burgers", "emoji": "🍔", "price": 7.99, "desc": "Beef patty, cheese, lettuce and our special sauce."},
    {"id": 102, "name": "Chicken Burger Meal", "category": "Burgers", "emoji": "🐔", "price": 6.99, "desc": "Crispy chicken fillet with mayo and fresh lettuce."},
    {"id": 103, "name": "Veggie Burger Meal", "category": "Burgers", "emoji": "🥬", "price": 6.49, "desc": "Garden veggie patty, tomato and a toasted bun."},
    {"id": 104, "name": "Cheese Burger", "category": "Burgers", "emoji": "🧀", "price": 4.99, "desc": "The classic: beef, melted cheese, pickles."},
    {"id": 105, "name": "Chicken Nuggets (9 pc)", "category": "Snacks", "emoji": "🍗", "price": 5.49, "desc": "Golden and crunchy, served with dipping sauce."},
    {"id": 106, "name": "Large Fries", "category": "Sides", "emoji": "🍟", "price": 2.99, "desc": "Hot, salty and crispy. Always."},
    {"id": 107, "name": "Onion Rings", "category": "Sides", "emoji": "🧅", "price": 3.49, "desc": "Thick-cut rings in a crunchy batter."},
    {"id": 108, "name": "Apple Pie", "category": "Desserts", "emoji": "🥧", "price": 2.49, "desc": "Warm pie with a flaky crust and cinnamon apples."},
]

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Meals | Quick Bites</title>
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
</style>
</head>
<body>
<header>
  <div class="wrap bar">
    <a class="logo" href="/" aria-label="Quick Bites home"><span class="mark">&#127828;</span>Quick<b>Bites</b></a>
    <input type="checkbox" id="menu-toggle" aria-hidden="true">
    <label class="burger" for="menu-toggle" aria-label="Toggle menu">&#9776;</label>
    <nav>
      <a class="link active" href="/meals">Meals</a>
      <a class="link" href="/beverages">Beverages</a>
      <a class="link" href="/orders">My Orders</a>
      <a class="btn btn-red" href="/orders">&#128722; Cart <span class="badge cartCount">0</span></a>
    </nav>
  </div>
</header>
<main class="wrap">
  <div class="pagehead">
    <span class="pill">&#128293; Fresh off the grill</span>
    <h1>Our <span>Meals</span></h1>
    <p>Burgers, nuggets, fries and more. Tap Add and we will keep your cart ready for checkout.</p>
  </div>
  <div class="chips" id="chips" aria-label="Categories"></div>
  <div class="grid" id="grid" aria-live="polite"></div>
</main>
<div class="cartbar" id="cartbar" role="status">
  <span id="barText">0 items</span>
  <a href="/orders">Checkout &rarr;</a>
</div>
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

const grid = document.getElementById("grid"), chips = document.getElementById("chips");
let items = [], cat = "All";
function render(){
  const cats = ["All", ...new Set(items.map(i => i.category))];
  chips.innerHTML = cats.map(c => `<button class="chip ${c === cat ? "on" : ""}" data-cat="${esc(c)}">${esc(c)}</button>`).join("");
  const list = items.filter(i => cat === "All" || i.category === cat);
  grid.innerHTML = list.map(i => {
    const q = cartQty(i.id);
    const ctl = q
      ? `<span class="stepper"><button data-act="dec" data-id="${i.id}" aria-label="Remove one">&minus;</button><b>${q}</b><button data-act="inc" data-id="${i.id}" aria-label="Add one">+</button></span>`
      : `<button class="btn btn-red add" data-act="inc" data-id="${i.id}">Add +</button>`;
    return `<article class="dish"><div class="pic">${esc(i.emoji)}</div><div class="body"><span class="cat">${esc(i.category)}</span><h3>${esc(i.name)}</h3><p>${esc(i.desc)}</p><div class="foot"><span class="price">${money(i.price)}</span>${ctl}</div></div></article>`;
  }).join("");
}
grid.addEventListener("click", e => {
  const b = e.target.closest("button[data-act]"); if (!b) return;
  const item = items.find(x => String(x.id) === b.dataset.id);
  if (item) changeQty(item, b.dataset.act === "inc" ? 1 : -1);
});
chips.addEventListener("click", e => {
  const b = e.target.closest("button[data-cat]"); if (!b) return;
  cat = b.dataset.cat; render();
});
window.onCart = () => { if (items.length) render(); };
grid.innerHTML = '<div class="skeleton"></div>'.repeat(6);
fetch("/meals/api").then(r => { if (!r.ok) throw 0; return r.json(); })
  .then(d => { items = d; render(); })
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
