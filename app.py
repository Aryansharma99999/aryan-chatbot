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
    files = [f for f in os.listdir(GALLERY_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
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
                k,v = line.split(':',1)
                meta[k.strip()] = v.strip()
        body = content[meta_match.end():].strip()
    html = markdown(body)
    return {
        "slug": slug,
        "title": meta.get("title", slug.replace('-', ' ').capitalize()),
        "date": meta.get("date", ""),
        "author": meta.get("author", ""),
        "summary": meta.get("summary", ""),
        "html": html,
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

# ---------------- Aryan facts (chatbot brain) ----------------
aryan_facts = {
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
    "what’s something aryan can’t live without": "Coffee. None 😅. But coffee keeps him warm, so no complaints.",
    "what makes aryan unique": "His ability to make people laugh even when he’s not trying.",
    "what’s aryan’s favorite weather": "Cold breeze + warm coffee = perfection.",
    "how does aryan relax": "Storytelling, music, and wandering thoughts.",
    "what is aryan passionate about": "Tech, creativity, and turning ideas into reality.",
    "what is aryan learning right now": "New tech skills… one coffee at a time.",
    "what type of person is aryan": "Calm, humorous, and secretly a deep thinker.",
    "what’s aryan’s favourite thing to do": "Observe life and turn it into funny, relatable stories.",
    "what does aryan dream about": "A life full of learning, creativity, and a never-ending coffee supply."
}

# ---------------- Premium Galaxy hero + dynamic chatbot (component) ----------------
hero_html = r"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
  <style>
    :root{
      --glass-bg: rgba(255,255,255,0.04);
      --glass-strong: rgba(255,255,255,0.06);
      --accent: rgba(140,180,255,0.95);
      --text: rgba(235,240,255,0.98);
    }
    html,body{height:100%;margin:0;padding:0;font-family:Inter,system-ui, -apple-system; background:transparent; color:var(--text); overflow:hidden;}
    /* Full-page canvas background */
    #galaxy-wrap { position:fixed; inset:0; z-index:0; }
    canvas { width:100%; height:100%; display:block; }

    /* page layout */
    .page { position:relative; z-index:5; display:flex; align-items:center; justify-content:center; min-height:100vh; padding:36px; box-sizing:border-box; }

    /* glass hero */
    .hero-card {
      width:88%; max-width:1100px; border-radius:18px;
      padding:44px 46px; box-sizing:border-box; backdrop-filter: blur(18px) saturate(120%);
      -webkit-backdrop-filter: blur(18px) saturate(120%);
      background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));
      border: 1px solid rgba(255,255,255,0.04);
      box-shadow: 0 40px 100px rgba(2,6,20,0.6);
      text-align:center;
      transform: translateY(20px);
      opacity: 0;
      transition: all 0.9s cubic-bezier(.2,.9,.3,1);
    }
    .hero-card.show { transform: translateY(0); opacity:1; }

    .hero-title { font-size:48px; font-weight:800; margin:0; letter-spacing:-0.02em; color: #f2f7ff; }
    .hero-sub { margin-top:10px; color: rgba(230,240,255,0.9); font-size:18px; }
    .typewrap { margin-top:12px; color: #ddeeff; font-weight:600; }
    .roles { color:#cfe8ff; font-weight:700; margin-left:8px; }

    .cta { margin-top:26px; display:flex; gap:12px; justify-content:center; align-items:center; }
    .btn {
      padding:10px 18px; border-radius:999px; font-weight:700; cursor:pointer; border:none;
      transition: transform .18s ease, box-shadow .18s ease;
    }
    .btn-primary {
      background: linear-gradient(90deg, rgba(140,180,255,0.95), rgba(120,160,255,0.9));
      color:#07182a; box-shadow: 0 8px 30px rgba(80,100,160,0.14);
    }
    .btn-ghost {
      background: transparent; color: #cfe8ff; border:1px solid rgba(255,255,255,0.06); padding:10px 18px;
    }
    .btn:hover { transform: translateY(-4px); }

    /* floating dynamic island/chat bubble */
    .chat-orb {
      position:fixed; right:28px; bottom:28px; z-index:20;
      width:64px; height:64px; border-radius:999px;
      background: linear-gradient(180deg, rgba(10,12,15,0.95), rgba(22,24,28,0.95));
      box-shadow: 0 18px 60px rgba(2,6,18,0.6);
      display:flex; align-items:center; justify-content:center; cursor:pointer;
      transition: transform .18s ease, box-shadow .18s ease;
      border: 1px solid rgba(255,255,255,0.03);
    }
    .chat-orb:hover { transform: translateY(-6px); box-shadow: 0 28px 84px rgba(2,6,18,0.75); }

    /* dynamic island modal */
    .island {
      position: fixed; right:26px; bottom:106px; z-index:30; display:none; width:420px; max-width:92vw;
      border-radius:14px; overflow:hidden; background: linear-gradient(180deg,#071018,#0b131a);
      box-shadow: 0 30px 100px rgba(1,4,10,0.7);
      border: 1px solid rgba(255,255,255,0.04);
    }
    .island.show { display:block; animation: islandIn .28s cubic-bezier(.2,.9,.3,1); }
    @keyframes islandIn { from { transform: translateY(10px) scale(.98); opacity:0 } to { transform: translateY(0) scale(1); opacity:1 } }

    .island .header { padding:12px 14px; display:flex; justify-content:space-between; align-items:center; color:#bfe8ff; font-weight:800; }
    .island .body { padding:10px 12px; max-height:340px; overflow:auto; }
    .island .footer { padding:12px; display:flex; gap:8px; }

    .msg { margin:8px 0; padding:10px 12px; border-radius:12px; max-width:82%; color:#eef7ff; }
    .msg.user { background: linear-gradient(90deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03)); color:#f3f9ff; margin-left:auto; text-align:right; }
    .msg.bot { background: linear-gradient(90deg, rgba(90,120,160,0.06), rgba(90,120,160,0.02)); color:#eef7ff; margin-right:auto; }

    .chat-input { flex:1; padding:10px 12px; border-radius:10px; border: none; background:#0f1316; color:#dfefff; outline:none; }

    /* small screens */
    @media (max-width:760px){
      .hero-card { padding:28px 22px; width:92%; }
      .hero-title { font-size:32px; }
      .island { left:12px; right:12px; bottom:90px; width:calc(100% - 24px); }
    }

    /* album-style subtle caption */
    .small-note { position:fixed; left:18px; bottom:16px; z-index:6; color:rgba(220,230,240,0.55); font-size:13px; }
  </style>
</head>
<body>
  <div id="galaxy-wrap">
    <canvas id="galaxy"></canvas>
  </div>

  <div class="page" role="main">
    <div class="hero-card" id="heroCard" role="banner" aria-label="Hero">
      <h1 class="hero-title">Aryan Sharma</h1>
      <div class="hero-sub">Welcome to my personal website!</div>
      <div class="typewrap">I'm a <span class="roles" id="role">tech enthusiast</span></div>

      <div class="cta">
        <a class="btn btn-primary" href="/resume.pdf#chatbot-section" role="button">Download Resume</a>
        <button class="btn btn-ghost" onclick="document.getElementById('projects_anchor').scrollIntoView({behavior:'smooth'})">Get In Touch</button>
      </div>
    </div>
  </div>

  <div class="chat-orb" id="chatOrb" aria-label="Open chat">
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden><path d="M21 15a2 2 0 0 1-2 2H8l-5 4V5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v10z" fill="white" opacity="0.95"/></svg>
  </div>

  <div class="island" id="island" role="dialog" aria-modal="true" aria-label="Chat with Aryan">
    <div class="header">Ask me about Aryan ☕ <div style="font-size:14px;opacity:.7">| Chat</div></div>
    <div class="body" id="chatBody" aria-live="polite"></div>
    <div class="footer">
      <input id="chatText" class="chat-input" placeholder="Type: Who is Aryan?" />
      <button id="chatSend" class="btn btn-primary" style="padding:8px 12px;">Send</button>
    </div>
  </div>

  <div class="small-note">Galaxy theme — optimized for desktop</div>

<script>
/* ========== Canvas Galaxy (multi-layered, parallax) ========== */
(() => {
  const canvas = document.getElementById('galaxy');
  const dpr = Math.max(1, window.devicePixelRatio || 1);
  let w = canvas.clientWidth;
  let h = canvas.clientHeight;
  canvas.width = w * dpr;
  canvas.height = h * dpr;
  const ctx = canvas.getContext('2d');
  ctx.scale(dpr, dpr);

  // star layers config
  const layers = [
    {count: 120, speed: 0.02, size: [0.4,1.2], alpha: 0.7},
    {count: 60, speed: 0.05, size: [1.2,2.2], alpha: 0.9},
    {count: 30, speed: 0.12, size: [2.6,3.8], alpha: 0.95}
  ];
  let stars = [];
  let t = 0;
  let mx = 0, my = 0;

  function rand(min,max){ return Math.random()*(max-min)+min; }

  function makeStars(){
    stars = layers.map(layer => {
      const arr = [];
      for(let i=0;i<layer.count;i++){
        arr.push({
          x: Math.random()*w,
          y: Math.random()*h,
          z: rand(layer.size[0], layer.size[1]),
          a: layer.alpha * (0.6 + Math.random()*0.4),
          vx: (Math.random()*2-1) * layer.speed,
          vy: (Math.random()*2-1) * layer.speed
        });
      }
      return arr;
    });
  }

  function drawNebula(){
    // soft drifting nebula using radial gradients
    const g = ctx.createLinearGradient(0,0,w,h);
    g.addColorStop(0, 'rgba(20,18,36,0.36)');
    g.addColorStop(0.35, 'rgba(60,30,90,0.18)');
    g.addColorStop(0.7, 'rgba(24,40,80,0.15)');
    ctx.fillStyle = g;
    ctx.fillRect(0,0,w,h);

    // layered lighter glows
    const cx = w * 0.68 + Math.sin(t*0.2)*120;
    const cy = h * 0.28 + Math.cos(t*0.15)*80;
    const rg = ctx.createRadialGradient(cx,cy,0,cx,cy, Math.max(w,h)*0.9);
    rg.addColorStop(0, 'rgba(95,120,220,0.14)');
    rg.addColorStop(0.25, 'rgba(120,80,220,0.08)');
    rg.addColorStop(0.55, 'rgba(20,28,48,0.02)');
    ctx.globalCompositeOperation = 'lighter';
    ctx.fillStyle = rg;
    ctx.fillRect(0,0,w,h);
    ctx.globalCompositeOperation = 'source-over';
  }

  function drawStars(){
    for(let li=0; li<stars.length; li++){
      const layer = stars[li];
      for(let s of layer){
        // parallax offset based on mouse
        const px = (mx - w/2) * (0.0005 + li*0.0009);
        const py = (my - h/2) * (0.0005 + li*0.0009);
        s.x += s.vx * (1+li*0.4);
        s.y += s.vy * (1+li*0.4);
        // wrap-around
        if (s.x < -10) s.x = w+10;
        if (s.x > w+10) s.x = -10;
        if (s.y < -10) s.y = h+10;
        if (s.y > h+10) s.y = -10;

        const size = s.z;
        ctx.beginPath();
        ctx.fillStyle = 'rgba(255,255,255,'+ (s.a* (0.6 + Math.sin((t+s.x+s.y)/70)*0.4)) +')';
        ctx.arc(s.x + px*40, s.y + py*40, size, 0, Math.PI*2);
        ctx.fill();
      }
    }
  }

  function resize(){
    w = canvas.clientWidth; h = canvas.clientHeight;
    canvas.width = w * dpr; canvas.height = h * dpr;
    ctx.scale(dpr, dpr);
    makeStars();
  }
  window.addEventListener('resize', resize);
  window.addEventListener('mousemove', (e) => { mx = e.clientX; my = e.clientY; });

  makeStars();

  function loop(){
    t += 0.016;
    ctx.clearRect(0,0,w,h);
    drawNebula();
    drawStars();
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);
})();

/* ========== Hero show animation + typewriter ========== */
window.addEventListener('DOMContentLoaded', function(){
  const hero = document.getElementById('heroCard');
  setTimeout(()=>hero.classList.add('show'), 120);
  // typewriter
  const roles = ["web developer","learner","tech enthusiast","programmer","writer","video editor"];
  let idx=0, pos=0, forw=true;
  const roleEl = document.getElementById('role');
  function tTick(){
    const cur = roles[idx];
    if (forw){ pos++; roleEl.textContent = cur.slice(0,pos); if (pos === cur.length){ forw=false; setTimeout(tTick,900); return; } }
    else { pos--; roleEl.textContent = cur.slice(0,pos); if (pos===0){ forw=true; idx=(idx+1)%roles.length; setTimeout(tTick,400); return; } }
    setTimeout(tTick,70);
  }
  tTick();
});

/* ========== Chatbot dynamic island behavior + client-side Q&A ========== */
(() => {
  const facts = JSON.parse(`""" + (lambda: ( (lambda d: d) (str(aryan_facts).replace("'", "\\'").replace("\\n","\\n")) ))() + """`); 
  // Note: the above is replaced at runtime by Python rendering - but Streamlit components.html escapes raw string.
})();

</script>

<script>
/* Because we cannot easily inject a Python dict via raw HTML here (components.html),
   we'll instead create a plain JS copy of the aryan_facts below for the chatbot. */
const ARYAN_FACTS = {
"""  # we'll append JS key-values from Python below
# Close the hero_html string in Python and we will reconstruct with aryan_facts inserted dynamically.
"""

# Build the JS facts mapping text (safe escaping)
facts_js_lines = []
for k, v in aryan_facts.items():
    # escape quotes and backslashes
    kk = k.replace("\\", "\\\\").replace("\"", "\\\"")
    vv = v.replace("\\", "\\\\").replace("\"", "\\\"")
    facts_js_lines.append(f'  "{kk}": "{vv}"')
facts_js = ",\n".join(facts_js_lines)

# Now produce the remainder of the HTML/JS (chat logic and footer)
hero_html_end = r"""
};

(function(){
  const orb = document.getElementById('chatOrb');
  const island = document.getElementById('island');
  const chatBody = document.getElementById('chatBody');
  const chatText = document.getElementById('chatText');
  const chatSend = document.getElementById('chatSend');

  function addMessage(text, who='bot'){
    const el = document.createElement('div');
    el.className = 'msg ' + (who === 'user' ? 'user' : 'bot');
    el.textContent = text;
    chatBody.appendChild(el);
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  // initial bot greeting
  function greet(){
    if (chatBody.children.length === 0){
      addMessage("Hi! I'm Aryan's assistant — ask me anything about Aryan ☕", 'bot');
    }
  }

  orb.addEventListener('click', (e)=>{
    island.classList.toggle('show');
    if (island.classList.contains('show')) { chatText.focus(); greet(); }
  });

  document.getElementById('chatSend').addEventListener('click', ()=>{
    const text = chatText.value.trim();
    if (!text) return;
    addMessage(text, 'user');
    chatText.value = '';
    // reply logic: try to match keys
    const q = text.toLowerCase();
    let reply = null;
    for (const k in ARYAN_FACTS){
      if (q.includes(k)) { reply = ARYAN_FACTS[k]; break; }
    }
    if (!reply){
      if (q.includes('name')) reply = "Aryan is Aryan Sharma — that guy who turns everyday moments into funny stories.";
      else if (q.includes('coffee')) reply = ARYAN_FACTS["what’s aryan’s comfort drink"] || "Coffee ☕";
      else if (q.includes('study')|| q.includes('studying')) reply = ARYAN_FACTS["what is aryan currently studying"] || "Pursuing a Bachelor's degree.";
      else if (q.includes('travel')) reply = ARYAN_FACTS["does aryan like travelling"] || "Yes! especially with coffee and mountains.";
      else reply = "Ask me anything about Aryan ☕🙂!";
    }
    // small delay for UX
    setTimeout(()=>addMessage(reply,'bot'), 260 + Math.random()*400);
  });

  chatText.addEventListener('keydown', (e)=>{ if (e.key === 'Enter') { e.preventDefault(); chatSend.click(); } });

  // allow close via ESC
  document.addEventListener('keydown', (e)=>{
    if (e.key === 'Escape') island.classList.remove('show');
  });

})();
</script>
</body>
</html>
"""

# Now combine hero_html + facts JS + hero_html_end into final_html string
full_hero_html = hero_html + facts_js + hero_html_end

# Render the hero HTML component (height tuned for large hero)
components.html(full_hero_html, height=760, scrolling=False)


# ---------------- Global CSS override for Streamlit (Apple glass + full galaxy) ----------------
st.markdown(
    """
    <style>
    /* make Streamlit app transparent so canvas shows through */
    .stApp {
      background: transparent !important;
      color: #eaf6ff !important;
    }

    /* make block containers glassy */
    .stBlock, .css-1lcbmhc.e1fqkh3o3, .st-b1, .css-18e3th9 {
      background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02)) !important;
      border: 1px solid rgba(255,255,255,0.04) !important;
      box-shadow: 0 12px 40px rgba(6,8,14,0.45) !important;
      color: #eaf6ff !important;
    }

    /* headings & text */
    .css-10trblm.egzxvld1 { color: #eaf6ff !important; }
    .stMarkdown, .stText, .stButton { color: #eaf6ff !important; }
    a { color: #cfe8ff !important; }

    /* gallery images: rounded glass cards */
    .gallery-image img { border-radius:12px; box-shadow: 0 14px 40px rgba(3,6,12,0.5); }

    /* make horizontal rule subtle */
    hr { border-color: rgba(255,255,255,0.04); }

    /* responsive tweaks */
    @media (max-width:800px){
      .stBlock, .css-1lcbmhc.e1fqkh3o3 { padding: 12px !important; }
    }
    </style>
    """, unsafe_allow_html=True
)

# ---------------- Streamlit content: gallery & blog (restyled) ----------------
st.markdown("---")
col1, col2 = st.columns([1,2])

with col1:
    st.markdown("### 📸 Photos (Gallery)")
    images = get_gallery_images()
    if not images:
        st.info("No images found. Add files to the `gallery/` folder.")
    else:
        # modern grid preview: two per column (use st.image)
        for i, img in enumerate(images):
            st.markdown(f"<div class='gallery-image' style='margin-bottom:14px;'><img src='{img}' style='width:100%; border-radius:12px;'/></div>", unsafe_allow_html=True)
            if i >= 5: break
        if len(images) > 6:
            st.caption(f"Plus {len(images)-6} more — they'll appear here automatically.")

with col2:
    st.markdown("### ✍️ Writings (anonymous)")
    if "anon_messages" not in st.session_state:
        st.session_state.anon_messages = []
    with st.form("anon_form", clear_on_submit=True):
        msg = st.text_area("Share anonymously", placeholder="Write something anonymously...")
        submitted = st.form_submit_button("Send anonymously")
        if submitted and msg.strip():
            st.session_state.anon_messages.insert(0, {"msg": msg, "time": time.asctime()})
            st.success("Message sent anonymously — visible in admin (local session).")
    if st.session_state.anon_messages:
        for m in st.session_state.anon_messages[:8]:
            st.info(m["msg"])

    st.markdown("---")
    st.markdown("### 📰 Blog Posts")
    posts = get_all_posts()
    if not posts:
        st.info("No blog posts found. Add `.md` files to `blog_posts/`.")
    else:
        for p in posts:
            st.subheader(p["title"])
            st.caption(p.get("date",""))
            st.markdown(p["html"], unsafe_allow_html=True)
            st.markdown("---")

# Indicate the chat is available via the dynamic island
st.markdown("---")
st.info("Chat is available via the floating chat orb (bottom-right). Click to Ask me about Aryan.")

# ---------------- Projects / Contact: glass cards ----------------
st.markdown("---")
st.markdown("<a id='projects_anchor'></a>", unsafe_allow_html=True)
st.header("Projects")
st.markdown("""
<div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap:18px;">
  <div style="background:linear-gradient(180deg, rgba(255,255,255,0.95), rgba(255,255,255,0.9)); padding:16px; border-radius:12px;">
    <strong>Chatbot App</strong><div style="opacity:.8; margin-top:6px;">Client-side Q&A chatbot with personality & fallback logic.</div>
  </div>
  <div style="background:linear-gradient(180deg, rgba(255,255,255,0.95), rgba(255,255,255,0.9)); padding:16px; border-radius:12px;">
    <strong>Portfolio Website</strong><div style="opacity:.8; margin-top:6px;">This polished portfolio & blog system.</div>
  </div>
  <div style="background:linear-gradient(180deg, rgba(255,255,255,0.95), rgba(255,255,255,0.9)); padding:16px; border-radius:12px;">
    <strong>Machine Learning</strong><div style="opacity:.8; margin-top:6px;">Small experiments with models & data.</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<a id='contact'></a>", unsafe_allow_html=True)
st.header("Contact")
st.write("Prefer DM on Instagram: ", "[aryanxsharma26](https://instagram.com/aryanxsharma26)")

# ---------------- Footer / notes ----------------
st.markdown("---")
st.markdown("### ⚙️ Notes & Setup")
st.markdown("""
- Place `resume.pdf` at the project root or in `public/` so `/resume.pdf` resolves (used by Download Resume link).
- Gallery images go in `gallery/`. Blog posts go in `blog_posts/` as `.md`.
- The chatbot is client-side JS using your 20 Q&A entries. If you want server-side logging or LLM answers, I can wire that next.
- To tweak animation speed or star density, edit the canvas JS in the `hero_html` string at the top of this file.
""")
