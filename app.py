import streamlit as st
import google.generativeai as genai
import pandas as pd
import PyPDF2
import os
import base64
import re

# --- FIND LOGOS FOR APP CONFIG ---
files_in_directory = os.listdir('.')

# Favicon (Browser Tab)
favicon_file = next((f for f in files_in_directory if f.lower().startswith('logo.') and f.lower().endswith(('.png', '.jpg', '.jpeg'))), "🧠")

# Target specific logo filenames
roundpeg_logo_file = next((f for f in files_in_directory if f.lower() == 'rplogopill.jpg'), None)
minutemaid_logo_file = next((f for f in files_in_directory if f.lower().startswith('minutemaid_logo.') and f.lower().endswith(('.png', '.jpg', '.jpeg'))), None)

# 1. App Configuration
st.set_page_config(
    page_title="Roundpeg Synthetic Research | Minute Maid", 
    layout="centered",
    page_icon=favicon_file
)

# --- UI INTRO TEXT & NAMES (For 1-on-1 Screen) ---
PERSONA_NAMES = {
    "Minute Maid Zero Sugar": "Jessica",
    "Minute Maid Carton/Refreshers": "Sarah"
}

UI_INTROS = {
    "Minute Maid Zero Sugar": "I am a busy, future-focused person who doesn't do anything by halves. I look for quick, low-stakes victories—like a great beverage—that give me a micro-pause without breaking my momentum or adding stress.",
    "Minute Maid Carton/Refreshers": "I believe life is too short to be miserable chasing distant goals, so I focus on the moment. For me, a great beverage is a micro-reward that sparks instant joy in the daily grind."
}

# --- ROUNDPEG BRAND CSS INJECTION ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@400;700&family=PT+Serif:wght@400;700&display=swap');
    
    .stApp { background-color: #FAF6EE; }
    
    /* Global Text Color */
    html, body, [class*="css"] {
        color: #6A6457 !important; 
    }

    /* SAFE TYPOGRAPHY: Georgia for chat and body text */
    p, li, a, .stMarkdown {
        font-family: 'Georgia', serif !important;
        font-weight: 400; 
        font-size: 16px; 
    }

    /* Landing Page Specific Headline */
    .landing-main-header {
        font-family: 'PT Serif', serif !important;
        color: #F39019 !important; 
        font-size: 2.8rem !important; 
        font-weight: 700 !important; 
        letter-spacing: -0.02em !important;
        line-height: 1.1 !important; 
        margin-bottom: 0.2rem !important;
        padding-top: 1rem !important;
    }

    /* Inner Pages Headline */
    .custom-main-header {
        font-family: 'PT Serif', serif !important;
        color: #F39019 !important; 
        font-size: 1.8rem !important; 
        font-weight: 700 !important; 
        letter-spacing: -0.02em !important;
        line-height: 1.1 !important; 
        margin-bottom: 0.2rem !important;
        padding-top: 1rem !important;
    }
    
    .custom-body-copy {
        font-family: 'Georgia', serif !important;
        color: #6A6457 !important;
        font-size: 1.1rem !important;
        line-height: 1.5 !important;
        margin-top: 0 !important;
        margin-bottom: 2.5rem !important;
    }

    /* UNIFIED SUB-HEADERS */
    .landing-sub-header {
        font-family: 'PT Serif', serif !important;
        color: #6A6457 !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        margin-top: 0 !important;
        margin-bottom: 0.5rem !important;
        padding-bottom: 0.3rem !important;
        border-bottom: 1px solid rgba(106, 100, 87, 0.4) !important;
        display: block !important;
    }

    /* Selectbox Styling */
    div[data-baseweb="select"] * {
        font-family: 'Libre Franklin', sans-serif !important;
    }

    /* Navigation & Metadata: Libre Franklin */
    [data-testid="stSidebar"] {
        background-color: #FDFBF7; 
        border-right: 1px solid rgba(106, 100, 87, 0.1);
    }
    
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown {
        font-family: 'Libre Franklin', sans-serif !important;
    }
    
    /* Tighten up Sidebar Element Spacing */
    [data-testid="stSidebar"] .stMarkdown {
        margin-bottom: -0.25rem !important;
    }

    /* --- CHAT BUBBLES --- */
    .stChatMessage.assistant {
        background-color: #FFFFFF; 
        border: 1px solid rgba(243, 144, 25, 0.15); 
        border-radius: 20px; 
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(106, 100, 87, 0.05);
        margin-bottom: 1.5rem;
    }

    .stChatMessage.user {
        background-color: rgba(243, 144, 25, 0.08); 
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }

    /* --- EXPANDER STYLING --- */
    [data-testid="stExpander"] {
        border: 1px solid rgba(106, 100, 87, 0.2) !important;
        border-radius: 8px !important;
        background-color: #FDFBF7 !important;
        margin-top: 1rem !important;
        margin-bottom: 2rem !important;
    }
    [data-testid="stExpander"] summary p {
        font-weight: 700 !important;
        color: #F39019 !important;
        font-family: 'Libre Franklin', sans-serif !important;
    }

    /* Layout Route Buttons & Download Buttons */
    .stButton>button, .stDownloadButton>button {
        width: 100% !important;
        min-height: 3rem !important;
        border-radius: 8px;
        border: 1px solid rgba(243, 144, 25, 0.4) !important; 
        background-color: #FFFFFF;
        color: #F39019;
        font-weight: 700;
        font-family: 'Libre Franklin', sans-serif !important;
        padding: 0.75rem;
        transition: all 0.3s;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        border-color: #F39019 !important;
        background-color: #FDFBF7;
        color: #F39019;
    }
    
    /* Handle long text for sidebar buttons */
    [data-testid="stSidebar"] .stDownloadButton>button, 
    [data-testid="stSidebar"] .stButton>button {
        height: auto !important; 
        min-height: 3rem !important;
        padding: 0.85rem !important;
        white-space: normal !important;
        line-height: 1.3 !important;
        margin-bottom: 0.5rem !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- CUSTOM NATIVE AVATARS (SVG DATA URIS) ---
USER_AVATAR = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' fill='%236A6457' rx='20'/%3E%3Ctext x='50' y='75' font-family='Libre Franklin, sans-serif' font-size='65' font-weight='bold' fill='white' text-anchor='middle'%3E?%3C/text%3E%3C/svg%3E"
ASSISTANT_AVATAR = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' fill='%23F39019' rx='20'/%3E%3Ctext x='50' y='75' font-family='Libre Franklin, sans-serif' font-size='65' font-weight='bold' fill='white' text-anchor='middle'%3E!%3C/text%3E%3C/svg%3E"

# --- INITIALIZE ROUTING & STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "app_mode" not in st.session_state:
    st.session_state.app_mode = "landing"
if "selected_mindset" not in st.session_state:
    st.session_state.selected_mindset = "Minute Maid Carton/Refreshers"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "focus_messages" not in st.session_state:
    st.session_state.focus_messages = []
if "heatmap_messages" not in st.session_state:
    st.session_state.heatmap_messages = []
if "compare_messages" not in st.session_state:
    st.session_state.compare_messages = []

# ==========================================
# LOGIN WALL LOGIC
# ==========================================
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if roundpeg_logo_file:
            st.image(roundpeg_logo_file, width=150)
        else:
            st.markdown("<h2 style='font-family: \"PT Serif\", serif; color: #F39019;'>ROUNDPEG</h2>", unsafe_allow_html=True)
            
        st.markdown('<div class="custom-main-header" style="padding-top: 0 !important; font-size: 2.2rem !important;">Client Portal</div>', unsafe_allow_html=True)
        st.markdown('<div class="custom-body-copy">Secure access to the Roundpeg Growth Consumer Activation Engine.</div>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Log In", use_container_width=True)
            
            if submit_button:
                if username.lower().strip() == "minutemaid" and password == "mindsets2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
                    
    st.stop()


# Function to clear chats when selection changes
def update_mindset():
    st.session_state.selected_mindset = st.session_state.mindset_dropdown
    st.session_state.messages = []
    st.session_state.focus_messages = []
    st.session_state.heatmap_messages = []

# --- DATA PROCESSING UTILITIES ---
def extract_text_from_pdf_path(file_path):
    try:
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ""
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def extract_text_from_uploaded_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

@st.cache_data
def load_embedded_data(prefix, mindset_name):
    # This strictly looks for external files uploaded to the directory
    formatted_name = mindset_name.lower().replace(" ", "_").replace("/", "_")
    for ext in ['txt', 'pdf', 'xlsx', 'csv']:
        file_path = f"{prefix}_{formatted_name}.{ext}"
        if os.path.exists(file_path):
            if ext == 'txt':
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            elif ext == 'pdf':
                return extract_text_from_pdf_path(file_path)
            elif ext == 'xlsx':
                df = pd.read_excel(file_path)
                return df.to_string()
            elif ext == 'csv':
                df = pd.read_csv(file_path)
                return df.to_string()
    return None

@st.cache_data
def get_raw_file(prefix, mindset_name):
    formatted_name = mindset_name.lower().replace(" ", "_").replace("/", "_")
    for ext in ['pdf', 'txt', 'xlsx', 'csv']:
        file_path = f"{prefix}_{formatted_name}.{ext}"
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return f.read(), file_path, ext
    return None, None, None

mindset_data = load_embedded_data("profile", st.session_state.selected_mindset)
journal_data = load_embedded_data("journal", st.session_state.selected_mindset)

# 2. Sidebar Layout
with st.sidebar:
    if minutemaid_logo_file:
        logo_col1, logo_col2, logo_col3 = st.columns([0.125, 0.75, 0.125])
        with logo_col2:
            st.image(minutemaid_logo_file, use_container_width=True)
    else:
        st.markdown("<h2 style='text-align: center; font-family: \"PT Serif\", serif;'>MINUTE MAID</h2>", unsafe_allow_html=True)
        
    st.markdown(
        """
        <div style="font-size: 0.9rem; line-height: 1.5; padding-top: 5px; margin-bottom: 5px;">
        Minute Maid has partnered with Roundpeg Consulting to identify distinct Growth Consumers that drive beverage choices, focusing on the Carton/Refreshers and Zero Sugar portfolio. Given the volume of insights generated, generative AI allows us to safely explore these segments in greater depth. Choose a Growth Consumer profile and let the learning begin...
        </div>
        """, 
        unsafe_allow_html=True
    )

    st.markdown("---")
    
    if st.session_state.app_mode != "landing":
        if st.button("← Back to Suite", use_container_width=True):
            st.session_state.app_mode = "landing"
            st.rerun()
        st.markdown("---")

    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except KeyError:
        st.error("API key not found. Please set GEMINI_API_KEY in Streamlit secrets.")
        st.stop()

    genai.configure(api_key=api_key)
    selected_model = "gemini-2.5-flash"
    
    st.markdown("**Which Growth Consumer would you like to learn about?**")
    mindset_options = [
        "Minute Maid Carton/Refreshers", 
        "Minute Maid Zero Sugar"
    ]
    
    st.selectbox(
        "Desired Growth Consumer", 
        options=mindset_options, 
        index=mindset_options.index(st.session_state.selected_mindset),
        key="mindset_dropdown",
        on_change=update_mindset,
        label_visibility="collapsed"
    )
    
    raw_bytes, file_name, ext = get_raw_file("profile", st.session_state.selected_mindset)
    
    if raw_bytes:
        mime_type = "application/pdf"
        if ext == "txt": mime_type = "text/plain"
        elif ext == "xlsx": mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif ext == "csv": mime_type = "text/csv"
        
        st.download_button(
            label=f"Click to download a one-pager on {st.session_state.selected_mindset}",
            data=raw_bytes,
            file_name=file_name,
            mime=mime_type,
            use_container_width=True
        )
    else:
        st.button(f"One-pager for {st.session_state.selected_mindset} is unavailable", disabled=True, use_container_width=True)

    if st.button("Click to learn more about the power of Growth Consumers", use_container_width=True):
        st.session_state.app_mode = "mindsets_power"
        st.rerun()
        
    st.markdown("---")
    
    if st.button("Log Out", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

model = genai.GenerativeModel(selected_model)

# 3. Main Panel Header
if roundpeg_logo_file:
    rp_col1, rp_col2 = st.columns([0.15, 0.85])
    with rp_col1:
        st.image(roundpeg_logo_file, use_container_width=True)

# ==========================================
# ROUTE: THE POWER OF MINDSETS
# ==========================================
if st.session_state.app_mode == "mindsets_power":
    st.markdown('<div class="custom-main-header">The Power of Growth Consumers</div>', unsafe_allow_html=True)
    st.markdown('<div class="custom-body-copy">Placeholder content. You can drop in an article, a video link, or general educational content about behavioral science here!</div>', unsafe_allow_html=True)


# ==========================================
# ROUTE 1: LANDING PAGE
# ==========================================
elif st.session_state.app_mode == "landing":
    st.markdown('<div class="landing-main-header">Synthetic Insight Experiences</div>', unsafe_allow_html=True)
    st.markdown('<div class="custom-body-copy">Select your desired Growth Consumer, then choose your preferred qualitative methodology below.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="landing-sub-header">1-on-1 Interview</div>', unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.95rem; margin-top: 0; margin-bottom: 1rem;'>Engage deeply with a unified persona representing the core Growth Consumer to uncover defining values, motivations, and behaviors.</p>", unsafe_allow_html=True)
        if st.button("Launch Interview", use_container_width=True):
            st.session_state.app_mode = "1_on_1"
            st.rerun()
            
    with col2:
        st.markdown('<div class="landing-sub-header">Focus Group Pre Field</div>', unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.95rem; margin-top: 0; margin-bottom: 1rem;'>Test your discussion guide against a dynamic panel of synthetic consumers before recruiting live focus groups.</p>", unsafe_allow_html=True)
        if st.button("Launch Focus Group", use_container_width=True):
            st.session_state.app_mode = "focus_group"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="landing-sub-header">Directional Heatmap</div>', unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.95rem; margin-top: 0; margin-bottom: 1rem;'>Rapidly test messaging or concepts to see which directions resonate most strongly with the selected Growth Consumer.</p>", unsafe_allow_html=True)
        if st.button("Launch Heatmap", use_container_width=True):
            st.session_state.app_mode = "heatmap"
            st.rerun()
            
    with col4:
        st.markdown('<div class="landing-sub-header">Compare & Contrast</div>', unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.95rem; margin-top: 0; margin-bottom: 1rem;'>Ask one question and view side-by-side responses to see how Jessica and Sarah react differently based on their profiles.</p>", unsafe_allow_html=True)
        if st.button("Launch Compare Tool", use_container_width=True):
            st.session_state.app_mode = "compare"
            st.rerun()

# ==========================================
# ROUTE 2: 1-ON-1 INTERVIEW 
# ==========================================
elif st.session_state.app_mode == "1_on_1":
    persona_name = PERSONA_NAMES.get(st.session_state.selected_mindset, "Jessica")
    intro_text = UI_INTROS.get(st.session_state.selected_mindset, "I can help you understand our underlying values and how we make beverage choices.")
    
    st.markdown(f'<div class="custom-main-header">Hello! My name is {persona_name}. I represent the {st.session_state.selected_mindset} growth consumer.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="custom-body-copy">{intro_text} Want to know more about me and my choices?</div>', unsafe_allow_html=True)
    st.markdown('<div class="landing-sub-header">Ask me anything...</div>', unsafe_allow_html=True)
    
    if not mindset_data:
        st.error("Awaiting embedded Growth Consumer data. Please upload your rich cross-tab file to your GitHub repository.")
        st.stop()

    for message in st.session_state.messages:
        avatar_to_use = USER_AVATAR if message["role"] == "user" else ASSISTANT_AVATAR
        with st.chat_message(message["role"], avatar=avatar_to_use):
            st.markdown(message["content"])
            if "facts" in message and message["facts"]:
                with st.expander("Why do I say that?"):
                    st.markdown(message["facts"])

    journal_injection = f"Additionally, factor in the following real consumer journal ethnographies to add authentic texture to your persona:\n\n<journal_ethnographies>\n{journal_data}\n</journal_ethnographies>\n\n" if journal_data else ""

    system_instruction = f"""
    You are a synthetic growth consumer named {persona_name}, representing the "{st.session_state.selected_mindset}" target audience. 
    You act as the aggregate embodiment and collective voice of this growth consumer segment.
    Your values, attitudes, motivations, and purchasing behaviors are defined by the core data below:

    <mindset_data>
    {mindset_data}
    </mindset_data>

    {journal_injection}
    Rules for your response:
    1. Answer entirely in the first person ("I", "my") as {persona_name}.
    2. Embody the tone, fears, and desires outlined in the core data.
    3. You MUST structure your response into exactly two parts, separated by this exact delimiter: |||
    4. Part 1 (Before the delimiter): Your conversational first-person response.
    5. Part 2 (After the delimiter): Exactly 5 factual bullet points drawn directly from the data that support why you answered that way. Do not include any intro text in Part 2.
    """

    if prompt := st.chat_input("Engage with the Growth Consumer..."):
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(prompt)
        # Cap chat history context for speed (saving the last 6 interactions)
        st.session_state.messages.append({"role": "user", "content": prompt})
        recent_messages = st.session_state.messages[-7:]

        full_prompt = system_instruction + "\n\n"
        for msg in recent_messages:
            full_prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"
        
        with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
            message_placeholder = st.empty()
            full_response = ""
            try:
                response = model.generate_content(full_prompt, stream=True)
                for chunk in response:
                    full_response += chunk.text
                    if "|||" in full_response:
                        parts = full_response.split("|||", 1)
                        message_placeholder.markdown(parts[0].strip() + "▌")
                    else:
                        message_placeholder.markdown(full_response + "▌")
                
                if "|||" in full_response:
                    parts = full_response.split("|||", 1)
                    main_text = parts[0].strip()
                    facts_text = parts[1].strip()
                    
                    message_placeholder.markdown(main_text)
                    with st.expander("Why do I say that?"):
                        st.markdown(facts_text)
                        
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": main_text,
                        "facts": facts_text
                    })
                else:
                    message_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"An error occurred: {e}")


# ==========================================
# ROUTE 3: FOCUS GROUP PRE FIELD
# ==========================================
elif st.session_state.app_mode == "focus_group":
    st.markdown('<div class="custom-main-header">Welcome to the synthetic focus group experience</div>', unsafe_allow_html=True)
    
    if not journal_data:
        st.warning(f"Focus groups perform best with diverse consumer journals. No journals found for '{st.session_state.selected_mindset}'. The AI will generate a panel based purely on the core profile.")
        
    if "fg_mindset" not in st.session_state or st.session_state.fg_mindset != st.session_state.selected_mindset:
        st.session_state.fg_mindset = st.session_state.selected_mindset
        st.session_state.focus_messages = []
        with st.spinner(f"Recruiting 5 synthetic participants for {st.session_state.selected_mindset}..."):
            panel_prompt = f"Create exactly 5 realistic focus group participants representing the '{st.session_state.selected_mindset}' Growth Consumer. Use this data for context:\n{mindset_data}\n\nFormat your response as a simple markdown list where each participant has a First Name, Age, and a 1-sentence profile explaining their relationship with beverages."
            try:
                resp = model.generate_content(panel_prompt)
                st.session_state.fg_panel_text = resp.text
            except Exception as e:
                st.session_state.fg_panel_text = "Panel generation failed. The AI will improvise participants during the session."

    st.markdown('<div class="landing-sub-header">Meet the focus group participants:</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown(st.session_state.fg_panel_text)
        st.markdown("<br>", unsafe_allow_html=True)
        
    for message in st.session_state.focus_messages:
        if message["role"] == "user":
            user_text = message["content"].replace("\n", "<br>")
            html = f'''
            <div style="margin-bottom: 1.5rem;">
                <div style="display: inline-block; background-color: #6A6457; color: white; padding: 4px 12px; border-radius: 4px; font-family: 'Libre Franklin', sans-serif; font-weight: bold; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 6px;">MODERATOR</div>
                <div style="background-color: rgba(243, 144, 25, 0.08); padding: 1.2rem; border-radius: 12px; font-family: 'Georgia', serif; color: #6A6457; line-height: 1.5;">{user_text}</div>
            </div>
            '''
            st.markdown(html, unsafe_allow_html=True)
        else:
            text = message["content"]
            parts = re.split(r'\[(.*?)\]', text)
            if len(parts) > 1:
                if parts[0].strip():
                    st.markdown(f"<p>{parts[0].strip()}</p>", unsafe_allow_html=True)
                for i in range(1, len(parts), 2):
                    name = parts[i].strip()
                    speech = parts[i+1].strip() if i+1 < len(parts) else ""
                    if not name or not speech: continue
                    speech_html = speech.replace("\n", "<br>")
                    html = f'''
                    <div style="margin-bottom: 1.5rem;">
                        <div style="display: inline-block; background-color: #F39019; color: white; padding: 4px 12px; border-radius: 4px; font-family: 'Libre Franklin', sans-serif; font-weight: bold; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 6px;">{name}</div>
                        <div style="background-color: #FFFFFF; border: 1px solid rgba(243, 144, 25, 0.15); padding: 1.2rem; border-radius: 12px; font-family: 'Georgia', serif; color: #6A6457; line-height: 1.5;">{speech_html}</div>
                    </div>
                    '''
                    st.markdown(html, unsafe_allow_html=True)
            else:
                text_html = text.replace("\n", "<br>")
                html = f'''
                <div style="margin-bottom: 1.5rem;">
                    <div style="display: inline-block; background-color: #F39019; color: white; padding: 4px 12px; border-radius: 4px; font-family: 'Libre Franklin', sans-serif; font-weight: bold; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 6px;">PANEL</div>
                    <div style="background-color: #FFFFFF; border: 1px solid rgba(243, 144, 25, 0.15); padding: 1.2rem; border-radius: 12px; font-family: 'Georgia', serif; color: #6A6457; line-height: 1.5;">{text_html}</div>
                </div>
                '''
                st.markdown(html, unsafe_allow_html=True)

    journal_injection = f"\n<journal_ethnographies>\n{journal_data}\n</journal_ethnographies>\n" if journal_data else ""
    focus_group_instruction = f"""
    You are simulating a focus group for the "{st.session_state.selected_mindset}" Growth Consumer. 
    The 5 participants in the panel are described below:
    {st.session_state.fg_panel_text}
    
    {journal_injection}
    
    Rules for the Focus Group:
    1. INSPIRATION OVER REGURGITATION: Do not just quote the data. Intuit how these specific people would feel, think, and react to the user's question. Let them have distinct opinions, push back on each other, and debate naturally!
    2. REQUIRED FORMAT: You MUST format the output script by placing the speaker's name in square brackets on its own line, followed by their response. Do not use bolding or colons for names. 
    Example:
    [Sarah]
    I completely agree with this concept.
    
    [Marcus]
    Really? I actually found it a bit confusing.
    """

    st.markdown("---")
    st.markdown("**How would you like to moderate?**")
    mod_mode = st.radio("Select Moderation Style", ["Ask Questions One-by-One", "Upload Full Discussion Guide"], horizontal=True, label_visibility="collapsed")
    
    if mod_mode == "Ask Questions One-by-One":
        if prompt := st.chat_input("Ask the panel a question..."):
            st.session_state.focus_messages.append({"role": "user", "content": prompt})
            st.rerun() 
            
    elif mod_mode == "Upload Full Discussion Guide":
        guide_file = st.file_uploader("Upload Discussion Guide (.txt, .pdf, .xlsx)", type=["txt", "pdf", "xlsx"])
        if guide_file and st.button("Run Focus Group", use_container_width=True):
            if guide_file.name.endswith('.txt'):
                guide_content = guide_file.getvalue().decode("utf-8")
            elif guide_file.name.endswith('.pdf'):
                guide_content = extract_text_from_uploaded_pdf(guide_file)
            elif guide_file.name.endswith('.xlsx'):
                df = pd.read_excel(guide_file)
                guide_content = df.to_string()
            else:
                guide_content = "File type not supported."
            
            st.session_state.focus_messages.append({"role": "user", "content": f"Please simulate a discussion based on this guide:\n\n{guide_content}"})
            st.rerun()

    if len(st.session_state.focus_messages) > 0 and st.session_state.focus_messages[-1]["role"] == "user":
        # Cap chat history context
        recent_messages = st.session_state.focus_messages[-7:]
        full_prompt = focus_group_instruction + "\n\n"
        for msg in recent_messages:
            prefix = "Moderator Question/Input: " if msg["role"] == "user" else "Panel: "
            full_prompt += f"{prefix}{msg['content']}\n\n"
        
        message_placeholder = st.empty()
        full_response = ""
        try:
            response = model.generate_content(full_prompt, stream=True)
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.empty()
            st.session_state.focus_messages.append({"role": "assistant", "content": full_response})
            st.rerun()
        except Exception as e:
            st.error(f"An error occurred: {e}")

# ==========================================
# ROUTE 4: RAPID DIRECTIONAL HEATMAP
# ==========================================
elif st.session_state.app_mode == "heatmap":
    st.markdown('<div class="custom-main-header">Directional Heatmap</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="custom-body-copy">Paste distinct concepts below. The AI will assign directional resonance scores and explain the underlying friction or appeal based on the <strong>{st.session_state.selected_mindset}</strong> values.</div>', unsafe_allow_html=True)
    st.markdown('<div class="landing-sub-header">Input Concepts for testing...</div>', unsafe_allow_html=True)
    
    if not mindset_data:
        st.error("Awaiting embedded Growth Consumer data. Please upload your rich cross-tab file to your GitHub repository.")
        st.stop()

    for message in st.session_state.heatmap_messages:
        avatar_to_use = USER_AVATAR if message["role"] == "user" else ASSISTANT_AVATAR
        with st.chat_message(message["role"], avatar=avatar_to_use):
            st.markdown(message["content"])

    heatmap_instruction = f"""
    You are analyzing beverage concepts, claims, or messaging through the lens of the "{st.session_state.selected_mindset}" Growth Consumer. 
    Your core values are defined below:
    <mindset_data>
    {mindset_data}
    </mindset_data>

    Task: The user will provide concepts or copy to evaluate. 
    For each distinct concept provided:
    1. Assign a directional "Resonance Score" (High, Medium, or Low).
    2. Provide a brief, punchy explanation of WHY it succeeds or fails based explicitly on this Growth Consumer's data. What creates friction? What drives appeal?
    Format your response cleanly with bold headers for each concept evaluated.
    """

    if prompt := st.chat_input("Paste concepts or copy here..."):
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(prompt)
        st.session_state.heatmap_messages.append({"role": "user", "content": prompt})

        # Cap chat history context
        recent_messages = st.session_state.heatmap_messages[-5:]
        full_prompt = heatmap_instruction + "\n\n"
        for msg in recent_messages:
            full_prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"
        
        with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
            message_placeholder = st.empty()
            full_response = ""
            try:
                response = model.generate_content(full_prompt, stream=True)
                for chunk in response:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                st.session_state.heatmap_messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"An error occurred: {e}")

# ==========================================
# ROUTE 5: COMPARE & CONTRAST
# ==========================================
elif st.session_state.app_mode == "compare":
    st.markdown('<div class="custom-main-header">Compare & Contrast</div>', unsafe_allow_html=True)
    st.markdown('<div class="custom-body-copy">Ask a single question to see how Jessica (Zero Sugar) and Sarah (Carton/Refreshers) react differently based on their unique Growth Consumer profiles.</div>', unsafe_allow_html=True)
    
    data_zs = load_embedded_data("profile", "Minute Maid Zero Sugar")
    data_cr = load_embedded_data("profile", "Minute Maid Carton/Refreshers")
    
    if not data_zs or not data_cr:
        st.error("Missing data for one or both Growth Consumers. Please ensure both profile files are uploaded to your GitHub repository.")
        st.stop()

    # Render previous dual-responses
    for msg in st.session_state.compare_messages:
        if msg["role"] == "user":
            with st.chat_message("user", avatar=USER_AVATAR):
                st.markdown(msg["content"])
        elif msg["role"] == "assistant":
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="landing-sub-header" style="color: #F39019 !important;">Jessica (Zero Sugar)</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="background-color: #FFFFFF; border: 1px solid rgba(243, 144, 25, 0.15); padding: 1.2rem; border-radius: 12px;">{msg["content_zs"]}</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="landing-sub-header" style="color: #6A6457 !important;">Sarah (Carton/Refreshers)</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="background-color: #FFFFFF; border: 1px solid rgba(106, 100, 87, 0.15); padding: 1.2rem; border-radius: 12px;">{msg["content_cr"]}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

    def generate_compare_prompt(name, segment, data, user_query):
        return f"""
        You are a synthetic growth consumer named {name}, representing the "{segment}" target audience. 
        You act as the aggregate embodiment and collective voice of this segment.
        Your values and attitudes are defined by this data:
        
        {data}
        
        Rule: Answer the user's question entirely in the first person ("I", "my") as {name} in one concise, highly conversational paragraph. Emphasize the distinct traits of your segment. Do NOT use bullet points.
        
        User Question: {user_query}
        """

    if prompt := st.chat_input("Ask a question to both Growth Consumers..."):
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(prompt)
        
        # We store user message, then immediately generate and store the dual response
        st.session_state.compare_messages.append({"role": "user", "content": prompt})
        
        col1, col2 = st.columns(2)
        
        # Generate Jessica (Zero Sugar)
        with col1:
            st.markdown('<div class="landing-sub-header" style="color: #F39019 !important;">Jessica (Zero Sugar)</div>', unsafe_allow_html=True)
            zs_placeholder = st.empty()
            prompt_zs = generate_compare_prompt("Jessica", "Minute Maid Zero Sugar", data_zs, prompt)
            
            try:
                resp_zs = model.generate_content(prompt_zs)
                zs_text = resp_zs.text
                zs_placeholder.markdown(f'<div style="background-color: #FFFFFF; border: 1px solid rgba(243, 144, 25, 0.15); padding: 1.2rem; border-radius: 12px;">{zs_text}</div>', unsafe_allow_html=True)
            except Exception as e:
                zs_text = f"Error generating response: {e}"
                zs_placeholder.error(zs_text)
                
        # Generate Sarah (Carton/Refreshers)
        with col2:
            st.markdown('<div class="landing-sub-header" style="color: #6A6457 !important;">Sarah (Carton/Refreshers)</div>', unsafe_allow_html=True)
            cr_placeholder = st.empty()
            prompt_cr = generate_compare_prompt("Sarah", "Minute Maid Carton/Refreshers", data_cr, prompt)
            
            try:
                resp_cr = model.generate_content(prompt_cr)
                cr_text = resp_cr.text
                cr_placeholder.markdown(f'<div style="background-color: #FFFFFF; border: 1px solid rgba(106, 100, 87, 0.15); padding: 1.2rem; border-radius: 12px;">{cr_text}</div>', unsafe_allow_html=True)
            except Exception as e:
                cr_text = f"Error generating response: {e}"
                cr_placeholder.error(cr_text)
                
        st.session_state.compare_messages.append({
            "role": "assistant",
            "content_zs": zs_text,
            "content_cr": cr_text
        })
        
        # Rerun to clear the raw markdown stream and ensure UI is locked in
        st.markdown("<br>", unsafe_allow_html=True)
