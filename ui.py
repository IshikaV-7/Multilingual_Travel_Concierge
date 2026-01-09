import streamlit as st
from backend import MultilingualChatbot
import json
from datetime import datetime
import base64
import os

# Set page configuration with custom theme
st.set_page_config(
    page_title="✈️ Travel Concierge",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load and encode background image
image_path = "../Gemini_Generated_Image_6fd7sj6fd7sj6fd7.png"
with open(image_path, "rb") as img_file:
    img_base64 = base64.b64encode(img_file.read()).decode()

# Add custom CSS for travel-themed aesthetic
st.markdown(f"""
    <style>
        /* Main background with image */
        .stApp {{
            background-image: url('data:image/png;base64,{img_base64}');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        
        /* Main container styling */
        [data-testid="stMainBlockContainer"] {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px !important;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            margin: 20px;
            backdrop-filter: blur(10px);
        }}
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%);
            border-radius: 20px;
            margin: 15px;
        }}
        
        [data-testid="stSidebarContent"] {{
            color: white;
        }}
        
        /* Title styling */
        h1 {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-align: center;
            font-size: 3em !important;
            font-weight: 800 !important;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }}
        
        h3 {{
            color: #667eea;
            font-weight: 700;
        }}
        
        /* Selectbox and input styling */
        .stSelectbox, .stTextInput {{
            border-radius: 10px !important;
        }}
        
        /* Button styling */
        .stButton > button {{
            border-radius: 10px !important;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            padding: 10px 20px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4) !important;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.6) !important;
        }}
        
        /* Chat message styling */
        .stChatMessage {{
            border-radius: 15px !important;
            padding: 15px !important;
        }}
        
        .stChatMessage[data-testid="chat-message-user"] {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border-radius: 15px 15px 5px 15px !important;
        }}
        
        .stChatMessage[data-testid="chat-message-assistant"] {{
            background: linear-gradient(135deg, #f093fb 0%, #4facfe 100%) !important;
            color: white !important;
            border-radius: 15px 15px 15px 5px !important;
        }}
        
        /* Chat input styling */
        .stChatInputContainer {{
            background: rgba(255, 255, 255, 0.8) !important;
            border-radius: 15px !important;
            padding: 10px !important;
        }}
        
        .stChatInput {{
            border-radius: 10px !important;
            border: 2px solid #667eea !important;
        }}
        
        .stChatInput:focus {{
            border-color: #764ba2 !important;
            box-shadow: 0 0 10px rgba(102, 126, 234, 0.4) !important;
        }}
        
        /* Divider styling */
        hr {{
            border: 1px solid rgba(102, 126, 234, 0.3) !important;
        }}
        
        /* Sidebar text color */
        .stSidebar .stSelectbox label {{
            color: white !important;
        }}
    </style>
""", unsafe_allow_html=True)

st.title("✈️ Multilingual Travel Concierge")

# Initialize sessions
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.all_chats[st.session_state.current_chat_id] = []

# Sidebar
with st.sidebar:
    language = st.selectbox("Language", [
        "English", "Spanish", "French", "German", 
        "Hindi", "Japanese", "Chinese", "Arabic"
    ])
    
    # New chat button
    if st.button("➕ New Chat"):
        st.session_state.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.all_chats[st.session_state.current_chat_id] = []
        st.rerun()
    
    st.markdown("---")
    
    # Show all previous chats
    st.markdown("### 💬 Chat History")
    for chat_id in reversed(list(st.session_state.all_chats.keys())):
        chat_messages = st.session_state.all_chats[chat_id]
        if chat_messages:
            # Get first message preview
            first_msg = chat_messages[0]["content"][:30]
            is_current = chat_id == st.session_state.current_chat_id
            
            # Show chat button
            if st.button(
                f"{'🟢' if is_current else '💬'} {first_msg}...",
                key=chat_id,
                use_container_width=True
            ):
                st.session_state.current_chat_id = chat_id
                st.rerun()

# Get current chat messages
current_messages = st.session_state.all_chats[st.session_state.current_chat_id]

# Display current chat
for msg in current_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
if prompt := st.chat_input("Type your message..."):
    
    # Show user message
    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # Get bot response
    chatbot = MultilingualChatbot()
    response = chatbot.chat(prompt, language, current_messages)
    
    # Show bot message
    current_messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.write(response)
    
    # Update chat in session
    st.session_state.all_chats[st.session_state.current_chat_id] = current_messages
    
    # Refresh
    st.rerun()