# app.py
import streamlit as st
import streamlit.components.v1 as components
import os
from pathlib import Path
from datetime import datetime
import shutil

# -------------------------
# Config / Setup
# -------------------------
st.set_page_config(page_title="Aryan Sharma — Portfolio", layout="wide", initial_sidebar_state="collapsed")

GALLERY_DIR = Path("gallery")
GALLERY_DIR.mkdir(exist_ok=True)

# -------------------------
# Admin detection via URL param ?admin=1
# -------------------------
query_params = st.experimental_get_query_params()
is_admin = query_params.get("admin", ["0"])[0] == "1"

# -------------------------
# Admin UI (upload + delete) - shown only if ?admin=1
# -------------------------
if is_admin:
    st.markdown("<div style='position:fixed;right:18px;top:18px;z-index:99999'>"
                "<div style='background:#1b0b2b;padding:10px;border-radius:10px;box-shadow:0 8px 30px rgba(0,0,0,0.6)'>"
                "<strong style='color:#fff'>Admin Panel</strong><br><small style='color:#ddd'>Uploads saved to /gallery</small>"
                "</div></div>", unsafe_allow_html=True)

    st.sidebar.header("Admin — Gallery Manager")
    st.sidebar.write("Upload images (jpg, png, webp). They will appear in the Gallery.")

    uploaded = st.sidebar.file_uploader("Upload image", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)
    if uploaded:
        for file in uploaded:
            # save file to gallery dir with timestamp to avoid collisions
            filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.name}"
            dest = GALLERY_DIR / filename
            with open(dest, "wb") as f:
                f.write(file.getbuffer())
        st.sidebar.success(f"Saved {len(uploaded)} file(s). Refresh the main page to see them.")
        st.experimental_rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("Existing images")
    imgs = sorted([p for p in GALLERY_DIR.iterdir() if p.is_file()], key=os.path.getmtime, reverse=True)
    if not imgs:
        st.sidebar.info("No images in gallery yet.")
    else:
        for img_path in imgs:
            cols = st.sidebar.columns([2,1])
            cols[0].write(f"**{img_path.name}**")
            if cols[1].button("Delete", key=f"del_{img_path.name}"):
                try:
                    img_path.unlink()
                    st.sidebar.success(f"Deleted {img_path.name}")
                    st.experimental_rerun()
                except Exception as e:
                    st.sidebar.error(f"Error deleting: {e}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("Admin access via URL param: `?admin=1`")

# -------------------------
# Prepare gallery HTML from uploaded images
# -------------------------
# We will reference the images as relative paths (gallery/filename).
# Streamlit serves files from the working directory, so components.html can load them.

def build_gallery_items():
    imgs = sorted([p for p in GALLERY_DIR.iterdir() if p.is_file()], key=os.path.getmtime, reverse=True)
    if not imgs:
        # placeholder cards
        placeholders = []
        for i in range(4):
            placeholders.append("""
            <div class="card">
              <div style="height:140px;display:grid;place-items:center;color:rgba(255,255,255,0.5)">
                Photo {i} — upload via Admin
              </div>
            </div>
            """.replace("{i}", str(i+1)))
        return "\n".join(placeholders)
    html_parts = []
    for p in imgs:
        url = f"gallery/{p.name}"
        # safe HTML for each card
        part = f"""
        <div class="card">
          <img src="{url}" style="width:100%;height:180px;object-fit:cover;border-radius:10px;border:1px solid rgba(255,255,255,0.03)">
        </div>
        """
        html_parts.append(part)
    return "\n".join(html_parts)

gallery_html = build_gallery_items()

# -------------------------
# Full HTML site (with gallery injected)
# -------------------------
# This HTML is self-contained; we inject gallery_html where indicated.
html_template = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Aryan Sharma — Portfolio</title>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root{{ --maxw:1400px; }}
    html,body{{ height:100%; margin:0; font-family: Poppins, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; }}
    body {{
      background: linear-gradient(180deg, #0b0020 0%, #210034 60%);
      color: #fff;
      -webkit-font-smoothing:antialiased;
      -moz-osx-font-smoothing:grayscale;
      overflow-x: hidden;
      min-height:100vh;
    }}

    /* STARFIELD (animated) */
    .stars, .twinkling {{
      position: fixed; top:0; left:0; right:0; bottom:0; width:100%; height:100%; display:block; z-index:0; pointer-events:none;
    }}
    .stars {{
      background: transparent url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="2" height="2"><circle cx="1" cy="1" r="1" fill="white" fill-opacity="0.03"/></svg>') repeat;
      background-size: 3px 3px;
      animation: moveStars 120s linear infinite;
      opacity:0.9;
      transform: translateZ(0);
    }}
    @keyframes moveStars {{ from {{background-position:0 0}} to {{background-position: -2000px 2000px}} }}

    .twinkling {{
      background-image: radial-gradient(circle, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0) 50%);
      background-repeat: repeat;
      background-size: 600px 600px;
      animation: twinkle 6s linear infinite;
      opacity:0.15;
      mix-blend-mode: screen;
    }}
    @keyframes twinkle {{ 0%{{opacity:0.06}}50%{{opacity:0.17}}100%{{opacity:0.06}} }}

    /* Page container full-screen */
    .page {{
      position: relative;
      z-index: 2;
      width: 100%;
      min-height: 100vh;
      padding: 40px 64px;
      box-sizing: border-box;
    }}

    /* Left fixed icon bar */
    .leftbar {{
      position: fixed;
      left: 18px;
      top: 40%;
      transform: translateY(-50%);
      display:flex;
      flex-direction:column;
      gap:14px;
      z-index: 40;
    }}
    .leftbtn {{
      width:56px;height:56px;border-radius:12px;
      background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
      border: 2px solid rgba(255,255,255,0.03);
      display:grid;place-items:center;
      cursor:pointer;
      box-shadow: 0 10px 30px rgba(0,0,0,0.5);
      transition: transform .18s ease, box-shadow .18s ease;
    }}
    .leftbtn:hover{{ transform: translateX(6px) }}
    .leftbtn img{{ width:22px;height:22px; filter: drop-shadow(0 6px 12px rgba(0,0,0,0.6)) }}

    /* HERO BOX */
    .hero-wrap {{
      width: 100%;
      position: relative;
      padding: 18px 0;
      border-radius: 22px;
      margin-bottom: 36px;
      z-index:5;
    }}
    .hero {{
      width: 100%;
      max-width: var(--maxw);
      margin: 0 auto;
      height: 300px;
      border-radius:18px;
      display:flex;
      flex-direction:column;
      align-items:center;
      justify-content:center;
      gap:12px;
      padding: 28px;
      background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
      border-radius:18px;
      border: 2px solid rgba(255,255,255,0.02);
      backdrop-filter: blur(6px);
      box-shadow: 0 30px 80px rgba(0,0,0,0.6);
      position:relative;
      overflow:hidden;
    }}

    /* outer animated stroke */
    .glow-border {{
      position: absolute;
      inset: -8px;
      border-radius:24px;
      pointer-events:none;
      z-index:1;
      background: conic-gradient(from 120deg, rgba(138,57,243,0.16), rgba(180,92,255,0.14), rgba(138,57,243,0.12));
      filter: blur(10px);
      animation: rotate 10s linear infinite;
      opacity:0.9;
    }}
    @keyframes rotate {{ to {{ transform: rotate(360deg) }} }}

    .hero h1 {{
      font-size:52px;
      margin:0;
      font-weight:800;
      letter-spacing:-0.02em;
      z-index:3;
      color: white;
      text-shadow: 0 6px 40px rgba(150,60,255,0.28);
    }}
    .hero .typing-block {{
      font-size:20px;
      color: #d9b7ff;
      font-weight:600;
      min-height:30px;
      z-index:3;
      text-align:center;
      letter-spacing:0.2px;
    }}

    /* about mini-box inside hero */
    .about-mini {{
      margin-top:8px;
      padding:12px 18px;
      border-radius:12px;
      background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
      border: 1px solid rgba(255,255,255,0.03);
      max-width:1100px;
      z-index:3;
      color:rgba(255,255,255,0.88);
      font-size:15px;
      text-align:center;
    }}

    /* CHAT WIDGET */
    .chat-widget {{
      position: fixed;
      left: 92px; /* since leftbar exists */
      bottom: 24px;
      width: 420px;
      max-width: calc(100% - 120px);
      border-radius: 18px;
      background: linear-gradient(180deg,#262626,#2e2e2e);
      box-shadow: 0 30px 80px rgba(0,0,0,0.7);
      z-index: 60;
      overflow: hidden;
      transform-origin: bottom left;
      display: none; /* toggled with JS */
    }}
    .chat-header {{
      padding: 14px 16px;
      display:flex;
      align-items:center;
      gap:12px;
      border-bottom: 1px solid rgba(255,255,255,0.02);
      color: #00c8ff;
      font-weight:700;
      background: linear-gradient(90deg, rgba(0,0,0,0.05), rgba(255,255,255,0.02));
    }}
    .faq-badge {{
      margin-left:auto;
      background:#0bbef3;
      color:#05232e;
      padding:4px 10px;
      border-radius:10px;
      font-weight:700;
      font-size:12px;
    }}
    .chat-body {{
      padding: 16px;
      min-height: 140px;
      max-height: 320px;
      overflow:auto;
      display:flex;
      flex-direction:column;
      gap:12px;
    }}
    .bot-msg {{
      max-width: 86%;
      background: #3b3b3b;
      color: white;
      padding: 10px 12px;
      border-radius: 10px;
      font-size:14px;
    }}
    .user-msg {{
      align-self: flex-end;
      background: linear-gradient(90deg,#00c8ff,#4cc8ff);
      color: #04232a;
      padding: 10px 12px;
      border-radius: 10px;
      font-size:14px;
    }}
    .chat-input {{
      padding: 12px;
      display:flex;
      gap:10px;
      border-top:1px solid rgba(255,255,255,0.02);
      background: linear-gradient(180deg, rgba(0,0,0,0.03), rgba(255,255,255,0.01));
      align-items:center;
    }}
    .chat-input input[type="text"]{ flex:1; padding:10px 12px; border-radius:10px; border:none; outline:none; background:#111; color:#fff; font-size:14px; }
    .send-btn {{ background: #00c8ff; color: #05232e; border:none; padding:10px 14px; border-radius:10px; font-weight:700; cursor:pointer; }}

    /* GALLERY / PROJECTS */
    .section {{ padding: 36px 0; color: #fff; }}
    .section h2 {{ font-size:28px; color:#e6d0ff; margin-bottom:14px; display:flex; gap:10px; align-items:center; }}
    .grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(220px,1fr)); gap:18px; }}
    .card {{ background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); border-radius:12px; padding:12px; border:1px solid rgba(255,255,255,0.03); }}

    /* responsive adjustments */
    @media (max-width:900px){ .hero {{ height:auto; padding:26px }} .hero h1{{ font-size:36px }} .leftbar{{ display:none }} .chat-widget{{ left:12px;width:92% }} }

  </style>
</head>
<body>
  <div class="stars"></div>
  <div class="twinkling"></div>

  <div class="leftbar" aria-hidden="false">
    <div class="leftbtn" id="homeBtn" title="Home (scroll)">
      <img src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'><path d='M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z'/></svg>"/>
    </div>
    <div class="leftbtn" id="galleryBtn" title="Open Gallery">
      <img src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'><path d='M21 19V5a2 2 0 0 0-2-2H5C3.9 3 3 3.9 3 5v14l4-3 3 2 5-4 6 4z'/></svg>"/>
    </div>
    <div class="leftbtn" id="chatBtn" title="Open Chat">
      <img src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'><path d='M21 6h-2v9H6v2c0 1.1.9 2 2 2h9l4 4V8c0-1.1-.9-2-2-2zM17 2H3c-1.1 0-2 .9-2 2v12l4-4h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z'/></svg>"/>
    </div>
    <div class="leftbtn" id="msgBtn" title="Anonymous Message">
      <img src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'><path d='M20 2H4a2 2 0 0 0-2 2v16l4-4h14a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2z'/></svg>"/>
    </div>
  </div>

  <div class="page" id="top">
    <div class="hero-wrap">
      <div class="glow-border" aria-hidden="true"></div>

      <div class="hero" role="banner" aria-label="Hero banner">
        <h1>Aryan Sharma</h1>
        <div class="typing-block" id="typingLine"></div>
        <div class="about-mini" id="aboutMini"></div>
      </div>
    </div>

    <section class="section" id="gallery">
      <h2>📷 Gallery</h2>
      <div class="grid">
        {gallery_html}
      </div>
    </section>

    <section class="section" id="projects">
      <h2>🚀 Projects</h2>
      <div class="grid">
        <div class="card"><strong>Chatbot Website</strong><p>Chat UI & assistant integration.</p></div>
        <div class="card"><strong>Portfolio Builder</strong><p>Auto-generate portfolio sites.</p></div>
        <div class="card"><strong>AI Experiments</strong><p>Small ML & prompt projects.</p></div>
      </div>
    </section>

    <footer style="padding:40px 0;text-align:center;color:rgba(255,255,255,0.5)">© 2025 Aryan Sharma</footer>
  </div>

  <!-- Chat widget -->
  <div class="chat-widget" id="chatWidget" aria-hidden="true" role="dialog" aria-label="Aryan's AI Chatbot">
    <div class="chat-header">
      <div style="font-weight:800;color:#00c8ff;font-size:15px;">
        Aryan's AI Chatbot<br><span style="color:#a8f2ff;font-size:12px;font-weight:600">Ask me about Aryan</span>
      </div>
      <div class="faq-badge">FAQ</div>
    </div>

    <div class="chat-body" id="chatBody">
      <div class="bot-msg">Ask me about Aryan.</div>
    </div>

    <div class="chat-input">
      <input type="text" id="chatInput" placeholder="Type your question..." aria-label="Type your question" />
      <button class="send-btn" id="sendBtn">Send</button>
    </div>
  </div>

<script>
  // Smooth scroll helpers
  function scrollToId(id){ const el = document.getElementById(id); if(el) el.scrollIntoView({behavior:'smooth', block:'start'}); }
  document.getElementById('homeBtn').addEventListener('click', ()=> scrollToId('top'));
  document.getElementById('galleryBtn').addEventListener('click', ()=> scrollToId('gallery'));
  document.getElementById('chatBtn').addEventListener('click', toggleChat);
  document.getElementById('msgBtn').addEventListener('click', ()=> alert('Anonymous message placeholder — implement backend to receive messages.'));

  // Chat toggle
  const chatWidget = document.getElementById('chatWidget');
  let chatOpen = false;
  function toggleChat(){
    chatOpen = !chatOpen;
    chatWidget.style.display = chatOpen ? 'block' : 'none';
    chatWidget.setAttribute('aria-hidden', (!chatOpen).toString());
    if(chatOpen) setTimeout(()=> document.getElementById('chatInput').focus(), 160);
  }

  // Simple chat send handler (UI-only)
  const sendBtn = document.getElementById('sendBtn');
  const chatBody = document.getElementById('chatBody');
  const chatInput = document.getElementById('chatInput');

  function appendMsg(text, cls='user-msg'){
    const d = document.createElement('div');
    d.className = cls;
    d.textContent = text;
    chatBody.appendChild(d);
    chatBody.scrollTop = chatBody.scrollHeight;
  }
  sendBtn.addEventListener('click', ()=> {
    const val = chatInput.value.trim();
    if(!val) return;
    appendMsg(val, 'user-msg');
    chatInput.value = '';
    setTimeout(()=> {
      const bot = document.createElement('div');
      bot.className = 'bot-msg';
      bot.textContent = "Thanks — here's a sample reply about Aryan. (Replace with your real assistant integration.)";
      chatBody.appendChild(bot);
      chatBody.scrollTop = chatBody.scrollHeight;
    }, 700);
  });
  chatInput.addEventListener('keydown', (e)=> { if(e.key === 'Enter') sendBtn.click(); });

  // Typing + deleting animation
  const roles = [
    "I'm a Web Designer",
    "I'm a Problem Solver",
    "I'm a Tech Enthusiast",
    "I'm a Developer",
    "I'm a Writer"
  ];
  const aboutLines = [
    "Hi, I'm Aryan Sharma, currently pursuing a Bachelor's Degree.",
    "I'm passionate about coding, learning, and developing new things.",
    "This site showcases my work and lets you chat with my AI assistant to learn more about me."
  ];

  function typeDelete(element, text, speed=40){
    return new Promise((resolve)=> {
      let i = 0;
      element.textContent = '';
      const t = setInterval(()=>{ element.textContent += text.charAt(i); i++; if(i >= text.length){ clearInterval(t); setTimeout(()=> { resolve(); }, 900); } }, speed);
    }).then(()=> {
      return new Promise((res)=> {
        let j = element.textContent.length;
        const d = setInterval(()=>{ element.textContent = element.textContent.slice(0, j-1); j--; if(j <= 0){ clearInterval(d); setTimeout(res, 250); } }, 28);
      });
    });
  }

  async function runLoop(){
    const typingEl = document.getElementById('typingLine');
    const aboutEl = document.getElementById('aboutMini');
    while(true){
      for(let r of roles){
        await typeDelete(typingEl, r, 48);
      }
      for(let a of aboutLines){
        await typeDelete(typingEl, a, 28);
        // show in the about-mini box
        aboutEl.style.opacity = 0;
        await new Promise(r => setTimeout(r, 220));
        aboutEl.textContent = a;
        aboutEl.style.transition = 'opacity 300ms';
        aboutEl.style.opacity = 1;
        await new Promise(r => setTimeout(r, 1600));
        typingEl.textContent = '';
      }
      await new Promise(r => setTimeout(r, 800));
    }
  }

  document.addEventListener('DOMContentLoaded', ()=> { runLoop().catch(console.error); });
  if(document.readyState === 'complete' || document.readyState === 'interactive'){ runLoop().catch(()=>{}); }

</script>
</body>
</html>
"""

# -------------------------
# Display the site: embed as HTML
# -------------------------
# Choose an appropriate height; allow scrolling inside component; use large height so it covers most screens.
components.html(html_template, height=1200, scrolling=True)
