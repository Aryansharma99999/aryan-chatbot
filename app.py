# app.py
import os
import re
import time
import streamlit as st
from markdown import markdown
import streamlit.components.v1 as components

st.set_page_config(page_title="Aryan Sharma", layout="wide", initial_sidebar_state="collapsed")

# ---------------- Helpers: gallery & blog ----------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
GALLERY_DIR = os.path.join(BASE_DIR, "gallery")
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")


def get_gallery_images():
    if not os.path.exists(GALLERY_DIR):
        return []
    files = [f for f in os.listdir(GALLERY_DIR)
             if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
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
                k, v = line.split(':', 1)
                meta[k.strip()] = v.strip()
        body = content[meta_match.end():].strip()

    html = markdown(body)
    return {
        "slug": slug,
        "title": meta.get("title", slug.replace('-', ' ').capitalize()),
        "date": meta.get("date", ""),
        "author": meta.get("author", ""),
        "summary": meta.get("summary", ""),
        "html": html
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


# ---------------- Premium Galaxy hero + dynamic chatbot ----------------

hero_html = """
<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">

<style>
:root{
  --text: #eaf6ff;
  --glass: rgba(255,255,255,0.04);
}

/* full galaxy canvas */
html, body{ margin:0; padding:0; height:100%; overflow:hidden; font-family:Inter, system-ui; color:var(--text); }
#galaxy-wrap { position:fixed; inset:0; z-index:0; }

/* hero container */
.page{ position:relative; z-index:5; min-height:100vh; display:flex; align-items:center; justify-content:center; padding:40px; }

/* glass hero card */
.hero-card {
  width:90%; max-width:1100px;
  padding:46px; border-radius:18px;
  backdrop-filter: blur(18px) saturate(140%);
  -webkit-backdrop-filter: blur(18px) saturate(140%);
  background: rgba(255,255,255,0.03);
  border:1px solid rgba(255,255,255,0.045);
  box-shadow:0 40px 110px rgba(2,6,20,0.55);
  text-align:center;
  transform: translateY(20px); opacity:0;
  transition:all .8s cubic-bezier(.2,.9,.3,1);
}
.hero-card.show { transform:translateY(0); opacity:1; }

.hero-title { font-size:48px; font-weight:800; }
.hero-sub { margin-top:8px; font-size:18px; opacity:.9; }
.roles { font-weight:700; color:#d2e6ff; }

.cta { margin-top:24px; display:flex; justify-content:center; gap:12px; }
.btn {
  padding:10px 18px; border-radius:999px; font-weight:700; cursor:pointer;
  transition:transform .18s ease;
  border:none;
}
.btn:hover{ transform:translateY(-4px); }
.btn-primary {
  background:#8db3ff; color:#07182a;
}
.btn-ghost {
  background:transparent; color:#eaf6ff; border:1px solid rgba(255,255,255,0.06);
}

/* Chat orb */
.chat-orb{
  position:fixed; right:26px; bottom:28px; width:62px; height:62px;
  border-radius:999px; z-index:10;
  background:rgba(10,12,18,0.92);
  display:flex; align-items:center; justify-content:center;
  box-shadow:0 24px 70px rgba(0,0,0,0.6);
  cursor:pointer; transition:transform .18s ease;
}
.chat-orb:hover{ transform:translateY(-5px); }

/* Dynamic island chat */
.island{
  position:fixed; right:26px; bottom:110px; width:380px; max-width:92vw;
  border-radius:14px; overflow:hidden; background:rgba(6,10,14,0.92);
  border:1px solid rgba(255,255,255,0.04);
  box-shadow:0 30px 100px rgba(0,0,0,0.65);
  display:none; z-index:20;
  animation:islandIn .25s ease;
}
@keyframes islandIn{
  from{transform:translateY(8px) scale(.98); opacity:0;}
  to{transform:translateY(0) scale(1); opacity:1;}
}

.island-header{ padding:12px; font-weight:700; background:rgba(255,255,255,0.04); }
.island-body{ padding:12px; max-height:300px; overflow:auto; }
.msg{ padding:10px 14px; margin:8px 0; border-radius:12px; max-width:80%; }
.msg.user{ background:rgba(255,255,255,0.08); margin-left:auto; }
.msg.bot{ background:rgba(120,160,255,0.08); }

.island-footer{ padding:12px; display:flex; gap:8px; }
.chat-input{ flex:1; padding:10px; border-radius:10px; border:none; background:#0d1014; color:#eaf6ff; }

</style>
</head>

<body>

<div id="galaxy-wrap">
  <canvas id="galaxy"></canvas>
</div>

<div class="page">
  <div class="hero-card" id="heroCard">
    <h1 class="hero-title">Aryan Sharma</h1>
    <div class="hero-sub">Welcome to my personal website!</div>
    <div style="margin-top:10px;">I'm a <span class="roles" id="role">developer</span></div>

    <div class="cta">
      <a href="/resume.pdf#chatbot-section" class="btn btn-primary">Download Resume</a>
      <button class="btn btn-ghost" onclick="document.getElementById('projects_anchor').scrollIntoView({behavior:'smooth'})">Get In Touch</button>
    </div>
  </div>
</div>

<div class="chat-orb" id="chatOrb">💬</div>

<div class="island" id="island">
  <div class="island-header">Ask me about Aryan ☕</div>
  <div class="island-body" id="chatBody"></div>
  <div class="island-footer">
    <input id="chatInput" class="chat-input" placeholder="Ask something...">
    <button id="chatSend" class="btn btn-primary">Send</button>
  </div>
</div>

<script>
/* ---------------- STARFIELD CANVAS ---------------- */
const canvas = document.getElementById('galaxy');
const ctx = canvas.getContext('2d');
function resize(){
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}
resize();
window.onresize = resize;

let stars = [];
for(let i=0;i<180;i++){
  stars.push({
    x:Math.random()*canvas.width,
    y:Math.random()*canvas.height,
    r:Math.random()*2+0.2,
    s:Math.random()*0.6+0.2
  });
}

function loop(){
  ctx.clearRect(0,0,canvas.width,canvas.height);
  ctx.fillStyle="white";
  for(let s of stars){
    ctx.globalAlpha = 0.5 + Math.sin(s.x*0.05 + s.y*0.05 + Date.now()*0.001)*0.3;
    ctx.beginPath();
    ctx.arc(s.x,s.y,s.r,0,Math.PI*2);
    ctx.fill();
    s.x += s.s;
    if(s.x > canvas.width) s.x = 0;
  }
  requestAnimationFrame(loop);
}
loop();

/* ---------------- HERO ANIMATION ---------------- */
window.onload = ()=> {
  document.getElementById("heroCard").classList.add("show");
};

/* ---------------- TYPEWRITER ---------------- */
const roles = ["web developer","tech enthusiast","programmer","writer","editor"];
let idx=0, pos=0, forward=true;
const roleEl = document.getElementById("role");

function type(){
  const curr = roles[idx];
  if(forward){
    pos++;
    roleEl.textContent = curr.slice(0,pos);
    if(pos===curr.length){ forward=false; setTimeout(type,800); return; }
  } else {
    pos--;
    roleEl.textContent = curr.slice(0,pos);
    if(pos===0){ forward=true; idx=(idx+1)%roles.length; setTimeout(type,400); return;}
  }
  setTimeout(type,70);
}
type();

/* ---------------- CHAT DATA ---------------- */
const ARYAN_FACTS = {
  "who is aryan": "Aryan is that guy who turns everyday moments into funny stories without even trying.",
  "what is aryan currently studying": "Pursuing a Bachelor's degree. 🎓",
  "what makes aryan smile": "Random jokes, good coffee, and accidental life plot twists.",
  "what’s aryan’s comfort drink": "Coffee ☕. Without it, he’s basically on airplane mode.",
  "does aryan like travelling": "Yes! Especially when the trip ends with coffee and mountain views.",
  "how does aryan handle pressure": "With calmness… and maybe two extra cups of coffee.",
  "what is aryan good at": "Turning simple moments into mini stories and making people laugh randomly.",
  "what’s aryan’s vibe": "Chill, creative, and always up for a good conversation.",
  "is aryan an introvert or extrovert": "Somewhere in between—depends on the energy, the weather, and the wifi.",
  "what motivates aryan": "New ideas, good music, and that one perfect cup of coffee.",
  "how does aryan face challenges": "With confidence… and sarcasm when required.",
  "what’s something aryan can’t live without": "Coffee. None 😅. But coffee keeps him warm.",
  "what makes aryan unique": "His ability to make people laugh even when he’s not trying.",
  "what’s aryan’s favorite weather": "Cold breeze + warm coffee = perfection.",
  "how does aryan relax": "Storytelling, music, and wandering thoughts.",
  "what is aryan passionate about": "Tech, creativity, and turning ideas into reality.",
  "what is aryan learning right now": "New tech skills… one coffee at a time.",
  "what type of person is aryan": "Calm, humorous, and secretly a deep thinker.",
  "what’s aryan’s favourite thing to do": "Observe life and turn it into funny, relatable stories.",
  "what does aryan dream about": "A life full of learning, creativity, and endless coffee."
};

/* ---------------- CHAT LOGIC ---------------- */
const orb = document.getElementById("chatOrb");
const island = document.getElementById("island");
const chatBody = document.getElementById("chatBody");
const chatInput = document.getElementById("chatInput");
const chatSend = document.getElementById("chatSend");

orb.onclick = () => {
  island.style.display = island.style.display==="block" ? "none" : "block";
  chatInput.focus();
  if(chatBody.children.length===0){
    addMsg("Hi! I'm Aryan's assistant ☕ Ask me anything.","bot");
  }
};

function addMsg(text, who){
  let el = document.createElement("div");
  el.className = "msg " + (who==="user"?"user":"bot");
  el.innerText = text;
  chatBody.appendChild(el);
  chatBody.scrollTop = chatBody.scrollHeight;
}

function botReply(q){
  q = q.toLowerCase();
  for(let k in ARYAN_FACTS){
    if(q.includes(k)) return ARYAN_FACTS[k];
  }
  if(q.includes("name")) return "Aryan Sharma — the guy with stories & coffee.";
  if(q.includes("coffee")) return ARYAN_FACTS["what’s aryan’s comfort drink"];
  if(q.includes("study")) return ARYAN_FACTS["what is aryan currently studying"];
  return "Ask me anything about Aryan ☕🙂!";
}

chatSend.onclick = () => {
  let t = chatInput.value.trim();
  if(!t) return;
  addMsg(t,"user");
  chatInput.value = "";
  setTimeout(()=> addMsg(botReply(t),"bot"), 300);
};

chatInput.onkeydown = (e)=>{
  if(e.key==="Enter"){
    chatSend.click();
  }
};
</script>

</body>
</html>
"""


# Render full hero component
components.html(hero_html, height=760, scrolling=False)


# ---------------- GLOBAL STREAMLIT GLASS THEME ----------------
st.markdown(
    """
    <style>
    .stApp {
        background: transparent !important;
        color: #eaf6ff !important;
    }
    .stBlock, .css-1lcbmhc, .st-cz, .st-b1, .css-18e3th9 {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.04) !important;
        box-shadow: 0 12px 40px rgba(0,0,0,0.45) !important;
        border-radius:12px;
        padding:16px;
    }
    a { color:#d8e9ff !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- PAGE CONTENT ----------------
st.markdown("---")
col1, col2 = st.columns([1,2])

with col1:
    st.markdown("### 📸 Photos (Gallery)")
    images = get_gallery_images()
    for img in images[:6]:
        st.image(img, use_column_width=True)
    if len(images) > 6:
        st.caption(f"{len(images)-6} more...")

with col2:
    st.markdown("### ✍️ Writings (Anonymous)")
    if "anon_msgs" not in st.session_state:
        st.session_state.anon_msgs = []
    with st.form("anon", clear_on_submit=True):
        m = st.text_area("Write anonymously...")
        if st.form_submit_button("Send"):
            if m.strip():
                st.session_state.anon_msgs.insert(0, m)
                st.success("Sent.")
    for m in st.session_state.anon_msgs[:8]:
        st.info(m)

    st.markdown("---")
    st.markdown("### 📰 Blog Posts")
    posts = get_all_posts()
    for p in posts:
        st.subheader(p["title"])
        st.caption(p["date"])
        st.markdown(p["html"], unsafe_allow_html=True)
        st.markdown("---")

st.markdown("---")
st.info("Use the floating chat orb to talk to Aryan's chatbot ☕")

st.markdown("---")
st.markdown("<a id='projects_anchor'></a>", unsafe_allow_html=True)
st.header("Projects")
st.markdown("""
- Chatbot Website  
- Portfolio Builder  
- AI Experiments  
""")

st.header("Contact")
st.write("Instagram:", "[aryanxsharma26](https://instagram.com/aryanxsharma26)")
