# app.py
import os, time, re, json
import streamlit as st
from markdown import markdown
import streamlit.components.v1 as components

st.set_page_config(page_title="Aryan Sharma — Portfolio", layout="wide")

# ---------------- hide streamlit chrome ----------------
st.markdown("""
<style>
/* hide header/menu/footer */
#MainMenu, header, footer {visibility: hidden !important; height:0;}

/* ensure no container padding so the component can occupy whole viewport */
.block-container {padding: 0 !important; margin: 0 auto !important; max-width: 100% !important;}
main {padding: 0 !important; margin: 0 !important;}
body {background: transparent !important; overflow-x: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------- helpers: gallery & posts ----------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
GALLERY_DIR = os.path.join(BASE_DIR, "gallery")
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")

def get_gallery_images():
    if not os.path.exists(GALLERY_DIR):
        return []
    files = [f for f in os.listdir(GALLERY_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif"))]
    files.sort()
    # convert to relative paths Streamlit serves as static files
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
    for m in sorted(md_files, reverse=True):
        slug = m[:-3]
        data = get_post_data(slug)
        if data:
            posts.append(data)
    return posts

# Build dynamic HTML fragments for gallery and posts
gallery_images = get_gallery_images()
gallery_html = ""
if gallery_images:
    for i, img in enumerate(gallery_images):
        # small alt from filename
        alt = os.path.basename(img)
        gallery_html += f'<div class="gallery-item"><img src="{img}" alt="{alt}" loading="lazy"/></div>\n'
else:
    gallery_html = '<div class="empty-note">No images found — add files to the <code>gallery/</code> folder.</div>'

posts = get_all_posts()
posts_html = ""
if posts:
    for p in posts:
        posts_html += f'''
        <article class="post-card">
          <h3 class="post-title">{p["title"]}</h3>
          <div class="post-meta">{p.get("date","")}</div>
          <div class="post-body">{p["html"]}</div>
        </article>
        '''
else:
    posts_html = '<div class="empty-note">No blog posts — add `.md` files to <code>blog_posts/</code>.</div>'

# Aryan facts (chatbot)
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

# Serialize facts for JS
facts_json = json.dumps(ARYAN_FACTS)

# social links
linkedin = "https://www.linkedin.com/in/aryan-sharma99999"
instagram = "https://instagram.com/aryanxsharma26"

# ---------------- full HTML (single component) ----------------
html = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
<style>
:root{
  --bg1:#0b001a;
  --glass: rgba(255,255,255,0.03);
  --accent1: #8b52ff;
  --accent2: #ff66d2;
  --muted: rgba(230,225,255,0.14);
}
*{box-sizing:border-box}
html,body{height:100%; margin:0; font-family:Inter, system-ui, -apple-system, sans-serif; color:#e9e6ff; -webkit-font-smoothing:antialiased}
a{color:inherit}
/* full background */
.site-bg{
  position:fixed; inset:0; z-index:-3;
  background: radial-gradient(circle at 10% 10%, rgba(120,20,140,0.12), transparent 10%),
              radial-gradient(circle at 90% 80%, rgba(100,10,140,0.12), transparent 15%),
              linear-gradient(180deg,#0b001a 0%, #12001f 70%, #07000a 100%);
}

/* starfield layer */
.starfield{
  position:fixed; inset:0; z-index:-2; pointer-events:none;
  background-image: radial-gradient(#fff 0.9px, transparent 0.9px);
  background-size: 6px 6px;
  opacity:0.12;
}

/* subtle nebula gradient */
.nebula{
  position:fixed; inset:0; z-index:-1; pointer-events:none;
  background: radial-gradient(ellipse at 70% 40%, rgba(130,60,180,0.12), transparent 20%),
              radial-gradient(ellipse at 20% 70%, rgba(90,10,110,0.08), transparent 25%);
}

/* top navbar */
.navbar{
  position:fixed; top:18px; left:50%; transform:translateX(-50%);
  display:flex; gap:18px; z-index:60; align-items:center;
  padding:8px 14px; border-radius:999px; backdrop-filter: blur(6px);
  background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
  border:1px solid rgba(255,255,255,0.04);
  box-shadow: 0 6px 30px rgba(2,2,6,0.6);
}
.navbar .brand{ font-weight:800; letter-spacing:1px; padding-right:8px; color: #f2eaff}
.nav-item{ color:#dfe6ff; padding:8px 12px; border-radius:10px; cursor:pointer; font-weight:600; font-size:14px; opacity:0.95}
.nav-item:hover{ background: rgba(255,255,255,0.02); transform:translateY(-2px)}

/* layout */
.container{ width:100%; max-width:1200px; margin:0 auto; padding:0 28px; }

/* hero */
.hero {
  height:100vh; display:flex; align-items:center; justify-content:center; padding-top:30px; padding-bottom:30px;
}
.hero-card{
  width:90%; max-width:1100px; border-radius:20px; padding:48px 56px; text-align:center;
  background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));
  border:1px solid rgba(255,255,255,0.04);
  box-shadow: 0 40px 80px rgba(6,6,18,0.7);
  position:relative; overflow:hidden;
}

/* animated edge - mask trick */
.hero-card:after{
  content:"";
  position:absolute; inset:-2px; z-index:0; border-radius:18px;
  padding:2px;
  background: conic-gradient(from 180deg at 50% 50%, rgba(138,81,255,0.62), rgba(255,96,210,0.62), rgba(138,81,255,0.62));
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  animation: edgeMove 3.4s linear infinite;
  opacity:0.9;
}
@keyframes edgeMove {
  0%{transform:rotate(0deg)}
  50%{transform:rotate(180deg)}
  100%{transform:rotate(360deg)}
}

/* hero typography */
.hero-title{ font-size:56px; font-weight:800; margin:0; background:linear-gradient(90deg,#dfb3ff,#ffffff); -webkit-background-clip:text; color:transparent; z-index:2}
.hero-sub{ margin-top:10px; color:#d7d4ff; z-index:2}
.role { margin-top:12px; font-weight:700; color:#ffdff8; z-index:2}

/* buttons */
.hero-actions{ margin-top:20px; display:flex; gap:12px; justify-content:center; align-items:center; z-index:2}
.btn {
  padding:12px 20px; border-radius:999px; font-weight:700; cursor:pointer; border:none;
}
.btn-primary{ background: linear-gradient(90deg,var(--accent1),var(--accent2)); color:#071026; box-shadow: 0 8px 30px rgba(120,40,160,0.25)}
.btn-ghost{ background:transparent; border:1px solid rgba(255,255,255,0.06); color:#dfe8ff }

/* sections area below hero */
.page-body { padding: 60px 20px 140px; }

/* grid cards */
.grid {
  display:grid;
  grid-template-columns: 1fr 2fr;
  gap:28px;
  align-items:start;
}

/* glass cards */
.card {
  background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
  padding:18px; border-radius:12px; border:1px solid rgba(255,255,255,0.035);
  box-shadow: 0 16px 40px rgba(0,0,0,0.45);
}

/* gallery */
.gallery {
  display:grid;
  grid-template-columns: repeat(2, 1fr);
  gap:10px;
}
.gallery-item img { width:100%; height:120px; object-fit:cover; border-radius:8px; transition: transform .25s; }
.gallery-item img:hover { transform: scale(1.04); }

/* blog posts */
.post-card { background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); padding:22px; border-radius:12px; margin-bottom:16px; border:1px solid rgba(255,255,255,0.03); }
.post-title { font-size:20px; font-weight:800; color:#f5eaff; margin:0 0 8px 0; }
.post-meta { color:#cfc9e6; font-size:13px; margin-bottom:8px; }

/* writings */
.empty-note{ color:#d9d6ea; padding:12px; border-radius:8px; background: rgba(255,255,255,0.01); }

/* footer */
.footer { padding:40px 20px; text-align:center; color:#d7d2ea; }

/* responsive */
@media (max-width:900px){
  .grid{ grid-template-columns: 1fr; }
  .hero-title{ font-size:34px; }
  .hero-card{ padding:28px; }
  .gallery-item img{ height:90px; }
  .navbar{ left:12px; transform:none; right:12px; top:12px;}
}
</style>
</head>
<body>
<div class="site-bg"></div>
<div class="starfield"></div>
<div class="nebula"></div>

<!-- NAV -->
<div class="navbar container" role="navigation" aria-label="main-nav">
  <div class="brand">ARYAN</div>
  <div class="nav-item" onclick="scrollToId('hero')">Home</div>
  <div class="nav-item" onclick="scrollToId('gallery')">Gallery</div>
  <div class="nav-item" onclick="scrollToId('writings')">Writings</div>
  <div class="nav-item" onclick="scrollToId('blog')">Blog</div>
  <div class="nav-item" onclick="scrollToId('projects')">Projects</div>
  <div style="width:12px"></div>
</div>

<!-- HERO -->
<section id="hero" class="hero" aria-label="hero section">
  <div class="hero-card container" role="region" aria-labelledby="site-title">
    <h1 class="hero-title" id="site-title">ARYAN SHARMA</h1>
    <div class="hero-sub">Welcome to my personal website — crafted with attention to detail.</div>
    <div class="role">I'm a <span id="roleTxt">web developer</span></div>
    <div class="hero-actions">
      <a class="btn btn-primary" href="/resume.pdf" download>Download Resume</a>
      <a class="btn btn-ghost" href=""" + linkedin + """ target="_blank">LinkedIn</a>
      <a class="btn btn-ghost" href=""" + instagram + """ target="_blank">Instagram</a>
    </div>
  </div>
</section>

<!-- CONTENT -->
<section class="page-body container" id="content">
  <div class="grid">
    <div>

      <!-- Gallery card -->
      <div class="card" id="gallery" role="region" aria-label="gallery section">
        <h3 style="margin-top:0">📸 Photos (Gallery)</h3>
        <div class="gallery">
          """ + gallery_html + """
        </div>
      </div>

      <div style="height:20px"></div>

      <!-- Projects -->
      <div class="card" id="projects" role="region" aria-label="projects">
        <h3 style="margin-top:0">🧩 Projects</h3>
        <ul>
          <li><strong>Chatbot Website</strong> — Client-side Q&A & demo</li>
          <li><strong>Portfolio Builder</strong> — Template & theme</li>
          <li><strong>AI Experiments</strong> — Small ML projects</li>
        </ul>
      </div>

    </div>

    <div>
      <!-- Writings -->
      <div class="card" id="writings" role="region" aria-label="writings">
        <h3 style="margin-top:0">📝 Writings (anonymous)</h3>
        <div class="empty-note">No anonymous writings yet — use the Streamlit sidebar form or add via app session.</div>
      </div>

      <div style="height:20px"></div>

      <!-- Blog -->
      <div class="card" id="blog" role="region" aria-label="blog posts">
        <h3 style="margin-top:0">📰 Blog Posts</h3>
        """ + posts_html + """
      </div>
    </div>
  </div>

  <div style="height:28px"></div>

  <div class="card">
    <h3 style="margin-top:0">Contact & Socials</h3>
    <p>Built with ❤️ — Connect: <a href='""" + linkedin + """' target='_blank'>LinkedIn</a> • <a href='""" + instagram + """' target='_blank'>Instagram</a></p>
  </div>

</section>

<footer class="footer">© 2025 Aryan Sharma</footer>

<!-- Floating chat orb -->
<div id="chatOrb" style="position:fixed;right:26px;bottom:26px;z-index:80;">
  <button id="openChat" title="Ask me about Aryan" style="width:64px;height:64px;border-radius:50%;border:none;background:linear-gradient(135deg, #8b52ff,#ff66d2);box-shadow:0 10px 30px rgba(140,60,255,0.3);cursor:pointer;font-size:26px;color:white;">💬</button>
</div>

<!-- Chat popup (simple) -->
<div id="chatPopup" style="position:fixed;right:26px;bottom:96px;z-index:90;display:none;width:360px;background:rgba(6,6,10,0.92);border-radius:12px;padding:12px;border:1px solid rgba(255,255,255,0.04);box-shadow:0 20px 60px rgba(2,2,8,0.6);">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;color:#cfe7ff;font-weight:700;">Ask me about Aryan <button id="closeChat" style="background:transparent;border:none;color:#9fbde8;cursor:pointer;font-size:16px;">✕</button></div>
  <div id="chatMessages" style="max-height:260px;overflow:auto;padding:6px 0;color:#e6eefc;"></div>
  <div style="display:flex;gap:8px;margin-top:8px;">
    <input id="chatInput" placeholder="Type a question (e.g. Who is Aryan?)" style="flex:1;padding:10px;border-radius:8px;border:1px solid rgba(255,255,255,0.06);background:#0b0b0e;color:#eaf3ff" />
    <button id="chatSend" style="padding:10px 12px;border-radius:8px;border:none;background:linear-gradient(90deg,#8b52ff,#ff66d2);color:#071026;font-weight:700;cursor:pointer">Send</button>
  </div>
</div>

<script>
/* smooth scroll helper */
function scrollToId(id){
  const el = document.getElementById(id);
  if(!el) return;
  window.scrollTo({top: el.getBoundingClientRect().top + window.scrollY - 60, behavior: 'smooth'});
}

/* Typewriter roles */
const roles = ["web developer","tech enthusiast","video editor","writer","designer","learner"];
let ridx = 0, rpos = 0, rfor = true;
const roleEl = document.getElementById('roleTxt');
function tick(){
  const cur = roles[ridx];
  if(rfor){
    rpos++; roleEl.textContent = cur.slice(0,rpos);
    if(rpos===cur.length){ rfor=false; setTimeout(tick,900); return; }
  } else {
    rpos--; roleEl.textContent = cur.slice(0,rpos);
    if(rpos===0){ rfor=true; ridx=(ridx+1)%roles.length; setTimeout(tick,400); return; }
  }
  setTimeout(tick,70);
}
tick();

/* Chat logic - client-side facts (injected from Python) */
const ARYAN_FACTS = %s;

const openBtn = document.getElementById('openChat');
const chatPopup = document.getElementById('chatPopup');
const closeBtn = document.getElementById('closeChat');
const chatSend = document.getElementById('chatSend');
const chatInput = document.getElementById('chatInput');
const chatMessages = document.getElementById('chatMessages');

openBtn.onclick = ()=> { chatPopup.style.display = 'block'; chatInput.focus(); if(!chatMessages.innerHTML) addBot("Hi! I'm Aryan's assistant ☕ Ask me anything about Aryan."); };
closeBtn.onclick = ()=> { chatPopup.style.display = 'none'; };

function addUser(txt){
  const d = document.createElement('div'); d.style.textAlign='right'; d.style.margin='8px 0'; d.innerHTML = '<div style="display:inline-block;background:rgba(255,255,255,0.06);padding:8px 12px;border-radius:12px;color:#fff;">'+escapeHTML(txt)+'</div>';
  chatMessages.appendChild(d); chatMessages.scrollTop = chatMessages.scrollHeight;
}
function addBot(txt){
  const d = document.createElement('div'); d.style.textAlign='left'; d.style.margin='8px 0'; d.innerHTML = '<div style="display:inline-block;background:linear-gradient(90deg, rgba(120,120,255,0.07), rgba(120,50,180,0.04));padding:8px 12px;border-radius:12px;color:#eaf4ff;">'+escapeHTML(txt)+'</div>';
  chatMessages.appendChild(d); chatMessages.scrollTop = chatMessages.scrollHeight;
}
function escapeHTML(s){ return s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;'); }

function answer(q){
  const ql = q.toLowerCase();
  for(const k in ARYAN_FACTS){
    if(ql.includes(k)) return ARYAN_FACTS[k];
  }
  if(ql.includes('name')) return "Aryan Sharma — that guy who turns everyday moments into stories (and drinks coffee).";
  if(ql.includes('coffee')) return ARYAN_FACTS["what’s aryan’s comfort drink"];
  if(ql.includes('study')||ql.includes('studying')) return ARYAN_FACTS["what is aryan currently studying"];
  return "Ask me anything about Aryan ☕🙂!";
}

chatSend.onclick = ()=>{
  const t = chatInput.value.trim();
  if(!t) return;
  addUser(t); chatInput.value='';
  setTimeout(()=> { addBot(answer(t)); }, 320 + Math.random()*360);
};
chatInput.addEventListener('keydown', (e)=>{ if(e.key==='Enter'){ e.preventDefault(); chatSend.click(); }})

/* populate gallery image lightbox click (simple) */
document.querySelectorAll('.gallery-item img').forEach(img=>{
  img.style.cursor='zoom-in';
  img.onclick = ()=> {
    const overlay = document.createElement('div'); overlay.style.position='fixed'; overlay.style.inset=0; overlay.style.background='rgba(0,0,0,0.85)'; overlay.style.display='flex'; overlay.style.alignItems='center'; overlay.style.justifyContent='center'; overlay.style.zIndex=9999;
    const big = document.createElement('img'); big.src = img.src; big.style.maxWidth='90%'; big.style.maxHeight='90%'; big.style.borderRadius='8px'; overlay.appendChild(big);
    overlay.onclick = ()=> document.body.removeChild(overlay);
    document.body.appendChild(overlay);
  }
});
</script>

</body>
</html>
""" % (facts_json)

# Render the full site as a single HTML component. Allow internal scrolling so the page behaves like a normal website.
components.html(html, height=900, scrolling=True)

# ---------------- Optional small Streamlit admin bits below (hidden if user hides sidebar) ----------------
st.sidebar.title("Editor: Gallery & Blog")
st.sidebar.write("- Add images to `gallery/` (jpg/png/webp/gif) to populate the gallery.")
st.sidebar.write("- Add markdown files (`.md`) to `blog_posts/` to create blog posts (YAML frontmatter supported).")
st.sidebar.write("Use the chat orb (bottom-right) to ask questions about Aryan.")
