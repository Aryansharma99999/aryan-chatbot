# Full app.py — Streamlit app with Telegram notifications (chat_id embedded)
import os
import re
import time
import json
import requests
from datetime import datetime
from markdown import markdown
import streamlit as st

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(page_title='Aryan Chatbot & Blog', layout="wide", initial_sidebar_state="expanded")

# Secret admin token (normalized)
ADMIN_TOKEN = "admin-aryan"
ADMIN_QUERY_PARAM = "admin"  # use ?admin=admin-aryan to open admin view

# Files / folders
BASE_DIR = os.path.dirname(__file__)
MSG_FILE = os.path.join(BASE_DIR, "anonymous_messages.txt")
POSTS_DIR = os.path.join(BASE_DIR, 'blog_posts')

# Telegram settings
# IMPORTANT: Set TELEGRAM_BOT_TOKEN as an environment variable (DO NOT hardcode tokens)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = "8521726094"  # <-- the chat_id you provided

# Instagram username
INSTAGRAM_USERNAME = "aryanxsharma26"

# ----------------------------
# Helper functions for messages
# ----------------------------
def ensure_msg_file():
    if not os.path.exists(MSG_FILE):
        with open(MSG_FILE, 'w', encoding='utf-8') as f:
            pass  # create empty file

def load_messages():
    ensure_msg_file()
    msgs = []
    with open(MSG_FILE, 'r', encoding='utf-8') as f:
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
    with open(MSG_FILE, 'w', encoding='utf-8') as f:
        for m in msgs:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

def send_telegram_notification(text):
    """Send a notification to your Telegram chat if token is configured."""
    token = TELEGRAM_BOT_TOKEN
    if not token:
        # token not configured — skip sending
        return False, "No TELEGRAM_BOT_TOKEN configured."
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            return True, "Sent"
        else:
            return False, f"Telegram error {resp.status_code}: {resp.text}"
    except Exception as e:
        return False, str(e)

def save_message(text):
    ensure_msg_file()
    msg = {
        "id": int(time.time() * 1000),
        "text": text,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }
    with open(MSG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(msg, ensure_ascii=False) + "\n")

    # Send Telegram notification (non-blocking-ish)
    notification_text = f"📨 New anonymous message:\n\n{text}\n\nID: {msg['id']}\nTime: {msg['timestamp']}"
    ok, info = send_telegram_notification(notification_text)
    return msg, ok, info

# ----------------------------
# BLOG utilities
# ----------------------------
def get_post_data(slug):
    file_path = os.path.join(POSTS_DIR, f"{slug}.md")
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    metadata_match = re.match(r'---\n(.*?)\n---', content, re.DOTALL)
    metadata = {}
    content_body = content
    if metadata_match:
        metadata_str = metadata_match.group(1)
        for line in metadata_str.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
        content_body = content[metadata_match.end():].strip()
    html_content = markdown(content_body)
    return {
        'slug': slug,
        'title': metadata.get('title', 'Untitled Post'),
        'date': metadata.get('date', 'N/A'),
        'author': metadata.get('author', 'N/A'),
        'summary': metadata.get('summary', 'No summary available.'),
        'html_content': html_content,
    }

def get_all_posts_metadata():
    if not os.path.exists(POSTS_DIR):
        return []
    post_files = [f for f in os.listdir(POSTS_DIR) if f.endswith('.md')]
    all_metadata = []
    for filename in post_files:
        slug = filename.replace('.md', '')
        data = get_post_data(slug)
        if data:
            all_metadata.append({
                'slug': data['slug'],
                'title': data['title'],
                'date': data['date'],
                'summary': data['summary'],
            })
    try:
        all_metadata.sort(key=lambda x: time.strptime(x['date'], '%B %d, %Y'), reverse=True)
    except:
        pass
    return all_metadata

# ----------------------------
# Blog rendering
# ----------------------------
def render_post_detail(post_slug):
    post = get_post_data(post_slug)
    if not post:
        st.error("Error: Blog Post not found!")
        return
    st.title(post['title'])
    st.caption(f"By {post['author']} on {post['date']}")
    st.markdown("---")
    st.markdown(post['html_content'], unsafe_allow_html=True)
    st.markdown("---")
    if st.button("← Back to All Posts"):
        st.session_state.app_page = 'Blog'
        st.session_state.blog_view = 'index'
        st.rerun()

def render_blog_index():
    st.header("My Blog")
    posts = get_all_posts_metadata()
    if not posts:
        st.info("No blog posts have been published yet!")
        return
    for post in posts:
        with st.container():
            st.subheader(post['title'])
            st.caption(f"Published: {post['date']}")
            st.write(post['summary'])
            if st.button("Read More →", key=f"read_{post['slug']}"):
                st.session_state.blog_view = 'detail'
                st.session_state.current_post_slug = post['slug']
                st.rerun()

def blog_app():
    if 'blog_view' not in st.session_state:
        st.session_state.blog_view = 'index'
    if 'current_post_slug' not in st.session_state:
        st.session_state.current_post_slug = None
    if st.session_state.blog_view == 'detail' and st.session_state.current_post_slug:
        render_post_detail(st.session_state.current_post_slug)
    else:
        render_blog_index()

# ----------------------------
# Photos Page
# ----------------------------
def photos_page():
    st.title("📸 My Photos")
    st.write("Here are some of my pictures (images loaded from repo root):")
    img_folder = BASE_DIR
    images = [f for f in os.listdir(img_folder) if f.lower().endswith((".jpg", ".png", ".jpeg"))]
    if not images:
        st.info("No images found! Upload images (.jpg/.png) directly into your repo folder.")
        return
    cols = st.columns(3)
    for idx, img in enumerate(images):
        with cols[idx % 3]:
            st.image(os.path.join(img_folder, img), caption=img, use_column_width=True)

# ----------------------------
# Writings Page
# ----------------------------
def writings_page():
    st.title("📝 My Writings")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.subheader("📚 Categories")
        st.markdown("""
- Daily Thoughts  
- Motivation  
- Projects  
- Life Lessons  
        """)
    with col2:
        st.subheader("Welcome!")
        st.write("Select a category from the left to explore my writings. Keep full posts in the `blog_posts/` folder.")

# ----------------------------
# Anonymous Message Box (public)
# ----------------------------
def anonymous_box_page():
    st.title("✉️ Anonymous Message Box")
    st.write("Leave a message — your name or email is not required.")
    with st.form("anon_msg_form", clear_on_submit=True):
        msg_text = st.text_area("Your message", max_chars=2000, placeholder="Write something nice...")
        submitted = st.form_submit_button("Send Anonymously")
    if submitted:
        if not msg_text or not msg_text.strip():
            st.warning("Please write a message before sending.")
        else:
            saved, ok, info = save_message(msg_text.strip())
            if ok:
                st.success("Message sent. Thank you!")
            else:
                st.warning("Message saved but Telegram notification failed: " + str(info))
            st.caption(f"Message ID: {saved['id']} • {saved['timestamp']}")
    st.markdown("---")
    st.info("This is public and anonymous. Only you (with the admin token) can view messages on the admin page.")

# ----------------------------
# Admin page (hidden)
# ----------------------------
def admin_page():
    st.title("🔒 Anonymous Messages - Admin")
    st.info("You are viewing the hidden admin page. Only access this if you have the secret token.")
    msgs = load_messages()
    st.markdown(f"**Total messages:** {len(msgs)}")
    msgs_sorted = sorted(msgs, key=lambda m: m.get("id", 0), reverse=True)
    if not msgs_sorted:
        st.info("No anonymous messages yet.")
    else:
        for m in msgs_sorted:
            with st.expander(f"Message ID {m.get('id')} • {m.get('timestamp')}"):
                st.write(m.get('text'))
                if st.button("Delete this message", key=f"del_{m.get('id')}"):
                    new_msgs = [x for x in msgs if x.get('id') != m.get('id')]
                    overwrite_messages(new_msgs)
                    st.success("Message deleted.")
                    st.experimental_rerun()
        st.markdown("---")
        if st.button("Clear All Messages", key="clear_all_confirm"):
            overwrite_messages([])
            st.success("All messages cleared.")
            st.experimental_rerun()

# ----------------------------
# Main Navigation & Routing
# ----------------------------
if 'app_page' not in st.session_state:
    st.session_state.app_page = 'Chatbot'

# Sidebar navigation
st.sidebar.title("Navigation")
st.sidebar.markdown("### 📸 Follow Me")
st.sidebar.markdown(f"[Instagram](https://instagram.com/{INSTAGRAM_USERNAME})")

page_selection = st.sidebar.radio(
    "Go to:",
    ["Chatbot", "Blog", "Photos", "Writings", "Anonymous Box"],
    key='page_selector',
    index=["Chatbot", "Blog", "Photos", "Writings", "Anonymous Box"].index(st.session_state.app_page)
)

if st.session_state.app_page != page_selection:
    st.session_state.app_page = page_selection
    st.rerun()

# Check for admin query param or manual unlock
query_params = st.experimental_get_query_params()
has_admin_token = False
if ADMIN_QUERY_PARAM in query_params:
    token = query_params.get(ADMIN_QUERY_PARAM, [""])[0]
    if token == ADMIN_TOKEN:
        has_admin_token = True

st.sidebar.markdown("---")
with st.sidebar.expander("🔑 Admin (hidden)"):
    entered = st.text_input("Enter admin token to unlock admin page (private)", type="password", key="admin_input")
    if st.button("Unlock Admin", key="unlock_btn"):
        if entered.strip() == ADMIN_TOKEN:
            st.session_state._admin_unlocked = True
            st.experimental_set_query_params(**{ADMIN_QUERY_PARAM: ADMIN_TOKEN})
            st.experimental_rerun()
        else:
            st.error("Invalid token.")

if st.session_state.get("_admin_unlocked", False):
    has_admin_token = True

if has_admin_token:
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"[Open Admin Page](?{ADMIN_QUERY_PARAM}={ADMIN_TOKEN})")

# Route pages
if st.session_state.app_page == "Chatbot":
    st.title('Ask Me Anything!')
    st.subheader('I will answer questions about myself.')
    question_bank = {
        'what is your name': 'My name is Aryan.',
        'where are you from': 'I am from India.',
        'what do you do': 'I am passionate about technology and building websites.',
        'what are your hobbies': 'I love coding, learning new things, and helping others.',
        'how can i contact you': 'You can contact me via email: aryanxsharma26@gmail.com'
    }
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message['role'], avatar='🤖' if message['role'] == 'system' else '👤'):
            st.markdown(message['content'])
    user_input = st.chat_input('Ask me a question...')
    if user_input:
        message = {'role': 'user', 'content': user_input}
        st.session_state.messages.append(message)
        answer = question_bank.get(user_input.lower(), "Sorry! I don't have an answer for that.")
        message = {'role': 'system', 'content': answer}
        st.session_state.messages.append(message)
        with st.chat_message('system', avatar='🤖'):
            typing_placeholder = st.empty()
            typing_text = ''
            for char in answer:
                typing_text += char
                typing_placeholder.markdown(typing_text)
                time.sleep(0.02)
            typing_placeholder.markdown(answer)

elif st.session_state.app_page == "Blog":
    blog_app()

elif st.session_state.app_page == "Photos":
    photos_page()

elif st.session_state.app_page == "Writings":
    writings_page()

elif st.session_state.app_page == "Anonymous Box":
    anonymous_box_page()

# If admin token present, allow opening admin page inline
if has_admin_token:
    st.markdown("---")
    st.markdown("### Admin access")
    if st.button("Open Hidden Admin Page", key="open_admin"):
        admin_page()
