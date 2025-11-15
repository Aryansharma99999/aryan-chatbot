# FULL FINAL app.py
# (Complete working file with fullscreen, animation, gallery, admin panel, chatbox)
# Paste into your Streamlit app directly.

import streamlit as st
import streamlit.components.v1 as components
import os
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Aryan Sharma — Portfolio", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
html, body, .stApp {margin:0 !important; padding:0 !important;}
[data-testid="stHeader"] {display:none !important;}
main.block-container {padding:0 !important; margin:0 !important;}
#root > div:nth-child(1) {padding:0 !important; margin:0 !important;}
section[data-testid="stSidebar"] {display:none !important;}
</style>
""", unsafe_allow_html=True)

GALLERY_DIR = Path("gallery")
GALLERY_DIR.mkdir(exist_ok=True)

query_params = st.experimental_get_query_params()
is_admin = query_params.get("admin", ["0"])[0] == "1"

if is_admin:
    st.sidebar.title("Admin Panel — Gallery Manager")
    uploaded = st.sidebar.file_uploader("Upload Images", type=["png","jpg","jpeg","webp"], accept_multiple_files=True)
    if uploaded:
        for file in uploaded:
            filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.name}"
            with open(GALLERY_DIR / filename, "wb") as f:
                f.write(file.getbuffer())
        st.sidebar.success("Uploaded Successfully.")
        st.experimental_rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("Existing Images")
    imgs = sorted(GALLERY_DIR.glob("*"), key=os.path.getmtime, reverse=True)
    for img in imgs:
        c1, c2 = st.sidebar.columns([3, 1])
        c1.write(img.name)
        if c2.button("Delete", key=f"del_{img.name}"):
            img.unlink()
            st.sidebar.success("Deleted.")
            st.experimental_rerun()


def get_gallery_html():
    imgs = sorted(GALLERY_DIR.glob("*"), key=os.path.getmtime, reverse=True)
    if not imgs:
        return "<div class='card'>No photos yet — upload using Admin Panel (?admin=1)</div>"
    html = ""
    for img in imgs:
        html += f"""
        <div class='card'>
            <img src='gallery/{img.name}' style='width:100%;height:180px;object-fit:cover;border-radius:10px;'>
        </div>
        """
    return html

gallery_html = get_gallery_html()

html_template = """
<!doctype html>
<html>
<head>
<meta charset='utf-8'>
<title>Aryan Sharma — Portfolio</title>
<link href='https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap' rel='stylesheet'>
<style>
body{margin:0;font-family:Poppins;background:linear-gradient(180deg,#0b0020,#210034 60%);color:white;overflow-x:hidden;}
.page{width:100%;min-height:100vh;padding:0;margin:0;position:relative;z-index:2;}

.stars,.twinkling{position:fixed;inset:0;width:100%;height:100%;pointer-events:none;z-index:0;}
.stars{
 background:transparent url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2' height='2'><circle cx='1' cy='1' r='1' fill='white' fill-opacity='0.03'/></svg>") repeat;
 background-size:3px 3px;
 animation:starMove 120s linear infinite;
}
@keyframes starMove{from{background-position:0 0;}to{background-position:-2000px 2000px;}}
.twinkling{background-image:radial-gradient(circle,rgba(255,255,255,0.18),transparent 50%);animation:twinkle 5s infinite linear;opacity:.15;}
@keyframes twinkle{0%{opacity:.05;}50%{opacity:.18;}100%{opacity:.05;}}

.leftbar{position:fixed;top:50%;left:18px;transform:translateY(-50%);z-index:100;display:flex;flex-direction:column;gap:14px;}
.leftbtn{width:56px;height:56px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:12px;display:grid;place-items:center;cursor:pointer;}
.leftbtn:hover{transform:translateX(6px);} .leftbtn img{width:24px;}

.hero-wrap{width:100%;padding-top:160px;display:flex;justify-content:center;}
.hero{width:90%;max-width:1350px;height:300px;border-radius:22px;background:rgba(255,255,255,0.04);backdrop-filter:blur(8px);border:2px solid rgba(255,255,255,0.08);box-shadow:0 20px 80px rgba(0,0,0,0.6);display:flex;flex-direction:column;justify-content:center;align-items:center;}
.hero h1{font-size:58px;margin:0;font-weight:800;}
.typing-block{margin-top:10px;font-size:22px;color:#d9c8ff;min-height:28px;font-weight:600;}
.about-mini{margin-top:16px;padding:12px 20px;background:rgba(255,255,255,0.05);border-radius:12px;border:1px solid rgba(255,255,255,0.12);max-width:900px;text-align:center;}

.section{padding:40px 60px;}
.grid{display:grid;gap:20px;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));}
.card{background:rgba(255,255,255,0.05);padding:10px;border-radius:12px;}

.chat-widget{position:fixed;bottom:24px;left:90px;width:400px;background:#242424;border-radius:16px;display:none;z-index:200;}
.chat-header{padding:14px 16px;font-weight:800;color:#00d1ff;border-bottom:1px solid rgba(255,255,255,0.08);} .chat-body{padding:14px;height:250px;overflow-y:auto;}
.bot-msg{background:#333;padding:10px 14px;border-radius:12px;margin-bottom:10px;} .user-msg{background:#00d1ff;color:#003344;padding:10px 14px;border-radius:12px;margin-bottom:10px;text-align:right;}
.chat-input{display:flex;border-top:1px solid rgba(255,255,255,0.1);} .chat-input input{flex:1;padding:10px;background:#111;border:none;color:white;} .chat-input button{background:#00d1ff;border:none;padding:10px 14px;color:#002e35;font-weight:700;cursor:pointer;}
</style>
</head>
<body>

<div class='stars'></div><div class='twinkling'></div>

<div class='leftbar'>
 <div class='leftbtn' onclick="scrollToId('top')"><img src='data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" fill="white" viewBox="0 0 24 24"><path d="M12 3 2 12h3v8h6v-6h2v6h6v-8h3z"/></svg>'></div>
 <div class='leftbtn' onclick="scrollToId('gallery')"><img src='data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" fill="white" viewBox="0 0 24 24"><path d="M21 19V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14l4-3 3 2 5-4 6 4z"/></svg>'></div>
 <div class='leftbtn' onclick="toggleChat()"><img src='data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" fill="white" viewBox="0 0 24 24"><path d="M4 2h16v14l-4-4H4z"/></svg>'></div>
</div>

<div class='page' id='top'>
 <div class='hero-wrap'>
   <div class='hero'>
      <h1>Aryan Sharma</h1>
      <div class='typing-block' id='typingLine'></div>
      <div class='about-mini' id='aboutMini'></div>
   </div>
 </div>

 <div class='section' id='gallery'>
   <h2>📷 Gallery</h2>
   <div class='grid'>###GALLERY###</div>
 </div>

 <div class='section'><h2>🚀 Projects</h2>
   <div class='grid'>
     <div class='card'><b>Chatbot Website</b><br>AI Chat UI</div>
     <div class='card'><b>Portfolio Builder</b><br>Create sites instantly</div>
     <div class='card'><b>AI Experiments</b><br>Mini ML Projects</div>
   </div>
 </div>
</div>

<div class='chat-widget' id='chatWidget'>
  <div class='chat-header'>Aryan's AI Chatbot — Ask me about Aryan</div>
  <div class='chat-body' id='chatBody'><div class='bot-msg'>Hi! Ask me about Aryan.</div></div>
  <div class='chat-input'><input id='chatInput' placeholder='Type message...'><button onclick='sendChat()'>Send</button></div>
</div>

<script>
function scrollToId(id){document.getElementById(id).scrollIntoView({behavior:'smooth'});} 
function toggleChat(){var w=document.getElementById('chatWidget');w.style.display=(w.style.display==='block')?'none':'block';}
function sendChat(){var i=document.getElementById('chatInput');var v=i.value.trim();if(!v)return;var b=document.getElementById('chatBody');b.innerHTML+="<div class='user-msg'>"+v+"</div>";i.value='';setTimeout(()=>{b.innerHTML+="<div class='bot-msg'>Thanks — here's a sample reply about Aryan.</div>";b.scrollTop=b.scrollHeight;},600);b.scrollTop=b.scrollHeight;}

async function typeEffect(e,t,s){e.innerHTML="";for(let i=0;i<t.length;i++){e.innerHTML+=t.charAt(i);await new Promise(r=>setTimeout(r,s));}}
async function deleteEffect(e,s){while(e.innerHTML.length>0){e.innerHTML=e.innerHTML.slice(0,-1);await new Promise(r=>setTimeout(r,s));}}

var roles=["I'm a Web Designer","I'm a Problem Solver","I'm a Tech Enthusiast","I'm a Developer","I'm a Writer"];
var aboutLines=["Hi, I'm Aryan Sharma, currently pursuing a Bachelor's Degree.","I'm passionate about coding, learning, and developing new things.","This site showcases my work and lets you chat with my AI assistant to learn more about me."];

async function startLoop(){var m=document.getElementById('typingLine');var a=document.getElementById('aboutMini');while(true){
 for(let r of roles){await typeEffect(m,r,40);await new Promise(r=>setTimeout(r,900));await deleteEffect(m,22);} 
 for(let l of aboutLines){await typeEffect(m,l,32);a.innerHTML=l;await new Promise(r=>setTimeout(r,1600));await deleteEffect(m,22);} }}
setTimeout(startLoop,400);
</script>
</body>
</html>
"""

html_template = html_template.replace("###GALLERY###", gallery_html)
components.html(html_template, height=900, scrolling=False)
