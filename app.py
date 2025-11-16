# app.py  (Final premium "Pinterest Soft Aesthetic" - Layout C3, Chat style A, Font: Sora)
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


# ---------- Hero component (Sora font) ----------
# Use triple-single-quote to avoid conflicts with quotes inside HTML/JS.
hero_html = '''
<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800&display=swap" rel="stylesheet">
<style>
  :root{
    --p1: #fbe9f9;
    --p2: #eaf6ff;
    --p3: #f7f0ff;
    --accent: rgba(123, 68, 229, 0.95);
    --card: rgba(255,255,255,0.68);
    --glass-border: rgba(255,255,255,0.72);
  }
  html,body{height:100%;margin:0;padding:0;font-family:'Sora',system-ui,Arial,sans-serif;background:transparent;}
  .canvas{
    position:fixed; inset:0; z-index:0; overflow:hidden;
    background:
      radial-gradient(circle at 8% 20%, rgba(255,245,255,1) 0%, transparent 12%),
      radial-gradient(circle at 92% 80%, rgba(235,248,255,1) 0%, transparent 14%),
      linear-gradient(180deg, var(--p2) 0%, var(--p3) 50%, var(--p1) 100%);
    background-size: cover;
  }
  .blob{ position:absolute; filter:blur(48px); opacity:.9; transform:translate3d(0,0,0); }
  .b1{ width:520px;height:420px; left:-120px; top:-80px; background:linear-gradient(90deg,#ffdbe9,#eaf6ff); }
  .b2{ width:420px;height:360px; right:-100px; top:40px; background:linear-gradient(90deg,#f6ecff,#e7f8ff); }
  .b3{ width:360px;height:300px; left:10%; bottom:-80px; background:linear-gradient(90deg,#fff2ec,#f9f0ff); }

  .page{ position:relative; z-index:2; min-height:66vh; display:flex; align-items:center; justify-content:center; padding:48px; box-sizing:border-box; }

  .hero-card{
    width:88%; max-width:1100px; border-radius:18px; padding:44px; box-sizing:border-box;
    background: var(--card); border:1px solid var(--glass-border);
    box-shadow: 0 20px 50px rgba(16,18,24,0.06); backdrop-filter: blur(10px) saturate(120%);
    -webkit-backdrop-filter: blur(10px) saturate(120%);
    text-align:left; position:relative; overflow:hidden;
    transform-style: preserve-3d; transition: transform 0.12s ease-out;
  }

  .hero-left{ display:flex; flex-direction:column; gap:12px; max-width:68%; }
  .hi{ font-size:15px; color:#6b6f77; margin:0; font-weight:600; }
  .name{ font-size:48px; margin:0; font-weight:800; color:#121218; letter-spacing:-0.6px; }
  .desc{ color:#44464a; margin-top:6px; font-size:18px; max-width:86%; }
  .typewrap{ margin-top:12px; display:flex; gap:10px; align-items:center; font-weight:700; color:#6d6b7a; }
  .roles{ color:var(--accent); background: linear-gradient(90deg, rgba(123,68,229,0.12), rgba(123,68,229,0.06)); padding:8px 12px; border-radius:999px; box-shadow:0 6px 20px rgba(123,68,229,0.04); }

  .hero-actions{ margin-top:18px; display:flex; gap:12px; align-items:center; }
  .btn{ padding:12px 18px; border-radius:999px; border:none; cursor:pointer; font-weight:700; font-size:15px; background: linear-gradient(90deg,#ffd6eb,#dfe9ff); color:#14121a; box-shadow: 0 8px 26px rgba(22,18,30,0.06); }
  .btn-ghost{ padding:12px 18px; border-radius:999px; border:1px solid rgba(20,18,26,0.06); background:transparent; color:#4a4d52; font-weight:700; }

  .hero-right{ position:absolute; right:28px; top:28px; display:flex; gap:12px; align-items:center; transform: translateZ(40px); }
  .preview{ width:110px; height:110px; border-radius:14px; overflow:hidden; background:linear-gradient(180deg, rgba(255,255,255,0.6), rgba(255,255,255,0.45)); box-shadow:0 10px 28px rgba(16,18,26,0.06); border:1px solid rgba(255,255,255,0.5); }
  .preview img{ width:100%; height:100%; object-fit:cover; display:block; }

  @media (max-width:920px){
    .hero-card{ padding:28px; }
    .name{ font-size:34px; }
    .hero-right{ display:none; }
    .page{ padding:28px; }
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
  // typewriter roles
  const roles = ["Tech Enthusiast","AI Learner","Creative Storyteller","Coffee-Powered Human ☕"];
  let ridx = 0, rpos = 0, rforward = true;
  const roleEl = document.getElementById("typewriter");
  function typeTick(){
    const cur = roles[ridx];
    if (rforward){
      rpos++;
      roleEl.textContent = cur.slice(0,rpos);
      if (rpos === cur.length){ rforward = false; setTimeout(typeTick,1000); return; }
    } else {
      rpos--;
      roleEl.textContent = cur.slice(0,rpos);
      if (rpos === 0){ rforward = true; ridx = (ridx+1)%roles.length; setTimeout(typeTick,400); return; }
    }
    setTimeout(typeTick,60);
  }
  typeTick();

  // parallax hero
  const hero = document.getElementById("parallaxHero");
  document.addEventListener("mousemove", (e) => {
    const x = (window.innerWidth / 2 - e.clientX) / 40;
    const y = (window.innerHeight / 2 - e.clientY) / 40;
    hero.style.transform = `perspective(900px) rotateY(${x}deg) rotateX(${y}deg)`;
  });

  // placeholder images (will be populated by Streamlit if available)
</script>
</body>
</html>
'''

# Render hero component (tall so it fills top)
components.html(hero_html, height=760, scrolling=False)


# ---------- Global Streamlit CSS (pastel glass) ----------
st.markdown('''
<style>
/* global app background */
.stApp {
  background: linear-gradient(180deg, rgba(234,246,255,0.95), rgba(247,240,255,0.96)) !important;
  color: #111;
}

/* glass card feel for Streamlit blocks */
.stBlock, .css-1lcbmhc.e1fqkh3o3, .st-b1 {
  background: rgba(255,255,255,0.74) !important;
  border: 1px solid rgba(255,255,255,0.65);
  box-shadow: 0 12px 30px rgba(12,12,18,0.04);
  backdrop-filter: blur(8px) !important;
}

/* headings */
.css-10trblm.egzxvld1 { color:#18181b; }
.stMarkdown { color:#222; }
.stText { color:#222; }
a { color: #7b44e5 !important; }

/* gallery grid CSS for injected HTML */
.gallery-grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap:18px; align-items:start; }
.gallery-item { border-radius:14px; overflow:hidden; box-shadow: 0 10px 30px rgba(16,18,26,0.06); transition: transform .25s ease, box-shadow .25s ease; background: white;}
.gallery-item img { width:100%; height:100%; object-fit:cover; display:block; transition: transform .45s ease; }
.gallery-item:hover { transform: translateY(-8px); box-shadow: 0 20px 60px rgba(16,18,26,0.09); }
.gallery-item:hover img { transform: scale(1.06); }
</style>
''', unsafe_allow_html=True)


# ---------- Blog / Projects area ----------
st.markdown("---")
st.header("Writings & Projects")
st.markdown("## ✍️ Latest Writings")
posts = get_all_posts()
if not posts:
    st.info("No blog posts found. Add `.md` files to `blog_posts/`.")
else:
    for p in posts:
        st.subheader(p["title"])
        if p.get("date"):
            st.caption(p["date"])
        st.markdown(p["html"], unsafe_allow_html=True)
        st.markdown("---")

st.markdown("## 🛠 Projects")
st.markdown("""
- Chatbot Website  
- Portfolio Builder  
- AI Experiments  
(Add project details or link to GitHub repos.)
""")

st.markdown("<a id='contact'></a>", unsafe_allow_html=True)
st.header("Contact")
st.write("Prefer DM on Instagram: ", "[aryanxsharma26](https://instagram.com/aryansharmax26)")


# ---------- Client-side Soft Pastel Chat (Style A) ----------
# We'll inject a compact HTML+JS component for a soft pastel bubble and smooth fade+slide popup.
chat_html = '''
<div id="ps-chat" style="position:fixed; right:22px; bottom:22px; z-index:9998; font-family: 'Sora', sans-serif;">
  <button id="ps-chat-btn" aria-label="Ask me about Aryan" title="Ask me about Aryan"
          style="width:64px;height:64px;border-radius:999px;border:none;background:linear-gradient(180deg,#ffe9f4,#eaf6ff);box-shadow:0 12px 30px rgba(16,18,26,0.07);cursor:pointer;font-size:18px;font-weight:700;color:#171717;">
    Ask me about Aryan ☕
  </button>

  <div id="ps-chat-popup" style="display:none; position:fixed; right:22px; bottom:96px; width:360px; max-width:92vw; z-index:9999;">
    <div id="ps-chat-card" style="opacity:0; transform: translateY(10px); transition: all 260ms cubic-bezier(.2,.9,.2,1); background: linear-gradient(180deg,#071217, #0a0f12); color:#e6f7ff; border-radius:12px; box-shadow:0 30px 70px rgba(7,9,12,0.6); overflow:hidden;">
      <div style="padding:10px 12px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255,255,255,0.02);">
        <div style="font-weight:800; color:#cfefff;">Ask me about Aryan ☕</div>
        <button id="ps-close" style="background:transparent;border:none;color:#cfefff; font-weight:700; cursor:pointer;">✕</button>
      </div>

      <div id="psMessages" style="padding:10px; max-height:260px; overflow:auto; background: linear-gradient(180deg,#071014,#071116);"></div>

      <div style="display:flex; gap:8px; padding:10px; background:#071014;">
        <input id="psInput" placeholder="Type a question..." style="flex:1; padding:10px; border-radius:8px; border:none; background:#0f1416; color:#dbefff;" />
        <button id="psSend" style="padding:10px 12px; border-radius:8px; border:none; background:linear-gradient(90deg,#ffd6eb,#dfe9ff); color:#14121a; font-weight:800; cursor:pointer;">Send</button>
      </div>
    </div>
  </div>
</div>

<script>
  (function(){
    const facts = {
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
      "what is aryan learning right now": "New tech skills… one coffee at a time."
    };

    const btn = document.getElementById("ps-chat-btn");
    const popupWrap = document.getElementById("ps-chat-popup");
    const card = document.getElementById("ps-chat-card");
    const closeBtn = document.getElementById("ps-close");
    const messages = document.getElementById("psMessages");
    const input = document.getElementById("psInput");
    const send = document.getElementById("psSend");

    function addMessage(text, who){
      const el = document.createElement("div");
      el.style.margin = "8px 0";
      el.style.padding = "8px 10px";
      el.style.borderRadius = "10px";
      el.style.maxWidth = "86%";
      el.style.fontSize = "14px";
      if (who === "user"){
        el.style.background = "#fff";
        el.style.color = "#071018";
        el.style.marginLeft = "12%";
      } else {
        el.style.background = "linear-gradient(90deg,#0f1720,#0b1114)";
        el.style.color = "#dff9ff";
        el.style.marginRight = "12%";
      }
      el.textContent = text;
      messages.appendChild(el);
      messages.scrollTop = messages.scrollHeight;
    }

    function replyTo(q){
      const text = q.toLowerCase().trim();
      for (let k in facts){
        if (text.includes(k)) return facts[k];
      }
      if (text.includes("name")) return "Aryan is Aryan Sharma — a storyteller who loves coffee and code.";
      if (text.includes("study") || text.includes("studying")) return facts["what is aryan currently studying"];
      if (text.includes("coffee")) return facts["what’s aryan’s comfort drink"];
      return "Ask me anything about Aryan ☕🙂!";
    }

    function openPopup(){
      popupWrap.style.display = "block";
      // animate card: fade + slide up
      requestAnimationFrame(() => {
        card.style.opacity = "1";
        card.style.transform = "translateY(0)";
      });
      input.focus();
      if (!messages.hasChildNodes()){
        addMessage("Hi! Ask me about Aryan ☕", "bot");
      }
    }

    function closePopup(){
      card.style.opacity = "0";
      card.style.transform = "translateY(10px)";
      setTimeout(()=>{ popupWrap.style.display = "none"; }, 260);
    }

    btn.addEventListener("click", () => {
      if (popupWrap.style.display === "block"){
        closePopup();
      } else {
        openPopup();
      }
    });
    closeBtn.addEventListener("click", closePopup);

    function sendMessage(){
      const txt = input.value.trim();
      if (!txt) return;
      addMessage(txt, "user");
      input.value = "";
      setTimeout(()=> {
        const r = replyTo(txt);
        addMessage(r, "bot");
      }, 300 + Math.random()*300);
    }

    send.addEventListener("click", sendMessage);
    input.addEventListener("keydown", function(e){ if (e.key === "Enter"){ e.preventDefault(); sendMessage(); }});

  })();
</script>
'''
components.html(chat_html, height=1, scrolling=False)


# ---------- Gallery at the very bottom (C3) ----------
images = get_gallery_images()

def make_base64(img_path):
    try:
        with open(img_path, "rb") as fh:
            data = base64.b64encode(fh.read()).decode("utf-8")
            ext = os.path.splitext(img_path)[1].lower().replace('.', '')
            return f"data:image/{ext};base64,{data}"
    except Exception:
        return None

st.markdown("---")
st.markdown("<a id='gallery'></a>", unsafe_allow_html=True)
st.header("Gallery")
if not images:
    st.info("No gallery images found. Add images to the `gallery/` folder (jpg, png, webp).")
else:
    # build gallery items
    gallery_items = []
    for p in images:
        b64 = make_base64(p)
        if not b64:
            continue
        name = os.path.basename(p)
        # use single quotes inside to be safe
        item_html = f"""
        <div class='gallery-item'>
          <img src="{b64}" alt="{name}" loading="lazy" onclick="openLightbox(this.src)" />
        </div>
        """
        gallery_items.append(item_html)

    gallery_html = """
    <div style='padding:18px 6px;'>
      <div style='display:flex; align-items:center; justify-content:space-between; gap:12px;'>
        <h2 style='margin:6px 0 14px 6px; color:#2b2b2f;'>Photographs</h2>
        <div style='color:#6b6f77; font-weight:600; font-size:14px;'>Click an image to view</div>
      </div>

      <div class='gallery-grid'>
    """ + "".join(gallery_items) + """
      </div>
    </div>

    <!-- Lightbox -->
    <div id='ps-lightbox' style='display:none; position:fixed; inset:0; z-index:9999; align-items:center; justify-content:center; background: rgba(8,10,14,0.6);'>
      <div style='position:relative; max-width:92%; max-height:92%; display:flex; align-items:center; justify-content:center;'>
        <img id='pslb-img' src='' style='max-width:100%; max-height:100%; border-radius:12px; box-shadow: 0 30px 80px rgba(0,0,0,0.6);' />
        <button onclick='closeLightbox()' style='position:absolute; right:-8px; top:-8px; background:#fff; border-radius:999px; border:none; padding:8px 10px; cursor:pointer; font-weight:700;'>✕</button>
      </div>
    </div>

    <script>
      function openLightbox(src){
        const lb = document.getElementById('ps-lightbox');
        const img = document.getElementById('pslb-img');
        img.src = src;
        lb.style.display = 'flex';
        // fade in
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


# ---------- Footer ----------
st.markdown("---")
st.write("© " + time.strftime("%Y") + " Aryan Sharma — Built with ❤️")
