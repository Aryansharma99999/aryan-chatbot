# app.py
import os
import re
import time
import json
import streamlit as st
import streamlit.components.v1 as components
from markdown import markdown

st.set_page_config(page_title="Aryan Sharma", layout="wide", initial_sidebar_state="collapsed")

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
    out = []
    if not os.path.exists(POSTS_DIR):
        return out
    fns = [f for f in sorted(os.listdir(POSTS_DIR)) if f.endswith(".md")]
    for fn in fns:
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
        out.append({
            "title": meta.get("title", fn[:-3].replace('-', ' ').title()),
            "date": meta.get("date", ""),
            "html": markdown(body)
        })
    return out

# ---------------- Aryan Q&A facts ----------------
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

# ---------------- Session state for anon messages ----------------
if "anon_messages" not in st.session_state:
    st.session_state.anon_messages = []

# Sidebar anonymous form (Streamlit-native)
with st.sidebar.form("anon_form", clear_on_submit=True):
    st.write("✍️ Share anonymously (appears on the page)")
    anon_msg = st.text_area("Write anonymously...", height=140)
    if st.form_submit_button("Send anonymously"):
        if anon_msg and anon_msg.strip():
            st.session_state.anon_messages.insert(0, {"msg": anon_msg.strip(), "time": time.asctime()})
            st.success("Saved — check the Writings section on the page.")

# ---------------- Collect data for JS injection ----------------
gallery_list = get_gallery_images()
posts_list = get_blog_posts()
anon_list = st.session_state.anon_messages

INSTAGRAM = "https://instagram.com/aryanxsharma26"
LINKEDIN = "https://www.linkedin.com/in/aryan-sharma99999"

js_gallery = json.dumps(gallery_list)
js_posts = json.dumps(posts_list)
js_anon = json.dumps(anon_list)
js_facts = json.dumps(ARYAN_FACTS)
js_social = json.dumps({"instagram": INSTAGRAM, "linkedin": LINKEDIN})

# ---------------- Full HTML component (scroll-snap, full-coverage canvas) ----------------
html_template = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Aryan Sharma — Portfolio</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
  <style>
    :root{
      --accent1:#b14cff;
      --accent2:#7a3cff;
      --glass: rgba(255,255,255,0.03);
      --text: #eaf6ff;
    }
    html,body{height:100%;margin:0;padding:0;background:#060010;font-family:Inter,system-ui,Arial;color:var(--text);-webkit-font-smoothing:antialiased;}
    /* canvas covers full viewport and everything (behind the site) */
    #anim-bg { position: fixed; inset: 0; width:100vw; height:100vh; z-index: 0; pointer-events:none; display:block; }
    /* site sits above the canvas */
    .site { position: relative; z-index: 5; min-height:100vh; display:flex; flex-direction:column; align-items:center; gap:40px; box-sizing:border-box; padding:0; }
    /* scroll-snap container */
    main.snap-container { width:100%; scroll-snap-type: y mandatory; overflow-y:auto; height:100vh; }
    section.snap { min-height:100vh; display:flex; align-items:center; justify-content:center; scroll-snap-align: start; padding:48px 28px; box-sizing:border-box; }
    /* glass hero */
    .hero-card{ width: min(1150px,92%); border-radius:20px; padding:40px; background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); border:1px solid rgba(255,255,255,0.03); box-shadow: 0 30px 90px rgba(6,6,12,0.6); text-align:center; backdrop-filter: blur(10px) saturate(130%); -webkit-backdrop-filter: blur(10px) saturate(130%); }
    .hero-title{ font-size:46px; font-weight:800; margin:0; background: linear-gradient(90deg,#ffd1ff,#c8b1ff); -webkit-background-clip:text; color:transparent; }
    .hero-sub{ margin-top:8px; font-size:18px; color: rgba(230,240,255,0.95); }
    .typewrap{ margin-top:12px; font-weight:700; font-size:20px; color:#d6c9ff; }
    .cta{ display:flex; gap:12px; justify-content:center; margin-top:18px; }
    .btn{ padding:10px 18px; border-radius:999px; border:none; cursor:pointer; font-weight:800; }
    .btn-primary{ background: linear-gradient(90deg,var(--accent1),var(--accent2)); color:#0b1220; box-shadow:0 10px 30px rgba(16,8,40,0.5); }
    .btn-ghost{ background:transparent; color:#dfefff; border:1px solid rgba(255,255,255,0.04); }

    /* two-column layout (gallery left, content right) */
    .main-grid{ width: min(1150px,96%); display:grid; grid-template-columns: 320px 1fr; gap:28px; align-items:start; box-sizing:border-box; }
    .glass-card{ background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); border-radius:12px; padding:14px; border:1px solid rgba(255,255,255,0.03); box-shadow: 0 10px 36px rgba(6,6,12,0.45); }
    .section-title{ font-weight:800; color:#d6e8ff; display:flex; gap:10px; align-items:center; }
    .gallery-grid{ display:grid; grid-template-columns: repeat(2,1fr); gap:10px; margin-top:10px; }
    .gallery-grid img{ width:100%; height:120px; object-fit:cover; border-radius:8px; border:1px solid rgba(255,255,255,0.025); transition: transform .25s ease, box-shadow .25s ease; }
    .gallery-grid img:hover{ transform: translateY(-6px); box-shadow:0 18px 50px rgba(10,6,30,0.6); }
    .post-card{ margin-bottom:18px; padding:10px; border-radius:10px; }
    .post-card h3{ margin:0; color:#eaf6ff; }
    .post-card .date{ color:rgba(200,220,255,0.65); font-size:13px; margin-bottom:8px; }
    .projects-grid{ display:grid; grid-template-columns: repeat(auto-fit,minmax(200px,1fr)); gap:12px; margin-top:12px; }
    .proj{ padding:12px; border-radius:10px; background: linear-gradient(180deg, rgba(255,255,255,0.015), rgba(255,255,255,0.01)); }

    /* chating */
    .chat-orb{ position: fixed; right:28px; bottom:28px; width:68px; height:68px; border-radius:999px; z-index:9999; display:flex; align-items:center; justify-content:center; cursor:pointer; background: linear-gradient(180deg,#110017,#1a0028); border:2px solid var(--accent1); box-shadow:0 40px 90px rgba(120,40,180,0.18); color:#fff; font-size:28px; }
    .chat-popup{ position: fixed; right:28px; bottom:108px; width:380px; max-width:92vw; border-radius:12px; overflow:hidden; z-index:9999; display:none; box-shadow:0 30px 100px rgba(0,0,0,0.6); border:1px solid rgba(255,255,255,0.03); background: linear-gradient(180deg, rgba(6,8,12,0.98), rgba(8,10,16,0.98)); }
    .chat-head{ padding:12px; font-weight:800; color:#dff6ff; border-bottom:1px solid rgba(255,255,255,0.03); }
    .chat-body{ max-height:260px; overflow:auto; padding:12px; color:#eaf6ff; }
    .chat-input{ display:flex; gap:8px; padding:12px; border-top:1px solid rgba(255,255,255,0.02); }
    .chat-input input{ flex:1; padding:10px; border-radius:10px; border:none; background: rgba(255,255,255,0.04); color:var(--text); }
    .footer{ width: min(1150px,96%); padding:10px 12px; color: rgba(200,220,255,0.85); display:flex; justify-content:space-between; align-items:center; }

    /* make sure everything looks good on mobile */
    @media (max-width:980px){ .main-grid{ grid-template-columns: 1fr; } .gallery-grid img{ height:120px; } .hero-title{ font-size:34px; } }
  </style>
</head>
<body>
  <canvas id="anim-bg"></canvas>

  <div class="site">
    <main class="snap-container" id="snapContainer">

      <!-- SECTION: HERO -->
      <section class="snap" id="heroSection" aria-label="Hero section">
        <div class="hero-card" role="banner">
          <div class="hero-title">ARYAN SHARMA</div>
          <div class="hero-sub">Welcome to my personal website!</div>
          <div class="typewrap">I'm a <span id="typewriter">web developer</span></div>
          <div class="cta">
            <a class="btn btn-primary" href="/resume.pdf#chatbot-section" target="_blank" rel="noreferrer">Download Resume</a>
            <a class="btn btn-ghost" href="{LINKEDIN}" target="_blank" rel="noreferrer">LinkedIn</a>
            <a class="btn btn-ghost" href="{INSTAGRAM}" target="_blank" rel="noreferrer">Instagram</a>
          </div>
        </div>
      </section>

      <!-- SECTION: GALLERY & WRITINGS -->
      <section class="snap" id="gallerySection" aria-label="Gallery and Writings">
        <div style="width:100%;display:flex;justify-content:center;">
          <div class="main-grid" role="main">
            <div class="col-left">
              <div class="glass-card">
                <div class="section-title">📸 Photos (Gallery)</div>
                <div class="gallery-grid" id="galleryGrid"></div>
              </div>

              <div style="height:18px"></div>

              <div class="glass-card">
                <div class="section-title">💼 Projects</div>
                <div class="projects-grid" id="projectsGrid">
                  <div class="proj"><strong>Chatbot Website</strong><div style="opacity:.8">Client-side Q&A & demo.</div></div>
                  <div class="proj"><strong>Portfolio Builder</strong><div style="opacity:.8">Template & theme.</div></div>
                  <div class="proj"><strong>AI Experiments</strong><div style="opacity:.8">Small ML projects.</div></div>
                </div>
              </div>
            </div>

            <div class="col-right">
              <div class="glass-card">
                <div class="section-title">✍️ Writings (Anonymous)</div>
                <div id="anonList" style="margin-top:8px;"></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- SECTION: BLOG -->
      <section class="snap" id="blogSection" aria-label="Blog">
        <div style="width:100%;display:flex;justify-content:center;">
          <div style="width:min(1150px,96%);">
            <div class="glass-card">
              <div class="section-title">📰 Blog Posts</div>
              <div id="postsArea" style="margin-top:12px;"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- SECTION: CONTACT / FOOTER -->
      <section class="snap" id="contactSection" aria-label="Contact and footer">
        <div style="width:100%;display:flex;justify-content:center;">
          <div style="width:min(1150px,96%);">
            <div class="glass-card">
              <h3>Contact</h3>
              <p>Prefer DM on Instagram: <a href="{INSTAGRAM}" target="_blank" style="color:#cde8ff">{INSTAGRAM}</a></p>
              <p>LinkedIn: <a href="{LINKEDIN}" target="_blank" style="color:#cde8ff">{LINKEDIN}</a></p>
            </div>
            <div style="height:18px"></div>
            <div class="footer"> <div>© {YEAR} Aryan Sharma</div> <div>Built with ❤️ · <a href="{LINKEDIN}" target="_blank" style="color:#cde8ff">LinkedIn</a> · <a href="{INSTAGRAM}" target="_blank" style="color:#cde8ff">Instagram</a></div> </div>
          </div>
        </div>
      </section>

    </main>
  </div>

  <div class="chat-orb" id="chatOrb" title="Ask me about Aryan">💬</div>
  <div class="chat-popup" id="chatPop" aria-hidden="true">
    <div class="chat-head">Ask me about Aryan ☕</div>
    <div class="chat-body" id="chatBody"></div>
    <div class="chat-input">
      <input id="chatInput" placeholder="Who is Aryan?"/>
      <button id="chatSend" style="background:var(--accent1);border-radius:8px;padding:8px 12px;border:none;font-weight:800;color:#17041a;">Send</button>
    </div>
  </div>

<script>
  // Inject data from Python
  window.ST_GALLERY = __GALLERY__;
  window.ST_POSTS = __POSTS__;
  window.ST_ANON = __ANON__;
  window.ST_FACTS = __FACTS__;
  window.ST_SOCIAL = __SOCIAL__;

  /* ---------------- Canvas starfield (moving) ---------------- */
  (function(){
    const canvas = document.getElementById('anim-bg');
    const ctx = canvas.getContext('2d');
    function resize(){ canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
    resize(); window.addEventListener('resize', resize);

    const stars = [];
    const STAR_COUNT = Math.max(350, Math.floor((window.innerWidth * window.innerHeight) / 5000));
    for(let i=0;i<STAR_COUNT;i++){
      stars.push({
        x: Math.random()*window.innerWidth,
        y: Math.random()*window.innerHeight,
        r: Math.random()*1.6 + 0.2,
        s: Math.random()*0.8 + 0.1,
        o: Math.random()*0.9 + 0.1
      });
    }
    let t = 0;
    function draw(){
      t += 0.008;
      // base gradient
      const g = ctx.createLinearGradient(0,0,canvas.width,canvas.height);
      g.addColorStop(0, '#1b0126');
      g.addColorStop(0.45, '#23003b');
      g.addColorStop(1, '#090015');
      ctx.fillStyle = g;
      ctx.fillRect(0,0,canvas.width,canvas.height);

      // moving nebula
      const cx = canvas.width * 0.7 + Math.sin(t*0.6)*100;
      const cy = canvas.height * 0.3 + Math.cos(t*0.4)*80;
      const rad = Math.max(canvas.width, canvas.height) * 0.7;
      const rg = ctx.createRadialGradient(cx,cy,0,cx,cy,rad);
      rg.addColorStop(0, 'rgba(110,20,150,0.12)');
      rg.addColorStop(0.3, 'rgba(90,30,160,0.06)');
      rg.addColorStop(0.7, 'rgba(20,10,40,0.02)');
      ctx.globalCompositeOperation = 'lighter';
      ctx.fillStyle = rg;
      ctx.fillRect(0,0,canvas.width,canvas.height);
      ctx.globalCompositeOperation = 'source-over';

      // stars
      for(const s of stars){
        ctx.beginPath();
        const alpha = 0.4 + Math.sin((t*6 + s.x + s.y)/80)*0.3;
        ctx.fillStyle = 'rgba(255,255,255,' + (s.o * alpha) + ')';
        ctx.arc(s.x, s.y, s.r, 0, Math.PI*2);
        ctx.fill();
        s.x += s.s;
        if(s.x > canvas.width + 20) s.x = -20;
      }

      requestAnimationFrame(draw);
    }
    draw();
  })();

  /* ---------------- Typewriter effect ---------------- */
  (function(){
    const roles = ["web developer","writer","learner","tech enthusiast","video editor"];
    let ridx = 0, pos = 0, forward = true;
    const el = document.getElementById('typewriter');
    function tick(){
      const cur = roles[ridx];
      if(forward){
        pos++; el.textContent = cur.slice(0,pos);
        if(pos === cur.length){ forward=false; setTimeout(tick,900); return; }
      } else {
        pos--; el.textContent = cur.slice(0,pos);
        if(pos === 0){ forward=true; ridx=(ridx+1)%roles.length; setTimeout(tick,400); return; }
      }
      setTimeout(tick,70);
    }
    tick();
  })();

  /* ---------------- Inject content (gallery, posts, anon) ---------------- */
  (function(){
    const gallery = window.ST_GALLERY || [];
    const posts = window.ST_POSTS || [];
    const anon = window.ST_ANON || [];

    const gnode = document.getElementById('galleryGrid');
    if(!gallery || gallery.length === 0){
      gnode.innerHTML = "<div style='color:rgba(200,220,255,0.6);padding:8px'>No images found in gallery/</div>";
    } else {
      gnode.innerHTML = '';
      for(const u of gallery){
        const d = document.createElement('div');
        d.innerHTML = `<img src="${u}" alt="gallery">`;
        gnode.appendChild(d);
      }
    }

    const postsNode = document.getElementById('postsArea');
    if(!posts || posts.length === 0){
      postsNode.innerHTML = "<div style='color:rgba(200,220,255,0.6);padding:8px'>No blog posts found in blog_posts/</div>";
    } else {
      postsNode.innerHTML = '';
      for(const p of posts){
        const card = document.createElement('div');
        card.className = 'post-card';
        const dateHtml = p.date ? `<div class='date'>${p.date}</div>` : '';
        card.innerHTML = `<h3>${p.title}</h3>${dateHtml}<div style='margin-top:8px;color:rgba(220,235,255,0.95)'>${p.html}</div>`;
        postsNode.appendChild(card);
      }
    }

    const anonNode = document.getElementById('anonList');
    if(!anon || anon.length === 0){
      anonNode.innerHTML = "<div style='color:rgba(200,220,255,0.6);padding:8px'>No anonymous writings yet. Use the sidebar form to post.</div>";
    } else {
      anonNode.innerHTML = '';
      for(const m of anon){
        const el = document.createElement('div');
        el.className = 'glass-card';
        el.style.marginBottom = '8px';
        el.innerHTML = `<div style='font-size:14px;color:rgba(220,235,255,0.95)'>${m.msg}</div><div style='font-size:11px;color:rgba(180,200,220,0.6);margin-top:6px'>${m.time}</div>`;
        anonNode.appendChild(el);
      }
    }
  })();

  /* ---------------- Chat logic ---------------- */
  (function(){
    const orb = document.getElementById('chatOrb');
    const pop = document.getElementById('chatPop');
    const body = document.getElementById('chatBody');
    const input = document.getElementById('chatInput');
    const send = document.getElementById('chatSend');
    const facts = window.ST_FACTS || {};

    function addMsg(text, who){
      const el = document.createElement('div');
      el.textContent = text;
      el.style.padding = '8px 10px';
      el.style.marginBottom = '8px';
      el.style.borderRadius = '10px';
      if(who === 'user'){
        el.style.background = 'rgba(255,255,255,0.08)';
        el.style.textAlign = 'right';
      } else {
        el.style.background = 'rgba(110,140,255,0.06)';
      }
      body.appendChild(el);
      body.scrollTop = body.scrollHeight;
    }

    orb.addEventListener('click', function(){
      const showing = pop.style.display === 'block';
      pop.style.display = showing ? 'none' : 'block';
      if(!showing && body.children.length === 0) addMsg("Hi! I'm Aryan's assistant — ask me anything about Aryan ☕");
      input.focus();
    });

    send.addEventListener('click', function(){
      const q = (input.value || '').trim();
      if(!q) return;
      addMsg(q,'user');
      input.value = '';
      setTimeout(function(){
        const lq = q.toLowerCase();
        let out = null;
        for(const k in facts){
          if(lq.includes(k)) { out = facts[k]; break; }
        }
        if(!out){
          if(lq.includes('name')) out = "Aryan Sharma — that guy with stories & coffee.";
          else if(lq.includes('coffee')) out = facts["what’s aryan’s comfort drink"] || "Coffee ☕";
          else out = "Ask me anything about Aryan ☕🙂!";
        }
        addMsg(out,'bot');
      }, 240 + Math.random()*420);
    });

    input.addEventListener('keydown', function(e){ if(e.key === 'Enter'){ e.preventDefault(); send.click(); }});
  })();
</script>
</body>
</html>
"""

# ------------- Replace placeholders -------------
html = html_template.replace("__GALLERY__", js_gallery).replace("__POSTS__", js_posts).replace("__ANON__", js_anon).replace("__FACTS__", js_facts).replace("__SOCIAL__", js_social)
html = html.replace("{LINKEDIN}", LINKEDIN).replace("{INSTAGRAM}", INSTAGRAM).replace("{YEAR}", str(time.localtime().tm_year))

# Render the HTML in Streamlit component
# Use tall height and allow scrolling inside the HTML because it's a full scroll-snap page
components.html(html, height=980, scrolling=True)

# ---------------- Force full transparency on Streamlit wrappers (stronger CSS) ----------------
st.markdown("""
<style>
/* Make Streamlit containers transparent so canvas shows through entire page */
html, body, .stApp, .block-container, .main, .css-1lcbmhc, .css-18e3th9, .css-1v3fvcr {
    background: transparent !important;
}

/* Sometimes Streamlit inserts additional wrappers with dynamic class names;
   the following rules aggressively force transparency for common cases. */
.stApp > .main > div { background: transparent !important; }
footer, .reportview-container, .main .block-container { background: transparent !important; }

/* Remove extra white spacing above the component so the canvas is fully visible */
.block-container { padding-top: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ---------------- Small Streamlit notes below the component ----------------
st.markdown("---")
st.markdown("### Editor: Gallery & Blog")
st.markdown("• Add images to the `gallery/` folder (jpg, png, webp, gif). They will appear in the gallery grid above.")
st.markdown("• Put markdown files (`.md`) in `blog_posts/` — they will be parsed and shown in Blog Posts.")
st.markdown("---")
st.write("LinkedIn:", LINKEDIN)
st.write("Instagram:", INSTAGRAM)
