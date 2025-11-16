# app.py  (Premium "Pinterest Soft Aesthetic" upgrade)
import os
import re
import time
import base64
import streamlit as st
from markdown import markdown
import streamlit.components.v1 as components

st.set_page_config(page_title="Aryan Sharma", layout="wide", initial_sidebar_state="collapsed")

# ---------- Helper: BLOG & GALLERY ----------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
GALLERY_DIR = os.path.join(BASE_DIR, "gallery")
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")


def get_gallery_images():
    if not os.path.exists(GALLERY_DIR):
        return []
    files = [f for f in os.listdir(GALLERY_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
    files.sort()
    return [os.path.join(GALLERY_DIR, f) for f in files]


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
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = content[meta_match.end():].strip()
    html = markdown(body)
    return {
        "slug": slug,
        "title": meta.get("title", slug.replace("-", " ").capitalize()),
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


# ---------- Soft / Pinterest-style Hero (components.html) ----------
# Pastel gradient blobs, frosted card, soft typewriter + parallax
hero_html = """
<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700;800&display=swap" rel="stylesheet">
<style>
  :root{
    --bg1: #fbe9f9;
    --bg2: #eaf6ff;
    --bg3: #f7f0ff;
    --accent: rgba(123, 68, 229, 0.9);
    --card-bg: rgba(255,255,255,0.65);
    --glass-border: rgba(255,255,255,0.7);
    --soft-shadow: 0 20px 50px rgba(21,24,30,0.06);
  }
  html,body{height:100%;margin:0;padding:0;font-family:'Inter',system-ui,Arial,sans-serif;background:transparent;}
  .canvas {
    position:fixed; inset:0; z-index:0; overflow:hidden;
    background: radial-gradient(circle at 10% 20%, #fff6ff 0%, transparent 15%),
                radial-gradient(circle at 90% 80%, #f0fbff 0%, transparent 18%),
                linear-gradient(180deg, var(--bg2) 0%, var(--bg3) 50%, var(--bg1) 100%);
  }
  /* soft blobs for depth */
  .blob {
    position:absolute; filter: blur(48px); opacity:0.85;
    transform: translate3d(0,0,0);
  }
  .b1{ width:520px; height:420px; left:-120px; top:-80px; background:linear-gradient(90deg,#ffdbe9,#eaf6ff);}
  .b2{ width:420px; height:360px; right:-100px; top:40px; background:linear-gradient(90deg,#f6ecff,#e7f8ff);}
  .b3{ width:360px; height:300px; left:10%; bottom:-80px; background:linear-gradient(90deg,#fff2ec,#f9f0ff);}

  /* centered page container */
  .page {
    position:relative; z-index:2; min-height:100vh; display:flex; align-items:center; justify-content:center;
    padding:48px; box-sizing:border-box;
  }

  .hero-card {
    width:86%; max-width:1100px; border-radius:20px; padding:44px; box-sizing:border-box;
    background: var(--card-bg);
    border: 1px solid var(--glass-border);
    box-shadow: var(--soft-shadow);
    backdrop-filter: blur(10px) saturate(120%);
    -webkit-backdrop-filter: blur(10px) saturate(120%);
    text-align:left; position:relative; overflow:hidden;
    transform-style: preserve-3d;
    transition: transform 0.12s ease-out;
  }

  .hero-left { display:flex; flex-direction:column; gap:12px; max-width:65%; }
  .hi { font-size:16px; color:#6b6f77; margin:0; font-weight:500; }
  .name { font-size:44px; margin:0; font-weight:800; color:#16161A; letter-spacing:-0.6px; }
  .desc { color:#4a4d52; margin-top:6px; font-size:18px; max-width:80%; }
  .typewrap { margin-top:14px; display:flex; gap:10px; align-items:center; font-weight:700; color:#6d6b7a; }
  .roles { color: #7b44e5; background: linear-gradient(90deg, rgba(123,68,229,0.12), rgba(123,68,229,0.06)); padding:8px 12px; border-radius:999px; box-shadow: 0 6px 20px rgba(123,68,229,0.04); }

  .hero-actions { margin-top:18px; display:flex; gap:12px; align-items:center; }
  .btn {
    padding:12px 18px; border-radius:999px; border:none; cursor:pointer; font-weight:700; font-size:15px;
    background: linear-gradient(90deg,#ffd6eb,#dfe9ff);
    color:#14121a; box-shadow: 0 8px 26px rgba(22,18,30,0.06);
  }
  .btn-ghost {
    padding:12px 18px; border-radius:999px; border:1px solid rgba(20,18,26,0.06);
    background:transparent; color:#4a4d52; font-weight:700;
  }

  /* right column - small preview cards */
  .hero-right { position:absolute; right:32px; top:32px; display:flex; gap:12px; align-items:center; transform: translateZ(40px); }
  .preview {
    width:120px; height:120px; border-radius:14px; overflow:hidden; background:linear-gradient(180deg, rgba(255,255,255,0.6), rgba(255,255,255,0.45));
    box-shadow: 0 10px 28px rgba(16,18,26,0.06); border:1px solid rgba(255,255,255,0.5);
  }
  .preview img { width:100%; height:100%; object-fit:cover; display:block; }

  /* responsive */
  @media (max-width:900px){
    .hero-card { padding:28px; }
    .hero-left { max-width:100%; }
    .name { font-size:34px; }
    .hero-right{ display:none; }
  }
</style>
</head>
<body>
  <div class="canvas">
    <div class="blob b1"></div>
    <div class="blob b2"></div>
    <div class="blob b3"></div>
  </div>

  <div class="page">
    <div class="hero-card" id="parallaxHero">
      <div style="display:flex; gap:28px; align-items:flex-start;">
        <div class="hero-left">
          <div class="hi">Hello, I'm</div>
          <h1 class="name">Aryan Sharma</h1>
          <div class="desc">I turn everyday life into little stories—coffee-powered, curious, and always building.</div>
          <div class="typewrap">I am a <span class="roles" id="typewriter">Tech Enthusiast</span></div>

          <div class="hero-actions">
            <button class="btn" onclick="location.href='#projects'">View Projects</button>
            <button class="btn-ghost" onclick="location.href='#contact'">Contact</button>
          </div>
        </div>

        <div class="hero-right" aria-hidden="true">
          <div class="preview"><img src="" id="p1"></div>
          <div class="preview"><img src="" id="p2"></div>
          <div class="preview"><img src="" id="p3"></div>
        </div>
      </div>
    </div>
  </div>

<script>
  // simple typewriter roles
  const roles = ["Tech Enthusiast","AI Learner","Creative Storyteller","Coffee-Powered Human ☕"];
  let ridx=0, rpos=0, rforward=true;
  const roleEl = document.getElementById('typewriter');
  function typeTick(){
    const cur = roles[ridx];
    if (rforward){
      rpos++;
      roleEl.textContent = cur.slice(0,rpos);
      if (rpos === cur.length){ rforward=false; setTimeout(typeTick,1100); return; }
    } else {
      rpos--;
      roleEl.textContent = cur.slice(0,rpos);
      if (rpos === 0){ rforward=true; ridx=(ridx+1)%roles.length; setTimeout(typeTick,400); return; }
    }
    setTimeout(typeTick,60);
  }
  typeTick();

  // parallax hero
  const hero = document.getElementById('parallaxHero');
  document.addEventListener('mousemove', (e) => {
    const x = (window.innerWidth / 2 - e.clientX) / 40;
    const y = (window.innerHeight / 2 - e.clientY) / 40;
    hero.style.transform = `perspective(900px) rotateY(${x}deg) rotateX(${y}deg)`;
  });

  // Placeholder images (filled by Streamlit below via JS injection)
  // Streamlit will replace these through innerHTML injection when component is loaded.
</script>
</body>
</html>
"""

# Render hero component
components.html(hero_html, height=760, scrolling=False)

# ---------- Global soft CSS for Streamlit area and premium cards ----------
st.markdown(
    """
    <style>
    /* match Streamlit background to the soft pastel look */
    .stApp {
        background: linear-gradient(180deg, rgba(234,246,255,0.95), rgba(247,240,255,0.96)) !important;
        color: #111;
    }
    /* Glassy card feel for streamlit blocks */
    .stBlock, .css-1lcbmhc.e1fqkh3o3, .st-b1 {
        background: rgba(255,255,255,0.7) !important;
        border: 1px solid rgba(255,255,255,0.6);
        box-shadow: 0 12px 30px rgba(12,12,18,0.04);
        backdrop-filter: blur(8px) !important;
    }
    /* headings */
    .css-10trblm.egzxvld1 { color:#18181b; }
    .stMarkdown { color:#222; }
    .stText { color:#222; }
    a { color: #7b44e5 !important; }
    /* tidy margins for images area */
    .gallery-grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap:18px; align-items:start; }
    .gallery-item { border-radius:14px; overflow:hidden; box-shadow: 0 10px 30px rgba(16,18,26,0.06); transition: transform .25s ease, box-shadow .25s ease; background: white;}
    .gallery-item img { width:100%; height:100%; object-fit:cover; display:block; transition: transform .45s ease; }
    .gallery-item:hover { transform: translateY(-8px); box-shadow: 0 20px 60px rgba(16,18,26,0.09); }
    .gallery-item:hover img { transform: scale(1.06); }
    </style>
    """, unsafe_allow_html=True
)

# ---------- Gallery: create an HTML masonry-style grid with lightbox (images base64-embedded) ----------
images = get_gallery_images()

def make_base64(img_path):
    try:
        with open(img_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
            ext = os.path.splitext(img_path)[1].lower().replace('.', '')
            return f"data:image/{ext};base64,{data}"
    except Exception as e:
        return None

if images:
    # Build HTML gallery
    gallery_items = []
    for p in images:
        b64 = make_base64(p)
        if not b64:
            continue
        # short filename for caption
        name = os.path.basename(p)
        item_html = f"""
        <div class="gallery-item">
          <img src="{b64}" alt="{name}" loading="lazy" onclick="openLightbox(this.src, '{name}')"/>
        </div>
        """
        gallery_items.append(item_html)

    gallery_html = f"""
    <div style="padding:18px 6px;">
      <h2 style="margin:6px 0 14px 6px; color:#2b2b2f;">My Gallery</h2>
      <div class="gallery-grid">
        {''.join(gallery_items)}
      </div>
    </div>

    <!-- Lightbox modal -->
    <div id="ps-lightbox" style="display:none; position:fixed; inset:0; z-index:9999; align-items:center; justify-content:center; background: rgba(8,10,14,0.6);">
      <div style="position:relative; max-width:92%; max-height:92%; display:flex; align-items:center; justify-content:center;">
        <img id="pslb-img" src="" style="max-width:100%; max-height:100%; border-radius:12px; box-shadow: 0 30px 80px rgba(0,0,0,0.6);" />
        <button onclick="closeLightbox()" style="position:absolute; right:-8px; top:-8px; background:#fff; border-radius:999px; border:none; padding:8px 10px; cursor:pointer; font-weight:700;">✕</button>
      </div>
    </div>

    <script>
      function openLightbox(src, name){
        const lb = document.getElementById('ps-lightbox');
        const img = document.getElementById('pslb-img');
        img.src = src;
        lb.style.display = 'flex';
      }
      function closeLightbox(){
        const lb = document.getElementById('ps-lightbox');
        lb.style.display = 'none';
      }
      // close on esc
      document.addEventListener('keydown', function(e){
        if (e.key === 'Escape') closeLightbox();
      });
    </script>
    """

    st.markdown(gallery_html, unsafe_allow_html=True)
else:
    st.info("No gallery images found. Add images to the `gallery/` folder (jpg, png, webp).")

# ---------- Right Column: Blog & Writings (keeps previous functionality) ----------
st.markdown("---")
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 📸 Photos (Gallery)")
    if not images:
        st.info("No images found. Add files to the `gallery/` folder.")
    else:
        # Show a compact preview strip (small thumbnails)
        for i, img in enumerate(images):
            st.image(img, width=200, caption=os.path.basename(img))
            if i >= 3:
                break
        if len(images) > 4:
            st.caption(f"Plus {len(images)-4} more — click 'My Gallery' to view them all.")

with col2:
    st.markdown("### ✍️ Writings")
    posts = get_all_posts()
    if not posts:
        st.info("No blog posts found. Add `.md` files to `blog_posts/`.")
    else:
        for p in posts:
            st.subheader(p["title"])
            st.caption(p.get("date", ""))
            st.markdown(p["html"], unsafe_allow_html=True)
            st.markdown("---")

# ---------- Client-side chat (unchanged concept — messages are local to the user's page) ----------
st.markdown("---")
st.info("Chat is available via the floating 💬 bubble (bottom-right). The chat runs client-side and does not store messages on the server.")

# Embed a small client-side chat bubble & script (re-using your Q&A)
chat_js = """
<div id="ps-chat" style="position:fixed; right:22px; bottom:22px; z-index:9998;">
  <button id="ps-chat-btn" style="width:62px;height:62px;border-radius:999px;border:none;background:linear-gradient(180deg,#f7e8ff,#eaf6ff);box-shadow:0 12px 30px rgba(16,18,26,0.07);cursor:pointer;font-size:22px;">💬</button>
  <div id="ps-chat-popup" style="display:none; position:fixed; right:22px; bottom:96px; width:360px; max-width:92vw; z-index:9999;">
    <div style="background:linear-gradient(180deg, #0b0e12, #0e1114); color:#fff; border-radius:12px; box-shadow:0 30px 80px rgba(7,8,10,0.6); overflow:hidden;">
      <div style="padding:8px 12px; display:flex; justify-content:space-between; align-items:center;">
        <div style="font-weight:800; color:#cfefff;">Ask about Aryan ☕</div>
        <button onclick="psCloseChat()" style="background:transparent;border:none;color:#cfefff; font-weight:700; cursor:pointer;">✕</button>
      </div>
      <div id="psChatMessages" style="padding:8px; max-height:260px; overflow:auto; background:linear-gradient(180deg,#08090b,#0b0d10);"></div>
      <div style="display:flex; gap:8px; padding:10px; background:#071014;">
        <input id="psChatInput" placeholder="Type a question..." style="flex:1; padding:10px; border-radius:8px; border:none; background:#0f1416; color:#dbefff;" />
        <button id="psSendBtn" style="padding:10px 12px; border-radius:8px; border:none; background:#7b44e5; color:#fff; font-weight:700; cursor:pointer;">Send</button>
      </div>
    </div>
  </div>
</div>

<script>
  const aryanFacts = {
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
  };

  const btn = document.getElementById('ps-chat-btn');
  const popup = document.getElementById('ps-chat-popup');
  const messagesWrap = document.getElementById('psChatMessages');
  const input = document.getElementById('psChatInput');
  const sendBtn = document.getElementById('psSendBtn');

  btn.addEventListener('click', () => {
    popup.style.display = (popup.style.display === 'flex' || popup.style.display === 'block') ? 'none' : 'block';
    input.focus();
    if (!messagesWrap.hasChildNodes()) {
      addMessage("Hi! Ask me about Aryan ☕", 'bot');
    }
  });

  function addMessage(text, who='bot'){
    const el = document.createElement('div');
    el.style.margin = '6px 0';
    el.style.padding = '8px 10px';
    el.style.borderRadius = '9px';
    el.style.maxWidth = '86%';
    el.style.clear = 'both';
    el.style.fontSize = '14px';
    if (who === 'user'){ el.style.background = 'linear-gradient(90deg,#fff,#fff)'; el.style.color='#061018'; el.style.marginLeft='18%'; } 
    else { el.style.background = 'linear-gradient(90deg,#0f1720,#0b1114)'; el.style.color='#dff9ff'; el.style.marginRight='18%'; }
    el.textContent = text;
    messagesWrap.appendChild(el);
    messagesWrap.scrollTop = messagesWrap.scrollHeight;
  }

  function replyTo(text){
    const q = text.toLowerCase().trim();
    for (const k in aryanFacts){
      if (q.includes(k)) return aryanFacts[k];
    }
    if (q.includes('name')) return "Aryan is Aryan Sharma — a storyteller who loves coffee and code.";
    if (q.includes('study') || q.includes('studying')) return aryanFacts["what is aryan currently studying"];
    if (q.includes('coffee')) return aryanFacts["what’s aryan’s comfort drink"];
    return "Ask me anything about Aryan ☕🙂!";
  }

  function handleSend(){
    const txt = input.value.trim();
    if (!txt) return;
    addMessage(txt, 'user');
    input.value = '';
    setTimeout(() => {
      const r = replyTo(txt);
      addMessage(r, 'bot');
    }, 350 + Math.random()*300);
  }

  sendBtn.addEventListener('click', handleSend);
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') { e.preventDefault(); handleSend(); }
  });

  function psCloseChat(){ popup.style.display='none'; }
</script>
"""
components.html(chat_js, height=1, scrolling=False)  # height small; main UI is in page

# ---------- Footer / Projects / Contact placeholders ----------
st.markdown("---")
st.markdown("<a id='projects'></a>", unsafe_allow_html=True)
st.header("Projects")
st.markdown("""
- Chatbot Website  
- Portfolio Builder  
- AI Experiments  
(Projects area — add details or use markdown posts.)
""")

st.markdown("<a id='contact'></a>", unsafe_allow_html=True)
st.header("Contact")
st.write("Prefer DM on Instagram: ", "[aryanxsharma26](https://instagram.com/aryansharmax26)")

# ---------- End ----------
