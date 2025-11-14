# app.py - Full SmarthSood-like portfolio replicated in Streamlit
# Sections: Home · About · Skills · Projects · Experience · Photos · Blog · Writings · Chatbot · Contact
# Navbar: floating glass-blur bar (sticky)
# Floating chatbot widget, photos grid, blog, anonymous writings, admin
# No hard-coded tokens. TELEGRAM_BOT_TOKEN must be set in env/secrets if you want Telegram alerts.

import os
import re
import time
import json
import requests
from datetime import datetime
from markdown import markdown
import streamlit as st
import streamlit.components.v1 as components

# ----------------------------
# Basic config & constants
# ----------------------------
st.set_page_config(page_title="Aryan Sharma — Portfolio", layout="wide", initial_sidebar_state="collapsed")
BASE_DIR = os.path.dirname(__file__)
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")
MSG_FILE = os.path.join(BASE_DIR, "anonymous_messages.txt")
ADMIN_TOKEN = "admin-aryan"
ADMIN_QUERY_PARAM = "admin"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = "8521726094"
HERO_NAME = "Aryan Sharma"
HERO_ROLE = "I'M a developer , writer , editor and a learner"

# ----------------------------
# Utilities: messages & telegram
# ----------------------------
def ensure_msg_file():
    if not os.path.exists(MSG_FILE):
        with open(MSG_FILE, "w", encoding="utf-8") as f:
            pass

def save_message(text):
    ensure_msg_file()
    msg = {"id": int(time.time() * 1000), "text": text, "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}
    with open(MSG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(msg, ensure_ascii=False) + "\n")
    # Telegram notification (best effort)
    if TELEGRAM_BOT_TOKEN:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": f"📨 New anonymous message:\n\n{text}\n\nID:{msg['id']}", "parse_mode":"HTML"}
            requests.post(url, json=payload, timeout=6)
        except Exception:
            pass
    return msg

def load_messages():
    ensure_msg_file()
    out = []
    with open(MSG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                out.append(json.loads(line))
            except:
                continue
    return out

def overwrite_messages(msgs):
    with open(MSG_FILE, "w", encoding="utf-8") as f:
        for m in msgs:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

# ----------------------------
# Blog helpers
# ----------------------------
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
        if p:
            posts.append(p)
    return posts

# ----------------------------
# Photos helper (loads images from repo root)
# ----------------------------
def get_gallery_images():
    files = [f for f in os.listdir(BASE_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
    # remove common dev files if any
    ignore = {"vercel.png", "screenshot.png"}
    images = [f for f in files if f not in ignore]
    return images

# ----------------------------
# Hero + Navbar (HTML string w/ placeholders replaced safely)
# ----------------------------
def render_hero_and_navbar():
    # Use placeholders __HERO_NAME__ and __HERO_ROLE__ to avoid f-string JS braces problems
    html = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    :root{
      --grad1:#ff77e9; --grad2:#8a6aff; --card:#1b141a;
      --pink:#ff53d6; --violet:#8b8bff; --cyan:#00d4ff;
    }
    html,body,.stApp{height:100%; margin:0; font-family:Inter, system-ui, -apple-system, 'Segoe UI', Roboto;}
    body{background: linear-gradient(135deg, var(--grad1) 0%, var(--grad2) 100%);}
    /* floating glass navbar */
    .glass-nav{
      position:fixed; top:18px; left:50%; transform:translateX(-50%); z-index:9999;
      background: rgba(255,255,255,0.05);
      backdrop-filter: blur(8px) saturate(120%);
      -webkit-backdrop-filter: blur(8px) saturate(120%);
      border: 1px solid rgba(255,255,255,0.06);
      padding:8px 18px; border-radius:14px; box-shadow:0 8px 30px rgba(2,6,23,0.5);
      display:flex; gap:22px; align-items:center;
    }
    .nav-brand{font-weight:800; color:#fff; letter-spacing:0.3px; margin-right:14px;}
    .nav-links{display:flex; gap:10px; align-items:center;}
    .nav-links a{color:rgba(255,255,255,0.95); text-decoration:none; padding:8px 12px; border-radius:8px; font-weight:600;}
    .nav-links a:hover{background:rgba(255,255,255,0.02);}
    /* hero */
    .hero-wrap{display:flex; align-items:center; justify-content:center; min-height:92vh; padding:28px;}
    .hero-card{width:min(1200px,96%); background: linear-gradient(180deg, rgba(4,3,5,0.98), rgba(10,6,10,0.98)); border-radius:36px; padding:64px; position:relative; box-shadow:0 30px 80px rgba(0,0,0,0.45); overflow:visible;}
    #tsparticles{ position:absolute; inset:0; z-index:0; border-radius:36px; }
    .hero-inner{position:relative; z-index:2; color:#fff; text-align:center;}
    .hero-title{font-size:56px; font-weight:800; color:var(--pink); margin:0; letter-spacing:-1px;}
    .hero-role{font-size:18px; font-weight:700; color:var(--violet); margin:8px 0 18px 0;}
    .hero-desc{max-width:900px; margin:0 auto 26px auto; line-height:1.6; color:rgba(255,255,255,0.9); font-size:16px;}
    .cta-row{display:flex; gap:12px; justify-content:center; margin-bottom:18px;}
    .btn-primary{background:linear-gradient(90deg,var(--pink),var(--violet)); color:white; padding:12px 20px; border-radius:28px; font-weight:800; text-decoration:none; box-shadow:0 14px 40px rgba(130,60,200,0.16);}
    .btn-ghost{background:transparent; color:var(--violet); padding:10px 16px; border-radius:28px; border:2px solid rgba(139,139,255,0.12); font-weight:700; text-decoration:none;}
    .social-row{display:flex; gap:12px; justify-content:center; margin-top:10px;}
    .social-btn{width:46px;height:46px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.03); color:#dbe8ff; text-decoration:none; font-weight:700;}
    /* floating chat */
    .floating-chat{position:absolute; right:-42px; top:200px; width:360px; background: linear-gradient(180deg,#0f1114,#17171a); border-radius:18px; padding:12px; box-shadow: 0 24px 60px rgba(8,8,20,0.7); border:1px solid rgba(255,255,255,0.04); z-index:3;}
    .floating-chat h4{ color:var(--cyan); margin:6px 0 8px 0; font-weight:800; font-size:18px;}
    .floating-chat .bubble{background:rgba(255,255,255,0.04); padding:10px;border-radius:8px;color:#dbe8ff; margin-bottom:8px;}
    .floating-chat .input-row{display:flex; gap:8px; margin-top:8px;}
    .floating-chat input{flex:1; background:#0f1114; border-radius:8px; border:1px solid rgba(255,255,255,0.04); color:#e6eefc; padding:8px;}
    .floating-chat button{background:var(--cyan); color:#001018; border-radius:8px; border:none; padding:8px 12px; font-weight:700; cursor:pointer;}
    /* sections area */
    .section-wrap{width:100%; max-width:1200px; margin:40px auto 80px; padding:0 12px;}
    .two-col{display:flex; gap:28px; align-items:flex-start;}
    .left-col{width:320px;}
    .right-col{flex:1;}
    .card{background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); padding:14px; border-radius:12px; margin-bottom:12px; border:1px solid rgba(255,255,255,0.02);}
    .section{padding:40px 0;}
    .section h2{font-size:28px; color:var(--violet); margin-bottom:12px;}
    .skill-chip{display:inline-block;margin:6px 6px 0 0;padding:8px 10px;border-radius:8px;background:rgba(255,255,255,0.03); color:#fff;}
    .photo-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-top:8px}
    .photo-grid img{width:100%;height:160px;object-fit:cover;border-radius:10px;box-shadow:0 10px 30px rgba(2,6,23,0.4);transition:transform .25s ease}
    .photo-grid img:hover{transform:translateY(-6px) scale(1.02)}
    @media (max-width:980px){
      .hero-title{font-size:36px;}
      .floating-chat{display:none;}
      .two-col{flex-direction:column;}
      .left-col{width:100%;}
      .glass-nav{left:12px; transform:none;}
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

    <div id="home" class="hero-wrap">
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
          <div style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:8px">Anonymous messages appear in admin.</div>
        </div>
      </div>
    </div>

    <script>
      // tsparticles init
      if (window.tsParticles) {
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
        const script = document.createElement('script');
        script.src = "https://cdn.jsdelivr.net/npm/tsparticles@2.3.4/tsparticles.bundle.min.js";
        script.onload = function(){ tsParticles.load("tsparticles", { fullScreen: { enable:false }, particles: { number:{ value:28}, color:{ value:["#ff6ad1","#8b8bff","#00d4ff"] }, shape:{ type:"circle"}, opacity:{ value:0.65 }, size:{ value:{ min:2, max:6}}, move:{ enable:true, speed:0.6, outModes:"out"}}); };
        document.head.appendChild(script);
      }

      document.addEventListener('DOMContentLoaded', function(){
        var btn = document.getElementById('floating_send');
        if(btn){
          btn.addEventListener('click', function(){
            const v = document.getElementById('floating_input').value;
            if(!v || !v.trim()){ alert('Write a question'); return; }
            const params = new URLSearchParams();
            params.set('anon_q', v);
            window.open(window.location.pathname + "?" + params.toString(), "_self");
          });
        }
      });
    </script>
    """
    # safe replacement of placeholders
    html = html.replace("__HERO_NAME__", HERO_NAME).replace("__HERO_ROLE__", HERO_ROLE)
    # render via components
    components.html(html, height=780, scrolling=False)

# ----------------------------
# Sections (About / Skills / Projects / Experience / Photos / Blog / Writings / Contact)
# ----------------------------
def render_sections_and_content():
    st.markdown('<div class="section-wrap">', unsafe_allow_html=True)

    # two-column area: left = writings/admin, right = main tabs
    col_left, col_right = st.columns([1, 2.2], gap="large")

    with col_left:
        # Writings (anonymous)
        st.markdown('<div id="writings"><h3 style="color:#fff;margin-bottom:6px">Writings (anonymous)</h3></div>', unsafe_allow_html=True)
        msgs = load_messages()
        if not msgs:
            st.markdown("<div class='card'>No writings yet. Visitors can add messages below.</div>", unsafe_allow_html=True)
        else:
            for m in sorted(msgs, key=lambda x: x.get("id", 0), reverse=True)[:8]:
                txt = m.get("text", "")
                ts = m.get("timestamp", "")
                st.markdown(f"<div class='card'><div style='font-weight:600'>{txt[:150]}{'...' if len(txt)>150 else ''}</div><div style='color:rgba(255,255,255,0.6);margin-top:6px;font-size:12px'>{ts}</div></div>", unsafe_allow_html=True)

        # anonymous message box
        st.markdown('<div id="anon_box" style="margin-top:12px"><h4 style="color:#fff">Send anonymous message</h4></div>', unsafe_allow_html=True)
        with st.form("anon_main", clear_on_submit=True):
            text = st.text_area("Your message", max_chars=1500, placeholder="Share a thought...")
            sent = st.form_submit_button("Send anonymously")
        if sent:
            if not text or not text.strip():
                st.warning("Please write a message.")
            else:
                save_message(text.strip())
                st.success("Message saved. Thank you!")

        # Admin panel
        st.markdown('<div id="admin" style="margin-top:12px"><h4 style="color:#fff">Admin</h4></div>', unsafe_allow_html=True)
        qp = st.experimental_get_query_params()
        if ADMIN_QUERY_PARAM in qp and qp.get(ADMIN_QUERY_PARAM, [""])[0] == ADMIN_TOKEN:
            st.session_state._admin_unlocked = True
        if st.session_state.get("_admin_unlocked", False):
            st.success("Admin unlocked")
            messages = load_messages()
            st.markdown(f"<div style='color:rgba(255,255,255,0.6)'>Total messages: {len(messages)}</div>", unsafe_allow_html=True)
            for m in sorted(messages, key=lambda x: x.get("id", 0), reverse=True):
                with st.expander(f"ID {m.get('id')} • {m.get('timestamp')}"):
                    st.write(m.get("text"))
                    if st.button("Delete", key=f"del_{m.get('id')}"):
                        new = [x for x in messages if x.get("id") != m.get("id")]
                        overwrite_messages(new)
                        st.success("Deleted")
                        st.experimental_rerun()
            if st.button("Clear all messages", key="clear_all"):
                overwrite_messages([])
                st.success("Cleared")
                st.experimental_rerun()
        else:
            token = st.text_input("Enter admin token", type="password", key="adm_token_left")
            if st.button("Unlock admin", key="unlock_btn_left"):
                if token.strip() == ADMIN_TOKEN:
                    st.session_state._admin_unlocked = True
                    st.experimental_set_query_params(**{ADMIN_QUERY_PARAM: ADMIN_TOKEN})
                    st.experimental_rerun()
                else:
                    st.error("Invalid token")

    with col_right:
        # Tabs: Chatbot, Blog, Photos
        tabs = st.tabs(["Chatbot", "Blog", "Photos"])
        with tabs[0]:
            st.markdown('<div id="chat" style="margin-bottom:8px"><h3 style="color:#fff">Chatbot</h3></div>', unsafe_allow_html=True)
            # small chatbot implementation
            qbank = {
                "what is your name": f"My name is {HERO_NAME}.",
                "where are you from": "I'm from India.",
                "what do you do": "I build websites, write, and learn."
            }
            if "chat_messages" not in st.session_state:
                st.session_state.chat_messages = []
            for m in st.session_state.chat_messages[-8:]:
                if m["role"] == "user":
                    st.markdown(f"<div style='background:#0f1724;padding:10px;border-radius:8px;margin-bottom:8px;color:#cfe8ff'>{m['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='background:#f7f6ff;color:#0b0f14;padding:10px;border-radius:8px;margin-bottom:8px'>{m['content']}</div>", unsafe_allow_html=True)
            q = st.text_input("Ask a question...", key="chat_input_main")
            if q:
                st.session_state.chat_messages.append({"role":"user","content":q})
                a = qbank.get(q.lower(), "Sorry! I don't have an answer for that.")
                st.session_state.chat_messages.append({"role":"bot","content":a})
                st.experimental_rerun()

        with tabs[1]:
            st.markdown('<div id="blog" style="margin-bottom:8px"><h3 style="color:#fff">Blog</h3></div>', unsafe_allow_html=True)
            posts = get_all_posts()
            if not posts:
                st.info("No blog posts found — add markdown files in blog_posts/")
            else:
                for p in posts:
                    st.markdown(f"<div style='padding:12px;border-radius:8px;background:rgba(255,255,255,0.02);margin-bottom:10px'><div style='font-weight:700'>{p['title']}</div><div style='color:rgba(255,255,255,0.6)'>{p['date']}</div><p style='margin-top:8px'>{p['summary']}</p></div>", unsafe_allow_html=True)
                    if st.button("Read", key=f"read_{p['slug']}"):
                        st.session_state.selected_post = p['slug']
                        st.experimental_rerun()
                if st.session_state.get("selected_post"):
                    slug = st.session_state.get("selected_post")
                    post = get_post_data(slug)
                    if post:
                        st.markdown("<hr>", unsafe_allow_html=True)
                        st.markdown(f"<h3 style='color: #8b8bff'>{post['title']}</h3>", unsafe_allow_html=True)
                        st.markdown(post['html'], unsafe_allow_html=True)
                        if st.button("Back to list"):
                            st.session_state.selected_post = None
                            st.experimental_rerun()

        with tabs[2]:
            st.markdown('<div id="photos" style="margin-bottom:8px"><h3 style="color:#fff">Photos</h3></div>', unsafe_allow_html=True)
            images = get_gallery_images()
            if not images:
                st.info("No images found in the project root. Upload JPG/PNG files to show a gallery.")
            else:
                grid_css = """
                <style>
                .photo-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-top:8px}
                .photo-grid img{width:100%;height:180px;object-fit:cover;border-radius:10px;box-shadow:0 10px 30px rgba(2,6,23,0.4);transition:transform .25s ease}
                .photo-grid img:hover{transform:translateY(-6px) scale(1.02)}
                </style>
                """
                imgs_html = "".join([f"<img src='{img}' alt='{img}' />" for img in images])
                st.markdown(grid_css + f"<div class='photo-grid'>{imgs_html}</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close section-wrap

    # Below: full-width sections (About, Skills, Projects, Experience, Contact)
    st.markdown('<div style="max-width:1200px;margin:20px auto 120px;padding:0 12px">', unsafe_allow_html=True)

    # About
    st.markdown('<div id="about" class="section">', unsafe_allow_html=True)
    st.markdown('<h2>About</h2>', unsafe_allow_html=True)
    about_text = f"<p style='color:#0f1724'>Hi — I am <strong>{HERO_NAME}</strong>. {HERO_ROLE}. This page shows projects, photos, blog posts and a chatbot. Built clean and modern.</p>"
    st.markdown(f"<div class='card'>{about_text}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Skills
    st.markdown('<div id="skills" class="section">', unsafe_allow_html=True)
    st.markdown('<h2>Skills</h2>', unsafe_allow_html=True)
    skills = ["Python", "Streamlit", "Web Dev", "HTML/CSS", "JavaScript", "Git", "Data Analysis", "AI/ML"]
    chips = "".join([f"<span class='skill-chip'>{s}</span>" for s in skills])
    st.markdown(f"<div class='card'>{chips}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Projects
    st.markdown('<div id="projects" class="section">', unsafe_allow_html=True)
    st.markdown('<h2>Projects</h2>', unsafe_allow_html=True)
    st.markdown("<div class='card'><strong>Chatbot & Portfolio</strong><div class='muted'>Streamlit-based personal site with blog, photos and anonymous message box.</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='card'><strong>Other Projects</strong><div class='muted'>Add project cards here.</div></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Experience
    st.markdown('<div id="experience" class="section">', unsafe_allow_html=True)
    st.markdown('<h2>Experience</h2>', unsafe_allow_html=True)
    st.markdown("<div class='card'>Working on personal and open-source projects, learning systems and AI.</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Contact
    st.markdown('<div id="contact" class="section">', unsafe_allow_html=True)
    st.markdown('<h2>Contact</h2>', unsafe_allow_html=True)
    contact_html = "<p style='color:#0f1724'>Email: aryanxsharma26@gmail.com • Instagram: @aryanxsharma26</p>"
    st.markdown(f"<div class='card'>{contact_html}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# Main function: assemble everything
# ----------------------------
def main():
    # check for anon_q param (floating widget uses query param to submit)
    qp = st.experimental_get_query_params()
    if "anon_q" in qp:
        q = qp.get("anon_q", [""])[0]
        if q and q.strip():
            save_message(q.strip())
            st.experimental_set_query_params()  # clear params
            st.success("Your anonymous message was saved. Thank you!")

    render_hero_and_navbar()
    render_sections_and_content()
    # footer spacing
    st.markdown("<div style='height:120px'></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
