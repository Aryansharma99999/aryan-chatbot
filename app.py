import streamlit as st
import time

st.set_page_config(page_title='Aryan Chatbot')
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
        typing_placeholder = st.empty()
        typing_text = ''
        for char in answer:
            typing_text += char
            typing_placeholder.markdown(typing_text)
            time.sleep(0.05)
