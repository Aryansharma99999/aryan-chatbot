# app.py - SmarthSood-style portfolio (fullscreen hero, navbar, projects cards (2), responsive/mobile)
# Features:
# - Fullscreen hero (100vh) with gradient + tsparticles
# - Floating glass-blur navbar (sticky)
# - Sections: Home, About, Skills, Projects (2-card carousel), Experience, Photos, Blog, Writings, Chatbot, Contact
# - Photos grid (loads images from repo root)
# - Blog posts from blog_posts/ (Markdown)
# - Anonymous writings + admin panel (delete/clear)
# - Floating chatbot widget (submits via query param)
# - Mobile friendly & responsive
# - No f-string nesting issues
# - Telegram notifications via TELEGRAM_BOT_TOKEN env var (optional)
import os
import re
import time
import json
import requests
from datetime import datetime
from markdown import markdown
import streamlit as st
import streamlit.components.v1 as components

# -----------------------
# Config
# -----------------------
st.set_page_config(page_title="Aryan Sharma — Portfolio", layout="wide", initial_sidebar_state="collapsed")
BASE_DIR = os.path.dirname(__file__) if os.path.isdir(os.path.dirname(__file__) or "") else "."
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")
MSG_FILE = os.path.join(BASE_DIR, "anonymous_messages.txt")
ADMIN_TOKEN = "admin-aryan"  # change if you want
ADMIN_QUERY_PARAM = "admin"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "") or "8521726094"
HERO_NAME = "Aryan Sharma"
HERO_ROLE = "I'M a developer , writer , editor and a learner"

# -----------------------
# Utilities: messages + telegram
# -----------------------
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

    # Try telegram best-effort
    if TELEGRAM_BOT_TOKEN:
        try:
            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": f"📨 New anonymous message:\n\n{text}\n\nID:{msg['id']}", "parse_mode":"HTML"}
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

# -----------------------
# Blog helpers
# -----------------------
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
        for line in meta.split("\n"):
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
    fs = [f for f in os.listdir(POSTS_DIR) if f.endswith(".md")]
    posts = []
    for f in fs:
        slug = f.replace(".md", "")
        p = get_post_data(slug)
        if p: posts.append(p)
    return posts

# -----------------------
# Gallery helper (safe)
# -----------------------
def get_gallery_images():
    try:
        root = BASE_DIR if os.path.isdir(BASE_DIR) else "."
        files = os.listdir(root)
    except Exception:
        return []
    images = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
    ignore = {"vercel.png", "screenshot.png"}
    return [i for i in images if i not in ignore]

# -----------------------
# Helper: small CSS to remove streamlit padding and hide menu
# -----------------------
def inject_global_css():
    css = """
    <style>
    /* Remove Streamlit default padding and menu to allow full-bleed hero */
    .css-1d391kg {padding-top:0rem !important;} /* older streamlit class fallback */
    .reportview-container .main .block-container{padding-top:0rem !important; padding-left:0rem !important; padding-right:0rem !important;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# -----------------------
# Hero + navbar HTML (placeholders replaced safely)
# -----------------------
def render_hero():
    # build HTML with placeholders __HERO_NAME__ and __HERO_ROLE__ to avoid braces conflicts
    html = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    :root{
      --g1: #ff77e9;
      --g2: #8a6aff;
      --card: #0d0b0e;
      --pink: #ff53d6;
      --violet: #8b8bff;
      --cyan: #00d4ff;
    }
    html,body{height:100%; margin:0; font-family:Inter, system-ui, -apple-system, 'Segoe UI', Roboto;}
    body{background:linear-gradient(135deg,var(--g1) 0%, var(--g2) 100%); overflow-x:hidden;}

    /* Floating glass navbar */
    .glass-nav{
      position:fixed; top:18px; left:50%; transform:translateX(-50%); z-index:9999;
      background: rgba(255,255,255,0.06);
      backdrop-filter: blur(10px) saturate(120%);
      -webkit-backdrop-filter: blur(10px) saturate(120%);
      border: 1px solid rgba(255,255,255,0.06);
      padding:10px 20px; border-radius:16px; box-shadow:0 30px 60px rgba(2,6,23,0.35);
      display:flex; gap:24px; align-items:center; max-width:1200px; width:90%;
    }
    .nav-brand{font-weight:800; color:#fff; font-size:18px; margin-right:6px;}
    .nav-links{display:flex; gap:14px; align-items:center; flex-wrap:wrap;}
    .nav-links a{color:rgba(255,255,255,0.95); text-decoration:none; padding:8px 12px; border-radius:10px; font-weight:700;}
    .nav-links a:hover{background:rgba(255,255,255,0.02);}

    /* Hero full-viewport */
    .hero-viewport{height:100vh; min-height:680px; display:flex; align-items:center; justify-content:center; padding:28px;}
    .hero-card{width:min(1200px,96%); background:linear-gradient(180deg, rgba(4,3,5,0.98), rgba(10,6,10,0.98)); border-radius:36px; padding:64px; position:relative; box-shadow:0 30px 80px rgba(0,0,0,0.45); overflow:hidden;}
    #tsparticles{ position:absolute; inset:0; z-index:0; border-radius:36px; }
    .hero-inner{position:relative; z-index:2; color:#fff; text-align:center;}
    .hero-title{font-size:56px; font-weight:800; color:var(--pink); margin:0; letter-spacing:-1px;}
    .hero-role{font-size:20px; font-weight:700; color:var(--violet); margin:8px 0 18px 0;}
    .hero-desc{max-width:940px;margin:0 auto 28px; color:rgba(255,255,255,0.9); line-height:1.6; font-size:16px;}
    .cta-row{display:flex; gap:14px; justify-content:center; margin-bottom:18px; align-items:center;}
    .btn-primary{background:linear-gradient(90deg,var(--pink),var(--violet)); color:white; padding:12px 22px; border-radius:28px; font-weight:800; text-decoration:none; box-shadow:0 16px 40px rgba(139,60,200,0.16);}
    .btn-ghost{background:transparent; color:var(--violet); padding:10px 18px; border-radius:28px; border:2px solid rgba(139,139,255,0.08); font-weight:700; text-decoration:none;}
    .social-row{display:flex; gap:12px; justify-content:center; margin-top:10px;}
    .social-btn{width:48px;height:48px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.03); color:#dbe8ff; text-decoration:none; font-weight:700;}

    /* Floating chat */
    .floating-chat{position:absolute; right:12px; bottom:40px; width:340px; background: linear-gradient(180deg,#0f1114,#17171a); border-radius:14px; padding:12px; box-shadow: 0 24px 60px rgba(8,8,20,0.7); border:1px solid rgba(255,255,255,0.04); z-index:3;}
    .floating-chat h4{ color:var(--cyan); margin:6px 0 8px 0; font-weight:800; font-size:16px;}
    .floating-chat .bubble{background:rgba(255,255,255,0.04); padding:10px;border-radius:8px;color:#dbe8ff; margin-bottom:8px;}
    .floating-chat .input-row{display:flex; gap:8px; margin-top:8px;}
    .floating-chat input{flex:1; background:#0f1114; border-radius:8px; border:1px solid rgba(255,255,255,0.04); color:#e6eefc; padding:8px;}
    .floating-chat button{background:var(--cyan); color:#001018; border-radius:8px; border:none; padding:8px 12px; font-weight:700; cursor:pointer;}

    @media (max-width:980px){
      .hero-title{font-size:34px;}
      .hero-card{padding:28px;}
      .floating-chat{right:12px; bottom:14px; width:88%; left:6%; }
      .glass-nav{left:8px; transform:none; width:calc(100% - 16px);}
      .nav-links{display:none;}
    }
    </style>

    <div class="glass-nav" role="navigation">
      <div class="nav-brand">Aryan</div>
      <div class="nav-links">
        <a href="#home">Home</a>
        <a href="#about">About</a>
        <a href="#skills">Skills</a>
        <a href="#projects">Projects</a>
        <a href="#experience">Experience</a>
        <a href="#photos">Photos</a>
        <a href="#blog">Blog</a>
        <a href="#writings">Writings</a>
        <a href="#chat">Chatbot</a>
        <a href="#contact">Contact</a>
      </div>
    </div>

    <div id="home" class="hero-viewport">
      <div class="hero-card">
        <div id="tsparticles"></div>
        <div class="hero-inner">
          <h1 class="hero-title">__HERO_NAME__</h1>
          <div class="hero-role">__HERO_ROLE__</div>
          <div class="hero-desc">Welcome to my personal website — explore projects, photos, writings and chat with my AI assistant.</div>
          <div class="cta-row">
            <a class="btn-primary" href="/resume.pdf" target="_blank">Download Resume</a>
            <a class="btn-ghost" href="#contact">Get In Touch</a>
          </div>
          <div class="social-row">
            <a class="social-btn" href="https://github.com/aryansharma99999" target="_blank" title="GitHub">
              <!-- github svg -->
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M12 0.5C5.5 0.5 0.5 5.5 0.5 12C0.5 17.2 3.9 21.7 8.4 23.2C9 23.3 9.2 23 9.2 22.7C9.2 22.4 9.2 21.7 9.2 20.7C6 21.3 5.2 19.3 5.2 19.3C4.6 17.9 3.6 17.5 3.6 17.5C2.2 16.7 3.7 16.7 3.7 16.7C5.3 16.8 6.1 18.3 6.1 18.3C7.6 20.6 9.8 20 10.8 19.7C10.9 18.7 11.3 18 11.8 17.6C8.9 17.2 6 16.1 6 11.5C6 10.2 6.4 9.2 7.2 8.4C7.1 8 6.7 6.8 7.3 5.1C7.3 5.1 8.3 4.7 9.2 6.2C10 5.9 10.9 5.8 11.8 5.8C12.7 5.8 13.6 5.9 14.4 6.2C15.3 4.7 16.3 5.1 16.3 5.1C16.9 6.8 16.5 8 16.4 8.4C17.2 9.2 17.6 10.2 17.6 11.5C17.6 16.1 14.7 17.2 11.8 17.6C12.3 18.1 12.7 19 12.7 20.2C12.7 22 12.7 23 12.7 23.2C17.2 21.7 20.6 17.2 20.6 12C20.6 5.5 15.6 0.5 12 0.5Z" fill="currentColor"/></svg>
            </a>
            <a class="social-btn" href="https://instagram.com/aryanxsharma26" target="_blank" title="Instagram">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M7.75 2H16.25C20.1 2 22 3.9 22 7.75V16.25C22 20.1 20.1 22 16.25 22H7.75C3.9 22 2 20.1 2 16.25V7.75C2 3.9 3.9 2 7.75 2ZM12 7.1C9.24 7.1 7.1 9.24 7.1 12C7.1 14.76 9.24 16.9 12 16.9C14.76 16.9 16.9 14.76 16.9 12C16.9 9.24 14.76 7.1 12 7.1ZM18.4 6.3C18.4 6.86 17.96 7.3 17.4 7.3C16.84 7.3 16.4 6.86 16.4 6.3C16.4 5.74 16.84 5.3 17.4 5.3C17.96 5.3 18.4 5.74 18.4 6.3Z" fill="currentColor"/></svg>
            </a>
            <a class="social-btn" href="mailto:aryanxsharma26@gmail.com" title="Email">✉️</a>
          </div>
        </div>

        <div class="floating-chat" id="floating-chat">
          <h4>Aryan's AI Chatbot</h4>
          <div class="bubble">Hi! Ask me questions about Aryan.</div>
          <div class="input-row">
            <input id="floating_input" placeholder="Type your question..." />
            <button id="floating_send">Send</button>
          </div>
          <div style="font-size:12px;color:rgba(255,255,255,0.55);margin-top:8px">Anonymous messages appear in admin.</div>
        </div>
      </div>
    </div>

    <script>
    // load tsparticles if not present
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

    document.addEventListener('DOMContentLoaded', function(){
      var btn = document.getElementById('floating_send');
      if(btn){
        btn.addEventListener('click', function(){
          var v = document.getElementById('floating_input').value;
          if(!v || !v.trim()){ alert('Write a question'); return; }
          var params = new URLSearchParams();
          params.set('anon_q', v);
          window.open(window.location.pathname + "?" + params.toString(), "_self");
        });
      }
      // smooth scroll for nav links
      document.querySelectorAll('.nav-links a').forEach(function(a){
        a.addEventListener('click', function(e){
          e.preventDefault();
          var id = a.getAttribute('href').replace('#','');
          var el = document.getElementById(id);
          if(el){
            el.scrollIntoView({behavior:'smooth', block:'start'});
          }
        });
      });
    });
    </script>
    """
    html = html.replace("__HERO_NAME__", HERO_NAME).replace("__HERO_ROLE__", HERO_ROLE)
    components.html(html, height=900, scrolling=False)

# -----------------------
# Sections: Projects (2-card carousel) and other content
# -----------------------
def render_main_sections():
    # Wrapper to center content and provide spacing
    st.markdown('<div style="max-width:1200px;margin:40px auto 60px;padding:0 16px;">', unsafe_allow_html=True)

    # Two-column area: left writings/admin, right: tabs (Chatbot/Blog/Photos) — similar to earlier design
    col1, col2 = st.columns([1, 2.2], gap="large")

    with col1:
        st.markdown('<div id="writings" style="margin-bottom:14px"><h3 style="color:#0f1724">Writings (anonymous)</h3></div>', unsafe_allow_html=True)
        messages = load_messages()
        if not messages:
            st.markdown("<div style='padding:12px;border-radius:8px;background:rgba(0,0,0,0.03)'>No writings yet.</div>", unsafe_allow_html=True)
        else:
            for m in sorted(messages, key=lambda x: x.get("id",0), reverse=True)[:8]:
                st.markdown(f"<div style='padding:10px;border-radius:8px;background:rgba(0,0,0,0.03);margin-bottom:8px'><div style='font-weight:600'>{m.get('text')[:150]}{'...' if len(m.get('text',''))>150 else ''}</div><div style='font-size:12px;color:rgba(0,0,0,0.55);margin-top:6px'>{m.get('timestamp')}</div></div>", unsafe_allow_html=True)
        st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
        with st.form("anon_write", clear_on_submit=True):
            txt = st.text_area("Your message", max_chars=1200, placeholder="Share anonymously...")
            sub = st.form_submit_button("Send anonymously")
        if sub:
            if not txt or not txt.strip():
                st.warning("Please write something.")
            else:
                save_message(txt.strip())
                st.success("Message saved. Thank you!")

        st.markdown('<div style="margin-top:12px"><h4>Admin</h4></div>', unsafe_allow_html=True)
        qp = st.experimental_get_query_params()
        if ADMIN_QUERY_PARAM in qp and qp.get(ADMIN_QUERY_PARAM, [""])[0] == ADMIN_TOKEN:
            st.session_state._admin_unlocked = True
        if st.session_state.get("_admin_unlocked", False):
            st.success("Admin unlocked")
            msgs = load_messages()
            st.markdown(f"<div style='color:rgba(0,0,0,0.6)'>Total messages: {len(msgs)}</div>", unsafe_allow_html=True)
            for m in sorted(msgs, key=lambda x: x.get("id",0), reverse=True):
                with st.expander(f"ID {m.get('id')} • {m.get('timestamp')}"):
                    st.write(m.get("text"))
                    if st.button("Delete", key=f"del_{m.get('id')}"):
                        new = [x for x in msgs if x.get("id") != m.get("id")]
                        overwrite_messages(new)
                        st.success("Deleted")
                        st.experimental_rerun()
            if st.button("Clear all messages"):
                overwrite_messages([])
                st.experimental_rerun()
        else:
            token = st.text_input("Enter admin token", type="password", key="adm_token_right")
            if st.button("Unlock admin"):
                if token.strip() == ADMIN_TOKEN:
                    st.session_state._admin_unlocked = True
                    st.experimental_set_query_params(**{ADMIN_QUERY_PARAM: ADMIN_TOKEN})
                    st.experimental_rerun()
                else:
                    st.error("Invalid token")

    with col2:
        # small tabs
        tabs = st.tabs(["Chatbot","Blog","Photos"])
        with tabs[0]:
            st.markdown('<div id="chat"><h3>Chatbot</h3></div>', unsafe_allow_html=True)
            chat_qs = {"what is your name": f"My name is {HERO_NAME}.", "where are you from":"I am from India.", "what do you do":"I build, write and learn."}
            if "chat_messages" not in st.session_state:
                st.session_state.chat_messages = []
            for m in st.session_state.chat_messages[-8:]:
                if m["role"]=="user":
                    st.markdown(f"<div style='background:#0f1724;padding:10px;border-radius:8px;margin-bottom:8px;color:#cfe8ff'>{m['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='background:#f7f6ff;color:#0b0f14;padding:10px;border-radius:8px;margin-bottom:8px'>{m['content']}</div>", unsafe_allow_html=True)
            q = st.text_input("Ask me a question...", key="chat_input_small")
            if q:
                st.session_state.chat_messages.append({"role":"user","content":q})
                a = chat_qs.get(q.lower(), "Sorry! I don't have an answer for that.")
                st.session_state.chat_messages.append({"role":"bot","content":a})
                st.experimental_rerun()
        with tabs[1]:
            st.markdown('<div id="blog"><h3>Blog</h3></div>', unsafe_allow_html=True)
            posts = get_all_posts()
            if not posts:
                st.info("No blog posts found.")
            else:
                for p in posts:
                    st.markdown(f"<div style='padding:12px;border-radius:8px;background:rgba(0,0,0,0.03);margin-bottom:10px'><div style='font-weight:700'>{p['title']}</div><div style='color:rgba(0,0,0,0.6)'>{p['date']}</div><p style='margin-top:8px'>{p['summary']}</p></div>", unsafe_allow_html=True)
                    if st.button("Read", key=f"read_{p['slug']}"):
                        st.session_state.selected_post = p['slug']
                        st.experimental_rerun()
                if st.session_state.get("selected_post"):
                    slug = st.session_state.get("selected_post")
                    post = get_post_data(slug)
                    if post:
                        st.markdown("<hr>", unsafe_allow_html=True)
                        st.markdown(f"<h3 style='color:#444'>{post['title']}</h3>", unsafe_allow_html=True)
                        st.markdown(post['html'], unsafe_allow_html=True)
                        if st.button("Back to list"):
                            st.session_state.selected_post = None
                            st.experimental_rerun()
        with tabs[2]:
            st.markdown('<div id="photos"><h3>Photos</h3></div>', unsafe_allow_html=True)
            imgs = get_gallery_images()
            if not imgs:
                st.info("No images found. Upload JPG/PNG to the repo root.")
            else:
                grid_css = """
                <style>
                .photo-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-top:8px}
                .photo-grid img{width:100%;height:140px;object-fit:cover;border-radius:8px;box-shadow:0 10px 30px rgba(2,6,23,0.2);transition:transform .25s ease}
                .photo-grid img:hover{transform:translateY(-6px) scale(1.02)}
                </style>
                """
                imgs_html = "".join([f"<img src='{i}' alt='{i}' />" for i in imgs])
                st.markdown(grid_css + f"<div class='photo-grid'>{imgs_html}</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close wrapper

    # Projects section: 2-card carousel (desktop large visual, mobile stacked)
    st.markdown('<div id="projects" style="padding:40px 0; background:linear-gradient(180deg, rgba(255,255,255,0.00), rgba(0,0,0,0.00));">', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align:center;color:#8b8bff;font-size:32px;margin-bottom:6px">Featured Projects</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:rgba(0,0,0,0.6);max-width:900px;margin:8px auto 24px">Here are some of my recent projects.</p>', unsafe_allow_html=True)

    # Two sample project cards data (you can replace with dynamic content later)
    projects = [
        {
            "title": "Draw App",
            "tagline": "Collaborative drawing & whiteboard",
            "desc": "A collaborative drawing app with a hand-drawn feel and real-time collaboration features.",
            "tags": ["Next.js", "Canvas", "WebSockets", "Tailwind CSS", "Node.js"]
        },
        {
            "title": "Portfolio Builder",
            "tagline": "Generate portfolios from templates",
            "desc": "A template-based portfolio generator that helps users create beautiful portfolios quickly.",
            "tags": ["React", "Templates", "Design System", "Deploy"]
        }
    ]

    # Carousel HTML (responsive)
    proj_html = """
    <style>
    .proj-wrap{max-width:1100px;margin:20px auto 40px; padding:18px; border-radius:18px; background:linear-gradient(180deg, rgba(0,0,0,0.03), rgba(0,0,0,0.02));}
    .proj-inner{display:flex; align-items:center; gap:24px;}
    .proj-media{flex:1; min-height:260px; background:linear-gradient(180deg,#0f0f12,#1a1a1d); border-radius:14px; display:flex; align-items:center; justify-content:center; color:#888;}
    .proj-detail{flex:1; color:rgba(0,0,0,0.8);}
    .proj-title{font-size:26px; font-weight:800; color:#222; margin:0 0 6px;}
    .proj-desc{color:rgba(0,0,0,0.6); margin-bottom:14px;}
    .tag{display:inline-block;background:linear-gradient(90deg,#6b5bff,#ff6ad1); color:white;padding:6px 10px;border-radius:999px;margin-right:8px;margin-bottom:8px;font-weight:700;font-size:12px;}
    .proj-controls{display:flex; gap:12px; align-items:center; margin-top:12px;}
    .pill{padding:10px 12px;border-radius:8px;background:white;border:1px solid rgba(0,0,0,0.06);font-weight:700}
    .arrow{width:44px;height:44px;border-radius:50%;background:transparent;border:2px solid rgba(0,0,0,0.06);display:flex;align-items:center;justify-content:center;cursor:pointer;box-shadow:0 10px 30px rgba(0,0,0,0.12)}
    .dots{display:flex;gap:8px;align-items:center;justify-content:center;margin-top:14px}
    .dot{width:10px;height:10px;border-radius:50%;background:rgba(0,0,0,0.1)}
    .dot.active{background:linear-gradient(90deg,#6b5bff,#ff6ad1)}
    @media (max-width:880px){
      .proj-inner{flex-direction:column;}
      .proj-media{width:100%;}
    }
    </style>

    <div class="proj-wrap">
      <div id="carousel" class="proj-carousel">
        <!-- slides inserted by JS -->
      </div>
      <div class="dots" id="proj-dots"></div>
    </div>

    <script>
    (function(){
      var projects = __PROJECTS_JSON__;
      var carousel = document.getElementById('carousel');
      var dots = document.getElementById('proj-dots');
      var current = 0;

      function renderSlide(i){
        var p = projects[i];
        var html = '<div class="proj-inner">';
        html += '<div class="proj-media"><div style="padding:24px;color:#9aa0a6;text-align:center"><div style="font-weight:800;font-size:20px">'+p.title+'</div><div style="margin-top:14px;color:#7a7f86">'+p.tagline+'</div></div></div>';
        html += '<div class="proj-detail"><div class="proj-title">'+p.title+'</div><div class="proj-desc">'+p.desc+'</div><div>';
        p.tags.forEach(function(t){ html += '<span class="tag">'+t+'</span>'; });
        html += '</div><div class="proj-controls"><div class="pill">Code</div><div class="pill" style="background:linear-gradient(90deg,#6b5bff,#ff6ad1);color:#fff;border:none">Live Demo</div></div></div></div>';
        carousel.innerHTML = html;
        // update dots
        dots.innerHTML = '';
        for(var k=0;k<projects.length;k++){
          var d = document.createElement('div');
          d.className = 'dot' + (k===i ? ' active' : '');
          d.addEventListener('click',(function(idx){ return function(){ current = idx; renderSlide(idx); }; })(k));
          dots.appendChild(d);
        }
      }

      // prev/next by swipe left/right on mobile
      var touchstartX = 0;
      var touchendX = 0;
      carousel.addEventListener('touchstart', function(e){ touchstartX = e.changedTouches[0].screenX; }, false);
      carousel.addEventListener('touchend', function(e){ touchendX = e.changedTouches[0].screenX; if(touchendX < touchstartX - 30){ current = (current+1) % projects.length; renderSlide(current); } if(touchendX > touchstartX + 30){ current = (current-1+projects.length)%projects.length; renderSlide(current); } }, false);

      // initial
      renderSlide(0);
      // auto rotate
      setInterval(function(){ current = (current+1) % projects.length; renderSlide(current); }, 8000);
    })();
    </script>
    """
    # inject projects json safely
    projects_json = json.dumps(projects)
    proj_html = proj_html.replace("__PROJECTS_JSON__", projects_json)
    components.html(proj_html, height=420, scrolling=False)

    st.markdown('</div>', unsafe_allow_html=True)  # close projects section

    # Experience & Skills (simple)
    st.markdown('<div id="skills" style="padding:40px 0;"><h2 style="text-align:center;color:#8b8bff">Skills</h2>', unsafe_allow_html=True)
    skills = ["Python","Streamlit","Web Dev","HTML/CSS","JavaScript","React","Git","AI/ML"]
    chips = "".join([f"<span style='display:inline-block;margin:6px 6px 0 0;padding:8px 10px;border-radius:8px;background:linear-gradient(90deg,#6b5bff,#ff6ad1);color:#fff;font-weight:700'>{s}</span>" for s in skills])
    st.markdown(f"<div style='max-width:900px;margin:8px auto 0;text-align:center'>{chips}</div></div>", unsafe_allow_html=True)

    st.markdown('<div id="experience" style="padding:40px 0;"><h2 style="text-align:center;color:#8b8bff">Experience</h2><div style="max-width:900px;margin:10px auto;color:rgba(0,0,0,0.6);text-align:center">Working on personal projects and learning systems and AI.</div></div>', unsafe_allow_html=True)

    # Contact
    st.markdown('<div id="contact" style="padding:40px 0;"><h2 style="text-align:center;color:#8b8bff">Contact</h2>', unsafe_allow_html=True)
    st.markdown(f"<div style='max-width:900px;margin:10px auto;color:rgba(0,0,0,0.6);text-align:center'>Email: <a href='mailto:aryanxsharma26@gmail.com'>aryanxsharma26@gmail.com</a></div></div>", unsafe_allow_html=True)

# -----------------------
# Main
# -----------------------
def main():
    # If floating chat submitted via query param 'anon_q'
    qp = st.experimental_get_query_params()
    if "anon_q" in qp:
        q = qp.get("anon_q", [""])[0]
        if q and q.strip():
            save_message(q.strip())
            st.experimental_set_query_params()  # remove
            st.success("Your anonymous message was saved. Thank you!")

    inject_global_css()
    render_hero()
    render_main_sections()
    # footer spacing
    st.markdown("<div style='height:120px'></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
