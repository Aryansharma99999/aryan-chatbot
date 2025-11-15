# app.py
import os
import re
import time
import streamlit as st
from markdown import markdown
import streamlit.components.v1 as components

st.set_page_config(page_title="Aryan Sharma", layout="wide", initial_sidebar_state="collapsed")

# ---------- Helper: BLOG & GALLERY ----------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
GALLERY_DIR = os.path.join(BASE_DIR, "gallery")
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")

def get_gallery_images():
    if not os.path.exists(GALLERY_DIR):
        return []
    files = [f for f in os.listdir(GALLERY_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
    files.sort()
    return [os.path.join("gallery", f) for f in files]

def get_post_data(slug):
    file_path = os.path.join(POSTS_DIR, f"{slug}.md")
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as fh:
        content = fh.read()
    meta = {}
    body = content
    meta_match = re.match(r'---\n(.*?)\n---', content, re.DOTALL)
    if meta_match:
        meta_block = meta_match.group(1)
        for line in meta_block.splitlines():
            if ':' in line:
                k,v = line.split(':',1)
                meta[k.strip()] = v.strip()
        body = content[meta_match.end():].strip()
    html = markdown(body)
    return {
        "slug": slug,
        "title": meta.get("title", slug.replace('-', ' ').capitalize()),
        "date": meta.get("date", ""),
        "author": meta.get("author", ""),
        "summary": meta.get("summary", ""),
        "html": html,
    }

def get_all_posts():
    if not os.path.exists(POSTS_DIR):
        return []
    md_files = [f for f in os.listdir(POSTS_DIR) if f.endswith(".md")]
    posts = []
    for m in md_files:
        slug = m[:-3]
        data = get_post_data(slug)
        if data:
            posts.append(data)
    return posts

# ---------- Top in-page hero + animation (rendered via components.html) ----------
# We use components.html so JS animations run reliably.
hero_html = """
<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap" rel="stylesheet">
<style>
  :root{
    --bg1:#ff6fb5; /* pink */
    --bg2:#845ef7; /* purple */
    --bg3:#7ad3ff; /* blue */
  }
  html,body{height:100%;margin:0;padding:0;font-family:'Poppins',sans-serif;overflow-x:hidden;}
  body{
    background: linear-gradient(135deg, rgba(255,111,181,0.95) 0%, rgba(132,94,247,0.95) 50%, rgba(122,211,255,0.95) 100%);
    min-height:100vh;
    display:flex;
    align-items:center;
    justify-content:center;
  }
  /* starfield (small dots) */
  #stars {
    position:fixed; inset:0; z-index:0; pointer-events:none;
    background-image:
      radial-gradient(#fff 1px, transparent 1px);
    background-size: 6px 6px;
    opacity: .18;
    animation: twinkle 6s linear infinite;
  }
  @keyframes twinkle{
    0%{opacity:.18}
    50%{opacity:.12}
    100%{opacity:.18}
  }

  /* hero */
  .hero-wrap{
    width:86%;
    max-width:1100px;
    margin:30px auto;
    z-index:2;
    position:relative;
    border-radius:24px;
    padding:64px 64px 80px 64px;
    box-sizing:border-box;
    backdrop-filter: blur(8px) saturate(120%);
    -webkit-backdrop-filter: blur(8px) saturate(120%);
    background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));
    box-shadow: 0 20px 50px rgba(10,10,20,0.5), inset 0 1px 0 rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.04);
    overflow:hidden;
  }

  .neon-outline{
    position:absolute; inset:10px; border-radius:20px;
    pointer-events:none;
    box-shadow: 0 0 0 2px rgba(130,90,240,0.12), 0 0 30px rgba(130,90,240,0.08) inset;
    border: 3px solid rgba(130,90,240,0.12);
  }

  .hero-title{
    margin:0; font-size:48px; font-weight:800;
    text-align:center;
    background:linear-gradient(90deg,var(--bg1),var(--bg2));
    -webkit-background-clip:text; background-clip:text; color:transparent;
  }
  .hero-sub{
    text-align:center; color: #e6f0ff; font-size:18px; opacity:.95; margin-top:10px;
  }
  .typewrap{ text-align:center; margin-top:14px; color:#cde8ff; font-weight:600;}
  .roles { color:#ffd3f0; font-weight:700; font-size:18px; height:26px; display:inline-block; margin-left:6px; }

  /* Buttons row */
  .cta-row{ display:flex; gap:14px; justify-content:center; margin-top:28px; }
  .btn {
    padding:12px 20px; border-radius:999px; border:none; cursor:pointer;
    font-weight:700; font-size:15px;
    background:linear-gradient(90deg,var(--bg1),var(--bg2));
    color:#041622; box-shadow: 0 6px 18px rgba(0,0,0,0.25);
  }
  .btn-outline {
    padding:12px 20px; border-radius:999px; border:1px solid rgba(255,255,255,0.08);
    background:transparent; color:#d7d7ff; font-weight:700;
  }

  /* floating icons - bottom left vertical */
  .float-left {
    position:fixed; left:18px; bottom:26%;
    display:flex; flex-direction:column; gap:18px; z-index:6;
  }
  .float-btn {
    width:56px; height:56px; border-radius:999px; display:flex; align-items:center; justify-content:center;
    background:linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
    border:2px solid rgba(255,255,255,0.06);
    box-shadow: 0 8px 30px rgba(12,10,20,0.5);
    cursor:pointer;
    transition: transform .18s ease, box-shadow .18s ease;
    color:#fff; font-size:22px;
  }
  .float-btn:hover{ transform: translateY(-6px); box-shadow: 0 18px 40px rgba(10,10,20,0.6); }

  /* chatbot floating bottom right (static look) */
  .chat-float {
    position:fixed; right:26px; bottom:26px; z-index:7;
    background:linear-gradient(180deg, rgba(14,16,20,0.95), rgba(26,28,32,0.92));
    width:380px; max-width:92vw; border-radius:14px; padding:18px;
    box-shadow: 0 20px 60px rgba(10,10,20,0.6);
    color:#fff;
  }
  .chat-title{ color:#5fe4ff; font-weight:800; margin-bottom:8px; }
  .chat-input{ width:100%; padding:10px 12px; border-radius:8px; border:none; background:#111216; color:#ddd; }

  /* responsive */
  @media (max-width:800px){
    .hero-wrap{ padding:36px 22px; width:92%;}
    .hero-title{ font-size:32px;}
    .float-left{ left:10px; bottom:18%;}
    .chat-float{ width:320px; right:12px; bottom:12px;}
  }
</style>
</head>
<body>
  <div id="stars"></div>

  <div class="hero-wrap" id="hero">
    <div class="neon-outline"></div>
    <h1 class="hero-title">Aryan Sharma</h1>
    <div class="hero-sub">Welcome to my personal website! <span id="blink">|</span></div>

    <div class="typewrap">I'm a <span class="roles" id="role"></span></div>

    <div class="cta-row">
      <button class="btn" onclick="location.href='#projects'">Download Resume</button>
      <button class="btn-outline" onclick="location.href='#contact'">Get In Touch</button>
    </div>
  </div>

  <!-- floating icons left -->
  <div class="float-left" aria-hidden="true">
    <div class="float-btn" title="Gallery" onclick="document.getElementById('gallery-section').scrollIntoView({behavior:'smooth'})">📷</div>
    <div class="float-btn" title="Anonymous" onclick="document.getElementById('writings-section').scrollIntoView({behavior:'smooth'})">📝</div>
    <div class="float-btn" title="Writings" onclick="document.getElementById('blog-section').scrollIntoView({behavior:'smooth'})">✍️</div>
  </div>

  <!-- small JS: particles (tiny stars) and typewriter cycle -->
  <script>
    // Typewriter-like cycle (erase + replace)
    const roles = ["web developer","learner","tech enthusiast","programmer","writer","video editor"];
    let idx = 0, pos = 0, forward = true;
    const roleEl = document.getElementById('role');
    const blink = document.getElementById('blink');
    function tick() {
      const current = roles[idx];
      if (forward) {
        pos++;
        roleEl.textContent = current.slice(0,pos);
        if (pos === current.length) { forward = false; setTimeout(tick, 900); return; }
      } else {
        pos--;
        roleEl.textContent = current.slice(0,pos);
        if (pos === 0) { forward = true; idx = (idx+1)%roles.length; setTimeout(tick, 400); return; }
      }
      setTimeout(tick, 70);
    }
    tick();
    // blink cursor
    setInterval(()=>{ blink.style.visibility = (blink.style.visibility==='hidden'?'visible':'hidden') },600);

    // Simple particle effect (CSS background handles tiny dots and twinkle)
    // For little extra drifting, we'll animate via JS small translate on the hero overlay (subtle)
    const hero = document.querySelector('.hero-wrap');
    let t=0;
    function floatHero(){
      t+=0.002;
      const dx = Math.sin(t*1.2)*6;
      const dy = Math.cos(t)*6;
      hero.style.transform = `translate(${dx}px, ${dy}px)`;
      requestAnimationFrame(floatHero);
    }
    floatHero();
  </script>

</body>
</html>
"""

# -------------- Render the hero HTML (components) -------------
components.html(hero_html, height=520, scrolling=False)

# ---------- Streamlit content area below (sections auto-load) ----------
st.markdown("---")
col1, col2 = st.columns([1,2])

# Left column: Gallery preview (floating icons in component scroll to these)
with col1:
    st.markdown("### 📸 Photos (Gallery)")
    images = get_gallery_images()
    if not images:
        st.info("No images found. Add files to the `gallery/` folder.")
    else:
        # small preview grid
        for i, img in enumerate(images):
            st.image(img, use_column_width=True, caption=os.path.basename(img))
            if i>=5: break
        if len(images) > 6:
            st.caption(f"Plus {len(images)-6} more — they'll appear here automatically.")

# Right column: Blog & Writings sections
with col2:
    st.markdown("### ✍️ Writings (anonymous)")
    # anonymous message box
    if "anon_messages" not in st.session_state:
        st.session_state.anon_messages = []
    with st.form("anon_form", clear_on_submit=True):
        msg = st.text_area("Share anonymously", placeholder="Write something anonymously...")
        submitted = st.form_submit_button("Send anonymously")
        if submitted and msg.strip():
            st.session_state.anon_messages.insert(0, {"msg": msg, "time": time.asctime()})
            st.success("Message sent anonymously — visible in admin (local session).")
    if st.session_state.anon_messages:
        for m in st.session_state.anon_messages[:8]:
            st.info(m["msg"])

    st.markdown("---")
    st.markdown("### 📰 Blog Posts")
    posts = get_all_posts()
    if not posts:
        st.info("No blog posts found. Add `.md` files to `blog_posts/`.")
    else:
        for p in posts:
            st.subheader(p["title"])
            st.caption(p.get("date",""))
            st.markdown(p["html"], unsafe_allow_html=True)
            st.markdown("---")

# ---------- Chatbot (simple front-end demo) ----------
st.markdown("<div id='chatbox_placeholder'></div>", unsafe_allow_html=True)
# Simple chat UI in the Streamlit area (works with session state)
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role":"system", "text":"Hi! Ask me about Aryan."}]
st.markdown("## 💬 Chat with Aryan's assistant (demo)")
for m in st.session_state.messages:
    if m["role"] == "system":
        st.markdown(f"**Assistant:** {m['text']}")
    else:
        st.markdown(f"**You:** {m['text']}")

user_q = st.text_input("Type your question...")
if st.button("Send"):
    if user_q.strip():
        st.session_state.messages.append({"role":"user","text":user_q})
        # A tiny rule-based demo reply:
        q = user_q.lower()
        reply = "Sorry, I don't have an answer for that yet."
        if "name" in q:
            reply = "My name is Aryan."
        elif "where" in q:
            reply = "I'm from India."
        elif "contact" in q or "email" in q:
            reply = "You can reach me on Instagram: @aryanxsharma26"
        st.session_state.messages.append({"role":"system","text":reply})
        st.experimental_rerun()

# ---------- Footer / Projects / Contact placeholders ----------
st.markdown("---")
st.markdown("<a id='projects'></a>", unsafe_allow_html=True)
st.header("Projects")
st.markdown("""
- Chatbot Website  
- Portfolio Builder  
- AI Experiments  
(Projects area — add more details to `app.py` or use markdown posts.)
""")

st.markdown("<a id='contact'></a>", unsafe_allow_html=True)
st.header("Contact")
st.write("Prefer DM on Instagram: ", "[aryanxsharma26](https://instagram.com/aryanxsharma26)")

# ---------- Admin / instructions (hidden by default) ----------
st.markdown("---")
st.markdown("### ⚙️ Notes & Setup")
st.markdown("""
- Put image files inside `gallery/` (jpg, png, webp). They will auto-appear in the Photos section.
- Put markdown files (`.md`) inside `blog_posts/` — these will be parsed and displayed under Blog Posts.
- This is a demo front-end; you can wire the chat to a backend or Telegram bot by updating the chat send handler.
- To change colors/feel, edit the CSS in the `hero_html` string at the top.
""")

