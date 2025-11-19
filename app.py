import streamlit as st
import os, time, re
from markdown import markdown
import streamlit.components.v1 as components

st.set_page_config(page_title="Aryan Sharma", layout="wide")

# -------------------------------------------------------
# REMOVE ALL STREAMLIT WHITE SPACE & UI
# -------------------------------------------------------
st.markdown("""
<style>
/* Remove Streamlit Header + Footer + Menu */
#MainMenu, header, footer {visibility: hidden;}
/* Remove padding everywhere */
.stApp {margin: 0 !important; padding: 0 !important; background: transparent !important;}
.block-container {padding: 0 !important; margin: 0 !important; width: 100% !important; max-width: 100% !important;}
main, section.main > div {padding: 0 !important; margin: 0 !important;}
html, body {background: transparent !important; margin: 0; padding: 0; overflow-x: hidden;}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# BACKGROUND + HERO + CHATBOT (FULL SCREEN)
# -------------------------------------------------------
html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap" rel="stylesheet">

<style>
body {
  margin: 0;
  font-family: Poppins, sans-serif;
  overflow-x: hidden;
}

/* Full premium galaxy background */
.bg {
  position: fixed;
  inset: 0;
  background: radial-gradient(circle at 50% 0%, #3a007a, #0b001a 70%);
  z-index: -2;
}

/* Floating star particles */
.stars {
  position: fixed;
  inset:0;
  background-image: radial-gradient(white 1px, transparent 1px);
  background-size: 3px 3px;
  opacity: .15;
  animation: twinkle 6s infinite linear;
  z-index: -1;
}
@keyframes twinkle {
  0% {opacity: .18;}
  50% {opacity: .1;}
  100% {opacity: .18;}
}

/* HERO SECTION */
.hero {
  width: 100%;
  height: 95vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

.hero-box {
  width: 80%;
  max-width: 950px;
  padding: 50px 45px;
  text-align: center;
  border-radius: 25px;
  background: rgba(255,255,255,0.04);
  backdrop-filter: blur(16px);
  box-shadow: 0 0 40px rgba(140,60,255,0.25);

  /* Glowing animated border */
  border: 3px solid transparent;
  background-clip: padding-box;
  position: relative;
}
.hero-box::before {
  content: "";
  position: absolute;
  inset: -3px;
  background: linear-gradient(120deg,#a86bff,#ff36d2,#7b5bff,#a86bff);
  z-index: -1;
  border-radius: 25px;
  background-size: 300% 300%;
  animation: glow 4s ease infinite;
}
@keyframes glow {
  0% {background-position: 0% 50%;}
  50% {background-position: 100% 50%;}
  100% {background-position: 0% 50%;}
}

/* Title */
.hero-title {
  font-size: 52px;
  font-weight: 800;
  background: linear-gradient(90deg,#d995ff,#ffffff,#d995ff);
  -webkit-background-clip: text;
  color: transparent;
}

/* Subtitle */
.hero-sub {
  margin-top: 8px;
  font-size: 18px;
  color: #e4d9ff;
}

/* Typewriter text */
#role {
  font-weight: 700;
  font-size: 20px;
  color: #ffb2ff;
}

/* Buttons */
.btn {
  padding: 12px 26px;
  border-radius: 999px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: .2s;
  font-size: 15px;
}
.btn-primary {
  background: linear-gradient(90deg,#7d4bff,#c57aff);
  color: white;
}
.btn-primary:hover {transform: translateY(-4px);}

.btn-ghost {
  background: transparent;
  border: 1px solid rgba(255,255,255,0.25);
  color: #e7dbff;
}
.btn-ghost:hover {transform: translateY(-4px);}

/* Floating Chatbot Orb */
.chat-orb {
  position: fixed;
  right: 25px;
  bottom: 30px;
  width: 65px;
  height: 65px;
  background: linear-gradient(135deg,#b36bff,#ff64f9);
  border-radius: 50%;
  display:flex;
  align-items:center;
  justify-content:center;
  cursor:pointer;
  box-shadow: 0 0 30px rgba(255,100,255,0.7);
}
.chat-orb:hover {transform: scale(1.1);}
</style>

</head>
<body>

<div class="bg"></div>
<div class="stars"></div>

<!-- HERO -->
<div class="hero">
  <div class="hero-box">
    <div class="hero-title">ARYAN SHARMA</div>
    <div class="hero-sub">Welcome to my personal website!</div>
    <div class="hero-sub">I'm a <span id="role">developer</span></div>

    <div style="margin-top:20px;">
      <a href="/resume.pdf" download>
        <button class="btn btn-primary">Download Resume</button>
      </a>
      <a href="https://www.linkedin.com/in/aryan-sharma99999" target="_blank">
        <button class="btn btn-ghost">LinkedIn</button>
      </a>
      <a href="https://instagram.com/aryanxsharma26" target="_blank">
        <button class="btn btn-ghost">Instagram</button>
      </a>
    </div>

  </div>
</div>

<!-- Floating Bot -->
<div class="chat-orb">💬</div>

<script>
/* Typewriter Roles */
const roles = [
 "web developer",
 "tech enthusiast",
 "video editor",
 "designer",
 "writer",
 "learner"
];
let idx=0,pos=0,forward=true;
let roleSpan=document.getElementById("role");

function type(){
  let cur = roles[idx];
  if(forward){
     pos++;
     if(pos===cur.length){ forward=false; setTimeout(type,900); return;}
  } else {
     pos--;
     if(pos===0){ forward=true; idx=(idx+1)%roles.length; setTimeout(type,500); return;}
  }
  roleSpan.textContent = cur.slice(0,pos);
  setTimeout(type,70);
}
type();
</script>

</body>
</html>
"""

# FULLSCREEN HTML injection
components.html(html, height=6000, scrolling=False)

# -----------------------------------------------------------
# Now your Streamlit sections load BELOW the full theme
# -----------------------------------------------------------

st.markdown("## 📸 Gallery")
st.write("Your gallery will appear here when images are added to `/gallery` folder.")

st.markdown("## ✍️ Writings")
st.write("Anonymous writings will display here.")

st.markdown("## 📰 Blog Posts")
st.write("Your markdown blog posts will appear here.")

st.markdown("## 🧩 Projects")
st.write("- Chatbot Website\n- Portfolio Builder\n- AI Experiments")

