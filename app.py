# app_preview.py
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Aryan Sharma (Preview)", layout="wide", initial_sidebar_state="collapsed")

html = r'''
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Aryan Sharma — Preview</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;700;800&display=swap" rel="stylesheet">
<style>
  :root{
    --neon1: #7b2cff;
    --neon2: #ff4dd2;
    --neon3: #3fb3ff;
    --glass: rgba(12,6,20,0.55);
    --card-bg: rgba(18,6,28,0.7);
    --muted: rgba(255,255,255,0.7);
  }
  html,body{height:100%;margin:0;font-family:'Poppins',sans-serif;overflow:hidden}
  body{color:#f2eefd}
  /* full-screen container */
  #root{position:fixed;inset:0;display:flex;flex-direction:column;align-items:stretch}

  /* animated canvas layers */
  canvas.bg, canvas.stars {position:fixed;left:0;top:0;width:100%;height:100%;z-index:0}
  .content {
    position:relative;
    z-index:4;
    width:100%;
    max-width:1200px;
    margin:80px auto 60px;
    padding:40px 48px 80px;
    border-radius:22px;
    background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
    box-shadow: 0 20px 70px rgba(0,0,0,0.6), inset 0 0 0 1px rgba(255,255,255,0.02);
    border: 2px solid rgba(124, 44, 255, 0.18);
    backdrop-filter: blur(6px);
    margin-top:80px;
  }

  .hero {
    display:flex;
    gap:30px;
    align-items:flex-start;
  }
  .hero-left {flex:1;min-width:280px}
  .hero-right {flex:2;padding-top:18px}
  .hero-title{font-weight:800;font-size:64px;line-height:0.95;color:var(--neon2);text-shadow:0 2px 0 rgba(0,0,0,0.4)}
  .hero-sub{font-weight:600;font-size:22px;color:rgba(255,255,255,0.9);margin-top:6px}
  .hero-line{margin-top:18px;color:rgba(255,255,255,0.8);max-width:900px;line-height:1.6}

  .role {
    margin-top:18px;
    font-size:20px;
    color:var(--neon3);
    font-weight:700;
    height:26px;
  }

  .buttons-row{margin-top:30px;display:flex;gap:12px;align-items:center}
  .btn {padding:10px 18px;border-radius:12px;border:none;background:linear-gradient(90deg,var(--neon2),var(--neon1));box-shadow:0 6px 20px rgba(124,44,255,0.15);cursor:pointer;color:#120517;font-weight:700}
  .icon-btn {background:transparent;border:2px solid rgba(255,255,255,0.04);padding:12px;border-radius:12px;color:#fff}

  .socials{margin-top:26px;display:flex;gap:12px}
  .social {width:44px;height:44px;border-radius:10px;background: rgba(255,255,255,0.03);display:flex;align-items:center;justify-content:center;border:1px solid rgba(255,255,255,0.02)}

  /* left floating neon icons */
  .left-floating {
    position:fixed;left:22px;top:180px;z-index:6;display:flex;flex-direction:column;gap:18px
  }
  .float-btn {
    width:58px;height:58px;border-radius:50%;display:flex;align-items:center;justify-content:center;
    border:3px solid rgba(139, 43, 255, 0.24);
    box-shadow:0 8px 30px rgba(123,44,255,0.06), 0 0 24px rgba(124,44,255,0.08) inset;
    background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
    cursor:pointer;backdrop-filter: blur(3px);
  }
  .float-btn .emoji{font-size:22px}

  /* chat bubble */
  .chat-bubble {
    position:fixed;right:28px;bottom:30px;z-index:8;
    display:flex;flex-direction:column;align-items:flex-end;gap:10px;
  }
  .chat-circle {
    width:70px;height:70px;border-radius:50%;display:flex;align-items:center;justify-content:center;
    background:linear-gradient(135deg,var(--neon3),var(--neon1));box-shadow:0 16px 40px rgba(59,16,83,0.5),0 0 18px rgba(124,44,255,0.25) inset;
    cursor:pointer;font-weight:800;color:#0b0210;font-size:13px;
    transition:transform .18s ease;
  }
  .chat-circle:hover{transform:translateY(-6px)}
  .chat-panel {
    width:340px;max-width:86vw;background:var(--card-bg);padding:16px;border-radius:14px;color:#fff;
    box-shadow:0 30px 90px rgba(0,0,0,0.6);display:none;
  }
  .chat-panel h4{margin:0 0 6px 0;color:var(--neon1)}
  .chat-panel .hint{font-size:13px;color:rgba(255,255,255,0.7);margin-bottom:8px}
  .chat-panel input {width:100%;padding:10px;border-radius:10px;border:1px solid rgba(255,255,255,0.06);margin-bottom:8px;background:rgba(0,0,0,0.35);color:#fff}

  /* modal */
  .modal {
    position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);min-width:320px;max-width:90vw;background:var(--card-bg);padding:20px;border-radius:12px;z-index:20;display:none;box-shadow:0 40px 120px rgba(0,0,0,0.7)
  }
  .modal h3{margin-top:0;color:var(--neon2)}
  .close {position:absolute;right:12px;top:12px;cursor:pointer;color:#fff;font-weight:700}

  /* responsive */
  @media (max-width:900px){
    .content{margin:20px; padding:18px; border-radius:12px}
    .hero-title{font-size:36px}
    .left-floating{left:8px; top:120px}
    .chat-panel{width:260px}
  }
</style>
</head>
<body>
<canvas id="bg" class="bg"></canvas>
<canvas id="stars" class="stars"></canvas>

<div id="root">
  <div class="content" role="main">
    <div class="hero">
      <div class="hero-left">
        <div class="hero-title">Aryan Sharma</div>
        <div class="hero-sub">Welcome to my personal website!</div>

        <div class="role">I'm a <span id="typeText" style="color:var(--neon2)"></span><span id="cursor" style="opacity:1">|</span></div>

        <div class="hero-line">I build polished websites, experiment with AI-driven tools, write, create, and edit videos. Use the floating icons to open photos, anonymous messages, or writings.</div>

        <div class="buttons-row">
          <button class="btn">Download Resume</button>
          <button class="icon-btn">Get In Touch</button>
        </div>

        <div class="socials">
          <a class="social" href="https://github.com/aryanxsharma26" target="_blank" title="GitHub" style="border:1px solid rgba(255,255,255,0.04)"><svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 .5C5.73.5.75 5.48.75 11.76c0 4.95 3.22 9.14 7.69 10.62.56.1.77-.24.77-.53 0-.26-.01-1.13-.02-2.05-3.13.68-3.79-1.6-3.79-1.6-.51-1.3-1.24-1.65-1.24-1.65-1.02-.7.08-.69.08-.69 1.13.08 1.73 1.16 1.73 1.16 1 .17 1.56.87 1.94 1.49.43.82 1.2 1.1 1.9.83.06-.65.39-1.1.71-1.35-2.5-.29-5.13-1.25-5.13-5.56 0-1.23.44-2.23 1.16-3.02-.12-.29-.5-1.45.11-3.02 0 0 .95-.31 3.12 1.16a10.8 10.8 0 0 1 5.67 0c2.17-1.47 3.12-1.16 3.12-1.16.61 1.57.23 2.73.11 3.02.72.79 1.16 1.79 1.16 3.02 0 4.32-2.64 5.27-5.16 5.55.4.35.76 1.03.76 2.08 0 1.5-.01 2.71-.01 3.08 0 .29.2.64.78.53 4.47-1.5 7.67-5.7 7.67-10.62C23.25 5.48 18.27.5 12 .5z" fill="#ffffff"/></svg></a>
          <a class="social" href="https://instagram.com/Aryansharma99999" target="_blank" title="Instagram" style="border:1px solid rgba(255,255,255,0.04)"><svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M7.5 2h9A5.5 5.5 0 0 1 22 7.5v9A5.5 5.5 0 0 1 16.5 22h-9A5.5 5.5 0 0 1 2 16.5v-9A5.5 5.5 0 0 1 7.5 2zM12 7.25a4.75 4.75 0 1 0 0 9.5 4.75 4.75 0 0 0 0-9.5zm5.2-1.45a1.05 1.05 0 1 0 0 2.1 1.05 1.05 0 0 0 0-2.1zM12 9.25a2.75 2.75 0 1 1 0 5.5 2.75 2.75 0 0 1 0-5.5z" fill="#fff"/></svg></a>
        </div>

      </div>

      <div class="hero-right">
        <!-- decorative empty right area to keep hero centered and neon border -->
        <div style="height:180px"></div>
      </div>
    </div>
  </div>
</div>

<!-- left floating menu -->
<div class="left-floating" role="navigation" aria-label="left menu">
  <div class="float-btn" onclick="openModal('galleryModal')" title="Photos">
    <div class="emoji">📷</div>
  </div>
  <div class="float-btn" onclick="openModal('anonModal')" title="Anonymous">
    <div class="emoji">📝</div>
  </div>
  <div class="float-btn" onclick="openModal('writingsModal')" title="Writings">
    <div class="emoji">✍️</div>
  </div>
</div>

<!-- chat -->
<div class="chat-bubble">
  <div id="chatPanel" class="chat-panel" role="dialog" aria-hidden="true">
    <h4>Aryan's Chatbot <span style="background:var(--neon3);padding:3px 6px;border-radius:6px;font-size:12px;color:#08020b">FAQ</span></h4>
    <div class="hint">Hi! Ask me questions about Aryan.</div>
    <input id="chatInput" placeholder="Type your question..." />
    <div style="display:flex;gap:8px;justify-content:flex-end">
      <button class="btn" onclick="sendChat()">Send</button>
    </div>
  </div>
  <div class="chat-circle" onclick="toggleChat()">
    Ask
  </div>
</div>

<!-- modals -->
<div id="galleryModal" class="modal" aria-hidden="true">
  <div class="close" onclick="closeModal('galleryModal')">✕</div>
  <h3>Photos Gallery</h3>
  <p style="color:rgba(255,255,255,0.8)">No photos yet — this area will show uploaded photos in your repository's gallery folder.</p>
</div>

<div id="anonModal" class="modal" aria-hidden="true">
  <div class="close" onclick="closeModal('anonModal')">✕</div>
  <h3>Anonymous Box</h3>
  <textarea id="anonText" style="width:100%;min-height:120px;border-radius:10px;padding:12px;background:rgba(0,0,0,0.35);border:1px solid rgba(255,255,255,0.04);color:#fff" placeholder="Share anonymously..."></textarea>
  <div style="margin-top:10px;display:flex;gap:10px;justify-content:flex-end">
    <button class="btn" onclick="submitAnon()">Send anonymously</button>
  </div>
</div>

<div id="writingsModal" class="modal" aria-hidden="true">
  <div class="close" onclick="closeModal('writingsModal')">✕</div>
  <h3>Writings & Blog</h3>
  <p style="color:rgba(255,255,255,0.85)">Latest: <strong>Still working on</strong> — posts will appear here. Use your blog_posts folder.</p>
</div>

<script>
/* ---------------------------
   Background shader (simple flow)
   --------------------------- */
const canvas = document.getElementById('bg');
const stars = document.getElementById('stars');
const ctx = canvas.getContext('2d');
const sctx = stars.getContext('2d');

function resize() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  stars.width = window.innerWidth;
  stars.height = window.innerHeight;
}
resize();
window.addEventListener('resize', resize);

/* Flow gradient using simple moving blobs */
let t0 = 0;
function flowFrame(t) {
  t0 = t*0.001;
  const w = canvas.width, h = canvas.height;
  const g = ctx.createLinearGradient(0,0,w,h);
  // animated color stops
  const a = 0.5 + 0.5*Math.sin(t0*0.3);
  const b = 0.5 + 0.5*Math.sin(t0*0.2 + 1.5);
  const c = 0.5 + 0.5*Math.sin(t0*0.27 + 2.5);
  g.addColorStop(0, `rgba(${120 + 80*a|0}, ${10 + 50*b|0}, ${180 + 60*c|0}, 1)`);
  g.addColorStop(0.5, `rgba(${200|0}, ${70 + 120*b|0}, ${170|0}, 1)`);
  g.addColorStop(1, `rgba(24,8,36,1)`);
  ctx.fillStyle = g;
  ctx.fillRect(0,0,w,h);

  // subtle radial highlight moving
  const rx = w*0.75 + Math.cos(t0*0.4)*w*0.15;
  const ry = h*0.7 + Math.sin(t0*0.35)*h*0.12;
  const rad = ctx.createRadialGradient(rx,ry,w*0.05, rx,ry,w*0.9);
  rad.addColorStop(0, "rgba(124,44,255,0.18)");
  rad.addColorStop(1, "rgba(0,0,0,0)");
  ctx.fillStyle = rad;
  ctx.fillRect(0,0,w,h);

  requestAnimationFrame(flowFrame);
}
requestAnimationFrame(flowFrame);

/* small star particles layer */
const starsArr = [];
for(let i=0;i<600;i++){
  starsArr.push({
    x: Math.random()*stars.width,
    y: Math.random()*stars.height,
    r: Math.random()*1.4 + 0.3,
    vx: (Math.random()-0.5)*0.03,
    vy: (Math.random()-0.5)*0.03,
    alpha: 0.6 + Math.random()*0.4
  });
}
function drawStars(){
  sctx.clearRect(0,0,stars.width,stars.height);
  sctx.fillStyle = 'rgba(255,255,255,0.9)';
  for(let s of starsArr){
    s.x += s.vx;
    s.y += s.vy;
    if(s.x < 0) s.x = stars.width;
    if(s.x > stars.width) s.x = 0;
    if(s.y < 0) s.y = stars.height;
    if(s.y > stars.height) s.y = 0;
    sctx.beginPath();
    sctx.arc(s.x, s.y, s.r, 0, Math.PI*2);
    sctx.fillStyle = `rgba(255,255,255,${s.alpha})`;
    sctx.fill();
  }
  requestAnimationFrame(drawStars);
}
requestAnimationFrame(drawStars);

/* ---------------------------
   Typewriter "erase & type next"
   --------------------------- */
const phrases = ["web developer", "learner", "tech enthusiast", "programmer", "writer", "video editor"];
let pi = 0, ci = 0, deleting = false;
const speedType = 80, speedErase = 40, delayNext = 900;

const el = document.getElementById('typeText');
const cursor = document.getElementById('cursor');

function tick(){
  const current = phrases[pi];
  if(!deleting){
    el.textContent = current.slice(0, ci+1);
    ci++;
    if(ci === current.length){
      deleting = true;
      setTimeout(tick, delayNext);
      return;
    }
    setTimeout(tick, speedType);
  } else {
    el.textContent = current.slice(0, ci-1);
    ci--;
    if(ci === 0){
      deleting = false;
      pi = (pi+1)%phrases.length;
      setTimeout(tick, 300);
      return;
    }
    setTimeout(tick, speedErase);
  }
}
tick();
setInterval(()=>cursor.style.opacity = cursor.style.opacity == 1 ? 0.05 : 1,500);

/* ---------------------------
   Modal & chat handling
   --------------------------- */
function openModal(id){
  document.getElementById(id).style.display = 'block';
  document.getElementById(id).setAttribute('aria-hidden','false');
}
function closeModal(id){
  document.getElementById(id).style.display = 'none';
  document.getElementById(id).setAttribute('aria-hidden','true');
}
function toggleChat(){
  const p = document.getElementById('chatPanel');
  if(p.style.display === 'block'){ p.style.display = 'none'; p.setAttribute('aria-hidden','true'); }
  else { p.style.display = 'block'; p.setAttribute('aria-hidden','false'); }
}
function sendChat(){
  const v = document.getElementById('chatInput').value;
  if(!v) return alert("Type a question — preview only");
  alert("Preview: message sent (not live). In production you'd forward this to your bot.");
  document.getElementById('chatInput').value = '';
}

/* anonymous submission */
function submitAnon(){
  const v = document.getElementById('anonText').value.trim();
  if(!v) { alert('Please write something to send anonymously.'); return; }
  alert("Preview: anonymous message submitted (preview mode).");
  document.getElementById('anonText').value = '';
}

/* allow keyboard ESC to close modals */
document.addEventListener('keydown',function(e){
  if(e.key === 'Escape'){
    const modals = document.querySelectorAll('.modal');
    modals.forEach(m=>m.style.display='none');
    document.getElementById('chatPanel').style.display='none';
  }
});

</script>
</body>
</html>
'''

# Render the preview as a single embedded page.
components.html(html, height=900, scrolling=True)
