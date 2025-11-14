# app.py - Professional two-column layout with glassmorphism, animations, icons
import os
import re
import time
import json
import requests
from datetime import datetime
from markdown import markdown
import streamlit as st

# ----------------------------
# Basic config & constants
# ----------------------------
st.set_page_config(page_title="Aryan Chatbot & Blog", layout="wide", initial_sidebar_state="collapsed")
BASE_DIR = os.path.dirname(__file__)
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")
MSG_FILE = os.path.join(BASE_DIR, "anonymous_messages.txt")
ADMIN_TOKEN = "admin-aryan"  # keep private; you know this
ADMIN_QUERY_PARAM = "admin"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = "8521726094"  # your chat id
INSTAGRAM_USERNAME = "aryanxsharma26"

# ----------------------------
# CSS: Glassmorphism + Animations + Icons
# ----------------------------
def inject_css():
    css = r"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

    :root{
      --bg-dark: #071022;
      --glass: rgba(255,255,255,0.04);
      --glass-2: rgba(255,255,255,0.03);
      --accent: linear-gradient(90deg,#7A58FF,#58C8FF);
      --muted: rgba(255,255,255,0.7);
    }

    /* App background */
    .stApp {
      font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, Arial;
      background:
        radial-gradient(800px 400px at 5% 10%, rgba(122,88,255,0.08), transparent),
        radial-gradient(600px 300px at 90% 90%, rgba(88,200,255,0.04), transparent),
        var(--bg-dark);
      color: #e8eef8;
      min-height:100vh;
      padding-top:18px;
    }

    /* Columns container */
    .two-col {
      display: flex;
      gap: 28px;
      align-items: flex-start;
    }

    /* Left column (narrow) */
    .left-panel {
      width: 320px;
      min-height: 60vh;
    }

    /* Right column (main) */
    .right-panel {
      flex: 1;
      min-height: 60vh;
    }

    /* Generic glass card */
    .glass {
      background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
      border: 1px solid rgba(255,255,255,0.06);
      backdrop-filter: blur(8px) saturate(120%);
      -webkit-backdrop-filter: blur(8px) saturate(120%);
      border-radius: 14px;
      padding: 18px;
      margin-bottom: 16px;
      box-shadow: 0 8px 30px rgba(2,6,23,0.6);
      transition: transform 0.35s cubic-bezier(.2,.9,.3,1), box-shadow .35s;
      opacity: 0;
      transform: translateY(8px);
      animation: fadeUp 0.6s forwards;
    }
    .glass:hover { transform: translateY(-6px) scale(1.01); box-shadow: 0 18px 60px rgba(2,6,23,0.8); }

    /* Headings */
    .hero {
      font-size: 34px;
      font-weight: 800;
      margin: 0 0 6px 0;
      color: #fff;
    }
    .sub {
      color: var(--muted);
      margin-bottom: 10px;
    }

    /* Buttons */
    .btn {
      background: var(--accent);
      color: #fff;
      padding: 10px 14px;
      border-radius: 10px;
      border: none;
      font-weight: 600;
      cursor: pointer;
      box-shadow: 0 10px 30px rgba(122,88,255,0.12);
      transition: transform .18s ease, box-shadow .18s ease;
    }
    .btn:hover { transform: translateY(-3px); box-shadow: 0 18px 50px rgba(122,88,255,0.16); }

    /* Chat bubbles */
    .chat-user { background: rgba(255,255,255,0.03); color:#eaf2ff; padding:12px; border-radius:10px; margin-bottom:8px; }
    .chat-bot { background: rgba(122,88,255,0.12); color:#071022; padding:12px; border-radius:10px; margin-bottom:8px; border:1px solid rgba(122,88,255,0.16); }

    /* Small text */
    .muted { color: var(--muted); font-size:13px; }

    /* form styling tweaks (generic) */
    input, textarea { background: rgba(255,255,255,0.02) !important; color:#e8eef8 !important; border-radius:10px !important; border:1px solid rgba(255,255,255,0.06) !important; padding:10px !important; }

    /* icons row */
    .icon-row { display:flex; gap:10px; align-items:center; margin-top:8px; }
    .icon-chip { padding:8px 10px; border-radius:10px; background: rgba(255,255,255,0.02); color:var(--muted); font-weight:600; font-size:14px; }

    /* animation */
    @keyframes fadeUp { to { opacity:1; transform: translateY(0); } }

    /* responsive */
    @media (max-width:900px) {
      .two-col { flex-direction: column; }
      .left-panel { width: 100%; }
      .right-panel { width: 100%; }
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Inject CSS once
inject_css()

# ----------------------------
# Message storage & telegram
# ----------------------------
def ensure_msg_file():
    if not os.path.exists(MSG_FILE):
        with open(MSG_FILE, "w", encoding="utf-8") as f:
            pass

def load_messages():
    ensure_msg_file()
    msgs = []
    with open(MSG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                msgs.append(json.loads(line))
            except:
                continue
    return msgs

def overwrite_messages(msgs):
    with open(MSG_FILE, "w", encoding="utf-8") as f:
        for m in msgs:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

def send_telegram_notification(text):
    token = TELEGRAM_BOT_TOKEN
    if not token:
        return False, "No TELEGRAM_BOT_TOKEN configured."
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            return True, "Sent"
        return False, f"HTTP {r.status_code}: {r.text}"
    except Exception as e:
        return False, str(e)

def save_message(text):
    ensure_msg_file()
    msg = {"id": int(time.time() * 1000), "text": text, "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}
    with open(MSG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(msg, ensure_ascii=False) + "\n")
    # send telegram notification
    notification = f"📨 New anonymous message:\n\n{text}\n\nID: {msg['id']}\nTime: {msg['timestamp']}"
    ok, info = send_telegram_notification(notification)
    return msg, ok, info

# ----------------------------
# Blog helpers (unchanged, robust)
# ----------------------------
def get_post_data(slug):
    file_path = os.path.join(POSTS_DIR, f"{slug}.md")
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    metadata_match = re.match(r'---\n(.*?)\n---', content, re.DOTALL)
    metadata = {}
    content_body = content
    if metadata_match:
        metadata_str = metadata_match.group(1)
        for line in metadata_str.split("\n"):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
        content_body = content[metadata_match.end():].strip()
    html_content = markdown(content_body)
    return {"slug": slug, "title": metadata.get("title", "Untitled Post"),
            "date": metadata.get("date", "N/A"), "author": metadata.get("author", "N/A"),
            "summary": metadata.get("summary", "No summary available."), "html_content": html_content}

def get_all_posts_metadata():
    if not os.path.exists(POSTS_DIR):
        return []
    post_files = [f for f in os.listdir(POSTS_DIR) if f.endswith(".md")]
    all_metadata = []
    for filename in post_files:
        slug = filename.replace(".md", "")
        data = get_post_data(slug)
        if data:
            all_metadata.append({"slug": data["slug"], "title": data["title"], "date": data["date"], "summary": data["summary"]})
    try:
        all_metadata.sort(key=lambda x: time.strptime(x["date"], "%B %d, %Y"), reverse=True)
    except:
        pass
    return all_metadata

# ----------------------------
# Renderers: Chatbot & Blog right column
# ----------------------------
def render_chatbot():
    st.markdown("<div class='glass'><h2 class='hero'>Ask Me Anything!</h2><div class='sub'>I will answer questions about myself.</div></div>", unsafe_allow_html=True)

    question_bank = {
        'what is your name': 'My name is Aryan.',
        'where are you from': 'I am from India.',
        'what do you do': 'I build websites and explore AI.',
        'what are your hobbies': 'Coding, photography, and learning new tech.',
        'how can i contact you': 'Email: aryanxsharma26@gmail.com'
    }

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # show conversation
    for m in st.session_state.messages:
        role = m.get("role")
        content = m.get("content")
        if role == "user":
            st.markdown(f"<div class='chat-user'>{content}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bot'>{content}</div>", unsafe_allow_html=True)

    user_input = st.chat_input("Ask me a question...")
    if user_input:
        st.session_state.messages.append({"role":"user","content":user_input})
        answer = question_bank.get(user_input.lower(), "Sorry! I don't have an answer for that.")
        st.session_state.messages.append({"role":"system","content":answer})
        # typing effect
        placeholder = st.empty()
        text = ""
        for ch in answer:
            text += ch
            placeholder.markdown(f"<div class='chat-bot'>{text}</div>", unsafe_allow_html=True)
            time.sleep(0.01)
        placeholder.markdown(f"<div class='chat-bot'>{answer}</div>", unsafe_allow_html=True)

def render_blog():
    st.markdown("<div class='glass'><h2 class='hero'>My Blog</h2><div class='sub'>Latest posts</div></div>", unsafe_allow_html=True)
    posts = get_all_posts_metadata()
    if not posts:
        st.info("No blog posts found. Add .md files to the blog_posts/ folder.")
        return
    for p in posts:
        st.markdown(f"<div class='glass'><h3 style='margin:0'>{p['title']}</h3><div class='muted'>{p['date']}</div><p>{p['summary']}</p></div>", unsafe_allow_html=True)
        if st.button("Read →", key=f"r_{p['slug']}"):
            st.session_state.selected_post = p['slug']
            st.session_state.view_post = True
            st.experimental_rerun()
    if st.session_state.get("view_post", False) and st.session_state.get("selected_post"):
        slug = st.session_state.selected_post
        post = get_post_data(slug)
        if post:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown(f"<div class='glass'><h2>{post['title']}</h2><div class='muted'>By {post['author']} • {post['date']}</div></div>", unsafe_allow_html=True)
            st.markdown(post['html_content'], unsafe_allow_html=True)
            if st.button("← Back to Blog"):
                st.session_state.view_post = False
                st.experimental_rerun()

# ----------------------------
# Left column: Writings (anonymous), Anonymous Box, Admin
# ----------------------------
def left_writings_panel():
    st.markdown("<div class='glass'><h3 style='margin:0'>📝 Writings (anonymous)</h3><div class='muted'>Public snippets (no author)</div></div>", unsafe_allow_html=True)
    # For demo, show latest anonymous messages as "writings" (anonymous)
    msgs = load_messages()
    if not msgs:
        st.markdown("<div class='glass'><div class='muted'>No writings yet — visitors can add messages below.</div></div>", unsafe_allow_html=True)
    else:
        # show most recent 6 messages
        recent = sorted(msgs, key=lambda x: x.get("id",0), reverse=True)[:6]
        for m in recent:
            text = m.get("text","")
            ts = m.get("timestamp","")
            st.markdown(f"<div class='glass'><div style='font-weight:600'>{text[:80]}{'...' if len(text)>80 else ''}</div><div class='muted' style='margin-top:6px'>{ts}</div></div>", unsafe_allow_html=True)

def left_anonymous_box():
    st.markdown("<div class='glass'><h4 style='margin:0'>✉️ Anonymous Box</h4><div class='muted'>Send a message without your name</div></div>", unsafe_allow_html=True)
    with st.form("left_anon_form", clear_on_submit=True):
        anon_msg = st.text_area("Your message", max_chars=2000, placeholder="Write something kind, a thought, feedback, or a question...")
        submitted = st.form_submit_button("Send Anonymously")
    if submitted:
        if not anon_msg or not anon_msg.strip():
            st.warning("Please write a message before sending.")
        else:
            saved, ok, info = save_message(anon_msg.strip())
            if ok:
                st.success("Message saved and Telegram notified (if token set).")
            else:
                st.success("Message saved. Telegram notification not sent: " + str(info))
            st.markdown(f"<div class='muted'>ID: {saved['id']} • {saved['timestamp']}</div>", unsafe_allow_html=True)

def left_admin_panel():
    st.markdown("<div class='glass'><h4 style='margin:0'>🔒 Admin</h4><div class='muted'>Private view (enter token)</div></div>", unsafe_allow_html=True)
    # unlock via query param or input
    qp = st.experimental_get_query_params()
    unlocked = False
    if ADMIN_QUERY_PARAM in qp:
        if qp.get(ADMIN_QUERY_PARAM, [""])[0] == ADMIN_TOKEN:
            unlocked = True
            st.session_state._admin_unlocked = True
    if st.session_state.get("_admin_unlocked", False):
        unlocked = True
    with st.expander("Admin Controls"):
        if not unlocked:
            entered = st.text_input("Enter admin token to unlock", type="password", key="left_admin_input")
            if st.button("Unlock", key="left_unlock_btn"):
                if entered.strip() == ADMIN_TOKEN:
                    st.session_state._admin_unlocked = True
                    st.experimental_set_query_params(**{ADMIN_QUERY_PARAM: ADMIN_TOKEN})
                    st.experimental_rerun()
                else:
                    st.error("Invalid token")
        else:
            st.success("Admin unlocked")
            # show messages with delete controls
            msgs = load_messages()
            st.markdown(f"<div class='muted'>Total messages: {len(msgs)}</div>", unsafe_allow_html=True)
            if not msgs:
                st.info("No anonymous messages yet.")
            else:
                for m in sorted(msgs, key=lambda x: x.get("id",0), reverse=True):
                    with st.expander(f"ID {m.get('id')} • {m.get('timestamp')}"):
                        st.markdown(f"<div class='muted'>{m.get('text')}</div>", unsafe_allow_html=True)
                        if st.button("Delete message", key=f"adm_del_{m.get('id')}"):
                            new = [x for x in msgs if x.get('id') != m.get('id')]
                            overwrite_messages(new)
                            st.success("Deleted")
                            st.experimental_rerun()
                if st.button("Clear all messages", key="adm_clear_all"):
                    overwrite_messages([])
                    st.success("Cleared all messages")
                    st.experimental_rerun()

# ----------------------------
# Layout & routing
# ----------------------------
if "app_page" not in st.session_state:
    st.session_state.app_page = "Chatbot"  # default

# Top header (real website feel)
st.markdown("<div style='display:flex; align-items:center; justify-content:space-between; margin-bottom:18px'>"
            "<div style='display:flex; gap:14px; align-items:center'>"
            "<div style='width:48px; height:48px; border-radius:10px; background:linear-gradient(90deg,#7A58FF,#58C8FF); display:flex; align-items:center; justify-content:center; font-weight:800'>A</div>"
            "<div><div style='font-weight:800; font-size:18px'>Aryan Chatbot</div><div class='muted' style='font-size:12px'>AI • Blog • Photos</div></div>"
            "</div>"
            "<div style='display:flex; gap:10px; align-items:center'>"
            f"<a href='https://instagram.com/{INSTAGRAM_USERNAME}' target='_blank' style='color:inherit; text-decoration:none'><div class='icon-chip'>📸 Instagram</div></a>"
            "<div class='icon-chip'>✨ Professional</div>"
            "</div>"
            "</div>", unsafe_allow_html=True)

# Two-column layout
left_col, right_col = st.columns([1, 2.2], gap="large")

with left_col:
    st.markdown("<div class='left-panel'>", unsafe_allow_html=True)
    left_writings_panel()
    left_anonymous_box()
    left_admin_panel()
    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    # tabs feel
    tabs = st.tabs(["💬 Chatbot", "📰 Blog"])
    with tabs[0]:
        render_chatbot()
    with tabs[1]:
        # blog view may include selected post state
        if st.session_state.get("view_post", False) and st.session_state.get("selected_post"):
            render_blog()  # render_blog handles showing the selected post when state set
        else:
            render_blog()

# footer spacing
st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)
