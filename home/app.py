from flask import Flask

app = Flask(__name__)

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Quick Bites - fresh meals and cold drinks, ordered in seconds.">
<title>Quick Bites | Fast, fresh, hot</title>
<style>
  :root {
    --bg:#fff7e6; --surface:#ffffff; --ink:#2b1a14; --muted:#7a655b; --line:#f1dfc7;
    --red:#d62828; --red-dark:#a61e1e; --gold:#ffb703; --gold-soft:#ffe8a3;
    --shadow:0 10px 30px rgba(120,60,20,.12); --radius:18px;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg:#1b1210; --surface:#271a17; --ink:#fff1e3; --muted:#c9ad9c; --line:#3d2a24;
      --red:#ff5a4f; --red-dark:#e04137; --gold:#ffc83d; --gold-soft:#4a3513;
      --shadow:0 10px 30px rgba(0,0,0,.45);
    }
  }
  * { box-sizing:border-box; }
  html { scroll-behavior:smooth; }
  body { margin:0; font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; background:var(--bg); color:var(--ink); line-height:1.5; }
  a { color:inherit; text-decoration:none; }
  .wrap { max-width:1100px; margin:0 auto; padding:0 24px; }

  /* ---------- header ---------- */
  header { position:sticky; top:0; z-index:20; background:color-mix(in srgb, var(--bg) 82%, transparent); backdrop-filter:blur(10px); border-bottom:1px solid var(--line); }
  .bar { display:flex; align-items:center; justify-content:space-between; height:68px; }
  .logo { display:flex; align-items:center; gap:10px; font-weight:800; font-size:21px; letter-spacing:-.3px; }
  .logo .mark { display:grid; place-items:center; width:38px; height:38px; border-radius:12px; background:var(--red); font-size:20px; box-shadow:0 4px 12px rgba(214,40,40,.35); }
  .logo b { color:var(--red); }
  nav { display:flex; align-items:center; gap:6px; }
  nav a.link { padding:8px 14px; border-radius:999px; font-weight:600; font-size:15px; color:var(--muted); transition:.2s; }
  nav a.link:hover, nav a.link:focus-visible { background:var(--gold-soft); color:var(--ink); }
  .btn { display:inline-flex; align-items:center; gap:8px; padding:12px 22px; border-radius:999px; font-weight:700; font-size:16px; border:2px solid transparent; transition:transform .15s, box-shadow .15s, background .2s; cursor:pointer; }
  .btn:hover { transform:translateY(-2px); }
  .btn-red { background:var(--red); color:#fff; box-shadow:0 8px 20px rgba(214,40,40,.35); }
  .btn-red:hover { background:var(--red-dark); }
  .btn-ghost { border-color:var(--line); background:var(--surface); }
  .btn-ghost:hover { border-color:var(--gold); }
  a:focus-visible, button:focus-visible { outline:3px solid var(--gold); outline-offset:3px; }
  #menu-toggle, .burger { display:none; }

  /* ---------- hero ---------- */
  .hero { position:relative; overflow:hidden; padding:72px 0 96px; }
  .hero::before { content:""; position:absolute; inset:-20% -10% auto auto; width:620px; height:620px; border-radius:50%; background:radial-gradient(circle at 30% 30%, var(--gold) 0%, transparent 65%); opacity:.55; z-index:0; }
  .hero-grid { position:relative; z-index:1; display:grid; grid-template-columns:1.1fr .9fr; gap:40px; align-items:center; }
  .pill { display:inline-block; padding:6px 14px; border-radius:999px; background:var(--gold-soft); font-weight:700; font-size:13px; letter-spacing:.4px; text-transform:uppercase; }
  h1 { margin:18px 0 14px; font-size:clamp(38px,6vw,64px); line-height:1.04; letter-spacing:-1.5px; }
  h1 span { color:var(--red); position:relative; white-space:nowrap; }
  h1 span::after { content:""; position:absolute; left:0; right:0; bottom:2px; height:10px; background:var(--gold); opacity:.6; z-index:-1; border-radius:6px; }
  .lead { max-width:480px; color:var(--muted); font-size:18px; margin:0 0 28px; }
  .cta { display:flex; flex-wrap:wrap; gap:14px; }
  .stats { display:flex; gap:32px; margin-top:38px; }
  .stats div b { display:block; font-size:28px; letter-spacing:-.5px; }
  .stats div span { color:var(--muted); font-size:14px; }

  .plate { position:relative; aspect-ratio:1; max-width:430px; margin-left:auto; border-radius:50%; background:var(--surface); box-shadow:var(--shadow); display:grid; place-items:center; border:10px solid var(--gold-soft); }
  .plate .big { font-size:min(190px,32vw); animation:bob 4s ease-in-out infinite; }
  .float { position:absolute; display:grid; place-items:center; width:70px; height:70px; border-radius:50%; background:var(--surface); box-shadow:var(--shadow); font-size:34px; animation:bob 5s ease-in-out infinite; }
  .float.f1 { top:2%; left:6%; animation-delay:-1s; }
  .float.f2 { bottom:8%; left:-4%; animation-delay:-2s; }
  .float.f3 { top:14%; right:-4%; animation-delay:-3s; }
  .float.f4 { bottom:0; right:10%; animation-delay:-.5s; }
  @keyframes bob { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-14px); } }

  /* ---------- sections ---------- */
  section { padding:64px 0; }
  .head { text-align:center; max-width:560px; margin:0 auto 40px; }
  .head h2 { margin:0 0 8px; font-size:clamp(28px,4vw,40px); letter-spacing:-.8px; }
  .head p { margin:0; color:var(--muted); }

  .cards { display:grid; grid-template-columns:repeat(3,1fr); gap:22px; }
  .card { position:relative; display:flex; flex-direction:column; gap:10px; padding:28px; border-radius:var(--radius); background:var(--surface); border:1px solid var(--line); box-shadow:var(--shadow); transition:transform .2s, border-color .2s; overflow:hidden; }
  .card:hover, .card:focus-visible { transform:translateY(-6px); border-color:var(--gold); }
  .card .ico { display:grid; place-items:center; width:64px; height:64px; border-radius:18px; font-size:34px; background:var(--gold-soft); }
  .card h3 { margin:6px 0 0; font-size:22px; }
  .card p { margin:0; color:var(--muted); flex:1; }
  .card .go { display:flex; align-items:center; gap:6px; font-weight:700; color:var(--red); margin-top:8px; }
  .card .go i { font-style:normal; transition:transform .2s; }
  .card:hover .go i { transform:translateX(6px); }
  .card .tag { position:absolute; top:18px; right:18px; font-size:12px; font-weight:700; padding:4px 10px; border-radius:999px; background:var(--red); color:#fff; }

  .steps { display:grid; grid-template-columns:repeat(4,1fr); gap:18px; counter-reset:s; }
  .step { position:relative; padding:24px 20px; border-radius:var(--radius); background:var(--surface); border:1px dashed var(--line); text-align:center; }
  .step::before { counter-increment:s; content:counter(s); display:grid; place-items:center; width:38px; height:38px; margin:0 auto 12px; border-radius:50%; background:var(--red); color:#fff; font-weight:800; }
  .step b { display:block; margin-bottom:4px; }
  .step span { color:var(--muted); font-size:14px; }

  .banner { display:flex; align-items:center; justify-content:space-between; gap:24px; flex-wrap:wrap; padding:40px 44px; border-radius:28px; background:linear-gradient(120deg,var(--red) 0%, #ff7b2e 100%); color:#fff; box-shadow:0 18px 40px rgba(214,40,40,.3); }
  .banner h2 { margin:0 0 6px; font-size:clamp(26px,3.6vw,36px); letter-spacing:-.6px; }
  .banner p { margin:0; opacity:.92; }
  .banner .btn { background:#fff; color:var(--red-dark); }

  footer { padding:36px 0 48px; border-top:1px solid var(--line); color:var(--muted); font-size:14px; }
  footer .wrap { display:flex; justify-content:space-between; flex-wrap:wrap; gap:12px; }
  footer a:hover { color:var(--red); }

  /* ---------- responsive ---------- */
  @media (max-width:900px) {
    .hero-grid { grid-template-columns:1fr; text-align:center; }
    .lead { margin-inline:auto; } .cta, .stats { justify-content:center; }
    .plate { margin:10px auto 0; max-width:340px; }
    .cards { grid-template-columns:1fr; } .steps { grid-template-columns:1fr 1fr; }
  }
  @media (max-width:720px) {
    .burger { display:grid; place-items:center; width:42px; height:42px; border-radius:12px; border:1px solid var(--line); background:var(--surface); cursor:pointer; font-size:20px; }
    nav { position:absolute; top:68px; left:0; right:0; flex-direction:column; align-items:stretch; padding:12px 24px 20px; background:var(--bg); border-bottom:1px solid var(--line); display:none; }
    #menu-toggle:checked ~ nav { display:flex; }
    nav a.link { text-align:center; } nav .btn { justify-content:center; margin-top:6px; }
  }
  @media (max-width:480px) { .steps { grid-template-columns:1fr; } .banner { padding:30px 24px; } }
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
      <a class="link" href="/meals">Meals</a>
      <a class="link" href="/beverages">Beverages</a>
      <a class="link" href="/orders">My Orders</a>
      <a class="btn btn-red" href="/meals">Order now</a>
    </nav>
  </div>
</header>

<main>
  <div class="hero">
    <div class="wrap hero-grid">
      <div>
        <span class="pill">&#128293; Hot &amp; fresh every day</span>
        <h1>Big taste. <span>Zero wait.</span></h1>
        <p class="lead">Pick your favourite burger meal, add an ice-cold drink and place your order in seconds. We save every order so you can track it anytime.</p>
        <div class="cta">
          <a class="btn btn-red" href="/meals">Browse meals &rarr;</a>
          <a class="btn btn-ghost" href="/beverages">See drinks</a>
        </div>
        <div class="stats">
          <div><b>10 min</b><span>avg. prep time</span></div>
          <div><b>10+</b><span>menu items</span></div>
          <div><b>4.9 &#9733;</b><span>customer rating</span></div>
        </div>
      </div>
      <div class="plate" aria-hidden="true">
        <span class="big">&#127828;</span>
        <span class="float f1">&#127839;</span>
        <span class="float f2">&#129380;</span>
        <span class="float f3">&#127830;</span>
        <span class="float f4">&#127789;</span>
      </div>
    </div>
  </div>

  <section id="menu">
    <div class="wrap">
      <div class="head">
        <h2>What are you craving?</h2>
        <p>Choose a category to get started.</p>
      </div>
      <div class="cards">
        <a class="card" href="/meals">
          <span class="tag">Popular</span>
          <span class="ico">&#127828;</span>
          <h3>Meals</h3>
          <p>Burgers, nuggets and crispy fries &mdash; the classics made fresh to order.</p>
          <span class="go">View meals <i>&rarr;</i></span>
        </a>
        <a class="card" href="/beverages">
          <span class="ico">&#129380;</span>
          <h3>Beverages</h3>
          <p>Cold drinks, shakes, juices and iced coffee to go with every bite.</p>
          <span class="go">View drinks <i>&rarr;</i></span>
        </a>
        <a class="card" href="/orders">
          <span class="ico">&#129534;</span>
          <h3>Orders</h3>
          <p>Every order is stored safely. Check your past orders and totals in one place.</p>
          <span class="go">View orders <i>&rarr;</i></span>
        </a>
      </div>
    </div>
  </section>

  <section>
    <div class="wrap">
      <div class="head">
        <h2>How it works</h2>
        <p>From hungry to happy in four easy steps.</p>
      </div>
      <div class="steps">
        <div class="step"><b>Pick a meal</b><span>Choose from our menu</span></div>
        <div class="step"><b>Add a drink</b><span>Cold, sweet or classic</span></div>
        <div class="step"><b>Place order</b><span>Enter your name and confirm</span></div>
        <div class="step"><b>Enjoy</b><span>Your order is saved &amp; on its way</span></div>
      </div>
    </div>
  </section>

  <section>
    <div class="wrap">
      <div class="banner">
        <div>
          <h2>Hungry already?</h2>
          <p>Your meal is only a few clicks away.</p>
        </div>
        <a class="btn" href="/meals">Start your order &rarr;</a>
      </div>
    </div>
  </section>
</main>

<footer>
  <div class="wrap">
    <span>&copy; Quick Bites. Served fresh, built as microservices.</span>
    <span><a href="/meals">Meals</a> &middot; <a href="/beverages">Beverages</a> &middot; <a href="/orders">Orders</a></span>
  </div>
</footer>

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
