import streamlit as st
import json
import time

st.set_page_config(page_title="Aryan Sharma", layout="wide")

# ------------------ CSS ------------------

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
    background: radial-gradient(circle at bottom, #2b0a45, #0a0217 60%);
    color: white;
    overflow-x: hidden;
}

# -------- STARFIELD BACKGROUND --------

body::before {
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100vw;
    height: 100vh;
    background-image:
        radial-gradient(2px 2px at random()*100% random()*100%, white 70%, transparent 0),
        radial-gradient(2px 2px at random()*100% random()*100%, white 70%, transparent 0),
        radial-gradient(1px 1px at random()*100% random()*100%, white 70%, transparent 0);
    opacity: 0.25;
    z-index: -2;
}

# --------- MAIN HERO PANEL ---------
.hero-box {
    width: 80%;
    margin: auto;
    padding: 60px;
    margin-top: 130px;
    border-radius: 25px;

    background: rgba(10, 0, 30, 0.55); /* DARK but visible */
    border: 3px solid #a020f0;
    box-shadow: 0 0 25px #a020f0;
}

.hero-title {
    font-size: 52px;
    font-weight: 700;
    color: #f4c2ff;
}

.hero-sub {
    font-size: 22px;
    color: #caaaff;
}

a {
    color: #d9c7ff;
    text-decoration: none !important;
}
a:hover {
    color: white;
}

# ---------- FLOATING LEFT ICONS ----------
.left-icons {
    position: fixed;
    top: 45%;
    left: 15px;
    z-index: 1000;
}

.float-icon {
    background: rgba(255,255,255,0.08);
    padding: 18px;
    border-radius: 50%;
    margin-top: 18px;
    width: 55px;
    text-align: center;
    border: 2px solid #a020f0;
    transition: 0.3s;
}
.float-icon:hover {
    background: rgba(255,255,255,0.2);
    transform: scale(1.1);
}

# ---------- FLOATING CHATBOT ----------
.chatbot-button {
    position: fixed;
    bottom: 30px;
    right: 30px;
    padding: 16px 30px;
    border-radius: 25px;
    background: linear-gradient(90deg, #a020f0, #6500b5);
    border: none;
    color: white;
    font-size: 18px;
    box-shadow: 0 0 18px #a020f0;
    cursor: pointer;
}

</style>
""", unsafe_allow_html=True)

# ---------------- FLOATING LEFT ICONS ----------------
st.markdown("""
<div class="left-icons">
    <a href="#photos"><div class="float-icon">📷</div></a>
    <a href="#writings"><div class="float-icon">✍️</div></a>
</div>
""", unsafe_allow_html=True)

# ---------------- HERO SECTION ----------------
st.markdown("""
<div class="hero-box">

    <div class="hero-title">Aryan Sharma</div>
    <div class="hero-sub">I'm a developer, writer, editor & learner.</div>

    <br>

    <p style="font-size:18px;color:#ddd;">
        Welcome to my personal website — explore projects, photos, writings, and chat with my AI assistant.
    </p>

    <br>

    <a href="https://github.com/aryanxsharma26">
        <button style="padding:10px 20px;border-radius:10px;border:none;margin-right:10px;">GH</button>
    </a>

    <a href="https://instagram.com/Aryansharma99999">
        <button style="padding:10px 20px;border-radius:10px;border:none;">IG</button>
    </a>

</div>
""", unsafe_allow_html=True)

# ---------------- FLOATING CHATBOT ----------------
st.markdown("""
<button class="chatbot-button">Ask Aryan</button>
""", unsafe_allow_html=True)
