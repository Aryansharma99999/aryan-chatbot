# app.py — Final FAANG-style portfolio (Hero + Gallery + Premium Chatbot)
import os
import re
import time
import base64
import streamlit as st
from markdown import markdown
import streamlit.components.v1 as components

# ---------------- Page config ----------------
st.set_page_config(page_title="Aryan Sharma", layout="wide", initial_sidebar_state="collapsed")

# ---------------- Paths & helpers ----------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
GALLERY_DIR = os.path.join(BASE_DIR, "gallery")
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")


def get_gallery_images():
    """Return sorted list of image paths in gallery folder."""
    if not os.path.exists(GALLERY_DIR):
        return []
    files = [f for f in os.listdir(GALLERY_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
    files.sort()
    return [os.path.join(GALLERY_DIR, f) for f in files]


def to_base64(path):
    """Return base64 data URL for an image path or None on error."""
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
        data = base64.b64encode(raw).decode("utf-8")
        ext = os.path.splitext(path)[1].lower().replace(".", "")
        # normalize jpg -> jpeg
        if ext == "jpg":
            ext = "jpeg"
        return f"data:image/{ext};base64,{data}"
    except Exception:
        return None


def get_post_data(slug):
    """Read markdown post and extract simple YAML-like meta block if present."""
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
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = content[meta_match.end():].strip()
    html = markdown(body)
    return {
        "slug": slug,
        "title": meta.get("title", slug.replace("-", " ").title()),
        "date": meta.get("date", ""),
        "author": meta.get("author", ""),
        "summary": meta.get("summary", ""),
        "html": html,
    }


def get_all_posts():
    """Return list of parsed posts found in blog_posts/"""
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


# ---------------- HERO (FAANG-like pastel + Sora font) ----------------
hero_html = '''
<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
:root{
  --p1:#fbe9f9; --p2:#eaf6ff; --p3:#f7f0ff;
  --accent:#7b44e5;
  --card: rgba(255,255,255,0.74);
}
*{box-sizing:border-box}
html,body{height:100%;margin:0;padding:0;background:transparent;font-family:'Sora',system-ui,Arial,sans-serif;}
.hero-stage{
  position:relative; min-height:78vh; display:flex; align-items:center; justify-content:center;
  padding:48px;
  background: linear-gradient(180deg,var(--p2),var(--p3),var(--p1));
  overflow:hidden;
}
.blob{ position:absolute; filter:blur(56px); opacity:.85; transform:translate3d(0,0,0); border-radius:50%; }
.b1{ width:640px; height:520px; left:-140px; top:-100px; background:linear-gradient(90deg,#ffdbe9,#eaf6ff);}
.b2{ width:500px; height:420px; right:-160px; top:30px; background:linear-gradient(90deg,#f6ecff,#e7f8ff);}
.b3{ width:380px; height:320px; left:12%; bottom:-120px; background:linear-gradient(90deg,#fff2ec,#f9f0ff);}

.hero-card{
  width:92%; max-width:1200px; border-radius:22px; padding:48px; background:var(--card);
  border:1px solid rgba(255,255,255,0.7); box-shadow: 0 40px 100px rgba(6,6,8,0.06);
  backdrop-filter: blur(12px) saturate(120%);
  transform-style:preserve-3d; transition: transform 0.12s ease-out;
  position:relative;
}

.hero-grid{ display:flex; gap:28px; align-items:flex-start; }
.left {
  flex:1 1 60%;
}
.hi { margin:0; color:#6b6f77; font-weight:600; }
.title { margin:6px 0 0 0; font-size:56px; font-weight:800; color:#0f1113; letter-spacing:-0.6px; }
.lead { margin-top:12px; color:#404345; font-size:18px; max-width:84%; line-height:1.45; }
.role-pill { display:inline-block; margin-top:14px; padding:10px 16px; border-radius:999px; background:linear-gradient(90deg, rgba(123,68,229,0.12), rgba(123,68,229,0.06)); color:var(--accent); font-weight:700; }

.actions{ margin-top:24px; display:flex; gap:12px; align-items:center; }
.btn { padding:12px 20px; border-radius:999px; border:none; cursor:pointer; font-weight:700; background:linear-gradient(90deg,#ffd6eb,#dfe9ff); }
.ghost { padding:12px 20px; border-radius:999px; background:transparent; border:1px solid rgba(0,0,0,0.06); }

.right-previews{ width:260px; display:flex; gap:12px; flex-direction:column; align-items:flex-end; transform: translateZ(40px); }
.preview-card{ width:84px; height:84px; border-radius:12px; overflow:hidden; background:linear-gradient(180deg,rgba(255,255,255,0.8),rgba(255,255,255,0.6)); box-shadow: 0 18px 36px rgba(8,10,16,0.06); border:1px solid rgba(255,255,255,0.6); display:flex; align-items:center; justify-content:center; }
.preview-card img{ width:100%; height:100%; object-fit:cover; display:block; }

@media (max-width:980px){
  .hero-grid{ flex-direction:column; }
  .right-previews{ display:none; }
  .title{ font-size:36px; }
  .hero-card{ padding:28px; border-radius:18px; }
}
</style>
</head>
<body>
  <div class="hero-stage" id="heroStage">
    <div class="blob b1"></div>
    <div class="blob b2"></div>
    <div class="blob b3"></div>

    <div class="hero-card" id="heroCard">
      <div class="hero-grid">
        <div class="left">
          <p class="hi">Hello, I'm</p>
          <h1 class="title">Aryan Sharma</h1>
          <p class="lead">I turn everyday life into little stories—coffee-powered, curious, and always building.</p>
          <div class="role-pill" id="roleField">Creative Storyteller</div>

          <div class="actions">
            <button class="btn" onclick="location.href='#projects'">View Projects</button>
            <button class="ghost" onclick="location.href='#contact'">Contact</button>
          </div>
        </div>

        <div class="right-previews" aria-hidden="true">
          <div class="preview-card"><img id="p1" src=""></div>
          <div class="preview-card"><img id="p2" src=""></div>
          <div class="preview-card"><img id="p3" src=""></div>
        </div>
      </div>
    </div>
  </div>

<script>
/* typewriter */
const roles = ["Creative Storyteller","Tech Enthusiast","AI Learner","Coffee-Powered Human ☕"];
let ridx = 0, rpos = 0, rfor = true;
const roleEl = document.getElementById("roleField");
function typeTick(){
  const cur = roles[ridx];
  if (rfor){
    rpos++;
    roleEl.textContent = cur.slice(0,rpos);
    if (rpos === cur.length){ rfor = false; setTimeout(typeTick,900); return; }
  } else {
    rpos--;
    roleEl.textContent = cur.slice(0,rpos);
    if (rpos === 0){ rfor = true; ridx = (ridx+1)%roles.length; setTimeout(typeTick,400); return; }
  }
  setTimeout(typeTick,60);
}
typeTick();

/* parallax */
const hero = document.getElementById("heroCard");
document.addEventListener("mousemove", (e) => {
  const x = (window.innerWidth/2 - e.clientX)/40;
  const y = (window.innerHeight/2 - e.clientY)/40;
  hero.style.transform = `perspective(900px) rotateY(${x}deg) rotateX(${y}deg)`;
});
</script>
</body>
</html>
'''
# render hero component
components.html(hero_html, height=760, scrolling=False)

# ---------------- Inject hero preview images (first 3 gallery images) ----------------
images = get_gallery_images()

inject_parts = []
for i in range(3):
    if i < len(images):
        data = to_base64(images[i])
        if data:
            inject_parts.append(f"document.getElementById('p{i+1}').src = '{data}';")
        else:
            inject_parts.append(f"document.getElementById('p{i+1}').style.display='none';")
    else:
        inject_parts.append(f"document.getElementById('p{i+1}').style.display='none';")

inject_js = "<script>" + "".join(inject_parts) + "</script>"
st.markdown(inject_js, unsafe_allow_html=True)


# ---------------- Global theme CSS for Streamlit area ----------------
st.markdown("""
<style>
.stApp {
  background: linear-gradient(180deg, rgba(234,246,255,0.95), rgba(247,240,255,0.96)) !important;
  color: #111;
}
/* glassy card style */
.stBlock, .css-1lcbmhc.e1fqkh3o3, .st-b1 {
  background: rgba(255,255,255,0.78) !important;
  border: 1px solid rgba(255,255,255,0.66);
  box-shadow: 0 12px 30px rgba(12,12,18,0.04);
  backdrop-filter: blur(8px) !important;
}
.css-10trblm.egzxvld1 { color:#18181b; }
.stMarkdown { color:#222; }
a { color: #7b44e5 !important; }

/* ensure gallery classes are styled when HTML is injected */
.gallery-grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap:18px; align-items:start; }
.gallery-item { border-radius:14px; overflow:hidden; box-shadow: 0 10px 30px rgba(16,18,26,0.06); transition: transform .25s ease, box-shadow .25s ease; background: white;}
.gallery-item img { width:100%; height:100%; object-fit:cover; display:block; transition: transform .45s ease; }
.gallery-item:hover { transform: translateY(-8px); box-shadow: 0 20px 60px rgba(16,18,26,0.09); }
.gallery-item:hover img { transform: scale(1.06); }
</style>
""", unsafe_allow_html=True)


# ---------------- Content: Writings & Projects ----------------
st.markdown("---")
st.header("Writings & Projects")
st.subheader("Latest Writings")
posts = get_all_posts()
if not posts:
    st.info("No blog posts found. Add `.md` files to the blog_posts/ folder.")
else:
    for p in posts:
        st.subheader(p["title"])
        if p.get("date"):
            st.caption(p["date"])
        st.markdown(p["html"], unsafe_allow_html=True)
        st.markdown("---")

st.subheader("Projects")
st.markdown("""
- Chatbot Website (this site)  
- Portfolio Builder  
- AI Experiments  
(You can add project details or link to repositories.)
""")

st.markdown("<a id='contact'></a>", unsafe_allow_html=True)
st.header("Contact")
st.write("Prefer DM on Instagram: ", "[aryanxsharma26](https://instagram.com/aryansharmax26)")


# ---------------- Gallery (C3) ----------------
st.markdown("---")
st.markdown("<a id='gallery'></a>", unsafe_allow_html=True)
st.header("Gallery")

if not images:
    st.info("No gallery images found. Add images (jpg, png, webp) to the `gallery/` folder.")
else:
    gallery_items = []
    for p in images:
        b64 = to_base64(p)
        if not b64:
            continue
        nm = os.path.basename(p)
        gallery_items.append(f'''
            <div class="gallery-item" onclick="openLightbox('{b64}')">
                <img src="{b64}" alt="{nm}" loading="lazy"/>
            </div>
        ''')
    gallery_html = """
    <div style="padding:10px 14px;">
      <div style="display:flex; justify-content:space-between; align-items:center; gap:12px;">
        <h2 style="margin:6px 0 10px 6px; color:#2b2b2f;">Photographs</h2>
        <div style="color:#6b6f77; font-weight:600; font-size:14px;">Click an image to view</div>
      </div>

      <div style="padding-top:6px;" class="gallery-grid">
    """ + "".join(gallery_items) + """
      </div>
    </div>

    <!-- Lightbox -->
    <div id="ps-lightbox" style="display:none; position:fixed; inset:0; z-index:99999; align-items:center; justify-content:center; background: rgba(8,10,14,0.6);">
      <div style="position:relative; max-width:92%; max-height:92%; display:flex; align-items:center; justify-content:center;">
        <img id="pslb-img" src="" style="max-width:100%; max-height:100%; border-radius:12px; box-shadow: 0 30px 90px rgba(0,0,0,0.6);" />
        <button onclick="closeLightbox()" style="position:absolute; right:-10px; top:-10px; background:#fff; border-radius:999px; border:none; padding:8px 10px; cursor:pointer; font-weight:700;">✕</button>
      </div>
    </div>

    <script>
      function openLightbox(src){
        const lb = document.getElementById('ps-lightbox');
        const img = document.getElementById('pslb-img');
        img.src = src;
        lb.style.display = 'flex';
        lb.style.opacity = 0;
        requestAnimationFrame(()=>{ lb.style.transition = 'opacity 220ms ease'; lb.style.opacity = 1; });
      }
      function closeLightbox(){
        const lb = document.getElementById('ps-lightbox');
        lb.style.opacity = 0;
        setTimeout(()=>{ lb.style.display = 'none'; }, 220);
      }
      document.addEventListener('keydown', function(e){
        if (e.key === 'Escape') closeLightbox();
      });
    </script>
    """
    st.markdown(gallery_html, unsafe_allow_html=True)


# ---------------- Premium Floating Chatbot (Style A) ----------------
chat_html = '''
<style>
#aryan-chat-float { position: fixed; right: 28px; bottom: 28px; z-index: 999999; font-family: 'Sora', sans-serif; }
#aryan-chat-btn {
    width:72px; height:72px; border-radius:50%; border:none; cursor:pointer;
    background: linear-gradient(180deg,#ffeef8,#eaf6ff);
    box-shadow: 0 20px 50px rgba(6,8,12,0.12); font-size:15px; font-weight:700; padding:8px;
    transition: transform .22s ease, box-shadow .22s ease;
}
#aryan-chat-btn:hover { transform: translateY(-6px); box-shadow: 0 28px 70px rgba(6,8,12,0.16); }

/* Chat window */
#aryan-chat-box {
    position: fixed; right: 28px; bottom: 110px; width: 380px; max-width:92vw; display:none; z-index:1000000;
    border-radius:14px; overflow:hidden; box-shadow: 0 30px 90px rgba(6,8,12,0.28);
    background: linear-gradient(180deg,#071217,#0a0f12); color:#dff6ff;
    transform-origin: bottom right; transition: all 260ms cubic-bezier(.2,.9,.2,1);
}
#aryan-chat-head { padding:10px 14px; display:flex; justify-content:space-between; align-items:center; font-weight:800; color:#bfefff; background:linear-gradient(90deg,#061014,#081218); }
#aryan-chat-body { max-height:300px; overflow:auto; padding:12px; background:linear-gradient(180deg,#071014,#071116); }
.chat-msg { margin:8px 0; padding:10px 12px; border-radius:10px; max-width:82%; white-space:pre-wrap; font-size:14px; }
.chat-user { background:white; color:#071018; margin-left:18%; }
.chat-bot { background:linear-gradient(90deg,#0f1720,#0b1114); color:#dff9ff; margin-right:18%; }

/* input area */
#aryan-chat-input-wrap { display:flex; gap:8px; padding:12px; background:#071014; }
#aryan-chat-input { flex:1; padding:10px; border-radius:8px; border:none; background:#0f1416; color:#dbefff; }
#aryan-chat-send { padding:10px 12px; border-radius:8px; border:none; background:linear-gradient(90deg,#ffd6eb,#dfe9ff); color:#14121a; font-weight:800; cursor:pointer; }
@media (max-width:480px){
  #aryan-chat-box { right: 12px; left:12px; width: auto; bottom: 90px; }
  #aryan-chat-btn { width:58px; height:58px; font-size:14px; }
}
</style>

<div id="aryan-chat-float">
  <button id="aryan-chat-btn" aria-label="Ask me about Aryan">Ask me about Aryan ☕</button>

  <div id="aryan-chat-box" role="dialog" aria-label="Aryan chatbot">
    <div id="aryan-chat-head">
      <div>Ask me about Aryan ☕</div>
      <div><button id="aryan-chat-close" style="background:transparent;border:none;color:#bfefff;font-weight:800;cursor:pointer;">✕</button></div>
    </div>

    <div id="aryan-chat-body" aria-live="polite"></div>

    <div id="aryan-chat-input-wrap">
      <input id="aryan-chat-input" placeholder="Type a question..." />
      <button id="aryan-chat-send">Send</button>
    </div>
  </div>
</div>

<script>
(function(){
  const facts = {
    "who is aryan":"Aryan is someone who turns everyday moments into little stories—coffee-powered and curious.",
    "what is aryan studying":"Pursuing a Bachelor's degree. 🎓",
    "coffee":"Coffee ☕ is essential — without it he's basically on airplane mode.",
    "travel":"Yes — especially trips that end with coffee and mountain views.",
    "vibe":"Chill, creative, and always ready for a laugh."
  };

  const btn = document.getElementById('aryan-chat-btn');
  const box = document.getElementById('aryan-chat-box');
  const closeBtn = document.getElementById('aryan-chat-close');
  const body = document.getElementById('aryan-chat-body');
  const input = document.getElementById('aryan-chat-input');
  const send = document.getElementById('aryan-chat-send');

  function addMessage(text, who){
    const el = document.createElement('div');
    el.className = 'chat-msg ' + (who==='user'?'chat-user':'chat-bot');
    el.textContent = text;
    body.appendChild(el);
    body.scrollTop = body.scrollHeight;
  }

  function replyTo(q){
    const t = q.toLowerCase();
    for (let k in facts){
      if (t.includes(k)) return facts[k];
    }
    if (t.includes('name')) return "Aryan Sharma — storyteller, coder, coffee-lover.";
    if (t.includes('study') || t.includes('studying')) return facts["what is aryan studying"];
    if (t.includes('coffee')) return facts["coffee"];
    return "Ask me anything about Aryan ☕🙂";
  }

  function openBox(){
    box.style.display = 'block';
    requestAnimationFrame(()=>{ box.style.opacity=1; box.style.transform='translateY(0)'; });
    if (!body.hasChildNodes()) addMessage("Hi! Ask me about Aryan ☕", 'bot');
    input.focus();
  }
  function closeBox(){
    box.style.opacity = 0;
    box.style.transform = 'translateY(8px)';
    setTimeout(()=>{ box.style.display='none'; }, 260);
  }

  btn.addEventListener('click', ()=>{
    if (box.style.display === 'block') closeBox(); else openBox();
  });
  closeBtn.addEventListener('click', closeBox);

  function sendMsg(){
    const txt = input.value.trim();
    if (!txt) return;
    addMessage(txt, 'user');
    input.value = '';
    setTimeout(()=>{ addMessage(replyTo(txt), 'bot'); }, 300 + Math.random()*300);
  }
  send.addEventListener('click', sendMsg);
  input.addEventListener('keydown', function(e){ if (e.key==='Enter'){ e.preventDefault(); sendMsg(); } });
})();
</script>
'''
components.html(chat_html, height=10, scrolling=False)


# ---------------- Footer ----------------
st.markdown("---")
st.markdown(f"<div style='text-align:center; opacity:0.78; padding:16px 0;'>© {time.strftime('%Y')} Aryan Sharma — Built with ☕</div>", unsafe_allow_html=True)
