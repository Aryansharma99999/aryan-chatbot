# app.py
# Full single-page portfolio (Bright Lavender cosmic theme)
# Features: H3 abstract hero, small white particles, floating icons (left),
# floating chatbot (right, slides up), photos modal, writings page (anonymous)
# Requirements: streamlit, markdown, requests

import os
import re
import time
import json
from datetime import datetime
from markdown import markdown
import streamlit as st
import streamlit.components.v1 as components
import requests

# ---------- Config ----------
st.set_page_config(page_title="Aryan Sharma — Portfolio", layout="wide", initial_sidebar_state="collapsed")
BASE_DIR = os.path.dirname(__file__) or "."
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")
MSG_FILE = os.path.join(BASE_DIR, "anonymous_messages.txt")

# Optional environment (do NOT hardcode credentials)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

HERO_NAME = "Aryan Sharma"
HERO_SUB  = "I'm a developer, writer, editor & learner"

# ---------- Utilities ----------
def ensure_file(path):
    if not os.path.exists(path):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("")
        except Exception:
            pass

def save_anonymous_message(text):
    ensure_file(MSG_FILE)
    msg = {
        "id": int(time.time() * 1000),
        "text": text,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }
    try:
        with open(MSG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(msg, ensure_ascii=False) + "\n")
    except Exception:
        pass

    # Optional notify via Telegram (best-effort)
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": f"📨 New anonymous message:\n\n{msg['text']}"}
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json=payload, timeout=5)
        except Exception:
            pass
    return msg

def load_anonymous_messages():
    ensure_file(MSG_FILE)
    out = []
    try:
        with open(MSG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except Exception:
                    continue
    except Exception:
        return []
    return out

def get_gallery_images():
    try:
        files = os.listdir(BASE_DIR)
    except Exception:
        files = []
    imgs = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
    # ignore preview files commonly produced
    ignore = {"final_preview_c2.png","theme_preview_final.png","preview_top.png","preview_mid.png","preview_bot.png","final_top.png","final_mid.png","final_bot.png","preview_regenerated.png","preview_particles_small.png","final_stitched.png","preview_full_stitched.png"}
    return [i for i in imgs if i not in ignore]

def get_all_posts():
    if not os.path.exists(POSTS_DIR):
        return []
    posts = []
    for f in os.listdir(POSTS_DIR):
        if not f.endswith(".md"):
            continue
        path = os.path.join(POSTS_DIR, f)
        try:
            with open(path, "r", encoding="utf-8") as fh:
                content = fh.read()
        except Exception:
            continue
        meta = {}
        body = content
        m = re.match(r"---\n(.*?)\n---", content, re.DOTALL)
        if m:
            for ln in m.group(1).splitlines():
                if ":" in ln:
                    k, v = ln.split(":", 1)
                    meta[k.strip()] = v.strip()
            body = content[m.end():].strip()
        html = markdown(body)
        posts.append({"slug": f[:-3], "title": meta.get("title", f[:-3]), "date": meta.get("date", "N/A"), "summary": meta.get("summary", ""), "html": html})
    return posts

# ---------- Inject global CSS & helper JS ----------
def inject_global_css_js():
    # Normal string (no f-strings) to avoid brace escaping errors
    css_js = """
    <style>
    :root{
      --accent1: #EED1FF;   /* bright lavender text */
      --accent2: #CAA8FF;   /* subtitle */
      --card-fill: rgba(140,0,255,0.18);
      --card-border: rgba(255,140,255,0.32);
      --bg-top: rgba(120,0,255,0.06);
      --neon: #C43BFF;
    }
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
      background: radial-gradient(circle at 20% 10%, rgba(120,0,255,0.36), rgba(10,0,20,0.95) 60%), linear-gradient(180deg,#0a0018 0%, #14021a 100%) !important;
      color: var(--accent1);
      font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
      -webkit-font-smoothing:antialiased;
    }
    /* remove default chrome */
    #MainMenu, header, footer { display: none !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    a { color: var(--accent1); }
    /* Tiny adjustments for images so gallery previews look good */
    img { max-width:100%; height:auto; display:block; }
    </style>

    <script>
    // helper to set query param and reload
    function setQueryParam(key, value) {
      const u = new URL(window.location);
      u.searchParams.set(key, value);
      window.location = u.toString();
    }
    // helper to clear a param
    function clearParams() {
      const u = new URL(window.location);
      u.searchParams.delete('show_photos');
      u.searchParams.delete('page');
      u.searchParams.delete('anon_q');
      window.location = u.toString();
    }
    </script>
    """
    st.markdown(css_js, unsafe_allow_html=True)

# ---------- Hero / Nav component (HTML + small-particle canvas + floating icons + chat) ----------
def render_hero_and_nav():
    # We'll embed a canvas script that draws *small white dots* as requested
    html = """
    <style>
    .nav {
      position: fixed; top: 18px; left: 50%; transform: translateX(-50%); z-index: 9999;
      width: 94%; max-width: 1200px; display:flex; align-items:center; justify-content:space-between;
      padding: 10px 18px; border-radius: 12px; backdrop-filter: blur(10px) saturate(120%);
      background: rgba(20,0,40,0.46); border: 1px solid rgba(255,255,255,0.03);
      box-shadow: 0 20px 60px rgba(0,0,0,0.55);
    }
    .brand { font-weight:800; color: var(--accent1); font-size: 18px; }
    .nav-links { display:flex; gap:14px; align-items:center; }
    .nav-links a { color: var(--accent1); text-decoration:none; padding:6px 8px; border-radius:8px; font-weight:700; opacity:0.95; }
    .hero-wrap { height: 82vh; min-height: 520px; display:flex; align-items:center; justify-content:center; padding: 36px 20px; position:relative; overflow:hidden; }
    .hero-card {
      width: min(1100px,96%); border-radius: 28px; padding: 34px; position: relative; overflow: hidden;
      box-shadow: 0 30px 100px rgba(0,0,0,0.45);
      background: rgba(35,0,55,0.56);
      border: 1px solid var(--card-border);
      backdrop-filter: blur(12px) saturate(120%);
    }
    .hero-title { font-size: 56px; font-weight: 800; color: var(--accent1); margin: 0; letter-spacing: -0.6px; }
    .hero-sub { font-size: 18px; font-weight: 700; color: var(--accent2); margin-top: 8px; }
    .hero-desc { color: rgba(238,209,255,0.95); margin-top: 12px; max-width: 880px; line-height: 1.6; }
    .cta { display:flex; gap:12px; margin-top: 18px; }
    .btn-primary { background: linear-gradient(90deg,var(--accent1),var(--accent2)); color:#081018; padding:10px 18px; border-radius:20px; font-weight:800; text-decoration:none; box-shadow: 0 12px 40px rgba(170,110,255,0.12); }
    .btn-ghost { background:transparent; border:1px solid rgba(255,255,255,0.05); color:var(--accent2); padding:10px 16px; border-radius:20px; font-weight:700; text-decoration:none; }
    .socials { margin-top:12px; display:flex; gap:10px; }
    .social { width:44px; height:44px; border-radius:10px; background:rgba(255,255,255,0.02); display:flex; align-items:center; justify-content:center; font-weight:800; color:#fff; text-decoration:none; box-shadow:0 8px 28px rgba(120,0,255,0.06); }
    /* floating left icons */
    .floating-left { position: fixed; top: 28%; left: 20px; z-index: 9998; display:flex; flex-direction:column; gap:18px; }
    .float-icon { width:64px; height:64px; border-radius:50%; display:flex; align-items:center; justify-content:center; background: linear-gradient(180deg, rgba(150,50,255,0.22), rgba(120,10,200,0.14)); box-shadow: 0 12px 40px rgba(140,40,180,0.14); cursor:pointer; font-size:24px; color: var(--accent1); border: 2px solid rgba(255,140,255,0.18); transition: transform .18s ease, box-shadow .18s ease; }
    .float-icon:hover { transform: translateX(6px) scale(1.06); box-shadow: 0 18px 48px rgba(255,120,200,0.12); }
    /* chat pill bottom-right */
    .chat-pill { position: fixed; right:18px; bottom:18px; z-index:9999; padding:12px 16px; border-radius:28px; background: linear-gradient(90deg,var(--accent1),var(--accent2)); color:#081018; font-weight:800; box-shadow: 0 20px 60px rgba(0,0,0,0.36); cursor:pointer; display:flex; align-items:center; gap:10px; }
    /* chat slide-up container */
    .slide-chat { position: fixed; right: 18px; bottom: 86px; z-index: 20000; width: 360px; max-width: 88%; border-radius:12px; padding:12px; background: rgba(12,8,18,0.96); box-shadow: 0 30px 90px rgba(0,0,0,0.6); border: 1px solid rgba(255,140,255,0.12); transform: translateY(24px); opacity: 0; transition: transform .28s cubic-bezier(.2,.9,.2,1), opacity .28s; }
    .slide-chat.open { transform: translateY(0); opacity: 1; }
    @media (max-width:880px) {
      .hero-title { font-size: 36px; }
      .floating-left { left: 8px; transform: none; }
      .nav { left: 6px; width: calc(100% - 12px); transform: none; }
      .hero-card { padding: 20px; border-radius: 16px; }
      .slide-chat { right: 8px; left: 8px; width: auto; }
    }
    </style>

    <div class="nav" id="site-nav">
      <div style="display:flex;gap:14px;align-items:center">
        <div class="brand">Aryan</div>
        <div class="nav-links">
          <a class="nav-link" href="#home">Home</a>
          <a class="nav-link" href="#about">About</a>
          <a class="nav-link" href="#projects">Projects</a>
          <a class="nav-link" href="#experience">Experience</a>
        </div>
      </div>
      <div style="display:flex;gap:12px;align-items:center">
        <a class="nav-link" href="#photos" id="nav-photos">Photos</a>
        <a class="nav-link" href="?page=writings" id="nav-writings">Writings</a>
        <a class="nav-link" href="#contact">Contact</a>
      </div>
    </div>

    <div id="home" class="hero-wrap">
      <canvas id="particles-small" style="position:absolute; inset:0; z-index:0; width:100%; height:100%;"></canvas>
      <div class="hero-card" style="position:relative; z-index:2">
        <div style="position:relative; z-index:2">
          <div class="hero-title">__HERO_NAME__</div>
          <div class="hero-sub">__HERO_SUB__</div>
          <div class="hero-desc">Welcome to my personal website — explore projects, photos, writings, and chat with my AI assistant.</div>
          <div class="cta">
            <a class="btn-primary" href="/resume.pdf" target="_blank">Download Resume</a>
            <a class="btn-ghost" href="#contact">Get In Touch</a>
          </div>
          <div class="socials">
            <a class="social" target="_blank" href="https://github.com/Aryansharma99999">GH</a>
            <a class="social" target="_blank" href="https://instagram.com/aryanxsharma26">IG</a>
          </div>
        </div>
      </div>
    </div>

    <div class="floating-left" aria-hidden="false">
      <div class="float-icon" id="open-photos" title="Photos">📷</div>
      <div class="float-icon" id="open-writings" title="Writings">✍</div>
      <a href="https://instagram.com/aryanxsharma26" target="_blank"><div class="float-icon" title="Instagram">IG</div></a>
      <a href="https://github.com/Aryansharma99999" target="_blank"><div class="float-icon" title="GitHub">GH</div></a>
    </div>

    <div class="chat-pill" id="chat-pill">Ask Aryan</div>
    <div id="chat-container-root"></div>

    <script>
    // small white particles canvas
    (function(){
      const c = document.getElementById('particles-small');
      if(c){
        const ctx = c.getContext('2d');
        function fitCanvas(){
          c.width = c.clientWidth * devicePixelRatio;
          c.height = c.clientHeight * devicePixelRatio;
          ctx.scale(devicePixelRatio, devicePixelRatio);
        }
        fitCanvas();
        window.addEventListener('resize', function(){ fitCanvas(); });

        const W = c.clientWidth;
        const H = c.clientHeight;
        const particles = [];
        const N = Math.floor((W*H)/12000); // density tweak
        for(let i=0;i<N;i++){
          particles.push({
            x: Math.random()*W,
            y: Math.random()*H,
            r: (Math.random()*1.6)+0.6, // small dots
            vy: (Math.random()*0.3)+0.02,
            alpha: 0.6 + Math.random()*0.4
          });
        }
        function tick(){
          ctx.clearRect(0,0,c.clientWidth,c.clientHeight);
          for(let p of particles){
            p.y += p.vy;
            if(p.y > c.clientHeight + 6) { p.y = -6; p.x = Math.random()*c.clientWidth; }
            ctx.beginPath();
            ctx.fillStyle = 'rgba(255,255,255,' + (p.alpha*0.95) + ')';
            ctx.arc(p.x, p.y, p.r, 0, Math.PI*2);
            ctx.fill();
          }
          requestAnimationFrame(tick);
        }
        tick();
      }

      // nav smooth anchors:
      document.querySelectorAll('.nav-links a, .nav .nav-link').forEach(function(a){
        a.addEventListener('click', function(e){
          var href = this.getAttribute('href');
          if(!href) return;
          if(href.startsWith('#')){
            e.preventDefault();
            var id = href.slice(1);
            var el = document.getElementById(id);
            if(el) el.scrollIntoView({behavior:'smooth', block:'start'});
          }
        });
      });

      // floating icons behavior:
      document.getElementById('open-photos').addEventListener('click', function(){
        var qp = new URLSearchParams(window.location.search);
        qp.set('show_photos','1');
        window.location.search = qp.toString();
      });
      document.getElementById('open-writings').addEventListener('click', function(){
        var qp = new URLSearchParams(window.location.search);
        qp.set('page','writings');
        window.location.search = qp.toString();
      });

      // chat pill slide up (C2)
      var open = false;
      document.getElementById('chat-pill').addEventListener('click', function(){
        var root = document.getElementById('chat-container-root');
        if(open){
          var el = document.getElementById('slide-chat');
          if(el){ el.classList.remove('open'); setTimeout(function(){ if(el) el.remove(); }, 300); }
          open = false;
          return;
        }
        var chat = document.createElement('div');
        chat.id = 'slide-chat';
        chat.className = 'slide-chat';
        chat.innerHTML = `
          <div style="font-weight:800;color:var(--accent1);margin-bottom:8px">Aryan's AI Chatbot</div>
          <div id="chat-history" style="background:rgba(255,255,255,0.02);height:220px;border-radius:8px;padding:8px;overflow:auto;color:#e6f7ff">Hi! Ask me questions about Aryan.</div>
          <div style="display:flex;gap:8px;margin-top:8px">
            <input id="chat-input" placeholder="Type a question..." style="flex:1;padding:8px;border-radius:8px;border:1px solid rgba(255,255,255,0.04);background:transparent;color:#e6f7ff"/>
            <button id="chat-send" style="padding:8px 12px;border-radius:8px;background:linear-gradient(90deg,var(--accent1),var(--accent2));border:none;color:#081018;font-weight:800">Ask</button>
          </div>
        `;
        root.appendChild(chat);
        setTimeout(function(){ chat.classList.add('open'); }, 40);
        open = true;

        // canned local answers (replace with your bot backend if desired)
        document.getElementById('chat-send').addEventListener('click', function(){
          var v = document.getElementById('chat-input').value || "";
          if(!v.trim()) return;
          var h = document.getElementById('chat-history');
          var u = document.createElement('div'); u.style.marginTop = '8px'; u.style.fontWeight='700'; u.style.color='#dbe8ff'; u.textContent = v;
          h.appendChild(u);
          var a = document.createElement('div'); a.style.marginTop = '6px'; a.style.color = '#cfe8ff'; a.textContent = "Sorry! I don't have an answer for that.";
          h.appendChild(a);
          h.scrollTop = h.scrollHeight;
          document.getElementById('chat-input').value = '';
        });
      });

    })();
    </script>
    """
    # replace placeholders
    html = html.replace("__HERO_NAME__", HERO_NAME).replace("__HERO_SUB__", HERO_SUB)
    components.html(html, height=820, scrolling=False)

# ---------- Sections: About / Projects / Experience / Photos / Blog / Contact ----------
def render_sections(page):
    if page == "writings":
        st.markdown("<div style='padding:48px 20px;max-width:1100px;margin:auto'>", unsafe_allow_html=True)
        st.markdown('<h1 style="color:var(--accent1);font-size:32px">Writings (anonymous)</h1>', unsafe_allow_html=True)
        msgs = load_anonymous_messages()
        if not msgs:
            st.markdown('<p style="color:rgba(238,209,255,0.95)">No writings yet. Visitors can submit anonymously using the left ✍ icon or the site form.</p>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin-top:16px">', unsafe_allow_html=True)
            for m in sorted(msgs, key=lambda x: x.get("id",0), reverse=True):
                txt = m.get("text","")
                ts = m.get("timestamp","")
                card = f'<div style="background:linear-gradient(180deg,#fff,#fbf9ff);padding:14px;border-radius:10px;color:#0b0f14"><div style="font-weight:700">{txt}</div><div style="font-size:12px;color:rgba(0,0,0,0.45);margin-top:8px">{ts}</div></div>'
                st.markdown(card, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with st.form("anon_submit", clear_on_submit=True):
            txt = st.text_area("Share anonymously", placeholder="Write something...", height=140)
            submitted = st.form_submit_button("Send anonymously")
            if submitted and txt and txt.strip():
                save_anonymous_message(txt.strip())
                st.success("Message saved anonymously.")
                st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # About
    st.markdown('<div id="about" style="min-height:72vh;padding:28px"><div style="max-width:1100px;margin:auto">', unsafe_allow_html=True)
    st.markdown(f'<h2 style="color:var(--accent1);font-size:34px">About</h2>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:rgba(238,209,255,0.95);line-height:1.6">Hi I am <strong style="color:#fff">{HERO_NAME}</strong>. {HERO_SUB}. I build polished websites, experiment with AI-driven tools, write, and create. Use the floating icons to view photos or write anonymously.</p>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    # Projects
    projects = [
        {"title": "Draw App", "desc": "Collaborative drawing app — still building UI & realtime features."},
        {"title": "Portfolio Builder", "desc": "Template-driven portfolio generator — polished UIs & deploy flow."}
    ]
    proj_html = """
    <div id='projects' style='min-height:60vh;padding:20px'>
      <div style='max-width:1100px;margin:auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px'>
    """
    for p in projects:
        proj_html += f"""
        <div style="padding:18px;border-radius:16px;background:var(--card-fill);box-shadow:0 18px 60px rgba(0,0,0,0.4);border:1px solid var(--card-border)">
          <div style="font-weight:800;color:var(--accent1);font-size:20px">{p['title']}</div>
          <div style="color:rgba(238,209,255,0.92);margin-top:10px">{p['desc']}</div>
        </div>
        """
    proj_html += "</div></div>"
    st.markdown(proj_html, unsafe_allow_html=True)

    # Experience
    st.markdown('<div id="experience" style="min-height:48vh;padding:28px"><div style="max-width:1100px;margin:auto">', unsafe_allow_html=True)
    st.markdown('<h2 style="color:var(--accent1);font-size:34px">Experience</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:rgba(238,209,255,0.95)">Working on personal projects focused on web & AI — building polished experiences and learning continuously. More content coming soon.</p>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    # Photos preview grid (reads images in repo root)
    imgs = get_gallery_images()
    if imgs:
        html = "<div id='photos' style='min-height:64vh;padding:28px'><div style='max-width:1100px;margin:auto'><h2 style='color:var(--accent1);font-size:34px'>Photos</h2>"
        html += "<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-top:12px'>"
        for im in imgs:
            html += f"<div style='border-radius:10px;overflow:hidden;box-shadow:0 12px 40px rgba(0,0,0,0.35);border:1px solid rgba(255,255,255,0.02)'><img src='{im}' style='width:100%;height:160px;object-fit:cover;display:block'/></div>"
        html += "</div></div></div>"
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown("<div id='photos' style='min-height:48vh;padding:28px'><div style='max-width:1100px;margin:auto'><h2 style='color:var(--accent1);font-size:34px'>Photos</h2><p style='color:rgba(238,209,255,0.85)'>No photos found — add JPG/PNG images to the repo root.</p></div></div>", unsafe_allow_html=True)

    # Blog (simple list)
    posts = get_all_posts()
    st.markdown('<div id="blog" style="min-height:48vh;padding:28px"><div style="max-width:1100px;margin:auto">', unsafe_allow_html=True)
    st.markdown('<h2 style="color:var(--accent1);font-size:34px">Blog</h2>', unsafe_allow_html=True)
    if not posts:
        st.markdown('<p style="color:rgba(238,209,255,0.85)">No blog posts yet — add markdown files to blog_posts/</p>', unsafe_allow_html=True)
    else:
        for p in posts:
            st.markdown(f'<div style="margin-top:10px;padding:12px;border-radius:10px;background:var(--card-fill);border:1px solid var(--card-border)"><b style="color:var(--accent1)">{p["title"]}</b><div style="color:rgba(238,209,255,0.6)">{p["date"]}</div><p style="color:rgba(238,209,255,0.95)">{p["summary"]}</p></div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    # Contact
    st.markdown('<div id="contact" style="min-height:40vh;padding:28px"><div style="max-width:1100px;margin:auto">', unsafe_allow_html=True)
    st.markdown('<h2 style="color:var(--accent1);font-size:34px">Contact</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:rgba(238,209,255,0.95)">Email: <a href="mailto:aryanxsharma26@gmail.com" style="color:var(--accent1)">aryanxsharma26@gmail.com</a></p>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

# ---------- Query params: show_photos modal ----------
def handle_query_params():
    qp = st.experimental_get_query_params()
    # photos modal
    if "show_photos" in qp and qp.get("show_photos", [""])[0] == "1":
        imgs = get_gallery_images()
        if not imgs:
            components.html("<div style='position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);background:#0b0c10;padding:18px;border-radius:10px;color:#fff'>No photos found. Add images to repo root. <a href='.' style='color:#fff'>Close</a></div>", height=220)
            return
        # modal
        html = "<div style='position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);z-index:30000;background:linear-gradient(180deg,rgba(12,8,18,0.98),rgba(18,12,22,0.98));padding:18px;border-radius:12px;box-shadow:0 30px 90px rgba(0,0,0,0.6);max-width:92%;width:920px;color:#fff'>"
        html += "<div style='display:flex;justify-content:space-between;align-items:center'><div style='font-weight:800;color:var(--accent1)'>Photos</div><div><a href='.' style='color:#fff;text-decoration:none;font-weight:700'>Close ✖</a></div></div>"
        html += "<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin-top:12px'>"
        for img in imgs:
            html += f"<div style='border-radius:8px;overflow:hidden'><img src='{img}' style='width:100%;height:160px;object-fit:cover;display:block;border-radius:6px'/></div>"
        html += "</div></div>"
        components.html(html, height=680, scrolling=False)
        return

    # anon message via qp (optional)
    if "anon_q" in qp:
        q = qp.get("anon_q", [""])[0]
        if q and q.strip():
            save_anonymous_message(q.strip())
            st.experimental_set_query_params()
            st.experimental_rerun()

# ---------- Admin (hidden via ?admin=admin-aryan) ----------
def admin_sidebar():
    qp = st.experimental_get_query_params()
    tok = qp.get("admin", [""])[0]
    unlocked = False
    if tok == "admin-aryan":
        unlocked = True
    if unlocked:
        st.sidebar.title("Admin — Anonymous messages")
        msgs = load_anonymous_messages()
        st.sidebar.write("Total:", len(msgs))
        for m in sorted(msgs, key=lambda x: x.get("id",0), reverse=True):
            st.sidebar.markdown(f"**{m.get('timestamp')}**")
            st.sidebar.write(m.get("text"))
            if st.sidebar.button(f"Delete {m.get('id')}", key=f"del_{m.get('id')}"):
                new = [x for x in msgs if x.get("id") != m.get("id")]
                try:
                    with open(MSG_FILE, "w", encoding="utf-8") as f:
                        for item in new:
                            f.write(json.dumps(item, ensure_ascii=False) + "\n")
                except Exception:
                    pass
                st.experimental_rerun()
        if st.sidebar.button("Clear all"):
            try:
                with open(MSG_FILE, "w", encoding="utf-8") as f:
                    f.write("")
            except Exception:
                pass
            st.experimental_rerun()

# ---------- Main ----------
def main():
    inject_global_css_js()
    handle_query_params()
    page = st.experimental_get_query_params().get("page", [""])[0]
    render_hero_and_nav()
    render_sections(page or "home")
    admin_sidebar()
    st.markdown('<div style="height:60px"></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
