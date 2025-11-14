# app.py - Minimal professional layout inspired by your Vercel site
import os, re, time, json, requests
from datetime import datetime
from markdown import markdown
import streamlit as st

# ----------------------------
# Config & paths
# ----------------------------
st.set_page_config(page_title="Aryan Chatbot", layout="wide", initial_sidebar_state="collapsed")
BASE_DIR = os.path.dirname(__file__)
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")
MSG_FILE = os.path.join(BASE_DIR, "anonymous_messages.txt")
ADMIN_TOKEN = "admin-aryan"
ADMIN_QUERY_PARAM = "admin"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = "8521726094"
IG = "aryanxsharma26"

# ----------------------------
# Simple CSS to match a Vercel-like clean look
# ----------------------------
def inject_css():
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    :root { --bg:#f8fafc; --card:#ffffff; --muted:#6b7280; --accent:#6d28d9; }
    .stApp { font-family: Inter, system-ui, -apple-system, 'Segoe UI', Roboto; background:var(--bg); color:#0f172a; padding:18px 24px; }
    /* header */
    .topbar { display:flex; justify-content:space-between; align-items:center; gap:16px; margin-bottom:18px; }
    .brand { display:flex; gap:12px; align-items:center; text-decoration:none; color:inherit; }
    .logo { width:44px; height:44px; border-radius:10px; background:linear-gradient(90deg,#7c3aed,#06b6d4); display:flex; align-items:center; justify-content:center; color:white; font-weight:700; }
    .navlinks { display:flex; gap:10px; align-items:center; }
    .navlink { padding:8px 12px; border-radius:8px; color:var(--muted); text-decoration:none; font-weight:600; }
    .navlink.active { background:transparent; color:var(--accent); }
    /* layout */
    .main { display:flex; gap:28px; align-items:flex-start; }
    .left { width:320px; }
    .right { flex:1; }
    .card { background:var(--card); border-radius:12px; padding:14px; box-shadow: 0 6px 20px rgba(2,6,23,0.06); margin-bottom:14px; }
    .muted { color:var(--muted); font-size:13px; }
    .hero { font-size:22px; font-weight:700; margin:0; }
    .sub { color:var(--muted); margin-top:6px; }
    /* chat */
    .chat-box { max-height:380px; overflow:auto; padding-right:6px; }
    .bubble-user { background:#eef2ff; color:#0b1220; border-radius:10px; padding:10px; margin-bottom:8px; display:inline-block; }
    .bubble-bot { background:#111827; color:white; border-radius:10px; padding:10px; margin-bottom:8px; display:inline-block; }
    /* small screens */
    @media (max-width:900px){ .main{ flex-direction:column; } .left{ width:100%; } }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

inject_css()

# ----------------------------
# Utilities: messages & telegram
# ----------------------------
def ensure_msg_file():
    if not os.path.exists(MSG_FILE):
        with open(MSG_FILE,"w",encoding="utf-8") as f: f.write("")

def load_messages():
    ensure_msg_file()
    out=[]
    with open(MSG_FILE,"r",encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            try: out.append(json.loads(line))
            except: continue
    return out

def overwrite_messages(msgs):
    with open(MSG_FILE,"w",encoding="utf-8") as f:
        for m in msgs: f.write(json.dumps(m,ensure_ascii=False) + "\n")

def send_telegram(text):
    token = TELEGRAM_BOT_TOKEN
    if not token:
        return False, "no token"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id":TELEGRAM_CHAT_ID,"text":text,"parse_mode":"HTML"}
    try:
        r = requests.post(url,json=payload,timeout=8)
        if r.status_code==200: return True, "sent"
        return False, r.text
    except Exception as e:
        return False,str(e)

def save_message(text):
    ensure_msg_file()
    msg = {"id":int(time.time()*1000),"text":text,"timestamp":datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}
    with open(MSG_FILE,"a",encoding="utf-8") as f: f.write(json.dumps(msg,ensure_ascii=False) + "\n")
    ok, info = send_telegram(f"📨 New anonymous message:\n\n{text}\n\nID:{msg['id']}")
    return msg, ok, info

# ----------------------------
# Blog helpers (basic)
# ----------------------------
def get_post_data(slug):
    p = os.path.join(POSTS_DIR, f"{slug}.md")
    if not os.path.exists(p): return None
    with open(p,"r",encoding="utf-8") as f: content=f.read()
    m = re.match(r'---\n(.*?)\n---',content,re.DOTALL)
    md={}
    body = content
    if m:
        meta = m.group(1)
        for line in meta.split("\n"):
            if ":" in line:
                k,v=line.split(":",1); md[k.strip()]=v.strip()
        body = content[m.end():].strip()
    return {"slug":slug,"title":md.get("title","Untitled"),"date":md.get("date","N/A"),"summary":md.get("summary",""),"html":markdown(body)}

def get_all_posts():
    if not os.path.exists(POSTS_DIR): return []
    fs=[f for f in os.listdir(POSTS_DIR) if f.endswith(".md")]
    out=[]
    for f in fs:
        s=f.replace(".md","")
        d=get_post_data(s)
        if d: out.append(d)
    return out

# ----------------------------
# Renderers
# ----------------------------
def show_chat():
    st.markdown("<div class='card'><div class='hero'>Chat with Aryan</div><div class='sub'>Simple Q&A — type a question below</div>", unsafe_allow_html=True)
    # small chat area
    if "messages" not in st.session_state: st.session_state.messages=[]
    with st.container():
        st.markdown("<div class='chat-box'>", unsafe_allow_html=True)
        for m in st.session_state.messages:
            if m["role"]=="user":
                st.markdown(f"<div class='bubble-user'>{m['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='bubble-bot'>{m['content']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    # input
    q = st.text_input("Ask a question", key="chat_input")
    if q:
        st.session_state.messages.append({"role":"user","content":q})
        bank = {'what is your name':'My name is Aryan.','where are you from':'I am from India.'}
        ans = bank.get(q.lower(),"Sorry! I don't have an answer for that.")
        st.session_state.messages.append({"role":"system","content":ans})
        st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def show_blog():
    posts = get_all_posts()
    st.markdown("<div class='card'><div class='hero'>Blog</div><div class='sub'>Latest posts</div></div>", unsafe_allow_html=True)
    if not posts:
        st.info("No blog posts yet. Add .md files to blog_posts/")
        return
    for p in posts:
        st.markdown(f"<div class='card'><strong>{p['title']}</strong><div class='muted'>{p['date']}</div><p>{p['summary']}</p></div>", unsafe_allow_html=True)
        if st.button("Read", key=f"read_{p['slug']}"):
            st.session_state.read_post = p['slug']; st.experimental_rerun()
    if st.session_state.get("read_post"):
        slug = st.session_state["read_post"]
        post = get_post_data(slug)
        if post:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"## {post['title']}\n\n*{post['date']}*\n\n", unsafe_allow_html=True)
            st.markdown(post['html'], unsafe_allow_html=True)
            if st.button("Back to blog"): st.session_state["read_post"]=None; st.experimental_rerun()
            st.markdown("</div>", unsafe_allow_html=True)

def left_writings():
    st.markdown("<div class='card'><strong>Writings (anonymous)</strong><div class='muted'>Public snippets</div></div>", unsafe_allow_html=True)
    msgs = load_messages()
    if not msgs:
        st.markdown("<div class='card muted'>No writings yet.</div>", unsafe_allow_html=True)
        return
    for m in sorted(msgs, key=lambda x: x.get("id",0), reverse=True)[:8]:
        txt = m.get("text","")
        ts = m.get("timestamp","")
        st.markdown(f"<div class='card'><div style='font-weight:600'>{txt[:120]}{'...' if len(txt)>120 else ''}</div><div class='muted'>{ts}</div></div>", unsafe_allow_html=True)

def left_anon_box():
    st.markdown("<div class='card'><strong>Anonymous Box</strong><div class='muted'>Send a message without your name</div></div>", unsafe_allow_html=True)
    with st.form("anon"):
        msg = st.text_area("Message", max_chars=2000)
        send = st.form_submit_button("Send")
    if send:
        if not msg or not msg.strip(): st.warning("Write a message.")
        else:
            saved, ok, info = save_message(msg.strip())
            if ok: st.success("Sent.")
            else: st.success("Saved (no telegram): " + str(info))
            st.experimental_rerun()

def left_admin():
    st.markdown("<div class='card'><strong>Admin</strong><div class='muted'>Private</div></div>", unsafe_allow_html=True)
    qp = st.experimental_get_query_params()
    unlocked=False
    if ADMIN_QUERY_PARAM in qp and qp[ADMIN_QUERY_PARAM][0]==ADMIN_TOKEN: unlocked=True; st.session_state._admin_unlocked=True
    if st.session_state.get("_admin_unlocked",False): unlocked=True
    if not unlocked:
        token = st.text_input("Admin token", type="password", key="adm_in")
        if st.button("Unlock", key="adm_btn"):
            if token.strip()==ADMIN_TOKEN:
                st.session_state._admin_unlocked=True
                st.experimental_set_query_params(**{ADMIN_QUERY_PARAM:ADMIN_TOKEN})
                st.experimental_rerun()
            else:
                st.error("Invalid")
    else:
        st.success("Unlocked")
        msgs=load_messages()
        st.markdown(f"<div class='muted'>Total: {len(msgs)}</div>", unsafe_allow_html=True)
        for m in sorted(msgs, key=lambda x: x.get("id",0), reverse=True):
            with st.expander(f"ID {m.get('id')} • {m.get('timestamp')}"):
                st.write(m.get("text"))
                if st.button("Delete", key=f"del_{m.get('id')}"):
                    new=[x for x in msgs if x.get("id")!=m.get("id")]
                    overwrite_messages(new); st.success("Deleted"); st.experimental_rerun()
        if st.button("Clear all"): overwrite_messages([]); st.success("Cleared"); st.experimental_rerun()

# ----------------------------
# Layout & routing
# ----------------------------
# header/navigation (top)
st.markdown(f"""
<div class="topbar">
  <div class="brand">
    <div class="logo">A</div>
    <div>
      <div style="font-weight:700">Aryan Chatbot</div>
      <div class="muted" style="font-size:12px">AI • Blog • Photos</div>
    </div>
  </div>
  <div class="navlinks">
    <a class="navlink {'active' if st.session_state.get('page','Chatbot')=='Chatbot' else ''}" href="#">Chatbot</a>
    <a class="navlink {'active' if st.session_state.get('page','Blog')=='Blog' else ''}" href="#">Blog</a>
    <a class="navlink" href="https://instagram.com/{IG}" target="_blank">Instagram</a>
  </div>
</div>
""", unsafe_allow_html=True)

# main 2-column
left_col, right_col = st.columns([1,2.2], gap="large")

with left_col:
    left_writings()
    left_anon_box()
    left_admin()

with right_col:
    # top small hero cards
    st.markdown("<div class='card'><div style='display:flex; justify-content:space-between; align-items:center'><div><div class='hero'>Welcome</div><div class='sub'>Ask me or read my posts</div></div></div></div>", unsafe_allow_html=True)
    # choose tab-like simple routing
    tab = st.radio("", ["Chatbot","Blog"], horizontal=True, key="right_tab")
    if tab=="Chatbot":
        show_chat()
    else:
        show_blog()

# footer
st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)

