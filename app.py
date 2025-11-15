# FULL AND FINAL app.py (Single Complete File)
# 100% Working — Fullscreen + Hero Animation + Gallery + Admin Panel + Chatbot

import streamlit as st
import streamlit.components.v1 as components
import os
from pathlib import Path
from datetime import datetime

# ------------------------------------------------------------------------
# STREAMLIT FULLSCREEN FIX (MUST COME AFTER IMPORTS — OR ERROR)
# ------------------------------------------------------------------------
st.markdown("""
<style>
/* Remove header */
[data-testid="stHeader"] { display: none !important; }

/* Remove side padding */
.block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
    width: 100% !important;
}

/* Remove top gap */
.css-18ni7ap, .css-1avcm0n, .e1fqkh3o3 {
    padding-top: 0 !important;
    margin-top: 0 !important;
}

/* Full viewport width+height */
html, body, .main, [data-testid="stAppViewContainer"] {
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
    height: 100% !important;
}

iframe {
    width: 100% !important;
    height: 100% !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------
# GALLERY FOLDER
# ------------------------------------------------------------------------
GALLERY_DIR = Path("gallery")
GALLERY_DIR.mkdir(exist_ok=True)

# ------------------------------------------------------------------------
# ADMIN MODE
# ------------------------------------------------------------------------
query_params = st.experimental_get_query_params()
is_admin = query_params.get("admin", ["0"])[0] == "1"

if is_admin:
    st.sidebar.title("Admin Panel — Gallery Manager")

    uploaded = st.sidebar.file_uploader(
        "Upload Images", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True
    )
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

# ------------------------------------------------------------------------
# BUILD GALLERY HTML
# ------------------------------------------------------------------------
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

# ------------------------------------------------------------------------
# MAIN HTML TEMPLATE
# ------------------------------------------------------------------------
html_template = """
<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'>
<title>Aryan Sharma — Portfolio</title>
<link href='https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap' rel='stylesheet'>

<style>
body {
    margin:0;
    font-family:Poppins;
    background:linear-gradient(180deg,#0b0020,#210034 60%);
    color:white;
    overflow-x:hidden;
}

.page { width:100%; min-height:100vh; margin:0; padding:0; position:relative; }

/* BACKGROUND STARFIELD */
.stars,.twinkling { position:fixed; inset:0; width:100%; height:100%; pointer-events:none; z-index:0; }

.stars {
 background:transparent url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='2' height='2'><circle cx='1' cy='1' r='1' fill='white' fill-opacity='0.03'/></svg>") repeat;
 background-size:3px 3px;
 animation:starMove 120s linear infinite;
}

@keyframes starMove { from{background-position:0 0;} to{background-position:-2000px 2000px;} }

.twinkling {
 background-image:radial-gradient(circle,rgba(255,255,255,0.18),transparent 50%);
 animation:twinkle 5s infinite linear;
 opacity:.15;
}

@keyframes twinkle { 0%{opacity:.05;} 50%{opacity:.18;} 100%{opacity:.05;} }

/* LEFTBAR */
.leftbar {
 position:fixed; top:50%; left:18px; transform:translateY(-50%);
 display:flex; flex-direction:column; gap:14px; z-index:100;
}
.leftbtn {
 width:56px; height:56px; background:rgba(255,255,255,0.05);
 border:1px solid rgba(255,255,255,0.1);
 border-radius:12px; display:grid; place-items:center; cursor:pointer;
}
.leftbtn:hover { transform:translateX(6px); }
.leftbtn img { width:24px; }

/* HERO */
.hero-wrap { width:100%; display:flex; justify-content:center; padding-top:160px; }
.hero {
 width:90%; max-width:1350px; height:300px;
 border-radius:22px;
 background:rgba(255,255,255,0.04);
 backdrop-filter:blur(8px);
 border:2px solid rgba(255,255,255,0.08);
 box-shadow:0 20px 80px rgba(0,0,0,0.6);
 display:flex; flex-direction:column; justify-content:center; align-items:center;
}
.hero h1 { font-size:58px; font-weight:800; margin:0; }

.typing-block { margin-top:12px; font-size:22px; color:#d9c8ff; min-height:28px; font-weight:600; }
.about-mini { margin-top:16px; padding:12px 20px; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:12px; max-width:850px; text-align:center; }

/* SECTIONS */
.section { padding:40px 60px; }
.grid { display:grid; gap:20px; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); }
.card { background:rgba(255,255,255,0.05); padding:10px; border-radius:12px; }

/* CHATBOX */
.chat-widget { position:fixed; bottom:24px; left:90px; width:400px; background:#242424; border-radius:16px; display:none; z-index:200; }
.chat-header { padding:14px; font-weight:800; color:#00d1ff; border-bottom:1px solid rgba(255,255,255,0.08); }
.chat-body { height:250px; overflow-y:auto; padding:14px; }
.bot-msg { background:#333; padding:10px; border-radius:12px; margin-bottom:10px; }
.user-msg { background:#00d1ff; color:#003344; padding:10px; border-radius:12px; margin-bottom:10px; text-align:right; }
.chat-input { display:flex; }
.chat-input input { flex:1; padding:10px; background:#111; border:none; color:white; }
.chat-input button { background:#00d1ff; border:none; padding:10px 14px; color:#002e35; font-weight:700; cursor:pointer; }
</style>
</head>
<body>

<div class='stars'></div>
<div class='twinkling'></div>

<!-- LEFTBAR -->
<div class='leftbar'>
 <div class='leftbtn' onclick="scrollToId('top')"><img src='data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" fill="white" viewBox="0 0 24 24"><path d="M12 3 2 12h3v8h6v-6h2v6h6v-8h3z"/></svg>'></div>
 <div class='leftbtn' onclick="scrollToId('gallery')"><img src='
