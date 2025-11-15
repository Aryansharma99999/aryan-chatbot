import streamlit as st
import streamlit.components.v1 as components
import os
from pathlib import Path
from datetime import datetime

# ---------------------------
# Streamlit config
# ---------------------------
st.set_page_config(page_title="Aryan Sharma — Portfolio", layout="wide", initial_sidebar_state="collapsed")

# ---------------------------
# Fullscreen CSS (after imports)
# ---------------------------
st.markdown("""
<style>
/* Hide header & sidebar area */
[data-testid="stHeader"], section[data-testid="stSidebar"] { display: none !important; }
/* Make block container full width */
.block-container { padding: 0 !important; margin: 0 !important; max-width: 100% !important; width: 100% !important; }
/* Remove other possible gaps */
.css-18ni7ap, .css-1avcm0n, .e1fqkh3o3 { padding-top: 0 !important; margin-top: 0 !important; }
/* Full viewport */
html, body, .stApp, [data-testid="stAppViewContainer"] { margin: 0 !important; padding: 0 !important; width: 100% !important; height: 100% !important; }
/* iframe */
iframe { width:100% !important; height:100% !important; border:none !important; margin:0 !important; padding:0 !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Gallery folder
# ---------------------------
GALLERY_DIR = Path("gallery")
GALLERY_DIR.mkdir(exist_ok=True)

# ---------------------------
# Admin mode via ?admin=1
# ---------------------------
query_params = st.experimental_get_query_params()
is_admin = query_params.get("admin", ["0"])[0] == "1"

if is_admin:
    st.sidebar.title("Admin — Gallery Manager")
    uploaded = st.sidebar.file_uploader("Upload images (png, jpg, webp)", type=["png","jpg","jpeg","webp"], accept_multiple_files=True)
    if uploaded:
        for f in uploaded:
            safe_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{f.name}"
            with open(GALLERY_DIR / safe_name, "wb") as out:
                out.write(f.getbuffer())
        st.sidebar.success("Uploaded successfully.")
        st.experimental_rerun()
    st.sidebar.markdown("---")
    st.sidebar.subheader("Existing images")
    imgs = sorted(GALLERY_DIR.glob("*"), key=os.path.getmtime, reverse=True)
    if not imgs:
        st.sidebar.info("No images in gallery yet.")
    else:
        for img in imgs:
            c1, c2 = st.sidebar.columns([3,1])
            c1.write(img.name)
            if c2.button("Delete", key=f"del_{img.name}"):
                try:
                    img.unlink()
                    st.sidebar.success("Deleted.")
                    st.experimental_rerun()
                except Exception as e:
                    st.sidebar.error(f"Error deleting: {e}")

# ---------------------------
# Build gallery HTML
# ---------------------------
def build_gallery_html():
    imgs = sorted(GALLERY_DIR.glob("*"), key=os.path.getmtime, reverse=True)
    if not imgs:
        return "<div class='card'>No photos yet — upload using Admin Panel (?admin=1)</div>"
    parts = []
    for p in imgs:
        # Use relative path so Streamlit serves it
        parts.append(f\"\"\"
        <div class=\"card\">
            <img src=\"gallery/{p.name}\" style=\"width:100%;height:180px;object-fit:cover;border-radius:10px;\">
        </div>
        \"\"\")
    return \"\\n\".join(parts)

gallery_html = build_gallery_html()

# ---------------------------
# Full HTML template (safe quoting)
# ---------------------------
html_template = \"\"\"<!doctype html>
<html>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Aryan Sharma — Portfolio</title>
<link href='https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap' rel='stylesheet'>
<style>
:root{ --accent: #9b3bff; }
html,body{height:100%;margin:0;padding:0;font-family:Poppins,system-ui,-apple-system,Segoe UI,Roboto,'Helvetica Neue',Arial;color:#fff;}
body{background:linear-gradient(180deg,#0b0020 0%,#210034 60%);overflow-x:hidden;}
.page{width:100%;min-height:100vh;box-sizing:border-box;position:relative;z-index:2;padding:0;margin:0;}
/* starfield */
.stars,.twinkling{position:fixed;inset:0;width:100%;height:100%;pointer-events:none;z-index:0;}
.stars{background:transparent url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2' height='2'><circle cx='1' cy='1' r='1' fill='white' fill-opacity='0.03'/></svg>\") repeat;background-size:3px 3px;animation:starMove 120s linear infinite;opacity:0.95;}
@keyframes starMove{from{background-position:0 0}to{background-position:-2000px 2000px}}
.twinkling{background-image:radial-gradient(circle,rgba(255,255,255,0.08),transparent 50%);animation:twinkle 6s linear infinite;opacity:0.12;mix-blend-mode:screen;}
@keyframes twinkle{0%{opacity:0.06}50%{opacity:0.18}100%{opacity:0.06}}

/* left bar */
.leftbar{position:fixed;left:18px;top:50%;transform:translateY(-50%);display:flex;flex-direction:column;gap:14px;z-index:40}
.leftbtn{width:56px;height:56px;border-radius:12px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.06);display:grid;place-items:center;cursor:pointer;box-shadow:0 8px 30px rgba(0,0,0,0.5)}
.leftbtn img{width:22px;height:22px}
.leftbtn:hover{transform:translateX(6px)}

/* hero */
.hero-wrap{width:100%;display:flex;justify-content:center;padding-top:120px;padding-bottom:20px;z-index:6}
.hero{width:92%;max-width:1300px;height:320px;border-radius:22px;padding:28px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;background:linear-gradient(180deg,rgba(255,255,255,0.02),rgba(255,255,255,0.01));border:2px solid rgba(255,255,255,0.03);backdrop-filter:blur(6px);box-shadow:0 20px 60px rgba(0,0,0,0.6);position:relative;overflow:hidden}
.hero h1{font-size:56px;margin:0;font-weight:800;text-shadow:0 6px 30px rgba(150,60,255,0.2)}
.typing-block{font-size:20px;color:#e6d0ff;min-height:28px;font-weight:700;text-align:center}
.about-mini{margin-top:8px;padding:12px 18px;border-radius:12px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.03);max-width:900px;text-align:center;color:rgba(255,255,255,0.9)}

/* sections */
.section{padding:40px 60px}
.grid{display:grid;gap:18px;grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}
.card{background:rgba(255,255,255,0.03);padding:12px;border-radius:12px;border:1px solid rgba(255,255,255,0.03)}

/* chat widget */
.chat-widget{position:fixed;left:92px;bottom:24px;width:420px;border-radius:16px;background:linear-gradient(180deg,#262626,#202020);box-shadow:0 30px 80px rgba(0,0,0,0.7);z-index:60;display:none;overflow:hidden}
.chat-header{padding:12px 14px;font-weight:800;color:#00c8ff;border-bottom:1px solid rgba(255,255,255,0.02)}
.faq-badge{margin-left:auto;background:#0bbef3;color:#05232e;padding:4px 10px;border-radius:10px;font-weight:700;font-size:12px}
.chat-body{padding:14px;min-height:140px;max-height:320px;overflow:auto;display:flex;flex-direction:column;gap:12px}
.bot-msg{max-width:86%;background:#333;padding:10px 12px;border-radius:10px;color:#fff}
.user-msg{align-self:flex-end;background:linear-gradient(90deg,#00c8ff,#4cc8ff);color:#04232a;padding:10px 12px;border-radius:10px}
.chat-input{padding:12px;display:flex;gap:10px;border-top:1px solid rgba(255,255,255,0.02);background:linear-gradient(180deg,rgba(0,0,0,0.03),rgba(255,255,255,0.01));align-items:center}
.chat-input input[type='text']{flex:1;padding:10px 12px;border-radius:10px;border:none;outline:none;background:#111;color:#fff;font-size:14px}
.send-btn{background:#00c8ff;color:#05232e;border:none;padding:10px 14px;border-radius:10px;font-weight:700;cursor:pointer}

@media(max-width:900px){.hero{height:auto;padding:18px}.hero h1{font-size:36px}.leftbar{display:none}.chat-widget{left:12px;width:92%}}
</style>
</head>
<body>
  <div class='stars'></div>
  <div class='twinkling'></div>

  <div class='leftbar' aria-hidden='false'>
    <div class='leftbtn' id='homeBtn' title='Home (scroll)'><img src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'><path d='M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z'/></svg>" /></div>
    <div class='leftbtn' id='galleryBtn' title='Gallery'><img src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'><path d='M21 19V5a2 2 0 0 0-2-2H5C3.9 3 3 3.9 3 5v14l4-3 3 2 5-4 6 4z'/></svg>" /></div>
    <div class='leftbtn' id='chatBtn' title='Chat'><img src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'><path d='M21 6h-2v9H6v2c0 1.1.9 2 2 2h9l4 4V8c0-1.1-.9-2-2-2zM17 2H3c-1.1 0-2 .9-2 2v12l4-4h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z'/></svg>" /></div>
  </div>

  <div class='page' id='top'>
    <div class='hero-wrap'>
      <div class='hero' role='banner' aria-label='Hero banner'>
        <h1>Aryan Sharma</h1>
        <div class='typing-block' id='typingLine'></div>
        <div class='about-mini' id='aboutMini'></div>
      </div>
    </div>

    <section class='section' id='gallery'>
      <h2>📷 Gallery</h2>
      <div class='grid'>
        ###GALLERY###
      </div>
    </section>

    <section class='section' id='projects'>
      <h2>🚀 Projects</h2>
      <div class='grid'>
        <div class='card'><strong>Chatbot Website</strong><p>Chat UI & assistant integration.</p></div>
        <div class='card'><strong>Portfolio Builder</strong><p>Auto-generate portfolio sites.</p></div>
        <div class='card'><strong>AI Experiments</strong><p>Small ML & prompt projects.</p></div>
      </div>
    </section>

    <footer style='padding:40px 0;text-align:center;color:rgba(255,255,255,0.5)'>© 2025 Aryan Sharma</footer>
  </div>

  <div class='chat-widget' id='chatWidget' aria-hidden='true' role='dialog' aria-label=\"Aryan's AI Chatbot\">
    <div class='chat-header'>
      <div style='font-weight:800;color:#00c8ff;font-size:15px;'>Aryan's AI Chatbot<br><span style='color:#a8f2ff;font-size:12px;font-weight:600'>Ask me about Aryan</span></div>
      <div class='faq-badge'>FAQ</div>
    </div>

    <div class='chat-body' id='chatBody'>
      <div class='bot-msg'>Ask me about Aryan.</div>
    </div>

    <div class='chat-input'>
      <input type='text' id='chatInput' placeholder='Type your question...' aria-label='Type your question' />
      <button class='send-btn' id='sendBtn'>Send</button>
    </div>
  </div>

<script>
// Smooth scroll helpers
function scrollToId(id){ const el = document.getElementById(id); if(el) el.scrollIntoView({behavior:'smooth', block:'start'}); }
document.getElementById('homeBtn').addEventListener('click', ()=> scrollToId('top'));
document.getElementById('galleryBtn').addEventListener('click', ()=> scrollToId('gallery'));
document.getElementById('chatBtn').addEventListener('click', toggleChat);

// Chat UI (dummy)
const chatWidget = document.getElementById('chatWidget');
let chatOpen = false;
function toggleChat(){ chatOpen = !chatOpen; chatWidget.style.display = chatOpen ? 'block' : 'none'; chatWidget.setAttribute('aria-hidden', (!chatOpen).toString()); if(chatOpen) setTimeout(()=> document.getElementById('chatInput').focus(), 160); }

const sendBtn = document.getElementById('sendBtn');
const chatBody = document.getElementById('chatBody');
const chatInput = document.getElementById('chatInput');

function appendMsg(text, cls='user-msg'){ const d = document.createElement('div'); d.className = cls; d.textContent = text; chatBody.appendChild(d); chatBody.scrollTop = chatBody.scrollHeight; }

sendBtn.addEventListener('click', ()=> {
  const val = chatInput.value.trim(); if(!val) return; appendMsg(val, 'user-msg'); chatInput.value = '';
  setTimeout(()=> { const bot = document.createElement('div'); bot.className = 'bot-msg'; bot.textContent = \"Thanks — here's a sample reply about Aryan.\"; chatBody.appendChild(bot); chatBody.scrollTop = chatBody.scrollHeight; }, 700);
});
chatInput.addEventListener('keydown', (e)=> { if(e.key === 'Enter') sendBtn.click(); });

// Typing + About animation (Option B)
const roles = [
  \"I'm a Web Designer\",
  \"I'm a Problem Solver\",
  \"I'm a Tech Enthusiast\",
  \"I'm a Developer\",
  \"I'm a Writer\"
];

const aboutLines = [
  \"Hi, I'm Aryan Sharma, currently pursuing a Bachelor's Degree.\",
  \"I'm passionate about coding, learning, and developing new things.\",
  \"This site showcases my work and lets you chat with my AI assistant to learn more about me.\"
];

function typeText(el, text, speed){ return new Promise(res => { el.textContent = ''; let i=0; const t = setInterval(()=>{ el.textContent += text.charAt(i); i++; if(i>=text.length){ clearInterval(t); setTimeout(res,700); } }, speed); }); }
function deleteText(el, speed){ return new Promise(res => { let j = el.textContent.length; const d = setInterval(()=>{ el.textContent = el.textContent.slice(0, j-1); j--; if(j<=0){ clearInterval(d); setTimeout(res,200); } }, speed); }); }

async function runLoop(){ const typingEl = document.getElementById('typingLine'); const aboutEl = document.getElementById('aboutMini'); while(true){ for(let r of roles){ await typeText(typingEl, r, 48); await deleteText(typingEl, 24); } for(let a of aboutLines){ await typeText(typingEl, a, 28); aboutEl.style.opacity = 0; await new Promise(r=>setTimeout(r,220)); aboutEl.textContent = a; aboutEl.style.transition = 'opacity 300ms'; aboutEl.style.opacity = 1; await new Promise(r=>setTimeout(r,1600)); await deleteText(typingEl, 22); } await new Promise(r=>setTimeout(r,800)); } }\n\ndocument.addEventListener('DOMContentLoaded', ()=> { try{ runLoop(); }catch(e){ console.error(e); } });\nif(document.readyState === 'interactive' || document.readyState === 'complete'){ try{ runLoop(); }catch(e){} }\n</script>\n</body>\n</html>\"\"\"

# inject gallery html
html_template = html_template.replace(\"###GALLERY###\", gallery_html)

# render the page (large height so it fills)
components.html(html_template, height=1000, scrolling=False)
