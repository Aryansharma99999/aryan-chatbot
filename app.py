# app.py - SmarthSood-style portfolio replicated in Streamlit (top-to-bottom)
# Features:
# - Sticky top navigation (Home / About / Skills / Projects / Experience / Contact)
# - Fullscreen hero with gradient + particles
# - Smooth modular sections (About, Skills, Projects, Experience, Contact)
# - Floating chatbot card (right) that sends anonymous messages to admin storage
# - Photos grid, Blog, Writings (anonymous), Admin
# - Telegram notification (optional via TELEGRAM_BOT_TOKEN env variable)
# - Mobile responsive
# Usage: put images (jpg/png) in repo root for Photos, blog posts in blog_posts/
import os, re, time, json, requests
from datetime import datetime
from markdown import markdown
import streamlit as st
import streamlit.components.v1 as components

# ----------------------------
# Basic config
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
    # Telegram best-effort
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
    out=[]
    with open(MSG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            try: out.append(json.loads(line))
            except: continue
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
                k,v = line.split(":",1)
                md_meta[k.strip()] = v.strip()
        body = content[m.end():].strip()
    html = markdown(body)
    return {"slug": slug, "title": md_meta.get("title","Untitled"), "date": md_meta.get("date","N/A"), "author": md_meta.get("author","N/A"), "summary": md_meta.get("summary",""), "html": html}

def get_all_posts():
    if not os.path.exists(POSTS_DIR):
        return []
    fs = [f for f in os.listdir(POSTS_DIR) if f.endswith(".md")]
    posts=[]
    for f in fs:
        slug = f.replace(".md","")
        p = get_post_data(slug)
        if p: posts.append(p)
    return posts

# ----------------------------
# Gallery helper
# ----------------------------
def get_gallery_images():
    files = [f for f in os.listdir(BASE_DIR) if f.lower().endswith((".jpg",".jpeg",".png",".webp"))]
    return files

# ----------------------------
# Render top hero (full screen) with particles & navbar
# ----------------------------
def render_top_hero():
    css = r"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    :root{
      --grad1:#ff77e9; --grad2:#8a6aff; --carddark:#1b141a;
      --neon-pink:#ff53d6; --neon-blue:#8b8bff; --cyan:#00d4ff;
    }
    html,body,.stApp{height:100%; margin:0; font-family:Inter,system-ui, -apple-system, 'Segoe UI', Roboto;}
    body{background:linear-gradient(135deg,var(--grad1) 0%, var(--grad2) 100%);}
    /* sticky top nav */
    .top-nav{position:sticky; top:10px; z-index:9999; display:flex; justify-content:center;}
    .nav-bar{width:100%; max-width:1200px; display:flex; align-items:center; justify-content:space-between; padding:12px 18px; background:transparent;}
    .nav-left{display:flex; align-items:center; gap:12px;}
    .site-brand{font-weight:800; color:#ffffff; letter-spacing:0.2px}
    .nav-links{display:flex; gap:14px; align-items:center;}
    .nav-links a{color:rgba(255,255,255,0.9); text-decoration:none; padding:8px 12px; border-radius:8px; font-weight:600;}
    .nav-links a:hover{background:rgba(255,255,255,0.04);}
    /* hero */
    .hero-viewport{display:flex; align-items:center; justify-content:center; min-height:92vh; padding:28px 12px 6px 12px;}
    .hero-card{width:min(1240px,96%); background:linear-gradient(180deg, rgba(4,3,5,0.98), rgba(10,6,10,0.98)); border-radius:36px; padding:64px; position:relative; box-shadow:0 30px 80px rgba(0,0,0,0.45);}
    #tsparticles{ position:absolute; inset:0; z-index:0; border-radius:36px; }
    .hero-inner{position:relative; z-index:2; text-align:center; color:#fff;}
    .hero-title{font-size:58px; font-weight:800; color:var(--neon-pink); margin:0;}
    .hero-role{font-size:18px; font-weight:700; color:var(--neon-blue); margin:8px 0 18px 0;}
    .hero-desc{max-width:920px;margin:0 auto 26px; color:rgba(255,255,255,0.9); line-height:1.6;}
    .cta-row{display:flex; gap:12px; justify-content:center; margin-bottom:20px;}
    .btn-primary{background:linear-gradient(90deg,var(--neon-pink),var(--neon-blue)); color:white; padding:12px 20px; border-radius:28px; font-weight:800; text-decoration:none;}
    .btn-ghost{background:transparent; color:var(--neon-blue); padding:10px 18px; border-radius:28px; border:2px solid rgba(139,139,255,0.12); font-weight:700; text-decoration:none;}
    .social-row{display:flex; gap:12px; justify-content:center; margin-top:10px;}
    .social-btn{width:48px;height:48px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.03); color:#dbe8ff; text-decoration:none; font-weight:700;}
    /* floating chat */
    .floating-chat{position:absolute; right:-44px; top:200px; width:360px; background: linear-gradient(180deg,#0f1114,#17171a); border-radius:18px; padding:14px; box-shadow: 0 24px 60px rgba(8,8,20,0.7); border:1px solid rgba(255,255,255,0.04); z-index:3;}
    .floating-chat h4{ color:var(--cyan); margin:6px 0 8px 0; font-weight:800; font-size:18px;}
    .floating-chat .bubble{background:rgba(255,255,255,0.04); padding:10px;border-radius:8px;color:#dbe8ff; margin-bottom:8px;}
    .floating-chat .input-row{display:flex; gap:8px; margin-top:8px;}
    .floating-chat input{flex:1; background:#0f1114; border-radius:8px; border:1px solid rgba(255,255,255,0.04); color:#e6eefc; padding:8px;}
    .floating-chat button{background:var(--cyan); color:#001018; border-radius:8px; border:none; padding:8px 12px; font-weight:700; cursor:pointer;}
    /* two-column section container */
    .section-wrap{width:100%; max-width:1200px; margin:40px auto 80px; padding:0 12px;}
    .two-col{display:flex; gap:28px; align-items:flex-start;}
    .left-col{width:320px;}
    .right-col{flex:1;}
    .card{background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); padding:14px; border-radius:12px; margin-bottom:12px; border:1px solid rgba(255,255,255,0.02);}
    /* About/Skills/Projects sections */
    .section { padding:40px 0; }
    .section h2 { font-size:28px; color:var(--neon-blue); margin-bottom:12px; }
    .skills-grid { display:flex; gap:8px; flex-wrap:wrap; }
    .skill-chip { padding:10px 12px; border-radius:10px; background:rgba(255,255,255,0.03); color:#fff; }
    /* gallery grid */
    .photo-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-top:8px}
    .photo-grid img{width:100%;height:160px;object-fit:cover;border-radius:10px;box-shadow:0 10px 30px rgba(2,6,23,0.4);transition:transform .25s ease}
    .photo-grid img:hover{transform:translateY(-6px) scale(1.02)}
    /* responsive */
    @media (max-width:980px){
      .hero-title{font-size:34px;}
      .floating-chat{display:none;}
      .two-col{flex-direction:column;}
      .left-col{width:100%;}
    }
    </style>
    """

    hero_html = f"""
    {css}
    <script src="https://cdn.jsdelivr.net/npm/tsparticles@2.3.4/tsparticles.bundle.min.js"></script>
    <div class="top-nav">
      <div class="nav-bar">
        <div class="nav-left">
          <div class="site-brand">Aryan</div>
        </div>
        <div class="nav-links">
          <a href="#home">Home</a>
          <a href="#about">About</a>
          <a href="#skills">Skills</a>
          <a href="#projects">Projects</a>
          <a href="#experience">Experience</a>
          <a href="#contact">Contact</a>
        </div>
      </div>
    </div>

    <div id="home" class="hero-viewport">
      <div class="hero-card" id="hero-card">
        <div id="tsparticles"></div>
        <div class="hero-inner">
          <h1 class="hero-title">{HERO_NAME}</h1>
          <div class="hero-role">{HERO_ROLE}</div>
          <div class="hero-desc">Welcome — explore my projects, view photos, read my blog, or ask me anything using the chat widget.</div>
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
          <div style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:8px">Anonymous messages will appear in admin.</div>
        </div>
      </div>
    </div>

    <script>
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

      document.getElementById('floating_send').addEventListener('click', function(){
        const v = document.getElementById('floating_input').value;
        if(!v || !v.trim()){ alert('Write a question'); return; }
        const params = new URLSearchParams();
        params.set('anon_q', v);
        window.open(window.location.pathname + "?" + params.toString(), "_self");
      });
    </script>
    """
    components.html(hero_html, height=780, scrolling=False)

# ----------------------------
# Sections: About / Skills / Projects / Experience / Contact
# ----------------------------
def render_sections():
    # wrapper and anchor-friendly markup
    st.markdown('<div class="section-wrap">', unsafe_allow_html=True)

    # ABOUT
    st.markdown('<div id="about" class="section">', unsafe_allow_html=True)
    st.markdown('<h2>About Me</h2>', unsafe_allow_html=True)
    about_html = f"<p style='max-width:900px;color:rgba(0,0,0,0.8)'>Hi — I am <strong>{HERO_NAME}</strong>. {HERO_ROLE}. This site showcases projects, writings, photos and an AI chatbot to interact with me. Built with simplicity and polish.</p>"
    st.markdown(f"<div class='card'>{about_html}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # SKILLS
    st.markdown('<div id="skills" class="section">', unsafe_allow_html=True)
    st.markdown('<h2>Skills</h2>', unsafe_allow_html=True)
    skills = ["Python","Streamlit","Web Development","HTML/CSS","JavaScript","Git","Data Analysis","AI/ML"]
    chips = " ".join([f"<span class='skill-chip' style='display:inline-block;margin:6px 6px 0 0;padding:8px 10px;border-radius:8px;background:rgba(0,0,0,0.05);'>{s}</span>" for s in skills])
    st.markdown(f"<div class='card'><div style='max-width:900px'>{chips}</div></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # PROJECTS
    st.markdown('<div id="projects" class="section">', unsafe_allow_html=True)
    st.markdown('<h2>Projects</h2>', unsafe_allow_html=True)
    st.markdown("<div class='card'><strong>Chatbot Website</strong><div class='muted'>A Streamlit chatbot + blog + gallery</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='card'><strong>Portfolio Builder</strong><div class='muted'>Template-driven portfolio generator</div></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # EXPERIENCE
    st.markdown('<div id="experience" class="section">', unsafe_allow_html=True)
    st.markdown('<h2>Experience</h2>', unsafe_allow_html=True)
    st.markdown("<div class='card'>Working on personal projects and learning AI/ML. Internships and competitions details can be listed here.</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # CONTACT
    st.markdown('<div id="contact" class="section">', unsafe_allow_html=True)
    st.markdown('<h2>Contact</h2>', unsafe_allow_html=True)
    contact_html = "<p style='max-width:900px;color:rgba(0,0,0,0.8)'>Email: aryanxsharma26@gmail.com | Instagram: @aryanxsharma26</p>"
    st.markdown(f"<div class='card'>{contact_html}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# Right column: Chat / Blog / Photos
# ----------------------------
def render_chat_area():
    st.markdown("<div style='margin-bottom:8px'><strong>Chatbot</strong></div>", unsafe_allow_html=True)
    qbank = {
        "what is your name": f"My name is {HERO_NAME}.",
        "where are you from": "I'm from India.",
        "what do you do": "I make things with code and words."
    }
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages=[]
    for m in st.session_state.chat_messages[-8:]:
        if m["role"]=="user":
            st.markdown(f"<div style='background:#0f1724;padding:10px;border-radius:8px;margin-bottom:8px;color:#cfe8ff'>{m['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background:#f7f6ff;color:#0b0f14;padding:10px;border-radius:8px;margin-bottom:8px'>{m['content']}</div>", unsafe_allow_html=True)
    q = st.text_input("Ask me a question...", key="chat_input_area")
    if q:
        st.session_state.chat_messages.append({"role":"user","content":q})
        a = qbank.get(q.lower(), "Sorry! I don't have an answer for that.")
        st.session_state.chat_messages.append({"role":"bot","content":a})
        st.experimental_rerun()

def render_blog_area():
    st.markdown("<div style='margin-bottom:8px'><strong>Blog</strong></div>", unsafe_allow_html=True)
    posts = get_all_posts()
    if not posts:
        st.info("No blog posts found — add markdown files in blog_posts/")
        return
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

def render_photos_grid():
    st.markdown("<div style='margin-bottom:8px'><strong>Photos</strong></div>", unsafe_allow_html=True)
    images = get_gallery_images()
    if not images:
        st.info("No images found in the project root.")
        return
    grid_css = """
    <style>
    .photo-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-top:8px}
    .photo-grid img{width:100%;height:160px;object-fit:cover;border-radius:10px;box-shadow:0 10px 30px rgba(2,6,23,0.4);transition:transform .25s ease}
    .photo-grid img:hover{transform:translateY(-6px) scale(1.02)}
    </style>
    """
    imgs_html = "".join([f"<img src='{img}' alt='{img}' />" for img in images])
    st.markdown(grid_css + f"<div class='photo-grid'>{imgs_html}</div>", unsafe_allow_html=True)

# ----------------------------
# Left column: Writings + Anonymous form + Admin
# ----------------------------
def render_left_column():
    st.markdown("<div style='margin-bottom:8px'><strong>Writings (anonymous)</strong></div>", unsafe_allow_html=True)
    msgs = load_messages()
    if not msgs:
        st.markdown("<div style='padding:12px;border-radius:8px;background:rgba(255,255,255,0.02)'>No writings yet — visitors can add messages below.</div>", unsafe_allow_html=True)
    else:
        for m in sorted(msgs, key=lambda x: x.get("id",0), reverse=True)[:8]:
            txt = m.get("text","")
            ts = m.get("timestamp","")
            st.markdown(f"<div style='padding:10px;border-radius:8px;background:rgba(255,255,255,0.02);margin-bottom:8px'><div style='font-weight:600'>{txt[:150]}{'...' if len(txt)>150 else ''}</div><div style='color:rgba(255,255,255,0.6);margin-top:6px;font-size:12px'>{ts}</div></div>", unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    with st.form("anon_form_main", clear_on_submit=True):
        text = st.text_area("Your message", max_chars=1500, placeholder="Share a thought, feedback, or a question...")
        submitted = st.form_submit_button("Send anonymously")
    if submitted:
        if not text or not text.strip():
            st.warning("Please write a message.")
        else:
            save_message(text.strip())
            st.success("Message saved. Thank you!")
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom:8px'><strong>Admin</strong></div>", unsafe_allow_html=True)
    qp = st.experimental_get_query_params()
    if ADMIN_QUERY_PARAM in qp and qp.get(ADMIN_QUERY_PARAM, [""])[0] == ADMIN_TOKEN:
        st.session_state._admin_unlocked = True
    if st.session_state.get("_admin_unlocked", False):
        st.success("Admin unlocked")
        messages = load_messages()
        st.markdown(f"<div style='color:rgba(255,255,255,0.6)'>Total messages: {len(messages)}</div>", unsafe_allow_html=True)
        for m in sorted(messages, key=lambda x: x.get("id",0), reverse=True):
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
        token = st.text_input("Enter admin token", type="password", key="adm_token_main")
        if st.button("Unlock admin", key="unlock_btn_main"):
            if token.strip() == ADMIN_TOKEN:
                st.session_state._admin_unlocked = True
                st.experimental_set_query_params(**{ADMIN_QUERY_PARAM: ADMIN_TOKEN})
                st.experimental_rerun()
            else:
                st.error("Invalid token")

# ----------------------------
# Main assembly
# ----------------------------
def main():
    # handle floating chat sending via query param
    qp = st.experimental_get_query_params()
    if "anon_q" in qp:
        q = qp.get("anon_q", [""])[0]
        if q and q.strip():
            save_message(q.strip())
            st.experimental_set_query_params()
            st.success("Your anonymous message was saved. Thank you!")

    # hero + navbar
    render_top_hero()

    # sections container
    st.markdown("<div class='section-wrap'>", unsafe_allow_html=True)

    # two-column area with left writings/admin and right explore tabs
    col1, col2 = st.columns([1,2.2], gap="large")
    with col1:
        render_left_column()
    with col2:
        tabs = st.tabs(["Chatbot","Blog","Photos"])
        with tabs[0]:
            render_chat_area()
        with tabs[1]:
            render_blog_area()
        with tabs[2]:
            render_photos_grid()

    st.markdown("</div>", unsafe_allow_html=True)

    # full-width About/Skills/Projects/Experience/Contact below (like original)
    render_sections()

    # footer spacing
    st.markdown("<div style='height:100px'></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
