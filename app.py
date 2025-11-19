import streamlit as st
import os, re, time
from markdown import markdown
import streamlit.components.v1 as components

st.set_page_config(page_title="Aryan Sharma", layout="wide")

# ---------------- REMOVE ALL STREAMLIT UI ----------------
st.markdown("""
<style>
#MainMenu, header, footer {visibility: hidden;}
.stApp {padding: 0; margin: 0; background: transparent;}
.block-container {padding-top: 0 !important;}
html, body {overflow-x: hidden; background: transparent;}
</style>
""", unsafe_allow_html=True)

# ---------------- HERO HTML ----------------
hero_html = """
<div class="bg"></div>
<div class="stars"></div>

<style>

body {
  margin: 0;
  font-family: Poppins, sans-serif;
}

/* Galaxy Background */
.bg {
  position: fixed;
  inset: 0;
  background: radial-gradient(circle at 50% 0%, #3a007a 0%, #0b001a 70%);
  z-index: -2;
}

/* Stars layer */
.stars {
  position: fixed;
  inset: 0;
  background-image: radial-gradient(white 1px, transparent 1px);
  background-size: 3px 3px;
  opacity: 0.12;
  animation: twinkle 6s infinite linear;
  z-index: -1;
}

@keyframes twinkle {
  0% {opacity: 0.16;}
  50% {opacity: 0.05;}
  100% {opacity: 0.16;}
}

/* HERO SECTION */
.hero {
  height: 100vh;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.hero-box {
  width: 85%;
  max-width: 900px;
  padding: 50px;
  text-align: center;
  background: rgba(255,255,255,0.04);
  backdrop-filter: blur(15px);
  border-radius: 25px;
  border: 2px solid rgba(255,255,255,0.12);
  position: relative;
  box-shadow: 0 0 35px rgba(200,100,255,0.25);
}

/* Animated glowing edge */
.hero-box::before {
  content: "";
  position: absolute;
  inset: -3px;
  border-radius: 25px;
  background: linear-gradient(120deg,#b06bff,#ff39d2,#7d5bff,#b06bff);
  background-size: 300% 300%;
  animation: glow 4s infinite;
  z-index: -1;
}

@keyframes glow {
  0% {background-position: 0% 50%;}
  50% {background-position: 100% 50%;}
  100% {background-position: 0% 50%;}
}

.hero-title {
  font-size: 50px;
  font-weight: 800;
  background: linear-gradient(90deg,#d995ff,#ffffff,#d995ff);
  -webkit-background-clip: text;
  color: transparent;
}

.hero-sub {
  font-size: 18px;
  color: #e7dfff;
  margin-top: 8px;
}

#role {
  color: #ffb8ff;
  font-weight: 700;
  font-size: 20px;
}

/* Buttons */
.btn {
  padding: 12px 25px;
  border-radius: 50px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  font-size: 16px;
  margin: 5px;
}
.btn-primary {
  background: linear-gradient(90deg,#7d4bff,#d57aff);
  color: white;
}
.btn-outline {
  background: transparent;
  border: 1px solid rgba(255,255,255,0.25);
  color: #e7dbff;
}

.btn:hover {transform: translateY(-4px);}

/* Chat orb */
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
  box-shadow: 0 0 25px rgba(255,100,255,0.6);
  font-size: 28px;
}

</style>

<div class="hero">
  <div class="hero-box">
    <div class="hero-title">ARYAN SHARMA</div>
    <div class="hero-sub">Welcome to my personal website!</div>
    <div class="hero-sub">I'm a <span id="role"></span></div>
    
    <div style="margin-top: 20px;">
      <a href="/resume.pdf" download><button class="btn btn-primary">Download Resume</button></a>
      <a href="https://www.linkedin.com/in/aryan-sharma99999" target="_blank"><button class="btn btn-outline">LinkedIn</button></a>
      <a href="https://instagram.com/aryanxsharma26" target="_blank"><button class="btn btn-outline">Instagram</button></a>
    </div>
  </div>
</div>

<div class="chat-orb">💬</div>

<script>
/* TYPEWRITER ROLES */
const roles = ["web developer","tech enthusiast","video editor","writer","designer","learner"];
let i = 0, j = 0, forward = true;

function type() {
  const role = roles[i];
  if (forward) {
    j++;
    if (j === role.length) { forward = false; setTimeout(type, 900); return; }
  } else {
    j--;
    if (j === 0) { forward = true; i = (i + 1) % roles.length; setTimeout(type, 400); return; }
  }
  document.getElementById("role").textContent = role.slice(0, j);
  setTimeout(type, 70);
}
type();
</script>
"""

components.html(hero_html, height=900, scrolling=False)

# ------------------- CONTENT BELOW HERO -------------------
st.markdown("## 📸 Photos (Gallery)")
st.write("Add images to the `gallery` folder.")

st.markdown("## ✍️ Anonymous Writings")
st.write("User-submitted anonymous thoughts appear here.")

st.markdown("## 📰 Blog Posts")
st.write("Markdown posts from `blog_posts/` folder will appear here.")

st.markdown("## 🧩 Projects")
st.write("""
- Chatbot Website  
- Portfolio Builder  
- AI Experiments  
""")

st.markdown("## 🔗 Socials")
st.write("[LinkedIn](https://www.linkedin.com/in/aryan-sharma99999)  |  [Instagram](https://instagram.com/aryanxsharma26)")
