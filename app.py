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
#galaxy-wrap { position:fixed; inset:0; z-index:0; pointer-events:none; }

/* hero container */
.page{ position:relative; z-index:6; min-height:100vh; display:flex; align-items:center; justify-content:center; padding:40px; }

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

.hero-title { font-size:48px; font-weight:800; margin:0; color: #f1f8ff; }
.hero-sub { margin-top:8px; font-size:18px; opacity:.92; color: rgba(230,240,255,0.9); }
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
  border-radius:999px; z-index:20;
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
  display:none; z-index:30;
  animation:islandIn .25s ease;
}
@keyframes islandIn{
  from{transform:translateY(8px) scale(.98); opacity:0;}
  to{transform:translateY(0) scale(1); opacity:1;}
}

.island-header{ padding:12px; font-weight:700; background:rgba(255,255,255,0.04); color:#cdeeff; }
.island-body{ padding:12px; max-height:300px; overflow:auto; }
.msg{ padding:10px 14px; margin:8px 0; border-radius:12px; max-width:80%; color:#eef7ff; }
.msg.user{ background:rgba(255,255,255,0.08); margin-left:auto; color:#081827; }
.msg.bot{ background:rgba(120,160,255,0.08); }

/* input */
.island-footer{ padding:12px; display:flex; gap:8px; }
.chat-input{ flex:1; padding:10px; border-radius:10px; border:none; background:#0d1014; color:#eaf6ff; outline:none; }

/* small mobile tweaks */
@media (max-width:760px){
  .hero-title { font-size:32px; }
  .island{ left:12px; right:12px; width:calc(100% - 24px); bottom:80px; }
}
</style>
</head>

<body>

<div id="galaxy-wrap">
  <canvas id="galaxy"></canvas>
</div>

<div class="page">
  <div class="hero-card" id="heroCard" role="banner" aria-label="Hero">
    <h1 class="hero-title">Aryan Sharma</h1>
    <div class="hero-sub">Welcome to my personal website!</div>
    <div style="margin-top:10px;">I'm a <span class="roles" id="role">developer</span></div>

    <div class="cta">
      <a href="/resume.pdf#chatbot-section" class="btn btn-primary">Download Resume</a>
      <button class="btn btn-ghost" onclick="document.getElementById('projects_anchor').scrollIntoView({behavior:'smooth'})">Get In Touch</button>
    </div>
  </div>
</div>

<div class="chat-orb" id="chatOrb" aria-label="Open chat">💬</div>

<div class="island" id="island" role="dialog" aria-modal="true" aria-label="Chat with Aryan">
  <div class="island-header">Ask me about Aryan ☕</div>
  <div class="island-body" id="chatBody" aria-live="polite"></div>
  <div class="island-footer">
    <input id="chatInput" class="chat-input" placeholder="Ask something...">
    <button id="chatSend" class="btn btn-primary">Send</button>
  </div>
</div>

<script>
/* ---------------- STARFIELD CANVAS (optimized, multi-layer look) ---------------- */
(function(){
  const canvas = document.getElementById('galaxy');
  const ctx = canvas.getContext('2d');

  function resize(){
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  // create multi-layer star sets for depth
  const layers = [
    {count: 90, speed: 0.2, size: [0.3, 1.0], alpha: 0.5},
    {count: 50, speed: 0.6, size: [1.2, 2.2], alpha: 0.85},
    {count: 25, speed: 1.2, size: [2.8, 4.0], alpha: 0.95}
  ];
  let starGroups = [];
  function makeStars(){
    starGroups = [];
    for(const L of layers){
      const arr = [];
      for(let i=0;i<L.count;i++){
        arr.push({
          x: Math.random()*canvas.width,
          y: Math.random()*canvas.height,
          r: Math.random()*(L.size[1]-L.size[0]) + L.size[0],
          vx: (Math.random()*2-1)*L.speed*0.3,
          vy: (Math.random()*2-1)*L.speed*0.3,
          a: L.alpha*(0.6 + Math.random()*0.4)
        });
      }
      starGroups.push(arr);
    }
  }
  makeStars();

  let t = 0, mx = canvas.width/2, my = canvas.height/2;
  window.addEventListener('mousemove', (e)=>{ mx = e.clientX; my = e.clientY; });

  function drawNebula(){
    // dark gradient base
    const g = ctx.createLinearGradient(0,0,canvas.width,canvas.height);
    g.addColorStop(0, 'rgba(8,10,18,0.95)');
    g.addColorStop(1, 'rgba(12,14,28,0.95)');
    ctx.fillStyle = g;
    ctx.fillRect(0,0,canvas.width,canvas.height);

    // soft nebula radial glows
    const cx = canvas.width*0.65 + Math.sin(t*0.2)*120;
    const cy = canvas.height*0.28 + Math.cos(t*0.15)*80;
    const rg = ctx.createRadialGradient(cx,cy,0,cx,cy, Math.max(canvas.width,canvas.height)*0.9);
    rg.addColorStop(0, 'rgba(60,40,120,0.14)');
    rg.addColorStop(0.25, 'rgba(80,60,160,0.08)');
    rg.addColorStop(0.6, 'rgba(6,10,20,0.02)');
    ctx.globalCompositeOperation = 'lighter';
    ctx.fillStyle = rg;
    ctx.fillRect(0,0,canvas.width,canvas.height);
    ctx.globalCompositeOperation = 'source-over';
  }

  function drawStars(){
    for(let gi=0; gi<starGroups.length; gi++){
      const group = starGroups[gi];
      for(const s of group){
        // parallax based on mouse
        const px = (mx - canvas.width/2) * (0.0006 + gi*0.001);
        const py = (my - canvas.height/2) * (0.0006 + gi*0.001);
        s.x += s.vx;
        s.y += s.vy;
        if(s.x < -10) s.x = canvas.width + 10;
        if(s.x > canvas.width + 10) s.x = -10;
        if(s.y < -10) s.y = canvas.height + 10;
        if(s.y > canvas.height + 10) s.y = -10;

        ctx.beginPath();
        ctx.fillStyle = 'rgba(255,255,255,' + (s.a * (0.6 + Math.sin((t + s.x + s.y)/90)*0.35)) + ')';
        ctx.arc(s.x + px*40, s.y + py*40, s.r, 0, Math.PI*2);
        ctx.fill();
      }
    }
  }

  function loop(){
    t += 0.018;
    drawNebula();
    drawStars();
    requestAnimationFrame(loop);
  }
  loop();
})();

/* ---------------- HERO SHOW + TYPEWRITER ---------------- */
window.addEventListener('DOMContentLoaded', function(){
  setTimeout(()=>document.getElementById('heroCard').classList.add('show'), 120);
  const roles = ["web developer","tech enthusiast","programmer","writer","editor"];
  let idx=0,pos=0,fw=true; const el = document.getElementById('role');
  (function tick(){
    const cur = roles[idx];
    if(fw){ pos++; el.textContent = cur.slice(0,pos); if(pos===cur.length){ fw=false; setTimeout(tick,800); return; } }
    else { pos--; el.textContent = cur.slice(0,pos); if(pos===0){ fw=true; idx=(idx+1)%roles.length; setTimeout(tick,400); return; } }
    setTimeout(tick,70);
  })();
});

/* ---------------- ARYAN_FACTS (client-side JS) ---------------- */
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

/* ---------------- CHAT SCRIPT ---------------- */
(function(){
  const orb = document.getElementById('chatOrb');
  const island = document.getElementById('island');
  const body = document.getElementById('chatBody');
  const input = document.getElementById('chatInput');
  const send = document.getElementById('chatSend');

  function addMsg(t, who){
    const el = document.createElement('div');
    el.className = 'msg ' + (who==='user'? 'user' : 'bot');
    el.textContent = t;
    body.appendChild(el);
    body.scrollTop = body.scrollHeight;
  }

  orb.addEventListener('click', ()=>{
    island.style.display = island.style.display === 'block' ? 'none' : 'block';
    input.focus();
    if(body.children.length === 0) addMsg("Hi! I'm Aryan's assistant — ask me anything about Aryan ☕", 'bot');
  });

  send.addEventListener('click', ()=>{
    const q = input.value.trim();
    if(!q) return;
    addMsg(q, 'user');
    input.value = '';
    setTimeout(()=> {
      const lq = q.toLowerCase();
      let resp = null;
      for(const k in ARYAN_FACTS){
        if(lq.includes(k)) { resp = ARYAN_FACTS[k]; break; }
      }
      if(!resp){
        if(lq.includes('name')) resp = "Aryan Sharma — the guy with stories & coffee.";
        else if(lq.includes('coffee')) resp = ARYAN_FACTS["what’s aryan’s comfort drink"];
        else if(lq.includes('study')) resp = ARYAN_FACTS["what is aryan currently studying"];
        else resp = "Ask me anything about Aryan ☕🙂!";
      }
      addMsg(resp, 'bot');
    }, 300 + Math.random()*320);
  });

  input.addEventListener('keydown', (e)=>{ if(e.key === 'Enter'){ e.preventDefault(); send.click(); } });
})();
</script>

</body>
</html>
"""

# Render component (place at top so canvas sits behind)
components.html(hero_html, height=760, scrolling=False)

# ---------------- VERY ROBUST STREAMLIT TRANSPARENCY OVERRIDE ----------------
# This CSS aggressively forces Streamlit to be transparent so the canvas and glass hero appear as intended.
st.markdown(
    """
    <style>
    /* Make page background transparent so canvas shows through */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] > div, .block-container {
        background: transparent !important;
        background-image: none !important;
    }

    /* Target common Streamlit generated class name patterns and remove background/shadow */
    .css-18e3th9, .css-1lcbmhc, .css-1d391kg, .css-hi6a2p, .css-1offfwp, .css-1avcm0n, .st-cz, .st-b1 {
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }

    /* Block container padding removal (so hero sits near top) */
    .block-container { padding-top: 0 !important; padding-left: 28px !important; padding-right: 28px !important; }

    /* Make headers and text lighter for contrast */
    .css-10trblm, .stMarkdown, .stText, .stButton, .css-1kyxreq {
        color: #eaf6ff !important;
    }

    /* Gallery images style */
    .stImage img { border-radius: 12px; box-shadow: 0 14px 40px rgba(0,0,0,0.45); }

    /* Ensure the components iframe is above background but below Streamlit controls */
    .stApp > div:nth-child(1) { background: transparent !important; }

    /* Mobile tweaks */
    @media (max-width: 780px){
      .block-container { padding-left: 12px !important; padding-right: 12px !important; }
    }
    </style>
    """, unsafe_allow_html=True
)

# ---------------- PAGE CONTENT (Streamlit containers) ----------------
st.markdown("---")
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 📸 Photos (Gallery)")
    images = get_gallery_images()
    if not images:
        st.info("No images found. Add files to the `gallery/` folder.")
    else:
        for i, img in enumerate(images):
            # display as modern rounded images
            st.markdown(f"<div style='margin-bottom:14px;border-radius:12px;overflow:hidden;'><img src='{img}' style='width:100%;display:block;'/></div>", unsafe_allow_html=True)
            if i >= 5:
                break
        if len(images) > 6:
            st.caption(f"Plus {len(images)-6} more — they'll appear here automatically.")

with col2:
    st.markdown("### ✍️ Writings (Anonymous)")
    if "anon_msgs" not in st.session_state:
        st.session_state.anon_msgs = []
    with st.form("anon", clear_on_submit=True):
        m = st.text_area("Write anonymously...", height=120)
        if st.form_submit_button("Send"):
            if m and m.strip():
                st.session_state.anon_msgs.insert(0, m.strip())
                st.success("Sent anonymouly — visible in this session.")
    for mm in st.session_state.anon_msgs[:8]:
        st.info(mm)

    st.markdown("---")
    st.markdown("### 📰 Blog Posts")
    posts = get_all_posts()
    if not posts:
        st.info("No blog posts found. Add `.md` files to `blog_posts/`.")
    else:
        for p in posts:
            st.subheader(p["title"])
            if p.get("date"): st.caption(p["date"])
            st.markdown(p["html"], unsafe_allow_html=True)
            st.markdown("---")

st.markdown("---")
st.info("Chat is available via the floating chat orb (bottom-right) — click it to Ask me about Aryan ☕")

st.markdown("---")
st.markdown("<a id='projects_anchor'></a>", unsafe_allow_html=True)
st.header("Projects")
st.markdown("""
<div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap:18px;">
  <div style="background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(255,255,255,0.9)); padding:14px; border-radius:12px;">
    <strong>Chatbot App</strong><div style="opacity:.8; margin-top:6px;">Client-side Q&A chatbot with personality & fallback logic.</div>
  </div>
  <div style="background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(255,255,255,0.9)); padding:14px; border-radius:12px;">
    <strong>Portfolio Website</strong><div style="opacity:.8; margin-top:6px;">This polished portfolio & blog system.</div>
  </div>
  <div style="background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(255,255,255,0.9)); padding:14px; border-radius:12px;">
    <strong>Machine Learning</strong><div style="opacity:.8; margin-top:6px;">Small experiments with models & data.</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.header("Contact")
st.write("Prefer DM on Instagram: ", "[aryanxsharma26](https://instagram.com/aryanxsharma26)")

st.markdown("---")
st.markdown("### ⚙️ Notes & Setup")
st.markdown("""
- Place `resume.pdf` at the project root so `/resume.pdf` resolves (used by the Download Resume link).
- Gallery images go in `gallery/`. Blog posts go in `blog_posts/` as `.md`.
- To adjust star density or nebula color, edit the canvas JS in the `hero_html` string above.
- If you want server-side chat logging or an LLM-backed chat, I can wire it up next.
""")
