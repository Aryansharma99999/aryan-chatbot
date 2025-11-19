# app.py
# Ultra-Premium "Cyber-Luxury Neon Galaxy" single-file Streamlit site
# - Full-screen animated background across the whole page
# - Glowing animated hero card with moving border line
# - Parallax, rings, particle trails, typewriter roles
# - Floating chatbot (client-side Q&A using provided facts)
# - Gallery reads /gallery, blog reads /blog_posts
# - All placeholders safely injected (no % formatting issues)
# Paste this file as-is and run with Streamlit.

import os
import re
import json
import time
import streamlit as st
import streamlit.components.v1 as components
from markdown import markdown

st.set_page_config(page_title="Aryan Sharma — Cyber-Luxury", layout="wide")

# ---------------- hide Streamlit chrome & ensure transparent containers ----------------
st.markdown("""
<style>
/* hide header/menu/footer */
#MainMenu, header, footer { visibility: hidden !important; height: 0 !important; }

/* force block container full width and no padding so HTML component can control layout */
.block-container { padding: 0 !important; margin: 0 auto !important; max-width: 100% !important; }
.main { padding: 0 !important; margin: 0 !important; }
html, body { background: transparent !important; overflow-x: hidden !important; }
</style>
""", unsafe_allow_html=True)

# ---------------- Helpers: gallery & blog reading ----------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
GALLERY_DIR = os.path.join(BASE_DIR, "gallery")
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")

def get_gallery_images():
    if not os.path.exists(GALLERY_DIR):
        return []
    files = [f for f in sorted(os.listdir(GALLERY_DIR)) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif"))]
    return [os.path.join("gallery", f) for f in files]

def get_post_data(slug):
    file_path = os.path.join(POSTS_DIR, f"{slug}.md")
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as fh:
        txt = fh.read()
    meta = {}
    body = txt
    m = re.match(r'---\n(.*?)\n---', txt, re.DOTALL)
    if m:
        meta_block = m.group(1)
        for line in meta_block.splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                meta[k.strip()] = v.strip()
        body = txt[m.end():].strip()
    return {
        "slug": slug,
        "title": meta.get("title", slug.replace('-', ' ').title()),
        "date": meta.get("date", ""),
        "author": meta.get("author", ""),
        "summary": meta.get("summary", ""),
        "html": markdown(body)
    }

def get_all_posts():
    if not os.path.exists(POSTS_DIR):
        return []
    mds = [f for f in sorted(os.listdir(POSTS_DIR)) if f.endswith(".md")]
    posts = []
    for m in mds:
        p = get_post_data(m[:-3])
        if p:
            posts.append(p)
    return posts

# ---------------- Chat facts (client-side) ----------------
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
    "what’s something aryan can't live without": "Coffee. None 😅.",
    "what makes aryan unique": "His ability to make people laugh even when he’s not trying.",
    "what’s aryan’s favorite weather": "Cold breeze + warm coffee = perfection.",
    "how does aryan relax": "Storytelling, music, and wandering thoughts.",
    "what is aryan passionate about": "Tech, creativity, and turning ideas into reality.",
    "what is aryan learning right now": "New tech skills… one coffee at a time.",
    "what type of person is aryan": "Calm, humorous, and secretly a deep thinker.",
    "what’s aryan’s favourite thing to do": "Observe life and turn it into funny, relatable stories.",
    "what does aryan dream about": "A life full of learning, creativity, and a never-ending coffee supply."
}

facts_json = json.dumps(ARYAN_FACTS)

# ---------------- Build gallery HTML safely ----------------
gallery_images = get_gallery_images()
if gallery_images:
    gallery_html = ""
    for i, src in enumerate(gallery_images):
        alt = os.path.basename(src)
        # Note: using simple img tag; Streamlit serves files from local folder when path is relative
        gallery_html += f'<div class="gallery-item"><img src="{src}" alt="{alt}" loading="lazy"/></div>\n'
else:
    gallery_html = '<div class="empty">No images found in <code>gallery/</code></div>'

# ---------------- Build posts HTML safely ----------------
posts = get_all_posts()
if posts:
    posts_html = ""
    for p in posts:
        title = p["title"]
        date = p.get("date", "")
        html_body = p["html"]
        posts_html += f'''
        <article class="post-card">
          <h3 class="post-title">{title}</h3>
          <div class="post-meta">{date}</div>
          <div class="post-body">{html_body}</div>
        </article>
        '''
else:
    posts_html = '<div class="empty">No blog posts in <code>blog_posts/</code></div>'

# ---------------- Social links ----------------
linkedin = "https://www.linkedin.com/in/aryan-sharma99999"
instagram = "https://instagram.com/aryanxsharma26"
year_str = str(time.localtime().tm_year)

# ---------------- HTML TEMPLATE (placeholders used) ----------------
html_template = """
<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Aryan Sharma — Cyber-Luxury</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
<style>
:root{
  --bg0: #03000a;
  --nebula1: rgba(140,40,200,0.12);
  --nebula2: rgba(60,120,255,0.06);
  --glass: rgba(255,255,255,0.03);
  --accent1: #c56cff;
  --accent2: #5ef3ff;
  --muted: rgba(220,230,255,0.85);
}

/* reset */
*{box-sizing:border-box}
html,body{height:100%;margin:0;padding:0;background:var(--bg0);font-family:Inter,system-ui,-apple-system,'Segoe UI',Roboto;color:var(--muted);-webkit-font-smoothing:antialiased}

/* full canvas layers */
#canvas-wrap { position:fixed; inset:0; z-index:-4; pointer-events:none; }
.nebula-layer { position:fixed; inset:0; z-index:-3; pointer-events:none; background:
    radial-gradient(ellipse at 70% 30%, var(--nebula1), transparent 15%),
    radial-gradient(ellipse at 20% 80%, var(--nebula2), transparent 18%); opacity:0.95; }
.starfield { position:fixed; inset:0; z-index:-2; background-image: radial-gradient(#fff 1px, transparent 1px); background-size:6px 6px; opacity:0.12; pointer-events:none; }

/* navbar */
.navbar { position:fixed; top:18px; left:50%; transform:translateX(-50%); z-index:70; display:flex; gap:12px; padding:8px 14px; border-radius:999px; backdrop-filter: blur(8px) saturate(120%); background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); border:1px solid rgba(255,255,255,0.03); }
.brand { font-weight:900; letter-spacing:1px; color:#f6ecff; padding-right:10px; }
.nav-item { color:var(--muted); padding:8px 10px; border-radius:8px; cursor:pointer; font-weight:700; opacity:0.95 }
.nav-item:hover { background: rgba(255,255,255,0.02); transform:translateY(-3px); }

/* layout container */
.container { width:100%; max-width:1180px; margin:0 auto; padding:0 24px; }

/* HERO */
.hero { height:100vh; display:flex; align-items:center; justify-content:center; }
.hero-card { width:92%; max-width:1060px; border-radius:20px; padding:56px 48px; text-align:center; position:relative; overflow:hidden; background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); border:1px solid rgba(255,255,255,0.03); box-shadow: 0 40px 120px rgba(6,6,12,0.7); backdrop-filter: blur(12px) saturate(140%); }

/* animated neon border using pseudo element */
.hero-card:before{
  content:""; position:absolute; inset:-3px; border-radius:22px; padding:3px; z-index:0;
  background: linear-gradient(90deg, rgba(197,108,255,0.0), var(--accent1), var(--accent2), var(--accent1), rgba(197,108,255,0.0));
  background-size:400% 400%;
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  animation: borderFlow 6s linear infinite;
  box-shadow: 0 14px 80px rgba(120,40,180,0.12) inset;
}
@keyframes borderFlow { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }

.rings { position:absolute; left:50%; top:20%; transform:translateX(-50%); z-index:0; pointer-events:none; filter: blur(12px); opacity:0.7; }
.ring { width:820px; height:420px; border-radius:50%; border:1px solid rgba(140,80,200,0.06); box-shadow: inset 0 0 120px rgba(140,80,200,0.02); animation: floaty 18s ease-in-out infinite; }
.ring.r2 { width:1060px; height:520px; animation-duration:26s; opacity:0.55; filter: blur(20px) saturate(120%); }
@keyframes floaty { 0%{transform:translate(-50%,-3%) scale(1)} 50%{transform:translate(-50%,3%) scale(1.01)} 100%{transform:translate(-50%,-3%) scale(1)} }

.hero-title { font-size:56px; font-weight:900; margin:0; z-index:2; background:linear-gradient(90deg,var(--accent1),var(--accent2)); -webkit-background-clip:text; color:transparent; }
.hero-sub { margin-top:12px; color:rgba(230,230,255,0.9); z-index:2; }
.typewriter { margin-top:12px; font-weight:800; color:#ffdff8; z-index:2; }

/* CTA */
.cta { margin-top:20px; display:flex; gap:12px; justify-content:center; align-items:center; z-index:2; }

/* PAGE BODY */
.page-body { padding:64px 24px 140px; background:transparent; }

/* grid layout */
.grid { display:grid; grid-template-columns: 1fr 1fr; gap:28px; align-items:start; max-width:1180px; margin:0 auto; }

/* glass card */
.card { background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); padding:18px; border-radius:12px; border:1px solid rgba(255,255,255,0.03); box-shadow: 0 14px 40px rgba(6,6,15,0.5); }

/* gallery */
.gallery { display:grid; grid-template-columns: 1fr 1fr; gap:10px; }
.gallery-item img { width:100%; height:150px; object-fit:cover; border-radius:8px; transition: transform .25s ease; }
.gallery-item img:hover { transform:scale(1.04); filter: drop-shadow(0 18px 40px rgba(120,40,180,0.18)); }

/* posts */
.post-card { margin-bottom:14px; padding:12px; border-radius:10px; background: linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.005)); border:1px solid rgba(255,255,255,0.02); }
.post-title { margin:0; font-weight:800; color:#f3eaff; }
.post-meta { color:#cfc7e8; font-size:13px; margin-bottom:8px; }

/* floating chat orb */
.chat-orb { position:fixed; right:26px; bottom:28px; width:72px; height:72px; border-radius:999px; display:flex; align-items:center; justify-content:center; z-index:80; background:linear-gradient(90deg,var(--accent1),var(--accent2)); color:#07030a; font-weight:900; box-shadow: 0 30px 90px rgba(120,40,180,0.18); cursor:pointer; }

/* chat popup */
.chat-popup { position:fixed; right:26px; bottom:110px; width:380px; max-width:92vw; border-radius:12px; overflow:hidden; display:none; z-index:90; box-shadow: 0 30px 80px rgba(2,2,8,0.6); border:1px solid rgba(255,255,255,0.03); }
.chat-head { padding:12px; background: linear-gradient(90deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); color:#eaf8ff; font-weight:800; }
.chat-body { padding:12px; max-height:260px; overflow:auto; background: linear-gradient(180deg, rgba(6,6,8,0.98), rgba(8,8,10,0.98)); color:var(--muted); }
.chat-row { padding:12px; display:flex; gap:8px; background: linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.007)); }

/* footer */
.footer { padding:40px 20px; text-align:center; color:#d7d2ea; }

@media (max-width:920px){
  .grid { grid-template-columns: 1fr; }
  .hero-title { font-size:40px; }
  .gallery-item img { height:100px; }
  .hero-card { padding:28px; }
}
</style>
</head>
<body>

<div id="canvas-wrap">
  <div class="nebula-layer" aria-hidden="true"></div>
  <div class="starfield" aria-hidden="true"></div>
</div>

<!-- NAV -->
<div class="navbar container" role="navigation" aria-label="main-nav">
  <div class="brand">ARYAN</div>
  <div class="nav-item" onclick="scrollToId('hero')">Home</div>
  <div class="nav-item" onclick="scrollToId('gallery')">Gallery</div>
  <div class="nav-item" onclick="scrollToId('writings')">Writings</div>
  <div class="nav-item" onclick="scrollToId('blog')">Blog</div>
  <div class="nav-item" onclick="scrollToId('projects')">Projects</div>
</div>

<!-- HERO -->
<section id="hero" class="hero" aria-label="hero">
  <div class="hero-card container" role="region" aria-labelledby="hero-title">
    <div class="rings" aria-hidden="true">
      <div class="ring"></div>
      <div class="ring r2"></div>
    </div>

    <h1 class="hero-title" id="hero-title">ARYAN SHARMA</h1>
    <div class="hero-sub">Crafting ideas into code, stories and experiences.</div>
    <div class="typewriter">I'm a <span id="role">web developer</span></div>

    <div class="cta">
      <a class="btn btn-primary" href="/resume.pdf" target="_blank" rel="noreferrer">Download Resume</a>
      <a class="btn" href="__LINKEDIN__" target="_blank" rel="noreferrer">LinkedIn</a>
      <a class="btn" href="__INSTAGRAM__" target="_blank" rel="noreferrer">Instagram</a>
    </div>

  </div>
</section>

<!-- PAGE BODY -->
<section class="page-body" id="content" aria-label="content">
  <div class="grid container">

    <div>
      <div class="card" id="gallery" role="region" aria-label="gallery">
        <h3 style="margin-top:0">📸 Photos (Gallery)</h3>
        <div class="gallery">
          __GALLERY_HTML__
        </div>
      </div>

      <div style="height:20px"></div>

      <div class="card" id="projects" role="region" aria-label="projects">
        <h3 style="margin-top:0">🧩 Projects</h3>
        <div style="display:flex;flex-direction:column;gap:10px;">
          <div style="padding:12px;border-radius:8px;background:rgba(255,255,255,0.01);font-weight:700">Chatbot Website <div style="font-weight:400;font-size:13px;opacity:0.8">Client Q&A demo</div></div>
          <div style="padding:12px;border-radius:8px;background:rgba(255,255,255,0.01);font-weight:700">Portfolio Builder <div style="font-weight:400;font-size:13px;opacity:0.8">Template & theme</div></div>
          <div style="padding:12px;border-radius:8px;background:rgba(255,255,255,0.01);font-weight:700">AI Experiments <div style="font-weight:400;font-size:13px;opacity:0.8">Small ML projects</div></div>
        </div>
      </div>
    </div>

    <div>
      <div class="card" id="writings" role="region" aria-label="writings">
        <h3 style="margin-top:0">✍️ Writings (anonymous)</h3>
        <div id="anonList" class="empty">No anonymous writings yet.</div>
      </div>

      <div style="height:20px"></div>

      <div class="card" id="blog" role="region" aria-label="blog">
        <h3 style="margin-top:0">📰 Blog Posts</h3>
        __POSTS_HTML__
      </div>
    </div>
  </div>

  <div style="height:36px"></div>

  <div class="card container" style="max-width:1180px;">
    <h3 style="margin-top:0">Contact</h3>
    <p>Connect on <a href="__LINKEDIN__" target="_blank">LinkedIn</a> or <a href="__INSTAGRAM__" target="_blank">Instagram</a>.</p>
  </div>
</section>

<footer class="footer">© __YEAR__ Aryan Sharma • Built with ❤️</footer>

<!-- Chat orb and popup -->
<div class="chat-orb" id="chatOrb" title="Ask me about Aryan">✦</div>

<div class="chat-popup" id="chatPopup" aria-hidden="true" role="dialog">
  <div class="chat-head">Ask me about Aryan ☕ <button id="closeChat" style="float:right;background:transparent;border:none;color:#9fbde8;cursor:pointer">✕</button></div>
  <div class="chat-body" id="chatBody"></div>
  <div class="chat-row">
    <input id="chatInput" placeholder="Type a question..." style="flex:1;padding:10px;border-radius:8px;border:1px solid rgba(255,255,255,0.04);background:#0b0b10;color:var(--muted)" />
    <button id="chatSend" style="padding:10px 12px;border-radius:8px;border:none;background:linear-gradient(90deg,var(--accent1),var(--accent2));font-weight:800;color:#071026;cursor:pointer">Send</button>
  </div>
</div>

<script>
/* Safe scroll helper */
function scrollToId(id){
  const el = document.getElementById(id);
  if(!el) return;
  const top = el.getBoundingClientRect().top + window.scrollY - 72;
  window.scrollTo({ top: top, behavior: 'smooth' });
}

/* Typewriter animation */
(function(){
  const words = ["web developer","tech enthusiast","video editor","writer","learner"];
  let idx = 0, pos = 0, forward = true;
  const el = document.getElementById('role');
  function tick(){
    const cur = words[idx];
    if(forward){
      pos++; el.textContent = cur.slice(0,pos);
      if(pos === cur.length){ forward=false; setTimeout(tick,900); return; }
    } else {
      pos--; el.textContent = cur.slice(0,pos);
      if(pos === 0){ forward=true; idx=(idx+1)%words.length; setTimeout(tick,400); return; }
    }
    setTimeout(tick,70);
  }
  tick();
})();

/* Chat client-side simple Q&A (FACTS injected) */
const ARYAN_FACTS = __FACTS__;

/* Chat UI */
const orb = document.getElementById('chatOrb');
const popup = document.getElementById('chatPopup');
const body = document.getElementById('chatBody');
const input = document.getElementById('chatInput');
const send = document.getElementById('chatSend');
const closeBtn = document.getElementById('closeChat');

function addMsg(text, who){
  const el = document.createElement('div');
  el.style.margin = '8px 0';
  el.style.padding = '8px';
  el.style.borderRadius = '10px';
  if(who === 'user'){ el.style.textAlign = 'right'; el.style.background = 'rgba(255,255,255,0.06)'; el.style.color = '#fff'; el.innerText = text; }
  else { el.style.textAlign = 'left'; el.style.background = 'linear-gradient(90deg, rgba(120,120,255,0.06), rgba(140,60,200,0.03))'; el.style.color = '#eaf6ff'; el.innerText = text; }
  body.appendChild(el);
  body.scrollTop = body.scrollHeight;
}

orb.addEventListener('click', ()=>{
  popup.style.display = popup.style.display === 'block' ? 'none' : 'block';
  if(popup.style.display === 'block' && body.children.length === 0) addMsg("Hi — I'm Aryan's assistant ☕ Ask me anything about Aryan.");
  input.focus();
});
closeBtn.addEventListener('click', ()=> popup.style.display = 'none');

send.addEventListener('click', ()=>{
  const q = (input.value || '').trim();
  if(!q) return;
  addMsg(q, 'user');
  input.value = '';
  setTimeout(()=> {
    const lq = q.toLowerCase();
    let out = null;
    for(const k in ARYAN_FACTS){
      if(lq.includes(k)) { out = ARYAN_FACTS[k]; break; }
    }
    if(!out){
      if(lq.includes('name')) out = "Aryan Sharma — that guy who turns everyday moments into funny stories.";
      else if(lq.includes('coffee')) out = ARYAN_FACTS["what’s aryan’s comfort drink"] || "Coffee ☕";
      else out = "Ask me anything about Aryan ☕🙂!";
    }
    addMsg(out, 'bot');
  }, 300 + Math.random()*450);
});
input.addEventListener('keydown', (e)=> { if(e.key === 'Enter'){ e.preventDefault(); send.click(); } });

/* Lightbox for gallery images */
document.querySelectorAll('.gallery-item img').forEach(img=>{
  img.style.cursor = 'zoom-in';
  img.addEventListener('click', ()=>{
    const overlay = document.createElement('div');
    overlay.style.position = 'fixed'; overlay.style.inset = 0; overlay.style.background = 'rgba(0,0,0,0.88)';
    overlay.style.display = 'flex'; overlay.style.alignItems = 'center'; overlay.style.justifyContent = 'center'; overlay.style.zIndex = 9999;
    const big = document.createElement('img'); big.src = img.src; big.style.maxWidth = '92%'; big.style.maxHeight = '92%'; big.style.borderRadius = '10px';
    overlay.appendChild(big);
    overlay.addEventListener('click', ()=> document.body.removeChild(overlay));
    document.body.appendChild(overlay);
  });
});
</script>
</body>
</html>
"""

# ---------------- Safe replacements (avoid %-formatting) ----------------
html = html_template.replace("__GALLERY_HTML__", gallery_html)
html = html.replace("__POSTS_HTML__", posts_html)
html = html.replace("__LINKEDIN__", linkedin)
html = html.replace("__INSTAGRAM__", instagram)
html = html.replace("__YEAR__", year_str)
html = html.replace("__FACTS__", facts_json)

# ---------------- Render component ----------------
# Use a tall height but enable scrolling inside the component so the page behaves normally.
components.html(html, height=960, scrolling=True)

# ---------------- Optional admin sidebar (small helpers) ----------------
with st.sidebar.expander("Admin: Quick tips", expanded=True):
    st.write("• Add images to `gallery/` (jpg/png/webp/gif) to populate the gallery.")
    st.write("• Add blog posts as `.md` files in `blog_posts/` (optional YAML frontmatter).")
    st.write("• The chat uses local client-side rules. Tell me if you want OpenAI integration.")
