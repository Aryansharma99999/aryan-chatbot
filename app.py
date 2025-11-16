# app.py - FAANG-Level Premium Portfolio (Fully Working)

import os, re, json, time, base64
import streamlit as st
from markdown import markdown
import streamlit.components.v1 as components

st.set_page_config(page_title="Aryan Sharma", layout="wide", initial_sidebar_state="collapsed")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
GALLERY_DIR = os.path.join(BASE_DIR, "gallery")
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")

os.makedirs(GALLERY_DIR, exist_ok=True)
os.makedirs(POSTS_DIR, exist_ok=True)

def get_gallery_images():
    if not os.path.exists(GALLERY_DIR):
        return []
    files = sorted([f for f in os.listdir(GALLERY_DIR) if f.lower().endswith((".jpg",".jpeg",".png",".webp"))])
    return [os.path.join("gallery", f) for f in files]

def make_data_url(path):
    try:
        real = os.path.join(BASE_DIR, path)
        with open(real,"rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        ext = os.path.splitext(real)[1][1:]
        return f"data:image/{ext};base64,{b64}"
    except:
        return ""

images = get_gallery_images()
hero_preview = images[:3] + [""]*(3-len(images[:3]))

hero_html = f"""<!doctype html><html><head>
<meta charset='utf-8'/><meta name='viewport' content='width=device-width,initial-scale=1'/>
<link href='https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700;800&display=swap' rel='stylesheet'>
<style>
:root{{--p1:#fbe9f9;--p2:#eaf6ff;--p3:#f7f0ff;--accent:#7b44e5;}}
html,body{{margin:0;padding:0;background:transparent;font-family:'Inter',sans-serif;}}
.bg{{position:fixed;inset:0;background:linear-gradient(135deg,var(--p2),var(--p3),var(--p1));background-size:300% 300%;animation:bgMove 18s infinite linear;}}
@keyframes bgMove{{0%{{background-position:0% 50%}}50%{{background-position:100% 50%}}100%{{background-position:0% 50%}}}}
.stage{{position:relative;z-index:2;min-height:75vh;display:flex;align-items:center;justify-content:center;padding:48px;}}
.card{{width:92%;max-width:1200px;background:rgba(255,255,255,0.8);border-radius:22px;padding:54px;backdrop-filter:blur(12px);
box-shadow:0 30px 80px rgba(0,0,0,0.07);position:relative;}}
.card h1{{font-size:56px;margin:0;color:#111;font-weight:800;}}
.card h3{{margin:0;color:#777;font-weight:500;}}
.lead{{margin-top:14px;color:#444;font-size:18px;max-width:70%;}}
.role{{display:inline-block;margin-top:14px;padding:10px 16px;border-radius:999px;background:rgba(123,68,229,0.12);color:var(--accent);font-weight:700;}}
.actions{{margin-top:22px;display:flex;gap:12px;}}
.btn{{padding:12px 18px;border-radius:999px;border:none;font-weight:700;cursor:pointer;}}
.btn.fill{{background:linear-gradient(90deg,#ffd6eb,#dfe9ff);color:#000;}}
.btn.ghost{{background:transparent;border:1px solid #ccc;color:#444;}}
.previews{{position:absolute;right:30px;top:30px;display:flex;gap:12px;}}
.prev{{width:120px;height:120px;border-radius:14px;overflow:hidden;box-shadow:0 12px 36px rgba(0,0,0,0.1);}}
.prev img{{width:100%;height:100%;object-fit:cover;}}
@media(max-width:980px){{.previews{{display:none;}}.card h1{{font-size:38px;}}}}
</style>
</head><body>
<div class='bg'></div>
<div class='stage'>
<div class='card' id='heroCard'>
<h3>Hello, I'm</h3>
<h1>Aryan Sharma</h1>
<p class='lead'>I turn everyday life into little stories—coffee-powered, curious, and always building.</p>
<div class='role' id='role'>Creative Storyteller</div>
<div class='actions'>
<button class='btn fill' onclick="location.href='#projects'">View Projects</button>
<button class='btn ghost' onclick="location.href='#contact'">Contact</button>
</div>

<div class='previews'>
<div class='prev'><img id='ph1'></div>
<div class='prev'><img id='ph2'></div>
<div class='prev'><img id='ph3'></div>
</div>
</div></div>

<script>
const roles=["Creative Storyteller","Tech Enthusiast","AI Learner","Coffee-Powered Human ☕"];
let i=0,p=0,fwd=true;const el=document.getElementById("role");

function type(){
 let t=roles[i];
 if(fwd){p++;el.textContent=t.slice(0,p);if(p===t.length){fwd=false;setTimeout(type,900);return;}}
 else{p--;el.textContent=t.slice(0,p);if(p===0){fwd=true;i=(i+1)%roles.length;setTimeout(type,400);return;}}
 setTimeout(type,60);
}
type();

const imgs={json.dumps(hero_preview)};
["ph1","ph2","ph3"].forEach((id,n)=>{
 if(imgs[n]) document.getElementById(id).src=imgs[n];
 else document.getElementById(id).parentElement.style.display="none";
});
</script></body></html>"""

components.html(hero_html,height=760,scrolling=False)

st.markdown("<style>header{display:none;} .stApp{background:linear-gradient(180deg,#fbe9f9,#eaf6ff,#f7f0ff)!important;}</style>",unsafe_allow_html=True)

st.markdown("## 📸 Gallery")
cols = st.columns(3)
for idx,p in enumerate(images):
    try:
        with cols[idx%3]:
            st.image(p,use_column_width=True)
    except:
        with cols[idx%3]:
            st.image(make_data_url(p),use_column_width=True)

st.markdown("---")
st.header("Projects")
st.write("- Chatbot Website
- Portfolio Builder
- AI Experiments")

st.markdown("---")
st.header("Contact")
st.write("DM on Instagram: [aryansharmax26](https://instagram.com/aryansharmax26)")
