import streamlit as st
import requests
import json
from datetime import datetime
import os

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
# ADVANCED THEME MATRIX (40 UNIQUE SCHEMES)
# ==========================================
with st.sidebar:
    st.header("🎨 Palette Studio")
    
    # 1. First pick the category to organize the 40 options
    theme_category = st.selectbox(
        "Select Theme Category:",
        ["Dark IDE & Dev Pro", "Sleek Enterprise Light", "Cyberpunk & High-Contrast", "Earth, Nordic & Pastel Minimalist"]
    )
    
    # 2. Dynamically load sub-options based on category choice
    if theme_category == "Dark IDE & Dev Pro":
        theme_choice = st.selectbox("Select Workspace Profile:", [
            "1. GitHub Dark Default", "2. One Dark Pro", "3. Dracula Official", "4. Monokai Charcoal", 
            "5. Nord Deep Freeze", "6. Night Owl", "7. Tokyo Night", "8. Material Palenight", 
            "9. Solarized Dark", "10. SynthWave '84"
        ])
    elif theme_category == "Sleek Enterprise Light":
        theme_choice = st.selectbox("Select Workspace Profile:", [
            "11. GitHub Light Pristine", "12. One Light Crisp", "13. Solarized Light Calm", "14. Milk Tea Latte", 
            "15. Soft Lavender Cream", "16. Corporate Quartz", "17. Nordic Snow", "18. Minimalist Ivory", 
            "19. Mint Matcha Clean", "20. Warm Desert Clay"
        ])
    elif theme_category == "Cyberpunk & High-Contrast":
        theme_choice = st.selectbox("Select Workspace Profile:", [
            "21. Neon Outrun Blue", "22. Matrix Terminal Green", "23. Acid Lime Radioactive", "24. Hot Magenta Glow", 
            "25. Electric Turquoise", "26. Cyber Purple Grid", "27. Amber Warning", "28. Blood Ruby Dark", 
            "29. Toxic Wasteland Purple", "30. Carbon Mono Contrast"
        ])
    else:  # Earth, Nordic & Pastel Minimalist
        theme_choice = st.selectbox("Select Workspace Profile:", [
            "31. Forest Moss & Sage", "32. Ochre Autumn Ochre", "33. Terracotta Dust", "34. Warm Sandstone", 
            "35. Ocean Horizon Mist", "36. Eucalyptus Breeze", "37. Vintage Espresso Mocha", "38. Rose Quartz & Ash", 
            "39. Plum Wine Velvet", "40. Olive Grove Dusk"
        ])

    # =========================================================================
    # THE VALUE MATRIX: Primary Accent | Background | Main Text | Container Background
    # =========================================================================
    theme_map = {
        # --- CATEGORY 1: DARK IDE & DEV PRO ---
        "1. GitHub Dark Default":        ("#58a6ff", "#0d1117", "#c9d1d9", "#161b22"),
        "2. One Dark Pro":               ("#61afef", "#282c34", "#abb2bf", "#21252b"),
        "3. Dracula Official":           ("#bd93f9", "#282a36", "#f8f8f2", "#343746"),
        "4. Monokai Charcoal":           ("#ffd866", "#191919", "#fcfcfa", "#222222"),
        "5. Nord Deep Freeze":           ("#88c0d0", "#2e3440", "#d8dee9", "#3b4252"),
        "6. Night Owl":                  ("#7fdbca", "#011627", "#d6deeb", "#0b2942"),
        "7. Tokyo Night":                ("#7aa2f7", "#1a1b26", "#a9b1d6", "#24283b"),
        "8. Material Palenight":         ("#ab47bc", "#292d3e", "#a6accd", "#32374d"),
        "9. Solarized Dark":             ("#2aa198", "#002b36", "#839496", "#073642"),
        "10. SynthWave '84":             ("#f92aad", "#2b213a", "#ffffff", "#3f2e56"),

        # --- CATEGORY 2: SLEEK ENTERPRISE LIGHT ---
        "11. GitHub Light Pristine":     ("#0969da", "#ffffff", "#24292f", "#f6f8fa"),
        "12. One Light Crisp":           ("#40a9ff", "#fafafa", "#383a42", "#f0f0f0"),
        "13. Solarized Light Calm":      ("#b58900", "#fdf6e3", "#586e75", "#eee8d5"),
        "14. Milk Tea Latte":            ("#b08968", "#f7f5f0", "#4a3b32", "#ede9df"),
        "15. Soft Lavender Cream":       ("#7c4dff", "#f9f8ff", "#2c2638", "#f0edff"),
        "16. Corporate Quartz":          ("#0052cc", "#f4f5f7", "#172b4d", "#ffffff"),
        "17. Nordic Snow":               ("#5e81ac", "#e5e9f0", "#2e3440", "#eceff4"),
        "18. Minimalist Ivory":          ("#111111", "#fffff8", "#222222", "#f4f4ec"),
        "19. Mint Matcha Clean":         ("#2e7d32", "#f1f8e9", "#1b5e20", "#e8f5e9"),
        "20. Warm Desert Clay":          ("#d84315", "#fbe9e7", "#3e2723", "#ffccbc"),

        # --- CATEGORY 3: CYBERPUNK & HIGH-CONTRAST ---
        "21. Neon Outrun Blue":          ("#00f2fe", "#050515", "#e0e0ff", "#0d0d2b"),
        "22. Matrix Terminal Green":     ("#00ff00", "#000000", "#33ff33", "#0a0a0a"),
        "23. Acid Lime Radioactive":     ("#ccff00", "#11140c", "#e5ff80", "#1b2114"),
        "24. Hot Magenta Glow":          ("#ff007f", "#12000d", "#ffb3d9", "#24001a"),
        "25. Electric Turquoise":        ("#00f5d4", "#001011", "#98f1ee", "#002528"),
        "26. Cyber Purple Grid":         ("#9b5de5", "#0f051d", "#f1e4ff", "#1f0c3a"),
        "27. Amber Warning":             ("#ffb703", "#141108", "#ffe8b3", "#241e0f"),
        "28. Blood Ruby Dark":           ("#e63946", "#1a0508", "#ffccd5", "#2d0f14"),
        "29. Toxic Wasteland Purple":    ("#a7ff33", "#1a0033", "#e6ccff", "#2b0054"),
        "30. Carbon Mono Contrast":      ("#ffffff", "#000000", "#ffffff", "#1a1a1a"),

        # --- CATEGORY 4: EARTH, NORDIC & PASTEL MINIMALIST ---
        "31. Forest Moss & Sage":        ("#4f772d", "#132a13", "#ecf39e", "#31572c"),
        "32. Ochre Autumn Ochre":        ("#e36414", "#3f1a04", "#fb8b24", "#5f2706"),
        "33. Terracotta Dust":           ("#e07a5f", "#2f3e46", "#f4f1de", "#354f52"),
        "34. Warm Sandstone":            ("#e29578", "#3d5a80", "#edf6f9", "#293241"),
        "35. Ocean Horizon Mist":        ("#0077b6", "#03045e", "#caf0f8", "#023e8a"),
        "36. Eucalyptus Breeze":         ("#83c5be", "#2b2d42", "#edf2f4", "#8d99ae"),
        "37. Vintage Espresso Mocha":    ("#ddb892", "#4a3728", "#f5ebe0", "#634832"),
        "38. Rose Quartz & Ash":         ("#ffb5a7", "#3d3434", "#f8edeb", "#4a3e3e"),
        "39. Plum Wine Velvet":          ("#ff4d6d", "#250914", "#fff0f3", "#380e22"),
        "40. Olive Grove Dusk":          ("#a3b18a", "#344e41", "#dad7cd", "#3a5a40"),
    }

    # Extract target values safely based on current selection
    primary, bg, text, card_bg = theme_map.get(theme_choice, ("#58a6ff", "#0d1117", "#c9d1d9", "#161b22"))

    # ==========================================
    # ULTRA-ROBUST CUSTOM CSS INJECTION LAYER (WITH SIDEBAR & NAVBAR CORRECTIONS)
    # ==========================================
    st.markdown(f"""
        <style>
        /* Base App Application Colors Override */
        .stApp, div[data-testid="stAppViewContainer"] {{ 
            background-color: {bg} !important; 
            color: {text} !important; 
        }}
        
        /* --- SIDEBAR BACKGROUND CORRECTION --- */
        section[data-testid="stSidebar"], 
        div[data-testid="stSidebarUserContent"],
        div[data-testid="stSidebarNav"] {{
            background-color: {card_bg} !important; /* Sidebar gets container style for layered contrast */
            color: {text} !important;
        }}
        
        /* --- TOP NAVBAR / HEADER BG CORRECTION --- */
        header[data-testid="stHeader"] {{
            background-color: {bg} !important;
            backdrop-filter: blur(8px);
            border-bottom: 1px solid {primary}22;
        }}
        
        /* Metric Highlight Overrides */
        div[data-testid="stMetricValue"] {{ 
            color: {primary} !important; 
        }}
        
        /* Standard Header Elements Colorization */
        h1, h2, h3, h4, h5, h6, p, span, label, caption, small {{
            color: {text} !important;
        }}
        
        /* Interactive Input & Field Containers Styling */
        div[data-baseweb="textarea"] textarea, div[data-baseweb="input"] input {{
            background-color: {bg} !important;
            color: {text} !important;
            border: 1px solid {primary}44 !important;
        }}
        
        /* Streamlit Native Block Borders (st.container(border=True)) */
        div[data-testid="stElementContainer"] div[style*="border"] {{
            background-color: {card_bg} !important;
            border: 1px solid {primary}44 !important;
        }}
        
        /* Dropdown & Selectbox Interactivity Components */
        div[data-baseweb="select"] > div {{
            background-color: {bg} !important;
            color: {text} !important;
            border: 1px solid {primary}44 !important;
        }}
        
        /* Fix for Dropdown Option POPUP list background */
        ul[role="listbox"], li[role="option"] {{
            background-color: {card_bg} !important;
            color: {text} !important;
        }}
        li[role="option"]:hover {{
            background-color: {primary} !important;
            color: {bg} !important;
        }}
        
        /* Global Button Component Re-skinning */
        .stButton>button {{
            background-color: {card_bg} !important;
            color: {text} !important;
            border: 1px solid {primary} !important;
            border-radius: 6px;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        
        /* Hover Transform Interactions */
        .stButton>button:hover {{
            background-color: {primary} !important;
            color: {bg} !important;
            box-shadow: 0 0 10px {primary}88;
        }}
        
        /* Tabs styling adjustment */
        button[data-baseweb="tab"] {{
            color: {text}aa !important;
        }}
        button[aria-selected="true"] {{
            color: {primary} !important;
            border-bottom-color: {primary} !important;
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