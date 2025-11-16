# app.py
import os
import re
import time
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


# ---------- Chatbot knowledge (kept here for reference / future server-side use) ----------
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

# ---------- Full-screen themed hero + popup chat (rendered via components.html) ----------
# This hero_html contains:
#  - animated gradient background
#  - typewriter role line
#  - neon/glass hero wrap
#  - floating chat bubble with client-side JS (no server storage)
hero_html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap" rel="stylesheet">
<style>
  :root{
    --bg1:#ff6fb5;
    --bg2:#845ef7;
    --bg3:#7ad3ff;
  }
  html,body{height:100%;margin:0;padding:0;font-family:'Poppins',sans-serif;overflow-x:hidden;background:transparent;}
  /* animated gradient background */
  .page-bg{
    position:fixed; inset:0; z-index:0;
    background: linear-gradient(135deg, var(--bg1) 0%, var(--bg2) 50%, var(--bg3) 100%);
    background-size: 400% 400%;
    animation: gradientFlow 12s ease infinite;
    filter: saturate(1.05);
  }
  @keyframes gradientFlow {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }

  /* subtle starfield for depth */
  .stars {
    position:fixed; inset:0; z-index:1; pointer-events:none;
    background-image: radial-gradient(rgba(255,255,255,0.85) 1px, transparent 1px);
    background-size: 6px 6px; opacity: .10;
    animation: twinkle 6s linear infinite;
  }
  @keyframes twinkle{
    0%{opacity:.10}
    50%{opacity:.06}
    100%{opacity:.10}
  }

  /* hero container */
  .page {
    position:relative; z-index:2; min-height:100vh; display:flex; align-items:center; justify-content:center;
    padding:40px; box-sizing:border-box;
  }
  .hero-wrap{
    width:86%; max-width:1100px; border-radius:24px; padding:48px; box-sizing:border-box;
    backdrop-filter: blur(10px) saturate(120%);
    -webkit-backdrop-filter: blur(10px) saturate(120%);
    background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));
    box-shadow: 0 20px 50px rgba(10,10,20,0.45), inset 0 1px 0 rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.04);
    text-align:center;
    transform-style: preserve-3d;
    transition: transform 0.12s ease-out;
    position: relative;
  }
  .hero-title{ margin:0; font-size:48px; font-weight:800;
    background:linear-gradient(90deg,var(--bg1),var(--bg2)); -webkit-background-clip:text; color:transparent;
  }
  .hero-sub{ margin-top:10px; color:#e6f7ff; font-size:18px; opacity:.95; }
  .typewrap{ text-align:center; margin-top:14px; color:#cde8ff; font-weight:600; }
  .roles { color:#ffd3f0; font-weight:700; font-size:18px; height:26px; display:inline-block; margin-left:6px; }

  .cta-row{ display:flex; gap:14px; justify-content:center; margin-top:22px; }
  .btn {
    padding:12px 20px; border-radius:999px; border:none; cursor:pointer; font-weight:700; font-size:15px;
    background:linear-gradient(90deg,var(--bg1),var(--bg2)); color:#041622; box-shadow: 0 6px 18px rgba(0,0,0,0.25);
  }
  .btn-outline {
    padding:12px 20px; border-radius:999px; border:1px solid rgba(255,255,255,0.08);
    background:transparent; color:#d7d7ff; font-weight:700;
  }

  /* floating bubble (bottom-right) */
  .chat-bubble {
    position:fixed; right:26px; bottom:26px; z-index:6;
    width:64px; height:64px; border-radius:999px; display:flex; align-items:center; justify-content:center;
    background:linear-gradient(180deg,var(--bg2),var(--bg1));
    box-shadow: 0 12px 40px rgba(10,10,20,0.45);
    color:white; font-size:26px; cursor:pointer; transition: transform .18s ease;
  }
  .chat-bubble:hover{ transform: translateY(-6px); }

  /* popup chat window (client-side only; DOES NOT store messages server-side) */
  .chat-popup {
    position:fixed; right:26px; bottom:100px; z-index:7; width:380px; max-width:92vw;
    border-radius:14px; overflow:hidden; box-shadow: 0 30px 80px rgba(10,10,20,0.6);
    display:none;
    transform-origin: bottom right;
  }
  .chat-card {
    background: linear-gradient(180deg, rgba(8,10,14,0.98), rgba(12,14,18,0.95));
    color:#fff;
    padding:12px; box-sizing:border-box;
  }
  .chat-header{ display:flex; justify-content:space-between; align-items:center; padding:6px 8px; }
  .chat-title { color:#6ef0ff; font-weight:800; font-size:15px; }
  .chat-close { background:transparent; border:none; color:#b9dff7; font-size:18px; cursor:pointer; }
  .chat-messages { max-height:320px; overflow:auto; padding:8px; margin-top:8px; }
  .msg { margin:8px 0; padding:10px 12px; border-radius:12px; display:inline-block; clear:both; max-width:85%; }
  .msg.user { background: linear-gradient(90deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03)); float:right; color:#fff; }
  .msg.bot { background: linear-gradient(90deg, rgba(120,120,255,0.06), rgba(120,120,255,0.02)); float:left; color:#fff; }
  .chat-input-row { display:flex; gap:8px; margin-top:10px; }
  .chat-input { flex:1; padding:10px; border-radius:10px; border:none; background:#0f1113; color:#e6eef8; }
  .chat-send { padding:10px 12px; border-radius:10px; border:none; background:linear-gradient(90deg,var(--bg1),var(--bg2)); color:#041622; cursor:pointer; font-weight:700; }

  @media (max-width:800px){
    .hero-title{ font-size:32px; }
    .chat-popup { right:12px; left:12px; bottom:90px; width:calc(100% - 24px); }
    .chat-bubble { right:12px; bottom:12px; }
  }
</style>
</head>
<body>
  <div class="page-bg"></div>
  <div class="stars"></div>

  <div class="page">
    <div class="hero-wrap" id="parallaxHero" role="main" aria-label="hero">
      <h1 class="hero-title">Aryan Sharma</h1>
      <div class="hero-sub">Welcome to my personal website!</div>
      <div class="typewrap">I'm a <span class="roles" id="role">tech enthusiast</span></div>
      <div class="cta-row">
        <button class="btn" onclick="location.href='#projects'">Download Resume</button>
        <button class="btn-outline" onclick="location.href='#contact'">Get In Touch</button>
      </div>
    </div>
  </div>

  <!-- floating chat bubble -->
  <div class="chat-bubble" id="chatBubble" title="Ask me about Aryan">💬</div>

  <!-- popup chat (client-side only) -->
  <div class="chat-popup" id="chatPopup" role="dialog" aria-modal="true" aria-label="Aryan chatbot popup">
    <div class="chat-card">
      <div class="chat-header">
        <div class="chat-title">Ask me about Aryan ☕</div>
        <div>
          <button class="chat-close" id="minimizeBtn" title="Minimize">—</button>
          <button class="chat-close" id="closeBtn" title="Close">✕</button>
        </div>
      </div>
      <div class="chat-messages" id="chatMessages" aria-live="polite"></div>
      <div class="chat-input-row">
        <input type="text" id="chatInput" class="chat-input" placeholder="Type a question (e.g. Who is Aryan?)" />
        <button id="sendBtn" class="chat-send">Send</button>
      </div>
    </div>
  </div>

<script>
  // client-side copy of Aryan Q&A (no server storage; messages exist only in the user's page session)
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

  // UI elements
  const bubble = document.getElementById('chatBubble');
  const popup = document.getElementById('chatPopup');
  const messages = document.getElementById('chatMessages');
  const input = document.getElementById('chatInput');
  const sendBtn = document.getElementById('sendBtn');
  const closeBtn = document.getElementById('closeBtn');
  const minimizeBtn = document.getElementById('minimizeBtn');
  const hero = document.getElementById('parallaxHero');

  function addMessage(text, who='bot'){
    const el = document.createElement('div');
    el.className = 'msg ' + (who === 'user' ? 'user' : 'bot');
    el.textContent = text;
    messages.appendChild(el);
    messages.scrollTop = messages.scrollHeight;
  }

  function replyTo(text){
    const q = text.toLowerCase().trim();
    // exact matching by presence of key words:
    for (const k in aryanFacts){
      if (q.includes(k)) {
        return aryanFacts[k];
      }
    }
    // fallback simple keyword heuristics
    if (q.includes('name')) return "Aryan is Aryan Sharma — that guy who turns everyday moments into funny stories.";
    if (q.includes('study') || q.includes('studying')) return aryanFacts["what is aryan currently studying"];
    if (q.includes('coffee')) return aryanFacts["what’s aryan’s comfort drink"];
    if (q.includes('travel')) return aryanFacts["does aryan like travelling"];
    // default fallback
    return "Ask me anything about Aryan ☕🙂!";
  }

  bubble.addEventListener('click', () => {
    popup.style.display = 'block';
    input.focus();
    if (!messages.hasChildNodes()){
      addMessage("Hi! I'm Aryan's assistant — ask me anything about Aryan ☕", 'bot');
    }
  });

  closeBtn.addEventListener('click', () => { popup.style.display = 'none'; });
  minimizeBtn.addEventListener('click', () => { popup.style.display = 'none'; });

  function handleSend(){
    const txt = input.value.trim();
    if (!txt) return;
    addMessage(txt, 'user');
    input.value = '';
    setTimeout(() => {
      const r = replyTo(txt);
      addMessage(r, 'bot');
    }, 300 + Math.random()*300);
  }

  sendBtn.addEventListener('click', handleSend);
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') { e.preventDefault(); handleSend(); }
  });

  // Roles typewriter (hero)
  const roles = ["Tech Enthusiast","AI Learner","Creative Storyteller","Coffee-Powered Human ☕"];
  let ridx=0, rpos=0, rfor=true;
  const roleEl = document.getElementById('role');
  function tick(){
    const cur = roles[ridx];
    if (rfor){
      rpos++;
      roleEl.textContent = cur.slice(0,rpos);
      if (rpos === cur.length){ rfor=false; setTimeout(tick,1100); return; }
    } else {
      rpos--;
      roleEl.textContent = cur.slice(0,rpos);
      if (rpos === 0){ rfor=true; ridx=(ridx+1)%roles.length; setTimeout(tick,400); return; }
    }
    setTimeout(tick,70);
  }
  tick();

  // 3D parallax on mouse move (subtle)
  document.addEventListener("mousemove", (e) => {
    const x = (window.innerWidth / 2 - e.clientX) / 40;
    const y = (window.innerHeight / 2 - e.clientY) / 40;
    hero.style.transform = `perspective(800px) rotateY(${x}deg) rotateX(${y}deg) translateZ(0)`;
  });
  document.addEventListener("mouseleave", () => { hero.style.transform = "none"; });
</script>
</body>
</html>
"""

# -------------- Render the hero HTML (components) -------------
# Components height set to comfortably show hero area
components.html(hero_html, height=820, scrolling=False)

# ---------- Global CSS override for Streamlit app background to match theme ----------
# Keeps Streamlit areas readable while matching the hero's visual style.
st.markdown(
    """
    <style>
    /* Use a matching gradient for the Streamlit app background (transparent feel) */
    .stApp {
        background: linear-gradient(135deg, rgba(255,111,181,0.95) 0%, rgba(132,94,247,0.95) 50%, rgba(122,211,255,0.95) 100%) !important;
        color: #eaf6ff;
    }
    /* Make typical Streamlit cards look glassy */
    .stBlock, .css-1lcbmhc.e1fqkh3o3, .st-b1 {
        background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02)) !important;
        border: 1px solid rgba(255,255,255,0.04);
        box-shadow: 0 10px 40px rgba(6,6,10,0.35);
    }
    /* Tweak headings and text colors for contrast */
    .css-10trblm.egzxvld1 { color: #eaf6ff; } /* headers */
    .stMarkdown { color: #eaf6ff; }
    .stText { color: #eaf6ff; }
    a { color: #cde8ff !important; }
    </style>
    """, unsafe_allow_html=True
)

# ---------- Streamlit content area below (sections auto-load) ----------
st.markdown("---")
col1, col2 = st.columns([1, 2])

# Left column: Gallery preview (floating icons in component scroll to these)
with col1:
    st.markdown("### 📸 Photos (Gallery)")
    images = get_gallery_images()
    if not images:
        st.info("No images found. Add files to the `gallery/` folder.")
    else:
        # small preview grid (show up to 6)
        for i, img in enumerate(images):
            st.image(img, use_column_width=True, caption=os.path.basename(img))
            if i >= 5:
                break
        if len(images) > 6:
            st.caption(f"Plus {len(images)-6} more — they'll appear here automatically.")

# Right column: Blog & Writings sections
with col2:
    st.markdown("### ✍️ Writings (Markdown posts)")
    posts = get_all_posts()
    if not posts:
        st.info("No blog posts found. Add `.md` files to `blog_posts/`.")
    else:
        for p in posts:
            st.subheader(p["title"])
            st.caption(p.get("date", ""))
            st.markdown(p["html"], unsafe_allow_html=True)
            st.markdown("---")

# ---------- Short info about chat availability (client-side) ----------
st.markdown("---")
st.info("Chat is available via the floating 💬 bubble (bottom-right). The chat runs client-side and does not store messages on the server.")

# ---------- Footer / Projects / Contact placeholders ----------
st.markdown("---")
st.markdown("<a id='projects'></a>", unsafe_allow_html=True)
st.header("Projects")
st.markdown(
    """
- Chatbot Website  
- Portfolio Builder  
- AI Experiments  
(Projects area — add more details to `app.py` or use markdown posts.)
"""
)

st.markdown("<a id='contact'></a>", unsafe_allow_html=True)
st.header("Contact")
st.write("Prefer DM on Instagram: ", "[aryanxsharma26](https://instagram.com/aryanxsharma26)")

# ---------- (Removed Notes & Setup UI section by user request) ----------
# The "Notes & Setup" section has been intentionally removed from display.
# If you'd like it back for admins, I can add it behind a secret toggle.
