import os
import re
import time
from markdown import markdown
import streamlit as st 

# Make sure this is the exact line in your app.py
st.set_page_config(page_title='Aryan Chatbot & Blog', layout="wide", initial_sidebar_state="expanded")
# --- 1. BLOG UTILITY FUNCTIONS (Reads and Parses Posts) ---

POSTS_DIR = os.path.join(os.path.dirname(__file__), 'blog_posts')

def get_post_data(slug):
    """Reads and processes a single blog post."""
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
    """Gets metadata for all available posts."""
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
            
    # Attempt to sort by date (newest first)
    try:
        all_metadata.sort(key=lambda x: time.strptime(x['date'], '%B %d, %Y'), reverse=True)
    except:
        pass
        
    return all_metadata

# --- 2. BLOG STREAMLIT RENDERING FUNCTIONS ---

def render_post_detail(post_slug):
    """Displays a single blog post page."""
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
    """Displays the list of all blog posts."""
    st.header("My Blog")
    posts = get_all_posts_metadata()
    
    if not posts:
        st.info("No blog posts have been published yet!")
        return

    for post in posts:
        with st.container(border=True):
            st.subheader(post['title'])
            st.caption(f"Published: {post['date']}")
            st.write(post['summary'])

            if st.button("Read More →", key=f"read_{post['slug']}"):
                st.session_state.blog_view = 'detail'
                st.session_state.current_post_slug = post['slug']
                st.rerun()

def blog_app():
    """Main function for the blog page flow."""
    if 'blog_view' not in st.session_state:
        st.session_state.blog_view = 'index'
    if 'current_post_slug' not in st.session_state:
        st.session_state.current_post_slug = None

    if st.session_state.blog_view == 'detail' and st.session_state.current_post_slug:
        render_post_detail(st.session_state.current_post_slug)
    else:
        render_blog_index()

# --- 3. MAIN NAVIGATION AND APP LOGIC ---

# Initialize Page State 
if 'app_page' not in st.session_state:
    st.session_state.app_page = 'Chatbot' # Default page

# Sidebar for Navigation
st.sidebar.title("Navigation")

# Create the radio selection for navigation
page_selection = st.sidebar.radio(
    "Go to:", 
    ["Chatbot", "Blog"],
    key='page_selector',
    # Set the initial selection based on the current state
    index=["Chatbot", "Blog"].index(st.session_state.app_page)
)

# If the user selects a new page, update state and rerun
if st.session_state.app_page != page_selection:
    st.session_state.app_page = page_selection
    st.rerun()

# --- Conditional Page Rendering ---

if st.session_state.app_page == "Chatbot":
    # --- Existing Chatbot Logic Starts Here ---
    
    st.title('Ask Me Anything!')
    st.subheader('I will answer questions about myself.')

    # Your questions and answers
    question_bank = {
        'what is your name': 'My name is Aryan.',
        'where are you from': 'I am from India.',
        'what do you do': 'I am passionate about technology and building websites.',
        'what are your hobbies': 'I love coding, learning new things, and helping others.',
        'how can i contact you': 'You can contact me via email: aryan@example.com'
    }

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message['role'], avatar='🤖' if message['role'] == 'system' else '👤'):
            st.markdown(message['content'])

    user_input = st.chat_input('Ask me a question...')

    if user_input:
        message = {
            'role': 'user',
            'content': user_input
        }
        st.session_state.messages.append(message)
        with st.chat_message('user', avatar='👤'):
            st.markdown(user_input)

        answer = question_bank.get(user_input.lower(), "Sorry! I don't have an answer for that.")

        message = {
            'role': 'system',
            'content': answer
        }
        st.session_state.messages.append(message)
        with st.chat_message('system', avatar='🤖'):
            # The typing simulation is slightly modified to work correctly in Streamlit's rerun cycle
            typing_placeholder = st.empty()
            typing_text = ''
            for char in answer:
                typing_text += char
                typing_placeholder.markdown(typing_text)
                time.sleep(0.05)
            # Ensure the final answer remains
            typing_placeholder.markdown(answer)

    # --- Existing Chatbot Logic Ends Here ---

elif st.session_state.app_page == "Blog":
    blog_app() # Run the blog functionality
