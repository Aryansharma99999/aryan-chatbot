
import streamlit as st
import streamlit.components.v1 as components
import os
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Aryan Sharma — Portfolio", layout="wide", initial_sidebar_state="collapsed")

# Fullscreen fix
st.markdown("""
<style>
[data-testid="stHeader"], section[data-testid="stSidebar"] {display:none!important;}
.block-container {padding:0!important; margin:0!important; max-width:100%!important;}
html, body, .stApp, [data-testid="stAppViewContainer"] {margin:0!important; padding:0!important; width:100%!important; height:100%!important;}
iframe {width:100%!important; height:100%!important; border:none!important;}
</style>
""", unsafe_allow_html=True)

GALLERY_DIR = Path("gallery")
GALLERY_DIR.mkdir(exist_ok=True)

# Admin mode
query = st.experimental_get_query_params()
is_admin = query.get("admin", ["0"])[0] == "1"

if is_admin:
    st.sidebar.title("Admin — Gallery")
    files = st.sidebar.file_uploader("Upload", type=["png","jpg","jpeg","webp"], accept_multiple_files=True)
    if files:
        for f in files:
            name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{f.name}"
            open(GALLERY_DIR/name, "wb").write(f.getbuffer())
        st.experimental_rerun()

    st.sidebar.markdown("---")
    for img in sorted(GALLERY_DIR.glob("*"), key=os.path.getmtime, reverse=True):
        c1, c2 = st.sidebar.columns([3,1])
        c1.write(img.name)
        if c2.button("Delete", key=str(img)):
            img.unlink()
            st.experimental_rerun()

def build_gallery():
    imgs = sorted(GALLERY_DIR.glob("*"), key=os.path.getmtime, reverse=True)
    if not imgs:
        return "<div class='card'>No images yet</div>"
    html = ""
    for i in imgs:
        html += f"""
        <div class='card'>
            <img src='gallery/{i.name}' style='width:100%;height:180px;object-fit:cover;border-radius:10px;'>
        </div>"""
    return html

gallery_html = build_gallery()

html = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'>
<title>Aryan Sharma — Portfolio</title>
<link href='https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap' rel='stylesheet'>
<style>
body{margin:0;font-family:Poppins;background:linear-gradient(180deg,#0b0020,#210034);color:#fff;overflow-x:hidden;}
.section{padding:40px 60px;}
.grid{display:grid;gap:20px;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));}
.card{background:rgba(255,255,255,0.05);padding:10px;border-radius:12px;}
.hero{margin:100px auto;width:80%;text-align:center;}
</style>
</head>
<body>

<div class='hero'>
  <h1>Aryan Sharma</h1>
  <h3>I'm a Developer | Designer | Tech Enthusiast</h3>
</div>

<div class='section'>
<h2>📷 Gallery</h2>
<div class='grid'>
###GALLERY###
</div>
</div>

</body>
</html>
"""

html = html.replace("###GALLERY###", gallery_html)
components.html(html, height=900, scrolling=True)
