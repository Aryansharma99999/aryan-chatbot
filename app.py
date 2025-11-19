# -------------------------------------------------------------
#  ARYAN SHARMA • PREMIUM PORTFOLIO + CHATBOT • FULL CODE
#  Works on Streamlit — fully full-screen animated background
# -------------------------------------------------------------

import os
import re
import time
import streamlit as st
from markdown import markdown
import streamlit.components.v1 as components

st.set_page_config(page_title="Aryan Sharma", layout="wide")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
GALLERY_DIR = os.path.join(BASE_DIR, "gallery")
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")

# ---------------- Gallery ----------------
def get_gallery_images():
    if not os.path.exists(GALLERY_DIR):
        return []
    files = [f for f in os.listdir(GALLERY_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
    files.sort()
    return [os.path.join("gallery", f) for f in files]

# ---------------- Blog Posts ----------------
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
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = content[meta_match.end():].strip()

    html = markdown(body)
    return {
        "slug": slug,
        "title": meta.get("title", slug.replace("-", " ").title()),
        "date": meta.get("date", ""),
        "author": meta.get("author", ""),
        "html": html
    }

def get_all_posts():
    if not os.path.exists(POSTS_DIR):
        return []
    posts = []
    for f in os.listdir(POSTS_DIR):
        if f.endswith(".md"):
            data = get_post_data(f[:-3])
            if data: posts.append(data)
    return posts


# ---------------- Full Screen HTML Component ----------------
html_code = """
<style>

/* Global remove Streamlit padding */
html, body, .stApp {
    background: transparent !important;
    margin: 0 !important;
    padding: 0 !important;
    height: 100% !important;
    overflow-x: hidden !important;
}

.main, .block-container, [data-testid="block-container"] {
    padding: 0 !important;
    margin: 0 !important;
    background: transparent !important;
    max-width: 100% !important;
}

/* Full Screen Galaxy Background */
#bg {
  position: fixed;
  inset: 0;
  z-index: -1;
  background: radial-gradient(circle at top, #2a003b, #0a0115 70%);
  overflow: hidden;
}

.star {
  position: absolute;
  width: 2px;
  height: 2px;
  background: white;
  opacity: 0.7;
  border-radius: 50%;
  animation: twinkle 4s infinite ease-in-out alternate;
}
@keyframes twinkle {
  from { opacity: 0.2; }
  to   { opacity: 0.8; }
}

/* HERO BOX */
.hero {
  width: min(1100px, 93%);
  margin: 160px auto 100px auto;
  padding: 55px 50px;
  background: rgba(255,255,255,0.02);
  backdrop-filter: blur(18px) saturate(160%);
  border-radius: 22px;
  text-align: center;
  position: relative;
  box-shadow: 0 0 65px rgba(150, 60, 255, 0.20),
              inset 0 0 45px rgba(150, 60, 255, 0.12);
  color: white;
  overflow: hidden;
}

/* Neon Border Animation */
.hero::before {
  content: "";
  position: absolute;
  inset: -3px;
  border-radius: 24px;
  padding: 3px;
  background: linear-gradient(
      120deg,
      rgba(197,108,255,0.0),
      rgba(197,108,255,0.7),
      rgba(94,243,255,0.9),
      rgba(197,108,255,0.7),
      rgba(197,108,255,0.0)
  );
  background-size: 400% 400%;
  animation: borderFlow 6s linear infinite;
  -webkit-mask:
      linear-gradient(#fff 0 0) content-box,
      linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
          mask-composite: exclude;
}

@keyframes borderFlow {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* Buttons */
.btn {
  padding: 10px 22px;
  background: rgba(255,255,255,0.08);
  border-radius: 999px;
  color: white;
  margin: 6px;
  cursor: pointer;
  border: 1px solid rgba(255,255,255,0.15);
  transition: 0.2s;
}
.btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 0 18px rgba(150,60,255,0.55);
}

/* Chatbot Orb */
#chatOrb {
  position: fixed;
  right: 30px;
  bottom: 30px;
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: radial-gradient(circle, #e9a6ff, #7d1aff);
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  box-shadow: 0 0 25px rgba(170, 60, 255, .9);
  color: white;
  font-size: 30px;
  transition: 0.25s;
}
#chatOrb:hover {
  transform: scale(1.15);
}

</style>

<div id="bg"></div>

<script>
// Generate stars
const bg = document.getElementById("bg");
for (let i = 0; i < 250; i++) {
  const s = document.createElement("div");
  s.className = "star";
  s.style.top = Math.random()*100 + "%";
  s.style.left = Math.random()*100 + "%";
  s.style.animationDelay = (Math.random()*3)+"s";
  bg.appendChild(s);
}
</script>

<div class="hero">
    <h1 style="font-size:52px; font-weight:900;
      background:linear-gradient(90deg,#d36bff,#76e0ff);
      -webkit-background-clip:text;
      color:transparent;">
      ARYAN SHARMA
    </h1>

    <p style="font-size:18px; margin-top:10px; opacity:0.85;">
        Welcome to my personal website!
    </p>

    <h3 id="roleText" style="margin-top:8px; font-weight:700;"></h3>

    <div style="margin-top:25px;">
        <a href="/resume.pdf" class="btn">Download Resume</a>
        <a href="https://www.linkedin.com/in/aryan-sharma99999" class="btn">LinkedIn</a>
        <a href="https://instagram.com/aryanxsharma26" class="btn">Instagram</a>
    </div>
</div>

<div id="chatOrb">💬</div>

<script>
// Typewriter
const roles = ["web developer", "writer", "tech enthusiast", "video editor", "learner"];
let idx = 0, pos = 0, forward = true;
const el = document.getElementById("roleText");

function tick(){
  const word = roles[idx];
  if (forward){
    pos++;
    if (pos == word.length){ forward = false; setTimeout(tick, 900); return; }
  } else {
    pos--;
    if (pos == 0){ forward = true; idx = (idx+1)%roles.length; }
  }
  el.textContent = "I'm a " + word.slice(0,pos);
  setTimeout(tick, 80);
}
tick();
</script>
"""

components.html(html_code, height=780, scrolling=False)

# ---------------- Streamlit Sections ----------------

st.markdown("### 📸 Photos (Gallery)")
images = get_gallery_images()
if images:
    for img in images[:6]:
        st.image(img, use_column_width=True)

st.markdown("### ✍️ Writings (Anonymous)")
if "anon_msgs" not in st.session_state:
    st.session_state.anon_msgs = []

with st.form("anon", clear_on_submit=True):
    m = st.text_area("Write anonymously...")
    if st.form_submit_button("Send"):
        if m.strip():
            st.session_state.anon_msgs.insert(0, m)

for m in st.session_state.anon_msgs[:5]:
    st.info(m)

st.markdown("### 📰 Blog Posts")
for p in get_all_posts():
    st.subheader(p["title"])
    st.caption(p["date"])
    st.markdown(p["html"], unsafe_allow_html=True)
    st.markdown("---")

st.markdown("### 🛠 Projects")
st.write("- Chatbot Website")
st.write("- Portfolio Builder")
st.write("- AI Experiments")
