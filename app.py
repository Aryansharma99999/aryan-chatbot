# app.py
# SmarthSood-style portfolio with full-screen sections and floating anonymous modal (B2)
import os, re, json, time, requests
from datetime import datetime
from markdown import markdown
import streamlit as st
import streamlit.components.v1 as components

# -------- CONFIG --------
st.set_page_config(page_title="Aryan Sharma — Portfolio", layout="wide", initial_sidebar_state="collapsed")
BASE_DIR = os.path.dirname(__file__) if os.path.isdir(os.path.dirname(__file__) or "") else "."
POSTS_DIR = os.path.join(BASE_DIR, "blog_posts")
MSG_FILE = os.path.join(BASE_DIR, "anonymous_messages.txt")
ADMIN_TOKEN = "admin-aryan"   # change if desired
ADMIN_QUERY_PARAM = "admin"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "") or "8521726094"
HERO_NAME = "Aryan Sharma"
HERO_ROLE = "I'M a developer , writer , editor and a learner"

# -------- UTILITIES --------
def ensure_msg_file():
    try:
        if not os.path.exists(MSG_FILE):
            with open(MSG_FILE, "w", encoding="utf-8") as f:
                pass
    except:
        pass

def save_message(text):
    ensure_msg_file()
    msg = {"id": int(time.time() * 1000), "text": text, "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}
    try:
        with open(MSG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(msg, ensure_ascii=False) + "\n")
    except:
        pass
    # Telegram best-effort
    if TELEGRAM_BOT_TOKEN:
        try:
            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": f"📨 New anonymous message:\n\n{text}\n\nID:{msg['id']}", "parse_mode":"HTML"}
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json=payload, timeout=6)
        except:
            pass
    return msg

def load_messages():
    ensure_msg_file()
    out=[]
    try:
        with open(MSG_FILE,"r",encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                try: out.append(json.loads(line))
                except: continue
    except:
        return []
    return out

def overwrite_messages(msgs):
    try:
        with open(MSG_FILE,"w",encoding="utf-8") as f:
            for m in msgs:
                f.write(json.dumps(m, ensure_ascii=False) + "\n")
    except:
        pass

# Blog helpers
def get_post_data(slug):
    file_path = os.path.join(POSTS_DIR, f"{slug}.md")
    if not os.path.exists(file_path): return None
    with open(file_path,"r",encoding="utf-8") as f:
        content = f.read()
    md_meta={}
    body = content
    m = re.match(r'---\n(.*?)\n---', content, re.DOTALL)
    if m:
        meta = m.group(1)
        for line in meta.splitlines():
            if ":" in line:
                k,v = line.split(":",1); md_meta[k.strip()] = v.strip()
        body = content[m.end():].strip()
    html = markdown(body)
    return {"slug":slug,"title":md_meta.get("title","Untitled"),"date":md_meta.get("date","N/A"),"author":md_meta.get("author","N/A"),"summary":md_meta.get("summary",""),"html":html}

def get_all_posts():
    if not os.path.exists(POSTS_DIR): return []
    files = [f for f in os.listdir(POSTS_DIR) if f.endswith(".md")]
    posts=[]
    for f in files:
        slug=f.replace(".md","")
        p=get_post_data(slug)
        if p: posts.append(p)
    return posts

# Gallery helper (safe)
def get_gallery_images():
    try:
        root = BASE_DIR if os.path.isdir(BASE_DIR) else "."
        files = os.listdir(root)
    except:
        return []
    images=[f for f in files if f.lower().endswith((".jpg",".jpeg",".png",".webp"))]
    ignore={"vercel.png","screenshot.png"}
    return [i for i in images if i not in ignore]

# Inject CSS to remove Streamlit padding and hide menu/footer
def inject_global_css():
    css = """
    <style>
    /* Remove Streamlit paddings and UI chrome */
    .reportview-container .main .block-container{padding-top:0rem !important; padding-left:0rem !important; padding-right:0rem !important;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# -------- HERO & NAVBAR (HTML injected safely with placeholders) --------
def render_hero_nav():
    html = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    :root{--g1:#ff77e9;--g2:#8a6aff;--card:#0d0b0e;--pink:#ff53d6;--violet:#8b8bff;--cyan:#00d4ff;}
    html,body{height:100%;margin:0;font-family:Inter,system-ui,-apple-system,'Segoe UI',Roboto;}
    body{background:linear-gradient(135deg,var(--g1) 0%, var(--g2) 100%); overflow-x:hidden;}
    .glass-nav{position:fixed;top:18px;left:50%;transform:translateX(-50%);z-index:9999;background:rgba(255,255,255,0.06);backdrop-filter:blur(10px);padding:10px 20px;border-radius:16px;display:flex;gap:18px;align-items:center;max-width:1200px;width:90%;box-shadow:0 20px 50px rgba(0,0,0,0.25);}
    .nav-brand{font-weight:800;color:#fff}
    .nav-links{display:flex;gap:12px}
    .nav-links a{color:rgba(255,255,255,0.95);text-decoration:none;padding:8px 10px;border-radius:8px;font-weight:700}
    .hero-viewport{height:100vh;min-height:640px;display:flex;align-items:center;justify-content:center;padding:28px}
    .hero-card{width:min(1200px,96%);background:linear-gradient(180deg,rgba(4,3,5,0.98),rgba(10,6,10,0.98));border-radius:36px;padding:64px;position:relative;box-shadow:0 30px 80px rgba(0,0,0,0.45);overflow:hidden}
    #tsparticles{position:absolute;inset:0;z-index:0;border-radius:36px}
    .hero-inner{position:relative;z-index:2;color:#fff;text-align:center}
    .hero-title{font-size:56px;font-weight:800;color:var(--pink);margin:0;letter-spacing:-1px}
    .hero-role{font-size:20px;font-weight:700;color:var(--violet);margin:8px 0 18px 0}
    .hero-desc{max-width:900px;margin:0 auto 28px;color:rgba(255,255,255,0.9);line-height:1.6}
    .cta-row{display:flex;gap:14px;justify-content:center;margin-bottom:18px}
    .btn-primary{background:linear-gradient(90deg,var(--pink),var(--violet));color:#fff;padding:12px 22px;border-radius:28px;font-weight:800;text-decoration:none;box-shadow:0 16px 40px rgba(139,60,200,0.16)}
    .btn-ghost{background:transparent;color:var(--violet);padding:10px 18px;border-radius:28px;border:2px solid rgba(139,139,255,0.08);font-weight:700}
    .social-row{display:flex;gap:12px;justify-content:center;margin-top:10px}
    .social-btn{width:48px;height:48px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03);color:#dbe8ff;text-decoration:none;font-weight:700}
    /* floating FAB for anonymous message */
    .fab{position:fixed;right:20px;bottom:24px;width:64px;height:64px;border-radius:50%;background:linear-gradient(90deg,var(--pink),var(--violet));display:flex;align-items:center;justify-content:center;color:white;font-weight:800;font-size:22px;box-shadow:0 18px 40px rgba(0,0,0,0.35);z-index:9998;cursor:pointer}
    .fab:active{transform:scale(.98)}
    /* modal */
    .modal-backdrop{position:fixed;inset:0;background:rgba(0,0,0,0.45);display:flex;align-items:center;justify-content:center;z-index:10000;animation:fadeIn .18s ease-out}
    .modal-card{background:linear-gradient(180deg,#0f1114,#151517);border-radius:12px;padding:18px;width:92%;max-width:520px;box-shadow:0 30px 80px rgba(0,0,0,0.7);border:1px solid rgba(255,255,255,0.04);color:#eaf2ff;transform:translateY(8px);animation:popUp .18s ease-out}
    @keyframes popUp{from{opacity:0;transform:translateY(12px) scale(.995)}to{opacity:1;transform:translateY(0) scale(1)}}
    @keyframes fadeIn{from{opacity:0}to{opacity:1}}
    .modal-card textarea{width:100%;height:120px;border-radius:8px;padding:12px;background:#0b0c0e;border:1px solid rgba(255,255,255,0.04);color:#eaf2ff}
    .modal-actions{display:flex;gap:10px;justify-content:flex-end;margin-top:10px}
    .toast{position:fixed;right:20px;bottom:100px;background:linear-gradient(90deg,var(--pink),var(--violet));padding:10px 14px;border-radius:10px;color:#001018;font-weight:700;box-shadow:0 18px 40px rgba(0,0,0,0.3);z-index:10001;animation:toastIn .25s ease-out}
    @keyframes toastIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
    @media (max-width:980px){
      .hero-title{font-size:34px}
      .hero-card{padding:28px}
      .glass-nav{left:12px;transform:none;width:calc(100% - 24px)}
    }
    </style>

    <div class="glass-nav">
      <div class="nav-brand">Aryan</div>
      <div class="nav-links">
        <a href="#home">Home</a><a href="#about">About</a><a href="#skills">Skills</a><a href="#projects">Projects</a>
        <a href="#experience">Experience</a><a href="#photos">Photos</a><a href="#blog">Blog</a><a href="#writings">Writings</a><a href="#chat">Chatbot</a><a href="#contact">Contact</a>
      </div>
    </div>

    <div id="home" class="hero-viewport">
      <div class="hero-card">
        <div id="tsparticles"></div>
        <div class="hero-inner">
          <h1 class="hero-title">__HERO_NAME__</h1>
          <div class="hero-role">__HERO_ROLE__</div>
          <div class="hero-desc">Welcome to my personal website — explore projects, photos, writings and chat with my AI assistant.</div>
          <div class="cta-row">
            <a class="btn-primary" href="/resume.pdf" target="_blank">Download Resume</a>
            <a class="btn-ghost" href="#contact">Get In Touch</a>
          </div>
          <div class="social-row">
            <a class="social-btn" href="https://github.com/aryansharma99999" target="_blank" title="GitHub">GH</a>
            <a class="social-btn" href="https://instagram.com/aryanxsharma26" target="_blank" title="Instagram">IG</a>
            <a class="social-btn" href="mailto:aryanxsharma26@gmail.com" title="Email">✉️</a>
          </div>
        </div>
      </div>
    </div>

    <!-- Floating action button -->
    <div id="fab" class="fab">✉</div>

    <!-- Modal placeholder -->
    <div id="modal-root"></div>

    <!-- Toast placeholder -->
    <div id="toast-root"></div>

    <script>
      // particles loader
      (function(){
        function initParticles(){
          if(window.tsParticles){
            tsParticles.load("tsparticles", {
              fullScreen:{enable:false},
              particles:{number:{value:28}, color:{value:["#ff6ad1","#8b8bff","#00d4ff"]}, shape:{type:"circle"}, opacity:{value:0.65}, size:{value:{min:2,max:6}}, move:{enable:true,speed:0.6,outModes:"out"}}, detectRetina:true
            });
          } else {
            var s = document.createElement('script'); s.src="https://cdn.jsdelivr.net/npm/tsparticles@2.3.4/tsparticles.bundle.min.js"; s.onload=initParticles; document.head.appendChild(s);
          }
        }
        initParticles();
      })();

      // fab open modal -> set modal HTML
      document.getElementById('fab').addEventListener('click', function(){
        const modalRoot = document.getElementById('modal-root');
        modalRoot.innerHTML = `
          <div class="modal-backdrop" id="modal-backdrop">
            <div class="modal-card">
              <div style="font-weight:800;font-size:16px;margin-bottom:8px">Send an anonymous message</div>
              <textarea id="anon_text" placeholder="Share a thought..."></textarea>
              <div class="modal-actions">
                <button id="anon_cancel" style="background:transparent;border:1px solid rgba(255,255,255,0.08);padding:8px 12px;border-radius:8px;color:#dbe8ff">Cancel</button>
                <button id="anon_send" style="background:linear-gradient(90deg,#ff77e9,#8a6aff);border:none;padding:8px 12px;border-radius:8px;color:#001018;font-weight:800">Send anonymously</button>
              </div>
            </div>
          </div>
        `;
        document.getElementById('anon_cancel').addEventListener('click', function(){ modalRoot.innerHTML=''; });
        document.getElementById('anon_send').addEventListener('click', function(){
          var v = document.getElementById('anon_text').value;
          if(!v || !v.trim()){ alert('Write a message'); return; }
          // submit by opening same page with query param anon_q
          const params = new URLSearchParams(); params.set('anon_q', v);
          window.location.search = params.toString();
        });
      });

      // smooth scroll for nav anchors
      document.querySelectorAll('.nav-links a').forEach(function(a){
        a.addEventListener('click', function(e){
          e.preventDefault();
          var id = a.getAttribute('href').replace('#',''); var el = document.getElementById(id);
          if(el){ el.scrollIntoView({behavior:'smooth', block:'start'}); }
        });
      });
    </script>
    """
    html = html.replace("__HERO_NAME__", HERO_NAME).replace("__HERO_ROLE__", HERO_ROLE)
    components.html(html, height=900, scrolling=False)

# -------- MAIN PAGE SECTIONS (streamlit rendered but styled) --------
def render_sections():
    st.markdown('<div style="max-width:1200px;margin:20px auto 80px;padding:0 16px;">', unsafe_allow_html=True)

    # ABOUT
    st.markdown('<div id="about" style="height:100vh;display:flex;align-items:center;"><div style="width:100%"><h2 style="color:#8b8bff">About</h2><p style="color:rgba(0,0,0,0.65);max-width:900px">Hi, I am <strong>{}</strong>. {}. This site shows projects, photos, writings and a chatbot, styled for a modern portfolio.</p></div></div>'.format(HERO_NAME,HERO_ROLE), unsafe_allow_html=True)

    # SKILLS
    st.markdown('<div id="skills" style="height:100vh;display:flex;align-items:center;"><div style="width:100%"><h2 style="color:#8b8bff">Skills</h2><div style="max-width:900px">', unsafe_allow_html=True)
    skills = ["Python","Streamlit","Web Dev","HTML/CSS","JavaScript","React","Git","AI/ML"]
    chips = "".join([f"<span style='display:inline-block;margin:6px 6px 0 0;padding:8px 10px;border-radius:8px;background:linear-gradient(90deg,#6b5bff,#ff6ad1);color:#fff;font-weight:700'>{s}</span>" for s in skills])
    st.markdown(f"{chips}</div></div></div>", unsafe_allow_html=True)

    # PROJECTS (2-card carousel) - implemented in HTML to ensure smoothness
    projects = [
        {"title":"Draw App","tagline":"Collaborative drawing & whiteboard","desc":"A collaborative drawing app with a hand-drawn aesthetic and real-time multiuser support.","tags":["Canvas","WebSockets","Node.js"]},
        {"title":"Portfolio Builder","tagline":"Template-driven portfolio generator","desc":"A generator that creates pixel-perfect portfolios from templates and content.","tags":["React","Templates","Deploy"]}
    ]
    proj_html = """
    <style>
    .proj-section{padding:40px 0}
    .proj-wrap{max-width:1100px;margin:0 auto;background:linear-gradient(180deg,rgba(255,255,255,0.02),rgba(255,255,255,0.01));padding:18px;border-radius:14px}
    .proj-inner{display:flex;gap:20px;align-items:center}
    .proj-media{flex:1;min-height:260px;background:linear-gradient(180deg,#0f0f12,#1a1a1d);border-radius:10px;display:flex;align-items:center;justify-content:center;color:#9aa0a6}
    .proj-detail{flex:1}
    .tag{display:inline-block;background:linear-gradient(90deg,#6b5bff,#ff6ad1);color:#fff;padding:6px 10px;border-radius:999px;margin-right:8px;margin-bottom:8px;font-weight:700}
    .dots{display:flex;gap:8px;justify-content:center;margin-top:14px}
    .dot{width:10px;height:10px;border-radius:50%;background:rgba(0,0,0,0.1)}
    .dot.active{background:linear-gradient(90deg,#6b5bff,#ff6ad1)}
    @media (max-width:880px){ .proj-inner{flex-direction:column} .proj-media{width:100%} }
    </style>
    <div id="projects" class="proj-section"><h2 style="text-align:center;color:#8b8bff">Featured Projects</h2>
    <div class="proj-wrap"><div id="carousel"></div><div class="dots" id="dots"></div></div></div>
    <script>
    (function(){
      var projects = __PJSON__;
      var carousel = document.getElementById('carousel');
      var dots = document.getElementById('dots');
      var idx=0;
      function render(i){
        var p=projects[i];
        carousel.innerHTML = '<div class="proj-inner"><div class="proj-media"><div style="text-align:center"><b style="font-size:18px">'+p.title+'</b><div style="color:#888;margin-top:10px">'+p.tagline+'</div></div></div><div class="proj-detail"><h3 style="margin:0">'+p.title+'</h3><p style="color:#666">'+p.desc+'</p><div>';
        p.tags.forEach(function(t){ carousel.innerHTML += '<span class="tag">'+t+'</span>'; });
        carousel.innerHTML += '</div></div></div>';
        dots.innerHTML=''; for(var k=0;k<projects.length;k++){ var d=document.createElement('div'); d.className='dot'+(k===i?' active':''); (function(n){ d.onclick=function(){ idx=n; render(n); }; })(k); dots.appendChild(d); }
      }
      render(0);
      setInterval(function(){ idx=(idx+1)%projects.length; render(idx); },8000);
    })();
    </script>
    """
    components.html(proj_html.replace("__PJSON__", json.dumps(projects)), height=420, scrolling=False)

    # EXPERIENCE
    st.markdown('<div id="experience" style="height:100vh;display:flex;align-items:center;"><div style="width:100%"><h2 style="color:#8b8bff">Experience</h2><p style="color:rgba(0,0,0,0.65);max-width:900px">Working on personal projects and building experience across web and AI.</p></div></div>', unsafe_allow_html=True)

    # PHOTOS
    imgs = get_gallery_images()
    if imgs:
        grid_html = "<div id='photos' style='padding:40px 0'><h2 style='text-align:center;color:#8b8bff'>Photos</h2><div style='max-width:1100px;margin:14px auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px'>"
        for i in imgs:
            grid_html += f"<img src='{i}' style='width:100%;height:140px;object-fit:cover;border-radius:8px'/>"
        grid_html += "</div></div>"
        st.markdown(grid_html, unsafe_allow_html=True)
    else:
        st.markdown('<div id="photos" style="padding:40px 0"><h2 style="text-align:center;color:#8b8bff">Photos</h2><p style="text-align:center;color:rgba(0,0,0,0.6)">No photos found. Add jpg/png to repo root.</p></div>', unsafe_allow_html=True)

    # BLOG
    posts = get_all_posts()
    st.markdown('<div id="blog" style="padding:40px 0"><h2 style="text-align:center;color:#8b8bff">Blog</h2>', unsafe_allow_html=True)
    if not posts:
        st.markdown('<p style="text-align:center;color:rgba(0,0,0,0.6)">No blog posts found. Add markdown files to blog_posts/</p>', unsafe_allow_html=True)
    else:
        for p in posts:
            st.markdown(f"<div style='max-width:900px;margin:12px auto;padding:12px;border-radius:8px;background:rgba(255,255,255,0.02)'><b>{p['title']}</b><div style='color:rgba(0,0,0,0.6)'>{p['date']}</div><p>{p['summary']}</p></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # WRITINGS (full-screen section)
    st.markdown('<div id="writings" style="height:100vh;padding:40px 0"><h2 style="text-align:center;color:#8b8bff">Writings</h2>', unsafe_allow_html=True)
    msgs = load_messages()
    if not msgs:
        st.markdown('<p style="text-align:center;color:rgba(0,0,0,0.6)">No writings yet — use the ✉ button to add anonymously.</p>', unsafe_allow_html=True)
    else:
        cards_html = "<div style='max-width:1100px;margin:18px auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px'>"
        for m in sorted(msgs, key=lambda x: x.get("id",0), reverse=True):
            text = (m.get("text","")[:400] + ("..." if len(m.get("text",""))>400 else ""))
            ts = m.get("timestamp","")
            cards_html += f"<div style='background:linear-gradient(180deg,#fff,#f8f8ff);padding:14px;border-radius:10px;box-shadow:0 12px 30px rgba(2,6,23,0.05)'><div style='font-weight:700;color:#111'>{text}</div><div style='color:rgba(0,0,0,0.5);font-size:12px;margin-top:8px'>{ts}</div></div>"
        cards_html += "</div>"
        st.markdown(cards_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Chatbot (simple)
    st.markdown('<div id="chat" style="padding:40px 0"><h2 style="text-align:center;color:#8b8bff">Chatbot</h2>', unsafe_allow_html=True)
    if "chat_messages" not in st.session_state: st.session_state.chat_messages=[]
    for m in st.session_state.chat_messages[-8:]:
        if m["role"]=="user": st.markdown(f"<div style='max-width:900px;margin:6px auto;padding:10px;border-radius:8px;background:#0f1724;color:#cfe8ff'>{m['content']}</div>", unsafe_allow_html=True)
        else: st.markdown(f"<div style='max-width:900px;margin:6px auto;padding:10px;border-radius:8px;background:#f7f6ff;color:#0b0f14'>{m['content']}</div>", unsafe_allow_html=True)
    q = st.text_input("Ask me a question...", key="chat_main")
    if q:
        st.session_state.chat_messages.append({"role":"user","content":q})
        answer = {"what is your name":f"My name is {HERO_NAME}.","where are you from":"I am from India."}.get(q.lower(),"Sorry! I don't have an answer for that.")
        st.session_state.chat_messages.append({"role":"bot","content":answer})
        st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # CONTACT (end)
    st.markdown('<div id="contact" style="padding:60px 0"><h2 style="text-align:center;color:#8b8bff">Contact</h2><p style="text-align:center;color:rgba(0,0,0,0.6)">Email: <a href="mailto:aryanxsharma26@gmail.com">aryanxsharma26@gmail.com</a></p></div>', unsafe_allow_html=True)

    st.markdown('<div style="height:120px"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -------- Process anon_q param (modal submission) and show toast --------
def handle_query_params():
    qp = st.experimental_get_query_params()
    if "anon_q" in qp:
        q = qp.get("anon_q",[""])[0]
        if q and q.strip():
            save_message(q.strip())
            # Clear params to avoid duplicates
            st.experimental_set_query_params()
            # show animated toast via components.html small snippet
            toast_html = """
            <style>
            .toast{position:fixed;right:20px;bottom:100px;background:linear-gradient(90deg,#ff77e9,#8a6aff);padding:10px 14px;border-radius:10px;color:#001018;font-weight:800;box-shadow:0 18px 40px rgba(0,0,0,0.3);z-index:10001;animation:toastIn .25s ease-out}
            @keyframes toastIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
            </style>
            <div class="toast">Message sent anonymously ✓</div>
            <script>setTimeout(()=>{document.querySelector('.toast').style.transition='opacity .4s';document.querySelector('.toast').style.opacity='0';},2200);setTimeout(()=>{document.querySelector('.toast').remove();},2800);</script>
            """
            components.html(toast_html, height=0)
            st.experimental_rerun()

# -------- Admin unlocking (hidden unless token) --------
def admin_unlock_flow():
    qp = st.experimental_get_query_params()
    if ADMIN_QUERY_PARAM in qp and qp.get(ADMIN_QUERY_PARAM,[""])[0] == ADMIN_TOKEN:
        st.session_state._admin_unlocked = True

    if st.session_state.get("_admin_unlocked", False):
        # show a small admin floating control at bottom-left (not visible by default to others)
        if st.button("Open Admin (hidden)"):
            msgs = load_messages()
            st.write("Total messages:", len(msgs))
            for m in sorted(msgs, key=lambda x: x.get("id",0), reverse=True):
                with st.expander(f"ID {m.get('id')} • {m.get('timestamp')}"):
                    st.write(m.get("text"))
                    if st.button("Delete "+str(m.get("id")), key=f"deladm{m.get('id')}"):
                        new = [x for x in msgs if x.get("id") != m.get("id")]
                        overwrite_messages(new)
                        st.experimental_rerun()
            if st.button("Clear all messages", key="clearalladm"):
                overwrite_messages([])
                st.experimental_rerun()
    else:
        # show hidden input only if developer wants; we keep it not rendered by default.
        pass

# -------- MAIN --------
def main():
    inject_global_css()
    handle_query_params()
    render_hero_nav()
    render_sections()
    admin_unlock_flow()
    # small spacing
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
