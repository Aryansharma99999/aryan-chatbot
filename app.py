# app.py
# Premium single-file Streamlit portfolio (Neon Galaxy, hero parallax, nebula, masonry gallery, chatbot)
# SAFE: HTML is inserted as a normal triple-quoted string (NOT an f-string) and placeholders are replaced.

import os
import re
import json
import time
import streamlit as st
import streamlit.components.v1 as components
from markdown import markdown

st.set_page_config(page_title="Aryan Sharma — Premium", layout="wide", initial_sidebar_state="collapsed")

# ---------------- Paths ----------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
GALLERY_DIR = os.path.join(BASE_DIR, "gallery")
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")

# ---------------- Helpers ----------------
def get_gallery_images():
    if not os.path.exists(GALLERY_DIR):
        return []
    files = [f for f in sorted(os.listdir(GALLERY_DIR)) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif"))]
    return [os.path.join("gallery", f) for f in files]

def get_blog_posts():
    results = []
    if not os.path.exists(POSTS_DIR):
        return results
    for fn in sorted(os.listdir(POSTS_DIR)):
        if not fn.endswith(".md"):
            continue
        path = os.path.join(POSTS_DIR, fn)
        with open(path, "r", encoding="utf-8") as fh:
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
        results.append({
            "title": meta.get("title", fn[:-3].replace('-', ' ').title()),
            "date": meta.get("date", ""),
            "html": markdown(body)
        })
    return results

# ---------------- Aryan facts ----------------
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
    "what does aryan dream about": "A life full of learning, creativity, and endless coffee."
}

# ---------------- Session state for anonymous writings ----------------
if "anon_messages" not in st.session_state:
    st.session_state.anon_messages = []

# Keep a minimal sidebar form as backup (we hide sidebar via CSS in the main UI)
with st.sidebar.form("anon_form", clear_on_submit=True):
    st.write("Share anonymously (backup)")
    m = st.text_area("Write anonymously...", height=120)
    if st.form_submit_button("Send"):
        if m and m.strip():
            st.session_state.anon_messages.insert(0, {"msg": m.strip(), "time": time.asctime()})
            st.success("Saved — appears on the page.")

# ---------------- Data to inject ----------------
gallery = get_gallery_images()
posts = get_blog_posts()
anon = st.session_state.anon_messages

SOCIAL = {
    "instagram": "https://instagram.com/aryanxsharma26",
    "linkedin": "https://www.linkedin.com/in/aryan-sharma99999"
}

DATA = {
    "gallery": gallery,
    "posts": posts,
    "anon": anon,
    "facts": ARYAN_FACTS,
    "social": SOCIAL,
    "year": time.localtime().tm_year
}

DATA_JSON = json.dumps(DATA)

# ---------------- Safe HTML template (not an f-string) ----------------
html_template = """
<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Aryan Sharma — Premium Neon Galaxy</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800;900&display=swap" rel="stylesheet">
<style>
  :root{
    --bg1:#0a0014;
    --nebula1:#481056;
    --nebula2:#2b0041;
    --neon:#c56cff;
    --neon-2:#5ef3ff;
    --glass: rgba(255,255,255,0.03);
    --muted: rgba(220,230,255,0.78);
  }
  html,body{height:100%;margin:0;padding:0;background:var(--bg1);font-family:Inter,system-ui,-apple-system,'Segoe UI',Roboto;color:var(--muted);-webkit-font-smoothing:antialiased;}
  /* canvas covers full viewport */
  #nebulaCanvas { position: fixed; inset: 0; z-index: 0; width:100vw; height:100vh; pointer-events:none; display:block; }
  .vignette { position: fixed; inset: 0; z-index: 1; pointer-events:none; background: radial-gradient(ellipse at 25% 20%, rgba(255,255,255,0.02), transparent 12%, rgba(0,0,0,0.6) 70%); }

  /* site on top */
  .app { position: relative; z-index: 5; min-height: 100vh; display:flex; align-items:stretch; justify-content:center; overflow:hidden; }
  .center { width:100%; max-width:1200px; margin:0 auto; padding:64px 24px; box-sizing:border-box; }

  /* HERO */
  .hero-section{ min-height:78vh; display:flex; align-items:center; justify-content:center; }
  .hero-card{ width:min(1100px,94%); border-radius:20px; padding:46px 44px; background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); border:1px solid rgba(255,255,255,0.03); box-shadow: 0 40px 120px rgba(4,2,10,0.7); transform-style:preserve-3d; position:relative; overflow:visible; backdrop-filter: blur(10px) saturate(140%); -webkit-backdrop-filter: blur(10px) saturate(140%); }
  .neon-outline { position:absolute; inset:-8px; border-radius:24px; pointer-events:none; box-shadow: 0 0 40px rgba(197,108,255,0.14), inset 0 0 16px rgba(94,243,255,0.03); border:2px solid rgba(197,108,255,0.06); }
  .hero-name{ font-size:56px; font-weight:900; margin:0; letter-spacing:1px; display:inline-block; color:transparent; background: linear-gradient(90deg, rgba(255,255,255,0.12), var(--neon)); -webkit-background-clip:text; background-clip:text; position:relative; z-index:6; }
  .hero-sub{ margin-top:14px; color: rgba(210,230,255,0.85); font-weight:600; z-index:6; position:relative; }
  .type{ margin-top:10px; font-weight:700; color:rgba(200,220,255,0.92); font-size:18px; z-index:6; position:relative; }
  .spotlight { position:absolute; left:0; right:0; top:-40%; bottom:-40%; z-index:0; pointer-events:none; mix-blend-mode:overlay; opacity:0.9; border-radius:24px; }

  .cta{ margin-top:22px; display:flex; gap:12px; justify-content:center; z-index:6; position:relative; }
  .btn{ padding:12px 18px; border-radius:999px; font-weight:800; cursor:pointer; border:none; }
  .btn-primary{ background: linear-gradient(90deg,var(--neon),var(--neon-2)); color:#0b0b10; box-shadow: 0 8px 30px rgba(120,50,160,0.28); }
  .btn-outline{ background:transparent; color:var(--muted); border:1px solid rgba(255,255,255,0.04); }

  /* Grid and Cards */
  .grid-wrap{ display:grid; grid-template-columns: 1fr 1fr; gap:28px; align-items:start; margin-top:26px; }
  .glass{ background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); border-radius:12px; padding:14px; border:1px solid rgba(255,255,255,0.03); box-shadow:0 12px 36px rgba(6,6,10,0.45); }
  .section-title{ font-weight:800; color:#dff3ff; display:flex; align-items:center; gap:10px; margin-bottom:10px; }

  /* masonry */
  .masonry{ column-count:2; column-gap:12px; }
  .masonry-item{ break-inside:avoid; margin-bottom:12px; position:relative; overflow:hidden; border-radius:10px; transition: transform .25s ease, box-shadow .25s ease; }
  .masonry-item img{ width:100%; display:block; border-radius:10px; transition: transform .28s ease; }
  .masonry-item:hover{ transform: translateY(-8px) rotateX(2deg) translateZ(6px); box-shadow:0 24px 80px rgba(30,8,40,0.6); }
  .masonry-item:hover img{ transform: scale(1.06); filter: drop-shadow(0 12px 30px rgba(140,40,200,0.22)); }

  .post-card{ margin-bottom:12px; padding:14px; border-radius:10px; background: linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.007)); border:1px solid rgba(255,255,255,0.025); }
  .post-card h3{ margin:0;color:#eaf6ff;font-weight:800; }

  /* socials */
  .socials{ display:flex; gap:12px; align-items:center; }
  .socials a{ text-decoration:none; color:var(--muted); padding:8px; border-radius:8px; display:inline-flex; align-items:center; gap:8px; transition: transform .18s ease, box-shadow .18s ease; border:1px solid rgba(255,255,255,0.02); }
  .socials a:hover{ transform: translateY(-4px); box-shadow: 0 18px 60px rgba(180,80,220,0.12); color: white; }
  .dot{ width:12px; height:12px; border-radius:999px; background: linear-gradient(90deg,var(--neon),var(--neon-2)); box-shadow: 0 6px 26px rgba(140,40,200,0.45); }

  /* chat gem */
  .chat-orb{ position:fixed; right:28px; bottom:28px; z-index:9999; width:72px; height:72px; border-radius:999px; display:flex; align-items:center; justify-content:center; cursor:pointer; background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.06), rgba(0,0,0,0.25)); border:2px solid rgba(197,108,255,0.28); box-shadow: 0 30px 80px rgba(120,40,180,0.16); transition: transform .18s ease; }
  .chat-orb:hover{ transform: translateY(-6px) rotate(-6deg) scale(1.02); }
  .chat-orb .inner{ width:46px; height:46px; border-radius:50%; background: linear-gradient(90deg,var(--neon),var(--neon-2)); display:flex; align-items:center; justify-content:center; color:#07030a; font-weight:800; box-shadow: 0 10px 30px rgba(140,40,200,0.38); transform-origin:center; animation:rotateOrb 6s linear infinite; }
  @keyframes rotateOrb{ from{transform:rotate(0deg);} to{transform:rotate(360deg);} }
  .chat-popup{ position:fixed; right:28px; bottom:112px; z-index:9999; width:380px; max-width:92vw; border-radius:12px; overflow:hidden; display:none; }
  .chat-head{ padding:12px; background: linear-gradient(90deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); font-weight:800; color:#eaf6ff; border-bottom:1px solid rgba(255,255,255,0.02); }
  .chat-body{ padding:12px; max-height:260px; overflow:auto; background: linear-gradient(180deg, rgba(10,8,14,0.98), rgba(6,4,8,0.98)); color:var(--muted); }
  .chat-input{ display:flex; gap:8px; padding:12px; background: linear-gradient(180deg, rgba(6,6,8,0.98), rgba(8,8,10,0.98)); border-top:1px solid rgba(255,255,255,0.02); }
  .chat-input input{ flex:1; padding:8px 10px; border-radius:10px; border:none; background: rgba(255,255,255,0.03); color:var(--muted); }

  /* responsive */
  @media (max-width:980px){
    .masonry{ column-count:1; }
    .hero-name{ font-size:42px; }
    .center{ padding:36px 18px; }
  }
</style>
</head>
<body>
<canvas id="nebulaCanvas"></canvas>
<div class="vignette"></div>

<div class="app">
  <div class="center">

    <!-- HERO -->
    <section class="hero-section" id="heroSection" aria-label="Hero">
      <div class="hero-card" id="heroCard" role="banner" aria-live="polite">
        <div class="neon-outline" aria-hidden="true"></div>
        <div style="position:relative; z-index:6;">
          <div style="text-align:center; position:relative; z-index:6;">
            <div class="hero-name" id="heroName">ARYAN SHARMA</div>
            <div class="hero-sub">Welcome to my personal website!</div>
            <div class="type">I'm a <span id="typeword">web developer</span></div>
            <div class="cta">
              <a class="btn btn-primary" href="/resume.pdf#chatbot-section" target="_blank" rel="noreferrer">Download Resume</a>
              <a class="btn btn-outline" id="linkLinked" target="_blank" href="%%LINKEDIN%%">LinkedIn</a>
              <a class="btn btn-outline" id="linkInsta" target="_blank" href="%%INSTAGRAM%%">Instagram</a>
            </div>
          </div>
        </div>
        <div class="spotlight" id="spotlight" aria-hidden="true"></div>
      </div>
    </section>

    <!-- CONTENT -->
    <section id="contentSection">
      <div class="grid-wrap">
        <div class="left-col">
          <div class="glass">
            <div class="section-title">📸 Photos (Gallery)</div>
            <div class="masonry" id="masonryGallery" aria-live="polite"></div>
          </div>

          <div style="height:18px"></div>

          <div class="glass" id="projectsCard">
            <div class="section-title">📁 Projects</div>
            <div style="display:flex;flex-direction:column;gap:8px;">
              <div style="padding:10px;border-radius:8px;background:rgba(255,255,255,0.01);font-weight:700">Chatbot Website <div style="font-weight:400;font-size:13px;opacity:0.8">Client Q&A demo</div></div>
              <div style="padding:10px;border-radius:8px;background:rgba(255,255,255,0.01);font-weight:700">Portfolio Builder <div style="font-weight:400;font-size:13px;opacity:0.8">Template & theme</div></div>
              <div style="padding:10px;border-radius:8px;background:rgba(255,255,255,0.01);font-weight:700">AI Experiments <div style="font-weight:400;font-size:13px;opacity:0.8">Small ML projects</div></div>
            </div>
          </div>
        </div>

        <div class="right-col">
          <div class="glass">
            <div class="section-title">✍️ Writings (Anonymous)</div>
            <div id="anonList" style="min-height:120px;"></div>
            <div style="height:12px"></div>
            <div class="section-title" style="margin-top:8px;">📰 Blog Posts</div>
            <div id="postsArea"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- FOOTER -->
    <section id="footerSection" style="padding-top:36px;padding-bottom:36px;">
      <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;">
        <div style="display:flex;align-items:center;gap:14px;">
          <div style="font-weight:800;font-size:15px;color:#eaf6ff">© %%YEAR%% Aryan Sharma</div>
          <div style="color:rgba(200,220,255,0.7)">Built with ❤️</div>
        </div>
        <div class="socials">
          <a href="%%LINKEDIN%%" target="_blank" rel="noreferrer"><span class="dot"></span> LinkedIn</a>
          <a href="%%INSTAGRAM%%" target="_blank" rel="noreferrer"><span class="dot"></span> Instagram</a>
        </div>
      </div>
    </section>

  </div>
</div>

<!-- chat orb + popup -->
<div class="chat-orb" id="chatOrb" title="Ask me about Aryan" aria-label="Open chat">
  <div class="inner">✦</div>
</div>

<div class="chat-popup" id="chatPopup" role="dialog" aria-hidden="true" aria-label="Aryan chatbot">
  <div class="chat-head">Hi — I'm Aryan's assistant</div>
  <div class="chat-body" id="chatBody"></div>
  <div class="chat-input">
    <input id="chatInput" placeholder="Ask me about Aryan..."/>
    <button id="chatSend" style="background:linear-gradient(90deg,var(--neon),var(--neon-2));border-radius:8px;padding:8px 12px;border:none;font-weight:800;color:#0b0610">Send</button>
  </div>
</div>

<script>
  // Inject data safely
  const DATA = %%DATA_JSON%%;

  /* Nebula + starfield with trails */
  (function(){
    const canvas = document.getElementById('nebulaCanvas');
    const ctx = canvas.getContext('2d');
    function resize(){ canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
    resize(); window.addEventListener('resize', resize);

    const stars = [];
    const STAR_BASE = Math.floor((window.innerWidth * window.innerHeight) / 7000);
    for(let i=0;i<Math.max(180, STAR_BASE); i++){
      stars.push({
        x: Math.random()*canvas.width,
        y: Math.random()*canvas.height,
        r: Math.random()*1.8 + 0.2,
        vx: (Math.random()*0.6)-0.3,
        vy: (Math.random()*0.2)-0.1,
        alpha: Math.random()*0.9 + 0.1
      });
    }
    const trails = [];
    function spawnTrail(x,y,vx,vy){ trails.push({x:x,y:y,vx:vx,vy:vy,life:Math.random()*60+40,age:0}); }

    let t = 0;
    function draw(){
      t += 0.005;
      // base gradient
      const g = ctx.createLinearGradient(0,0,canvas.width,canvas.height);
      g.addColorStop(0, '#08000a');
      g.addColorStop(0.45, '#1a0022');
      g.addColorStop(1, '#06000a');
      ctx.fillStyle = g;
      ctx.fillRect(0,0,canvas.width,canvas.height);

      // nebula radial
      const cx = canvas.width*0.65 + Math.sin(t*1.2)*140;
      const cy = canvas.height*0.35 + Math.cos(t*0.7)*120;
      const r = Math.max(canvas.width, canvas.height)*0.9;
      const rn = ctx.createRadialGradient(cx, cy, 0, cx, cy, r);
      rn.addColorStop(0, 'rgba(180,50,150,0.12)');
      rn.addColorStop(0.3, 'rgba(100,30,140,0.06)');
      rn.addColorStop(0.7, 'rgba(10,4,20,0.02)');
      ctx.globalCompositeOperation = 'lighter';
      ctx.fillStyle = rn;
      ctx.fillRect(0,0,canvas.width,canvas.height);
      ctx.globalCompositeOperation = 'source-over';

      // noise overlay
      const noise = ctx.createLinearGradient(canvas.width*0.2,0, canvas.width, canvas.height);
      noise.addColorStop(0, 'rgba(80,10,120,0.02)');
      noise.addColorStop(1, 'rgba(0,0,0,0.08)');
      ctx.fillStyle = noise;
      ctx.fillRect(0,0,canvas.width,canvas.height);

      // stars & trails
      for(const s of stars){
        s.x += s.vx; s.y += s.vy;
        if(s.x < -10) s.x = canvas.width + 10;
        if(s.x > canvas.width + 10) s.x = -10;
        if(s.y < -10) s.y = canvas.height + 10;
        if(s.y > canvas.height + 10) s.y = -10;

        const a = s.alpha * (0.6 + 0.4 * Math.sin((s.x + s.y + t*100)/60));
        ctx.beginPath();
        ctx.fillStyle = 'rgba(255,255,255,' + a + ')';
        ctx.arc(s.x, s.y, s.r, 0, Math.PI*2);
        ctx.fill();

        if(Math.random() < 0.002){
          spawnTrail(s.x, s.y, s.vx*6, s.vy*6 - 1.4);
        }
      }

      for(let i=trails.length-1;i>=0;i--){
        const p = trails[i];
        p.age++;
        p.x += p.vx; p.y += p.vy;
        const lifeRatio = 1 - (p.age / p.life);
        if(lifeRatio <= 0){ trails.splice(i,1); continue; }
        ctx.beginPath();
        ctx.fillStyle = 'rgba(220,180,255,' + (lifeRatio*0.8) + ')';
        ctx.arc(p.x, p.y, Math.max(0.8, lifeRatio*3.6), 0, Math.PI*2);
        ctx.fill();
      }

      requestAnimationFrame(draw);
    }
    draw();
  })();

  /* Hero parallax & spotlight sweep */
  (function(){
    const hero = document.getElementById('heroCard');
    const name = document.getElementById('heroName');
    const spotlight = document.getElementById('spotlight');

    function onMove(e){
      const cx = window.innerWidth/2;
      const cy = window.innerHeight/2;
      const dx = (e.clientX - cx) / cx;
      const dy = (e.clientY - cy) / cy;
      const rx = dx * 8;
      const ry = dy * -6;
      hero.style.transform = `perspective(1200px) rotateX(${ry}deg) rotateY(${rx}deg) translateZ(6px)`;
      spotlight.style.background = `radial-gradient(circle at ${50 + dx*20}% ${40 + dy*10}%, rgba(255,255,255,0.02), transparent 18%)`;
    }
    window.addEventListener('mousemove', onMove);
    hero.addEventListener('mouseleave', ()=> hero.style.transform = 'none');

    // sweep effect on text
    let sweep = 0;
    setInterval(()=> { sweep += 1; name.style.backgroundPosition = (sweep % 200) + "% 0%"; }, 60);
  })();

  /* Typewriter */
  (function(){
    const words = ["web developer","writer","learner","tech enthusiast","video editor"];
    let idx = 0, pos = 0, forward = true;
    const el = document.getElementById('typeword');
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

  /* Fill content (gallery, posts, anon) */
  (function(){
    const data = DATA;
    const gallery = data.gallery || [];
    const posts = data.posts || [];
    const anon = data.anon || [];

    const galNode = document.getElementById('masonryGallery');
    if(gallery.length === 0){
      galNode.innerHTML = "<div style='color:rgba(200,220,255,0.6);padding:8px'>No images in gallery/ — upload images to your repo.</div>";
    } else {
      galNode.innerHTML = '';
      gallery.forEach((src,i)=>{
        const item = document.createElement('div');
        item.className = 'masonry-item';
        item.innerHTML = `<img src="${src}" alt="gallery-${i}">`;
        galNode.appendChild(item);
      });
    }

    const postsArea = document.getElementById('postsArea');
    if(posts.length === 0){
      postsArea.innerHTML = "<div style='color:rgba(200,220,255,0.6);padding:8px'>No blog posts in blog_posts/</div>";
    } else {
      postsArea.innerHTML = '';
      posts.forEach(p=>{
        const c = document.createElement('div');
        c.className = 'post-card';
        c.innerHTML = `<div class='date'>${p.date}</div><h3>${p.title}</h3><div style='margin-top:8px;color:rgba(220,235,255,0.95)'>${p.html}</div>`;
        postsArea.appendChild(c);
      });
    }

    const anonNode = document.getElementById('anonList');
    if(!anon || anon.length === 0){
      anonNode.innerHTML = "<div style='color:rgba(200,220,255,0.6);padding:8px'>No anonymous writings yet. Use the sidebar or add via the app state.</div>";
    } else {
      anonNode.innerHTML = '';
      anon.forEach(a=>{
        const el = document.createElement('div');
        el.className = 'glass';
        el.style.marginBottom = '8px';
        el.innerHTML = `<div style="color:rgba(220,235,255,0.95)">${a.msg}</div><div style="font-size:12px;color:rgba(180,200,220,0.6);margin-top:8px">${a.time}</div>`;
        anonNode.appendChild(el);
      });
    }
  })();

  /* Chat */
  (function(){
    const orb = document.getElementById('chatOrb');
    const popup = document.getElementById('chatPopup');
    const body = document.getElementById('chatBody');
    const input = document.getElementById('chatInput');
    const send = document.getElementById('chatSend');
    const facts = DATA.facts || {};

    function addMsg(txt, who='bot'){
      const el = document.createElement('div');
      el.textContent = txt;
      el.style.padding = '8px 10px';
      el.style.marginBottom = '8px';
      el.style.borderRadius = '10px';
      if(who === 'user'){ el.style.background = 'rgba(255,255,255,0.06)'; el.style.textAlign = 'right'; }
      else { el.style.background = 'linear-gradient(90deg, rgba(110,140,255,0.06), rgba(140,60,200,0.03))'; }
      body.appendChild(el); body.scrollTop = body.scrollHeight;
    }

    let introShown = false;
    orb.addEventListener('click', ()=>{
      const open = popup.style.display === 'block';
      popup.style.display = open ? 'none' : 'block';
      if(!open && !introShown){
        addMsg("Hi — I'm Aryan's AI assistant. Ask me anything about Aryan ☕");
        introShown = true;
      }
      input.focus();
    });

    send.addEventListener('click', ()=>{
      const q = (input.value || '').trim();
      if(!q) return;
      addMsg(q, 'user'); input.value = '';
      setTimeout(()=>{
        const lq = q.toLowerCase();
        let out = null;
        for(const k in facts){ if(lq.includes(k)) { out = facts[k]; break; } }
        if(!out){ if(lq.includes('name')) out = "Aryan Sharma — that guy with stories & coffee."; else out = "Ask me anything about Aryan ☕🙂!"; }
        addMsg(out,'bot');
      }, 300 + Math.random()*400);
    });
    input.addEventListener('keydown', e=>{ if(e.key === 'Enter'){ e.preventDefault(); send.click(); } });
  })();
</script>
</body>
</html>
"""

# ---------------- Replace placeholders safely ----------------
html = html_template.replace("%%DATA_JSON%%", DATA_JSON)
html = html.replace("%%LINKEDIN%%", SOCIAL["linkedin"])
html = html.replace("%%INSTAGRAM%%", SOCIAL["instagram"])
html = html.replace("%%YEAR%%", str(DATA["year"]))

# ---------------- Render component ----------------
# components.html will embed this HTML. Use a tall height and allow scrolling inside the component.
components.html(html, height=980, scrolling=True)

# ---------------- Force Streamlit wrappers transparent (robust selectors) ----------------
# This CSS aggressively attempts to make Streamlit containers transparent so the background shows through.
st.markdown(
    """
    <style>
    html, body, .stApp, .block-container, .main, .css-1lcbmhc, .css-18e3th9, .css-1v3fvcr {
        background: transparent !important;
    }
    .stApp > .main > div { background: transparent !important; }
    footer, header { background: transparent !important; }
    .block-container { padding-top: 0 !important; }
    /* Hide sidebar (we used it only as a backup) */
    [data-testid="stSidebar"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True
)

# ---------------- Small Streamlit notes below the component ----------------
st.markdown("---")
st.markdown("### Notes")
st.markdown("- Put images in the `gallery/` folder (jpg/png/webp/gif).")
st.markdown("- Put blog `.md` files in the `blog_posts/` folder (YAML frontmatter optional).")
st.markdown("- If you still see white areas, paste a screenshot and I'll patch final CSS selectors (Streamlit versions differ).")
st.write("LinkedIn:", SOCIAL["linkedin"])
st.write("Instagram:", SOCIAL["instagram"])
