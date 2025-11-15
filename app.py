import streamlit as st
import random

st.set_page_config(page_title="Aryan Sharma", layout="wide")


# ============================
#          FIXED CSS
# ============================

st.markdown("""
<style>

html, body {
    margin: 0;
    padding: 0;
    background: transparent !important;
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background: radial-gradient(circle at bottom, #2b0a45, #0a0217 70%) !important;
    color: white !important;
    overflow-x: hidden !important;
}

/* Small floating stars */
.stars {
    position: fixed;
    top: 0; left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
    pointer-events: none;
}

.star {
    position: absolute;
    width: 2px;
    height: 2px;
    background: #ffffff;
    opacity: 0.7;
    border-radius: 50%;
    animation: floatUp 6s linear infinite;
}

@keyframes floatUp {
    from { transform: translateY(20px); opacity: 0.7; }
    to   { transform: translateY(-40px); opacity: 0.2; }
}

/* Floating Buttons Left */
.float-btn {
    position: fixed;
    left: 30px;
    width: 55px;
    height: 55px;
    border-radius: 50%;
    border: 3px solid #b24cff;
    background: rgba(90, 0, 140, 0.35);
    backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    z-index: 30;
    transition: 0.2s;
}
.float-btn:hover { transform: scale(1.12); }

#photos-btn { top: 140px; }
#writings-btn { top: 220px; }

/* Chatbot Floating Button */
#chatbot-btn {
    position: fixed;
    bottom: 30px;
    left: 30px;
    padding: 12px 22px;
    background: rgba(150, 0, 255, 0.45);
    border: 2px solid #c46aff;
    color: white;
    border-radius: 12px;
    font-weight: 600;
    backdrop-filter: blur(8px);
    cursor: pointer;
    z-index: 40;
}
#chatbot-btn:hover { transform: scale(1.05); }

/* Hero Box */
.hero-box {
    width: 90%;
    margin: auto;
    margin-top: 120px;
    padding: 55px;
    border-radius: 22px;
    background: rgba(20, 0, 40, 0.65);
    border: 3px solid #b24cff;
    backdrop-filter: blur(14px);
}

.hero-title {
    font-size: 52px;
    font-weight: 700;
    color: #f8c8ff;
}

.hero-sub {
    font-size: 22px;
    margin-top: 10px;
    color: #d8b8ff;
}

.hero-text {
    font-size: 18px;
    margin-top: 20px;
    color: #eee;
}

.btn {
    padding: 10px 20px;
    border-radius: 10px;
    border: none;
    background: #b24cff;
    color: white;
    font-weight: 600;
    margin-right: 10px;
    cursor: pointer;
}

.btn:hover { background: #d07cff; }

</style>
""", unsafe_allow_html=True)


# ============================
#     STARFIELD GENERATOR
# ============================
star_html = '<div class="stars">'
for i in range(140):
    x = random.randint(0,100)
    y = random.randint(0,100)
    delay = random.random()*3
    star_html += f'<div class="star" style="left:{x}%; top:{y}%; animation-delay:{delay}s;"></div>'
star_html += '</div>'
st.markdown(star_html, unsafe_allow_html=True)


# ============================
#     FLOATING BUTTONS
# ============================
st.markdown("""
<div id="photos-btn" class="float-btn">
    <a href="#photos-section">
    <img src="https://img.icons8.com/ios-filled/50/ffffff/camera.png" width="26">
    </a>
</div>

<div id="writings-btn" class="float-btn">
    <a href="#writings-section">
    <img src="https://img.icons8.com/ios-filled/50/ffffff/ballpoint-pen.png" width="26">
    </a>
</div>

<a href="#chatbot-section">
    <div id="chatbot-btn">Ask Aryan</div>
</a>
""", unsafe_allow_html=True)


# ============================
#         HERO SECTION
# ============================

st.markdown('<div class="hero-box">', unsafe_allow_html=True)

st.markdown("""
<div class="hero-title">Aryan Sharma</div>
<div class="hero-sub">I'm a developer, writer, editor & learner.</div>

<p class="hero-text">
Welcome to my personal website — explore projects, photos, writings,
and chat with my AI assistant.
</p>

<br>

<a href="https://github.com/aryanxsharma26">
<button class="btn">GH</button></a>

<a href="https://instagram.com/Aryansharma99999">
<button class="btn">IG</button></a>

""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# ============================
#   Placeholder sections
# ============================

st.markdown("<h2 id='photos-section'>📸 Photos Section</h2>", unsafe_allow_html=True)
st.write("Your photos will appear here...")

st.markdown("<h2 id='writings-section'>✍️ Writings Section</h2>", unsafe_allow_html=True)
st.write("Your writings will appear here...")

st.markdown("<h2 id='chatbot-section'>🤖 Chatbot</h2>", unsafe_allow_html=True)
st.write("Chatbot UI coming next...")

