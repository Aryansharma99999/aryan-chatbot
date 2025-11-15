import streamlit as st
import time

st.set_page_config(page_title="Aryan Sharma", layout="wide")

# -----------------------------------------------------------
#                     CUSTOM CSS + STARFIELD
# -----------------------------------------------------------

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
    background: radial-gradient(circle at bottom, #2b0a45, #0a0217 60%);
    color: white !important;
    overflow-x: hidden;
}

/* ---------- STARFIELD BACKGROUND ----------- */
.stars {
    position: fixed;
    width: 100%;
    height: 100%;
    top: 0; left: 0;
    z-index: -1;
    background: transparent;
    pointer-events: none;
}

.star {
    position: absolute;
    width: 2px;
    height: 2px;
    background: white;
    opacity: 0.7;
    border-radius: 50%;
    animation: float 6s linear infinite;
}

@keyframes float {
    0% { transform: translateY(0px); opacity: 0.8; }
    100% { transform: translateY(-40px); opacity: 0.2; }
}

/* ---------- Floating left buttons ----------- */
.float-btn {
    position: fixed;
    left: 30px;
    width: 55px;
    height: 55px;
    border-radius: 50%;
    border: 3px solid #b24cff;
    backdrop-filter: blur(6px);
    background: rgba(90, 0, 140, 0.4);
    display:flex;
    align-items:center;
    justify-content:center;
    cursor:pointer;
    z-index: 30;
    transition: 0.2s;
}

.float-btn:hover { transform: scale(1.1); }

/* Position of icons */
#photos-btn { top: 150px; }
#writings-btn { top: 230px; }

/* ---------- Floating Chatbot Button ----------- */
#chatbot-btn {
    position: fixed;
    bottom: 30px;
    left: 30px;
    padding: 10px 20px;
    border-radius: 12px;
    background: rgba(150, 0, 255, 0.4);
    border: 2px solid #b24cff;
    backdrop-filter: blur(6px);
    color: white;
    cursor: pointer;
    font-weight: 600;
    transition: 0.2s;
    z-index: 40;
}
#chatbot-btn:hover { transform: scale(1.05); }

/* ---------- HERO CARD ----------- */
.hero-box {
    width: 90%;
    margin: auto;
    margin-top: 120px;
    padding: 60px;
    border-radius: 22px;
    background: rgba(20, 0, 40, 0.65);
    border: 3px solid #b24cff;
    backdrop-filter: blur(10px);
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
    margin-top: 18px;
    color: #ddd;
}

/* Buttons */
.btn {
    padding: 10px 20px;
    border-radius: 10px;
    border: none;
    margin-right: 10px;
    cursor: pointer;
    background: #b24cff;
    color: white;
    font-weight: 600;
}
.btn:hover { background: #d07cff; }

</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
#                     STARFIELD GENERATOR
# -----------------------------------------------------------

star_html = '<div class="stars">'
import random
for i in range(120):
    x = random.randint(0, 100)
    y = random.randint(0, 100)
    delay = random.random() * 3
    star_html += f'<div class="star" style="top:{y}%; left:{x}%; animation-delay:{delay}s;"></div>'
star_html += "</div>"

st.markdown(star_html, unsafe_allow_html=True)

# -----------------------------------------------------------
#                 FLOATING ICON BUTTONS (LEFT)
# -----------------------------------------------------------

st.markdown("""
<div id="photos-btn" class="float-btn">
    <a href="#photos-section">
        <img src="https://img.icons8.com/ios-filled/50/ffffff/camera.png" width="28">
    </a>
</div>

<div id="writings-btn" class="float-btn">
    <a href="#writings-section">
        <img src="https://img.icons8.com/ios-filled/50/ffffff/ballpoint-pen.png" width="28">
    </a>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
#                 FLOATING CHATBOT BUTTON (BOTTOM LEFT)
# -----------------------------------------------------------

st.markdown("""
<a href="#chatbot-section">
    <div id="chatbot-btn">Ask Aryan</div>
</a>
""", unsafe_allow_html=True)


# -----------------------------------------------------------
#                         HERO SECTION
# -----------------------------------------------------------

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
    <button class="btn">GH</button>
</a>

<a href="https://instagram.com/Aryansharma99999">
    <button class="btn">IG</button>
</a>

""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------
#                Placeholder Sections Below
# -----------------------------------------------------------

st.markdown("<br><br><h2 id='photos-section'>📸 Photos Section</h2>", unsafe_allow_html=True)
st.write("Your photos will appear here...")

st.markdown("<br><br><h2 id='writings-section'>✍️ Writings Section</h2>", unsafe_allow_html=True)
st.write("Your writings will appear here...")

st.markdown("<br><br><h2 id='chatbot-section'>🤖 Chatbot</h2>", unsafe_allow_html=True)
st.write("Your chatbot code will appear here...")

