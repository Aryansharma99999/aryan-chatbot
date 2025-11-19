# app.py — Ultra Premium single-file portfolio (paste & run)
import os
import re
import json
import time
import streamlit as st
import streamlit.components.v1 as components
from markdown import markdown

st.set_page_config(page_title="Aryan Sharma — Ultra Premium", layout="wide", initial_sidebar_state="collapsed")
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
GALLERY_DIR = os.path.join(BASE_DIR, "gallery")
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")

# ---------------- helpers ----------------
def get_gallery_images():
    if not os.path.exists(GALLERY_DIR):
        return []
    files = [f for f in sorted(os.listdir(GALLERY_DIR)) if f.lower().endswith((".jpg",".jpeg",".png",".webp",".gif"))]
    return [os.path.join("gallery", f) for f in files]

def get_blog_posts():
    posts = []
    if not os.path.exists(POSTS_DIR):
        return posts
    for fn in sorted(os.listdir(POSTS_DIR)):
        if not fn.endswith(".md"): continue
        path = os.path.join(POSTS_DIR, fn)
        with open(path, "r", encoding="utf-8") as fh:
            txt = fh.read()
        meta = {}
        body = txt
        m = re.match(r'---\n(.*?)\n---', txt, re.DOTALL)
        if m:
            for line in m.group(1).splitlines():
                if ':' in line:
                    k,v = line.split(':',1); meta[k.strip()] = v.strip()
            body = txt[m.end():].strip()
        posts.append({
            "title": meta.get("title", fn[:-3].replace('-',' ').title()),
            "date": meta.get("date", ""),
            "html": markdown(body)
        })
    return posts

# ---------------- Aryan facts for chatbot ----------------
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

SOCIAL = {
    "linkedin": "https://www.linkedin.com/in/aryan-sharma99999",
    "instagram": "https://instagram.com/aryanxsharma26"
}

# session for anon messages
if "anon_messages" not in st.session_state:
    st.session_state.anon_messages = []

# ---------------- Prepare DATA -> JSON for client script ----------------
DATA = {
    "gallery": get_gallery_images(),
    "posts": get_blog_posts(),
    "anon": st.session_state.anon_messages,
    "facts": ARYAN_FACTS,
    "social": SOCIAL,
    "year": time.localtime().tm_year
}
DATA_JSON = json.dumps(DATA)

# ---------------- The Ultra Premium HTML (safe triple-quoted string) ----------------
html = """
<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Aryan Sharma — Ultra Premium</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">
<style>
  :root{
    --bg0: #050010;
    --nebula1:#3b003b;
    --nebula2:#15001a;
    --neon1:#d46aff;
    --neon2:#66f0ff;
    --glass: rgba(255,255,255,0.03);
    --muted: rgba(220,230,255,0.8);
  }
  html,body{height:100%;margin:0;padding:0;background:var(--bg0);font-family:Inter,system-ui,-apple-system,'Segoe UI',Roboto;color:var(--muted);}
  /* Force Streamlit frames to be transparent when embedded */
  /* We'll still embed this component with components.html; these selectors help in some environments */
  :root, body { -webkit-font-smoothing:antialiased; -moz-osx-font-smoothing:grayscale; }

  /* Full canvas layers */
  #bgCanvas { position:fixed; inset:0; z-index:0; display:block; }
  .overlay-aurora { position:fixed; inset:0; z-index:1; pointer-events:none; mix-blend-mode:overlay; opacity:0.9; }
  .page { position:relative; z-index:5; min-height:100vh; display:flex; align-items:flex-start; justify-content:center; }

  /* Center container */
  .center { width:100%; max-width:1250px; margin:0 auto; padding:60px 30px 120px; box-sizing:border-box; }

  /* HERO area */
  .hero-wrap{ min-height:72vh; display:flex; align-items:center; justify-content:center; position:relative; }
  .hero-card{
    width:min(1080px,95%); padding:56px 48px; border-radius:22px;
    background: linear-gradient(180deg, rgba(255,255,255,0.016), rgba(255,255,255,0.006));
    border:1px solid rgba(255,255,255,0.03);
    box-shadow: 0 40px 120px rgba(8,6,15,0.65);
    position:relative; overflow:visible; transform-style:preserve-3d;
    backdrop-filter: blur(14px) saturate(140%); -webkit-backdrop-filter: blur(14px) saturate(140%);
  }

  /* Animated neon border - moving line */
  .hero-card::before{
    content:""; position:absolute; inset:-3px; border-radius:26px; padding:3px;
    background: linear-gradient(90deg, transparent, var(--neon1), var(--neon2), var(--neon1), transparent);
    background-size: 400% 400%;
    animation: borderShift 6s linear infinite;
    -webkit-mask:
      linear-gradient(#fff 0 0) content-box,
      linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
            mask-composite: exclude;
    pointer-events:none;
  }
  @keyframes borderShift{ 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }

  /* Subtle inner glow line that sweeps */
  .hero-card .line-sweep{ position:absolute; left:-10%; top:0; width:120%; height:160%; pointer-events:none; transform:rotate(-10deg); opacity:.06; background:linear-gradient(90deg, transparent, #ffffff 20%, transparent 40%); animation: sweep 8s linear infinite; mix-blend-mode:overlay; }
  @keyframes sweep{ 0%{transform:translateX(-35%) rotate(-10deg)} 100%{transform:translateX(35%) rotate(-10deg)} }

  .hero-title{ font-size:56px; margin:0; font-weight:900; letter-spacing:1px; color:transparent; background: linear-gradient(90deg,var(--neon1),var(--neon2)); -webkit-background-clip:text; background-clip:text; }
  .hero-tag{ margin-top:12px; font-size:18px; color:rgba(210,230,255,0.85); font-weight:600; }
  .type { margin-top:8px; font-weight:800; color:rgba(220,240,255,0.95); font-size:18px; }

  /* floating rings behind hero */
  .rings { position:absolute; inset:auto; left:50%; transform:translateX(-50%); top:30%; z-index:0; pointer-events:none; filter:blur(16px); opacity:0.65; }
  .ring { width:820px; height:420px; border-radius:50%; border:1px solid rgba(120,40,180,0.12); box-shadow: inset 0 0 120px rgba(120,40,180,0.08); transform:translateZ(0); animation: floaty 12s ease-in-out infinite; }
  .ring.r2{ width:1080px; height:540px; border:1px solid rgba(100,200,255,0.04); animation-duration:18s; opacity:0.55; filter:blur(24px) saturate(140%); }
  @keyframes floaty { 0%{transform:translate(-50%,-2%) scale(1)} 50%{transform:translate(-50%,2%) scale(1.01)} 100%{transform:translate(-50%,-2%) scale(1)} }

  /* name reflection / chrome */
  .hero-title-reflect { position: absolute; left:0; right:0; top:calc(100% - 22px); text-align:center; color: rgba(255,255,255,0.04); transform: translateY(10px) scaleY(-1); filter: blur(8px); opacity:0.35; pointer-events:none; }

  /* CTA */
  .cta { margin-top:20px; display:flex; gap:12px; justify-content:center; z-index:4; }
  .btn {
    padding:12px 20px; border-radius:999px; font-weight:800; border:none; cursor:pointer;
    background: linear-gradient(90deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
    color: #eaf6ff; box-shadow: 0 10px 30px rgba(6,6,10,0.5);
  }
  .btn.primary { background: linear-gradient(90deg,var(--neon1),var(--neon2)); color:#0a0710; box-shadow: 0 18px 60px rgba(120,40,180,0.26); }

  /* page grid for gallery/blog */
  .grid { display:grid; grid-template-columns: 1fr 1fr; gap:28px; margin-top:36px; align-items:start; }
  .glass { background: linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.006)); padding:16px; border-radius:12px; border:1px solid rgba(255,255,255,0.02); box-shadow: 0 14px 40px rgba(6,6,10,0.5); }

  .section-title { font-weight:800; color:#dff3ff; display:flex; align-items:center; gap:8px; margin-bottom:12px; }

  /* masonry gallery */
  .masonry { column-count:2; column-gap:12px; }
  .masonry-item { break-inside: avoid; margin-bottom:12px; border-radius:10px; overflow:hidden; transition: transform .28s ease; }
  .masonry-item img { width:100%; display:block; border-radius:10px; transform-origin:center; transition: transform .28s ease; }
  .masonry-item:hover { transform: translateY(-8px); }
  .masonry-item:hover img { transform: scale(1.06); filter: drop-shadow(0 20px 50px rgba(120,40,180,0.25)); }

  /* Chat orb & popup */
  .chat-orb { position:fixed; right:28px; bottom:28px; z-index:9999; width:78px; height:78px; border-radius:999px;
              display:flex; align-items:center; justify-content:center; cursor:pointer; background:linear-gradient(90deg,var(--neon1),var(--neon2));
              box-shadow:0 30px 90px rgba(120,40,180,0.22); color:#0b0410; font-size:28px; font-weight:800; }
  .chat-popup { position:fixed; right:28px; bottom:112px; z-index:9999; width:380px; max-width:92vw; display:none; border-radius:12px; overflow:hidden; }
  .chat-header { padding:10px 12px; background:linear-gradient(90deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); font-weight:800; color:#eaf6ff; }
  .chat-body { padding:10px; max-height:280px; overflow:auto; background:#06030a; color:var(--muted); }
  .chat-row { display:flex; gap:8px; padding:10px; background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); }

  /* responsive */
  @media (max-width:980px){
    .masonry { column-count:1; }
    .grid { grid-template-columns: 1fr; }
    .hero-title { font-size:40px; }
  }
</style>
</head>
<body>
<canvas id="bgCanvas" aria-hidden="true"></canvas>
<div class="overlay-aurora" aria-hidden="true">
  <!-- aurora svg gradient layers -->
  <svg width="100%" height="100%" style="position:fixed; inset:0; z-index:1; pointer-events:none;">
    <defs>
      <linearGradient id="g1" x1="0%" x2="100%">
        <stop offset="0%" stop-color="#6b1aff" stop-opacity="0.06"/>
        <stop offset="50%" stop-color="#3bb8ff" stop-opacity="0.03"/>
        <stop offset="100%" stop-color="#6b1aff" stop-opacity="0.06"/>
      </linearGradient>
      <filter id="f1" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="120" result="blur"/>
        <feColorMatrix type="matrix" values="1 0 0 0 0
                                             0 1 0 0 0
                                             0 0 1 0 0
                                             0 0 0 0.8 0"/>
      </filter>
    </defs>
    <ellipse cx="25%" cy="20%" rx="500" ry="200" fill="url(#g1)" filter="url(#f1)"></ellipse>
    <ellipse cx="70%" cy="70%" rx="680" ry="300" fill="url(#g1)" filter="url(#f1)"></ellipse>
  </svg>
</div>

<div class="page">
  <div class="center">
    <section class="hero-wrap" aria-label="Hero">
      <div class="hero-card" id="heroCard" role="banner">
        <div class="rings" aria-hidden="true">
          <div class="ring"></div>
          <div class="ring r2"></div>
        </div>
        <div class="line-sweep" aria-hidden="true"></div>

        <div style="position:relative; z-index:4;">
          <h1 class="hero-title" id="heroTitle">ARYAN SHARMA</h1>
          <div class="hero-title-reflect" id="reflect">ARYAN SHARMA</div>
          <div class="hero-tag">Welcome to my personal website!</div>
          <div class="type" id="typeLine">I'm a <span id="roleword">web developer</span></div>

          <div class="cta">
            <a class="btn primary" href="/resume.pdf" target="_blank" rel="noreferrer">Download Resume</a>
            <a class="btn" href="%%LINKEDIN%%" target="_blank" rel="noreferrer">LinkedIn</a>
            <a class="btn" href="%%INSTAGRAM%%" target="_blank" rel="noreferrer">Instagram</a>
          </div>
        </div>
      </div>
    </section>

    <!-- content -->
    <section class="grid" aria-label="Content">
      <div>
        <div class="glass">
          <div class="section-title">📸 Photos (Gallery)</div>
          <div class="masonry" id="galleryNode" aria-live="polite"></div>
        </div>

        <div style="height:22px"></div>

        <div class="glass">
          <div class="section-title">📁 Projects</div>
          <div style="display:flex;flex-direction:column;gap:10px;">
            <div style="padding:12px;border-radius:8px;background:rgba(255,255,255,0.015);font-weight:700">Chatbot Website <div style="font-size:13px;font-weight:400;opacity:0.85">Client Q&A demo</div></div>
            <div style="padding:12px;border-radius:8px;background:rgba(255,255,255,0.015);font-weight:700">Portfolio Builder <div style="font-size:13px;font-weight:400;opacity:0.85">Template & theme</div></div>
            <div style="padding:12px;border-radius:8px;background:rgba(255,255,255,0.015);font-weight:700">AI Experiments <div style="font-size:13px;font-weight:400;opacity:0.85">Small ML projects</div></div>
          </div>
        </div>
      </div>

      <div>
        <div class="glass">
          <div class="section-title">✍️ Writings (Anonymous)</div>
          <div id="anonNode"></div>
        </div>

        <div style="height:22px"></div>

        <div class="glass">
          <div class="section-title">📰 Blog Posts</div>
          <div id="postsNode"></div>
        </div>
      </div>
    </section>

    <div style="height:34px"></div>

    <footer style="opacity:0.9; color: #cde8ff; display:flex; justify-content:space-between; align-items:center;">
      <div>© %%YEAR%% Aryan Sharma</div>
      <div style="display:flex;gap:12px;align-items:center;">
        <div style="font-weight:700">Built with ❤️</div>
        <a href="%%LINKEDIN%%" style="color:inherit; text-decoration:underline" target="_blank" rel="noreferrer">LinkedIn</a>
        <a href="%%INSTAGRAM%%" style="color:inherit; text-decoration:underline" target="_blank" rel="noreferrer">Instagram</a>
      </div>
    </footer>

  </div>
</div>

<div class="chat-orb" id="chatOrb" title="Ask me about Aryan">✦</div>

<div class="chat-popup" id="chatPopup" aria-hidden="true">
  <div class="chat-header">Ask me about Aryan ☕</div>
  <div class="chat-body" id="chatBody"></div>
  <div class="chat-row">
    <input id="chatInput" placeholder="Type a question..." style="flex:1;padding:8px;border-radius:8px;border:none;background:rgba(255,255,255,0.03);color:var(--muted)"/>
    <button id="chatSend" style="padding:8px 10px;border-radius:8px;border:none;background:linear-gradient(90deg,var(--neon1),var(--neon2));font-weight:800">Send</button>
  </div>
</div>

<script>
  // Inject DATA from Python (placeholder replaced)
  const DATA = %%DATA_JSON%%;

  // ---------- Canvas: stars + particles + parallax lighting ----------
  const canvas = document.getElementById('bgCanvas');
  const ctx = canvas.getContext('2d');
  function resize(){ canvas.width = innerWidth; canvas.height = innerHeight; }
  resize(); window.addEventListener('resize', resize);

  // stars
  const stars = [];
  const STAR_COUNT = Math.floor((innerWidth*innerHeight)/8000) + 120;
  for(let i=0;i<STAR_COUNT;i++){
    stars.push({
      x: Math.random()*canvas.width,
      y: Math.random()*canvas.height,
      r: Math.random()*1.6 + 0.2,
      vx: (Math.random()*0.2)-0.1,
      vy: (Math.random()*0.05)-0.02,
      a: Math.random()*0.9+0.1
    });
  }

  // particles for reactive effect
  const particles = [];
  function spawnParticle(x,y){
    particles.push({x,y,vx:(Math.random()-0.5)*2, vy:(Math.random()-0.5)*2, r: Math.random()*3+1, life: 60 + Math.random()*80, age:0});
  }

  let t=0, mx=innerWidth/2, my=innerHeight/2;
  window.addEventListener('mousemove', (e)=>{ mx=e.clientX; my=e.clientY; if(Math.random() < 0.08) spawnParticle(e.clientX,e.clientY); });

  function draw(){
    t+=0.01;
    ctx.clearRect(0,0,canvas.width,canvas.height);

    // subtle nebula gradient
    const g = ctx.createLinearGradient(0,0,canvas.width,canvas.height);
    g.addColorStop(0, '#04000e');
    g.addColorStop(0.45, '#1c0026');
    g.addColorStop(1, '#04000a');
    ctx.fillStyle = g; ctx.fillRect(0,0,canvas.width,canvas.height);

    // moving soft glow (parallax)
    const cx = canvas.width*0.6 + Math.sin(t*0.6)*140;
    const cy = canvas.height*0.35 + Math.cos(t*0.9)*120;
    const rn = ctx.createRadialGradient(cx,cy,0,cx,cy,Math.max(canvas.width,canvas.height));
    rn.addColorStop(0, 'rgba(160,60,200,0.075)');
    rn.addColorStop(0.35, 'rgba(50,150,220,0.03)');
    rn.addColorStop(1, 'rgba(0,0,0,0.0)');
    ctx.globalCompositeOperation = 'lighter';
    ctx.fillStyle = rn; ctx.fillRect(0,0,canvas.width,canvas.height);
    ctx.globalCompositeOperation = 'source-over';

    // stars
    for(const s of stars){
      s.x += s.vx + Math.sin(t + s.x*0.0007)*0.02;
      s.y += s.vy;
      if(s.x < -10) s.x = canvas.width + 10;
      if(s.x > canvas.width + 10) s.x = -10;
      if(s.y < -10) s.y = canvas.height + 10;
      if(s.y > canvas.height + 10) s.y = -10;

      ctx.beginPath();
      ctx.fillStyle = 'rgba(255,255,255,' + (0.2 + 0.8 * Math.abs(Math.sin((s.x + s.y + t*80)/40))) + ')';
      ctx.arc(s.x, s.y, s.r, 0, Math.PI*2);
      ctx.fill();
    }

    // particles
    for(let i = particles.length-1; i>=0; i--){
      const p = particles[i];
      p.age++;
      p.x += p.vx; p.y += p.vy;
      const life = 1 - (p.age / p.life);
      if(life <= 0){ particles.splice(i,1); continue; }
      ctx.beginPath();
      ctx.fillStyle = 'rgba(200,140,255,' + (0.25 * life) + ')';
      ctx.arc(p.x, p.y, p.r * life, 0, Math.PI*2);
      ctx.fill();
    }

    requestAnimationFrame(draw);
  }
  draw();

  // ---------- Hero parallax tilt + rings subtle motion ----------
  const hero = document.getElementById('heroCard');
  document.addEventListener('mousemove', e => {
    const cx = innerWidth/2, cy = innerHeight/2;
    const dx = (e.clientX - cx) / cx;
    const dy = (e.clientY - cy) / cy;
    hero.style.transform = `perspective(1200px) rotateX(${dy*6}deg) rotateY(${dx*6}deg) translateZ(10px)`;
    // ring motion achieved with CSS animation; we pass small css vars for subtle shift
    hero.style.setProperty('--rx', (dx*10)+'px');
    hero.style.setProperty('--ry', (dy*6)+'px');
  });
  hero.addEventListener('mouseleave', ()=> hero.style.transform = 'none');

  // ---------- Typewriter roles ----------
  (function(){
    const words = ["web developer", "writer", "learner", "tech enthusiast", "video editor"];
    let idx=0, pos=0, fwd=true;
    const el = document.getElementById('roleword');
    function tick(){
      const w = words[idx];
      if(fwd){
        pos++; el.textContent = w.slice(0,pos);
        if(pos === w.length){ fwd=false; setTimeout(tick,900); return; }
      } else {
        pos--; el.textContent = w.slice(0,pos);
        if(pos === 0){ fwd=true; idx=(idx+1)%words.length; setTimeout(tick,400); return; }
      }
      setTimeout(tick,70);
    }
    tick();
  })();

  // ---------- Fill gallery & posts & anon ----------
  (function(){
    const g = DATA.gallery || [];
    const galNode = document.getElementById('galleryNode');
    if(!g || g.length === 0){
      galNode.innerHTML = '<div style="color:rgba(200,220,255,0.7);padding:8px">No images in gallery/ — upload images to the folder.</div>';
    } else {
      galNode.innerHTML = '';
      g.forEach((src,i)=>{
        const d = document.createElement('div');
        d.className = 'masonry-item';
        d.innerHTML = `<img src="${src}" alt="gallery-${i}">`;
        galNode.appendChild(d);
      });
    }

    const posts = DATA.posts || [];
    const postsNode = document.getElementById('postsNode');
    if(!posts || posts.length === 0){
      postsNode.innerHTML = '<div style="color:rgba(200,220,255,0.7);padding:6px">No blog posts yet.</div>';
    } else {
      postsNode.innerHTML = '';
      posts.forEach(p=>{
        const card = document.createElement('div');
        card.style.padding = '12px';
        card.style.borderRadius = '8px';
        card.style.marginBottom = '10px';
        card.style.background = 'linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.007))';
        card.innerHTML = `<div style="font-weight:700;color:#dff3ff">${p.title}</div><div style="font-size:13px;color:rgba(200,220,255,0.6)">${p.date}</div><div style="margin-top:8px;color:rgba(210,230,255,0.9)">${p.html}</div>`;
        postsNode.appendChild(card);
      });
    }

    const anon = DATA.anon || [];
    const anonNode = document.getElementById('anonNode');
    if(!anon || anon.length === 0){
      anonNode.innerHTML = '<div style="color:rgba(200,220,255,0.65)">No anonymous writings yet.</div>';
    } else {
      anonNode.innerHTML = '';
      anon.forEach(m=>{
        const el = document.createElement('div');
        el.style.padding = '10px';
        el.style.borderRadius = '8px';
        el.style.marginBottom = '10px';
        el.style.background = 'rgba(255,255,255,0.01)';
        el.innerHTML = `<div style="color:rgba(220,235,255,0.95)">${m}</div>`;
        anonNode.appendChild(el);
      });
    }
  })();

  // ---------- Chatbot (client-side rules) ----------
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
      el.style.padding = '8px';
      el.style.marginBottom = '8px';
      el.style.borderRadius = '10px';
      if(who === 'user'){ el.style.background = 'rgba(255,255,255,0.06)'; el.style.textAlign = 'right'; }
      else { el.style.background = 'linear-gradient(90deg, rgba(120,60,220,0.06), rgba(150,80,230,0.03))'; }
      body.appendChild(el);
      body.scrollTop = body.scrollHeight;
    }

    orb.addEventListener('click', ()=>{
      popup.style.display = popup.style.display === 'block' ? 'none' : 'block';
      if(popup.style.display === 'block' && body.children.length === 0) {
        addMsg("Hi — I'm Aryan's assistant. Ask me anything about Aryan ☕");
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
        if(!out){
          if(lq.includes('name')) out = "Aryan Sharma — that guy with stories & coffee.";
          else if(lq.includes('study')||lq.includes('college')) out = facts["what is aryan currently studying"];
          else out = "Ask me anything about Aryan ☕🙂!";
        }
        addMsg(out, 'bot');
      }, 300 + Math.random()*400);
    });
    input.addEventListener('keydown', e=>{ if(e.key === 'Enter') send.click(); });
  })();

</script>
</body>
</html>
"""

# safe replacements for placeholders (no f-strings)
html = html.replace("%%DATA_JSON%%", json.dumps(DATA))
html = html.replace("%%LINKEDIN%%", SOCIAL["linkedin"])
html = html.replace("%%INSTAGRAM%%", SOCIAL["instagram"])
html = html.replace("%%YEAR%%", str(DATA["year"]))

# ---------------- Render component ----------------
# make component tall and allow internal scrolling; we forced Streamlit containers transparent above
components.html(html, height=980, scrolling=True)

# ---------------- provide fallback streamlit UI (below the component) ----------------
st.markdown("---")
st.markdown("### Quick Controls & Notes")
st.markdown("- Add images to `gallery/` to populate the gallery (jpg/png/webp/gif).")
st.markdown("- Add markdown files (`.md`) to `blog_posts/` to create blog posts (use YAML frontmatter optional).")
st.markdown("- Anonymous writings appear in the Writings card — or add via the small form below (local session only).")

with st.expander("Post anonymously (local session)"):
    txt = st.text_area("Write anonymously...", height=140)
    if st.button("Send anonymously"):
        if txt.strip():
            st.session_state.anon_messages.insert(0, txt.strip())
            st.success("Saved locally — refresh the page to see it in the UI.")

st.markdown("---")
st.write("LinkedIn:", SOCIAL["linkedin"])
st.write("Instagram:", SOCIAL["instagram"])
