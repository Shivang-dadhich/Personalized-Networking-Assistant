import streamlit as st
import requests
import json
from datetime import datetime

# ==========================================
# PAGE CONFIG & STATE MANAGEMENT
# ==========================================
st.set_page_config(
    page_title="Personalized Networking Assistant",
    page_icon="🤝",
    layout="wide"
)

# Initialize Session State for tracking history/feedback on frontend if mock required
if "feedback_log" not in st.session_state:
    st.session_state.feedback_log = []

# Backend URL Configuration (Maps to FastAPI AppRouter Prefix)
if "BACKEND_API_URL" in st.secrets:
    BASE_URL = st.secrets["BACKEND_API_URL"]
else:
    BASE_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000/conversation")

# ==========================================
# SIDEBAR DYNAMIC THEME SELECTOR
# ==========================================
with st.sidebar:
    st.header("🎨 Theme Customizer")
    theme_choice = st.selectbox(
        "Select Dashboard Theme:",
        ["Deep Space Dark", "Professional Navy", "Emerald Minimalist"]
    )
    
    # Map theme configurations dynamically using injection
    if theme_choice == "Deep Space Dark":
        primary, bg, text, card_bg = "#ff4b4b", "#0e1117", "#ffffff", "#1e2430"
    elif theme_choice == "Professional Navy":
        primary, bg, text, card_bg = "#00f2fe", "#0a192f", "#cbd5e1", "#172a45"
    else:
        primary, bg, text, card_bg = "#10b981", "#0f172a", "#f8fafc", "#1e293b"

    st.markdown(f"""
        <style>
        .stApp {{ background-color: {bg} !important; color: {text} !important; }}
        div[data-testid="stMetricValue"] {{ color: {primary} !important; }}
        .stButton>button {{
            background-color: {primary} !important;
            color: white !important;
            border-radius: 6px;
            font-weight: bold;
            border: none;
        }}
        .custom-card {{
            background-color: {card_bg};
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 5px solid {primary};
        }}
        .badge {{
            background-color: {primary}22;
            color: {primary};
            padding: 4px 10px;
            border-radius: 12px;
            font-weight: bold;
            font-size: 13px;
            margin-right: 5px;
            display: inline-block;
        }}
        </style>
    """, unsafe_allow_html=True)

    st.write("---")
    st.subheader("⚙️ Active Components")
    st.caption("✔️ Classifier: DistilBERT-base-uncased-mnli")
    st.caption("✔️ Generator: GPT-2 Pipeline / SmolLM2")
    st.caption("✔️ Verification: Wikipedia API Pipeline")

# Title Banner
st.title("🤝 Personalized Networking Assistant")
st.markdown("An AI-powered web framework providing dynamic context routing, professional icebreakers, and real-time validation.")
st.write("---")

# Navigation Tabs mapping directly to your 3 System Scenarios
tab1, tab2, tab3 = st.tabs([
    "🎯 Scenario 1: Smart Starters", 
    "🔍 Scenario 2: Quick Fact Verification", 
    "📊 Scenario 3: Strategy Review & Logs"
])

# ==========================================
# TAB 1: GENERATING SMART STARTERS (FIXED STATE LOSS)
# ==========================================
with tab1:
    st.subheader("Pipeline Orchestration Engine")
    st.write("Enter the context details below to trigger DistilBERT theme analysis followed by context-aware generation.")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        event_desc = st.text_area(
            "Event Description:",
            placeholder="e.g., AI for Sustainable Cities - discussing green grids and smart architecture...",
            key="event_input_field"
        )
        
        interests_input = st.text_input(
            "User Interests (Comma Separated):",
            placeholder="climate change, urban planning, machine learning",
            key="interests_input_field"
        )

    with col_right:
        st.info("💡 **Session State Fixed:** Responses are now locked in memory so clicking feedback handles won't wipe your screen data.")

    # Initialize session keys for tracking response output safely
    if "api_response_data" not in st.session_state:
        st.session_state.api_response_data = None

    if st.button("Execute Pipeline Journey"):
        if not event_desc.strip() or not interests_input.strip():
            st.error("Bhai, Event Description aur Interests dono field mandatory hain!")
        else:
            interests_list = [i.strip() for i in interests_input.split(",") if i.strip()]
            payload = {
                "event_description": event_desc.strip(),
                "user_interests": interests_list
            }

            with st.spinner("Invoking zero-shot pipeline and building structured prompt contexts..."):
                try:
                    res = requests.post(f"{BASE_URL}/generate-conversation", json=payload, timeout=45)
                    if res.status_code == 200:
                        # Save inside session state memory box
                        st.session_state.api_response_data = res.json()
                        st.success("Analysis Complete!")
                    else:
                        st.error(f"Backend Pipe Failure ({res.status_code}): {res.text}")
                        st.session_state.api_response_data = None
                except Exception as e:
                    st.error(f"Cannot bind to local port route: {str(e)}")
                    st.session_state.api_response_data = None

    # --- PERSISTENT RENDERING LAYER ---
    # This block renders data independently of state reruns
    if st.session_state.api_response_data is not None:
        stored_data = st.session_state.api_response_data
        
        st.write("---")
        # Display Extracted Themes
        st.markdown("### 🏷️ Analyzed Themes (DistilBERT Decision)")
        for theme in stored_data.get("extracted_themes", []):
            st.markdown(f'<span class="badge">{theme}</span>', unsafe_allow_html=True)
        
        # Display Conversation Starters
        st.markdown("### 💬 Target Icebreakers (GPT-2 Output)")
        starters = stored_data.get("conversation_starters", [])
        
        for idx, starter in enumerate(starters, 1):
            clean_starter = starter.strip('"\'? ')
            
            st.markdown(f"""
                <div class="custom-card">
                    <b>Starter #{idx}:</b> "{clean_starter}"
                </div>
            """, unsafe_allow_html=True)
            
            c1, c2, _ = st.columns([0.05, 0.05, 0.9])
            
            # --- THUMBS UP ACTION ---
            if c1.button("👍", key=f"up_{idx}_{clean_starter[:10]}"):
                feedback_payload = {"suggestion_text": clean_starter, "is_useful": True}
                try:
                    feedback_res = requests.post(f"{BASE_URL}/feedback", json=feedback_payload, timeout=10)
                    if feedback_res.status_code == 200:
                        st.toast("🔥 Feedback synchronized directly with server warehouse!")
                    else:
                        st.error(f"Server rejected telemetry state: {feedback_res.text}")
                except Exception as e:
                    st.error(f"Network pipeline failure: {str(e)}")

            # --- THUMBS DOWN ACTION ---
            if c2.button("👎", key=f"down_{idx}_{clean_starter[:10]}"):
                feedback_payload = {"suggestion_text": clean_starter, "is_useful": False}
                try:
                    feedback_res = requests.post(f"{BASE_URL}/feedback", json=feedback_payload, timeout=10)
                    if feedback_res.status_code == 200:
                        st.toast("🗑️ Marked as unhelpful. Sent telemetry loop to server!")
                    else:
                        st.error(f"Server rejected telemetry state: {feedback_res.text}")
                except Exception as e:
                    st.error(f"Network pipeline failure: {str(e)}")
                    
                    

# ==========================================
# TAB 2: QUICK FACT VERIFICATION
# ==========================================
with tab2:
    st.subheader("📚 External Knowledge Integration")
    st.write("Verify claims, historical reference modules, or domain terminologies using automated Wikipedia wrappers.")

    query_string = st.text_input(
        "Search or Verification Terminology:",
        placeholder="e.g., Blockchain in healthcare"
    )

    if st.button("Execute Verification Search"):
        if not query_string.strip():
            st.warning("Enter validation parameter text query.")
        else:
            payload = {"query": query_string.strip()}
            with st.spinner("Resolving semantic entity data targets via Wikipedia routing matrix..."):
                try:
                    res = requests.post(f"{BASE_URL}/fact-check", json=payload, timeout=20)
                    if res.status_code == 200:
                        data = res.json()
                        
                        #  st.markdown("### 📄 Verification Result Schema")
                        # st.json(data) # Shows structural validation metrics inside UI directly
                        
                        # Beautiful User Layout
                        st.markdown(f"""
                            <div class="custom-card">
                                <h4>🔍 Target Query: {data.get('VerifiedQueryText')}</h4>
                                <p><b>Status Summary:</b> {data.get('VerificationStatus')}</p>
                                <a href="{data.get('WikipediaSourceURL')}" target="_blank" style="color:{primary}; font-weight:bold;">
                                    🔗 Open Official Wikipedia Source Reference Link
                                </a>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(f"Verification Endpoint Issue: {res.text}")
                except Exception as e:
                    st.error(f"API Error mapping execution pipeline: {str(e)}")

# ==========================================
# TAB 3: REVIEWING PAST STRATEGIES (REAL API CALL)
# ==========================================
with tab3:
    st.subheader("📊 Server-Side Session Memory Analytics")
    st.markdown("This component invokes live backend routes to pull both conversation footprints and feedback logs.")

    # Two action triggers side-by-side to handle both histories clean
    c1, c2 = st.columns([1, 1])
    trigger_fetch = c1.button("🔄 Fetch Conversation History")
    trigger_feedback_fetch = c2.button("📋 Fetch Feedback History Log")
    
    st.write("---")

    # ------------------------------------------
    # BLOCK A: CONVERSATION HISTORY LOGS
    # ------------------------------------------
    if trigger_fetch:
        with st.spinner("Connecting to pipeline telemetry warehouse..."):
            try:
                res = requests.get(f"{BASE_URL}/history", timeout=15)
                if res.status_code == 200:
                    server_logs = res.json()
                    if not server_logs:
                        st.info("Backend database returned empty array. No historical sessions logged yet.")
                    else:
                        try:
                            server_logs = sorted(server_logs, key=lambda x: x.get("timestamp", ""), reverse=True)
                        except Exception:
                            pass

                        st.success(f"Successfully retrieved {len(server_logs)} historic conversation sessions!")
                        
                        for idx, log in enumerate(server_logs, 1):
                            desc = log.get("event_description" or "EventDescription", "N/A")
                            themes = log.get("extracted_themes" or "AnalyzedThemes", [])
                            starters = log.get("conversation_starters" or "Icebreakers", [])
                            
                            raw_ts = log.get("timestamp", "")
                            ist_time_str = "N/A"
                            if raw_ts:
                                try:
                                    from datetime import timedelta
                                    clean_ts = raw_ts.split("+")[0].split("Z")[0]
                                    dt_obj = datetime.fromisoformat(clean_ts)
                                    ist_dt = dt_obj + timedelta(hours=5, minutes=30)
                                    ist_time_str = ist_dt.strftime("%d-%b-%Y | %I:%M %p IST")
                                except Exception:
                                    ist_time_str = raw_ts[:19]

                            with st.container():
                                st.markdown(f"""
                                    <div class="custom-card">
                                        <h4>Log Run #{idx} <span style='font-size:13px; font-weight:bold; float:right; color:{primary};'>🕒 {ist_time_str}</span></h4>
                                        <p><b>Raw Event Context:</b> <i>"{desc}"</i></p>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                if themes:
                                    st.markdown("**Evaluated Themes:**")
                                    theme_badges = "".join([f'<span class="badge">{t}</span>' for t in themes])
                                    st.markdown(theme_badges, unsafe_allow_html=True)
                                
                                if starters:
                                    st.markdown("**Generated Starters:**")
                                    for s_idx, starter in enumerate(starters, 1):
                                        st.markdown(f"  `{s_idx}.` {starter}")
                                st.markdown("<br>", unsafe_allow_html=True)
                else:
                    st.error(f"Backend Retrieval Failure: {res.text}")
            except Exception as e:
                st.error(f"Execution tracking system error: {str(e)}")

    # ------------------------------------------
    # BLOCK B: EXPLICIT FEEDBACK HISTORY LOGS
    # ------------------------------------------
    if trigger_feedback_fetch:
        with st.spinner("Fetching analytical user evaluation telemetry..."):
            try:
                # Assumes your ready backend endpoint is GET /conversation/feedback or similar history log endpoint
                res = requests.get(f"{BASE_URL}/feedback", timeout=15)
                
                if res.status_code == 200:
                    feedback_logs = res.json()
                    
                    if not feedback_logs:
                        st.info("No explicit user evaluations recorded inside server logs yet.")
                    else:
                        # Sorting Latest-First based on timestamp key if present
                        try:
                            feedback_logs = sorted(feedback_logs, key=lambda x: x.get("timestamp", ""), reverse=True)
                        except Exception:
                            pass

                        st.success(f"Successfully retrieved {len(feedback_logs)} recorded feedback logs!")
                        
                        for idx, fb in enumerate(feedback_logs, 1):
                            suggestion = fb.get("suggestion_text")
                            is_useful = fb.get("action") == "like"
                            
                            
                            
                            
                            # Determine Status Tag & Color dynamically
                            if is_useful:
                                status_badge = '<span class="badge" style="background-color:#10b98122; color:#10b981;">👍 Useful (Upvoted)</span>'
                                card_border = "#10b981"
                            else:
                                status_badge = '<span class="badge" style="background-color:#ef444422; color:#ef4444;">👎 Unhelpful (Downvoted)</span>'
                                card_border = "#ef4444"

                            # Parse Timestamp safely to Indian Current Time (IST)
                            raw_ts = fb.get("timestamp", "")
                            ist_time_str = "N/A"
                            if raw_ts:
                                try:
                                    from datetime import timedelta
                                    clean_ts = raw_ts.split("+")[0].split("Z")[0]
                                    dt_obj = datetime.fromisoformat(clean_ts)
                                    ist_dt = dt_obj + timedelta(hours=5, minutes=30)
                                    ist_time_str = ist_dt.strftime("%d-%b-%Y | %I:%M %p IST")
                                except Exception:
                                    ist_time_str = raw_ts[:19]

                            # Display Feedback Entry Custom Layout Cards
                            st.markdown(f"""
                                <div class="custom-card" style="border-left: 5px solid {card_border};">
                                    <h5>Feedback Entry #{idx} <span style='font-size:12px; font-weight:normal; float:right; color:#888;'>🕒 {ist_time_str}</span></h5>
                                    <p style="margin-bottom:10px;"><b>Icebreaker Phrase:</b> <i>"{suggestion}"</i></p>
                                    {status_badge}
                                </div>
                            """, unsafe_allow_html=True)
                else:
                    st.error(f"Backend Feedback Retrieval Failure ({res.status_code}): {res.text}")
            except Exception as e:
                st.error(f"Cannot bind pipeline feedback loops: {str(e)}")