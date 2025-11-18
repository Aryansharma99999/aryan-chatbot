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


# ---------------- HTML component: full-screen galaxy + hero + chat ----------------
# We request a tall height for the component so iframe fills the viewport; we also aggressively force iframe height using CSS below.
hero_html = r"""
<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
<style>
:root{
  --text:#eaf6ff;
  --glass: rgba(255,255,255,0.03);
}

/* ensure the component covers viewport inside iframe */
html,body{height:100%;margin:0;padding:0;overflow:hidden;font-family:Inter,system-ui;color:var(--text);}

/* canvas covers full area of component */
#galaxy-wrap{position:fixed;inset:0;z-index:0;pointer-events:none;}
canvas{width:100%;height:100%;display:block;}

/* page container holds hero centered vertically */
.page{position:relative; z-index:6; min-height:100vh; display:flex; align-items:center; justify-content:center; padding:36px; box-sizing:border-box;}

/* hero glass card */
.hero-card{
  width:85%; max-width:1100px; border-radius:18px;
  padding:44px; box-sizing:border-box;
  backdrop-filter: blur(18px) saturate(140%);
  -webkit-backdrop-filter: blur(18px) saturate(140%);
  background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
  border:1px solid rgba(255,255,255,0.04);
  box-shadow: 0 40px 110px rgba(2,6,20,0.6);
  text-align:center;
  transform: translateY(18px); opacity:0;
  transition: all .8s cubic-bezier(.2,.9,.3,1);
}
.hero-card.show { transform: translateY(0); opacity:1; }

.hero-title{ font-size:46px; font-weight:800; margin:0; color:#f3f9ff; }
.hero-sub{ margin-top:10px; font-size:18px; color:rgba(230,240,255,0.9); }
.roles{ margin-top:10px; font-weight:700; color:#d3e9ff; }

.cta{ margin-top:22px; display:flex; gap:12px; justify-content:center; align-items:center; }
.btn{ padding:10px 18px; border-radius:999px; font-weight:700; cursor:pointer; border:none; transition: transform .18s ease; }
.btn:hover{ transform: translateY(-4px); }
.btn-primary{ background: #8db3ff; color:#07182a; }
.btn-ghost{ background:transparent; color:#dfefff; border:1px solid rgba(255,255,255,0.06); }

/* floating chat orb */
.chat-orb{
  position:fixed; right:26px; bottom:28px; width:64px; height:64px; z-index:40;
  border-radius:999px; display:flex; align-items:center; justify-content:center;
  background:linear-gradient(180deg, rgba(18,20,24,0.96), rgba(12,14,18,0.96));
  box-shadow:0 28px 80px rgba(0,0,0,0.6); cursor:pointer; border:1px solid rgba(255,255,255,0.03);
}
.chat-orb:hover{ transform: translateY(-6px); }

/* dynamic island chat modal (close to orb) */
.island{
  position:fixed; right:26px; bottom:106px; width:420px; max-width:92vw; z-index:45;
  border-radius:14px; overflow:hidden; display:none;
  background: linear-gradient(180deg, rgba(8,10,14,0.96), rgba(12,14,18,0.96));
  border:1px solid rgba(255,255,255,0.04);
  box-shadow:0 30px 100px rgba(0,0,0,0.7);
}
.island.show{ display:block; animation:islandIn .22s cubic-bezier(.2,.9,.3,1); }
@keyframes islandIn{ from{ transform: translateY(8px) scale(.98); opacity:0 } to { transform:none; opacity:1 } }

.island .header{ padding:12px 14px; font-weight:700; color:#cfeeff; background:rgba(255,255,255,0.02); }
.island .body{ padding:12px; max-height:320px; overflow:auto; }
.msg{ margin:8px 0; padding:10px 12px; border-radius:12px; max-width:82%; color:#eef9ff; }
.msg.user{ background: rgba(255,255,255,0.08); color:#071827; margin-left:auto; }
.msg.bot{ background: rgba(110,140,200,0.08); }

/* island footer */
.island .footer{ padding:12px; display:flex; gap:8px; }
.chat-input{ flex:1; padding:10px 12px; border-radius:10px; border:none; background:#0f1316; color:#eaf6ff; }

/* small responsive */
@media (max-width:780px){
  .hero-title{ font-size:32px; }
  .island{ left:12px; right:12px; width:calc(100% - 24px); bottom:84px; }
}
</style>
</head>
<body>
  <div id="galaxy-wrap"><canvas id="galaxy"></canvas></div>

  <div class="page" role="main">
    <div class="hero-card" id="heroCard" aria-label="Hero">
      <h1 class="hero-title">Aryan Sharma</h1>
      <div class="hero-sub">Welcome to my personal website!</div>
      <div class="roles" id="role">tech enthusiast</div>
      <div class="cta">
        <a href="/resume.pdf#chatbot-section" class="btn btn-primary" role="button">Download Resume</a>
        <button class="btn btn-ghost" onclick="document.getElementById('projects_anchor').scrollIntoView({behavior:'smooth'})">Get In Touch</button>
      </div>
    </div>
  </div>

  <div class="chat-orb" id="chatOrb" aria-label="Ask me about Aryan">💬</div>

  <div class="island" id="island" role="dialog" aria-modal="true" aria-label="Chat with Aryan">
    <div class="header">Ask me about Aryan ☕</div>
    <div class="body" id="chatBody" aria-live="polite"></div>
    <div class="footer">
      <input id="chatInput" class="chat-input" placeholder="Type a question (e.g. Who is Aryan?)" />
      <button id="chatSend" class="btn btn-primary">Send</button>
    </div>
  </div>

<script>
/* ========== Canvas Galaxy: multi-layer + subtle nebula ========== */
(function(){
  const canvas = document.getElementById('galaxy');
  const ctx = canvas.getContext('2d');

  function resize(){
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  const layers = [
    {count:120, speed:0.18, size:[0.3,1.0], alpha:0.6},
    {count:60, speed:0.45, size:[1.2,2.2], alpha:0.9},
    {count:30, speed:1.0, size:[2.6,4.0], alpha:1.0}
  ];
  let groups = [];
  function make(){
    groups = [];
    for(const L of layers){
      const arr=[];
      for(let i=0;i<L.count;i++){
        arr.push({
          x: Math.random()*canvas.width,
          y: Math.random()*canvas.height,
          r: Math.random()*(L.size[1]-L.size[0])+L.size[0],
          vx: (Math.random()*2-1)*L.speed*0.3,
          vy: (Math.random()*2-1)*L.speed*0.3,
          a: L.alpha*(0.6 + Math.random()*0.4)
        });
      }
      groups.push(arr);
    }
  }
  make();

  let t=0, mx = canvas.width/2, my = canvas.height/2;
  window.addEventListener('mousemove', (e)=>{ mx = e.clientX; my = e.clientY; });

  function drawNebula(){
    const g = ctx.createLinearGradient(0,0,canvas.width,canvas.height);
    g.addColorStop(0,'rgba(6,10,18,0.96)');
    g.addColorStop(1,'rgba(12,14,28,0.96)');
    ctx.fillStyle = g;
    ctx.fillRect(0,0,canvas.width,canvas.height);

    const cx = canvas.width*0.68 + Math.sin(t*0.2)*120;
    const cy = canvas.height*0.28 + Math.cos(t*0.15)*80;
    const rg = ctx.createRadialGradient(cx,cy,0,cx,cy, Math.max(canvas.width,canvas.height)*0.9);
    rg.addColorStop(0, 'rgba(60,40,120,0.14)');
    rg.addColorStop(0.3, 'rgba(80,60,160,0.08)');
    rg.addColorStop(0.6, 'rgba(6,10,20,0.02)');
    ctx.globalCompositeOperation = 'lighter';
    ctx.fillStyle = rg;
    ctx.fillRect(0,0,canvas.width,canvas.height);
    ctx.globalCompositeOperation = 'source-over';
  }

  function drawStars(){
    for(let gi=0; gi<groups.length; gi++){
      const group = groups[gi];
      for(const s of group){
        const px = (mx - canvas.width/2) * (0.0005 + gi*0.001);
        const py = (my - canvas.height/2) * (0.0005 + gi*0.001);
        s.x += s.vx; s.y += s.vy;
        if(s.x < -10) s.x = canvas.width+10;
        if(s.x > canvas.width+10) s.x = -10;
        if(s.y < -10) s.y = canvas.height+10;
        if(s.y > canvas.height+10) s.y = -10;

        ctx.beginPath();
        ctx.fillStyle = 'rgba(255,255,255,' + (s.a * (0.6 + Math.sin((t+s.x+s.y)/90)*0.35)) + ')';
        ctx.arc(s.x + px*40, s.y + py*40, s.r, 0, Math.PI*2);
        ctx.fill();
      }
    }
  }

  function loop(){
    t += 0.016;
    drawNebula();
    drawStars();
    requestAnimationFrame(loop);
  }
  loop();
})();

/* ===== hero show + typewriter ===== */
window.addEventListener('DOMContentLoaded', function(){
  setTimeout(()=>document.getElementById('heroCard').classList.add('show'), 120);
  const roles = ["web developer","tech enthusiast","programmer","writer","editor"];
  let idx=0,pos=0,fw=true; const el=document.getElementById('role');
  (function tick(){
    const cur = roles[idx];
    if(fw){ pos++; el.textContent = cur.slice(0,pos); if(pos===cur.length){ fw=false; setTimeout(tick,800); return; } }
    else { pos--; el.textContent = cur.slice(0,pos); if(pos===0){ fw=true; idx=(idx+1)%roles.length; setTimeout(tick,400); return; } }
    setTimeout(tick,70);
  })();
});

/* ===== Chatbot facts (client-side) ===== */
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

/* ===== Chat logic ===== */
(function(){
  const orb = document.getElementById('chatOrb');
  const island = document.getElementById('island');
  const body = document.getElementById('chatBody');
  const input = document.getElementById('chatInput');
  const send = document.getElementById('chatSend');

  function addMsg(t, who){
    const el = document.createElement('div');
    el.className = 'msg ' + (who === 'user' ? 'user' : 'bot');
    el.textContent = t;
    body.appendChild(el);
    body.scrollTop = body.scrollHeight;
  }

  orb.addEventListener('click', () => {
    island.classList.toggle('show');
    input.focus();
    if(body.children.length === 0) addMsg("Hi! I'm Aryan's assistant — ask me anything about Aryan ☕", 'bot');
  });

  send.addEventListener('click', () =>{
    const q = (input.value||'').trim();
    if(!q) return;
    addMsg(q, 'user');
    input.value = '';
    setTimeout(()=> {
      const lq = q.toLowerCase();
      let r = null;
      for(const k in ARYAN_FACTS){
        if(lq.includes(k)) { r = ARYAN_FACTS[k]; break;}
      }
      if(!r){
        if(lq.includes('name')) r = "Aryan Sharma — that guy with stories & coffee.";
        else if(lq.includes('coffee')) r = ARYAN_FACTS["what’s aryan’s comfort drink"];
        else if(lq.includes('study')) r = ARYAN_FACTS["what is aryan currently studying"];
        else r = "Ask me anything about Aryan ☕🙂!";
      }
      addMsg(r, 'bot');
    }, 260 + Math.random()*320);
  });

  input.addEventListener('keydown', (e)=>{ if(e.key==='Enter'){ e.preventDefault(); send.click(); } });
})();
</script>
</body>
</html>
"""

# Render component with a large height so iframe tries to fill viewport; CSS below forces iframe to 100vh
components.html(hero_html, height=900, scrolling=False)

# ---------------- VERY ROBUST STREAMLIT TRANSPARENCY + FULLSCREEN override ----------------
st.markdown(
    """
    <style>
    /* Force the Streamlit app to be transparent and remove default padding so the component fills the entire viewport */
    html, body, .stApp, [data-testid="stAppViewContainer"], .block-container {
        background: transparent !important;
        background-image: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* Force any iframe (component) to be full height in the viewport */
    iframe {
        height: 100vh !important;
        min-height: 100vh !important;
        max-height: 100vh !important;
    }

    /* Target common Streamlit wrapper class patterns & remove their backgrounds */
    .css-18e3th9, .css-1lcbmhc, .css-1d391kg, .css-hi6a2p, .css-1offfwp, .css-1avcm0n,
    .st-cz, .st-b1, .stImage {
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }

    /* Remove top toolbar gap and header */
    div[data-testid="stToolbar"], header[role="banner"] { display:none !important; height:0 !important; }

    /* Block container spacing adjustments */
    .block-container { padding-top: 0 !important; padding-left: 20px !important; padding-right: 20px !important; }

    /* Text color for readability */
    .css-10trblm, .stMarkdown, .stText, .stButton { color: #eaf6ff !important; }

    /* Make images rounded and glassy */
    .stImage img { border-radius:12px !important; box-shadow: 0 14px 40px rgba(0,0,0,0.45) !important; }

    @media (max-width:780px){
      .block-container { padding-left:10px !important; padding-right:10px !important; }
      iframe { height: 100vh !important; }
    }
    </style>
    """, unsafe_allow_html=True
)

# ---------------- PAGE CONTENT (Streamlit containers below) ----------------
st.markdown("---")
col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.markdown("### 📸 Photos (Gallery)")
    images = get_gallery_images()
    if not images:
        st.info("No images found. Add files to the `gallery/` folder.")
    else:
        # modern rounded previews
        for i, img in enumerate(images[:6]):
            st.markdown(
                f"<div style='margin-bottom:14px;border-radius:12px;overflow:hidden;'><img src='{img}' style='width:100%;display:block;'/></div>",
                unsafe_allow_html=True)
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
                st.success("Sent anonymously — visible in this session.")
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
- If Streamlit still shows a white stripe in your particular Codespace, send a screenshot of the page DOM (or tell me Streamlit version) and I'll patch the selector immediately — I already covered the most common class patterns.
""")
