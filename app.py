# # app.py
# Neon C2 single-page portfolio with popup photos, separate Writings page, and sliding chat pill.
# Requirements: streamlit, markdown, requests
# Put images (jpg/png/webp) in repo root for the photos gallery.
# Anonymous messages saved to file anonymous_messages.txt

import os
import re
import time
import json
from datetime import datetime
from markdown import markdown
import streamlit as st
import streamlit.components.v1 as components
import requests

# ---------------------------
# Config
# ---------------------------
st.set_page_config(page_title="Aryan Sharma — Portfolio", layout="wide", initial_sidebar_state="collapsed")
BASE_DIR = os.path.dirname(__file__) or "."
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")
MSG_FILE = os.path.join(BASE_DIR, "anonymous_messages.txt")

# Environment secrets (optional)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

HERO_NAME = "Aryan Sharma"
HERO_SUB  = "I'm a developer, writer, editor & learner"

# ---------------------------
# Utilities
# ---------------------------
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

    # Optional: Telegram notify (best-effort)
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            p = {"chat_id": TELEGRAM_CHAT_ID, "text": f"📨 New anonymous message:\n\n{msg['text']}\n\nID:{msg['id']}"}
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json=p, timeout=5)
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
    # optionally ignore preview images you create locally
    ignore = {"theme_preview_final.png", "final_preview_c2.png"}
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
                    k,v = ln.split(":",1)
                    meta[k.strip()] = v.strip()
            body = content[m.end():].strip()
        html = markdown(body)
        posts.append({"slug": f[:-3], "title": meta.get("title", f[:-3]), "date": meta.get("date","N/A"), "summary": meta.get("summary",""), "html": html})
    return posts

# ---------------------------
# Global CSS and JS injection
# ---------------------------
def inject_global_css_js():
    # We are not using f-strings so CSS braces don't cause a Python error
    css_js = """
    <style>
    :root{
      --c1: #ff77e9;
      --c2: #8a6aff;
      --bg-a: linear-gradient(180deg,#0b0120 0%, #120327 100%);
    }
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
      background: radial-gradient(circle at 10% 10%, rgba(255,120,200,0.04), transparent), var(--bg-a) !important;
      color: #e9e9ff;
      font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
    }
    /* hide default Streamlit menu and footer for a clean site look */
    #MainMenu, header, footer { display: none !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    /* top nav styling will be inside the hero HTML */
    /* small helper */
    a.nav-link { color: rgba(255,255,255,0.92); text-decoration: none; padding:6px 8px; border-radius:8px; font-weight:700; }
    </style>
    <script>
    // Helper to set query param without reloading (we will use reload for popups intentionally)
    function setQueryParams(params) {
      const url = new URL(window.location);
      Object.keys(params).forEach(k => url.searchParams.set(k, params[k]));
      window.history.replaceState({}, '', url);
    }
    </script>
    """
    st.markdown(css_js, unsafe_allow_html=True)

# ---------------------------
# Hero / Nav Component (HTML + JS)
# ---------------------------
def render_hero_and_nav():
    # We'll provide anchors for scroll: #home #about #projects #experience #photos #blog #writings #contact
    html = """
    <style>
    /* HERO + NAV styles */
    .nav {
      position: fixed; top: 18px; left: 50%; transform: translateX(-50%); z-index: 9999;
      width: 92%; max-width: 1200px; display:flex; align-items:center; justify-content:space-between;
      padding: 10px 18px; border-radius: 12px; backdrop-filter: blur(8px) saturate(120%);
      background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.02);
      box-shadow: 0 18px 50px rgba(0,0,0,0.55);
    }
    .brand { font-weight:800; color: var(--c1); font-size: 18px; }
    .nav-links { display:flex; gap:12px; align-items:center; }
    .nav-links a { color: rgba(255,255,255,0.9); text-decoration:none; padding:6px 8px; border-radius:8px; font-weight:700; }
    .hero-wrap { height: 82vh; min-height: 520px; display:flex; align-items:center; justify-content:center; padding: 36px 20px; }
    .hero-card {
      width: min(1100px,96%); border-radius: 24px; padding: 34px; position: relative; overflow: hidden;
      box-shadow: 0 30px 100px rgba(0,0,0,0.45);
      background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
      border: 1px solid rgba(138,106,255,0.08);
    }
    .hero-title { font-size: 48px; font-weight: 800; color: var(--c1); margin: 0; }
    .hero-sub { font-size: 18px; font-weight: 700; color: var(--c2); margin-top: 8px; }
    .hero-desc { color: rgba(255,255,255,0.9); margin-top: 12px; max-width: 880px; line-height: 1.6; }
    .cta { display:flex; gap:12px; margin-top: 16px; }
    .btn-primary { background: linear-gradient(90deg,var(--c1),var(--c2)); color:#081018; padding:10px 18px; border-radius:20px; font-weight:800; text-decoration:none; }
    .btn-ghost { background:transparent; border:1px solid rgba(255,255,255,0.04); color:var(--c2); padding:10px 16px; border-radius:20px; font-weight:700; text-decoration:none; }
    .socials { margin-top:12px; display:flex; gap:10px; }
    .social { width:44px; height:44px; border-radius:10px; background:rgba(255,255,255,0.02); display:flex; align-items:center; justify-content:center; font-weight:800; color:#fff; text-decoration:none; }
    /* floating left pure-emoji icons */
    .floating-tools { position: fixed; left:12px; top: 50%; transform: translateY(-50%); z-index: 9998; display:flex; flex-direction:column; gap:18px; }
    .tool { width:60px; height:60px; border-radius:50%; display:flex; align-items:center; justify-content:center; background:linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02)); box-shadow: 0 10px 30px rgba(0,0,0,0.6); cursor:pointer; font-size:26px; }
    .tool:hover { transform: translateX(8px); transition: transform .18s ease; }
    /* Chat pill (bottom-left) */
    .chat-pill { position: fixed; left:18px; bottom:18px; z-index:9999; padding:12px 16px; border-radius:28px; background: linear-gradient(90deg,var(--c1),var(--c2)); color:#081018; font-weight:800; box-shadow: 0 20px 60px rgba(0,0,0,0.4); cursor:pointer; display:flex; align-items:center; gap:10px; }
    /* Chat sliding container - will be injected */
    .slide-chat { position: fixed; left: 18px; bottom: 86px; z-index: 20000; width: 360px; max-width: 88%; border-radius:10px; padding:12px; background: linear-gradient(180deg, rgba(6,6,10,0.96), rgba(18,12,22,0.96)); box-shadow: 0 30px 90px rgba(0,0,0,0.6); border: 1px solid rgba(255,255,255,0.03); transform: translateY(24px); opacity: 0; transition: transform .28s cubic-bezier(.2,.9,.2,1), opacity .28s; }
    .slide-chat.open { transform: translateY(0); opacity: 1; }
    @media (max-width:880px) {
      .hero-title { font-size: 34px; }
      .hero-card { padding: 20px; border-radius: 16px; }
      .floating-tools { left:8px; }
      .nav { left: 6px; width: calc(100% - 12px); transform: none; }
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
      <div class="hero-card">
        <div style="position:absolute; inset:0; z-index:0; pointer-events:none" id="particles-root"></div>
        <div style="position:relative; z-index:2">
          <div class="hero-title">__HERO_NAME__</div>
          <div class="hero-sub">__HERO_SUB__</div>
          <div class="hero-desc">Welcome to my personal website — explore projects, photos, writings, and chat with my AI assistant.</div>
          <div class="cta">
            <a class="btn-primary" href="/resume.pdf" target="_blank">Download Resume</a>
            <a class="btn-ghost" href="#contact">Get In Touch</a>
          </div>
          <div class="socials">
            <a class="social" target="_blank" href="https://github.com/aryansharma99999">GH</a>
            <a class="social" target="_blank" href="https://instagram.com/aryanxsharma26">IG</a>
          </div>
        </div>
      </div>
    </div>

    <!-- floating left icons -->
    <div class="floating-tools" aria-hidden="false">
      <div class="tool" id="open-photos" title="Photos">📷</div>
      <div class="tool" id="open-writings" title="Writings">✍</div>
    </div>

    <!-- chat pill -->
    <div class="chat-pill" id="chat-pill">Ask Aryan</div>

    <div id="chat-container-root"></div>

    <script>
    // particles small engine (lightweight effect)
    (function(){
      function createParticles(root) {
        if(!root) return;
        var w = root.clientWidth, h = root.clientHeight;
        var c = document.createElement('canvas');
        c.width = w; c.height = h; c.style.width='100%'; c.style.height='100%'; c.style.display='block';
        root.appendChild(c);
        var ctx = c.getContext('2d');
        var parts = [];
        for(var i=0;i<40;i++){
          parts.push({x: Math.random()*w, y: Math.random()*h, r: Math.random()*2+0.6, sx: (Math.random()-0.5)*0.15, sy: Math.random()*0.2+0.02, hue: Math.random()*360});
        }
        function tick(){
          ctx.clearRect(0,0,w,h);
          for(var i=0;i<parts.length;i++){
            var p = parts[i];
            p.x += p.sx; p.y += p.sy;
            if(p.y > h+10) { p.y = -10; p.x = Math.random()*w; }
            ctx.beginPath();
            var grad = ctx.createRadialGradient(p.x,p.y,p.r*0.1,p.x,p.y,p.r*6);
            grad.addColorStop(0, 'rgba(255,120,200,0.9)');
            grad.addColorStop(0.5, 'rgba(138,106,255,0.34)');
            grad.addColorStop(1, 'rgba(255,120,200,0.02)');
            ctx.fillStyle = grad;
            ctx.arc(p.x,p.y, p.r*2, 0, Math.PI*2);
            ctx.fill();
          }
          requestAnimationFrame(tick);
        }
        tick();
        window.addEventListener('resize', function(){ c.width = root.clientWidth; c.height = root.clientHeight; w=c.width; h=c.height; });
      }
      createParticles(document.getElementById('particles-root'));

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

      // floating icons handlers:
      document.getElementById('open-photos').addEventListener('click', function(){
        var qp = new URLSearchParams(window.location.search);
        qp.set('show_photos','1');
        window.location.search = qp.toString();
      });
      document.getElementById('open-writings').addEventListener('click', function(){
        // user chose W3 = separate page: open ?page=writings
        var qp = new URLSearchParams(window.location.search);
        qp.set('page','writings');
        window.location.search = qp.toString();
      });

      // chat pill slide up (C2)
      var open = false;
      document.getElementById('chat-pill').addEventListener('click', function(){
        var root = document.getElementById('chat-container-root');
        if(open){
          // close
          var el = document.getElementById('slide-chat');
          if(el){ el.classList.remove('open'); setTimeout(function(){ if(el) el.remove(); }, 300); }
          open = false;
          return;
        }
        var chat = document.createElement('div');
        chat.id = 'slide-chat';
        chat.className = 'slide-chat';
        chat.innerHTML = `
          <div style="font-weight:800;color:#8fdcff;margin-bottom:8px">Aryan's AI Chatbot</div>
          <div id="chat-history" style="background:rgba(255,255,255,0.02);height:200px;border-radius:8px;padding:8px;overflow:auto;color:#e6f7ff">Hi! Ask me questions about Aryan.</div>
          <div style="display:flex;gap:8px;margin-top:8px">
            <input id="chat-input" placeholder="Type a question..." style="flex:1;padding:8px;border-radius:8px;border:1px solid rgba(255,255,255,0.04);background:transparent;color:#e6f7ff"/>
            <button id="chat-send" style="padding:8px 12px;border-radius:8px;background:linear-gradient(90deg,#ff77e9,#8a6aff);border:none;color:#081018;font-weight:800">Ask</button>
          </div>
        `;
        root.appendChild(chat);
        setTimeout(function(){ chat.classList.add('open'); }, 40);
        open = true;

        // send handler (local canned answer)
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
    # insert hero variables safely
    html = html.replace("__HERO_NAME__", HERO_NAME).replace("__HERO_SUB__", HERO_SUB)
    components.html(html, height=820, scrolling=False)

# ---------------------------
# Sections (About / Projects / Experience / Photos / Blog / Contact)
# ---------------------------
def render_sections(page):
    if page == "writings":
        # separate Writings page (W3)
        st.markdown("<div style='padding:48px 20px;max-width:1100px;margin:auto'>", unsafe_allow_html=True)
        st.markdown('<h1 style="color:var(--c1);font-size:32px">Writings (anonymous)</h1>', unsafe_allow_html=True)
        msgs = load_anonymous_messages()
        if not msgs:
            st.markdown('<p style="color:rgba(255,255,255,0.85)">No writings yet. Visitors can submit anonymously using the left ✍ icon or the site form.</p>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin-top:16px">', unsafe_allow_html=True)
            for m in sorted(msgs, key=lambda x: x.get("id",0), reverse=True):
                txt = m.get("text","")
                ts = m.get("timestamp","")
                card = f'<div style="background:linear-gradient(180deg,#fff,#fbf9ff);padding:14px;border-radius:10px;color:#0b0f14"><div style="font-weight:700">{txt}</div><div style="font-size:12px;color:rgba(0,0,0,0.45);margin-top:8px">{ts}</div></div>'
                st.markdown(card, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        # quick form to submit anonymously (also used by popup)
        with st.form("anon_submit", clear_on_submit=True):
            txt = st.text_area("Share anonymously", placeholder="Write something...", height=140)
            submitted = st.form_submit_button("Send anonymously")
            if submitted and txt and txt.strip():
                save_anonymous_message(txt.strip())
                st.success("Message saved anonymously.")
                st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # Default main page sections
    st.markdown('<div id="about" style="min-height:72vh;padding:28px"><div style="max-width:1100px;margin:auto">', unsafe_allow_html=True)
    st.markdown(f'<h2 style="color:var(--c1);font-size:34px">About</h2>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:rgba(255,255,255,0.9);line-height:1.6">Hi I am <strong style="color:#fff">{HERO_NAME}</strong>. {HERO_SUB}. I build polished websites, experiment with AI-driven tools, write, and create. Use the floating icons to view photos or write anonymously.</p>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    # Projects: 2 cards in a responsive grid
    projects = [
        {"title":"Draw App", "desc":"Collaborative drawing app — still building UI & realtime features."},
        {"title":"Portfolio Builder", "desc":"Template-driven portfolio generator — polished UIs & deploy flow."}
    ]
    proj_html = """
    <div id="projects" style="min-height:60vh;padding:20px">
      <div style="max-width:1100px;margin:auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px">
    """
    for p in projects:
        proj_html += f"""
        <div style="padding:18px;border-radius:16px;background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));box-shadow:0 18px 60px rgba(0,0,0,0.4)">
          <div style="font-weight:800;color:#fff;font-size:20px">{p['title']}</div>
          <div style="color:rgba(255,255,255,0.85);margin-top:10px">{p['desc']}</div>
        </div>
        """
    proj_html += "</div></div>"
    st.markdown(proj_html, unsafe_allow_html=True)

    # Experience section
    st.markdown('<div id="experience" style="min-height:48vh;padding:28px"><div style="max-width:1100px;margin:auto">', unsafe_allow_html=True)
    st.markdown('<h2 style="color:var(--c1);font-size:34px">Experience</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:rgba(255,255,255,0.9)">Working on personal projects focused on web & AI — building polished experiences and learning continuously. More content coming soon.</p>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    # Photos section (inline grid preview)
    imgs = get_gallery_images()
    if imgs:
        html = "<div id='photos' style='min-height:64vh;padding:28px'><div style='max-width:1100px;margin:auto'><h2 style='color:var(--c1);font-size:34px'>Photos</h2>"
        html += "<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-top:12px'>"
        for im in imgs:
            html += f"<div style='border-radius:10px;overflow:hidden'><img src='{im}' style='width:100%;height:160px;object-fit:cover;display:block'/></div>"
        html += "</div></div></div>"
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown("<div id='photos' style='min-height:48vh;padding:28px'><div style='max-width:1100px;margin:auto'><h2 style='color:var(--c1);font-size:34px'>Photos</h2><p style='color:rgba(255,255,255,0.85)'>No photos found — add JPG/PNG images to the repo root.</p></div></div>", unsafe_allow_html=True)

    # Blog (simple list)
    posts = get_all_posts()
    st.markdown('<div id="blog" style="min-height:48vh;padding:28px"><div style="max-width:1100px;margin:auto">', unsafe_allow_html=True)
    st.markdown('<h2 style="color:var(--c1);font-size:34px">Blog</h2>', unsafe_allow_html=True)
    if not posts:
        st.markdown('<p style="color:rgba(255,255,255,0.85)">No blog posts yet — add markdown files to blog_posts/</p>', unsafe_allow_html=True)
    else:
        for p in posts:
            st.markdown(f'<div style="margin-top:10px;padding:12px;border-radius:10px;background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01))"><b style="color:#fff">{p["title"]}</b><div style="color:rgba(255,255,255,0.6)">{p["date"]}</div><p style="color:rgba(255,255,255,0.85)">{p["summary"]}</p></div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    # Contact
    st.markdown('<div id="contact" style="min-height:40vh;padding:28px"><div style="max-width:1100px;margin:auto">', unsafe_allow_html=True)
    st.markdown('<h2 style="color:var(--c1);font-size:34px">Contact</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:rgba(255,255,255,0.9)">Email: <a href="mailto:aryanxsharma26@gmail.com" style="color:#fff">aryanxsharma26@gmail.com</a></p>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

# ---------------------------
# Query param popups: show_photos (P1) opens a modal gallery
# ---------------------------
def handle_query_params():
    qp = st.experimental_get_query_params()
    # photo modal
    if "show_photos" in qp and qp.get("show_photos", [""])[0] == "1":
        imgs = get_gallery_images()
        if not imgs:
            components.html("<div style='position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);background:#0b0c10;padding:18px;border-radius:10px;color:#fff'>No photos found. Add images to repo root. <a href='.' style='color:#fff'>Close</a></div>", height=220)
            return
        # create a simple modal
        html = "<div style='position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);z-index:30000;background:linear-gradient(180deg,rgba(12,8,16,0.98),rgba(18,12,22,0.98));padding:18px;border-radius:12px;box-shadow:0 30px 90px rgba(0,0,0,0.6);max-width:92%;width:920px;color:#fff'>"
        html += "<div style='display:flex;justify-content:space-between;align-items:center'><div style='font-weight:800;color:#ff9bdc'>Photos</div><div><a href='.' style='color:#fff;text-decoration:none;font-weight:700'>Close ✖</a></div></div>"
        html += "<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin-top:12px'>"
        for img in imgs:
            html += f"<div style='border-radius:8px;overflow:hidden'><img src='{img}' style='width:100%;height:160px;object-fit:cover;display:block;border-radius:6px'/></div>"
        html += "</div></div>"
        components.html(html, height=680, scrolling=False)
        return

    # anonymous message submit via query param (optional)
    if "anon_q" in qp:
        q = qp.get("anon_q", [""])[0]
        if q and q.strip():
            save_anonymous_message(q.strip())
            # clear params and refresh
            st.experimental_set_query_params()
            st.experimental_rerun()

# ---------------------------
# Admin (hidden) - optional: reveal via ?admin=token
# ---------------------------
def admin_sidebar():
    qp = st.experimental_get_query_params()
    admin_token = qp.get("admin", [""])[0]
    unlocked = False
    if admin_token == "admin-aryan":
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

# ---------------------------
# Main
# ---------------------------
def main():
    inject_global_css_js()
    handle_query_params()       # handles show_photos and anon_q
    page = st.experimental_get_query_params().get("page", [""])[0]
    render_hero_and_nav()

    # render sections or separate writing page
    render_sections(page or "home")

    # admin sidebar (optional)
    admin_sidebar()

    # small spacer
    st.markdown('<div style="height:60px"></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
