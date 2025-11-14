# app.py
# Final production-ready Streamlit portfolio (Neon C2 theme, middle-left floating icons, B-style chatbot pill that expands upward)
# Features included:
# - Global C2 gradient background (pink -> purple)
# - Fullscreen sections (100vh) with reduced gaps
# - Auto-hide navbar (appears on scroll up)
# - Smooth scroll-to-section anchors
# - Particles across all sections (tsparticles)
# - Projects (2-card carousel), Experience placeholders
# - Photos & Writings floating icons (middle-left) -> open floating popups (L2 style)
# - Chatbot floating pill bottom-left (expands UP)
# - Anonymous writings system (saved to anonymous_messages.txt)
# - Blog loader from blog_posts/*.md
# - Photos loader from repo root (jpg/png/webp)
# - Admin unlocked via query param ?admin=admin-aryan (hidden by default)
# - Uses environment variables for Telegram notifications:
#     TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
#
# Instructions:
# 1. Ensure requirements.txt includes: streamlit, markdown, requests
# 2. Put images (jpg/png/webp) at repo root to appear in Photos popup
# 3. Put blog markdown files in blog_posts/
# 4. Deploy to Streamlit Cloud / Vercel; set env vars for Telegram if needed
# 5. Copy this file as app.py and run: streamlit run app.py

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
# Configuration
# -------------------------
st.set_page_config(page_title="Aryan Sharma — Portfolio", layout="wide", initial_sidebar_state="collapsed")
BASE_DIR = os.path.dirname(__file__) if os.path.isdir(os.path.dirname(__file__) or "") else "."
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")
MSG_FILE = os.path.join(BASE_DIR, "anonymous_messages.txt")

# Admin token (not secret-critical; can be changed)
ADMIN_TOKEN = "admin-aryan"
ADMIN_QUERY_PARAM = "admin"

# Telegram from environment (S2) — do NOT hardcode secrets
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")  # example: "8521726094:AAAA..."
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")      # set in deployment env

# Hero text
HERO_NAME = "Aryan Sharma"
HERO_ROLE = "I'M a developer , writer , editor and a learner"

# -------------------------
# Utility functions
# -------------------------
def ensure_msg_file():
    try:
        if not os.path.exists(MSG_FILE):
            with open(MSG_FILE, "w", encoding="utf-8") as f:
                pass
    except Exception:
        pass

def save_message(text):
    """Append anonymous message as JSON line."""
    ensure_msg_file()
    msg = {"id": int(time.time() * 1000), "text": text, "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}
    try:
        with open(MSG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(msg, ensure_ascii=False) + "\n")
    except Exception:
        pass

    # send to Telegram (best-effort) if env vars present
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": f"📨 New anonymous message:\n\n{text}\n\nID:{msg['id']}"}
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json=payload, timeout=6)
        except Exception:
            pass
    return msg

def load_messages():
    ensure_msg_file()
    out = []
    try:
        with open(MSG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                try:
                    out.append(json.loads(line))
                except:
                    continue
    except Exception:
        return []
    return out

def overwrite_messages(msgs):
    try:
        with open(MSG_FILE, "w", encoding="utf-8") as f:
            for m in msgs:
                f.write(json.dumps(m, ensure_ascii=False) + "\n")
    except Exception:
        pass

# Blog helpers
def get_post_data(slug):
    file_path = os.path.join(POSTS_DIR, f"{slug}.md")
    if not os.path.exists(file_path): return None
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    md_meta = {}
    body = content
    m = re.match(r'---\n(.*?)\n---', content, re.DOTALL)
    if m:
        meta = m.group(1)
        for line in meta.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                md_meta[k.strip()] = v.strip()
        body = content[m.end():].strip()
    html = markdown(body)
    return {"slug": slug, "title": md_meta.get("title", "Untitled"), "date": md_meta.get("date", "N/A"),
            "author": md_meta.get("author", "N/A"), "summary": md_meta.get("summary", ""), "html": html}

def get_all_posts():
    if not os.path.exists(POSTS_DIR): return []
    files = [f for f in os.listdir(POSTS_DIR) if f.endswith(".md")]
    posts = []
    for f in files:
        slug = f.replace(".md", "")
        p = get_post_data(slug)
        if p: posts.append(p)
    # optional sort by date if format is consistent
    try:
        posts.sort(key=lambda x: time.strptime(x['date'], '%B %d, %Y'), reverse=True)
    except Exception:
        pass
    return posts

def get_gallery_images():
    try:
        root = BASE_DIR if os.path.isdir(BASE_DIR) else "."
        files = os.listdir(root)
    except Exception:
        return []
    images = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
    ignore = {"vercel.png", "screenshot.png"}
    return [i for i in images if i not in ignore]

# -------------------------
# Global CSS (apply gradient site-wide and remove Streamlit chrome)
# -------------------------
def inject_global_css():
    css = """
    <style>
    :root{
      --c1: #ff77e9; /* pink */
      --c2: #8a6aff; /* purple */
      --panel-dark: rgba(12,8,16,0.92);
      --neon-pink: #ff77e9;
      --neon-purple: #8a6aff;
      --neon-accent: #ff7ad1;
    }
    /* Apply gradient to the entire Streamlit app container */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
      background: linear-gradient(135deg, var(--c1) 0%, var(--c2) 100%) !important;
      min-height: 100% !important;
    }
    /* Remove Streamlit padding and chrome */
    .reportview-container .main .block-container {
      padding-top: 0rem !important;
      padding-left: 0rem !important;
      padding-right: 0rem !important;
      margin: 0 !important;
      max-width: 100% !important;
    }
    #MainMenu, header, footer { display: none !important; }
    /* Make sections full bleed and remove gaps */
    .full-section { width:100% !important; margin:0 auto !important; padding:0 !important; }
    section[data-testid="stVerticalBlock"]{ padding:0 !important; margin:0 !important; background:transparent !important; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# -------------------------
# Hero & Nav (components.html)
# -------------------------
def render_hero_nav():
    # Using placeholders to avoid f-string issues with braces in JS
    hero_html = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    :root{--c1:#ff77e9;--c2:#8a6aff;--panel:rgba(12,8,16,0.92);--neon1:#ff77e9;--neon2:#8a6aff}
    html,body{margin:0;padding:0;font-family:Inter,system-ui,-apple-system,'Segoe UI',Roboto}
    body{background:transparent}
    .nav {
      position:fixed; top:12px; left:50%; transform:translateX(-50%); z-index:9999; display:flex; align-items:center;
      gap:18px; padding:10px 20px; border-radius:12px; backdrop-filter: blur(10px) saturate(120%);
      background: rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.04);
      box-shadow:0 18px 40px rgba(2,6,23,0.35); transition: transform 260ms ease, opacity 260ms ease;
      max-width:1200px; width:92%;
    }
    .nav.hidden { transform: translateY(-140%); opacity:0; pointer-events:none;}
    .nav .brand{font-weight:800;color:white;font-size:18px}
    .nav a{color:rgba(255,255,255,0.95);text-decoration:none;padding:6px 10px;border-radius:8px;font-weight:700}
    .hero-wrap{height:100vh;min-height:640px;display:flex;align-items:center;justify-content:center;padding:28px}
    .hero-card{width:min(1120px,96%); background: linear-gradient(180deg, rgba(10,7,12,0.94), rgba(14,10,18,0.94)); border-radius:28px; padding:36px; position:relative; box-shadow:0 30px 80px rgba(0,0,0,0.35); overflow:hidden}
    /* Neon C2 border */
    .hero-card::before{
      content:"";
      position:absolute; inset:-2px; border-radius:30px;
      background: linear-gradient(90deg, rgba(255,120,200,0.06), rgba(138,106,255,0.06));
      pointer-events:none; z-index:0;
      box-shadow: 0 0 40px rgba(255,120,200,0.04), inset 0 0 30px rgba(138,106,255,0.02);
    }
    #tsparticles{ position:absolute; inset:0; z-index:0; border-radius:28px; pointer-events:none }
    .hero-inner{position:relative; z-index:2; color:white; text-align:left}
    .title{font-size:48px;font-weight:800;color:var(--neon1);margin:0}
    .role{font-size:18px;font-weight:700;color:var(--neon2);margin:8px 0 16px}
    .desc{max-width:880px;margin:0 0 18px;color:rgba(255,255,255,0.9);line-height:1.5}
    .cta{display:flex;gap:12px;flex-wrap:wrap}
    .btn-primary{background:linear-gradient(90deg,var(--neon1),var(--neon2));color:#0b0f14;padding:10px 18px;border-radius:20px;font-weight:800;text-decoration:none}
    .btn-ghost{background:transparent;color:var(--neon2);padding:10px 16px;border-radius:20px;border:1px solid rgba(255,255,255,0.06);font-weight:700}
    .socials{display:flex;gap:12px;margin-top:12px}
    .social{display:inline-flex;align-items:center;justify-content:center;width:44px;height:44px;border-radius:10px;background:rgba(255,255,255,0.02);color:#fff;font-weight:700}
    /* floating tools left (middle-left) */
    .floating-tools { position: fixed; left: 16px; top: 50%; transform: translateY(-50%); z-index:9998; display:flex;flex-direction:column; gap:12px; }
    .tool-icon { font-size:22px; color:rgba(255,255,255,0.92); text-shadow:0 6px 18px rgba(138,106,255,0.06); cursor:pointer; transition: transform .14s ease; }
    .tool-icon:hover { transform: translateX(6px); filter: drop-shadow(0 8px 20px rgba(255,120,200,0.12)); }
    /* FAB Chat pill bottom-left (style B) */
    .chat-pill { position:fixed; left:18px; bottom:18px; z-index:9999; display:flex; align-items:center; gap:8px; padding:12px 16px; border-radius:28px; background: linear-gradient(90deg, #ff77e9, #8a6aff); color:#081018; font-weight:800; box-shadow:0 20px 60px rgba(0,0,0,0.35); cursor:pointer; }
    .chat-pill .send-rect { background: rgba(255,255,255,0.95); padding:8px 10px; border-radius:8px; font-weight:800; }
    /* small responsive */
    @media (max-width:880px){
      .title{font-size:32px}
      .hero-card{padding:22px;border-radius:18px}
      .nav{left:12px;transform:none;width:calc(100% - 24px)}
      .floating-tools{ left:10px }
    }
    </style>

    <div class="nav" id="topnav">
      <div class="brand">Aryan</div>
      <div style="display:flex;gap:12px">
        <a href="#home">Home</a><a href="#about">About</a><a href="#skills">Skills</a><a href="#projects">Projects</a><a href="#experience">Experience</a><a href="#photos">Photos</a><a href="#blog">Blog</a><a href="#writings">Writings</a><a href="#chat">Chatbot</a><a href="#contact">Contact</a>
      </div>
    </div>

    <div id="home" class="hero-wrap">
      <div class="hero-card">
        <div id="tsparticles"></div>
        <div class="hero-inner">
          <h1 class="title">__HERO_NAME__</h1>
          <div class="role">__HERO_ROLE__</div>
          <div class="desc">Welcome to my personal website — explore projects, photos, writings and chat with my AI assistant.</div>
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

    <!-- Floating left tools (middle-left placement) -->
    <div class="floating-tools" id="floating-tools">
      <div class="tool-icon" id="open-photos" title="Photos">📷</div>
      <div class="tool-icon" id="open-writings" title="Writings">✍</div>
    </div>

    <!-- Chat pill -->
    <div class="chat-pill" id="chat-pill" title="Ask Aryan">
      <div style="font-weight:900">Ask Aryan</div>
      <div class="send-rect">Send</div>
    </div>

    <!-- modal/popups placeholder -->
    <div id="popup-root"></div>
    <div id="toast-root"></div>

    <script>
    // particles loader (tsparticles)
    (function(){
      function initParticles(){
        if(window.tsParticles){
          tsParticles.load("tsparticles", {
            fullScreen: { enable: false },
            particles: {
              number: { value: 30 },
              color: { value: ["#ff6ad1","#8b8bff","#ff77e9"] },
              shape: { type: "circle" },
              opacity: { value: 0.6 },
              size: { value: { min: 2, max: 6 } },
              move: { enable: true, speed: 0.45, outModes: "out" }
            },
            background: { color: "transparent" },
            detectRetina: true
          });
        } else {
          var s = document.createElement('script');
          s.src = "https://cdn.jsdelivr.net/npm/tsparticles@2.3.4/tsparticles.bundle.min.js";
          s.onload = function(){ initParticles(); };
          document.head.appendChild(s);
        }
      }
      initParticles();
    })();

    // smooth scroll for nav anchors
    document.querySelectorAll('.nav a').forEach(function(a){
      a.addEventListener('click', function(e){
        e.preventDefault();
        var id = a.getAttribute('href').replace('#','');
        var el = document.getElementById(id);
        if(el){ el.scrollIntoView({behavior:'smooth', block:'start'}); }
      });
    });

    // auto-hide navbar (hide on scroll down, show on scroll up)
    (function(){
      var lastScroll = 0;
      var nav = document.getElementById('topnav');
      window.addEventListener('scroll', function(){
        var st = window.scrollY || window.pageYOffset;
        if (st > lastScroll && st > 120){
          nav.classList.add('hidden');
        } else {
          nav.classList.remove('hidden');
        }
        lastScroll = st <= 0 ? 0 : st;
      }, { passive: true });
    })();

    // floating left icons handlers: open photo/writings popups
    (function(){
      var popupRoot = document.getElementById('popup-root');
      document.getElementById('open-photos').addEventListener('click', function(){
        // fetch images (relative paths are served by streamlit static) — we will just open a popup that instructs Streamlit to show photos via query param
        var params = new URLSearchParams(window.location.search);
        params.set('show_photos','1');
        window.location.search = params.toString();
      });
      document.getElementById('open-writings').addEventListener('click', function(){
        var params = new URLSearchParams(window.location.search);
        params.set('show_writings','1');
        window.location.search = params.toString();
      });
    })();

    // Chat pill click -> open chat above the pill
    (function(){
      var chat = document.getElementById('chat-pill');
      var popupRoot = document.getElementById('popup-root');
      chat.addEventListener('click', function(){
        // make a floating chat window above the pill
        popupRoot.innerHTML = `
          <div id="chat-popup" style="position:fixed;left:22px;bottom:88px;z-index:10000;width:360px;max-width:88%;border-radius:12px;background:linear-gradient(180deg, rgba(10,8,14,0.96), rgba(18,14,24,0.96));box-shadow:0 30px 80px rgba(0,0,0,0.6);padding:12px;border:1px solid rgba(255,255,255,0.03)">
            <div style="font-weight:800;color:#8fdcff;margin-bottom:8px">Aryan's AI Chatbot</div>
            <div id="chat-history" style="background:rgba(255,255,255,0.02);height:160px;border-radius:8px;padding:8px;overflow:auto;color:#e6f7ff">Hi! Ask me questions about Aryan.</div>
            <div style="display:flex;gap:8px;margin-top:8px">
              <input id="chat-input" placeholder="Type a question..." style="flex:1;padding:8px;border-radius:8px;border:1px solid rgba(255,255,255,0.04);background:transparent;color:#e6f7ff"/>
              <button id="chat-send" style="padding:8px 12px;border-radius:8px;background:linear-gradient(90deg,#ff77e9,#8a6aff);border:none;color:#081018;font-weight:800">Ask</button>
            </div>
          </div>
        `;
        // clicking outside should close it
        setTimeout(()=>{ document.addEventListener('click', closeChatOutside); }, 100);

        // send handler
        document.getElementById('chat-send').addEventListener('click', function(e){
          var val = document.getElementById('chat-input').value || "";
          if(!val.trim()){ alert('Write a question'); return; }
          // append to history (simple client-side simulation)
          var h = document.getElementById('chat-history');
          var user = document.createElement('div'); user.style.marginTop='8px'; user.style.fontWeight='700'; user.style.color='#dbe8ff'; user.textContent = val;
          h.appendChild(user);
          var ans = document.createElement('div'); ans.style.marginTop='6px'; ans.style.color='#d0e8ff'; ans.textContent = "Sorry! I don't have an answer for that.";
          h.appendChild(ans);
          h.scrollTop = h.scrollHeight;
          document.getElementById('chat-input').value = '';
        });

        function closeChatOutside(ev){
          var popup = document.getElementById('chat-popup');
          var pill = document.getElementById('chat-pill');
          if(!popup) return;
          if(!popup.contains(ev.target) && !pill.contains(ev.target)){
            popup.remove();
            document.removeEventListener('click', closeChatOutside);
          }
        }
      });
    })();
    </script>
    """
    hero_html = hero_html.replace("__HERO_NAME__", HERO_NAME).replace("__HERO_ROLE__", HERO_ROLE)
    components.html(hero_html, height=900, scrolling=False)

# -------------------------
# Render content sections with reduced gaps, full height
# -------------------------
def render_sections():
    st.markdown('<div class="full-section">', unsafe_allow_html=True)

    # ABOUT (100vh)
    about_html = f"""
    <div id="about" style="height:100vh;display:flex;align-items:center;padding:28px 20px;">
      <div style="max-width:1100px;margin:0 auto;color:white;">
        <h2 style="color:rgba(255,200,245,1);font-size:36px;margin-bottom:8px">About</h2>
        <p style="font-size:18px;color:rgba(255,255,255,0.92);max-width:900px">Hi, I'm <strong style="color:white">{HERO_NAME}</strong> — {HERO_ROLE}. I build polished websites and tools and enjoy writing and learning. This site showcases my projects, photos and writings. Use the floating icons to quickly view photos or submit anonymous writings.</p>
      </div>
    </div>
    """
    st.markdown(about_html, unsafe_allow_html=True)

    # SKILLS
    skills_html = """
    <div id="skills" style="height:100vh;display:flex;align-items:center;padding:24px;">
      <div style="max-width:1100px;margin:0 auto;color:white;">
        <h2 style="color:rgba(255,200,245,1);font-size:36px;margin-bottom:8px">Skills</h2>
        <div style="display:flex;flex-wrap:wrap;gap:10px">
          <span style="padding:8px 12px;border-radius:8px;background:linear-gradient(90deg,#ff77e9,#8a6aff);color:#081018;font-weight:700">Python</span>
          <span style="padding:8px 12px;border-radius:8px;background:linear-gradient(90deg,#ff77e9,#8a6aff);color:#081018;font-weight:700">Streamlit</span>
          <span style="padding:8px 12px;border-radius:8px;background:linear-gradient(90deg,#ff77e9,#8a6aff);color:#081018;font-weight:700">React</span>
          <span style="padding:8px 12px;border-radius:8px;background:linear-gradient(90deg,#ff77e9,#8a6aff);color:#081018;font-weight:700">Web Dev</span>
        </div>
      </div>
    </div>
    """
    st.markdown(skills_html, unsafe_allow_html=True)

    # PROJECTS — components for carousel (small height but close spacing)
    projects = [
        {"title":"Draw App","tagline":"Collaborative drawing & whiteboard","desc":"A collaborative drawing app for multiple users in real-time.", "tags":["Canvas","WebSockets"]},
        {"title":"Portfolio Builder","tagline":"Template-based portfolio generator","desc":"Create beautiful portfolios quickly using templates.", "tags":["React","Templates"]}
    ]
    proj_html = """
    <style>
    .proj-sec{height:84vh;display:flex;align-items:center;padding:18px}
    .proj-wrap{max-width:1100px;margin:0 auto;background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));padding:14px;border-radius:12px}
    .proj-inner{display:flex;gap:18px;align-items:center}
    .proj-media{flex:1;min-height:220px;border-radius:10px;display:flex;align-items:center;justify-content:center;color:#9aa0a6;background:linear-gradient(180deg, rgba(10,10,12,0.9), rgba(16,12,20,0.9));}
    .proj-detail{flex:1}
    .tag{display:inline-block;background:linear-gradient(90deg,#ff77e9,#8a6aff);padding:6px 10px;border-radius:999px;color:#081018;margin-right:8px;margin-bottom:8px;font-weight:700}
    .dots{display:flex;gap:8px;justify-content:center;margin-top:14px}
    .dot{width:10px;height:10px;border-radius:50%;background:rgba(0,0,0,0.1)}
    .dot.active{background:linear-gradient(90deg,#ff77e9,#8a6aff)}
    @media (max-width:880px){ .proj-inner{flex-direction:column} .proj-media{width:100%} }
    </style>
    <div id="projects" class="proj-sec"><div class="proj-wrap"><div id="carousel"></div><div class="dots" id="dots"></div></div></div>
    <script>
    (function(){
      var projects = __PJ__;
      var carousel = document.getElementById('carousel');
      var dots = document.getElementById('dots');
      var idx=0;
      function render(i){
        var p = projects[i];
        var html = '<div class="proj-inner"><div class="proj-media"><div style="text-align:center;padding:12px"><b style="font-size:20px;color:#fff">'+p.title+'</b><div style="color:#9aa0a6;margin-top:8px">'+p.tagline+'</div></div></div>';
        html += '<div class="proj-detail"><h3 style="margin:0;color:#fff">'+p.title+'</h3><p style="color:#cfd6e8">'+p.desc+'</p><div>';
        p.tags.forEach(function(t){ html += '<span class="tag">'+t+'</span>'; });
        html += '</div><div style="margin-top:12px"><button style="padding:8px 12px;border-radius:8px;border:1px solid rgba(255,255,255,0.06);background:transparent;color:#fff;margin-right:8px">Code</button><button style="padding:8px 12px;border-radius:8px;background:linear-gradient(90deg,#ff77e9,#8a6aff);color:#081018;border:none">Live Demo</button></div></div></div>';
        carousel.innerHTML = html;
        dots.innerHTML='';
        for(var k=0;k<projects.length;k++){ var d=document.createElement('div'); d.className='dot'+(k===i?' active':''); (function(n){ d.onclick=function(){ idx=n; render(n); }; })(k); dots.appendChild(d); }
      }
      render(0);
      setInterval(function(){ idx=(idx+1)%projects.length; render(idx); },8000);
    })();
    </script>
    """
    components.html(proj_html.replace("__PJ__", json.dumps(projects)), height=720, scrolling=False)

    # Experience (compact)
    exp_html = """
    <div id="experience" style="height:84vh;display:flex;align-items:center;padding:28px;">
      <div style="max-width:1100px;margin:0 auto;color:white;">
        <h2 style="color:rgba(255,200,245,1);font-size:34px;margin-bottom:6px">Experience</h2>
        <p style="color:rgba(255,255,255,0.9);max-width:900px">Working on personal projects focused on web and AI — building polished experiences and learning continuously. ⚙️ Still working on this section; more content coming soon.</p>
      </div>
    </div>
    """
    st.markdown(exp_html, unsafe_allow_html=True)

    # PHOTOS section (will also be shown via left popup)
    imgs = get_gallery_images()
    if imgs:
        photos_html = "<div id='photos' style='min-height:84vh;padding:28px;'><div style='max-width:1100px;margin:0 auto;color:white;'><h2 style='color:rgba(255,200,245,1);font-size:34px'>Photos</h2><div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-top:12px'>"
        for i in imgs:
            photos_html += f"<img src='{i}' style='width:100%;height:160px;object-fit:cover;border-radius:10px'/>"
        photos_html += "</div></div></div>"
        st.markdown(photos_html, unsafe_allow_html=True)
    else:
        st.markdown('<div id="photos" style="min-height:84vh;padding:28px;"><div style="max-width:1100px;margin:0 auto;color:white;"><h2 style="color:rgba(255,200,245,1);font-size:34px">Photos</h2><p style="color:rgba(255,255,255,0.85)">No photos found. Add JPG/PNG to the repository root for them to appear here or click the photo icon to view uploads.</p></div></div>', unsafe_allow_html=True)

    # Blog
    posts = get_all_posts()
    blog_html = '<div id="blog" style="min-height:84vh;padding:28px;"><div style="max-width:1100px;margin:0 auto;color:white;"><h2 style="color:rgba(255,200,245,1);font-size:34px">Blog</h2>'
    if not posts:
        blog_html += '<p style="color:rgba(255,255,255,0.85)">No blog posts found. Add markdown files to blog_posts/</p>'
    else:
        for p in posts:
            blog_html += f"<div style='margin-top:10px;padding:12px;border-radius:8px;background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01))'><b style='color:#fff'>{p['title']}</b><div style='color:rgba(255,255,255,0.6)'>{p['date']}</div><p style='color:rgba(255,255,255,0.85)'>{p['summary']}</p></div>"
    blog_html += '</div></div>'
    st.markdown(blog_html, unsafe_allow_html=True)

    # WRITINGS (full section, card list)
    st.markdown('<div id="writings" style="min-height:84vh;padding:28px;"><div style="max-width:1100px;margin:0 auto;color:white;"><h2 style="color:rgba(255,200,245,1);font-size:34px">Writings</h2>', unsafe_allow_html=True)
    messages = load_messages()
    if not messages:
        st.markdown('<p style="color:rgba(255,255,255,0.85)">No writings yet — click the ✍ icon to add anonymously.</p>', unsafe_allow_html=True)
    else:
        cards = "<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin-top:16px'>"
        for m in sorted(messages, key=lambda x: x.get("id",0), reverse=True):
            text = (m.get("text","")[:400] + ("..." if len(m.get("text",""))>400 else ""))
            ts = m.get("timestamp","")
            cards += f"<div style='background:linear-gradient(180deg,#fff,#fbf9ff);padding:14px;border-radius:10px;box-shadow:0 12px 30px rgba(2,6,23,0.06)'><div style='color:#0b0f14;font-weight:700'>{text}</div><div style='color:rgba(0,0,0,0.45);font-size:12px;margin-top:8px'>{ts}</div></div>"
        cards += "</div>"
        st.markdown(cards, unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    # Chatbot section (simple fallback)
    st.markdown('<div id="chat" style="min-height:56vh;padding:28px;"><div style="max-width:1100px;margin:0 auto;color:white;"><h2 style="color:rgba(255,200,245,1);font-size:34px">Chatbot</h2>', unsafe_allow_html=True)
    if "chat_messages" not in st.session_state: st.session_state.chat_messages = []
    for m in st.session_state.chat_messages[-6:]:
        if m["role"]=="user":
            st.markdown(f"<div style='margin-top:8px;padding:10px;border-radius:8px;background:#0f1724;color:#cfe8ff'>{m['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='margin-top:8px;padding:10px;border-radius:8px;background:#f7f6ff;color:#0b0f14'>{m['content']}</div>", unsafe_allow_html=True)
    q = st.text_input("Ask me a question...", key="chat_main_input")
    if q:
        st.session_state.chat_messages.append({"role":"user","content":q})
        answer = {"what is your name": f"My name is {HERO_NAME}.","where are you from":"I am from India."}.get(q.lower(), "Sorry! I don't have an answer for that.")
        st.session_state.chat_messages.append({"role":"bot","content":answer})
        st.experimental_rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

    # CONTACT
    st.markdown('<div id="contact" style="min-height:60vh;padding:28px;"><div style="max-width:1100px;margin:0 auto;color:white;"><h2 style="color:rgba(255,200,245,1);font-size:34px">Contact</h2><p style="color:rgba(255,255,255,0.9)">Email: <a href="mailto:aryanxsharma26@gmail.com" style="color:#fff">aryanxsharma26@gmail.com</a></p></div></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# Query param handlers & popup rendering (Photos & Writings)
# -------------------------
def handle_query_params_and_popups():
    qp = st.experimental_get_query_params()
    # Anon writing via tiny modal flow uses param 'anon_q' (created by modal JS)
    if "anon_q" in qp:
        q = qp.get("anon_q", [""])[0]
        if q and q.strip():
            save_message(q.strip())
            st.experimental_set_query_params()
            # show toast
            toast_html = """
            <style>
            .toast{position:fixed;right:20px;bottom:100px;background:linear-gradient(90deg,#ff77e9,#8a6aff);padding:10px 14px;border-radius:10px;color:#081018;font-weight:800;box-shadow:0 18px 40px rgba(0,0,0,0.3);z-index:10001;animation:toastIn .25s ease-out}
            @keyframes toastIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
            </style>
            <div class="toast">Message sent anonymously ✓</div>
            <script>setTimeout(()=>{document.querySelector('.toast').style.transition='opacity .4s';document.querySelector('.toast').style.opacity='0';},2200);setTimeout(()=>{document.querySelector('.toast').remove();},2800);</script>
            """
            components.html(toast_html, height=0)
            st.experimental_rerun()

    # Show Photos popup if show_photos param present
    if "show_photos" in qp:
        imgs = get_gallery_images()
        # Create HTML popup for photos
        if imgs:
            html = "<style>.pp{position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);z-index:20000;background:linear-gradient(180deg,rgba(12,8,16,0.96),rgba(18,12,22,0.96));padding:18px;border-radius:10px;box-shadow:0 30px 80px rgba(0,0,0,0.6);max-width:92%;width:820px;color:#fff}</style>"
            html += "<div class='pp'><div style='display:flex;justify-content:space-between;align-items:center'><div style='font-weight:800;color:#ff9bdc'>Photos</div><div><a href='.' style='color:#fff;text-decoration:none;font-weight:700'>Close ✖</a></div></div><div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px;margin-top:12px'>"
            for i in imgs:
                html += f"<img src='{i}' style='width:100%;height:120px;object-fit:cover;border-radius:8px'/>"
            html += "</div></div>"
            components.html(html, height=600, scrolling=False)
        else:
            components.html("<div style='position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);z-index:20000;background:#0b0c10;padding:18px;border-radius:10px;color:#fff'>No photos found. Add JPG/PNG images to the repo root. <br><a href='.' style='color:#fff'>Close</a></div>", height=240)
        return

    # Show Writings popup if show_writings param present
    if "show_writings" in qp:
        msgs = load_messages()
        html = "<style>.wp{position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);z-index:20000;background:linear-gradient(180deg,rgba(12,8,16,0.96),rgba(18,12,22,0.96));padding:18px;border-radius:10px;box-shadow:0 30px 80px rgba(0,0,0,0.6);max-width:92%;width:700px;color:#fff}</style>"
        html += "<div class='wp'><div style='display:flex;justify-content:space-between;align-items:center'><div style='font-weight:800;color:#ff9bdc'>Writings</div><div><a href='.' style='color:#fff;text-decoration:none;font-weight:700'>Close ✖</a></div></div>"
        if not msgs:
            html += "<div style='margin-top:12px;color:rgba(255,255,255,0.85)'>No writings yet — click the ✍ icon to add anonymously.</div>"
        else:
            html += "<div style='margin-top:12px;max-height:420px;overflow:auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:8px'>"
            for m in sorted(msgs, key=lambda x: x.get("id",0), reverse=True):
                txt = (m.get("text","")[:300] + ("..." if len(m.get("text",""))>300 else ""))
                html += f"<div style='background:linear-gradient(180deg,#fff,#fbf9ff);padding:10px;border-radius:8px;color:#0b0f14'><div style='font-weight:700'>{txt}</div><div style='font-size:12px;color:rgba(0,0,0,0.45);margin-top:8px'>{m.get('timestamp')}</div></div>"
            html += "</div>"
        # add quick submit form in popup via query param flow
        html += "<div style='margin-top:12px'><form action='.' method='get'><input name='anon_q' placeholder='Share anonymously...' style='width:60%;padding:8px;border-radius:8px;border:1px solid rgba(255,255,255,0.06)'/> <button style='padding:8px 12px;border-radius:8px;background:linear-gradient(90deg,#ff77e9,#8a6aff);border:none;color:#081018;font-weight:800'>Send</button></form></div>"
        html += "</div>"
        components.html(html, height=600, scrolling=False)
        return

# -------------------------
# Admin unlock flow (hidden unless token)
# -------------------------
def admin_unlock_flow():
    qp = st.experimental_get_query_params()
    if ADMIN_QUERY_PARAM in qp and qp.get(ADMIN_QUERY_PARAM, [""])[0] == ADMIN_TOKEN:
        st.session_state._admin_unlocked = True

    if st.session_state.get("_admin_unlocked", False):
        st.sidebar.title("Admin")
        st.sidebar.write("Messages management")
        msgs = load_messages()
        st.sidebar.write("Total messages:", len(msgs))
        for m in sorted(msgs, key=lambda x: x.get("id",0), reverse=True):
            st.sidebar.markdown(f"**ID {m.get('id')}** — {m.get('timestamp')}")
            st.sidebar.write(m.get("text"))
            if st.sidebar.button("Delete " + str(m.get("id")), key=f"deladm{m.get('id')}"):
                new = [x for x in msgs if x.get("id") != m.get("id")]
                overwrite_messages(new)
                st.experimental_rerun()
        if st.sidebar.button("Clear all messages", key="clearalladm"):
            overwrite_messages([])
            st.experimental_rerun()

# -------------------------
# Main
# -------------------------
def main():
    inject_global_css()
    # handle query params first (popups submit)
    handle_query_params_and_popups()
    render_hero_nav()
    render_sections()
    admin_unlock_flow()
    # small footer spacing
    st.markdown("<div style='height:64px'></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
