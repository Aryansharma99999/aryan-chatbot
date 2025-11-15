import streamlit as st
import streamlit.components.v1 as components
import os
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------
# STREAMLIT CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Aryan Sharma — Portfolio",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# GALLERY DIRECTORY
# ---------------------------------------------------------
GALLERY_DIR = Path("gallery")
GALLERY_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------
# ADMIN PANEL DETECTION (?admin=1)
# ---------------------------------------------------------
query_params = st.experimental_get_query_params()
is_admin = query_params.get("admin", ["0"])[0] == "1"

# ---------------------------------------------------------
# ADMIN PANEL UI
# ---------------------------------------------------------
if is_admin:
    st.sidebar.title("Admin Panel — Gallery Manager")

    uploaded = st.sidebar.file_uploader(
        "Upload Images", 
        type=["png", "jpg", "jpeg", "webp"], 
        accept_multiple_files=True
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
        col1, col2 = st.sidebar.columns([3, 1])
        col1.write(img.name)
        if col2.button("Delete", key=f"del_{img.name}"):
            img.unlink()
            st.sidebar.success("Deleted.")
            st.experimental_rerun()


# ---------------------------------------------------------
# BUILD GALLERY HTML
# ---------------------------------------------------------
def get_gallery_html():
    imgs = sorted(GALLERY_DIR.glob("*"), key=os.path.getmtime, reverse=True)
    if not imgs:
        return """
        <div class="card">No photos yet — upload using Admin Panel (?admin=1)</div>
        """
    html = ""
    for img in imgs:
        html += f"""
            <div class="card">
                <img src="gallery/{img.name}" 
                style="width:100%;height:180px;object-fit:cover;border-radius:10px;">
            </div>
        """
    return html

gallery_html = get_gallery_html()

# ---------------------------------------------------------
# FULL HTML (NO F-STRINGS)
# ---------------------------------------------------------
html_template = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Aryan Sharma — Portfolio</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap" rel="stylesheet">

<style>

 /* GENERAL */
body {
    margin: 0;
    font-family: Poppins, sans-serif;
    background: linear-gradient(180deg, #0b0020, #210034 60%);
    color: white;
    overflow-x: hidden;
}

/* FULL SCREEN PAGE */
.page {
    width: 100%;
    min-height: 100vh;
    padding: 40px 64px;
    box-sizing: border-box;
    position: relative;
    z-index: 2;
}

/* STARFIELD BACKGROUND */
.stars, .twinkling {
    position: fixed;
    inset: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
}
.stars {
    background:
        transparent url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="2" height="2"><circle cx="1" cy="1" r="1" fill="white" fill-opacity="0.03"/></svg>')
        repeat;
    background-size: 3px 3px;
    animation: starMove 120s linear infinite;
}
@keyframes starMove {
    from { background-position: 0 0; }
    to { background-position: -2000px 2000px; }
}
.twinkling {
    background-image: radial-gradient(circle, rgba(255,255,255,0.18), transparent 50%);
    animation: twinkle 5s infinite linear;
    opacity: .12;
}
@keyframes twinkle {
    0% {opacity: .05;}
    50% {opacity: .18;}
    100% {opacity: .05;}
}

/* LEFT TOOLBAR */
.leftbar {
    position: fixed;
    top: 50%;
    left: 18px;
    transform: translateY(-50%);
    z-index: 100;
    display: flex;
    flex-direction: column;
    gap: 14px;
}
.leftbtn {
    width: 56px;
    height: 56px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 12px;
    display: grid;
    place-items: center;
    cursor: pointer;
}
.leftbtn:hover {
    transform: translateX(5px);
}
.leftbtn img {
    width: 24px;
}

/* HERO SECTION */
.hero-wrap {
    width: 100%;
    margin-bottom: 40px;
}
.hero {
    width: 100%;
    max-width: 1300px;
    margin: auto;
    height: 300px;
    border-radius: 20px;
    padding: 30px;
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(7px);
    border: 2px solid rgba(255,255,255,0.08);
    position: relative;
    box-shadow: 0 20px 80px rgba(0,0,0,0.6);

    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}
.hero h1 {
    font-size: 54px;
    margin: 0;
    font-weight: 800;
    text-shadow: 0 3px 14px rgba(140,40,255,0.4);
}

.typing-block {
    margin-top: 10px;
    min-height: 28px;
    font-size: 20px;
    color: #d7c4ff;
    font-weight: 600;
    text-align: center;
}

/* ABOUT MINI TEXT */
.about-mini {
    margin-top: 12px;
    padding: 12px 18px;
    font-size: 14.5px;
    color: rgba(255,255,255,0.9);
    background: rgba(255,255,255,0.04);
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.1);
    max-width: 1000px;
    text-align: center;
}

/* GALLERY / PROJECTS */
.section {
    margin-top: 40px;
}
.section h2 {
    font-size: 28px;
    margin-bottom: 16px;
}
.grid {
    display: grid;
    gap: 18px;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}
.card {
    padding: 12px;
    background: rgba(255,255,255,0.04);
    border-radius: 14px;
}

/* CHAT WIDGET */
.chat-widget {
    position: fixed;
    left: 90px;
    bottom: 28px;
    width: 400px;
    max-height: 70vh;
    background: linear-gradient(180deg, #2b2b2b, #202020);
    border-radius: 18px;
    display: none;
    z-index: 200;
    overflow: hidden;
}
.chat-header {
    padding: 12px 16px;
    display: flex;
    gap: 12px;
    font-weight: 700;
    color: #00c8ff;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}
.chat-body {
    padding: 14px;
    overflow-y: auto;
    height: 260px;
    display: flex;
    flex-direction: column;
    gap: 10px;
}
.bot-msg {
    background: #3d3d3d;
    padding: 10px 14px;
    border-radius: 12px;
}
.user-msg {
    background: #00c8ff;
    color: #003344;
    padding: 10px 14px;
    border-radius: 12px;
    align-self: flex-end;
}
.chat-input {
    display: flex;
    border-top: 1px solid rgba(255,255,255,0.1);
}
.chat-input input {
    flex: 1;
    padding: 10px;
    background: #111;
    border: none;
    color: white;
    outline: none;
}
.chat-input button {
    background: #00c8ff;
    color: #003344;
    border: none;
    padding: 10px 15px;
    cursor: pointer;
    font-weight: 700;
}

</style>
</head>

<body>

<div class="stars"></div>
<div class="twinkling"></div>

<!-- LEFT TOOLBAR -->
<div class="leftbar">
    <div class="leftbtn" onclick="scrollToId('top')">
        <img src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/
2000/svg' viewBox='0 0 24 24' fill='white'><path d='M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z'/></svg>">
    </div>

    <div class="leftbtn" onclick="scrollToId('gallery')">
        <img src="data:image/svg+xml;utf8,<svg xmlns='http://www/
w3.org/2000/svg' viewBox='0 0 24 24' fill='white'><path d='M21 19V5a2 2 0 0 0-2-2H5C3.9 3 3 3.9 3 5v14l4-3 3 2 5-4 6 4z'/></svg>">
    </div>

    <div class="leftbtn" onclick="toggleChat()">
        <img src="data:image/svg+xml;utf8,<svg xmlns='http://www/
w3.org/2000/svg' viewBox='0 0 24 24' fill='white'><path d='M21 6h-2v9H6v2c0 1.1.9 2 2 2h9l4 4V8c0-1.1-.9-2-2-2zM17 2H3c-1.1 0-2 .9-2 2v12l4-4h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z'/></svg>">
    </div>

</div>

<!-- PAGE -->
<div class="page" id="top">

    <!-- HERO -->
    <div class="hero-wrap">
        <div class="hero">
            <h1>Aryan Sharma</h1>
            <div class="typing-block" id="typingLine"></div>
            <div class="about-mini" id="aboutMini"></div>
        </div>
    </div>

    <!-- GALLERY -->
    <div class="section" id="gallery">
        <h2>📷 Gallery</h2>
        <div class="grid">
            ###GALLERY###
        </div>
    </div>

    <!-- PROJECTS -->
    <div class="section">
        <h2>🚀 Projects</h2>
        <div class="grid">
            <div class="card"><strong>Chatbot Website</strong><br>AI-powered chat interface</div>
            <div class="card"><strong>Portfolio Builder</strong><br>Create sites instantly</div>
            <div class="card"><strong>AI Experiments</strong><br>Fun ML tests</div>
        </div>
    </div>

</div>

<!-- CHATBOX -->
<div class="chat-widget" id="chatWidget">
    <div class="chat-header">
        Aryan's AI Chatbot — Ask me about Aryan
    </div>
    <div class="chat-body" id="chatBody">
        <div class="bot-msg">Hi! Ask me anything about Aryan.</div>
    </div>
    <div class="chat-input">
        <input id="chatInput" placeholder="Type a message...">
        <button onclick="sendMessage()">Send</button>
    </div>
</div>

<script>

function scrollToId(id){
    var el = document.getElementById(id);
    if(el){
        el.scrollIntoView({behavior:"smooth"});
    }
}

/* CHATBOX TOGGLE */
function toggleChat(){
    var box = document.getElementById("chatWidget");
    if(box.style.display === "block"){
        box.style.display = "none";
    } else {
        box.style.display = "block";
    }
}

/* CHAT SEND */
function sendMessage(){
    var input = document.getElementById("chatInput");
    var body = document.getElementById("chatBody");
    var msg = input.value.trim();
    if(msg === "") return;

    body.innerHTML += "<div class='user-msg'>" + msg + "</div>";
    input.value = "";

    setTimeout(function(){
        body.innerHTML += "<div class='bot-msg'>This is a sample reply. You can integrate GPT here.</div>";
        body.scrollTop = body.scrollHeight;
    }, 600);

    body.scrollTop = body.scrollHeight;
}

/* TYPING + DELETING ANIMATION */
var roles = [
    "I'm a Web Designer",
    "I'm a Problem Solver",
    "I'm a Tech Enthusiast",
    "I'm a Developer",
    "I'm a Writer"
];

var aboutLines = [
    "Hi, I'm Aryan Sharma, currently pursuing a Bachelor's Degree.",
    "I'm passionate about coding, learning, and developing new things.",
    "This site showcases my work and lets you chat with my AI assistant to learn more about me."
];

function typeDelete(elem, text, speed){
    return new Promise(resolve => {
        let i = 0;
        elem.innerHTML = "";
        let add = setInterval(() => {
            elem.innerHTML += text.charAt(i);
            i++;
            if(i >= text.length){
                clearInterval(add);
                setTimeout(() => resolve(), 900);
            }
        }, speed);
    }).then(() => {
        return new Promise(resolve => {
            let j = elem.innerHTML.length;
            let del = setInterval(() => {
                elem.innerHTML = elem.innerHTML.slice(0, j-1);
                j--;
                if(j <= 0){
                    clearInterval(del);
                    resolve();
                }
            }, 28);
        });
    });
}

async function typingLoop(){
    var t = document.getElementById("typingLine");
    var a = document.getElementById("aboutMini");

    while(true){
        for(let r of roles){
            await typeDelete(t, r, 50);
        }
        for(let line of aboutLines){
            await typeDelete(t, line, 30);
            a.innerHTML = line;
            await new Promise(r => setTimeout(r, 1500));
        }
    }
}

setTimeout(typingLoop, 300);

</script>
</body>
</html>
"""

# ---------------------------------------------------------
# INSERT THE GALLERY HTML SAFELY (NO f-string)
# ---------------------------------------------------------
html_template = html_template.replace("###GALLERY###", gallery_html)

# ---------------------------------------------------------
# RENDER FULL SITE
# ---------------------------------------------------------
components.html(html_template, height=1500, scrolling=True)
