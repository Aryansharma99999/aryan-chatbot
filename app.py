# app.py - Final premium portfolio + gallery + chatbot (ready to paste)
import os
import re
import json
import time
import base64
import streamlit as st
from markdown import markdown
import streamlit.components.v1 as components

# ---------------- Page config ----------------
st.set_page_config(page_title="Aryan Sharma", layout="wide", initial_sidebar_state="collapsed")

# ---------------- Paths ----------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
GALLERY_DIR = os.path.join(BASE_DIR, "gallery")
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")

os.makedirs(GALLERY_DIR, exist_ok=True)
os.makedirs(POSTS_DIR, exist_ok=True)

# ---------------- Helpers ----------------
def get_gallery_images():
    """Return list of image file paths inside gallery/ (jpg/png/webp etc)."""
    if not os.path.exists(GALLERY_DIR):
        return []
    files = [f for f in os.listdir(GALLERY_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
    files.sort()
    return [os.path.join("gallery", f) for f in files]  # return relative paths for Streamlit

def read_markdown_file(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()

def get_post_data(slug):
    file_path = os.path.join(POSTS_DIR, f"{slug}.md")
    if not os.path.exists(file_path):
        return None
    content = read_markdown_file(file_path)
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

# ---------------- Inline utility for small Data-URL fallback (rare) ----------------
def make_data_url(rel_path):
    try:
        real = os.path.join(BASE_DIR, rel_path)
        with open(real, "rb") as fh:
            data = base64.b64encode(fh.read()).decode("utf-8")
        ext = os.path.splitext(real)[1].lstrip(".").lower()
        if ext == "jpg": ext = "jpeg"
        return f"data:image/{ext};base64,{data}"
    except Exception:
        return ""

# ---------------- Prepare gallery list and hero preview images ----------------
images = get_gallery_images()  # relative paths like "gallery/filename.jpg"
# Choose hero previews as: first, second, third (user chose 1,2,3). If missing, fallback gracefully.
hero_preview = []
for i in range(3):
    if i < len(images):
        hero_preview.append(images[i])
    else:
        hero_preview.append("")  # empty string -> will hide that preview in hero JS

# For the gallery viewer thumbnails (we'll use the same images list)
viewer_items = images.copy()

# JSON encode viewer items safely for injecting into JS
viewer_items_json = json.dumps(viewer_items)  # safe serialization

# ---------------- HERO (components.html) ----------------
# Hero HTML/CSS/JS uses the three hero_preview images (relative paths) and typewriter/parallax.
# We use json.dumps to pass hero_preview list safely to the component and then assign sources in JS.

hero_component = f"""
<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700;800&display=swap" rel="stylesheet">
<style>
  :root{{--p1:#fbe9f9;--p2:#eaf6ff;--p3:#f7f0ff;--accent:#7b44e5}}
  html,body{{height:100%;margin:0;padding:0;background:transparent;font-family:'Inter',sans-serif}}
  .bg{{position:fixed;inset:0;z-index:0;background:linear-gradient(135deg,var(--p2),var(--p3),var(--p1));background-size:400% 400%;animation:bgMove 16s linear infinite}}
  @keyframes bgMove{{0%{{background-position:0% 50%}}50%{{background-position:100% 50%}}100%{{background-position:0% 50%}}}}
  .stage{{position:relative;z-index:2;min-height:76vh;display:flex;align-items:center;justify-content:center;padding:48px;box-sizing:border-box}}
  .card{{width:92%;max-width:1200px;border-radius:22px;padding:54px;background:rgba(255,255,255,0.78);box-shadow:0 30px 80px rgba(6,6,8,0.06);backdrop-filter:blur(12px)}}
  .card h3{{margin:0;color:#777;font-weight:600}} .card h1{{margin:6px 0 0 0;font-size:56px;font-weight:800;color:#16161a}}
  .lead{{margin-top:12px;color:#404345;font-size:18px;max-width:78%}}
  .role{{display:inline-block;margin-top:14px;padding:10px 16px;border-radius:999px;background:linear-gradient(90deg, rgba(123,68,229,0.12), rgba(123,68,229,0.06));color:var(--accent);font-weight:700}}
  .actions{{margin-top:22px;display:flex;gap:12px;align-items:center}}
  .btn{{padding:12px 18px;border-radius:999px;border:none;cursor:pointer;font-weight:700}}
  .btn.fill{{background:linear-gradient(90deg,#ffd6eb,#dfe9ff);color:#111}}
  .btn.ghost{{background:transparent;border:1px solid rgba(0,0,0,0.06);color:#333}}
  .previews{{position:absolute;right:36px;top:32px;display:flex;gap:12px}}
  .prev{{width:120px;height:120px;border-radius:12px;overflow:hidden;background:#fff;box-shadow:0 12px 36px rgba(6,6,8,0.08)}}
  .prev img{{width:100%;height:100%;object-fit:cover;display:block}}
  @media(max-width:980px){{.previews{{display:none}} .card h1{{font-size:36px}}}}
</style>
</head>
<body>
  <div class="bg"></div>
  <div class="stage">
    <div class="card" id="heroCard">
      <h3>Hello, I'm</h3>
      <h1>Aryan Sharma</h1>
      <p class="lead">I turn everyday life into little stories—coffee-powered, curious, and always building.</p>
      <div class="role" id="role">Creative Storyteller</div>
      <div class="actions">
        <button class="btn fill" onclick="location.href='#projects'">View Projects</button>
        <button class="btn ghost" onclick="location.href='#contact'">Contact</button>
      </div>
      <div class="previews" aria-hidden="true">
        <div class="prev"><img id="ph1" src="" alt="preview 1"/></div>
        <div class="prev"><img id="ph2" src="" alt="preview 2"/></div>
        <div class="prev"><img id="ph3" src="" alt="preview 3"/></div>
      </div>
    </div>
  </div>

<script>
  // Typewriter for role
  const roles = ["Creative Storyteller","Tech Enthusiast","AI Learner","Coffee-Powered Human ☕"];
  let ridx=0, rpos=0, rfor=true;
  const roleEl = document.getElementById('role');
  function typeTick(){
    const cur = roles[ridx];
    if(rfor){ rpos++; roleEl.textContent = cur.slice(0,rpos); if(rpos===cur.length){ rfor=false; setTimeout(typeTick,900); return; } }
    else { rpos--; roleEl.textContent = cur.slice(0,rpos); if(rpos===0){ rfor=true; ridx=(ridx+1)%roles.length; setTimeout(typeTick,400); return; } }
    setTimeout(typeTick,60);
  }
  typeTick();

  // Parallax
  const hero = document.getElementById('heroCard');
  document.addEventListener('mousemove', (e) => {
    const x = (window.innerWidth/2 - e.clientX) / 40;
    const y = (window.innerHeight/2 - e.clientY) / 40;
    hero.style.transform = `perspective(900px) rotateY(${x}deg) rotateX(${y}deg)`;
  });

  // assign hero preview images passed from Streamlit
  const previews = {json.dumps(hero_preview)};
  // set images if non-empty; otherwise hide the preview slot
  for(let i=0;i<3;i++){
    const el = document.getElementById('ph'+(i+1));
    if(previews[i] && previews[i].length>0){
      el.src = previews[i];
    } else {
      // hide parent preview container if no image
      el.parentElement.style.display = 'none';
    }
  }
</script>
</body>
</html>
"""

# Render hero
components.html(hero_component, height=760, scrolling=False)

# ---------------- Global streamlit css ----------------
st.markdown("""
<style>
.stApp { background: linear-gradient(180deg,#fbe9f9,#eaf6ff,#f7f0ff) !important; }
.stBlock, .css-1lcbmhc.e1fqkh3o3, .st-b1 { background: rgba(255,255,255,0.82) !important; border:1px solid rgba(255,255,255,0.7); box-shadow:0 12px 30px rgba(6,6,8,0.04); backdrop-filter: blur(8px); }
header[role="banner"] { display:none; } /* optional: hide default header */
</style>
""", unsafe_allow_html=True)

# ---------------- Gallery section (streamlit-rendered thumbnails + lightbox hook) ----------------
st.markdown("---")
st.markdown("<h2 style='margin-bottom:8px;'>📸 My Gallery</h2>", unsafe_allow_html=True)

if not images:
    st.info("No images found. Add JPG/PNG/WebP files to the `gallery/` folder in your repo.")
else:
    # Build a simple grid with 3 columns for thumbnails (Streamlit images)
    cols = st.columns(3)
    for idx, rel in enumerate(images):
        col = cols[idx % 3]
        caption = os.path.basename(rel)
        try:
            # display using relative path so deployed app serves the file
            with col:
                st.image(rel, caption=caption, use_column_width=True)
        except Exception:
            # fallback: if path serving fails, try to create data URL and show
            data_url = make_data_url(rel)
            if data_url:
                with col:
                    st.image(data_url, caption=caption, use_column_width=True)
            else:
                with col:
                    st.write("Unable to show", caption)

    # inject a viewer (lightbox) that opens any clicked image src (best-effort).
    viewer_js = f"""
    <div id="viewer" style="display:none; position:fixed; inset:0; z-index:99999; align-items:center; justify-content:center; background:rgba(0,0,0,0.75);">
      <div style="position:relative; max-width:92%; max-height:92%; display:flex; align-items:center; justify-content:center;">
        <img id="viewer-img" src="" style="max-width:100%; max-height:100%; border-radius:12px; box-shadow:0 30px 90px rgba(0,0,0,0.6);" />
        <button onclick="document.getElementById('viewer').style.display='none'" style="position:absolute; right:-12px; top:-12px; background:#fff; border-radius:999px; border:none; padding:8px 10px; cursor:pointer; font-weight:700;">✕</button>
      </div>
    </div>

    <script>
      (function(){
        // Attach click handlers to images on the page (heuristic)
        setTimeout(()=>{
          document.querySelectorAll('img').forEach(img=>{
            img.style.cursor = 'zoom-in';
            img.addEventListener('click', function(e){
              // avoid clicking small UI images (heuristic: skip if width < 80)
              try{
                const w = img.naturalWidth || img.width;
                if(w < 80) return;
              }catch(e){}
              const viewer = document.getElementById('viewer');
              document.getElementById('viewer-img').src = img.src;
              viewer.style.display = 'flex';
            });
          });
        }, 400);
        // close on escape
        document.addEventListener('keydown', function(e){ if(e.key==='Escape'){ const v=document.getElementById('viewer'); if(v) v.style.display='none'; } });
      })();
    </script>
    """
    st.markdown(viewer_js, unsafe_allow_html=True)

# ---------------- Writings / Projects ----------------
st.markdown("---")
st.header("✍️ Writings & Projects")
posts = get_all_posts()
if not posts:
    st.info("No posts yet. Add `.md` files to the `blog_posts/` folder.")
else:
    for p in posts:
        st.subheader(p["title"])
        if p.get("date"): st.caption(p["date"])
        st.markdown(p["html"], unsafe_allow_html=True)
        st.markdown("---")

st.markdown("<a id='projects'></a>", unsafe_allow_html=True)
st.markdown("### Projects")
st.write("- Chatbot Website\n- Portfolio Builder\n- AI Experiments")

# ---------------- Chatbot (components.html) ----------------
# Bubble text chosen by user: "Ask me about Aryan ☕"
chat_html = """
<div id="chat-root" style="position:fixed; right:22px; bottom:22px; z-index:1000000; font-family:Inter, sans-serif;">
  <button id="chat-btn" aria-label="Ask me about Aryan" style="width:72px;height:72px;border-radius:999px;border:none;background:linear-gradient(135deg,#ffd6f7,#e5dbff);box-shadow:0 12px 40px rgba(0,0,0,0.12);font-weight:800;cursor:pointer;">Ask me about Aryan ☕</button>

  <div id="chat-box" style="display:none; position:fixed; right:22px; bottom:110px; width:360px; max-width:calc(100% - 44px); border-radius:12px; overflow:hidden; box-shadow:0 30px 80px rgba(6,6,8,0.3);">
    <div style="background:linear-gradient(90deg,#061014,#081218); color:#bfefff; font-weight:800; padding:12px 14px;">Ask me about Aryan ☕</div>
    <div id="chat-body" style="padding:12px; max-height:300px; overflow:auto; background:#f5f7fb;"></div>
    <div style="display:flex; gap:8px; padding:10px; background:#f5f7fb;">
      <input id="chat-input" placeholder="Type a question..." style="flex:1; padding:10px; border-radius:8px; border:1px solid #ddd;">
      <button id="chat-send" style="padding:10px 12px; border-radius:8px; background:#7b44e5; color:#fff; border:none; font-weight:700;">Send</button>
    </div>
  </div>
</div>

<script>
(function(){
  const data = {
    "who is aryan":"Aryan is that guy who turns everyday moments into funny stories without even trying.",
    "what is aryan currently studying":"Pursuing a Bachelor's degree. 🎓",
    "what makes aryan smile":"Random jokes, good coffee, and accidental life plot twists.",
    "coffee":"Coffee ☕. Without it, Aryan is basically on airplane mode.",
    "does aryan like travelling":"Yes — especially when the trip ends with coffee and mountain views.",
    "what is aryan good at":"Turning simple moments into mini stories and making people laugh randomly."
  };

  const btn = document.getElementById('chat-btn');
  const box = document.getElementById('chat-box');
  const body = document.getElementById('chat-body');
  const input = document.getElementById('chat-input');
  const send = document.getElementById('chat-send');

  btn.addEventListener('click', ()=> {
    box.style.display = (box.style.display === 'block') ? 'none' : 'block';
    input.focus();
    if(!body.hasChildNodes()){
      addMsg("Hi! Ask me about Aryan ☕", "bot");
    }
  });

  function addMsg(text, who){
    const el = document.createElement('div');
    el.style.margin = '8px 0';
    el.style.padding = '10px 12px';
    el.style.borderRadius = '10px';
    el.style.maxWidth = '80%';
    el.style.fontSize = '14px';
    if(who === 'user'){
      el.style.background = '#dfe6ff';
      el.style.marginLeft = '20%';
      el.style.color = '#041022';
    } else {
      el.style.background = '#ffffff';
      el.style.color = '#061018';
    }
    el.textContent = text;
    body.appendChild(el);
    body.scrollTop = body.scrollHeight;
  }

  function reply(q){
    const t = q.toLowerCase();
    for(const k in data){
      if(t.includes(k)) return data[k];
    }
    if(t.includes('name')) return "Aryan Sharma — storyteller, coder, coffee-lover.";
    if(t.includes('study') || t.includes('studying')) return data["what is aryan currently studying"];
    if(t.includes('coffee')) return data["coffee"];
    return "Ask me anything about Aryan ☕🙂!";
  }

  function sendMsg(){
    const txt = input.value.trim();
    if(!txt) return;
    addMsg(txt, 'user');
    input.value = '';
    setTimeout(()=>{ addMsg(reply(txt), 'bot'); }, 300 + Math.random()*300);
  }

  send.addEventListener('click', sendMsg);
  input.addEventListener('keydown', function(e){
    if(e.key === 'Enter'){ e.preventDefault(); sendMsg(); }
  });

})();
</script>
"""

# render chatbot as component (height small but scripts run)
components.html(chat_html, height=1, scrolling=False)

# ---------------- Footer ----------------
st.markdown("---")
st.markdown("<a id='contact'></a>", unsafe_allow_html=True)
st.header("Contact")
st.write("Prefer DM on Instagram: ", "[aryanxsharma26](https://instagram.com/aryansharmax26)")

st.markdown(f"<div style='text-align:center; color:#666; padding:12px 0;'>© {time.strftime('%Y')} Aryan Sharma — Built with ☕</div>", unsafe_allow_html=True)

