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


# ---------------- CLIENT-SIDE Q&A ----------------
# (twenty facts you provided, kept client-side for instant chat)
ARYAN_FACTS = {
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
}


# ---------------- HTML component: full-page galaxy + hero + chat ----------------
hero_html = r"""
<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
<style>
:root{
  --text: #eaf6ff;
  --glass: rgba(255,255,255,0.04);
  --card-glow: rgba(120,150,255,0.06);
  --accent: #8db3ff;
}

/* component fills iframe */
html,body{height:100%;margin:0;padding:0;overflow:hidden;font-family:Inter,system-ui;color:var(--text);}

/* galaxy canvas full area */
#galaxy-wrap{position:fixed;inset:0;z-index:0;pointer-events:none;}
#galaxy{width:100%;height:100%;display:block;}

/* content container sits above canvas */
.page{position:relative;z-index:6;min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:36px 24px;box-sizing:border-box;}

/* hero */
.hero-card{
  width:92%; max-width:1100px; border-radius:16px;
  padding:40px; box-sizing:border-box;
  backdrop-filter: blur(16px) saturate(140%);
  -webkit-backdrop-filter: blur(16px) saturate(140%);
  background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
  border:1px solid rgba(255,255,255,0.035);
  box-shadow: 0 40px 100px rgba(2,6,20,0.55);
  text-align:center; margin-bottom:48px;
  transform: translateY(18px); opacity:0; transition:all .7s ease-out;
}
.hero-card.show{ transform:none; opacity:1; }
.hero-title{ font-size:46px; font-weight:800; margin:0; color:#e9f6ff; }
.hero-sub{ margin-top:10px; font-size:18px; color:rgba(230,240,255,0.95); }
.roles{ font-weight:700; color:#d2e8ff; margin-top:10px; }

/* CTA */
.cta{ margin-top:22px; display:flex; justify-content:center; gap:12px; }
.btn{ padding:10px 18px; border-radius:999px; font-weight:700; cursor:pointer; border:none; }
.btn-primary{ background:var(--accent); color:#071827; box-shadow: 0 8px 26px rgba(20,40,80,0.18); }
.btn-ghost{ background:transparent; color:#dfefff; border:1px solid rgba(255,255,255,0.06); }

/* main layout for below-hero content */
.content-grid{ width:100%; max-width:1200px; display:grid; grid-template-columns: 320px 1fr; gap:34px; align-items:start; box-sizing:border-box; padding-bottom:80px; }

/* left column gallery (vertical grid of small cards) */
.gallery-col{ display:flex; flex-direction:column; gap:12px; align-items:flex-start; }
.gallery-card{
  width:100%; border-radius:12px; overflow:hidden; background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
  border: 1px solid rgba(255,255,255,0.04);
  box-shadow: 0 12px 30px rgba(2,6,20,0.45); padding:8px;
}

/* right column main sections (writings, posts) will be glass cards */
.section-card{
  background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
  border: 1px solid rgba(255,255,255,0.04);
  box-shadow: 0 14px 40px rgba(2,6,20,0.4);
  padding:18px; border-radius:12px; margin-bottom:24px;
}

/* gallery grid (inside left column card) */
.gallery-grid{ display:grid; grid-template-columns: repeat(2, 1fr); gap:10px; }
.gallery-grid .img { border-radius:10px; overflow:hidden; box-shadow: 0 10px 28px rgba(2,6,20,0.35); }

/* blog post title */
.post-title{ margin:8px 0 6px 0; color:#eaf6ff; font-weight:700; font-size:22px; }

/* small helpers */
.section-h { font-size:20px; font-weight:700; color:#d4ecff; margin-bottom:12px; display:flex; align-items:center; gap:8px; }

/* floating chat orb (global) */
.chat-orb{
  position:fixed; right:26px; bottom:28px; width:64px; height:64px; z-index:60;
  border-radius:999px; display:flex; align-items:center; justify-content:center;
  background:linear-gradient(180deg, rgba(16,18,22,0.96), rgba(10,12,16,0.96));
  box-shadow:0 32px 90px rgba(0,0,0,0.6); cursor:pointer; border:1px solid rgba(255,255,255,0.03);
}
.chat-orb:hover{ transform: translateY(-6px); }

/* island chat */
.island{ position:fixed; right:26px; bottom:106px; width:420px; max-width:92vw; z-index:70; border-radius:14px; display:none; }
.island.show{ display:block; }
.island .inner{ background: linear-gradient(180deg, rgba(8,10,14,0.96), rgba(12,14,18,0.96)); border:1px solid rgba(255,255,255,0.03); padding:0; border-radius:14px; box-shadow:0 30px 100px rgba(0,0,0,0.7); overflow:hidden;}
.island .header{ padding:12px 14px; font-weight:700; color:#cfeeff; background: rgba(255,255,255,0.02); }
.island .body{ padding:12px; max-height:300px; overflow:auto; color:#eaf6ff; }
.island .footer{ padding:12px; display:flex; gap:8px; }
.chat-input{ flex:1; padding:10px 12px; border-radius:10px; border:none; background:#0d1114; color:#eaf6ff; }

/* responsive */
@media (max-width:980px){
  .content-grid{ grid-template-columns: 1fr; }
  .gallery-col{ order:2; width:100%; display:flex; }
  .hero-card{ margin-bottom:28px; }
  .gallery-grid{ grid-template-columns: repeat(3,1fr); }
}
@media (max-width:520px){
  .gallery-grid{ grid-template-columns: repeat(2,1fr); }
  .hero-title{ font-size:28px; }
}
</style>
</head>
<body>
  <div id="galaxy-wrap"><canvas id="galaxy"></canvas></div>

  <div class="page" role="main" aria-label="Main content">
    <div class="hero-card" id="heroCard" role="banner">
      <h1 class="hero-title">Aryan Sharma</h1>
      <div class="hero-sub">Welcome to my personal website!</div>
      <div class="roles" id="role">tech enthusiast</div>
      <div class="cta">
        <a class="btn btn-primary" href="/resume.pdf#chatbot-section" role="button">Download Resume</a>
        <button class="btn btn-ghost" onclick="document.getElementById('projects').scrollIntoView({behavior:'smooth'})">Get In Touch</button>
      </div>
    </div>

    <div class="content-grid" role="region" aria-label="Main sections">
      <div class="gallery-col" aria-label="Photos gallery">
        <div class="gallery-card section-card" style="margin-bottom:12px;">
          <div class="section-h">📸 Photos (Gallery)</div>
          <div class="gallery-grid" id="galleryGrid">
            <!-- images injected by JS -->
          </div>
        </div>
      </div>

      <div class="main-col">
        <div class="section-card" aria-label="Writings">
          <div class="section-h">✍️ Writings (Anonymous)</div>
          <div id="writingsBox">
            <!-- simple form handled by Streamlit; placeholder -->
            <div style="padding:6px;color:rgba(230,240,255,0.85)">This area is managed by Streamlit. Use the form below to post anonymously.</div>
          </div>
        </div>

        <div class="section-card" aria-label="Blog posts">
          <div class="section-h">📰 Blog Posts</div>
          <div id="postsBox">
            <!-- posts filled from Streamlit below (HTML sync) -->
            <div style="padding:6px;color:rgba(200,220,255,0.85)">Posts are rendered below by Streamlit; they appear inside frosted cards.</div>
          </div>
        </div>

        <div id="projects" style="height:10px;"></div>
      </div>
    </div>
  </div>

  <div class="chat-orb" id="chatOrb" aria-label="Ask me about Aryan">💬</div>

  <div class="island" id="island" aria-hidden="true">
    <div class="inner" role="dialog" aria-label="Chat dialog">
      <div class="header">Ask me about Aryan ☕</div>
      <div class="body" id="chatBody" aria-live="polite"></div>
      <div class="footer">
        <input id="chatInput" class="chat-input" placeholder="Who is Aryan?" />
        <button id="chatSend" class="btn btn-primary">Send</button>
      </div>
    </div>
  </div>

<script>
/* ============ Galaxy canvas (depth layers + nebula) ============ */
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
    {count:120, speed:0.18, size:[0.3,0.9], alpha:0.6},
    {count:60, speed:0.5, size:[1.2,2.2], alpha:0.9},
    {count:30, speed:1.1, size:[2.8,4.0], alpha:1.0},
  ];
  let groups = [];
  function make(){
    groups = [];
    for(const L of layers){
      const arr = [];
      for(let i=0;i<L.count;i++){
        arr.push({
          x: Math.random()*canvas.width,
          y: Math.random()*canvas.height,
          r: Math.random()*(L.size[1]-L.size[0]) + L.size[0],
          vx: (Math.random()*2-1)*L.speed*0.4,
          vy: (Math.random()*2-1)*L.speed*0.4,
          a: L.alpha*(0.6 + Math.random()*0.4)
        });
      }
      groups.push(arr);
    }
  }
  make();

  let t=0, mx=canvas.width/2, my=canvas.height/2;
  window.addEventListener('mousemove', (e)=>{ mx=e.clientX; my=e.clientY; });

  function drawNebula(){
    const g = ctx.createLinearGradient(0,0,canvas.width,canvas.height);
    g.addColorStop(0,'rgba(6,10,18,0.96)');
    g.addColorStop(1,'rgba(12,14,28,0.96)');
    ctx.fillStyle = g;
    ctx.fillRect(0,0,canvas.width,canvas.height);

    const cx = canvas.width*0.68 + Math.sin(t*0.2)*120;
    const cy = canvas.height*0.28 + Math.cos(t*0.15)*80;
    const rg = ctx.createRadialGradient(cx,cy,0,cx,cy, Math.max(canvas.width,canvas.height)*0.9);
    rg.addColorStop(0, 'rgba(60,40,120,0.13)');
    rg.addColorStop(0.3, 'rgba(80,60,160,0.07)');
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
        s.x += s.vx;
        s.y += s.vy;
        if(s.x < -10) s.x = canvas.width+10;
        if(s.x > canvas.width+10) s.x = -10;
        if(s.y < -10) s.y = canvas.height+10;
        if(s.y > canvas.height+10) s.y = -10;

        ctx.beginPath();
        ctx.fillStyle = 'rgba(255,255,255,' + (s.a * (0.6 + Math.sin((t + s.x + s.y)/90)*0.35)) + ')';
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

/* ============ Hero show + typewriter ============ */
document.addEventListener('DOMContentLoaded', function(){
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

/* ============ Fill gallery grid from Streamlit-inserted global var (or fallback) ============ */
(function(){
  // Streamlit will include the image URLs in a global variable later via inserted script below.
  function populate(urls){
    const grid = document.getElementById('galleryGrid');
    grid.innerHTML = '';
    if(!urls || !urls.length){
      // placeholder empty state
      grid.innerHTML = "<div style='grid-column:1/-1;color:rgba(200,220,255,0.6);font-size:14px;padding:8px;'>No images found. Add images to the gallery/ folder.</div>";
      return;
    }
    for(const u of urls){
      const d = document.createElement('div');
      d.className = 'img';
      d.innerHTML = "<img src='"+u+"' style='width:100%;height:100%;object-fit:cover;display:block;'/>";
      grid.appendChild(d);
    }
  }

  // If Streamlit sets window.ST_GALLERY_URLS, use it; otherwise wait briefly.
  if(window.ST_GALLERY_URLS){
    populate(window.ST_GALLERY_URLS);
  } else {
    // try a few times (Streamlit will inject afterwards)
    let i=0;
    const iv = setInterval(()=>{
      if(window.ST_GALLERY_URLS){ populate(window.ST_GALLERY_URLS); clearInterval(iv); }
      i++; if(i>20) { populate([]); clearInterval(iv); }
    }, 150);
  }
})();

/* ============ Chat logic (client-side, local Q&A) ============ */
(function(){
  const orb = document.getElementById('chatOrb');
  const island = document.getElementById('island');
  const body = document.getElementById('chatBody');
  const input = document.getElementById('chatInput');
  const send = document.getElementById('chatSend');

  function addMsg(text, who){
    const el = document.createElement('div');
    el.className = 'msg ' + (who === 'user' ? 'user' : 'bot');
    el.textContent = text;
    body.appendChild(el);
    body.scrollTop = body.scrollHeight;
  }

  orb.addEventListener('click', ()=>{
    const show = island.classList.toggle('show');
    island.setAttribute('aria-hidden', show ? 'false' : 'true');
    input.focus();
    if(body.children.length === 0) addMsg("Hi — I'm Aryan's assistant. Ask me about Aryan ☕", 'bot');
  });

  send.addEventListener('click', ()=>{
    const q = (input.value || '').trim();
    if(!q) return;
    addMsg(q, 'user');
    input.value = '';
    setTimeout(()=>{
      const lq = q.toLowerCase();
      // prefer keys with contains check
      let out = null;
      for(const k in window.ST_ARYAN_FACTS || {}){
        if(lq.includes(k)) { out = window.ST_ARYAN_FACTS[k]; break; }
      }
      // fallback keywords
      if(!out){
        if(lq.includes('name')) out = "Aryan Sharma — the guy with stories & coffee.";
        else if(lq.includes('coffee')) out = (window.ST_ARYAN_FACTS && window.ST_ARYAN_FACTS["what’s aryan’s comfort drink"]) || "Coffee ☕";
        else if(lq.includes('study')) out = (window.ST_ARYAN_FACTS && window.ST_ARYAN_FACTS["what is aryan currently studying"]) || "Pursuing a Bachelor's degree.";
        else out = "Ask me anything about Aryan ☕🙂!";
      }
      addMsg(out, 'bot');
    }, 260 + Math.random()*420);
  });

  input.addEventListener('keydown', (e)=>{ if(e.key === 'Enter'){ e.preventDefault(); send.click(); }});
})();
</script>
</body>
</html>
"""

# Render the component; request large height so iframe tries to be full viewport.
components.html(hero_html, height=900, scrolling=False)


# ---------------- VERY AGGRESSIVE STREAMLIT TRANSPARENCY & FULL-PAGE OVERRIDES ----------------
# This CSS attempts to cover many Streamlit DOM versions and force the component to be the visible page background.
st.markdown(
    """
    <style>
    /* Make the app background transparent so our canvas shows through globally */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] > div, section.main, .block-container {
        background: transparent !important;
        background-image: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* Force the component iframe to occupy full viewport height */
    iframe {
        height: 100vh !important;
        min-height: 100vh !important;
        max-height: 100vh !important;
    }

    /* Neutralize common Streamlit wrapper boxes so glass cards look right */
    .css-18e3th9, .css-1lcbmhc, .css-1d391kg, .css-hi6a2p, .css-1offfwp, .css-1avcm0n,
    .st-cz, .st-b1, .stImage {
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }

    /* Hide the top toolbar and header that create a white strip */
    div[data-testid="stToolbar"], header[role="banner"] { display:none !important; height:0 !important; }

    /* Block container spacing adjustments */
    .block-container { padding-top: 0 !important; padding-left: 20px !important; padding-right: 20px !important; }

    /* Make Streamlit text readable on galaxy */
    .css-10trblm, .stMarkdown, .stText, .stButton { color: #eaf6ff !important; }

    /* Make images (Streamlit-rendered) rounded and glassy */
    .stImage img { border-radius:12px !important; box-shadow: 0 14px 40px rgba(0,0,0,0.45) !important; }

    /* Adjust scrollbars lightly for style */
    ::-webkit-scrollbar { height:10px; width:10px; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.06); border-radius:10px; }
    ::-webkit-scrollbar-track { background: transparent; }

    @media (max-width:780px){
      .block-container { padding-left: 10px !important; padding-right: 10px !important; }
      iframe { height: 100vh !important; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- STREAMLIT PAGE CONTENT BELOW (glass cards) ----------------
st.markdown("---")
col1, col2 = st.columns([1, 2], gap="large")

# Left column: photos (we will pass URLs to the JS component via a small script)
with col1:
    st.markdown("### 📸 Photos (Gallery)")
    images = get_gallery_images()
    if not images:
        st.info("No images found. Add files to the `gallery/` folder.")
    else:
        # show small previews as glass cards (these are also separately injected into the HTML gallery grid)
        for i, img in enumerate(images[:6]):
            st.markdown(
                f"<div style='border-radius:12px;overflow:hidden;margin-bottom:12px;'><img src='{img}' style='width:100%;display:block;border-radius:12px;object-fit:cover;'/></div>",
                unsafe_allow_html=True)
        if len(images) > 6:
            st.caption(f"Plus {len(images)-6} more — they'll appear here automatically.")

# Right column: writings + blog posts
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
            st.markdown(f"<div style='background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); padding:18px; border-radius:12px; border:1px solid rgba(255,255,255,0.04); box-shadow:0 14px 40px rgba(2,6,20,0.35); margin-bottom:18px;'>", unsafe_allow_html=True)
            st.subheader(p["title"])
            if p.get("date"): st.caption(p["date"])
            st.markdown(p["html"], unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.info("Chat is available via the floating chat orb (bottom-right) — click it to Ask me about Aryan ☕")

st.markdown("---")
st.markdown("<a id='projects'></a>", unsafe_allow_html=True)
st.header("Projects")
st.markdown("""
<div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap:18px;">
  <div style="background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); padding:14px; border-radius:12px;">
    <strong>Chatbot App</strong><div style="opacity:.85; margin-top:6px;">Client-side Q&A chatbot with personality & fallback logic.</div>
  </div>
  <div style="background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); padding:14px; border-radius:12px;">
    <strong>Portfolio Website</strong><div style="opacity:.85; margin-top:6px;">Polished portfolio & blog system with glass UI.</div>
  </div>
  <div style="background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); padding:14px; border-radius:12px;">
    <strong>AI Experiments</strong><div style="opacity:.85; margin-top:6px;">Small experiments with models & data.</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.header("Contact")
st.write("Prefer DM on Instagram: ", "[aryanxsharma26](https://instagram.com/aryanxsharma26)")

# ---------------- Inject the gallery image URLs and facts into the page JS ----------------
images = get_gallery_images()
# convert to absolute-ish paths that the browser can fetch - Streamlit serves from project root
# When running in some environments, relative paths like 'gallery/x.jpg' should load automatically.
js_gallery = "window.ST_GALLERY_URLS = " + str(images) + ";"
js_facts = "window.ST_ARYAN_FACTS = " + str(ARYAN_FACTS) + ";"

st.markdown(f"<script>{js_gallery}\n{js_facts}</script>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("### ⚙️ Notes & Setup")
st.markdown("""
- Put `resume.pdf` at the project root so the Download Resume link works.
- Put images inside the `gallery/` folder and markdown posts in `blog_posts/`.
- If you see any tiny white strip in your Codespace, send a screenshot: Streamlit can generate additional wrapper classes depending on version — I'll patch that selector quickly (I've already included many common ones).
- Want me to add a top navigation bar, theme switch or animate project cards next? Say the word.
""")
