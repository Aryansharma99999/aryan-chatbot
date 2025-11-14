# app.py - Portfolio-style Streamlit app with hero, particles, two-column layout,
# glassy floating chatbot card, anonymous writings, admin, blog, and Telegram hooks.
import os
import re
import time
import json
import requests
from datetime import datetime
from markdown import markdown
import streamlit as st
import streamlit.components.v1 as components

# ----------------------------
# Basic config & constants
# ----------------------------
st.set_page_config(page_title="Aryan Sharma — Portfolio & Chatbot", layout="wide", initial_sidebar_state="collapsed")
BASE_DIR = os.path.dirname(__file__)
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")
MSG_FILE = os.path.join(BASE_DIR, "anonymous_messages.txt")
ADMIN_TOKEN = "admin-aryan"          # keep private - you already set this earlier
ADMIN_QUERY_PARAM = "admin"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = "8521726094"     # keeps your chat id; change if needed
HERO_NAME = "Aryan Sharma"
HERO_ROLE = "I'M a developer , writer , editor and a learner"

# ----------------------------
# Helper: send Telegram (optional)
# ----------------------------
def send_telegram_notification(text: str):
    token = TELEGRAM_BOT_TOKEN
    if not token:
        return False, "No TELEGRAM_BOT_TOKEN configured"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            return True, "sent"
        return False, f"HTTP {resp.status_code}: {resp.text}"
    except Exception as e:
        return False, str(e)

# ----------------------------
# Message storage utilities
# ----------------------------
def ensure_msg_file():
    if not os.path.exists(MSG_FILE):
        with open(MSG_FILE, "w", encoding="utf-8") as f:
            pass

def save_message(text):
    ensure_msg_file()
    msg = {"id": int(time.time() * 1000), "text": text, "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}
    with open(MSG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(msg, ensure_ascii=False) + "\n")
    # send telegram notification (best-effort)
    note = f"📨 New anonymous message:\n\n{text}\n\nID: {msg['id']}\nTime: {msg['timestamp']}"
    ok, info = send_telegram_notification(note)
    return msg, ok, info

def load_messages():
    ensure_msg_file()
    out = []
    with open(MSG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                out.append(json.loads(line))
            except:
                continue
    return out

def overwrite_messages(msgs):
    with open(MSG_FILE, "w", encoding="utf-8") as f:
        for m in msgs:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

# ----------------------------
# Blog utilities
# ----------------------------
def get_post_data(slug):
    file_path = os.path.join(POSTS_DIR, f"{slug}.md")
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    metadata_match = re.match(r'---\n(.*?)\n---', content, re.DOTALL)
    metadata = {}
    body = content
    if metadata_match:
        meta = metadata_match.group(1)
        for line in meta.split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                metadata[k.strip()] = v.strip()
        body = content[metadata_match.end():].strip()
    html = markdown(body)
    return {
        "slug": slug,
        "title": metadata.get("title", "Untitled"),
        "date": metadata.get("date", "N/A"),
        "author": metadata.get("author", "N/A"),
        "summary": metadata.get("summary", ""),
        "html": html
    }

def get_all_posts():
    if not os.path.exists(POSTS_DIR):
        return []
    files = [f for f in os.listdir(POSTS_DIR) if f.endswith(".md")]
    posts = []
    for f in files:
        slug = f.replace(".md", "")
        data = get_post_data(slug)
        if data:
            posts.append(data)
    return posts

# ----------------------------
# CSS + hero HTML + particles
# ----------------------------
def inject_styles_and_hero():
    # CSS and hero HTML (gradient, container, fonts, buttons, floating chatbot)
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

    :root {{
      --bg1: #ff77e9;
      --bg2: #8a6aff;
      --card-dark: #2b2230; /* dark purple container */
      --card-accent: rgba(255,83,214,0.12);
      --neon-pink: #ff53d6;
      --neon-blue: #8b8bff;
      --cyan: #00d4ff;
      --muted: rgba(255,255,255,0.82);
    }}

    html, body, .stApp {{
      height: 100%;
      margin: 0;
      font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
      background: linear-gradient(135deg, var(--bg1) 0%, var(--bg2) 100%);
      color: white;
    }}

    /* center content and hero container */
    .hero-wrap {{
      display:flex;
      justify-content:center;
      padding:60px 20px 40px 20px;
    }}

    .hero-card {{
      width: min(1100px, 86%);
      background: linear-gradient(180deg, rgba(15,10,20,0.98), rgba(22,16,26,0.98));
      border-radius: 28px;
      padding: 64px 64px 96px 64px;
      box-shadow: 0 30px 80px rgba(0,0,0,0.45);
      position: relative;
      overflow: visible;
    }}

    .hero-title {{
      font-weight:800;
      font-size:48px;
      letter-spacing: -1px;
      color: var(--neon-pink);
      text-align:center;
      margin: 0 0 12px 0;
    }}
    .hero-role {{
      color: var(--neon-blue);
      font-weight:700;
      text-align:center;
      margin-bottom: 20px;
      font-size:20px;
    }}
    .hero-desc {{
      color: rgba(255,255,255,0.85);
      text-align:center;
      max-width: 760px;
      margin: 0 auto 28px auto;
      line-height:1.6;
      font-size:16px;
    }}

    /* CTA buttons */
    .cta-row {{
      display:flex;
      justify-content:center;
      gap:16px;
      margin-bottom: 28px;
      align-items:center;
    }}
    .btn-primary {{
      background: linear-gradient(90deg, rgba(255,83,214,1), rgba(139,139,255,1));
      color:white;
      border:none;
      padding:12px 18px;
      border-radius:28px;
      font-weight:700;
      box-shadow: 0 16px 40px rgba(137,78,255,0.18);
      cursor:pointer;
      text-decoration:none;
    }}
    .btn-ghost {{
      background: transparent;
      color: var(--neon-blue);
      border: 2px solid rgba(139,139,255,0.18);
      padding:10px 18px;
      border-radius:28px;
      font-weight:700;
      text-decoration:none;
    }}

    /* social icons row */
    .social-row {{ display:flex; justify-content:center; gap:14px; margin-top:18px; }}
    .social-btn {{
      width:48px;height:48px;border-radius:50%;display:flex;align-items:center;justify-content:center;
      background: rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.04);
      box-shadow: 0 12px 30px rgba(0,0,0,0.45);
      color: var(--neon-blue);
      font-weight:700;
      cursor:pointer;
      text-decoration:none;
    }}

    /* floating chatbot card (right) */
    .floating-chat {{
      position: absolute;
      right: -40px;
      top: 200px;
      width: 360px;
      background: linear-gradient(180deg, #111317, #1b1b22);
      border-radius: 18px;
      padding: 16px;
      box-shadow: 0 24px 60px rgba(8,8,20,0.6);
      border: 1px solid rgba(255,255,255,0.04);
    }}
    .floating-chat h4 {{ color: var(--cyan); margin: 6px 0 8px 0; font-weight:800; font-size:18px; }}
    .floating-chat .bubble {{ background: rgba(255,255,255,0.04); padding:10px;border-radius:8px;color:#dbe8ff; margin-bottom:8px; }}
    .floating-chat .input-row {{ display:flex; gap:8px; margin-top:8px; }}
    .floating-chat input {{ flex:1; background:#0f1114; border-radius:8px; border:1px solid rgba(255,255,255,0.04); color:#e6eefc; padding:8px; }}
    .floating-chat button {{ background: var(--cyan); color:#001018; border-radius:8px; border:none; padding:8px 12px; font-weight:700; cursor:pointer; }}

    /* two-column area below hero */
    .two-col {{ display:flex; gap:28px; margin-top:32px; }}
    .left-col {{ width:320px; }}
    .right-col {{ flex:1; }}

    .card {{
      background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));
      border-radius:12px; padding:12px; margin-bottom:12px; border:1px solid rgba(255,255,255,0.03);
    }}

    /* small screens */
    @media (max-width: 980px) {{
      .floating-chat {{ display:none; }}
      .hero-card {{ padding:30px; }}
      .hero-title {{ font-size:36px; }}
      .two-col {{ flex-direction:column; }}
      .left-col {{ width:100%; }}
    }}
    </style>
    """

    # Build HTML: hero container with tsparticles canvas for animated particles
    html = f"""
    {css}
    <!-- tsparticles for animated particles -->
    <script src="https://cdn.jsdelivr.net/npm/tsparticles@2.3.4/tsparticles.bundle.min.js"></script>
    <div class="hero-wrap">
      <div class="hero-card" id="hero-card">
        <div id="tsparticles" style="position:absolute; inset:0; z-index:0; border-radius:28px;"></div>
        <div style="position:relative; z-index:2;">
          <h1 class="hero-title">{HERO_NAME}</h1>
          <div class="hero-role">{HERO_ROLE}</div>
          <div class="hero-desc">Welcome to my personal website — explore my projects, read my thoughts, or ask me anything using the chat widget.</div>
          <div class="cta-row">
            <a class="btn-primary" href="#" onclick="window.open('/resume.pdf','_blank')">Download Resume</a>
            <a class="btn-ghost" href="#contact">Get In Touch</a>
          </div>
          <div class="social-row">
            <a class="social-btn" href="https://github.com/aryansharma99999" target="_blank">GH</a>
            <a class="social-btn" href="https://instagram.com/aryanxsharma26" target="_blank">IG</a>
            <a class="social-btn" href="mailto:aryanxsharma26@gmail.com">✉️</a>
          </div>
        </div>

        <!-- floating chat card -->
        <div class="floating-chat" id="floating-chat">
          <h4>Aryan's AI Chatbot</h4>
          <div class="bubble">Hi! Ask me questions about Aryan.</div>
          <div class="input-row">
            <input id="floating_input" placeholder="Type your question..." />
            <button id="floating_send">Send</button>
          </div>
          <div style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:8px">Anonymous messages will appear in admin.</div>
        </div>

      </div>
    </div>

    <script>
      /* tsparticles config - subtle floating dots */
      tsParticles.load("tsparticles", {{
        fullScreen: {{ enable: false }},
        particles: {{
          number: {{ value: 30 }},
          color: {{ value: ["#ff6ad1","#8b8bff","#00d4ff"] }},
          shape: {{ type: "circle" }},
          opacity: {{ value: 0.6 }},
          size: {{ value: {{ min: 1, max: 6 }} }},
          links: {{ enable: false }},
          move: {{ enable: true, speed: 0.6, direction: "none", outModes: "out" }}
        }},
        detectRetina: true
      }});
      // Floating chat send behaviour: send to server via fetch to /.?no-op - we will intercept in Streamlit with query param
      document.getElementById('floating_send').addEventListener('click', function(){{
        const v = document.getElementById('floating_input').value;
        if(!v||!v.trim()){{ alert('Write a question'); return; }}
        // send by opening a new tab with query parameters - Streamlit will see query params if user clicks the link
        const params = new URLSearchParams();
        params.set('anon_q', v);
        // open the app root with query to cause Streamlit to read it (user stays on same app, this opens overlay)
        window.open(window.location.pathname + "?" + params.toString(), "_self");
      }});
    </script>
    """

    # Render with components so scripts run
    components.html(html, height=520, scrolling=False)

# ----------------------------
# Render right-hand Chatbot and Blog
# ----------------------------
def render_chatbot_area():
    st.markdown("<div class='card'><strong>Chatbot</strong></div>", unsafe_allow_html=True)
    # simple Q&A dictionary
    qbank = {
        "what is your name": f"My name is {HERO_NAME}.",
        "where are you from": "I am from India.",
        "what do you do": "I make things with code and words."
    }
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    # show conversation limited height
    st.write("")  # spacer
    for m in st.session_state.chat_messages[-10:]:
        if m["role"] == "user":
            st.markdown(f"<div style='background:#0f1724;padding:10px;border-radius:8px;margin-bottom:6px;color:#cfe8ff'>{m['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background:#f7f6ff;color:#0b0f14;padding:10px;border-radius:8px;margin-bottom:6px'>{m['content']}</div>", unsafe_allow_html=True)
    # input
    user_q = st.text_input("Ask me a question...", key="chat_input_box")
    if user_q:
        st.session_state.chat_messages.append({"role":"user","content":user_q})
        answer = qbank.get(user_q.lower(), "Sorry! I don't have an answer for that.")
        # typing effect simplified: append answer
        st.session_state.chat_messages.append({"role":"bot","content":answer})
        st.experimental_rerun()

def render_blog_area():
    st.markdown("<div class='card'><strong>Blog</strong></div>", unsafe_allow_html=True)
    posts = get_all_posts()
    if not posts:
        st.info("No blog posts found. Add markdown files inside blog_posts/")
        return
    # render titles and summaries
    for p in posts:
        st.markdown(f"<div class='card'><div style='font-weight:700'>{p['title']}</div><div style='color:rgba(255,255,255,0.6)'>{p['date']}</div><p>{p['summary']}</p></div>", unsafe_allow_html=True)
        if st.button("Read", key=f"read_{p['slug']}"):
            st.session_state.selected_post = p['slug']
            st.experimental_rerun()
    # selected post view
    if st.session_state.get("selected_post"):
        slug = st.session_state.get("selected_post")
        post = get_post_data(slug)
        if post:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='color:var(--neon-blue)'>{post['title']}</h2>", unsafe_allow_html=True)
            st.markdown(post['html'], unsafe_allow_html=True)
            if st.button("Back to list"):
                st.session_state.selected_post = None
                st.experimental_rerun()

# ----------------------------
# Left column: Writings (anonymous), Anonymous Box, Admin
# ----------------------------
def render_left_column():
    st.markdown("<div class='card'><strong>Writings (anonymous)</strong></div>", unsafe_allow_html=True)
    msgs = load_messages()
    if not msgs:
        st.markdown("<div class='card'><div style='color:rgba(255,255,255,0.7)'>No writings yet. Visitors can add anonymous messages below.</div></div>", unsafe_allow_html=True)
    else:
        for m in sorted(msgs, key=lambda x: x.get("id", 0), reverse=True)[:6]:
            txt = m.get("text","")
            ts = m.get("timestamp","")
            st.markdown(f"<div class='card'><div style='font-weight:600'>{txt[:120]}{'...' if len(txt)>120 else ''}</div><div style='color:rgba(255,255,255,0.6);margin-top:6px'>{ts}</div></div>", unsafe_allow_html=True)

    # Anonymous box
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='card'><strong>Send an anonymous message</strong></div>", unsafe_allow_html=True)
    with st.form("anon_form_left", clear_on_submit=True):
        anon_text = st.text_area("Your message", max_chars=1500, placeholder="Share a thought, feedback, or question...")
        send = st.form_submit_button("Send anonymously")
    if send:
        if not anon_text or not anon_text.strip():
            st.warning("Please write a message before sending.")
        else:
            saved, ok, info = save_message(anon_text.strip())
            if ok:
                st.success("Message saved and notification sent.")
            else:
                st.success("Message saved. Notification not sent: " + str(info))

    # Admin panel
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='card'><strong>Admin</strong></div>", unsafe_allow_html=True)
    qp = st.experimental_get_query_params()
    unlocked = False
    if ADMIN_QUERY_PARAM in qp and qp.get(ADMIN_QUERY_PARAM, [""])[0] == ADMIN_TOKEN:
        st.session_state._admin_unlocked = True
    if st.session_state.get("_admin_unlocked", False):
        unlocked = True

    with st.expander("Admin controls"):
        if not unlocked:
            entered = st.text_input("Enter admin token", type="password", key="adm_inp")
            if st.button("Unlock admin", key="adm_unlock_btn"):
                if entered.strip() == ADMIN_TOKEN:
                    st.session_state._admin_unlocked = True
                    st.experimental_set_query_params(**{ADMIN_QUERY_PARAM: ADMIN_TOKEN})
                    st.experimental_rerun()
                else:
                    st.error("Invalid token")
        else:
            st.success("Admin unlocked")
            messages = load_messages()
            st.markdown(f"<div style='color:rgba(255,255,255,0.7)'>Total messages: {len(messages)}</div>", unsafe_allow_html=True)
            for m in sorted(messages, key=lambda x: x.get("id", 0), reverse=True):
                with st.expander(f"ID {m.get('id')} • {m.get('timestamp')}"):
                    st.write(m.get("text"))
                    if st.button("Delete", key=f"del_{m.get('id')}"):
                        new = [x for x in messages if x.get("id") != m.get("id")]
                        overwrite_messages(new)
                        st.success("Deleted")
                        st.experimental_rerun()
            if st.button("Clear all messages", key="clear_all_msgs"):
                overwrite_messages([])
                st.success("Cleared")
                st.experimental_rerun()

# ----------------------------
# Main: render everything
# ----------------------------
def main():
    # handle incoming query param from the floating chat JS (when user clicked send)
    qp = st.experimental_get_query_params()
    if "anon_q" in qp:
        # write anon message and remove query param by reloading the page (safer)
        q = qp.get("anon_q", [""])[0]
        if q and q.strip():
            save_message(q.strip())
            # remove the param by setting empty params and rerun
            st.experimental_set_query_params()
            st.success("Your anonymous message was saved. Thank you!")
    # render hero + particles
    inject_styles_and_hero()

    # two-column area below hero
    st.markdown("<div style='display:flex; justify-content:center; padding-top:8px'>", unsafe_allow_html=True)
    st.markdown("<div style='width:min(1100px, 86%)'>", unsafe_allow_html=True)
    st.markdown("<div class='two-col'>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2.2], gap="large")
    with col1:
        render_left_column()
    with col2:
        # show right column: small intro card then tabs for Chatbot & Blog
        st.markdown("<div class='card'><strong>Explore</strong></div>", unsafe_allow_html=True)
        tabs = st.tabs(["Chatbot","Blog"])
        with tabs[0]:
            render_chatbot_area()
        with tabs[1]:
            render_blog_area()

    st.markdown("</div></div></div>", unsafe_allow_html=True)

    # bottom spacing
    st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()


