# app.py — Premium FAANG-style portfolio with optimized static gallery + fixed chatbot
import os
import re
import time
import base64
import shutil
import streamlit as st
from markdown import markdown
import streamlit.components.v1 as components

# Try to import Pillow for image optimization
try:
    from PIL import Image, ImageOps
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

# ---------------- Page config ----------------
st.set_page_config(page_title="Aryan Sharma", layout="wide", initial_sidebar_state="collapsed")

# ---------------- Paths & helpers ----------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
GALLERY_DIR = os.path.join(BASE_DIR, "gallery")
THUMBS_DIR = os.path.join(GALLERY_DIR, "_thumbs")
WEBP_DIR = os.path.join(GALLERY_DIR, "_webp")
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")

# ensure gallery dirs exist (thumbs/webp will be created if needed)
os.makedirs(GALLERY_DIR, exist_ok=True)
os.makedirs(THUMBS_DIR, exist_ok=True)
os.makedirs(WEBP_DIR, exist_ok=True)


def list_gallery_images():
    """List original gallery images (jpg,jpeg,png,webp) sorted."""
    files = []
    if not os.path.exists(GALLERY_DIR):
        return files
    for f in sorted(os.listdir(GALLERY_DIR)):
        if f.startswith("_"):  # skip our helper folders
            continue
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            files.append(os.path.join(GALLERY_DIR, f))
    return files


def make_thumb(src_path, max_size=(900, 900), thumb_size=(360, 360)):
    """
    Create optimized full-size (max_size) and thumbnail (thumb_size) images in gallery/_webp and gallery/_thumbs.
    Returns tuple (thumb_path, webp_path) on success, (None,None) on failure.
    """
    if not PIL_AVAILABLE:
        return (None, None)
    try:
        filename = os.path.basename(src_path)
        name, _ = os.path.splitext(filename)
        thumb_path = os.path.join(THUMBS_DIR, f"{name}_thumb.webp")
        webp_path = os.path.join(WEBP_DIR, f"{name}.webp")

        # if both already exist and are newer than source, skip
        src_mtime = os.path.getmtime(src_path)
        if os.path.exists(thumb_path) and os.path.exists(webp_path):
            if os.path.getmtime(thumb_path) >= src_mtime and os.path.getmtime(webp_path) >= src_mtime:
                return (thumb_path, webp_path)

        img = Image.open(src_path).convert("RGB")
        img_full = ImageOps.exif_transpose(img)
        img_full.thumbnail(max_size, Image.LANCZOS)
        img_full.save(webp_path, "WEBP", quality=78, method=6)

        img_thumb = img.copy()
        img_thumb = ImageOps.exif_transpose(img_thumb)
        img_thumb.thumbnail(thumb_size, Image.LANCZOS)
        img_thumb.save(thumb_path, "WEBP", quality=78, method=6)

        return (thumb_path, webp_path)
    except Exception:
        return (None, None)


def to_data_url(path):
    """Return a small inline data URL for use in components (used only for tiny hero previews if needed)."""
    try:
        with open(path, "rb") as fh:
            data = base64.b64encode(fh.read()).decode("utf-8")
        ext = os.path.splitext(path)[1].lower().replace(".", "")
        if ext == "jpg":
            ext = "jpeg"
        return f"data:image/{ext};base64,{data}"
    except Exception:
        return None


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
        for line in meta_match.group(1).splitlines():
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
    if not os.path.exists(POSTS_DIR):
        return []
    md_files = [f for f in sorted(os.listdir(POSTS_DIR)) if f.endswith(".md")]
    posts = []
    for m in md_files:
        slug = m[:-3]
        data = get_post_data(slug)
        if data:
            posts.append(data)
    return posts


# ---------------- Generate/refresh thumbnails (safe & idempotent) ----------------
gallery_images = list_gallery_images()
thumb_map = []  # list of tuples (original_path, thumb_path_or_original, webp_path_or_original)

for p in gallery_images:
    if PIL_AVAILABLE:
        thumb, webp = make_thumb(p)
        thumb_map.append((p, thumb or p, webp or p))
    else:
        # fallback: no Pillow - just use original file paths
        thumb_map.append((p, p, p))


# ---------------- HERO HTML (same FAANG-like) ----------------
hero_html = '''
<!doctype html><html><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
:root{--p1:#fbe9f9;--p2:#eaf6ff;--p3:#f7f0ff;--accent:#7b44e5;--card: rgba(255,255,255,0.74);}
html,body{margin:0;padding:0;background:transparent;font-family:'Sora',sans-serif}
.hero-stage{position:relative;min-height:78vh;display:flex;align-items:center;justify-content:center;padding:48px;background:linear-gradient(180deg,var(--p2),var(--p3),var(--p1));overflow:hidden}
.blob{position:absolute;filter:blur(56px);opacity:.85;border-radius:50%}
.b1{width:640px;height:520px;left:-140px;top:-100px;background:linear-gradient(90deg,#ffdbe9,#eaf6ff)}
.b2{width:500px;height:420px;right:-160px;top:30px;background:linear-gradient(90deg,#f6ecff,#e7f8ff)}
.b3{width:380px;height:320px;left:12%;bottom:-120px;background:linear-gradient(90deg,#fff2ec,#f9f0ff)}
.hero-card{width:92%;max-width:1200px;border-radius:22px;padding:48px;background:var(--card);border:1px solid rgba(255,255,255,0.7);box-shadow:0 40px 100px rgba(6,6,8,0.06);backdrop-filter:blur(12px) saturate(120%);transform-style:preserve-3d;transition:transform 0.12s ease-out;position:relative}
.hero-grid{display:flex;gap:28px;align-items:flex-start}
.left{flex:1 1 60%}
.hi{margin:0;color:#6b6f77;font-weight:600}
.title{margin:6px 0 0 0;font-size:56px;font-weight:800;color:#0f1113;letter-spacing:-0.6px}
.lead{margin-top:12px;color:#404345;font-size:18px;max-width:84%;line-height:1.45}
.role-pill{display:inline-block;margin-top:14px;padding:10px 16px;border-radius:999px;background:linear-gradient(90deg, rgba(123,68,229,0.12), rgba(123,68,229,0.06));color:var(--accent);font-weight:700}
.actions{margin-top:24px;display:flex;gap:12px;align-items:center}
.btn{padding:12px 20px;border-radius:999px;border:none;cursor:pointer;font-weight:700;background:linear-gradient(90deg,#ffd6eb,#dfe9ff)}
.ghost{padding:12px 20px;border-radius:999px;background:transparent;border:1px solid rgba(0,0,0,0.06)}
.right-previews{width:260px;display:flex;gap:12px;flex-direction:column;align-items:flex-end;transform:translateZ(40px)}
.preview-card{width:84px;height:84px;border-radius:12px;overflow:hidden;background:linear-gradient(180deg,rgba(255,255,255,0.8),rgba(255,255,255,0.6));box-shadow:0 18px 36px rgba(8,10,16,0.06);border:1px solid rgba(255,255,255,0.6);display:flex;align-items:center;justify-content:center}
.preview-card img{width:100%;height:100%;object-fit:cover;display:block}
@media(max-width:980px){.hero-grid{flex-direction:column}.right-previews{display:none}.title{font-size:36px}.hero-card{padding:28px;border-radius:18px}}
</style>
</head><body>
<div class="hero-stage" id="heroStage">
  <div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div>
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
const roles = ["Creative Storyteller","Tech Enthusiast","AI Learner","Coffee-Powered Human ☕"];
let ridx=0,rpos=0,rfor=true;
const roleEl=document.getElementById('roleField');
function typeTick(){
  const cur=roles[ridx];
  if(rfor){ rpos++; roleEl.textContent=cur.slice(0,rpos); if(rpos===cur.length){ rfor=false; setTimeout(typeTick,900); return; } }
  else { rpos--; roleEl.textContent=cur.slice(0,rpos); if(rpos===0){ rfor=true; ridx=(ridx+1)%roles.length; setTimeout(typeTick,400); return; } }
  setTimeout(typeTick,60);
}
typeTick();
const hero=document.getElementById('heroCard');
document.addEventListener('mousemove',e=>{ const x=(window.innerWidth/2 - e.clientX)/40; const y=(window.innerHeight/2 - e.clientY)/40; hero.style.transform=`perspective(900px) rotateY(${x}deg) rotateX(${y}deg)`; });
</script>
</body></html>
'''

# render hero component
components.html(hero_html, height=760, scrolling=False)

# ---------------- Inject hero preview images (use thumbnails if available) ----------------
# Prepare JS that assigns p1/p2/p3 src to small thumb paths or data URLs
inject_js_lines = []
for i in range(3):
    if i < len(thumb_map):
        orig, thumb_path, webp_path = thumb_map[i]
        # prefer thumb_path (webp) if available
        if thumb_path and os.path.exists(thumb_path):
            # use relative path for Streamlit -- it serves files from app root
            rel = os.path.relpath(thumb_path, BASE_DIR).replace("\\", "/")
            inject_js_lines.append(f"document.getElementById('p{i+1}').src = '{rel}';")
        else:
            # fallback to data url of original (smaller risk)
            data_url = to_data_url(orig)
            if data_url:
                inject_js_lines.append(f"document.getElementById('p{i+1}').src = '{data_url}';")
            else:
                inject_js_lines.append(f"document.getElementById('p{i+1}').style.display='none';")
    else:
        inject_js_lines.append(f"document.getElementById('p{i+1}').style.display='none';")

inject_js = "<script>" + "".join(inject_js_lines) + "</script>"
st.markdown(inject_js, unsafe_allow_html=True)


# ---------------- Global Streamlit CSS ----------------
st.markdown("""
<style>
.stApp { background: linear-gradient(180deg, rgba(234,246,255,0.95), rgba(247,240,255,0.96)) !important; color:#111; }
.stBlock, .css-1lcbmhc.e1fqkh3o3, .st-b1 { background: rgba(255,255,255,0.78) !important; border:1px solid rgba(255,255,255,0.66); box-shadow:0 12px 30px rgba(12,12,18,0.04); backdrop-filter:blur(8px) !important; }
.css-10trblm.egzxvld1{ color:#18181b }
.stMarkdown{ color:#222 }
a{ color:#7b44e5 !important }
/* small navbar look */
header[role="banner"]{ display:none; } /* hide default streamlit header */
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
        if p.get("date"): st.caption(p["date"])
        st.markdown(p["html"], unsafe_allow_html=True)
        st.markdown("---")

st.subheader("Projects")
st.markdown("""
- Chatbot Website (this site)  
- Portfolio Builder  
- AI Experiments  
(You can add project details or link GitHub repos.)
""")
st.markdown("<a id='contact'></a>", unsafe_allow_html=True)
st.header("Contact")
st.write("Prefer DM on Instagram: ", "[aryanxsharma26](https://instagram.com/aryansharmax26)")


# ---------------- Gallery section (static thumbs for performance) ----------------
st.markdown("---")
st.markdown("<a id='gallery'></a>", unsafe_allow_html=True)
st.header("Gallery")

if not thumb_map:
    st.info("No gallery images found. Add jpg/png/webp images to the `gallery/` folder.")
else:
    # Build a responsive grid using columns (Streamlit)
    cols = st.columns(3)
    # display using thumbnails (relative file paths) which Streamlit serves fine
    for idx, (orig, thumb_path, webp_path) in enumerate(thumb_map):
        col = cols[idx % 3]
        # select best preview path (thumb_path if present else original)
        display_path = thumb_path if (thumb_path and os.path.exists(thumb_path)) else orig
        # convert to relative path for consistent serving in deployed app
        rel_path = os.path.relpath(display_path, BASE_DIR).replace("\\", "/")
        caption = os.path.basename(orig)
        with col:
            try:
                st.image(rel_path, caption=caption, use_column_width=True)
            except Exception:
                # fallback to st.image with PIL if relative path fails
                try:
                    from PIL import Image
                    im = Image.open(display_path)
                    st.image(im, caption=caption, use_column_width=True)
                except Exception:
                    st.write("Unable to show image:", caption)

    st.markdown("<small style='opacity:.7'>Click an image below to open the large viewer (lightbox).</small>", unsafe_allow_html=True)

    # Large lightbox viewer using injected HTML for smooth UX (uses webp/original data URLs)
    # Prepare JS array of full-res webp paths or data URLs
    viewer_items = []
    for orig, thumb_path, webp_path in thumb_map:
        full_path = webp_path if (webp_path and os.path.exists(webp_path)) else orig
        rel_full = os.path.relpath(full_path, BASE_DIR).replace("\\", "/")
        viewer_items.append(rel_full)

    # inject a small JS viewer at page bottom
    viewer_html = """
    <div id="viewer" style="display:none; position:fixed; inset:0; z-index:999999; align-items:center; justify-content:center; background:rgba(8,10,14,0.6);">
      <div style="position:relative; max-width:92%; max-height:92%; display:flex; align-items:center; justify-content:center;">
        <img id="viewer-img" src="" style="max-width:100%; max-height:100%; border-radius:12px; box-shadow:0 30px 90px rgba(0,0,0,0.6);" />
        <button onclick="closeViewer()" style="position:absolute; right:-10px; top:-10px; background:#fff; border-radius:999px; border:none; padding:8px 10px; cursor:pointer; font-weight:700;">✕</button>
      </div>
    </div>
    <script>
      const viewerItems = %s;
      function openViewer(src){
        const v = document.getElementById('viewer');
        const img = document.getElementById('viewer-img');
        img.src = src;
        v.style.display = 'flex';
      }
      function closeViewer(){
        const v = document.getElementById('viewer');
        v.style.display = 'none';
      }
      document.addEventListener('keydown', function(e){ if(e.key==='Escape') closeViewer(); });
      // attach click handlers for all images rendered by st.image (best-effort)
      setTimeout(()=>{
        // find imgs inside streamlit gallery area (heuristic)
        document.querySelectorAll('img').forEach(img=>{
          img.addEventListener('click', function(e){
            // skip if thumbnail already opens anything
            if (!this.src) return;
            openViewer(this.src);
          });
        });
      }, 600);
    </script>
    """ % (str(viewer_items).replace("\\\\","/"))

    st.markdown(viewer_html, unsafe_allow_html=True)


# ---------------- Premium Chatbot (fixed rendering & z-index) ----------------
chat_html = '''
<style>
#aryan-chat-float { position: fixed; right: 28px; bottom: 28px; z-index: 9999999; font-family: 'Sora', sans-serif; }
#aryan-chat-btn { width:72px; height:72px; border-radius:50%; border:none; cursor:pointer; background: linear-gradient(180deg,#ffeef8,#eaf6ff); box-shadow:0 20px 50px rgba(6,8,12,0.12); font-size:15px; font-weight:700; padding:8px; transition:transform .22s ease; }
#aryan-chat-btn:hover { transform: translateY(-6px); box-shadow:0 28px 70px rgba(6,8,12,0.16); }
#aryan-chat-box { position: fixed; right: 28px; bottom: 110px; width: 380px; max-width:92vw; display:none; z-index:10000000; border-radius:14px; overflow:hidden; box-shadow: 0 30px 90px rgba(6,8,12,0.28); background: linear-gradient(180deg,#071217,#0a0f12); color:#dff6ff; transform-origin: bottom right; transition: all 260ms cubic-bezier(.2,.9,.2,1); }
#aryan-chat-head { padding:10px 14px; display:flex; justify-content:space-between; align-items:center; font-weight:800; color:#bfefff; background:linear-gradient(90deg,#061014,#081218); }
#aryan-chat-body { max-height:300px; overflow:auto; padding:12px; background:linear-gradient(180deg,#071014,#071116); }
.chat-msg { margin:8px 0; padding:10px 12px; border-radius:10px; max-width:82%; white-space:pre-wrap; font-size:14px; }
.chat-user { background:white; color:#071018; margin-left:18%; }
.chat-bot { background:linear-gradient(90deg,#0f1720,#0b1114); color:#dff9ff; margin-right:18%; }
#aryan-chat-input-wrap { display:flex; gap:8px; padding:12px; background:#071014; }
#aryan-chat-input { flex:1; padding:10px; border-radius:8px; border:none; background:#0f1416; color:#dbefff; }
#aryan-chat-send { padding:10px 12px; border-radius:8px; border:none; background:linear-gradient(90deg,#ffd6eb,#dfe9ff); color:#14121a; font-weight:800; cursor:pointer; }
@media (max-width:480px){ #aryan-chat-box{ right:12px; left:12px; width:auto; bottom:90px } #aryan-chat-btn{ width:58px; height:58px; font-size:14px } }
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
    box.style.opacity = 0; box.style.transform = 'translateY(8px)';
    setTimeout(()=>{ box.style.display='none'; }, 260);
  }

  btn.addEventListener('click', ()=>{ if (box.style.display === 'block') closeBox(); else openBox(); });
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

# components.html is used with reasonable height so script runs reliably
components.html(chat_html, height=220, scrolling=False)


# ---------------- Footer ----------------
st.markdown("---")
st.markdown(f"<div style='text-align:center; opacity:0.78; padding:16px 0;'>© {time.strftime('%Y')} Aryan Sharma — Built with ☕</div>", unsafe_allow_html=True)
