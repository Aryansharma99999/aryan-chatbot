import streamlit as st
import streamlit.components.v1 as components
import os
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Aryan Sharma — Portfolio", layout="wide", initial_sidebar_state="collapsed")

# Fullscreen Patch
st.markdown("""
<style>
[data-testid="stHeader"], section[data-testid="stSidebar"] {display:none!important;}
.block-container {padding:0!important; margin:0!important; max-width:100%!important;}
html, body, .stApp, [data-testid="stAppViewContainer"] {
    margin:0!important; padding:0!important; width:100%!important; height:100%!important;
}
iframe {width:100%!important; height:100%!important; border:none!important;}
</style>
""", unsafe_allow_html=True)

# Gallery directory
GALLERY_DIR = Path("gallery")
GALLERY_DIR.mkdir(exist_ok=True)

# Admin mode
query_params = st.experimental_get_query_params()
is_admin = query_params.get("admin", ["0"])[0] == "1"

if is_admin:
    st.sidebar.title("Admin — Gallery Manager")
    uploaded = st.sidebar.file_uploader("Upload images", type=["png","jpg","jpeg","webp"], accept_multiple_files=True)
    if uploaded:
        for f in uploaded:
            filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{f.name}"
            with open(GALLERY_DIR / filename, "wb") as out:
                out.write(f.getbuffer())
        st.experimental_rerun()

    st.sidebar.subheader("Images")
    for img in sorted(GALLERY_DIR.glob("*")):
        row = st.sidebar.columns([4,1])
        row[0].write(img.name)
        if row[1].button("❌", key=img.name):
            img.unlink()
            st.experimental_rerun()

# Build gallery HTML
def gallery_html():
    imgs = sorted(GALLERY_DIR.glob("*"))
    if not imgs:
        return "<div class='card'>No images yet</div>"
    html = ""
    for img in imgs:
        html += f"""
        <div class='card'>
            <img src='gallery/{img.name}' style='width:100%;height:180px;object-fit:cover;border-radius:10px;'>
        </div>
        """
    return html

GALLERY_BLOCK = gallery_html()

# Full HTML page
HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'>
<title>Aryan Sharma</title>
<link href='https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap' rel='stylesheet'>
<style>
body{margin:0;font-family:Poppins;background:linear-gradient(180deg,#0b0020,#210034);color:#fff;}
.section{padding:40px 60px;}
.grid{display:grid;gap:20px;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));}
.card{background:rgba(255,255,255,0.05);padding:10px;border-radius:12px;}
.hero{margin:100px auto;width:80%;text-align:center;}
</style>
</head>
<body>

<div class='hero'>
  <h1 style='font-size:50px;font-weight:800;'>Aryan Sharma</h1>
  <h3>I'm a Web Designer | Developer | Tech Enthusiast</h3>
</div>

<div class='section'>
<h2>📷 Gallery</h2>
<div class='grid'>
###GALLERY###
</div>
</div>

<div class='section'>
<h2>🚀 Projects</h2>
<div class='grid'>
  <div class='card'><b>Chatbot Website</b><p>AI chat interface</p></div>
  <div class='card'><b>Portfolio Builder</b><p>Create sites instantly</p></div>
  <div class='card'><b>AI Experiments</b><p>Mini ML Projects</p></div>
</div>
</div>

</body>
</html>
"""

HTML = HTML.replace("###GALLERY###", GALLERY_BLOCK)

components.html(HTML, height=2000, scrolling=True)
import streamlit as st

st.set_page_config(layout="wide")

# --- Load the WebGL animation ---
html_code = open("animated_bg.html", "r").read()

st.components.v1.html(html_code, height=900, width=None)
