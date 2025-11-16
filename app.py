# app.py — Premium Portfolio + Floating Chatbot

import os
import re
import time
import base64
import streamlit as st
from markdown import markdown
import streamlit.components.v1 as components

st.set_page_config(page_title="Aryan Sharma", layout="wide", initial_sidebar_state="collapsed")

# ---------- Helper Paths ----------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
GALLERY_DIR = os.path.join(BASE_DIR, "gallery")
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")

def get_gallery_images():
    if not os.path.exists(GALLERY_DIR):
        return []
    files = [f for f in os.listdir(GALLERY_DIR) 
             if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
    files.sort()
    return [os.path.join(GALLERY_DIR, f) for f in files]

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
        for line in meta_match.group(1).splitlines():
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
        "summary": meta.get("summary", ""),
        "html": html,
    }

def get_all_posts():
    if not os.path.exists(POSTS_DIR):
        return []
    posts = []
    for file in os.listdir(POSTS_DIR):
        if file.endswith(".md"):
            slug = file[:-3]
            data = get_post_data(slug)
            if data:
                posts.append(data)
    return posts

# ---------- HERO SECTION (C3 style) ----------
hero_html = """
<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700;800&display=swap" rel="stylesheet">

<style>
:root{
  --bg1: #fbe9f9;
  --bg2: #eaf6ff;
  --bg3: #f7f0ff;
  --card: rgba(255,255,255,0.7);
  --accent: #7b44e5;
}
html,body{
  margin:0; padding:0; font-family:'Inter',sans-serif; background:transparent;
}

.hero-wrap{
  position:relative;
  width:100%;
  min-height:92vh;
  display:flex;
  justify-content:center;
  align-items:center;
  background:linear-gradient(180deg,var(--bg2),var(--bg3),var(--bg1));
  overflow:hidden;
}

/* floating pastel blobs */
.blob{
  position:absolute;
  width:500px;
  height:400px;
  filter:blur(60px);
  opacity:0.6;
  animation:float 12s infinite ease-in-out;
}
@keyframes float{
  0%{transform:translateY(0px);}
  50%{transform:translateY(40px);}
  100%{transform:translateY(0px);}
}
.b1{left:-120px; top:-80px; background:#ffd6eb;}
.b2{right:-140px; top:20px; background:#e8f0ff;}
.b3{left:10%; bottom:-80px; background:#fff2ec;}

.hero-card{
  width:86%;
  max-width:1100px;
  background:var(--card);
  backdrop-filter:blur(14px);
  border-radius:28px;
  padding:48px;
  box-shadow:0 25px 60px rgba(0,0,0,0.08);
  transform-style:preserve-3d;
}
.hero-title{
  font-size:48px;
  font-weight:800;
  margin:0;
  color:#101014;
}
.tag{
  display:inline-block;
  margin-top:12px;
  padding:8px 16px;
  border-radius:999px;
  background:rgba(123,68,229,0.14);
  color:var(--accent);
  font-weight:700;
}
.btn{
  padding:14px 24px;
  border:none;
  border-radius:999px;
  margin-top:22px;
  margin-right:10px;
  font-weight:700;
  cursor:pointer;
  background:linear-gradient(90deg,#ffd6eb,#dfe9ff);
}
.btn-ghost{
  padding:14px 24px;
  background:white;
  border-radius:999px;
  border:1px solid #ccc;
  margin-top:22px;
}
</style>
</head>

<body>
<div class="hero-wrap" id="hero">
  <div class="blob b1"></div>
  <div class="blob b2"></div>
  <div class="blob b3"></div>

  <div class="hero-card" id="heroCard">
    <p style="margin:0;font-weight:600;color:#444;">Hello, I'm</p>
    <h1 class="hero-title">Aryan Sharma</h1>
    <p style="font-size:20px;color:#444;margin-top:10px;">
      I turn everyday life into little stories—coffee-powered, curious, and always building.
    </p>

    <div class="tag" id="role">Creative Storyteller</div>

    <div>
      <button class="btn" onclick="location.href='#projects'">View Projects</button>
      <button class="btn-ghost" onclick="location.href='#contact'">Contact</button>
    </div>
  </div>
</div>

<script>
// typewriter
const roles = ["Creative Storyteller","Tech Enthusiast","AI Learner","Coffee-Powered Human"];
let r=0, pos=0, fw=true;
const el=document.getElementById("role");

function tw(){
  let t = roles[r];
  if(fw){
    pos++;
    if(pos===t.length){fw=false; setTimeout(tw,800); return;}
  } else {
    pos--;
    if(pos===0){fw=true; r=(r+1)%roles.length; setTimeout(tw,400); return;}
  }
  el.textContent = t.slice(0,pos);
  setTimeout(tw,60);
}
tw();

// parallax
document.addEventListener("mousemove", e=>{
  let x=(window.innerWidth/2 - e.clientX)/40;
  let y=(window.innerHeight/2 - e.clientY)/40;
  document.getElementById("heroCard").style.transform=
    `perspective(900px) rotateY(${x}deg) rotateX(${y}deg)`;
});
</script>

</body>
</html>
"""

components.html(hero_html, height=760, scrolling=False)

# ---------- Global Streamlit Soft Theme ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, rgba(234,246,255,0.96), rgba(247,240,255,0.97)) !important;
}
</style>
""", unsafe_allow_html=True)
# ---------- GALLERY SECTION ----------
import base64

images = get_gallery_images()

def to_base64(path):
    try:
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        ext = os.path.splitext(path)[1].replace(".", "")
        return f"data:image/{ext};base64,{data}"
    except:
        return None

if images:
    gallery_items = []
    for img in images:
        b64 = to_base64(img)
        if not b64:
            continue
        name = os.path.basename(img)

        gallery_items.append(f"""
            <div class="g-item" onclick="openLightbox('{b64}')">
                <img src="{b64}" loading="lazy" alt="{name}">
            </div>
        """)

    gallery_html = f"""
    <style>
        .g-grid {{
            display:grid;
            grid-template-columns:repeat(auto-fill, minmax(200px,1fr));
            gap:20px;
            padding:20px 10px;
        }}
        .g-item {{
            border-radius:16px;
            overflow:hidden;
            background:white;
            box-shadow:0 10px 25px rgba(0,0,0,0.08);
            transition:0.25s ease;
            cursor:pointer;
        }}
        .g-item:hover {{
            transform:translateY(-6px);
            box-shadow:0 20px 40px rgba(0,0,0,0.12);
        }}
        .g-item img {{
            width:100%; height:100%; object-fit:cover;
            transition:0.35s ease;
        }}
        .g-item:hover img {{
            transform:scale(1.06);
        }}

        /* LIGHTBOX */
        #lb {{
            display:none;
            position:fixed;
            inset:0;
            z-index:999999;
            background:rgba(0,0,0,0.6);
            backdrop-filter:blur(4px);
            justify-content:center;
            align-items:center;
        }}
        #lb img {{
            max-width:90%;
            max-height:90%;
            border-radius:14px;
            box-shadow:0 25px 70px rgba(0,0,0,0.6);
        }}
        #lb button {{
            position:absolute;
            top:30px; right:40px;
            padding:8px 14px;
            border:none;
            font-size:22px;
            border-radius:8px;
            cursor:pointer;
        }}
    </style>

    <h2 style="padding-left:10px; padding-top:10px;">My Gallery</h2>
    <div class="g-grid">
        {''.join(gallery_items)}
    </div>

    <div id="lb">
      <img id="lb-img" src="">
      <button onclick="closeLightbox()">✕</button>
    </div>

    <script>
        function openLightbox(src) {{
            document.getElementById("lb-img").src = src;
            document.getElementById("lb").style.display = "flex";
        }}
        function closeLightbox() {{
            document.getElementById("lb").style.display = "none";
        }}
        document.addEventListener("keydown", e => {{
            if(e.key === "Escape") closeLightbox();
        }});
    </script>
    """

    st.markdown(gallery_html, unsafe_allow_html=True)
else:
    st.info("No images found in gallery — upload images to /gallery folder.")


# ---------- BLOG / WRITINGS ----------
st.markdown("---")
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 📸 Gallery (Preview)")
    if not images:
        st.info("No images found. Add images to the `gallery/` folder.")
    else:
        for i, img in enumerate(images):
            st.image(img, width=200)
            if i >= 3:
                break
        if len(images) > 4:
            st.caption(f"+ {len(images)-4} more in the main gallery.")

with col2:
    st.markdown("### ✍️ Writings")
    posts = get_all_posts()
    if not posts:
        st.info("No blog posts found. Add `.md` files to blog_posts/.")
    else:
        for p in posts:
            st.subheader(p["title"])
            st.caption(p["date"])
            st.markdown(p["html"], unsafe_allow_html=True)
            st.markdown("---")
# ---------- PREMIUM FLOATING CHATBOT ----------
chat_html = """
<style>
/* Chat Bubble */
#chat-float {
    position: fixed;
    bottom: 28px;
    right: 26px;
    z-index: 99999;
}
#chat-btn {
    width: 68px; height: 68px;
    border-radius: 50%;
    border: none;
    cursor: pointer;
    background: linear-gradient(145deg, #fde8ff, #e8f2ff);
    box-shadow: 0 12px 28px rgba(0,0,0,0.12);
    font-size: 30px;
    transition: 0.25s ease;
}
#chat-btn:hover {
    transform: translateY(-4px);
    box-shadow: 0 18px 40px rgba(0,0,0,0.14);
}

/* Chat Window */
#chat-window {
    position: fixed;
    bottom: 110px;
    right: 26px;
    width: 360px;
    max-width: 92vw;
    display: none;
    z-index: 999999;
    background: rgba(255,255,255,0.9);
    border-radius: 16px;
    box-shadow: 0 25px 50px rgba(0,0,0,0.14);
    backdrop-filter: blur(10px);
    overflow: hidden;
    animation: fadeIn 0.25s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; }
}

/* Chat Header */
#chat-header {
    padding: 12px 16px;
    background: linear-gradient(145deg, #0c1116, #0f1419);
    color: #d7ecff;
    font-size: 17px;
    font-weight: 700;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
#chat-close {
    background: transparent;
    border: none;
    color: #d7ecff;
    font-size: 20px;
    cursor: pointer;
}

/* Messages */
#chat-messages {
    max-height: 260px;
    overflow-y: auto;
    padding: 12px;
    background: linear-gradient(180deg, #0c0f12, #111418);
}
.message {
    margin: 8px 0;
    padding: 10px 12px;
    border-radius: 10px;
    font-size: 14px;
    max-width: 80%;
    white-space: pre-wrap;
}
.msg-bot {
    background: linear-gradient(145deg, #11171d, #0c1115);
    color: #d5f1ff;
    margin-right: 20%;
}
.msg-user {
    background: white;
    color: #1a1a1a;
    margin-left: 20%;
}

/* Input */
#chat-input-area {
    display: flex;
    gap: 8px;
    padding: 12px;
    background: #f6f6ff;
}
#chat-input {
    flex: 1;
    padding: 10px;
    border-radius: 10px;
    border: none;
    background: #ffffff;
}
#chat-send {
    padding: 10px 14px;
    background: #7b44e5;
    color: #fff;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    font-weight: 700;
}
#chat-send:hover {
    opacity: 0.9;
}
</style>

<div id="chat-float">
  <button id="chat-btn">💬</button>
</div>

<div id="chat-window">
  <div id="chat-header">
    Ask me about Aryan ☕
    <button id="chat-close">✕</button>
  </div>
  <div id="chat-messages"></div>
  <div id="chat-input-area">
      <input id="chat-input" placeholder="Ask something..." />
      <button id="chat-send">Send</button>
  </div>
</div>

<script>
const chatBtn = document.getElementById("chat-btn");
const chatWindow = document.getElementById("chat-window");
const chatClose = document.getElementById("chat-close");
const msgArea = document.getElementById("chat-messages");
const chatInput = document.getElementById("chat-input");
const chatSend = document.getElementById("chat-send");

chatBtn.onclick = () => {
    chatWindow.style.display = "block";
    if (!msgArea.hasChildNodes()) addBot("Hey! Ask me anything about Aryan ☕");
    chatInput.focus();
};
chatClose.onclick = () => chatWindow.style.display = "none";

function addBot(text) {
    const el = document.createElement("div");
    el.className = "message msg-bot";
    el.textContent = text;
    msgArea.appendChild(el);
    msgArea.scrollTop = msgArea.scrollHeight;
}

function addUser(text) {
    const el = document.createElement("div");
    el.className = "message msg-user";
    el.textContent = text;
    msgArea.appendChild(el);
    msgArea.scrollTop = msgArea.scrollHeight;
}

const answers = {
    "who is aryan": "Aryan is someone who turns normal moments into little stories—coffee-powered and unintentionally funny.",
    "what is aryan studying": "He is pursuing his Bachelor's degree 🎓.",
    "does aryan drink coffee": "Coffee isn't a drink—it's his superpower ☕.",
    "does aryan like travelling": "Yes! But only if the destination includes mountains + coffee.",
    "what is aryan good at": "Storytelling, tech, and making people laugh without trying.",
    "what makes aryan unique": "His vibe + humour + the way he observes life.",
    "what motivates aryan": "New ideas, creativity, music, and good coffee.",
    "what is aryan learning": "Tech, AI, creativity… one cup at a time.",
};

function reply(msg) {
    let q = msg.toLowerCase();
    for (let key in answers) {
        if (q.includes(key)) return answers[key];
    }
    if (q.includes("name")) return "Aryan Sharma — the guy who mixes creativity + logic.";
    if (q.includes("coffee")) return "Coffee is basically his personality trait ☕";
    return "Ask me anything about Aryan ☕🙂";
}

chatSend.onclick = () => sendMsg();
chatInput.addEventListener("keydown", e => {
    if (e.key === "Enter") sendMsg();
});

function sendMsg() {
    let text = chatInput.value.trim();
    if (!text) return;
    addUser(text);
    chatInput.value = "";
    setTimeout(() => {
        addBot(reply(text));
    }, 300);
}
</script>
"""

components.html(chat_html, height=10, scrolling=False)


# ---------- FOOTER ----------
st.markdown("---")
st.markdown(
    """
    <div style='text-align:center; opacity:0.7; padding:18px 0;'>
        Made with ☕ by Aryan Sharma
    </div>
    """,
    unsafe_allow_html=True
)
