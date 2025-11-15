import streamlit as st
import time

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Aryan Sharma — Portfolio", layout="wide")

# ---- CUSTOM CSS ----
st.markdown("""
<style>

body {
    background: #0d0017;
}

/* HERO BOX */
.hero {
    width: 100%;
    padding: 80px 20px;
    text-align: center;
    border-radius: 20px;
    background: linear-gradient(120deg, #6d25ff40, #9f4dff40, #d9a7ff40);
    border: 2px solid #bb77ff40;
    backdrop-filter: blur(10px);
    animation: glow 6s infinite linear;
    margin-bottom: 40px;
}

@keyframes glow {
    0% { box-shadow: 0 0 20px #8b3dff; }
    50% { box-shadow: 0 0 40px #b96dff; }
    100% { box-shadow: 0 0 20px #8b3dff; }
}

.hero h1 {
    font-size: 52px;
    font-weight: 700;
    color: white;
}

/* Typing Text */
#typing {
    font-size: 22px;
    font-weight: 600;
    color: #e3c9ff;
    height: 30px;
}

/* About Box */
.about-box {
    padding: 25px;
    border-radius: 15px;
    background: #ffffff09;
    border: 1px solid #ffffff15;
    backdrop-filter: blur(8px);
    text-align: center;
}

/* Project Cards */
.card {
    padding: 20px;
    background: #ffffff08;
    border-radius: 16px;
    border: 1px solid #ffffff12;
    backdrop-filter: blur(7px);
    transition: 0.3s;
}

.card:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 32px #a86cff40;
}

</style>
""", unsafe_allow_html=True)

# ---- HERO SECTION ----
st.markdown("<div class='hero'><h1>Aryan Sharma</h1>", unsafe_allow_html=True)
typing_placeholder = st.empty()
st.markdown("</div>", unsafe_allow_html=True)

# ---- TYPING ANIMATION ----
roles = [
    "I'm a Web Designer",
    "I'm a Problem Solver",
    "I'm a Tech Enthusiast",
    "I'm a Developer",
    "I'm a Writer"
]

for word in roles:
    typing_placeholder.markdown(f"<div id='typing'>{word}</div>", unsafe_allow_html=True)
    time.sleep(1.8)

# ---- ABOUT ME ----
st.markdown("### 🧑‍💻 About Me")
st.markdown("""
<div class='about-box'>
Hi, I'm <b>Aryan Sharma</b>, currently pursuing a Bachelor's Degree.<br><br>
I'm passionate about coding, learning, and developing new things.<br>
This site showcases my work and lets you chat with my AI assistant to learn more about me.
</div>
""", unsafe_allow_html=True)

# ---- PROJECTS ----
st.markdown("## 🚀 Projects")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class='card'>
        <h3>Chatbot Website</h3>
        <p>A chatbot-enabled modern website.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='card'>
        <h3>Portfolio Builder</h3>
        <p>A tool that creates portfolios instantly.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='card'>
        <h3>AI Experiments</h3>
        <p>Mini AI projects exploring automation & creativity.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br><center>© 2025 Aryan Sharma</center>", unsafe_allow_html=True)
