# app.py
# Neon C2 portfolio - final polished version
# - Pure emoji left icons (📷 ✍)
# - Chat pill bottom-left expands UP
# - Photos & Writings open as floating popups (L2)
# - Particles (tsparticles) loaded via CDN
# - Environment variables for Telegram (S2)
# - No secrets hard-coded

import os
import re
import json
import time
import requests
from datetime import datetime
from markdown import markdown
import streamlit as st
import streamlit.components.v1 as components

# -------------------------
# Config
# -------------------------
st.set_page_config(page_title="Aryan Sharma — Portfolio", layout="wide", initial_sidebar_state="collapsed")
BASE_DIR = os.path.dirname(__file__) or "."
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")
MSG_FILE = os.path.join(BASE_DIR, "anonymous_messages.txt")

ADMIN_TOKEN = "admin-aryan"            # admin unlock via ?admin=admin-aryan
ADMIN_QP = "admin"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")  # safe: set in env
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

HERO_NAME = "Aryan Sharma"
HERO_SUB = "I'm a developer, writer, editor & learner"

# -------------------------
# Utilities: messages, posts, gallery
# -------------------------
def ensure_file(path):
    try:
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                pass
    except Exception:
        pass

def save_anonymous_message(text: str):
    ensure_file(MSG_FILE)
    msg = {"id": int(time.time() * 1000), "text": text, "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}
    try:
        with open(MSG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(msg, ensure_ascii=False) + "\n")
    except Exception:
        pass

    # optional: send to Telegram (best-effort)
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": f"📨 New anonymous message:\n\n{msg['text']}\n\nID:{msg['id']}"}
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json=payload, timeout=6)
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
                if not line: continue
                try:
                    out.append(json.loads(line))
                except Exception:
                    continue
    except Exception:
        return []
    return out

def overwrite_anonymous_messages(msgs):
    try:
        with open(MSG_FILE, "w", encoding="utf-8") as f:
            for m in msgs:
                f.write(json.dumps(m, ensure_ascii=False) + "\n")
    except Exception:
        pass

# Blog helpers
def get_post(slug):
    path = os.path.join(POSTS_DIR, f"{slug}.md")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    meta = {}
    body = content
    m = re.match(r'---\n(.*?)\n---', content, re.DOTALL)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = content[m.end():].strip()
    html = markdown(body)
    return {"slug": slug, "title": meta.get("title", "Untitled"), "date": meta.get("date","N/A"), "author": meta.get("author","N/A"), "summary": meta.get("summary",""), "html": html}

def get_all_posts():
    if not os.path.exists(POSTS_DIR):
        return []
    posts = []
    for f in os.listdir(POSTS_DIR):
        if f.endswith(".md"):
            p = get_post(f.replace(".md",""))
            if p:
                posts.append(p)
    return posts

# gallery
def get_gallery_images():
    try:
        files = os.listdir(BASE_DIR)
    except Exception:
        files = []
    imgs = [f for f in files if f.lower().endswith((".jpg",".jpeg",".png",".webp"))]
    # filter out assets we may have added intentionally
    ignore = {"preview_neon_C2.png","theme_preview_final.png"}
    return [i for i in imgs if i not in ignore]

# -------------------------
# Inject global CSS for the theme
# -------------------------
def inject_css():
    css = """
    <style>
    :root{
      --c1: #ff77e9;
      --c2: #8a6aff;
      --panel-dark: rgba(18,10,24,0.92);
      --panel-soft: rgba(255,255,255,0.02);
      --neon: linear-gradient(90deg,var(--c1),var(--c2));
    }
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"]{
      background: radial-gradient(circle at 20% 10%, rgba(255,120,200,0.06), transparent), linear-gradient(180deg, #0b0120 0%, #120327 100%) !important;
      min-height: 100% !important;
    }
    /* hide default header and footer */
    #MainMenu, header, footer { display: none !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    /* default text color */
    .stApp * { color: #e9e9ff; }
    /* full-bleed sections */
    .full-section{ width:100%; margin:0; padding:0; }
    /* scroll smooth for anchors */
    html { scroll-behavior: smooth; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# -------------------------
# Hero + Nav HTML (component)
# -------------------------
def render_hero_component():
    html = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    body{{font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto}}
    .nav {{
      position:fixed; top:18px; left:50%; transform:translateX(-50%); z-index:9999;
      width:92%; max-width:1200px; display:flex; align-items:center; justify-content:space-between;
      padding:10px 18px; border-radius:12px; backdrop-filter: blur(8px) saturate(120%);
      background: rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.02);
      box-shadow: 0 18px 50px rgba(0,0,0,0.6);
    }}
    .nav .left{display:flex;align-items:center;gap:14px}
    .brand{font-weight:800;color:var(--c1);font-size:18px}
    .nav a{color:rgba(255,255,255,0.95);text-decoration:none;padding:6px 8px;border-radius:8px;font-weight:700}
    .hero-wrap{{height:88vh;min-height:620px;display:flex;align-items:center;justify-content:center;padding:32px 28px}}
    .hero-card{{width:min(1100px,96%);border-radius:24px;padding:34px;position:relative;overflow:hidden;box-shadow:0 30px 100px rgba(0,0,0,0.45); background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));}}
    .hero-card::before{{ content:""; position:absolute; inset:0; border-radius:24px; padding:2px; pointer-events:none; box-shadow:0 0 40px rgba(138,106,255,0.05), inset 0 0 50px rgba(255,120,200,0.02); border: 2px solid rgba(138,106,255,0.12); }}
    #tsparticles{{position:absolute; inset:0; z-index:0; border-radius:24px; pointer-events:none}}
    .hero-inner{{position:relative; z-index:2; color:#fff; text-align:left}}
    .title{{font-size:48px;font-weight:800;color:var(--c1); margin:0}}
    .subtitle{{font-size:18px;font-weight:700;color:var(--c2); margin-top:8px}}
    .desc{{color:rgba(255,255,255,0.9); margin-top:14px; max-width:880px; line-height:1.6}}
    .cta{display:flex; gap:12px; margin-top:18px}
    .btn-primary{background:var(--neon); color:#081018; padding:10px 18px; border-radius:20px; font-weight:800; text-decoration:none}
    .btn-ghost{background:transparent;border:1px solid rgba(255,255,255,0.04);color:var(--c2);padding:10px 16px;border-radius:20px;font-weight:700}
    .socials{margin-top:12px; display:flex; gap:10px}
    .social{width:44px;height:44px;border-radius:10px;background:rgba(255,255,255,0.02);display:flex;align-items:center;justify-content:center;font-weight:800;color:#fff}
    /* floating tools (pure emoji icons) - middle-left */
    .floating-tools{position:fixed; left:12px; top:50%; transform:translateY(-50%); z-index:9998; display:flex; flex-direction:column; gap:18px}
    .tool-emoji{font-size:24px; cursor:pointer; transition: transform .14s ease, filter .14s ease; filter: drop-shadow(0 12px 32px rgba(138,106,255,0.06));}
    .tool-emoji:hover{ transform: translateX(8px); filter: drop-shadow(0 18px 48px rgba(255,120,200,0.12));}
    /* chat pill */
    .chat-pill{ position:fixed; left:18px; bottom:18px; z-index:9999; display:flex;align-items:center;gap:8px;padding:12px 16px;border-radius:28px;background:linear-gradient(90deg,var(--c1),var(--c2));color:#081018;font-weight:800;box-shadow:0 20px 60px rgba(0,0,0,0.4); cursor:pointer}
    .chat-pill .send-rect{ background:#081018;padding:8px 10px;border-radius:8px;color:var(--c1);font-weight:800}
    @media (max-width:880px){
      .title{font-size:34px}
      .hero-card{padding:18px;border-radius:16px}
      .floating-tools{ left:8px }
      .nav{left:6px;width:calc(100% - 12px); transform:none}
    }
    </style>

    <div class="nav" id="topnav">
      <div class="left"><div class="brand">Aryan</div>
        <div style="display:flex;gap:10px">
          <a href="#home">Home</a><a href="#about">About</a><a href="#projects">Projects</a><a href="#photos">Photos</a><a href="#blog">Blog</a>
        </div>
      </div>
      <div style="display:flex;gap:10px"><a href="#writings">Writings</a><a href="#contact">Contact</a></div>
    </div>

    <div id="home" class="hero-wrap">
      <div class="hero-card">
        <div id="tsparticles"></div>
        <div class="hero-inner">
          <h1 class="title">{HERO_NAME}</h1>
          <div class="subtitle">{HERO_SUB}</div>
          <div class="desc">Welcome to my personal website — explore projects, photos, writings, and chat with my AI assistant.</div>
          <div class="cta">
            <a class="btn-primary" href="/resume.pdf" target="_blank">Download Resume</a>
            <a class="btn-ghost" href="#contact">Get In Touch</a>
          </div>
          <div class="socials">
            <a class="social" href="https://github.com/aryansharma99999" target="_blank">GH</a>
            <a class="social" href="https://instagram.com/aryanxsharma26" target="_blank">IG</a>
          </div>
        </div>
      </div>
    </div>

    <!-- floating pure-emoji left icons -->
    <div class="floating-tools">
      <div id="open-photos" class="tool-emoji" title="Photos">📷</div>
      <div id="open-writings" class="tool-emoji" title="Writings">✍</div>
    </div>

    <!-- chat pill -->
    <div class="chat-pill" id="chat-pill" title="Ask Aryan">
      <div style="font-weight:900">Ask Aryan</div>
      <div class="send-rect">Send</div>
    </div>

    <div id="popup-root"></div>

    <!-- scripts: tsparticles, interactions -->
    <script>
    (function(){
      // load tsparticles if missing
      function loadParticles(){
        if(window.tsParticles){
          tsParticles.load("tsparticles", {
            fullScreen: { enable: false },
            detectRetina: true,
            particles: {
              number:{value:40},
              color:{value:["#ff77e9","#8a6aff","#ffd1f2"]},
              move:{enable:true,speed:0.45,outModes:"out"},
              size:{value:{min:1.2,max:4}},
              opacity:{value:0.72}
            },
            background:{color:"transparent"}
          });
        } else {
          var s = document.createElement('script');
          s.src = "https://cdn.jsdelivr.net/npm/tsparticles@2.3.4/tsparticles.bundle.min.js";
          s.onload = loadParticles;
          document.head.appendChild(s);
        }
      }
      loadParticles();

      // nav smooth anchors
      document.querySelectorAll('.nav a').forEach(a=>{
        a.addEventListener('click',function(e){
          e.preventDefault();
          var id = this.getAttribute('href').replace('#','');
          var el = document.getElementById(id);
          if(el) el.scrollIntoView({behavior:'smooth', block:'start'});
        });
      });

      // floating icons open popups by toggling query params so Streamlit handles content (L2)
      document.getElementById('open-photos').addEventListener('click',function(){
        var p = new URLSearchParams(window.location.search);
        p.set('show_photos','1');
        window.location.search = p.toString();
      });
      document.getElementById('open-writings').addEventListener('click',function(){
        var p = new URLSearchParams(window.location.search);
        p.set('show_writings','1');
        window.location.search = p.toString();
      });

      // chat pill opens chat popup above pill (expands UP)
      document.getElementById('chat-pill').addEventListener('click', function(e){
        var root = document.getElementById('popup-root');
        // if exists remove
        if(document.getElementById('chat-popup')) { document.getElementById('chat-popup').remove(); return; }
        root.innerHTML = `
          <div id="chat-popup" style="position:fixed;left:18px;bottom:86px;z-index:10000;width:360px;max-width:88%;border-radius:12px;background:linear-gradient(180deg, rgba(6,6,10,0.96), rgba(18,12,22,0.96));box-shadow:0 30px 80px rgba(0,0,0,0.6);padding:12px;border:1px solid rgba(255,255,255,0.03)">
            <div style="font-weight:800;color:#8fdcff;margin-bottom:8px">Aryan's AI Chatbot</div>
            <div id="chat-history" style="background:rgba(255,255,255,0.02);height:160px;border-radius:8px;padding:8px;overflow:auto;color:#e6f7ff">Hi! Ask me questions about Aryan.</div>
            <div style="display:flex;gap:8px;margin-top:8px">
              <input id="chat-input" placeholder="Type a question..." style="flex:1;padding:8px;border-radius:8px;border:1px solid rgba(255,255,255,0.04);background:transparent;color:#e6f7ff"/>
              <button id="chat-send" style="padding:8px 12px;border-radius:8px;background:linear-gradient(90deg,#ff77e9,#8a6aff);border:none;color:#081018;font-weight:800">Ask</button>
            </div>
          </div>
        `;
        setTimeout(()=>document.addEventListener('click', closeOut), 100);

        document.getElementById('chat-send').addEventListener('click', function(){
          var val = document.getElementById('chat-input').value || "";
          if(!val.trim()){ alert('Type a question'); return; }
          var h = document.getElementById('chat-history');
          var u = document.createElement('div'); u.style.marginTop='8px'; u.style.fontWeight='700'; u.style.color='#dbe8ff'; u.textContent = val;
          h.appendChild(u);
          var a = document.createElement('div'); a.style.marginTop='6px'; a.style.color='#cfe8ff'; a.textContent = "Sorry! I don't have an answer for that.";
          h.appendChild(a);
          h.scrollTop = h.scrollHeight;
          document.getElementById('chat-input').value = '';
        });

        function closeOut(ev){
          var pop = document.getElementById('chat-popup');
          var pill = document.getElementById('chat-pill');
          if(!pop) return;
          if(!pop.contains(ev.target) && !pill.contains(ev.target)){
            pop.remove();
            document.removeEventListener('click', closeOut);
          }
        }
      });

    })();
    </script>
    """
    components.html(html, height=880, scrolling=False)

# -------------------------
# Page sections
# -------------------------
def render_sections():
    st.markdown('<div class="full-section">', unsafe_allow_html=True)

    # About
    about_html = f"""
    <div id="about" style="min-height:84vh;display:flex;align-items:center;padding:32px 20px">
      <div style="max-width:1100px;margin:0 auto">
        <h2 style="color:var(--c1);font-size:34px;margin-bottom:6px">About</h2>
        <p style="color:rgba(255,255,255,0.92);font-size:18px;line-height:1.6">Hi, I'm <strong style="color:white">{HERO_NAME}</strong> — {HERO_SUB}. I build polished websites, experiment with AI-driven tools, write, and create. Use the floating icons to view photos or submit anonymous writings.</p>
      </div>
    </div>
    """
    st.markdown(about_html, unsafe_allow_html=True)

    # Projects (two cards)
    projects = [
        {"title":"Draw App","desc":"Collaborative drawing app — still building UI & realtime features."},
        {"title":"Portfolio Builder","desc":"Template-driven portfolio generator — polished UIs & deploy flow."}
    ]
    proj_html = """
    <style>
    .proj-section{min-height:78vh;display:flex;align-items:center;padding:20px}
    .proj-wrap{max-width:1100px;margin:0 auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px}
    .proj-card{padding:18px;border-radius:16px;background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));box-shadow:0 18px 60px rgba(0,0,0,0.4)}
    .proj-title{font-weight:800;color:#fff;font-size:20px}
    .proj-desc{color:rgba(255,255,255,0.85);margin-top:10px}
    </style>
    <div id="projects" class="proj-section"><div class="proj-wrap">
    """
    for p in projects:
        proj_html += f"<div class='proj-card'><div class='proj-title'>{p['title']}</div><div class='proj-desc'>{p['desc']}</div></div>"
    proj_html += "</div></div>"
    components.html(proj_html, height=520, scrolling=False)

    # Experience
    exp_html = """
    <div id="experience" style="min-height:60vh;padding:28px;display:flex;align-items:center">
      <div style="max-width:1100px;margin:0 auto">
        <h2 style="color:var(--c1);font-size:34px">Experience</h2>
        <p style="color:rgba(255,255,255,0.9);max-width:900px">Working on personal projects focused on web & AI — building polished experiences and learning continuously. More content coming soon.</p>
      </div>
    </div>
    """
    st.markdown(exp_html, unsafe_allow_html=True)

    # Photos (grid)
    imgs = get_gallery_images()
    if imgs:
        html = "<div id='photos' style='min-height:78vh;padding:28px'><div style='max-width:1100px;margin:0 auto'><h2 style='color:var(--c1);font-size:34px'>Photos</h2>"
        html += "<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-top:12px'>"
        for img in imgs:
            html += f"<div style='border-radius:10px;overflow:hidden'><img src='{img}' style='width:100%;height:160px;object-fit:cover;display:block'/></div>"
        html += "</div></div></div>"
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown("<div id='photos' style='min-height:60vh;padding:28px'><div style='max-width:1100px;margin:0 auto'><h2 style='color:var(--c1);font-size:34px'>Photos</h2><p style='color:rgba(255,255,255,0.85)'>No photos found — add JPG/PNG to the repo root.</p></div></div>", unsafe_allow_html=True)

    # Blog
    posts = get_all_posts()
    blog_html = "<div id='blog' style='min-height:64vh;padding:28px'><div style='max-width:1100px;margin:0 auto'><h2 style='color:var(--c1);font-size:34px'>Blog</h2>"
    if not posts:
        blog_html += "<p style='color:rgba(255,255,255,0.85)'>No blog posts — add markdown files to blog_posts/</p>"
    else:
        for p in posts:
            blog_html += f"<div style='margin-top:10px;padding:12px;border-radius:10px;background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01))'><b style='color:#fff'>{p['title']}</b><div style='color:rgba(255,255,255,0.6)'>{p['date']}</div><p style='color:rgba(255,255,255,0.85)'>{p['summary']}</p></div>"
    blog_html += "</div></div>"
    st.markdown(blog_html, unsafe_allow_html=True)

    # Writings (full section)
    st.markdown("<div id='writings' style='min-height:62vh;padding:28px'><div style='max-width:1100px;margin:0 auto'><h2 style='color:var(--c1);font-size:34px'>Writings</h2>", unsafe_allow_html=True)
    msgs = load_anonymous_messages()
    if not msgs:
        st.markdown("<p style='color:rgba(255,255,255,0.85)'>No writings yet — click the ✍ icon to add anonymously.</p>", unsafe_allow_html=True)
    else:
        cards_html = "<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin-top:16px'>"
        for m in sorted(msgs, key=lambda x: x.get("id",0), reverse=True):
            txt = m.get("text","")
            ts = m.get("timestamp","")
            cards_html += f"<div style='background:linear-gradient(180deg,#fff,#fbf9ff);padding:14px;border-radius:10px;color:#0b0f14'><div style='font-weight:700'>{txt}</div><div style='font-size:12px;color:rgba(0,0,0,0.45);margin-top:8px'>{ts}</div></div>"
        cards_html += "</div>"
        st.markdown(cards_html, unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

    # Contact
    contact_html = """
    <div id="contact" style="min-height:48vh;padding:28px">
      <div style="max-width:1100px;margin:0 auto">
        <h2 style="color:var(--c1);font-size:34px">Contact</h2>
        <p style="color:rgba(255,255,255,0.9)">Email: <a href="mailto:aryanxsharma26@gmail.com" style="color:#fff">aryanxsharma26@gmail.com</a></p>
      </div>
    </div>
    """
    st.markdown(contact_html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Query param popups (Photos & Writings)
# -------------------------
def handle_query_popups():
    qp = st.experimental_get_query_params()
    # anon message direct submit via anon_q
    if "anon_q" in qp:
        q = qp.get("anon_q", [""])[0]
        if q and q.strip():
            save_anonymous_message(q.strip())
            # clear param and show success via tiny injected toast
            st.experimental_set_query_params()
            toast = """<div style="position:fixed;right:20px;bottom:110px;background:linear-gradient(90deg,#ff77e9,#8a6aff);padding:10px 14px;border-radius:10px;color:#081018;font-weight:800;z-index:20000">Message sent anonymously ✓</div>
            <script>setTimeout(()=>{var t=document.querySelector('div[style*=\"Message sent\"]'); if(t) t.style.opacity=0;},2200);</script>"""
            components.html(toast, height=0)
            st.experimental_rerun()

    if "show_photos" in qp:
        imgs = get_gallery_images()
        if imgs:
            html = "<div style='position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);z-index:20000;background:linear-gradient(180deg,rgba(12,8,16,0.96),rgba(18,12,22,0.96));padding:18px;border-radius:12px;box-shadow:0 30px 90px rgba(0,0,0,0.6);max-width:92%;width:820px;color:#fff'>"
            html += "<div style='display:flex;justify-content:space-between;align-items:center'><div style='font-weight:800;color:#ff9bdc'>Photos</div><div><a href='.' style='color:#fff;text-decoration:none;font-weight:700'>Close ✖</a></div></div>"
            html += "<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px;margin-top:12px'>"
            for i in imgs:
                html += f"<img src='{i}' style='width:100%;height:120px;object-fit:cover;border-radius:8px'/>"
            html += "</div></div>"
            components.html(html, height=640, scrolling=False)
        else:
            components.html("<div style='position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);z-index:20000;background:#0b0c10;padding:18px;border-radius:10px;color:#fff'>No photos found. Add images to repo root. <a href='.' style='color:#fff'>Close</a></div>", height=240)
        return

    if "show_writings" in qp:
        msgs = load_anonymous_messages()
        html = "<div style='position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);z-index:20000;background:linear-gradient(180deg,rgba(12,8,16,0.96),rgba(18,12,22,0.96));padding:18px;border-radius:12px;box-shadow:0 30px 90px rgba(0,0,0,0.6);max-width:92%;width:700px;color:#fff'>"
        html += "<div style='display:flex;justify-content:space-between;align-items:center'><div style='font-weight:800;color:#ff9bdc'>Writings</div><div><a href='.' style='color:#fff;text-decoration:none;font-weight:700'>Close ✖</a></div></div>"
        if not msgs:
            html += "<div style='margin-top:14px;color:rgba(255,255,255,0.85)'>No writings yet — submit anonymously below.</div>"
        else:
            html += "<div style='margin-top:12px;max-height:360px;overflow:auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:8px'>"
            for m in sorted(msgs, key=lambda x: x.get("id",0), reverse=True):
                txt = m.get("text","")
                ts = m.get("timestamp","")
                html += f"<div style='background:linear-gradient(180deg,#fff,#fbf9ff);padding:10px;border-radius:8px;color:#0b0f14'><div style='font-weight:700'>{txt}</div><div style='font-size:12px;color:rgba(0,0,0,0.45);margin-top:8px'>{ts}</div></div>"
            html += "</div>"
        # quick submit form
        html += "<div style='margin-top:12px'><form action='.' method='get'><input name='anon_q' placeholder='Share anonymously...' style='width:62%;padding:8px;border-radius:8px;border:1px solid rgba(255,255,255,0.06)'/> <button style='padding:8px 12px;border-radius:8px;background:linear-gradient(90deg,#ff77e9,#8a6aff);border:none;color:#081018;font-weight:800'>Send</button></form></div>"
        html += "</div>"
        components.html(html, height=600, scrolling=False)
        return

# -------------------------
# Admin sidebar (unlock via query param)
# -------------------------
def admin_panel():
    qp = st.experimental_get_query_params()
    if ADMIN_QP in qp and qp.get(ADMIN_QP, [""])[0] == ADMIN_TOKEN:
        st.session_state["_admin_unlocked"] = True

    if st.session_state.get("_admin_unlocked", False):
        st.sidebar.title("Admin — Messages")
        msgs = load_anonymous_messages()
        st.sidebar.write("Total messages:", len(msgs))
        for m in sorted(msgs, key=lambda x: x.get("id",0), reverse=True):
            st.sidebar.markdown(f"**ID {m.get('id')}** — {m.get('timestamp')}")
            st.sidebar.write(m.get("text"))
            if st.sidebar.button(f"Delete {m.get('id')}", key=f"del_{m.get('id')}"):
                new = [x for x in msgs if x.get("id") != m.get("id")]
                overwrite_anonymous_messages(new)
                st.experimental_rerun()
        if st.sidebar.button("Clear all", key="clearall"):
            overwrite_anonymous_messages([])
            st.experimental_rerun()

# -------------------------
# Main
# -------------------------
def main():
    inject_css()
    handle_query_popups()
    render_hero_component()
    render_sections()
    admin_panel()
    st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
