import streamlit as st
import requests
import json

# Page Configuration
st.set_page_config(
    page_title="AI Contextual Conversation Starter",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend API Configuration
BACKEND_URL = "http://127.0.0.1:8000"  # Agar tumhara port alag hai toh change kar lena

# Custom CSS for modern styling
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        border-radius: 8px;
        font-weight: bold;
    }
    .stButton>button:hover { background-color: #ff2b2b; color: white; }
    .label-box {
        background-color: #1e2430;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0px;
        border-left: 5px solid #00f2fe;
    }
    .starter-box {
        background-color: #262730;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0px;
        border-left: 5px solid #ff4b4b;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# Title & Description
st.title("🚀 Smart Conversation Starter Generator")
st.caption("Backend Model: SmolLM2-360M-Instruct | Dynamic Context Routing")
st.write("---")

# Layout: Sidebar for User Profile & Main Area for Event Input
with st.sidebar:
    st.header("👤 User Profile & Interests")
    st.info("Yeh details default pipeline parameters me use hongi.")
    
    # Static preferences mirroring your backend database mock structure
    st.markdown("**Location:** Jaipur, Rajasthan")
    st.markdown("**Interests:** Cricket, Earning, Technology")
    st.markdown("**Active Event:** IPL Auction (Echona 2025)")
    st.write("---")
    st.success("Connected to Local LLM Pipeline")

# Main Input Section
st.subheader("📢 Enter Current Event Context")
user_event_input = st.text_area(
    label="Kya chal raha hai? Paste the news hook or event details below:",
    placeholder="Example: hey an political event happens in bjp office releted to recent election...",
    height=120
)

# Generate Button Trigger
if st.button("Generate Contextual Starters"):
    if not user_event_input.strip():
        st.warning("Bhai, pehle kuch event text toh dalo!")
    else:
        with st.spinner("Backend se processing ho rahi hai aur LLM soch raha hai... 🤔"):
            try:
                # 1. Trigger API Request to FastAPI Backend
                payload = {"text": user_event_input.strip()}
                response = requests.post(f"{BACKEND_URL}/generate-starters", json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Layout breakdown: Columns for Labels vs Starters
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.subheader("🎯 Extracted Labels")
                        labels = data.get("labels", [])
                        if labels:
                            for label in labels:
                                st.markdown(f'<div class="label-box">🔹 <b>{label}</b></div>', unsafe_allow_html=True)
                        else:
                            st.write("*No dynamic labels extracted.*")
                            
                    with col2:
                        st.subheader("💬 Conversation Starters")
                        starters = data.get("conversation_starters", [])
                        
                        if starters:
                            for idx, starter in enumerate(starters, 1):
                                # Secondary cleaning layer on frontend to handle raw quotes fallback
                                clean_starter = starter.strip('"\'? ')
                                st.markdown(
                                    f'<div class="starter-box"><b>{idx}.</b> "{clean_starter}"</div>', 
                                    unsafe_allow_html=True
                                )
                        else:
                            st.error("Backend se empty starters mile! Check logic or lower the generation temperature.")
                            
                else:
                    st.error(f"Backend Returned Error Code: {response.status_code}")
                    st.json(response.json())
                    
            except requests.exceptions.ConnectionError:
                st.error("🚨 **Connection Failed!** Tumhara FastAPI server `http://127.0.0.1:8000` par run nahi kar raha hai. Terminal check karo.")
            except Exception as e:
                st.error(f"Kuch toh gadbad hui hai: {str(e)}")

# Bottom informational banner
st.write("---")
st.markdown("> **Debug Tip:** Agar model abhi bhi out-of-context baatein (jaise bhangra/microsoft) generate kar raha hai, toh backend code me temperature ko aur drop (`temperature=0.1`) kar dena.")