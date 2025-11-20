# app.py
# Version 1A — Ultra-Premium Purple–Pink Neon (FULLSCREEN, section-based)
# Single-file Streamlit app that injects a full-screen HTML/CSS/JS site via components.html.
# - Fullscreen sections (hero, gallery, writings, blog, projects, contact)
# - Animated nebula/particles background
# - Glowing hero border with flowing line
# - Typewriter roles + floating chat orb with local Q&A using provided facts
# - Gallery reads files from ./gallery/, blog reads from ./blog_posts/
# IMPORTANT: paste this file into your app folder (alongside gallery/ and blog_posts/)

import os
import re
import json
import time
import streamlit as st
import streamlit.components.v1 as components
from markdown import markdown

st.set_page_config(page_title="Aryan Sharma — Ultra Premium", layout="wide")

# ---------------- Utility: read gallery & blog posts ----------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
GALLERY_DIR = os.path.join(BASE_DIR, "gallery")
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")

def get_gallery_images():
    if not os.path.exists(GALLERY_DIR):
        return []
    files = sorted(f for f in os.listdir(GALLERY_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")))
    # return relative paths so Streamlit serves them
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
                k,v = line.split(':',1)
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
    mds = sorted(f for f in os.listdir(POSTS_DIR) if f.endswith(".md"))
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

# ---------------- Build HTML fragments for gallery & posts ----------------
gallery_imgs = get_gallery_images()
if gallery_imgs:
    gallery_html = ""
    for i, src in enumerate(gallery_imgs):
        alt = os.path.basename(src)
        gallery_html += f'<div class="g-item"><img src="{src}" alt="{alt}" loading="lazy"/></div>\n'
else:
    gallery_html = '<div class="g-empty">No images found in <code>gallery/</code></div>'

posts = get_all_posts()
if posts:
    posts_html = ""
    for p in posts:
        title = p["title"]
        date = p.get("date","")
        body_html = p["html"]
        posts_html += f'''
        <article class="post">
          <h4 class="post-title">{title}</h4>
          <div class="post-date">{date}</div>
          <div class="post-body">{body_html}</div>
        </article>
        '''
else:
    posts_html = '<div class="g-empty">No blog posts found (add .md files to blog_posts/)</div>'

# ---------------- Socials & meta ----------------
linkedin = "https://www.linkedin.com/in/aryan-sharma99999"
instagram = "https://instagram.com/aryanxsharma26"
year_str = str(time.localtime().tm_year)

# ---------------- Fullscreen HTML (placeholders replaced safely below) ----------------
html = r"""
<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Aryan Sharma — Ultra Premium</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
<style>
:root{
  --bgA: #160021;
  --bgB: #2b003f;
  --accent1: #ff66d6;
  --accent2: #6af0ff;
  --muted: rgba(230,230,255,0.9);
  --card-bg: rgba(255,255,255,0.02);
}
*{box-sizing:border-box}
html,body{height:100%;margin:0;padding:0;background:linear-gradient(180deg,var(--bgA),var(--bgB));font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto;color:var(--muted);overflow:hidden}
a{color:var(--accent2);text-decoration:underline}

/* canvas layers (nebula + stars) */
#bg { position:fixed; inset:0; z-index:-6; }
.nebula { position:fixed; inset:0; background:
   radial-gradient(40% 40% at 10% 20%, rgba(255,102,214,0.06), transparent 8%),
   radial-gradient(60% 40% at 80% 80%, rgba(106,240,255,0.05), transparent 10%);
   filter:blur(18px) saturate(120%); opacity:0.95; z-index:-5; }
.stars { position:fixed; inset:0; background-image: radial-gradient(#fff 1px, transparent 1px); background-size:5px 5px; opacity:0.12; z-index:-4 }

/* snap container for fullscreen sections */
.container { height:100vh; width:100vw; scroll-snap-type: y mandatory; overflow-y: auto; -webkit-overflow-scrolling: touch; }

/* section basics */
.section { height:100vh; min-height:600px; display:flex; align-items:center; justify-content:center; scroll-snap-align: start; padding:32px; }

/* NAV */
.navbar { position:fixed; top:18px; left:50%; transform:translateX(-50%); z-index:90; display:flex; gap:10px; padding:8px 12px; border-radius:999px; backdrop-filter:blur(8px); background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); border:1px solid rgba(255,255,255,0.03); }
.nav-brand{ font-weight:800; letter-spacing:1px; color:#fff; padding-right:8px }
.nav-link{ padding:8px 10px; border-radius:8px; font-weight:700; cursor:pointer; color:var(--muted) }
.nav-link:hover{ transform:translateY(-3px); background: rgba(255,255,255,0.02) }

/* HERO card */
.hero-card{ width:92%; max-width:1100px; padding:56px; border-radius:22px; text-align:center; position:relative; overflow:hidden; background:var(--card-bg); border:1px solid rgba(255,255,255,0.035); box-shadow:0 40px 120px rgba(20,0,40,0.6); backdrop-filter: blur(12px) saturate(140%); }
.hero-title{ font-size:56px; font-weight:900; margin:0; background:linear-gradient(90deg,var(--accent1),var(--accent2)); -webkit-background-clip:text; color:transparent; }
.hero-sub{ margin-top:12px; color:rgba(230,230,255,0.9) }
.role { margin-top:12px; font-weight:800; color:#ffdff8 }

/* animated flowing neon border */
.hero-card::before{
  content:""; position:absolute; inset:-3px; border-radius:26px; padding:3px; z-index:0;
  background: linear-gradient(90deg, rgba(255,102,214,0.0), var(--accent1), var(--accent2), var(--accent1), rgba(255,102,214,0.0));
  background-size:300% 300%;
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  animation: neonFlow 6s linear infinite;
  filter: drop-shadow(0 30px 60px rgba(120,40,180,0.18));
}
@keyframes neonFlow{ 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }

/* subtle rings for depth */
.rings{ position:absolute; left:50%; top:10%; transform:translateX(-50%); z-index:0; pointer-events:none }
.rings .r1{ width:820px; height:420px; border-radius:50%; border:1px solid rgba(255,255,255,0.02); filter: blur(18px); opacity:0.7; }

/* CTA buttons */
.cta{ margin-top:18px; display:flex; justify-content:center; gap:12px; z-index:2 }
.btn{ padding:10px 18px; border-radius:999px; font-weight:800; cursor:pointer; border:none }
.btn-primary{ background:linear-gradient(90deg,var(--accent1),var(--accent2)); color:#07030a; box-shadow:0 18px 60px rgba(120,40,180,0.12) }
.btn-ghost{ background:transparent; border:1px solid rgba(255,255,255,0.04); color:var(--muted) }

/* SECTIONS: gallery / content */
.section-content{ width:100%; max-width:1180px; margin:0 auto; display:grid; grid-template-columns: 1fr 1fr; gap:28px; align-items:start }
.card{ background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); border-radius:12px; padding:18px; border:1px solid rgba(255,255,255,0.03); box-shadow: 0 18px 60px rgba(6,6,10,0.45); }

/* gallery grid */
.gallery-grid{ display:grid; grid-template-columns: 1fr 1fr; gap:10px }
.g-item img{ width:100%; height:160px; object-fit:cover; border-radius:8px; transition:transform .28s ease; cursor:zoom-in }
.g-item img:hover{ transform:scale(1.04); filter: drop-shadow(0 18px 40px rgba(120,40,180,0.18)) }

/* posts list */
.posts-list{ display:flex; flex-direction:column; gap:12px }
.post{ padding:12px; border-radius:10px; background:linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.005)); border:1px solid rgba(255,255,255,0.02) }
.post-title{ margin:0; font-weight:800; color:#f7ecff }

/* footer */
.footer{ text-align:center; padding:30px; color:#d9cfe8 }

/* chat orb */
.chat-orb{ position:fixed; right:26px; bottom:28px; width:72px; height:72px; border-radius:999px; display:flex; align-items:center; justify-content:center; z-index:95; background:linear-gradient(90deg,var(--accent1),var(--accent2)); color:#07030a; font-weight:900; box-shadow: 0 30px 90px rgba(120,40,180,0.18); cursor:pointer }

/* chat popup */
.chat-popup{ position:fixed; right:26px; bottom:110px; width:420px; max-width:92vw; border-radius:12px; overflow:hidden; display:none; z-index:96; box-shadow:0 30px 80px rgba(2,2,8,0.7); border:1px solid rgba(255,255,255,0.03) }
.chat-head{ padding:12px; background:linear-gradient(90deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); color:var(--muted); font-weight:800 }
.chat-body{ padding:12px; max-height:260px; overflow:auto; background: linear-gradient(180deg, rgba(6,6,8,0.98), rgba(8,8,10,0.98)); color:var(--muted) }
.chat-row{ padding:12px; display:flex; gap:8px; background:linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.007)) }

/* small screens */
@media (max-width:900px){
  .section-content{ grid-template-columns: 1fr; }
  .hero-title{ font-size:36px }
  .g-item img{ height:120px }
}
</style>
</head>
<body>
  <div id="bg">
    <div class="nebula" aria-hidden="true"></div>
    <div class="stars" aria-hidden="true"></div>
  </div>

  <div class="navbar" role="navigation" aria-label="main-nav">
    <div class="nav-brand">ARYAN</div>
    <div class="nav-link" data-target="hero">Home</div>
    <div class="nav-link" data-target="gallery">Gallery</div>
    <div class="nav-link" data-target="writings">Writings</div>
    <div class="nav-link" data-target="blog">Blog</div>
    <div class="nav-link" data-target="projects">Projects</div>
  </div>

  <!-- container with scroll snapping -->
  <div class="container" id="snapContainer" tabindex="0">

    <!-- HERO SECTION -->
    <section id="hero" class="section" aria-label="Hero">
      <div class="hero-card" role="region" aria-labelledby="heroTitle">
        <div class="rings" aria-hidden="true"><div class="r1"></div></div>
        <h1 class="hero-title" id="heroTitle">ARYAN SHARMA</h1>
        <div class="hero-sub">I design, build and tell stories through code.</div>
        <div class="role">I'm a <span id="typeRole">web developer</span></div>
        <div class="cta" role="group" aria-label="hero actions">
          <a class="btn btn-primary" href="/resume.pdf" target="_blank" rel="noreferrer">Download Resume</a>
          <a class="btn btn-ghost" href="__LINKEDIN__" target="_blank" rel="noreferrer">LinkedIn</a>
          <a class="btn btn-ghost" href="__INSTAGRAM__" target="_blank" rel="noreferrer">Instagram</a>
        </div>
      </div>
    </section>

    <!-- GALLERY + PROJECTS -->
    <section id="gallery" class="section" aria-label="Gallery & Projects">
      <div style="width:100%; max-width:1180px; margin:0 auto;" class="section-content">
        <div class="card">
          <h3 style="margin-top:0">📸 Photos (Gallery)</h3>
          <div class="gallery-grid">
            __GALLERY_HTML__
          </div>
        </div>
        <div class="card">
          <h3 style="margin-top:0">🧩 Projects</h3>
          <div style="display:flex;flex-direction:column;gap:12px">
            <div style="padding:12px;border-radius:8px;background:rgba(255,255,255,0.01);font-weight:700">Chatbot Website<div style="font-weight:400;font-size:13px;opacity:.8">Client-side Q&A demo</div></div>
            <div style="padding:12px;border-radius:8px;background:rgba(255,255,255,0.01);font-weight:700">Portfolio Builder<div style="font-weight:400;font-size:13px;opacity:.8">Template & theme</div></div>
            <div style="padding:12px;border-radius:8px;background:rgba(255,255,255,0.01);font-weight:700">AI Experiments<div style="font-weight:400;font-size:13px;opacity:.8">Small ML projects</div></div>
          </div>
        </div>
      </div>
    </section>

    <!-- WRITINGS + BLOG -->
    <section id="writings" class="section" aria-label="Writings & Blog">
      <div style="width:100%; max-width:1180px; margin:0 auto;" class="section-content">
        <div class="card">
          <h3 style="margin-top:0">✍️ Writings (Anonymous)</h3>
          <div id="anonBox" style="min-height:140px">No anonymous writings yet — use the chat or admin to add.</div>
        </div>
        <div class="card">
          <h3 style="margin-top:0">📰 Blog</h3>
          <div class="posts-list">
            __POSTS_HTML__
          </div>
        </div>
      </div>
    </section>

    <!-- CONTACT / FOOTER -->
    <section id="projects" class="section" aria-label="Contact & Footer">
      <div style="width:100%; max-width:1180px; margin:0 auto;">
        <div class="card">
          <h3 style="margin-top:0">Contact</h3>
          <p>Connect on <a href="__LINKEDIN__" target="_blank">LinkedIn</a> or <a href="__INSTAGRAM__" target="_blank">Instagram</a>.</p>
        </div>
        <div style="height:18px"></div>
        <div class="card">
          <h4 style="margin:0">© __YEAR__ Aryan Sharma</h4>
        </div>
      </div>
    </section>

  </div>

  <div class="chat-orb" id="chatOrb" title="Ask me about Aryan">✦</div>
  <div class="chat-popup" id="chatPopup" aria-hidden="true" role="dialog">
    <div class="chat-head">Ask me about Aryan ☕ <button id="closeChat" style="float:right;background:transparent;border:none;color:var(--muted);cursor:pointer">✕</button></div>
    <div class="chat-body" id="chatBody"></div>
    <div class="chat-row">
      <input id="chatInput" placeholder="Type a question..." style="flex:1;padding:10px;border-radius:8px;border:1px solid rgba(255,255,255,0.04);background:#0b0b10;color:var(--muted)"/>
      <button id="chatSend" style="padding:10px 12px;border-radius:8px;border:none;background:linear-gradient(90deg,var(--accent1),var(--accent2));font-weight:800;color:#071026;cursor:pointer">Send</button>
    </div>
  </div>

<script>
// Smooth nav: map nav items
document.querySelectorAll('.nav-link').forEach(el=>{
  el.addEventListener('click', ()=> {
    const id = el.getAttribute('data-target');
    const sec = document.getElementById(id);
    if(!sec) return;
    sec.scrollIntoView({behavior:'smooth', block:'start'});
  });
});

// keyboard: up/down to navigate sections
(function(){
  const container = document.getElementById('snapContainer');
  container.addEventListener('wheel', (e)=> {
    // allow default; CSS snap will lock to nearest
  }, {passive:true});
})();

// Typewriter roles
(function(){
  const words = ["web developer","tech enthusiast","video editor","writer","learner"];
  let idx = 0, pos = 0, forward = true;
  const el = document.getElementById('typeRole');
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

// Chat: simple client-side Q&A using injected facts
const ARYAN_FACTS = __FACTS__;

const orb = document.getElementById('chatOrb');
const popup = document.getElementById('chatPopup');
const body = document.getElementById('chatBody');
const input = document.getElementById('chatInput');
const send = document.getElementById('chatSend');
const closeBtn = document.getElementById('closeChat');

function addMsg(text, who){
  const div = document.createElement('div');
  div.style.margin = '8px 0';
  div.style.padding = '8px';
  div.style.borderRadius = '10px';
  div.style.maxWidth = '90%';
  if(who === 'user'){ div.style.marginLeft = 'auto'; div.style.background = 'rgba(255,255,255,0.06)'; div.style.color = '#fff'; div.textContent = text; }
  else { div.style.marginRight = 'auto'; div.style.background = 'linear-gradient(90deg, rgba(120,120,255,0.06), rgba(140,60,200,0.03))'; div.style.color = '#eaf6ff'; div.textContent = text; }
  body.appendChild(div);
  body.scrollTop = body.scrollHeight;
}

orb.addEventListener('click', ()=>{
  popup.style.display = popup.style.display === 'block' ? 'none' : 'block';
  if(popup.style.display === 'block' && body.children.length === 0) addMsg("Hi — I'm Aryan's assistant ☕ Ask me anything about Aryan.");
  input.focus();
});
closeBtn.addEventListener('click', ()=> popup.style.display = 'none');

send.addEventListener('click', ()=> {
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

// Lightbox for gallery
document.querySelectorAll('.g-item img').forEach(img=>{
  img.addEventListener('click', ()=> {
    const ov = document.createElement('div'); ov.style.position='fixed'; ov.style.inset=0; ov.style.background='rgba(0,0,0,0.9)'; ov.style.display='flex'; ov.style.alignItems='center'; ov.style.justifyContent='center'; ov.style.zIndex=9999;
    const big = document.createElement('img'); big.src=img.src; big.style.maxWidth='92%'; big.style.maxHeight='92%'; big.style.borderRadius='10px';
    ov.appendChild(big);
    ov.addEventListener('click', ()=> document.body.removeChild(ov));
    document.body.appendChild(ov);
  });
});
</script>
</body>
</html>
"""

# ---------------- Replace placeholders safely ----------------
html = html.replace("__GALLERY_HTML__", gallery_html)
html = html.replace("__POSTS_HTML__", posts_html)
html = html.replace("__LINKEDIN__", linkedin)
html = html.replace("__INSTAGRAM__", instagram)
html = html.replace("__YEAR__", year_str)
# facts_json contains quotes and braces — inject raw JSON string literal into JS
html = html.replace("__FACTS__", facts_json)

# ---------------- Render as a single components.html (scrolling enabled) ----------------
# Use a large height and let the internal CSS manage full-screen snapping.
components.html(html, height=1100, scrolling=True)

# ---------------- Optional simple admin hints in Streamlit sidebar ----------------
with st.sidebar.expander("Admin / Notes", expanded=True):
    st.write("• This is Version 1A (Fullscreen section-based). Use left column to view gallery/markdown changes.")
    st.write("• Add images to `gallery/` (jpg/png/webp/gif) to populate gallery.")
    st.write("• Add markdown files to `blog_posts/` to publish posts.")
    st.write("• If you want direct OpenAI-powered chat instead of client-side rules, tell me and I'll wire it in.")
