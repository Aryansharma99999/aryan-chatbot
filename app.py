# app.py - Streamlit app with Glassmorphism theme and animations
import os
import re
import time
import json
import requests
from datetime import datetime
from markdown import markdown
import streamlit as st

# ----------------------------
# Page config & constants
# ----------------------------
st.set_page_config(page_title='Aryan Chatbot & Blog', layout="wide", initial_sidebar_state="expanded")
BASE_DIR = os.path.dirname(__file__)
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")
MSG_FILE = os.path.join(BASE_DIR, "anonymous_messages.txt")
ADMIN_TOKEN = "admin-aryan"
ADMIN_QUERY_PARAM = "admin"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = "8521726094"
INSTAGRAM_USERNAME = "aryanxsharma26"

# ----------------------------
# Inject glassmorphism CSS + fonts + animations
# ----------------------------
def inject_glass_css():
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

    :root{
      --bg1: linear-gradient(135deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
      --glass-bg: rgba(255,255,255,0.06);
      --glass-border: rgba(255,255,255,0.14);
      --accent: rgba(120, 88, 255, 0.95);
      --muted: rgba(255,255,255,0.6);
    }

    /* page background */
    .stApp {
      font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
      background: radial-gradient(1200px 600px at 10% 20%, rgba(120,88,255,0.10), transparent),
                  radial-gradient(800px 400px at 90% 80%, rgba(88,200,255,0.06), transparent),
                  linear-gradient(180deg, #0f1723 0%, #071022 100%);
      color: #e8eef8;
      min-height: 100vh;
      transition: background 0.6s ease;
      padding-top: 18px;
    }

    /* sidebar glass */
    .css-1d391kg { /* inner container class may vary across Streamlit versions; using common selectors below too */
      background: transparent;
    }
    .stSidebar {
      background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
    }

    /* generic glass card */
    .glass {
      background: rgba(255,255,255,0.04);
      border: 1px solid rgba(255,255,255,0.06);
      backdrop-filter: blur(8px) saturate(120%);
      -webkit-backdrop-filter: blur(8px) saturate(120%);
      border-radius: 14px;
      box-shadow: 0 6px 30px rgba(2,6,23,0.6);
      padding: 18px;
      margin-bottom: 18px;
      transition: transform 0.35s cubic-bezier(.2,.9,.3,1), box-shadow 0.35s;
      opacity: 0;
      transform: translateY(8px);
      animation: fadeUp 0.6s forwards;
    }

    /* hover subtle lift */
    .glass:hover {
      transform: translateY(-6px) scale(1.01);
      box-shadow: 0 12px 40px rgba(2,6,23,0.75);
    }

    /* headings */
    .hero-title {
      font-weight: 800;
      font-size: 42px;
      color: #ffffff;
      margin: 0 0 6px 0;
      letter-spacing: -0.4px;
    }
    .hero-sub {
      color: rgba(255,255,255,0.82);
      font-size: 18px;
      margin-bottom: 12px;
    }

    /* chat message blocks */
    .chat-user, .chat-bot {
      border-radius: 12px;
      padding: 12px 14px;
      margin: 8px 0;
      font-size: 15px;
      line-height: 1.45;
    }
    .chat-user {
      background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));
      border: 1px solid rgba(255,255,255,0.04);
      text-align: left;
      color: #f6f9ff;
    }
    .chat-bot {
      background: linear-gradient(180deg, rgba(120,88,255,0.12), rgba(120,88,255,0.06));
      border: 1px solid rgba(120,88,255,0.16);
      color: #0b0f14;
      text-shadow: none;
    }

    /* buttons & inputs (Streamlit generates many classes; style generically) */
    .stButton>button, .stDownloadButton>button {
      background: linear-gradient(90deg, rgba(120,88,255,0.95), rgba(88,200,255,0.85));
      color: #fff;
      border: none;
      padding: 10px 16px;
      border-radius: 12px;
      font-weight: 600;
      box-shadow: 0 8px 20px rgba(120,88,255,0.12);
      transition: transform .18s ease, box-shadow .18s ease;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
      transform: translateY(-3px);
      box-shadow: 0 18px 40px rgba(120,88,255,0.14);
    }

    /* subtle input style */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
      background: rgba(255,255,255,0.02) !important;
      border: 1px solid rgba(255,255,255,0.06) !important;
      color: #e6eefc !important;
      padding: 10px !important;
      border-radius: 10px !important;
    }

    /* layout helpers */
    .sidebar .stButton button { width: 100%; }
    .left-glass { padding: 18px; margin-bottom: 20px; }
    .muted { color: rgba(255,255,255,0.65); font-size: 14px; }

    /* animation */
    @keyframes fadeUp {
      to { opacity: 1; transform: translateY(0); }
    }

    /* small screen tweaks */
    @media (max-width: 768px) {
      .hero-title { font-size: 32px; }
      .glass { border-radius: 10px; padding: 14px; }
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Inject CSS immediately
inject_glass_css()

# ----------------------------
# Utility: anonymous messages stored as JSON-lines
# ----------------------------
def ensure_msg_file():
    if not os.path.exists(MSG_FILE):
        with open(MSG_FILE, "w", encoding="utf-8") as f:
            pass

def load_messages():
    ensure_msg_file()
    out = []
    with open(MSG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
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
    notification = f"📨 New anonymous message:\n\n{text}\n\nID: {msg['id']}\nTime: {msg['timestamp']}"
    ok, info = send_telegram_notification(notification)
    return msg, ok, info

# ----------------------------
# Blog helpers (unchanged)
# ----------------------------
def get_post_data(slug):
    file_path = os.path.join(POSTS_DIR, f"{slug}.md")
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    metadata_match = re.match(r'---\\n(.*?)\\n---', content, re.DOTALL)
    metadata = {}
    content_body = content
    if metadata_match:
        metadata_str = metadata_match.group(1)
        for line in metadata_str.split("\\n"):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
        content_body = content[metadata_match.end():].strip()
    html_content = markdown(content_body)
    return {"slug": slug, "title": metadata.get("title", "Untitled Post"), "date": metadata.get("date", "N/A"),
            "author": metadata.get("author", "N/A"), "summary": metadata.get("summary", "No summary available."),
            "html_content": html_content}

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
# Renderers
# ----------------------------
def render_post_detail(post_slug):
    post = get_post_data(post_slug)
    if not post:
        st.error("Post not found")
        return
    st.markdown(f"<div class='glass'><h1 class='hero-title'>{post['title']}</h1><div class='muted'>By {post['author']} • {post['date']}</div></div>", unsafe_allow_html=True)
    st.markdown(post["html_content"], unsafe_allow_html=True)
    if st.button("← Back to All Posts"):
        st.session_state.blog_view = "index"
        st.session_state.app_page = "Blog"
        st.experimental_rerun()

def render_blog_index():
    st.markdown("<div class='glass'><h2 class='hero-title'>My Blog</h2></div>", unsafe_allow_html=True)
    posts = get_all_posts_metadata()
    if not posts:
        st.info("No posts yet")
        return
    for p in posts:
        st.markdown(f"<div class='glass'><h3 style='margin:0 0 6px 0'>{p['title']}</h3><div class='muted'>{p['date']}</div><p>{p['summary']}</p></div>", unsafe_allow_html=True)
        if st.button("Read →", key=f"r_{p['slug']}"):
            st.session_state.blog_view = "detail"
            st.session_state.current_post_slug = p['slug']
            st.experimental_rerun()

def blog_app():
    if "blog_view" not in st.session_state:
        st.session_state.blog_view = "index"
    if "current_post_slug" not in st.session_state:
        st.session_state.current_post_slug = None
    if st.session_state.blog_view == "detail" and st.session_state.current_post_slug:
        render_post_detail(st.session_state.current_post_slug)
    else:
        render_blog_index()

# ----------------------------
# Photos & Writings pages
# ----------------------------
def photos_page():
    st.markdown("<div class='glass'><h2 class='hero-title'>Photos</h2><div class='muted'>A small gallery</div></div>", unsafe_allow_html=True)
    images = [f for f in os.listdir(BASE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not images:
        st.info("No images found in repo root")
        return
    cols = st.columns(3)
    for i, img in enumerate(images):
        with cols[i % 3]:
            st.image(os.path.join(BASE_DIR, img), caption=img, use_column_width=True)

def writings_page():
    st.markdown("<div class='glass'><h2 class='hero-title'>Writings</h2></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([1,3])
    with col1:
        st.markdown("<div class='glass'><h4>Categories</h4><ul class='muted'><li>Daily Thoughts</li><li>Projects</li><li>Life Lessons</li></ul></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='glass'><h3>Recent</h3><p class='muted'>Keep full posts in blog_posts/ folder for detailed articles.</p></div>", unsafe_allow_html=True)

# ----------------------------
# Anonymous box & admin
# ----------------------------
def anonymous_box_page():
    st.markdown("<div class='glass'><h2 class='hero-title'>Anonymous Message Box</h2><div class='muted'>Send a message anonymously</div></div>", unsafe_allow_html=True)
    with st.form("anon_form", clear_on_submit=True):
        msg = st.text_area("Your message", max_chars=2000, placeholder="Write something helpful or kind...")
        submitted = st.form_submit_button("Send Anonymously")
    if submitted:
        if not msg or not msg.strip():
            st.warning("Please write a message.")
        else:
            saved, ok, info = save_message(msg.strip())
            if ok:
                st.success("Message sent. Thank you!")
            else:
                st.warning("Saved locally but Telegram not sent: " + str(info))
            st.markdown(f"<div class='muted'>ID: {saved['id']} • {saved['timestamp']}</div>", unsafe_allow_html=True)
    st.info("Only someone with the admin token can read messages in the Admin page.")

def admin_page():
    st.markdown("<div class='glass'><h2 class='hero-title'>Admin - Anonymous Messages</h2><div class='muted'>Private</div></div>", unsafe_allow_html=True)
    msgs = load_messages()
    st.markdown(f"<div class='muted'>Total messages: {len(msgs)}</div>", unsafe_allow_html=True)
    if not msgs:
        st.info("No messages yet.")
        return
    for m in sorted(msgs, key=lambda x: x.get("id",0), reverse=True):
        with st.expander(f"ID {m.get('id')} • {m.get('timestamp')}"):
            st.markdown(f"<div class='chat-user'>{m.get('text')}</div>", unsafe_allow_html=True)
            if st.button("Delete", key=f"del_{m.get('id')}"):
                new = [x for x in msgs if x.get('id') != m.get('id')]
                overwrite_messages(new)
                st.success("Deleted")
                st.experimental_rerun()
    if st.button("Clear all messages"):
        overwrite_messages([])
        st.success("Cleared")
        st.experimental_rerun()

# ----------------------------
# Main app & Navigation
# ----------------------------
if "app_page" not in st.session_state:
    st.session_state.app_page = "Chatbot"

# Sidebar content
with st.sidebar:
    st.markdown("<div class='left-glass glass'><h2 style='margin:0' class='hero-title'>Navigation</h2><div class='muted'>📸 Follow Me</div><a href='https://instagram.com/{0}' target='_blank' style='color:inherit'>Instagram</a></div>".format(INSTAGRAM_USERNAME), unsafe_allow_html=True)
    page = st.radio("Go to:", ["Chatbot","Blog","Photos","Writings","Anonymous Box"], index=["Chatbot","Blog","Photos","Writings","Anonymous Box"].index(st.session_state.app_page))
    if st.session_state.app_page != page:
        st.session_state.app_page = page
        st.experimental_rerun()

    st.markdown("---")
    with st.expander("🔑 Admin (hidden)"):
        entered = st.text_input("Enter admin token", type="password", key="admin_in")
        if st.button("Unlock Admin", key="unlock_btn"):
            if entered.strip() == ADMIN_TOKEN:
                st.session_state._admin_unlocked = True
                st.experimental_set_query_params(**{ADMIN_QUERY_PARAM: ADMIN_TOKEN})
                st.experimental_rerun()
            else:
                st.error("Invalid token")

if st.experimental_get_query_params().get(ADMIN_QUERY_PARAM, [""])[0] == ADMIN_TOKEN:
    st.session_state._admin_unlocked = True

if st.session_state.get("_admin_unlocked", False):
    st.sidebar.markdown("[Open Admin Page](?admin=admin-aryan)")

# Route pages
if st.session_state.app_page == "Chatbot":
    st.markdown("<div class='glass'><h1 class='hero-title'>Ask Me Anything!</h1><div class='hero-sub'>I will answer questions about myself.</div></div>", unsafe_allow_html=True)

    question_bank = {
        'what is your name': 'My name is Aryan.',
        'where are you from': 'I am from India.',
        'what do you do': 'I build websites and explore AI.',
        'what are your hobbies': 'Coding, photography, and learning new tech.',
        'how can i contact you': 'Email: aryanxsharma26@gmail.com'
    }

    if "messages" not in st.session_state:
        st.session_state.messages = []

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
        # small typing emulation
        typing_placeholder = st.empty()
        text = ""
        for ch in answer:
            text += ch
            typing_placeholder.markdown(f"<div class='chat-bot'>{text}</div>", unsafe_allow_html=True)
            time.sleep(0.01)
        typing_placeholder.markdown(f"<div class='chat-bot'>{answer}</div>", unsafe_allow_html=True)

elif st.session_state.app_page == "Blog":
    blog_app()
elif st.session_state.app_page == "Photos":
    photos_page()
elif st.session_state.app_page == "Writings":
    writings_page()
elif st.session_state.app_page == "Anonymous Box":
    anonymous_box_page()

# Show admin inline if unlocked
if st.session_state.get("_admin_unlocked", False):
    st.markdown("<hr>")
    if st.button("Open Admin Page"):
        admin_page()

# Footer spacing
st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Admin access")
    if st.button("Open Hidden Admin Page", key="open_admin"):
        admin_page()
