# app.py
import os
import re
import json
import streamlit as st
from markdown import markdown
import streamlit.components.v1 as components

st.set_page_config(page_title="Aryan Sharma", layout="wide", initial_sidebar_state="collapsed")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
GALLERY_DIR = os.path.join(BASE_DIR, "gallery")
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")

def get_gallery_images():
    if not os.path.exists(GALLERY_DIR):
        return []
    files = [f for f in os.listdir(GALLERY_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif"))]
    files.sort()
    # Use relative paths that the browser can load via Streamlit static serving
    return [os.path.join("gallery", f) for f in files]

def get_posts():
    posts = []
    if not os.path.exists(POSTS_DIR):
        return posts
    for fname in sorted(os.listdir(POSTS_DIR)):
        if not fname.endswith(".md"):
            continue
        slug = fname[:-3]
        path = os.path.join(POSTS_DIR, fname)
        with open(path, "r", encoding="utf-8") as fh:
            content = fh.read()
        # parse front matter simple '---' style
        meta = {}
        body = content
        m = re.match(r'---\n(.*?)\n---', content, re.DOTALL)
        if m:
            meta_block = m.group(1)
            for line in meta_block.splitlines():
                if ':' in line:
                    k, v = line.split(':', 1)
                    meta[k.strip()] = v.strip()
            body = content[m.end():].strip()
        html = markdown(body)
        posts.append({
            "slug": slug,
            "title": meta.get("title", slug.replace('-', ' ').capitalize()),
            "date": meta.get("date", ""),
            "author": meta.get("author", ""),
            "summary": meta.get("summary", ""),
            "html": html
        })
    return posts

# 20 facts you gave (in JS we'll inject them as ST_ARYAN_FACTS)
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

# Prepare data to inject into HTML
gallery_urls = get_gallery_images()
posts = get_posts()
js_gallery = json.dumps(gallery_urls)
js_posts = json.dumps(posts)
js_facts = json.dumps(ARYAN_FACTS)

# Full-page HTML (the entire site rendered inside the component)
html = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
  <title>Aryan — Portfolio</title>
  <style>
    :root {{
      --text: #eaf6ff;
      --glass: rgba(255,255,255,0.03);
      --accent: #8db3ff;
    }}
    html,body{{height:100%;margin:0;padding:0;overflow:auto;font-family:Inter,system-ui; background: #070814; color:var(--text);}}
    /* full canvas background covers whole viewport */
    #galaxy-wrap{{position:fixed;inset:0;z-index:0;pointer-events:none;}}
    canvas{{width:100%;height:100%;display:block;}}

    /* top-level app container */
    .app{{position:relative;z-index:5;min-height:100vh;display:flex;flex-direction:column;align-items:center;gap:28px;padding:28px 36px;box-sizing:border-box;}}

    /* hero */
    .hero{{width:100%;max-width:1200px;border-radius:16px;padding:44px;background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));box-shadow:0 40px 110px rgba(2,6,20,0.6);border:1px solid rgba(255,255,255,0.04);text-align:center;}}
    .hero h1{{margin:0;font-size:48px;font-weight:800;color:#e9f6ff}}
    .hero p{{margin:10px 0 0 0;color:rgba(230,240,255,0.9)}}
    .roles{{margin-top:12px;font-weight:700;color:#d2e8ff}}

    .cta{{margin-top:20px;display:flex;gap:12px;justify-content:center;align-items:center}}
    .btn{{padding:10px 18px;border-radius:999px;border:none;font-weight:700;cursor:pointer}}
    .btn-primary{{background:var(--accent);color:#071827;box-shadow:0 8px 26px rgba(20,40,80,0.18)}}
    .btn-ghost{{background:transparent;color:#dfefff;border:1px solid rgba(255,255,255,0.06)}}

    /* layout below hero */
    .main-grid{{width:100%;max-width:1200px;display:grid;grid-template-columns:320px 1fr;gap:32px;align-items:start;box-sizing:border-box;padding-bottom:64px}}
    .left-col{{display:flex;flex-direction:column;gap:14px}}
    .glass-card{{background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));border:1px solid rgba(255,255,255,0.04);box-shadow:0 14px 40px rgba(2,6,20,0.35);padding:14px;border-radius:12px;color:var(--text)}}
    .section-title{font-weight:700;color:#d4ecff;margin-bottom:12px;display:flex;gap:8px;align-items:center}

    /* gallery grid inside left column */
    .gallery-grid{display:grid;grid-template-columns: repeat(2, 1fr);gap:10px;}
    .gallery-grid img{width:100%;height:100%;object-fit:cover;border-radius:10px;display:block;box-shadow:0 10px 28px rgba(0,0,0,0.35)}

    /* right column - blog & writings */
    .post-card{margin-bottom:18px}
    .post-card h2{margin:0 0 8px 0;color:#eaf6ff}
    .post-card .date{color:rgba(200,220,255,0.68);font-size:13px;margin-bottom:12px}

    /* projects area */
    .projects{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:18px;margin-top:8px}
    .proj{padding:12px;border-radius:12px;background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));box-shadow:0 12px 30px rgba(0,0,0,0.35)}

    /* floating chat orb */
    .chat-orb{position:fixed;right:26px;bottom:28px;width:64px;height:64px;border-radius:999px;z-index:60;display:flex;align-items:center;justify-content:center;background:linear-gradient(180deg, rgba(16,18,22,0.96), rgba(10,12,16,0.96));box-shadow:0 32px 90px rgba(0,0,0,0.6);cursor:pointer;border:1px solid rgba(255,255,255,0.03)}
    .chat-orb:hover{transform:translateY(-6px)}

    .island{position:fixed;right:26px;bottom:108px;width:420px;max-width:92vw;z-index:70;display:none}
    .island.show{display:block}
    .island .inner{border-radius:12px;overflow:hidden;background:linear-gradient(180deg, rgba(8,10,14,0.96), rgba(12,14,18,0.96));box-shadow:0 30px 100px rgba(0,0,0,0.7);border:1px solid rgba(255,255,255,0.03)}
    .island .header{padding:12px 14px;font-weight:700;color:#cfeeff;background:rgba(255,255,255,0.02)}
    .island .body{padding:12px;max-height:260px;overflow:auto;color:#eaf6ff}
    .island .footer{padding:12px;display:flex;gap:8px}
    .chat-input{flex:1;padding:10px;border-radius:10px;border:none;background:#0d1114;color:#eaf6ff}

    /* footer */
    .footer{width:100%;max-width:1200px;color:rgba(210,230,255,0.85);padding:18px 0}

    /* responsive */
    @media (max-width:980px){ .main-grid{grid-template-columns:1fr} .gallery-grid{grid-template-columns:repeat(3,1fr)} }
    @media (max-width:520px){ .gallery-grid{grid-template-columns:repeat(2,1fr)} .hero h1{font-size:28px} .island{left:12px;right:12px;bottom:84px} }
  </style>
</head>
<body>
  <div id="galaxy-wrap"><canvas id="galaxy"></canvas></div>

  <div class="app" role="main" aria-label="Aryan portfolio app">
    <div class="hero" role="banner">
      <h1>Aryan Sharma</h1>
      <p>Welcome to my personal website!</p>
      <div class="roles" id="role">tech enthusiast</div>
      <div class="cta">
        <a class="btn btn-primary" href="/resume.pdf#chatbot-section" target="_blank">Download Resume</a>
        <button class="btn btn-ghost" onclick="document.getElementById('projects').scrollIntoView({behavior:'smooth'})">Get In Touch</button>
      </div>
    </div>

    <div class="main-grid">
      <div class="left-col">
        <div class="glass-card">
          <div class="section-title">📸 Photos (Gallery)</div>
          <div class="gallery-grid" id="galleryGrid">
            <!-- JS injects gallery images -->
          </div>
        </div>
      </div>

      <div class="right-col">
        <div class="glass-card">
          <div class="section-title">✍️ Writings (Anonymous)</div>
          <div id="writingsArea">
            <p style="margin:0 0 8px 0;color:rgba(210,230,255,0.9)">Use the Streamlit form below to post anonymously — posts appear in this UI automatically.</p>
            <div id="anonList"></div>
          </div>
        </div>

        <div class="glass-card">
          <div class="section-title">📰 Blog Posts</div>
          <div id="postsArea">
            <!-- posts injected by JS -->
          </div>
        </div>

        <div id="projects" style="margin-top:12px"></div>
      </div>
    </div>

    <div class="projects" style="max-width:1200px" id="projectsList">
      <div class="proj"> <strong>Chatbot App</strong><div style="opacity:.85">Client-side Q&A with Aryan's answers.</div></div>
      <div class="proj"> <strong>Portfolio Website</strong><div style="opacity:.85">Glass UI with full-page galaxy background.</div></div>
      <div class="proj"> <strong>AI Experiments</strong><div style="opacity:.85">Small experiments & projects.</div></div>
    </div>

    <div class="footer">Contact: DM on Instagram <a href="https://instagram.com/aryanxsharma26" target="_blank" style="color:#cde8ff">aryanxsharma26</a></div>
  </div>

  <div class="chat-orb" id="chatOrb" aria-label="Open chat">💬</div>
  <div class="island" id="island" aria-hidden="true">
    <div class="inner">
      <div class="header">Ask me about Aryan ☕</div>
      <div class="body" id="chatBody" aria-live="polite"></div>
      <div class="footer">
        <input id="chatInput" class="chat-input" placeholder="Who is Aryan?" />
        <button id="chatSend" class="btn btn-primary">Send</button>
      </div>
    </div>
  </div>

  <script>
    // Injected data from Python (will be replaced by Streamlit script below)
    window.ST_GALLERY_URLS = {js_gallery};
    window.ST_POSTS = {js_posts};
    window.ST_ARYAN_FACTS = {js_facts};

    /* --------------- Canvas galaxy (multi-layered) --------------- */
    (function(){
      const canvas = document.getElementById('galaxy');
      const ctx = canvas.getContext('2d');
      function resize(){ canvas.width=window.innerWidth; canvas.height=window.innerHeight; }
      resize(); window.addEventListener('resize', resize);

      const layers = [
        {count:120, speed:0.18, size:[0.3,0.9], alpha:0.6},
        {count:60, speed:0.5, size:[1.2,2.2], alpha:0.9},
        {count:30, speed:1.1, size:[2.8,4.0], alpha:1.0}
      ];
      let groups = [];
      function make(){
        groups=[];
        for(const L of layers){
          const arr=[];
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
      window.addEventListener('mousemove', e=>{ mx=e.clientX; my=e.clientY; });

      function drawNebula(){
        const g = ctx.createLinearGradient(0,0,canvas.width,canvas.height);
        g.addColorStop(0,'rgba(6,10,18,0.96)');
        g.addColorStop(1,'rgba(12,14,28,0.96)');
        ctx.fillStyle=g; ctx.fillRect(0,0,canvas.width,canvas.height);
        const cx = canvas.width*0.68 + Math.sin(t*0.2)*120;
        const cy = canvas.height*0.28 + Math.cos(t*0.15)*80;
        const rg = ctx.createRadialGradient(cx,cy,0,cx,cy, Math.max(canvas.width,canvas.height)*0.9);
        rg.addColorStop(0, 'rgba(60,40,120,0.13)');
        rg.addColorStop(0.3,'rgba(80,60,160,0.07)');
        rg.addColorStop(0.6,'rgba(6,10,20,0.02)');
        ctx.globalCompositeOperation='lighter'; ctx.fillStyle=rg; ctx.fillRect(0,0,canvas.width,canvas.height);
        ctx.globalCompositeOperation='source-over';
      }
      function drawStars(){
        for(let gi=0;gi<groups.length;gi++){
          const group=groups[gi];
          for(const s of group){
            const px=(mx - canvas.width/2)*(0.0005 + gi*0.001);
            const py=(my - canvas.height/2)*(0.0005 + gi*0.001);
            s.x += s.vx; s.y += s.vy;
            if(s.x < -10) s.x = canvas.width+10;
            if(s.x > canvas.width+10) s.x = -10;
            if(s.y < -10) s.y = canvas.height+10;
            if(s.y > canvas.height+10) s.y = -10;
            ctx.beginPath();
            ctx.fillStyle = 'rgba(255,255,255,' + (s.a * (0.6 + Math.sin((t + s.x + s.y)/90)*0.35)) + ')';
            ctx.arc(s.x + px*40, s.y + py*40, s.r, 0, Math.PI*2); ctx.fill();
          }
        }
      }
      function loop(){ t+=0.016; drawNebula(); drawStars(); requestAnimationFrame(loop); }
      loop();
    })();

    /* --------------- hero typewriter --------------- */
    (function(){
      setTimeout(()=>document.querySelector('.hero').classList.add('show'),120);
      const roles = ["web developer","tech enthusiast","programmer","writer","editor"];
      let idx=0,pos=0,fw=true,el=document.getElementById('role');
      (function tick(){
        const cur=roles[idx];
        if(fw){ pos++; el.textContent = cur.slice(0,pos); if(pos===cur.length){ fw=false; setTimeout(tick,800); return; } }
        else{ pos--; el.textContent = cur.slice(0,pos); if(pos===0){ fw=true; idx=(idx+1)%roles.length; setTimeout(tick,400); return; } }
        setTimeout(tick,70);
      })();
    })();

    /* --------------- inject posts & gallery into DOM --------------- */
    (function(){
      // gallery
      const gallery = window.ST_GALLERY_URLS || [];
      const grid = document.getElementById('galleryGrid');
      grid.innerHTML = '';
      if(gallery.length === 0){
        grid.innerHTML = "<div style='grid-column:1/-1;color:rgba(200,220,255,0.6);padding:8px'>No images found. Put files in gallery/.</div>";
      } else {
        for(const url of gallery){
          const d = document.createElement('div');
          d.innerHTML = "<img src='"+url+"' alt='gallery image'/>";
          grid.appendChild(d);
        }
      }

      // posts
      const posts = window.ST_POSTS || [];
      const postsArea = document.getElementById('postsArea');
      postsArea.innerHTML = '';
      if(posts.length === 0){
        postsArea.innerHTML = "<div style='color:rgba(200,220,255,0.65)'>No blog posts found. Add .md files into blog_posts/.</div>";
      } else {
        for(const p of posts){
          const wrap = document.createElement('div');
          wrap.className = 'post-card';
          wrap.innerHTML = "<h2>"+(p.title||'Untitled')+"</h2>" +
                           (p.date?("<div class='date'>"+p.date+"</div>"):"") +
                           "<div style='color:rgba(220,235,255,0.9)'>"+(p.html||'')+"</div>";
          postsArea.appendChild(wrap);
        }
      }
    })();

    /* --------------- chat logic (uses ST_ARYAN_FACTS) --------------- */
    (function(){
      const orb = document.getElementById('chatOrb');
      const island = document.getElementById('island');
      const chatBody = document.getElementById('chatBody');
      const input = document.getElementById('chatInput');
      const send = document.getElementById('chatSend');
      function addMsg(t, who){
        const el=document.createElement('div');
        el.className='msg ' + (who==='user'?'user':'bot');
        el.style.margin='8px 0'; el.style.padding='8px 10px'; el.style.borderRadius='10px';
        if(who==='user'){ el.style.background='rgba(255,255,255,0.08)'; el.style.color='#081827'; el.style.marginLeft='auto'; }
        else { el.style.background='rgba(110,140,255,0.06)'; el.style.color='#eaf6ff'; }
        el.textContent=t; chatBody.appendChild(el); chatBody.scrollTop = chatBody.scrollHeight;
      }
      orb.addEventListener('click', ()=>{
        const show = island.classList.toggle('show');
        island.setAttribute('aria-hidden', show ? 'false' : 'true');
        input.focus();
        if(chatBody.children.length === 0) addMsg("Hi — I'm Aryan's assistant. Ask me about Aryan ☕", 'bot');
      });
      send.addEventListener('click', ()=>{
        const q=(input.value||'').trim(); if(!q) return; addMsg(q,'user'); input.value='';
        setTimeout(()=> {
          const lq = q.toLowerCase();
          let out = null;
          const facts = window.ST_ARYAN_FACTS || {};
          for(const k in facts){ if(lq.includes(k)) { out = facts[k]; break; } }
          if(!out){
            if(lq.includes('name')) out = "Aryan Sharma — that guy with stories & coffee.";
            else if(lq.includes('coffee')) out = facts["what’s aryan’s comfort drink"] || "Coffee ☕";
            else if(lq.includes('study')) out = facts["what is aryan currently studying"] || "Pursuing a Bachelor's degree.";
            else out = "Ask me anything about Aryan ☕🙂!";
          }
          addMsg(out,'bot');
        }, 260 + Math.random()*420);
      });
      input.addEventListener('keydown', (e)=>{ if(e.key === 'Enter'){ e.preventDefault(); send.click(); }});
    })();

  </script>
</body>
</html>
"""

# Render the component. It's the whole page, so request a tall height; then force iframe height below.
components.html(html, height=900, scrolling=True)

# Force the Streamlit iframe to be full height (aggressive)
st.markdown("""
<style>
/* Force the component iframe to occupy the viewport so HTML "page" looks full-page */
iframe[srcdoc] { height: 100vh !important; min-height:100vh !important; max-height:100vh !important; }
html, body, .stApp, .block-container { background: transparent !important; padding:0 !important; margin:0 !important; }
</style>
""", unsafe_allow_html=True)

# Minimal Streamlit fallback: small info so user can still use streamlit controls if needed
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("### (If you prefer to edit content) — Gallery & blog are read from `gallery/` and `blog_posts/` in the repo root. Add images and `.md` files and refresh the page.", unsafe_allow_html=True)
