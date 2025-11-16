# ---------------------------------------------------------------
# Aryan Sharma – Premium Portfolio + Gallery + Chatbot (FAANG Style)
# ---------------------------------------------------------------

import os
import re
import time
import base64
import streamlit as st
from markdown import markdown
import streamlit.components.v1 as components

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Aryan Sharma",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- PATHS ----------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
GALLERY_DIR = os.path.join(BASE_DIR, "gallery")
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")


# ---------- HELPERS ----------
def get_gallery_images():
    if not os.path.exists(GALLERY_DIR):
        return []
    files = [f for f in os.listdir(GALLERY_DIR)
             if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
    files.sort()
    return [os.path.join(GALLERY_DIR, f) for f in files]


def make_base64(img_path):
    try:
        with open(img_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        ext = os.path.splitext(img_path)[1].lower().replace(".", "")
        return f"data:image/{ext};base64,{data}"
    except:
        return None


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
        "title": meta.get("title", slug.replace("-", " ").capitalize()),
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
    for f in md_files:
        data = get_post_data(f[:-3])
        if data:
            posts.append(data)
    return posts


# ---------------------------------------------------------------
# ⭐ HERO SECTION (FAANG GRADE — SMOOTH PARALLAX + TYPEWRITER)
# ---------------------------------------------------------------
hero_html = """
<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700;800&display=swap" rel="stylesheet">

<style>
body { margin:0; padding:0; font-family:'Inter',sans-serif; background:transparent; }

/* pastel animated background */
.bg {
  position:fixed; inset:0;
  background: linear-gradient(135deg,#fbe9f9,#eaf6ff,#f7f0ff,#ffe9f5);
  background-size:400% 400%;
  animation:bgMove 16s ease infinite;
  z-index:0;
}
@keyframes bgMove {
  0% {background-position:0% 50%;}
  50% {background-position:100% 50%;}
  100% {background-position:0% 50%;}
}

/* hero card */
.hero {
  position:relative; z-index:5;
  margin:120px auto;
  width:86%; max-width:1180px;
  background:rgba(255,255,255,0.72);
  border-radius:24px;
  padding:60px 60px 80px;
  box-shadow:0 30px 80px rgba(0,0,0,0.15);
  backdrop-filter:blur(14px);
  transform-style:preserve-3d;
  transition:transform .12s ease-out;
}

h1 { font-size:56px; font-weight:800; margin:0; color:#16161a; }
p { font-size:20px; color:#444; max-width:700px; }

.role-badge {
  display:inline-block;
  padding:10px 18px;
  border-radius:999px;
  background:linear-gradient(90deg,#e8d3ff,#ffd5ef);
  color:#5a2ea6; font-weight:700;
  margin-top:12px; font-size:18px;
}

/* buttons */
.btn {
  padding:14px 24px;
  border-radius:999px;
  font-weight:700;
  border:none;
  cursor:pointer;
  margin-right:12px;
  margin-top:20px;
  font-size:16px;
}
.fill { background:linear-gradient(90deg,#ffd6eb,#dfe9ff); color:#111; }
.outline { background:transparent; border:2px solid #999; color:#333; }

/* right preview images */
.prev-wrap {
  position:absolute; right:40px; top:40px;
  display:flex; gap:14px;
}
.prev {
  width:120px; height:120px;
  background:#fff; border-radius:14px; overflow:hidden;
  box-shadow:0 10px 30px rgba(0,0,0,0.18);
}
.prev img { width:100%; height:100%; object-fit:cover; }

/* parallax */
</style>
</head>

<body>

<div class="bg"></div>

<div class="hero" id="heroCard">
  <h3 style="color:#777;margin:0 0 6px;">Hello, I'm</h3>
  <h1>Aryan Sharma</h1>
  <p>I turn everyday life into little stories—coffee-powered, curious, and always building.</p>

  <div class="role-badge" id="role">Tech Enthusiast</div>

  <div>
    <button class="btn fill">View Projects</button>
    <button class="btn outline">Contact</button>
  </div>

  <div class="prev-wrap">
    <div class="prev"><img id="ph1"></div>
    <div class="prev"><img id="ph2"></div>
    <div class="prev"><img id="ph3"></div>
  </div>
</div>

<script>
/* typewriter names */
const roles = ["Tech Enthusiast","AI Learner","Creative Storyteller","Coffee-Powered Human ☕"];
let i=0,p=0,fwd=true;
const r = document.getElementById("role");

function tick(){
  const txt = roles[i];
  if(fwd){
    p++;
    if(p===txt.length) { fwd=false; setTimeout(tick,900); return; }
  } else {
    p--;
    if(p===0){ fwd=true; i=(i+1)%roles.length; }
  }
  r.textContent = txt.slice(0,p);
  setTimeout(tick,60);
}
tick();

/* parallax */
const card = document.getElementById("heroCard");
document.addEventListener("mousemove", e => {
  const x = (window.innerWidth/2 - e.clientX) / 40;
  const y = (window.innerHeight/2 - e.clientY) / 40;
  card.style.transform = `perspective(1200px) rotateY(${x}deg) rotateX(${y}deg)`;
});
</script>

</body>
</html>
"""

components.html(hero_html, height=780, scrolling=False)

# ---------------------------------------------------------------
#  ⭐ GLOBAL STYLING FOR STREAMLIT AREA
# ---------------------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#fbe9f9,#eaf6ff,#f7f0ff,#ffe9f5) !important;
}
.gallery-grid {
    display:grid;
    grid-template-columns:repeat(auto-fill,minmax(220px,1fr));
    gap:22px;
    padding:20px;
}
.g-item {
    border-radius:16px;
    overflow:hidden;
    box-shadow:0 10px 30px rgba(0,0,0,0.18);
    cursor:pointer;
    transition:.25s;
}
.g-item:hover { transform:translateY(-6px) scale(1.03); }
.g-item img { width:100%; height:100%; object-fit:cover; }

/* chat bubble */
#chatFloat {
    position:fixed;
    right:26px;
    bottom:26px;
    z-index:9999;
}
.chat-btn {
    width:68px;height:68px;
    border-radius:999px;border:none;
    cursor:pointer;font-size:28px;
    background:linear-gradient(135deg,#ffd6f7,#e5dbff);
    box-shadow:0 12px 40px rgba(0,0,0,0.26);
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------
# ⭐ GALLERY SECTION
# ---------------------------------------------------------------
st.markdown("## 📸 My Gallery")

images = get_gallery_images()

if images:
    g_html = "<div class='gallery-grid'>"

    for p in images:
        b64 = make_base64(p)
        if b64:
            g_html += f"""
            <div class='g-item' onclick="document.getElementById('lbImg').src='{b64}';document.getElementById('lb').style.display='flex';">
                <img src='{b64}' />
            </div>
            """

    g_html += "</div>"

    g_html += """
    <div id="lb" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.78); z-index:99999; align-items:center; justify-content:center;">
        <img id="lbImg" style="max-width:92%; max-height:92%; border-radius:18px;" />
        <button onclick="document.getElementById('lb').style.display='none';"
            style="position:absolute; top:22px; right:22px; background:#fff; font-size:22px; border-radius:999px; padding:10px 14px;">✕</button>
    </div>
    """

    st.markdown(g_html, unsafe_allow_html=True)
else:
    st.info("Add images to the `gallery` folder.")



# ---------------------------------------------------------------
# ⭐ BLOG SECTION
# ---------------------------------------------------------------
st.markdown("---")
st.markdown("## ✍️ Writings")

posts = get_all_posts()
if not posts:
    st.info("No blog posts found yet.")
else:
    for p in posts:
        st.subheader(p["title"])
        st.caption(p["date"])
        st.markdown(p["html"], unsafe_allow_html=True)
        st.markdown("---")



# ---------------------------------------------------------------
# ⭐ CHATBOT (Floating Bubble)
# ---------------------------------------------------------------
chat_html = """
<div id="chatFloat">
  <button class="chat-btn" onclick="toggleChat()">💬</button>

  <div id="chatBox" 
       style="display:none; position:fixed; right:26px; bottom:110px; width:360px; 
              background:#fff; border-radius:16px; box-shadow:0 20px 60px rgba(0,0,0,0.25); 
              overflow:hidden;">

      <div style="background:#18181b; color:#fff; padding:14px; font-weight:800;">
        Ask me about Aryan ☕
      </div>

      <div id="chatMessages" style="height:260px; overflow-y:auto; padding:12px; background:#f5f5f7;"></div>

      <div style="display:flex; padding:10px; gap:8px;">
        <input id="chatInput" placeholder="Type a question..." 
               style="flex:1; padding:10px; border-radius:10px; border:1px solid #ccc;">
        <button onclick="sendMsg()" 
                style="padding:10px 14px; border-radius:10px; border:none; background:#7b44e5; color:white;">
                Send
        </button>
      </div>
  </div>
</div>

<script>
function toggleChat(){
  let box = document.getElementById("chatBox");
  box.style.display = box.style.display === "none" ? "block" : "none";
}

function addMsg(text, who="bot"){
  let wrap = document.getElementById("chatMessages");
  let div = document.createElement("div");
  div.style.margin = "6px 0";
  div.style.padding = "10px 14px";
  div.style.maxWidth = "80%";
  div.style.borderRadius = "12px";
  div.style.fontSize = "14px";

  if(who==="user"){
    div.style.background="#dfe3ff";
    div.style.marginLeft="20%";
  } else {
    div.style.background="#ececec";
  }

  div.textContent = text;
  wrap.appendChild(div);
  wrap.scrollTop = wrap.scrollHeight;
}

const data = {
  "who is aryan": "Aryan is a calm, creative guy who turns moments into stories.",
  "what does aryan like": "Coffee, clean aesthetics, tech and learning new things.",
  "what motivates aryan": "Good ideas, good music and good coffee.",
};

function reply(q){
  q = q.toLowerCase();
  for(const k in data){
    if(q.includes(k)) return data[k];
  }
  if(q.includes("coffee")) return "Coffee is Aryan's superpower ☕.";
  if(q.includes("study")) return "He is currently pursuing BCA.";
  return "Ask me anything about Aryan ☕🙂!";
}

function sendMsg(){
  let inp = document.getElementById("chatInput");
  let txt = inp.value.trim();
  if(!txt) return;
  addMsg(txt, "user");
  inp.value="";
  setTimeout(()=>{ addMsg(reply(txt)); },400);
}
</script>
"""

components.html(chat_html, height=0, scrolling=False)


# ---------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------
st.markdown("---")
st.header("Projects")
st.write("- Chatbot Website\n- AI Experiments\n- Portfolio Designs")

st.header("Contact")
st.write("DM on Instagram: [aryanxsharma26](https://instagram.com/aryanxsharma26)")

