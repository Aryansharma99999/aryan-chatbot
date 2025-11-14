# app.py
# Final SmarthSood-style Streamlit portfolio with:
# - Global background applied site-wide
# - Fullscreen sections (100vh)
# - Auto-hide navbar (N2)
# - Floating FAB modal for anonymous messages (B2)
# - Writings as a full section (cards)
# - Projects (2-card carousel), Photos grid, Blog, Chatbot, Contact
# - Robust file handling, optional Telegram notification
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
BASE_DIR = os.path.dirname(__file__) if os.path.isdir(os.path.dirname(__file__) or "") else "."
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")
MSG_FILE = os.path.join(BASE_DIR, "anonymous_messages.txt")
ADMIN_TOKEN = "admin-aryan"        # change if you want
ADMIN_QUERY_PARAM = "admin"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "") or ""
HERO_NAME = "Aryan Sharma"
HERO_ROLE = "I'M a developer , writer , editor and a learner"

# -------------------------
# Utilities: messages & blog & gallery
# -------------------------
def ensure_msg_file():
    try:
        if not os.path.exists(MSG_FILE):
            with open(MSG_FILE, "w", encoding="utf-8") as f:
                pass
    except Exception:
        pass

def save_message(text):
    ensure_msg_file()
    msg = {"id": int(time.time() * 1000), "text": text, "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}
    try:
        with open(MSG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(msg, ensure_ascii=False) + "\n")
    except Exception:
        pass

    # Telegram best-effort
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
                if not line.strip():
                    continue
                try:
                    out.append(json.loads(line))
                except Exception:
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

def get_post_data(slug):
    file_path = os.path.join(POSTS_DIR, f"{slug}.md")
    if not os.path.exists(file_path):
        return None
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
    if not os.path.exists(POSTS_DIR):
        return []
    files = [f for f in os.listdir(POSTS_DIR) if f.endswith(".md")]
    posts = []
    for f in files:
        slug = f.replace(".md", "")
        p = get_post_data(slug)
        if p:
            posts.append(p)
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
# Global CSS / Force theme across Streamlit app
# -------------------------
def force_global_theme():
    # Make the entire Streamlit app use the gradient background and remove paddings.
    css = """
    <style>
    :root{
      --g1: #ff77e9;
      --g2: #8a6aff;
      --card-bg: rgba(10,8,12,0.95);
      --accent-pink: #ff53d6;
      --accent-violet: #8b8bff;
      --accent-cyan: #00d4ff;
    }
    /* Apply background to entire app container */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .appview-container {
      background: linear-gradient(135deg, var(--g1) 0%, var(--g2) 100%) !important;
      min-height: 100% !important;
      height: auto !important;
    }

    /* Remove Streamlit's top spacing and side padding */
    .reportview-container .main .block-container{
      padding-top: 0rem !important;
      padding-left: 0rem !important;
      padding-right: 0rem !important;
      margin: 0 !important;
      max-width: 100% !important;
      width: 100% !important;
    }

    /* Hide Streamlit default header/footer */
    #MainMenu, header, footer {
      display: none !important;
    }

    /* Make background of block transparent so our gradient shows through */
    .stBlock {
      background: transparent !important;
    }

    /* Ensure sections take full width */
    .full-section {
      width: 100% !important;
      margin: 0 auto !important;
      padding: 0 !important;
    }

    /* small fix for Streamlit white gaps */
    section[data-testid="stVerticalBlock"] {
      padding: 0 !important;
      margin: 0 !important;
      background: transparent !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# -------------------------
# Hero + Navbar HTML (component)
# -------------------------
def render_hero_and_nav():
    hero_html = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    :root{--card-bg:#0b0c0f;--pink:#ff53d6;--violet:#8b8bff;--cyan:#00d4ff}
    html,body{margin:0;padding:0;font-family:Inter,system-ui,-apple-system,'Segoe UI',Roboto}
    body{background:transparent}
    .nav {
      position:fixed; top:12px; left:50%; transform:translateX(-50%); z-index:9999; display:flex; align-items:center;
      gap:18px; padding:10px 20px; border-radius:12px; backdrop-filter: blur(10px) saturate(120%);
      background: rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.04);
      box-shadow:0 20px 50px rgba(2,6,23,0.35); transition: transform 260ms ease, opacity 260ms ease;
      max-width:1200px; width:90%;
    }
    .nav.hidden { transform: translateY(-120%); opacity:0; pointer-events:none;}
    .nav .brand{font-weight:800;color:white;font-size:18px}
    .nav a{color:rgba(255,255,255,0.95);text-decoration:none;padding:6px 10px;border-radius:8px;font-weight:700}
    .hero-wrap{height:100vh;min-height:640px;display:flex;align-items:center;justify-content:center;padding:28px;}
    .hero-card{width:min(1200px,96%); background: linear-gradient(180deg, rgba(5,4,6,0.95), rgba(12,9,12,0.95)); border-radius:36px; padding:64px; position:relative; box-shadow:0 30px 80px rgba(0,0,0,0.45); overflow:hidden}
    #tsparticles { position:absolute; inset:0; z-index:0; border-radius:36px }
    .hero-inner{position:relative; z-index:2; color:white; text-align:center}
    .title{font-size:56px;font-weight:800;color:var(--pink);margin:0}
    .role{font-size:20px;font-weight:700;color:var(--violet);margin:8px 0 18px}
    .desc{max-width:900px;margin:0 auto 28px;color:rgba(255,255,255,0.9);line-height:1.6}
    .cta{display:flex;gap:14px;justify-content:center;margin-bottom:18px}
    .btn-primary{background:linear-gradient(90deg,var(--pink),var(--violet));color:white;padding:12px 22px;border-radius:28px;font-weight:800;text-decoration:none}
    .btn-ghost{background:transparent;color:var(--violet);padding:10px 18px;border-radius:28px;border:2px solid rgba(139,139,255,0.08);font-weight:700}
    .socials{display:flex;gap:12px;justify-content:center;margin-top:10px}
    .social{width:44px;height:44px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);color:#dbe8ff}
    /* floating FAB */
    .fab { position: fixed; right: 20px; bottom: 24px; width:64px; height:64px; border-radius:50%; background: linear-gradient(90deg,var(--pink),var(--violet)); display:flex;align-items:center;justify-content:center;color:white;font-weight:800;font-size:22px; box-shadow:0 18px 40px rgba(0,0,0,0.35); z-index:9998; cursor:pointer; }
    .fab:active{transform:scale(.98)}
    /* modal & toast styles will be injected later */
    @media (max-width:980px){
      .title{font-size:34px}
      .hero-card{padding:28px}
      .nav{left:12px;transform:none;width:calc(100% - 24px)}
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
            <a class="social" href="mailto:aryanxsharma26@gmail.com">✉️</a>
          </div>
        </div>
      </div>
    </div>

    <div class="fab" id="fab">✉</div>

    <div id="modal-root"></div>
    <div id="toast-root"></div>

    <script>
    // particles loader
    (function(){
      function initParticles(){
        if(window.tsParticles){
          tsParticles.load("tsparticles", {
            fullScreen: { enable: false },
            particles: {
              number: { value: 28 },
              color: { value: ["#ff6ad1","#8b8bff","#00d4ff"] },
              shape: { type: "circle" },
              opacity: { value: 0.65 },
              size: { value: { min: 2, max: 6 } },
              move: { enable: true, speed: 0.6, outModes: "out" }
            },
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

    // auto-hide navbar logic: hides on scroll down, shows on scroll up
    (function(){
      var lastScroll = 0;
      var nav = document.getElementById('topnav');
      window.addEventListener('scroll', function(){
        var st = window.scrollY || window.pageYOffset;
        if (st > lastScroll && st > 120){
          // scrolling down
          nav.classList.add('hidden');
        } else {
          nav.classList.remove('hidden');
        }
        lastScroll = st <= 0 ? 0 : st;
      }, { passive: true });

      // Smooth nav anchor scroll
      document.querySelectorAll('.nav a').forEach(function(a){
        a.addEventListener('click', function(e){
          e.preventDefault();
          var id = a.getAttribute('href').replace('#', '');
          var el = document.getElementById(id);
          if(el){ el.scrollIntoView({behavior:'smooth', block:'start'}); }
        });
      });
    })();

    // FAB -> modal handler
    (function(){
      var fab = document.getElementById('fab');
      var modalRoot = document.getElementById('modal-root');
      fab.addEventListener('click', function(){
        modalRoot.innerHTML = `
          <div class="modal-backdrop" id="modal-backdrop" style="position:fixed;inset:0;background:rgba(0,0,0,0.45);display:flex;align-items:center;justify-content:center;z-index:10000;animation:fadeIn .18s ease-out;">
            <div style="background:linear-gradient(180deg,#0f1114,#151517);border-radius:12px;padding:18px;width:92%;max-width:520px;box-shadow:0 30px 80px rgba(0,0,0,0.7);border:1px solid rgba(255,255,255,0.04);color:#eaf2ff;">
              <div style="font-weight:800;font-size:16px;margin-bottom:8px">Send an anonymous message</div>
              <textarea id="anon_text" placeholder="Share a thought..." style="width:100%;height:120px;border-radius:8px;padding:12px;background:#0b0c0e;border:1px solid rgba(255,255,255,0.04);color:#eaf2ff"></textarea>
              <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:10px">
                <button id="anon_cancel" style="background:transparent;border:1px solid rgba(255,255,255,0.08);padding:8px 12px;border-radius:8px;color:#dbe8ff">Cancel</button>
                <button id="anon_send" style="background:linear-gradient(90deg,#ff77e9,#8a6aff);border:none;padding:8px 12px;border-radius:8px;color:#001018;font-weight:800">Send anonymously</button>
              </div>
            </div>
          </div>
        `;
        document.getElementById('anon_cancel').addEventListener('click', function(){ modalRoot.innerHTML = ''; });
        document.getElementById('anon_send').addEventListener('click', function(){
          var v = document.getElementById('anon_text').value;
          if(!v || !v.trim()){ alert('Write a message'); return; }
          var params = new URLSearchParams();
          params.set('anon_q', v);
          window.location.search = params.toString(); // navigate with query param
        });
      });
    })();
    </script>
    """
    # replace placeholders
    hero_html = hero_html.replace("__HERO_NAME__", HERO_NAME).replace("__HERO_ROLE__", HERO_ROLE)
    # render as component — height approx viewport; global background ensures continuity
    components.html(hero_html, height=920, scrolling=False)

# -------------------------
# Render page sections (Streamlit) — ensure each has class full-section and height:100vh
# -------------------------
def render_sections():
    # wrapper container
    st.markdown('<div class="full-section">', unsafe_allow_html=True)

    # About (100vh)
    about_html = f"""
    <div id="about" style="height:100vh;display:flex;align-items:center;padding:48px 24px;">
      <div style="max-width:1100px;margin:0 auto;color:white;">
        <h2 style="color:var(--accent-violet);font-size:40px;margin-bottom:12px">About</h2>
        <p style="font-size:18px;color:rgba(255,255,255,0.9);max-width:900px">Hi, I am <strong style="color:white">{HERO_NAME}</strong>. {HERO_ROLE}. This site showcases projects, photos, anonymous writings and a friendly AI chatbot. Scroll to explore.</p>
      </div>
    </div>
    """
    st.markdown(about_html, unsafe_allow_html=True)

    # Skills (100vh)
    skills_html = """
    <div id="skills" style="height:100vh;display:flex;align-items:center;padding:48px 24px;">
      <div style="max-width:1100px;margin:0 auto;color:white;">
        <h2 style="color:var(--accent-violet);font-size:40px;margin-bottom:12px">Skills</h2>
        <div style="display:flex;flex-wrap:wrap;gap:10px;">
          <span style="padding:8px 12px;border-radius:8px;background:linear-gradient(90deg,#6b5bff,#ff6ad1);font-weight:700">Python</span>
          <span style="padding:8px 12px;border-radius:8px;background:linear-gradient(90deg,#6b5bff,#ff6ad1);font-weight:700">Streamlit</span>
          <span style="padding:8px 12px;border-radius:8px;background:linear-gradient(90deg,#6b5bff,#ff6ad1);font-weight:700">React</span>
          <span style="padding:8px 12px;border-radius:8px;background:linear-gradient(90deg,#6b5bff,#ff6ad1);font-weight:700">Web Dev</span>
          <span style="padding:8px 12px;border-radius:8px;background:linear-gradient(90deg,#6b5bff,#ff6ad1);font-weight:700">AI/ML</span>
        </div>
      </div>
    </div>
    """
    st.markdown(skills_html, unsafe_allow_html=True)

    # Projects (carousel) — rendered via components for smoothness
    projects = [
        {"title": "Draw App", "tagline": "Collaborative drawing & whiteboard", "desc": "A collaborative drawing app with real-time multiuser support.", "tags": ["Canvas","WebSockets","Node.js"]},
        {"title": "Portfolio Builder", "tagline": "Template-driven portfolio generator", "desc": "Generate portfolios from templates and content rapidly.", "tags": ["React","Templates","Deploy"]}
    ]
    proj_html = """
    <style>
    .proj-section{height:100vh;display:flex;align-items:center;padding:28px}
    .proj-wrap{max-width:1100px;margin:0 auto;background:linear-gradient(180deg,rgba(255,255,255,0.02),rgba(255,255,255,0.01));padding:18px;border-radius:14px}
    .proj-inner{display:flex;gap:24px;align-items:center}
    .proj-media{flex:1;min-height:260px;background:linear-gradient(180deg,#0f0f12,#1a1a1d);border-radius:12px;display:flex;align-items:center;justify-content:center;color:#9aa0a6}
    .proj-detail{flex:1}
    .tag{display:inline-block;background:linear-gradient(90deg,#6b5bff,#ff6ad1);color:#fff;padding:6px 10px;border-radius:999px;margin-right:8px;margin-bottom:8px;font-weight:700}
    .dots{display:flex;gap:8px;justify-content:center;margin-top:14px}
    .dot{width:10px;height:10px;border-radius:50%;background:rgba(0,0,0,0.1)}
    .dot.active{background:linear-gradient(90deg,#6b5bff,#ff6ad1)}
    @media (max-width:880px){ .proj-inner{flex-direction:column} .proj-media{width:100%} }
    </style>
    <div id="projects" class="proj-section">
      <div class="proj-wrap">
        <div id="carousel"></div>
        <div class="dots" id="dots"></div>
      </div>
    </div>
    <script>
    (function(){
      var projects = __PJSON__;
      var carousel = document.getElementById('carousel');
      var dots = document.getElementById('dots');
      var idx = 0;
      function render(i){
        var p = projects[i];
        var html = '<div class="proj-inner">';
        html += '<div class="proj-media"><div style="text-align:center;padding:18px;"><b style="font-size:20px;color:#fff">'+p.title+'</b><div style="color:#9aa0a6;margin-top:10px">'+p.tagline+'</div></div></div>';
        html += '<div class="proj-detail"><h3 style="margin:0;color:#fff">'+p.title+'</h3><p style="color:#cfd6e8">'+p.desc+'</p><div>';
        p.tags.forEach(function(t){ html += '<span class="tag">'+t+'</span>'; });
        html += '</div><div style="margin-top:12px"><button style="padding:8px 12px;border-radius:8px;border:1px solid rgba(255,255,255,0.06);background:white;margin-right:8px">Code</button><button style="padding:8px 12px;border-radius:8px;background:linear-gradient(90deg,#6b5bff,#ff6ad1);color:#fff;border:none">Live Demo</button></div></div></div>';
        carousel.innerHTML = html;
        dots.innerHTML = '';
        for(var k=0;k<projects.length;k++){
          var d = document.createElement('div'); d.className = 'dot' + (k===i ? ' active' : '');
          (function(n){ d.onclick = function(){ idx=n; render(n); }; })(k);
          dots.appendChild(d);
        }
      }
      render(0);
      setInterval(function(){ idx = (idx+1) % projects.length; render(idx); }, 8000);
    })();
    </script>
    """
    components.html(proj_html.replace("__PJSON__", json.dumps(projects)), height=740, scrolling=False)

    # Experience (100vh)
    exp_html = """
    <div id="experience" style="height:100vh;display:flex;align-items:center;padding:48px 24px;">
      <div style="max-width:1100px;margin:0 auto;color:white;">
        <h2 style="color:var(--accent-violet);font-size:40px;margin-bottom:12px">Experience</h2>
        <p style="color:rgba(255,255,255,0.9);max-width:900px">Working on personal projects focused on web & AI, building polished experiences and learning continuously.</p>
      </div>
    </div>
    """
    st.markdown(exp_html, unsafe_allow_html=True)

    # Photos
    imgs = get_gallery_images()
    if imgs:
        photos_html = "<div id='photos' style='height:100vh;padding:48px 24px;'><div style='max-width:1100px;margin:0 auto;color:white;'><h2 style='color:var(--accent-violet);font-size:40px'>Photos</h2><div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-top:12px'>"
        for i in imgs:
            photos_html += f"<img src='{i}' style='width:100%;height:160px;object-fit:cover;border-radius:10px'/>"
        photos_html += "</div></div></div>"
        st.markdown(photos_html, unsafe_allow_html=True)
    else:
        st.markdown('<div id="photos" style="height:100vh;padding:48px 24px;"><div style="max-width:1100px;margin:0 auto;color:white;"><h2 style="color:var(--accent-violet);font-size:40px">Photos</h2><p style="color:rgba(255,255,255,0.85)">No photos found. Add JPG/PNG to the repo root.</p></div></div>', unsafe_allow_html=True)

    # Blog
    posts = get_all_posts()
    blog_html = '<div id="blog" style="height:100vh;padding:48px 24px;"><div style="max-width:1100px;margin:0 auto;color:white;"><h2 style="color:var(--accent-violet);font-size:40px">Blog</h2>'
    if not posts:
        blog_html += '<p style="color:rgba(255,255,255,0.85)">No blog posts found. Add markdown files to blog_posts/</p>'
    else:
        for p in posts:
            blog_html += f"<div style='margin-top:12px;padding:12px;border-radius:8px;background:rgba(255,255,255,0.02)'><b style='color:#fff'>{p['title']}</b><div style='color:rgba(255,255,255,0.6)'>{p['date']}</div><p style='color:rgba(255,255,255,0.8)'>{p['summary']}</p></div>"
    blog_html += '</div></div>'
    st.markdown(blog_html, unsafe_allow_html=True)

    # Writings (full-screen) - Card List layout
    st.markdown('<div id="writings" style="height:100vh;padding:48px 24px;"><div style="max-width:1100px;margin:0 auto;color:white;"><h2 style="color:var(--accent-violet);font-size:40px">Writings</h2>', unsafe_allow_html=True)
    messages = load_messages()
    if not messages:
        st.markdown('<p style="color:rgba(255,255,255,0.85)">No writings yet — click the ✉ button to add anonymously.</p>', unsafe_allow_html=True)
    else:
        cards = "<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px;margin-top:16px'>"
        for m in sorted(messages, key=lambda x: x.get("id",0), reverse=True):
            text = (m.get("text","")[:400] + ("..." if len(m.get("text",""))>400 else ""))
            ts = m.get("timestamp","")
            cards += f"<div style='background:linear-gradient(180deg,#ffffff,#fafaff);padding:14px;border-radius:10px;box-shadow:0 12px 30px rgba(2,6,23,0.06)'><div style='color:#0b0f14;font-weight:700'>{text}</div><div style='color:rgba(0,0,0,0.45);font-size:12px;margin-top:8px'>{ts}</div></div>"
        cards += "</div>"
        st.markdown(cards, unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    # Chatbot (simple)
    st.markdown('<div id="chat" style="height:100vh;padding:48px 24px;"><div style="max-width:1100px;margin:0 auto;color:white;"><h2 style="color:var(--accent-violet);font-size:40px">Chatbot</h2>', unsafe_allow_html=True)
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    for m in st.session_state.chat_messages[-8:]:
        if m["role"] == "user":
            st.markdown(f"<div style='margin-top:8px;padding:10px;border-radius:8px;background:#0f1724;color:#cfe8ff'>{m['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='margin-top:8px;padding:10px;border-radius:8px;background:#f7f6ff;color:#0b0f14'>{m['content']}</div>", unsafe_allow_html=True)
    q = st.text_input("Ask me a question...", key="chat_main_input")
    if q:
        st.session_state.chat_messages.append({"role":"user","content":q})
        answer = {"what is your name": f"My name is {HERO_NAME}.","where are you from":"I am from India."}.get(q.lower(), "Sorry! I don't have an answer for that.")
        st.session_state.chat_messages.append({"role":"bot","content":answer})
        st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Contact
    st.markdown('<div id="contact" style="height:100vh;padding:48px 24px;"><div style="max-width:1100px;margin:0 auto;color:white;"><h2 style="color:var(--accent-violet);font-size:40px">Contact</h2><p style="color:rgba(255,255,255,0.85)">Email: <a href="mailto:aryanxsharma26@gmail.com" style="color:white">aryanxsharma26@gmail.com</a></p></div></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# Handle query params (anon_q) -> save and show toast
# -------------------------
def handle_query_params():
    qp = st.experimental_get_query_params()
    if "anon_q" in qp:
        q = qp.get("anon_q", [""])[0]
        if q and q.strip():
            save_message(q.strip())
            # clear params
            st.experimental_set_query_params()
            # show toast animation
            toast_html = """
            <style>
            .toast{position:fixed;right:20px;bottom:100px;background:linear-gradient(90deg,#ff77e9,#8a6aff);padding:10px 14px;border-radius:10px;color:#001018;font-weight:800;box-shadow:0 18px 40px rgba(0,0,0,0.3);z-index:10001;animation:toastIn .25s ease-out}
            @keyframes toastIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
            </style>
            <div class="toast">Message sent anonymously ✓</div>
            <script>setTimeout(()=>{document.querySelector('.toast').style.transition='opacity .4s';document.querySelector('.toast').style.opacity='0';},2200);setTimeout(()=>{document.querySelector('.toast').remove();},2800);</script>
            """
            components.html(toast_html, height=0)
            st.experimental_rerun()

# -------------------------
# Admin unlocking (hidden unless token)
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
        for m in sorted(msgs, key=lambda x: x.get("id", 0), reverse=True):
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
    # Apply global gradient + remove Streamlit chrome
    force_global_theme()
    # If anon_q param present (from modal), save and show toast
    handle_query_params()
    # Render hero + nav (component)
    render_hero_and_nav()
    # Render all sections via Streamlit but styled to be full-screen and transparent
    render_sections()
    # Admin flow
    admin_unlock_flow()
    # spacing at end
    st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
