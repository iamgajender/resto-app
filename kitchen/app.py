import json
import logging
import os
import threading
import time
from contextlib import closing, contextmanager

import psycopg2
from psycopg2.extras import Json
from flask import Flask, jsonify, request

app = Flask(__name__)
log = logging.getLogger("kitchen")
logging.basicConfig(level=logging.INFO)

# ---- configuration (env vars / Kubernetes ConfigMap + Secret) ----
DB = dict(
    host=os.getenv("DB_HOST", "postgres"),
    port=os.getenv("DB_PORT", "5432"),
    dbname=os.getenv("DB_NAME", "restaurant"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "postgres"),
)
KAFKA_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "192.168.1.213:9092,192.168.1.139:9092,192.168.1.133:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "orders")
KAFKA_GROUP = os.getenv("KAFKA_GROUP", "kitchen-group")
KAFKA_ENABLED = os.getenv("KAFKA_ENABLED", "true").lower() == "true"

kafka_state = {"status": "connecting" if KAFKA_ENABLED else "disabled"}

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kitchen | Quick Bites</title>
<style>
  :root {
    --bg:#fff7e6; --surface:#ffffff; --ink:#2b1a14; --muted:#7a655b; --line:#f1dfc7;
    --red:#d62828; --red-dark:#a61e1e; --gold:#ffb703; --gold-soft:#ffe8a3; --ok:#1b8a4b; --amber:#e07a00;
    --shadow:0 10px 30px rgba(120,60,20,.12); --radius:18px;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg:#1b1210; --surface:#271a17; --ink:#fff1e3; --muted:#c9ad9c; --line:#3d2a24;
      --red:#ff5a4f; --red-dark:#e04137; --gold:#ffc83d; --gold-soft:#4a3513; --ok:#46c27a; --amber:#ffa133;
      --shadow:0 10px 30px rgba(0,0,0,.45);
    }
  }
  * { box-sizing:border-box; }
  body { margin:0; font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; background:var(--bg); color:var(--ink); line-height:1.5; }
  a { color:inherit; text-decoration:none; }
  button, input { font-family:inherit; }
  a:focus-visible, button:focus-visible, input:focus-visible { outline:3px solid var(--gold); outline-offset:2px; }
  .wrap { max-width:1300px; margin:0 auto; padding:0 24px; }

  header { position:sticky; top:0; z-index:20; background:color-mix(in srgb, var(--bg) 82%, transparent); backdrop-filter:blur(10px); border-bottom:1px solid var(--line); }
  .bar { display:flex; align-items:center; justify-content:space-between; gap:16px; min-height:68px; flex-wrap:wrap; padding:8px 0; }
  .logo { display:flex; align-items:center; gap:10px; font-weight:800; font-size:21px; letter-spacing:-.3px; }
  .logo .mark { display:grid; place-items:center; width:38px; height:38px; border-radius:12px; background:var(--red); font-size:20px; }
  .logo b { color:var(--red); }
  .stats { display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
  .stat { padding:6px 14px; border-radius:999px; background:var(--surface); border:1px solid var(--line); font-weight:700; font-size:14px; }
  .pill { display:inline-flex; align-items:center; gap:8px; padding:6px 14px; border-radius:999px; font-weight:700; font-size:13px; background:var(--gold-soft); }
  .pill i { width:9px; height:9px; border-radius:50%; background:var(--amber); }
  .pill.connected i { background:var(--ok); }
  .pill.disconnected i { background:var(--red); }

  .intro { padding:26px 0 6px; }
  .intro h1 { margin:0; font-size:clamp(28px,4vw,40px); letter-spacing:-1px; }
  .intro h1 span { color:var(--red); }
  .intro p { margin:6px 0 0; color:var(--muted); }
  #offline { margin:16px 0 0; padding:14px 18px; border-radius:14px; background:color-mix(in srgb, var(--red) 14%, transparent); color:var(--red); font-weight:700; }

  .board { display:grid; grid-template-columns:repeat(3,1fr); gap:22px; padding:22px 0 60px; align-items:start; }
  .col h2 { display:flex; align-items:center; justify-content:space-between; margin:0 0 14px; font-size:20px; }
  .col h2 em { font-style:normal; font-size:14px; padding:2px 12px; border-radius:999px; background:var(--gold-soft); }
  .stack { display:flex; flex-direction:column; gap:16px; min-height:120px; }
  .none { padding:28px 16px; text-align:center; color:var(--muted); border:2px dashed var(--line); border-radius:var(--radius); }

  .ticket { background:var(--surface); border:1px solid var(--line); border-radius:var(--radius); box-shadow:var(--shadow); padding:18px; }
  .ticket.fresh { animation:flash 1.4s ease-out 2; }
  @keyframes flash { 0%,100% { box-shadow:var(--shadow); } 50% { box-shadow:0 0 0 5px var(--gold), var(--shadow); } }
  .ticket .top { display:flex; align-items:baseline; justify-content:space-between; gap:10px; }
  .oid { font-size:22px; font-weight:800; }
  .cust { color:var(--muted); font-weight:600; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .items { margin:10px 0 6px; padding:0; list-style:none; }
  .items li { padding:3px 0; border-bottom:1px dashed var(--line); }
  .meta { color:var(--muted); font-size:13px; }
  .ask { margin:12px 0 8px; font-weight:700; }

  .chips { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:10px; }
  .chip { padding:6px 14px; border-radius:999px; border:1px solid var(--line); background:var(--bg); color:var(--ink); font-weight:700; cursor:pointer; }
  .chip:hover { border-color:var(--gold); }
  .row { display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin-top:8px; }
  input[type=number] { width:84px; padding:9px 10px; border:1px solid var(--line); border-radius:10px; background:var(--bg); color:var(--ink); font-size:16px; }
  .btn { display:inline-flex; align-items:center; justify-content:center; gap:6px; padding:10px 18px; border-radius:999px; border:0; font-weight:700; font-size:15px; cursor:pointer; transition:transform .15s, background .2s; }
  .btn:hover { transform:translateY(-1px); }
  .btn:disabled { opacity:.5; cursor:not-allowed; }
  .btn-red { background:var(--red); color:#fff; }
  .btn-red:hover { background:var(--red-dark); }
  .btn-ok { background:var(--ok); color:#fff; }
  .btn-sm { padding:7px 14px; font-size:14px; background:var(--gold-soft); color:var(--ink); }
  .wide { width:100%; margin-top:12px; }

  .timer { margin:12px 0 8px; font-size:54px; font-weight:800; letter-spacing:-1px; text-align:center; font-variant-numeric:tabular-nums; }
  .timer.soon { color:var(--amber); }
  .timer.late { color:var(--red); animation:pulse 1s infinite; }
  @keyframes pulse { 50% { opacity:.45; } }
  .bar-track { height:10px; border-radius:999px; background:var(--gold-soft); overflow:hidden; }
  .bar-track i { display:block; height:100%; width:0; background:linear-gradient(90deg,var(--gold),var(--red)); border-radius:999px; transition:width 1s linear; }
  .done { margin-top:12px; font-weight:800; color:var(--ok); }

  #toast { position:fixed; left:50%; bottom:24px; transform:translateX(-50%); padding:12px 20px; border-radius:999px; background:var(--ink); color:var(--bg); font-weight:700; box-shadow:0 10px 30px rgba(0,0,0,.35); z-index:50; }
  [hidden] { display:none !important; }
  @media (max-width:1000px) { .board { grid-template-columns:1fr; } }
  @media (prefers-reduced-motion:reduce) { * { animation:none !important; transition:none !important; } }
</style>
</head>
<body>
<header>
  <div class="wrap bar">
    <a class="logo" href="/" aria-label="Quick Bites home"><span class="mark">&#127859;</span>Quick<b>Bites</b> Kitchen</a>
    <div class="stats">
      <span class="stat">&#128276; New <b id="cNew">0</b></span>
      <span class="stat">&#128293; Preparing <b id="cPrep">0</b></span>
      <span class="stat">&#9989; Done <b id="cDone">0</b></span>
      <span class="pill" id="kafka"><i></i><span>Kafka: connecting</span></span>
    </div>
  </div>
</header>
<main class="wrap">
  <div class="intro">
    <h1>Kitchen <span>display</span></h1>
    <p>New orders appear here automatically. Set the preparation time, watch the countdown, and adjust it any time. Click anywhere once to enable the new-order sound.</p>
    <div id="offline" hidden>The kitchen service cannot reach its database. Retrying...</div>
  </div>
  <div class="board">
    <section class="col"><h2>&#128276; New orders <em id="hNew">0</em></h2><div class="stack" id="colNew"></div></section>
    <section class="col"><h2>&#128293; Preparing <em id="hPrep">0</em></h2><div class="stack" id="colPrep"></div></section>
    <section class="col"><h2>&#9989; Completed <em id="hDone">0</em></h2><div class="stack" id="colDone"></div></section>
  </div>
</main>
<div id="toast" hidden></div>
<script>
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const fmt = s => { s = Math.max(0, Math.ceil(s)); return String(Math.floor(s / 60)).padStart(2, "0") + ":" + String(s % 60).padStart(2, "0"); };
const clock = iso => new Date(iso).toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"});

let tickets = [], offset = 0, firstLoad = true, signature = "";
const known = new Set();
let actx = null;
document.addEventListener("click", () => {
  if (!actx) { try { actx = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) {} }
}, {once: true});
function beep(){
  if (!actx) return;
  const o = actx.createOscillator(), g = actx.createGain();
  o.connect(g); g.connect(actx.destination); o.frequency.value = 880; g.gain.value = 0.08;
  o.start(); o.stop(actx.currentTime + 0.25);
}
function toast(msg){
  const t = $("toast"); t.textContent = msg; t.hidden = false;
  clearTimeout(toast.h); toast.h = setTimeout(() => t.hidden = true, 3500);
}

function ticketHtml(t, fresh){
  const items = t.items.map(i => `<li><b>${esc(i.qty)}&times;</b> ${esc(i.name)}</li>`).join("");
  const head = `<div class="top"><span class="oid">#${t.order_id}</span><span class="cust">${esc(t.customer_name)}</span></div>
    <ul class="items">${items}</ul><div class="meta">Received ${clock(t.received_at)} &middot; Total $${Number(t.total).toFixed(2)}</div>`;
  let body = "";
  if (t.status === "NEW") {
    body = `<div class="ask">How long to prepare?</div>
      <div class="chips">${[5, 10, 15, 20].map(m => `<button class="chip" data-chip="${m}" data-id="${t.order_id}">${m} min</button>`).join("")}</div>
      <div class="row"><input type="number" min="0.5" max="180" step="0.5" value="10" data-input="start" data-id="${t.order_id}" aria-label="Preparation minutes"> <span>min</span>
      <button class="btn btn-red" data-act="start" data-id="${t.order_id}">Start preparing</button></div>`;
  } else if (t.status === "PREPARING") {
    body = `<div class="timer" data-timer="${t.order_id}">--:--</div>
      <div class="bar-track"><i data-bar="${t.order_id}"></i></div>
      <div class="meta" style="margin-top:6px">Ready at ${clock(t.ready_at)}</div>
      <div class="row"><button class="btn btn-sm" data-act="extend" data-min="-1" data-id="${t.order_id}">&minus;1 min</button>
        <button class="btn btn-sm" data-act="extend" data-min="1" data-id="${t.order_id}">+1 min</button>
        <button class="btn btn-sm" data-act="extend" data-min="5" data-id="${t.order_id}">+5 min</button></div>
      <div class="row"><input type="number" min="0.5" max="180" step="0.5" value="5" data-input="set" data-id="${t.order_id}" aria-label="New time from now in minutes"> <span>min from now</span>
        <button class="btn btn-sm" data-act="set_time" data-id="${t.order_id}">Set</button></div>
      <button class="btn btn-ok wide" data-act="complete" data-id="${t.order_id}">Mark completed</button>`;
  } else {
    body = `<div class="done">&#9989; Completed at ${clock(t.completed_at)}</div>
      <div class="meta">Preparation time ${Math.round(t.prep_seconds / 6) / 10} min</div>`;
  }
  return `<article class="ticket ${fresh ? "fresh" : ""}">${head}${body}</article>`;
}

function render(freshIds){
  // keep what the cook is typing while the board refreshes
  const typed = {};
  document.querySelectorAll("input[data-input]").forEach(el => typed[el.dataset.input + el.dataset.id] = el.value);
  const col = (status, id, empty) => {
    const list = tickets.filter(t => t.status === status);
    $(id).innerHTML = list.length ? list.map(t => ticketHtml(t, freshIds.includes(t.order_id))).join("") : `<div class="none">${empty}</div>`;
    return list.length;
  };
  const n = col("NEW", "colNew", "No new orders. Waiting for customers...");
  const p = col("PREPARING", "colPrep", "Nothing is being prepared right now.");
  const d = col("COMPLETED", "colDone", "Completed orders will show up here.");
  $("cNew").textContent = $("hNew").textContent = n;
  $("cPrep").textContent = $("hPrep").textContent = p;
  $("cDone").textContent = $("hDone").textContent = d;
  document.querySelectorAll("input[data-input]").forEach(el => {
    const k = el.dataset.input + el.dataset.id;
    if (k in typed) el.value = typed[k];
  });
  tick();
}

function tick(){
  tickets.filter(t => t.status === "PREPARING").forEach(t => {
    const remaining = (new Date(t.ready_at).getTime() - (Date.now() + offset)) / 1000;
    const el = document.querySelector(`[data-timer="${t.order_id}"]`);
    if (el) {
      el.textContent = fmt(remaining);
      el.classList.toggle("soon", remaining <= 60 && remaining > 0);
      el.classList.toggle("late", remaining <= 0);
    }
    const bar = document.querySelector(`[data-bar="${t.order_id}"]`);
    if (bar) bar.style.width = Math.min(100, Math.max(0, 100 * (1 - remaining / t.prep_seconds))) + "%";
    if (remaining <= 0 && !t.asked) { t.asked = true; setTimeout(load, 800); }
  });
}
setInterval(tick, 1000);

function setKafka(status){
  const p = $("kafka");
  p.className = "pill " + (status === "connected" ? "connected" : status === "disconnected" ? "disconnected" : "");
  p.lastElementChild.textContent = "Kafka: " + status;
}

async function load(){
  try {
    const r = await fetch("/kitchen/api/tickets");
    if (!r.ok) throw new Error("bad status");
    const d = await r.json();
    offset = new Date(d.server_now).getTime() - Date.now();
    setKafka(d.kafka);
    $("offline").hidden = true;
    const fresh = d.tickets.filter(t => t.status === "NEW" && !known.has(t.order_id)).map(t => t.order_id);
    d.tickets.forEach(t => known.add(t.order_id));
    if (!firstLoad && fresh.length) { beep(); toast("New order #" + fresh.join(", #")); }
    firstLoad = false;
    const sig = JSON.stringify(d.tickets);
    if (sig !== signature) { signature = sig; tickets = d.tickets; render(fresh); }
  } catch (e) { $("offline").hidden = false; }
}

async function patch(id, body){
  try {
    const r = await fetch("/kitchen/api/tickets/" + id, {method: "PATCH", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)});
    const d = await r.json().catch(() => ({}));
    if (!r.ok) toast(d.error || "Could not update the order");
  } catch (e) { toast("Kitchen service not reachable"); }
  load();
}
const inputOf = (kind, id) => document.querySelector(`input[data-input="${kind}"][data-id="${id}"]`);

document.addEventListener("click", e => {
  const chip = e.target.closest("button[data-chip]");
  if (chip) { const i = inputOf("start", chip.dataset.id); if (i) i.value = chip.dataset.chip; return; }
  const b = e.target.closest("button[data-act]"); if (!b) return;
  const id = b.dataset.id, act = b.dataset.act;
  if (act === "start") patch(id, {action: "start", minutes: inputOf("start", id).value});
  else if (act === "set_time") patch(id, {action: "set_time", minutes: inputOf("set", id).value});
  else if (act === "extend") patch(id, {action: "extend", minutes: b.dataset.min});
  else if (act === "complete") patch(id, {action: "complete"});
});

load();
setInterval(load, 3000);
</script>
</body>
</html>"""


# ----------------------------------------------------------------------------
# database
# ----------------------------------------------------------------------------
_table_ready = False
_table_lock = threading.Lock()

COLS = ("order_id, customer_name, items, total, status, prep_seconds, "
        "started_at, ready_at, completed_at, received_at")


def ensure_table():
    global _table_ready
    if _table_ready:
        return
    with _table_lock:
        if _table_ready:
            return
        with closing(psycopg2.connect(connect_timeout=5, **DB)) as conn:
            with conn, conn.cursor() as cur:
                cur.execute(
                    """CREATE TABLE IF NOT EXISTS kitchen_tickets (
                           order_id      INTEGER       PRIMARY KEY,
                           customer_name TEXT          NOT NULL,
                           items         JSONB         NOT NULL,
                           total         NUMERIC(10,2) NOT NULL,
                           status        TEXT          NOT NULL DEFAULT 'NEW',
                           prep_seconds  INTEGER,
                           started_at    TIMESTAMPTZ,
                           ready_at      TIMESTAMPTZ,
                           completed_at  TIMESTAMPTZ,
                           received_at   TIMESTAMPTZ   NOT NULL DEFAULT now()
                       )"""
                )
        _table_ready = True


@contextmanager
def db():
    """One connection and one transaction per call (commit on success)."""
    ensure_table()
    with closing(psycopg2.connect(connect_timeout=5, **DB)) as conn:
        with conn, conn.cursor() as cur:
            yield cur


def iso(value):
    return value.isoformat() if value else None


def ticket_dict(r):
    return {
        "order_id": r[0], "customer_name": r[1], "items": r[2], "total": float(r[3]),
        "status": r[4], "prep_seconds": r[5], "started_at": iso(r[6]),
        "ready_at": iso(r[7]), "completed_at": iso(r[8]), "received_at": iso(r[9]),
    }


def complete_due(cur):
    """A ticket whose timer ran out becomes COMPLETED (at the moment the timer ended)."""
    cur.execute(
        "UPDATE kitchen_tickets SET status = 'COMPLETED', completed_at = ready_at "
        "WHERE status = 'PREPARING' AND ready_at <= now()"
    )


def add_ticket(event):
    """Create a ticket from an ORDER_PLACED event. Safe to call twice for the same order."""
    if not isinstance(event, dict) or event.get("event_type") != "ORDER_PLACED":
        return False
    order_id = int(event["order_id"])
    items = event.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError("event has no items")
    name = str(event.get("customer_name") or "Guest").strip()[:60] or "Guest"
    with db() as cur:
        cur.execute(
            "INSERT INTO kitchen_tickets (order_id, customer_name, items, total) "
            "VALUES (%s, %s, %s, %s) ON CONFLICT (order_id) DO NOTHING",
            (order_id, name, Json(items), float(event.get("total") or 0)),
        )
        return cur.rowcount == 1


# ----------------------------------------------------------------------------
# Kafka consumer (runs in a background thread)
# ----------------------------------------------------------------------------
def safe_json(raw):
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return None          # a bad message must never block the topic


def run_consumer():
    from kafka import KafkaConsumer
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=[s.strip() for s in KAFKA_SERVERS.split(",")],
        group_id=KAFKA_GROUP,
        auto_offset_reset="earliest",
        enable_auto_commit=False,        # commit only after the ticket is safely in PostgreSQL
        value_deserializer=safe_json,
    )
    kafka_state["status"] = "connected"
    try:
        for message in consumer:
            try:
                created = add_ticket(message.value)
                if created:
                    log.info("New kitchen ticket for order %s", message.value["order_id"])
            except (KeyError, TypeError, ValueError):
                log.warning("Skipping invalid event at offset %s", message.offset)
            consumer.commit()            # database errors are NOT caught: the event is re-delivered
    finally:
        consumer.close()


def consumer_loop():
    while True:
        try:
            kafka_state["status"] = "connecting"
            run_consumer()
        except ImportError:
            kafka_state["status"] = "disabled (kafka library missing)"
            return
        except Exception:
            kafka_state["status"] = "disconnected"
            log.exception("Kafka consumer stopped, retrying in 5 seconds")
        time.sleep(5)


def start_consumer():
    if KAFKA_ENABLED:
        threading.Thread(target=consumer_loop, name="kafka-consumer", daemon=True).start()


# ----------------------------------------------------------------------------
# routes
# ----------------------------------------------------------------------------
@app.route("/kitchen", strict_slashes=False)
def page():
    return PAGE


@app.route("/kitchen/api/tickets", methods=["GET"])
def list_tickets():
    try:
        with db() as cur:
            complete_due(cur)
            cur.execute(
                f"SELECT {COLS} FROM kitchen_tickets "
                "WHERE status <> 'COMPLETED' OR completed_at > now() - interval '12 hours' "
                "ORDER BY order_id"
            )
            rows = cur.fetchall()
            cur.execute("SELECT now()")
            now = cur.fetchone()[0]
    except psycopg2.Error:
        return jsonify(error="Database not reachable."), 503
    return jsonify(server_now=now.isoformat(), kafka=kafka_state["status"],
                   tickets=[ticket_dict(r) for r in rows])


@app.route("/kitchen/api/events", methods=["POST"])
def receive_event():
    """Same payload Kafka delivers. Handy for testing without Kafka."""
    event = request.get_json(silent=True)
    try:
        created = add_ticket(event)
    except (KeyError, TypeError, ValueError):
        return jsonify(error="Invalid ORDER_PLACED event."), 400
    except psycopg2.Error:
        return jsonify(error="Database not reachable."), 503
    return jsonify(created=created), 201 if created else 200


@app.route("/kitchen/api/tickets/<int:order_id>", methods=["PATCH"])
def update_ticket(order_id):
    data = request.get_json(silent=True) or {}
    action = data.get("action")
    if action not in ("start", "set_time", "extend", "complete"):
        return jsonify(error="Unknown action."), 400

    secs = 0
    if action != "complete":
        try:
            minutes = float(data.get("minutes"))
        except (TypeError, ValueError):
            return jsonify(error="Enter the time in minutes."), 400
        if action == "extend":
            valid = minutes != 0 and abs(minutes) <= 180
        else:
            valid = 0.5 <= minutes <= 180
        if not valid:
            return jsonify(error="Time must be between 0.5 and 180 minutes."), 400
        secs = int(round(minutes * 60))

    try:
        with db() as cur:
            complete_due(cur)
            cur.execute("SELECT status FROM kitchen_tickets WHERE order_id = %s FOR UPDATE", (order_id,))
            row = cur.fetchone()
            if row is None:
                return jsonify(error="Order not found."), 404
            status = row[0]

            if action == "start":
                if status != "NEW":
                    return jsonify(error="This order was already started."), 409
                cur.execute(
                    "UPDATE kitchen_tickets SET status = 'PREPARING', prep_seconds = %s, started_at = now(), "
                    "ready_at = now() + make_interval(secs => %s) WHERE order_id = %s",
                    (secs, secs, order_id),
                )
            else:
                if status != "PREPARING":
                    msg = "Start preparing first." if status == "NEW" else "This order is already completed."
                    return jsonify(error=msg), 409
                if action == "set_time":
                    cur.execute(
                        "UPDATE kitchen_tickets SET ready_at = now() + make_interval(secs => %s) WHERE order_id = %s",
                        (secs, order_id),
                    )
                elif action == "extend":
                    cur.execute(
                        "UPDATE kitchen_tickets SET ready_at = "
                        "GREATEST(ready_at + make_interval(secs => %s), now() + interval '5 seconds') "
                        "WHERE order_id = %s",
                        (secs, order_id),
                    )
                else:  # complete
                    cur.execute(
                        "UPDATE kitchen_tickets SET status = 'COMPLETED', completed_at = now() WHERE order_id = %s",
                        (order_id,),
                    )
                if action != "complete":
                    cur.execute(
                        "UPDATE kitchen_tickets SET prep_seconds = "
                        "round(extract(epoch FROM (ready_at - started_at)))::int WHERE order_id = %s",
                        (order_id,),
                    )

            cur.execute(f"SELECT {COLS} FROM kitchen_tickets WHERE order_id = %s", (order_id,))
            result = ticket_dict(cur.fetchone())
    except psycopg2.Error:
        return jsonify(error="Database not reachable."), 503
    return jsonify(result)


@app.route("/healthz")
def healthz():
    return "ok"


if os.getenv("START_CONSUMER", "1") == "1":
    start_consumer()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
