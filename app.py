# app.py
import os
import re
import json
import time
import streamlit as st
import streamlit.components.v1 as components
from markdown import markdown

st.set_page_config(page_title="Aryan Sharma — Premium", layout="wide", initial_sidebar_state="collapsed")

# -------------------- paths --------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
GALLERY_DIR = os.path.join(BASE_DIR, "gallery")
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")

# -------------------- helpers --------------------
def get_gallery_images():
    if not os.path.exists(GALLERY_DIR):
        return []
    files = [f for f in sorted(os.listdir(GALLERY_DIR)) if f.lower().endswith((".jpg",".jpeg",".png",".webp",".gif"))]
    return [os.path.join("gallery", f) for f in files]

def get_blog_posts():
    out = []
    if not os.path.exists(POSTS_DIR):
        return out
    for fn in sorted(os.listdir(POSTS_DIR)):
        if not fn.endswith(".md"): continue
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
                    k,v = line.split(':',1)
                    meta[k.strip()] = v.strip()
            body = txt[m.end():].strip()
        out.append({
            "title": meta.get("title", fn[:-3].replace('-', ' ').title()),
            "date": meta.get("date", ""),
            "html": markdown(body)
        })
    return out

# -------------------- facts for chatbot --------------------
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
    "what’s something aryan can’t live without": "Coffee. None 😅.",
    "what makes aryan unique": "His ability to make people laugh even when he’s not trying.",
    "what’s aryan’s favorite weather": "Cold breeze + warm coffee = perfection.",
    "how does aryan relax": "Storytelling, music, and wandering thoughts.",
    "what is aryan passionate about": "Tech, creativity, and turning ideas into reality.",
    "what is aryan learning right now": "New tech skills… one coffee at a time.",
    "what type of person is aryan": "Calm, humorous, and secretly a deep thinker.",
    "what’s aryan’s favourite thing to do": "Observe life and turn it into funny, relatable stories.",
    "what does aryan dream about": "A life full of learning, creativity, and endless coffee."
}

# -------------------- session state --------------------
if "anon_msgs" not in st.session_state:
    st.session_state.anon_msgs = []

# If user submits the built-in Streamlit form, save message
# We'll render an in-page form inside the component as well (JS posts) but keep this for backup
with st.sidebar:
    st.write(" ")
    st.write(" ")
    # Keep sidebar minimal (hidden by CSS later) - but include a small helper to add posts directly.
    with st.form("side_anon", clear_on_submit=True):
        t = st.text_area("Share anonymously (sidebar backup)", height=80, placeholder="Write anonymously...")
        if st.form_submit_button("Send anonymously"):
            if t.strip():
                st.session_state.anon_msgs.insert(0, {"msg": t.strip(), "time": time.asctime()})
                st.success("Saved — Will appear in the Writings section.")

# -------------------- prepare data for HTML --------------------
gallery = get_gallery_images()
posts = get_blog_posts()
anon = st.session_state.anon_msgs

DATA = {
    "gallery": gallery,
    "posts": posts,
    "anon": anon,
    "facts": ARYAN_FACTS,
    "social": {
        "linkedin": "https://www.linkedin.com/in/aryan-sharma99999",
        "instagram": "https://instagram.com/aryanxsharma26"
    },
    "year": time.localtime().tm_year
}

DATA_JSON = json.dumps(DATA)

# -------------------- HTML + CSS + JS (big component) --------------------
# This HTML is self-contained and implements:
# - Nebula background (canvas)
# - starfield with trailing
# - hero with parallax / 3D mouse move
# - cinematic sweeping spotlight on name
# - masonry gallery with hover neon glow (CSS + JS)
# - chatbot orb with intro bubble once on first open
# - neon social icons
# - full-screen scroll sections
html = f"""
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
    --muted: rgba(220,230,255,0.7);
  }
  html,body{height:100%;margin:0;padding:0;background:var(--bg1);font-family:Inter,system-ui,-apple-system,'Segoe UI',Roboto;}
  /* Canvas BG covers everything */
  #nebulaCanvas { position:fixed; inset:0; z-index:0; display:block; width:100vw; height:100vh; pointer-events:none; }
  /* Subtle vignette overlay */
  .vignette { position:fixed; inset:0; z-index:1; background: radial-gradient(ellipse at 25% 20%, rgba(255,255,255,0.02), transparent 12%, rgba(0,0,0,0.6) 70%); pointer-events:none; }

  /* page content layer */
  .app { position:relative; z-index:5; min-height:100vh; display:flex; align-items:stretch; justify-content:center; overflow:hidden; }

  /* center column */
  .center { width:100%; max-width:1200px; margin:0 auto; padding:64px 24px; box-sizing:border-box; color:var(--muted); }

  /* scroll sections */
  section { padding:60px 0; display:block; box-sizing:border-box; min-height:60vh; }
  .hero-section{ min-height:78vh; display:flex; align-items:center; justify-content:center; }

  /* Hero card (3D parallax) */
  .hero-card{
    width:min(1100px,94%); border-radius:20px; padding:46px 44px;
    background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
    border:1px solid rgba(255,255,255,0.03);
    box-shadow: 0 40px 120px rgba(4,2,10,0.7), inset 0 -10px 40px rgba(0,0,0,0.12);
    transform-style:preserve-3d;
    transition: transform 0.18s ease, box-shadow 0.18s ease;
    position:relative; overflow:visible;
    backdrop-filter: blur(10px) saturate(140%);
  }
  .hero-name{ font-size:56px; font-weight:900; margin:0; letter-spacing:1px; display:inline-block; position:relative; color: transparent;
     background: linear-gradient(90deg, rgba(255,255,255,0.12), var(--neon));
     -webkit-background-clip:text; background-clip:text;
  }
  /* cinematic sweeping spotlight - pseudo */
  .spotlight { position:absolute; left:0; right:0; top:-40%; bottom:-40%; z-index:0; pointer-events:none; mix-blend-mode:overlay; opacity:0.9; }
  .hero-sub{ margin-top:14px; color: rgba(210,230,255,0.85); font-weight:600; }

  /* typewriter */
  .type { margin-top:10px; font-weight:700; color:rgba(200,220,255,0.92); font-size:18px; }

  /* neon outline pulse */
  .neon-outline { position:absolute; inset:-8px; border-radius:24px; pointer-events:none; box-shadow: 0 0 40px rgba(197,108,255,0.14), inset 0 0 16px rgba(94,243,255,0.03); border:2px solid rgba(197,108,255,0.06); }

  /* CTA */
  .cta { margin-top:22px; display:flex; gap:12px; justify-content:center; z-index:5; position:relative; }
  .btn { padding:12px 18px; border-radius:999px; font-weight:800; cursor:pointer; border:none; }
  .btn-primary { background: linear-gradient(90deg,var(--neon),var(--neon-2)); color:#0b0b10; box-shadow: 0 8px 30px rgba(120,50,160,0.28); }
  .btn-outline { background:transparent; color:var(--muted); border:1px solid rgba(255,255,255,0.04); }

  /* Masonry gallery card + posts card */
  .grid-wrap{ display:grid; grid-template-columns: 1fr 1fr; gap:28px; align-items:start; margin-top:26px; }
  .left-col, .right-col { min-height:120px; }
  .glass{ background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); border-radius:12px; padding:14px; border:1px solid rgba(255,255,255,0.03);
        box-shadow:0 12px 36px rgba(6,6,10,0.45); }
  .section-title{ font-weight:800; color: #dff3ff; display:flex; align-items:center; gap:10px; margin-bottom:10px; }

  /* masonry gallery */
  .masonry { column-count: 2; column-gap: 12px; }
  .masonry-item { break-inside: avoid; margin-bottom:12px; position:relative; overflow:hidden; border-radius:10px; transform-origin:center; transition: transform .25s ease, box-shadow .25s ease; }
  .masonry-item img{ width:100%; display:block; border-radius:10px; transform-origin:center; transition: transform .28s ease; }
  .masonry-item:hover{ transform: translateY(-8px) rotateX(2deg) translateZ(6px); box-shadow:0 24px 80px rgba(30,8,40,0.6); }
  .masonry-item:hover img{ transform: scale(1.06); filter: drop-shadow(0 12px 30px rgba(140,40,200,0.22)); }
  .masonry-item::after{ content:''; position:absolute; inset:0; border-radius:10px; pointer-events:none; box-shadow: inset 0 0 0 2px rgba(197,108,255,0.03); mix-blend-mode:screen; }

  /* posts */
  .post-card{ margin-bottom:12px; padding:14px; border-radius:10px; background: linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.007)); border:1px solid rgba(255,255,255,0.025); }
  .post-card h3{ margin:0;color:#eaf6ff;font-weight:800; }
  .post-card .date{ font-size:12px; color:rgba(200,220,255,0.6); margin-bottom:8px; }

  /* neon social icons */
  .socials{ display:flex; gap:12px; align-items:center; }
  .socials a{ text-decoration:none; color:var(--muted); padding:8px; border-radius:8px; display:inline-flex; align-items:center; gap:8px; transition: transform .18s ease, box-shadow .18s ease; border:1px solid rgba(255,255,255,0.02); }
  .socials a:hover{ transform: translateY(-4px); box-shadow: 0 18px 60px rgba(180,80,220,0.12); color: white; }
  .socials a .dot{ width:12px; height:12px; border-radius:999px; background: linear-gradient(90deg,var(--neon),var(--neon-2)); box-shadow: 0 6px 26px rgba(140,40,200,0.45); }

  /* chat orb (3D rotating gem) */
  .chat-orb { position:fixed; right:28px; bottom:28px; z-index:9999; width:72px; height:72px; border-radius:999px; display:flex; align-items:center; justify-content:center; cursor:pointer;
    background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.06), rgba(0,0,0,0.25)); border:2px solid rgba(197,108,255,0.28); box-shadow: 0 30px 80px rgba(120,40,180,0.16); transition: transform .18s ease; }
  .chat-orb:hover { transform: translateY(-6px) rotate(-6deg) scale(1.02); }
  .chat-orb .inner { width:46px; height:46px; border-radius:50%; background: linear-gradient(90deg,var(--neon),var(--neon-2)); display:flex; align-items:center; justify-content:center; color:#07030a; font-weight:800; box-shadow: 0 10px 30px rgba(140,40,200,0.38); transform-origin:center; animation: rotateOrb 6s linear infinite; }
  @keyframes rotateOrb { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

  .chat-popup{ position:fixed; right:28px; bottom:112px; z-index:9999; width:380px; max-width:92vw; border-radius:12px; overflow:hidden; display:none; }
  .chat-head{ padding:12px; background: linear-gradient(90deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); font-weight:800; color:#eaf6ff; border-bottom:1px solid rgba(255,255,255,0.02); }
  .chat-body{ padding:12px; max-height:260px; overflow:auto; background: linear-gradient(180deg, rgba(10,8,14,0.98), rgba(6,4,8,0.98)); color:var(--muted); }
  .chat-input{ display:flex; gap:8px; padding:12px; background: linear-gradient(180deg, rgba(6,6,8,0.98), rgba(8,8,10,0.98)); border-top:1px solid rgba(255,255,255,0.02); }
  .chat-input input{ flex:1; padding:8px 10px; border-radius:10px; border:none; background: rgba(255,255,255,0.03); color:var(--muted); }

  /* responsive adjustments */
  @media (max-width:980px){
    .grid-wrap{ grid-template-columns: 1fr; }
    .masonry { column-count: 1; }
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
              <a class="btn btn-outline" id="linkLinked" target="_blank" href="{DATA[social][linkedin]}">LinkedIn</a>
              <a class="btn btn-outline" id="linkInsta" target="_blank" href="{DATA[social][instagram]}">Instagram</a>
            </div>
          </div>
        </div>
        <div class="spotlight" id="spotlight" aria-hidden="true"></div>
      </div>
    </section>

    <!-- GALLERY / WRITINGS / PROJECTS -->
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
            <div id="anonList" style="min-height:120px;"> </div>
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
          <div style="font-weight:800;font-size:15px;color:#eaf6ff">© {DATA[year]} Aryan Sharma</div>
          <div style="color:rgba(200,220,255,0.7)">Built with ❤️</div>
        </div>
        <div class="socials">
          <a href="{DATA[social][linkedin]}" target="_blank" rel="noreferrer"><span class="dot"></span> LinkedIn</a>
          <a href="{DATA[social][instagram]}" target="_blank" rel="noreferrer"><span class="dot"></span> Instagram</a>
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
  // DATA injected
  const DATA = {json_data} ;

  // ---------------- Nebula canvas: volumetric nebula + starfield + trails ----------------
  (function(){
    const canvas = document.getElementById('nebulaCanvas');
    const ctx = canvas.getContext('2d');
    function resize(){ canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
    resize(); window.addEventListener('resize', resize);

    // create stars
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

    // moving trail particles
    const trails = [];
    function spawnTrail(x,y,vx,vy){
      trails.push({x:x,y:y,vx:vx,vy:vy,life:Math.random()*60+40,age:0});
    }

    let t = 0;
    function draw(){
      t += 0.005;
      // base gradient (dark -> purple)
      const g = ctx.createLinearGradient(0,0,canvas.width,canvas.height);
      g.addColorStop(0, '#08000a');
      g.addColorStop(0.45, '#1a0022');
      g.addColorStop(1, '#06000a');
      ctx.fillStyle = g;
      ctx.fillRect(0,0,canvas.width,canvas.height);

      // nebula soft radial blur (animated)
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

      // subtle noise glow overlay (vignette)
      const noise = ctx.createLinearGradient(canvas.width*0.2,0, canvas.width, canvas.height);
      noise.addColorStop(0, 'rgba(80,10,120,0.02)');
      noise.addColorStop(1, 'rgba(0,0,0,0.08)');
      ctx.fillStyle = noise;
      ctx.fillRect(0,0,canvas.width,canvas.height);

      // stars
      for(const s of stars){
        s.x += s.vx;
        s.y += s.vy;
        if(s.x < -10) s.x = canvas.width + 10;
        if(s.x > canvas.width + 10) s.x = -10;
        if(s.y < -10) s.y = canvas.height + 10;
        if(s.y > canvas.height + 10) s.y = -10;

        // twinkle
        const a = s.alpha * (0.6 + 0.4 * Math.sin((s.x + s.y + t*100)/60));
        ctx.beginPath();
        ctx.fillStyle = 'rgba(255,255,255,' + a + ')';
        ctx.arc(s.x, s.y, s.r, 0, Math.PI*2);
        ctx.fill();

        // occasionally spawn a trail
        if(Math.random() < 0.002){
          spawnTrail(s.x, s.y, s.vx*6, s.vy*6 - 1.4);
        }
      }

      // trails
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

  // ---------------- Hero parallax & spotlight sweep ----------------
  (function(){
    const hero = document.getElementById('heroCard');
    const name = document.getElementById('heroName');
    const spotlight = document.getElementById('spotlight');
    let rect = hero.getBoundingClientRect();

    function onMove(e){
      const cx = window.innerWidth/2;
      const cy = window.innerHeight/2;
      const dx = (e.clientX - cx) / cx;
      const dy = (e.clientY - cy) / cy;
      const rx = dx * 8;
      const ry = dy * -6;
      hero.style.transform = `perspective(1200px) rotateX(${ry}deg) rotateY(${rx}deg) translateZ(6px)`;
      // spotlight follows mouse gently
      spotlight.style.background = `radial-gradient(circle at ${50 + dx*20}% ${40 + dy*10}%, rgba(255,255,255,0.02), transparent 18%)`;
    }
    window.addEventListener('mousemove', onMove);

    // cinematic sweeping light across name
    let sweep = 0;
    setInterval(()=> {
      sweep += 1;
      name.style.backgroundPosition = (sweep % 200) + "% 0%";
    }, 60);

    // subtle reset when mouse leaves
    hero.addEventListener('mouseleave', ()=> {
      hero.style.transform = 'none';
    });
  })();

  // ---------------- Typewriter for roles ----------------
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

  // ---------------- Fill gallery (masonry) & posts & anon ----------------
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
      gallery.forEach((src,i) => {
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
      posts.forEach(p => {
        const c = document.createElement('div');
        c.className = 'post-card';
        c.innerHTML = `<div class="date">${p.date}</div><h3>${p.title}</h3><div style='margin-top:8px;color:rgba(220,235,255,0.95)'>${p.html}</div>`;
        postsArea.appendChild(c);
      });
    }

    const anonNode = document.getElementById('anonList');
    if(!anon || anon.length === 0){
      anonNode.innerHTML = "<div style='color:rgba(200,220,255,0.6);padding:8px'>No anonymous writings yet. Use the sidebar form or the 'Share' button to post.</div>";
    } else {
      anonNode.innerHTML = '';
      anon.forEach(a => {
        const el = document.createElement('div');
        el.className = 'glass';
        el.style.marginBottom = '8px';
        el.innerHTML = `<div style="color:rgba(220,235,255,0.95)">${a.msg}</div><div style="font-size:12px;color:rgba(180,200,220,0.6);margin-top:8px">${a.time}</div>`;
        anonNode.appendChild(el);
      });
    }
  })();

  // ---------------- Chat logic: intro bubble once + simple Q/A ----------------
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
      if(who === 'user'){
        el.style.background = 'rgba(255,255,255,0.06)'; el.style.textAlign = 'right';
      } else {
        el.style.background = 'linear-gradient(90deg, rgba(110,140,255,0.06), rgba(140,60,200,0.03))';
      }
      body.appendChild(el);
      body.scrollTop = body.scrollHeight;
    }

    // Intro bubble only the first time per page load (you can store to localStorage if persistent needed)
    let shownIntro = false;
    orb.addEventListener('click', ()=> {
      const open = popup.style.display === 'block';
      popup.style.display = open ? 'none' : 'block';
      if(!open && !shownIntro){
        addMsg("Hi — I'm Aryan's AI assistant. Ask me anything about Aryan ☕");
        shownIntro = true;
      }
      input.focus();
    });

    send.addEventListener('click', ()=> {
      const q = (input.value || '').trim();
      if(!q) return;
      addMsg(q, 'user');
      input.value = '';
      setTimeout(()=> {
        let lower = q.toLowerCase();
        let out = null;
        for(const k in facts) if(lower.includes(k)) { out = facts[k]; break; }
        if(!out){
          if(lower.includes('name')) out = "Aryan Sharma — that guy with stories & coffee.";
          else out = "Ask me anything about Aryan ☕🙂!";
        }
        addMsg(out,'bot');
      }, 350 + Math.random()*420);
    });
    input.addEventListener('keydown', function(e){ if(e.key === 'Enter'){ e.preventDefault(); send.click(); }});
  })();

  // small helper: show floating neon pulse when user scrolls near bottom (optional)
  (function(){
    const orb = document.getElementById('chatOrb');
    window.addEventListener('scroll', ()=>{
      const st = window.scrollY + window.innerHeight;
      const h = document.body.scrollHeight;
      if(h - st < 240){
        orb.style.transform = 'translateY(-6px) scale(1.02)';
      } else {
        orb.style.transform = 'none';
      }
    }, {passive:true});
  })();

</script>
</body>
</html>
""".replace("{json_data}", json.dumps(DATA)).replace("{DATA[social][linkedin]}", DATA["social"]["linkedin"]).replace("{DATA[social][instagram]}", DATA["social"]["instagram"]).replace("{DATA[year]}", str(DATA["year"]))

# render component: large height, scrolling inside component enabled (component is full page)
components.html(html, height=980, scrolling=True)

# -------------------- Force transparency of Streamlit UI wrappers --------------------
# Strong CSS to remove white backgrounds and let the canvas show through fully.
st.markdown("""
<style>
/* Make streamlit app background transparent */
html, body, .stApp, .main, .block-container, .css-1cpxqw2, .css-18e3th9 {
    background: transparent !important;
}

/* Hide default header & footer margins (some streamlit versions) */
header, footer { background: transparent !important; }

/* If your streamlit injects other wrappers, aggressively force them transparent */
[class^="css"] { background: transparent !important; }

/* remove top padding added by Streamlit block container */
.block-container { padding-top: 0 !important; }

/* Make sidebar invisible (we used a small sidebar backup form). If you need sidebar visible, remove this. */
.css-1d391kg { display: none !important; } /* common sidebar wrapper - may vary by version */
</style>
""", unsafe_allow_html=True)

# -------------------- Page notes for user --------------------
st.markdown("---")
st.markdown("**Notes & usage**")
st.markdown("- Upload images to the `gallery/` folder (jpg, png, webp, gif). They will appear in the Masonry gallery above.")
st.markdown("- Put Markdown posts into `blog_posts/` (use YAML frontmatter optional).")
st.markdown("- If any white blocks remain (Streamlit version differences), paste a screenshot and I'll patch the final CSS selectors.")
st.markdown("- Want voice-mode for the chat or persistent localStorage intro? I can add it next.")

# small footer links for fallback
st.write("LinkedIn:", DATA["social"]["linkedin"])
st.write("Instagram:", DATA["social"]["instagram"])
