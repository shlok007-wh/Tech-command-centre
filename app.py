import os
import re
import streamlit as st
import feedparser
from groq import Groq

# 1. Page Configuration
st.set_page_config(
    page_title="Tech Frontier Radar", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CSS Animations & Theme Styling
st.markdown("""
<style>
    /* Global Background */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #0f172a 0%, #020617 100%);
        color: #f8fafc;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.85) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(56, 189, 248, 0.2);
    }

    /* Sidebar Card Panels */
    .sidebar-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 16px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }

    .sidebar-card:hover {
        border-color: #818cf8;
        box-shadow: 0 0 15px rgba(129, 140, 248, 0.3);
    }

    /* Title Styling */
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.025em;
    }

    .sub-caption {
        font-size: 1rem;
        color: #94a3b8;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 1.5rem;
    }

    /* Base Article Container */
    [data-testid="stVerticalBlock"] > div:has(div.article-anchor) {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
    }

    /* Hover State for Article Box */
    [data-testid="stVerticalBlock"] > div:has(div.article-anchor):hover {
        border-color: #38bdf8;
        box-shadow: 0 12px 30px -10px rgba(56, 189, 248, 0.35);
        background: rgba(30, 41, 59, 0.95);
    }

    /* Slide-In Hover Details (Hides by default, slides in from left on hover) */
    .reveal-details {
        max-height: 0px;
        opacity: 0;
        transform: translateX(-40px);
        overflow: hidden;
        transition: transform 0.5s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.4s ease, max-height 0.6s ease;
    }

    /* Trigger Slide-In from Left on Hover */
    [data-testid="stVerticalBlock"] > div:has(div.article-anchor):hover .reveal-details {
        max-height: 500px;
        opacity: 1;
        transform: translateX(0px);
        margin-top: 15px;
        padding-top: 15px;
        border-top: 1px dashed rgba(56, 189, 248, 0.3);
    }

    /* Primary Action Button */
    .stButton>button {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
        color: #ffffff;
        border: none;
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: 700;
        letter-spacing: 0.03em;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
        width: 100%;
    }

    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 25px rgba(56, 189, 248, 0.5);
    }

    /* Status Badge */
    .status-badge {
        background: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid rgba(74, 222, 128, 0.3);
        padding: 10px 14px;
        border-radius: 10px;
        font-weight: 600;
        text-align: center;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

# Main Title Header
st.markdown('<div class="main-title">⚡ Tech Frontier Radar</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-caption">Live Feed Aggregator • Powered by Groq (Llama 3.3)</div>', unsafe_allow_html=True)

# 3. Active High-Signal RSS Feeds
FEEDS = {
    "AI & Machine Learning": "https://rss.arxiv.org/rss/cs.AI",
    "Quantum Computing": "https://phys.org/rss-feed/physics-news/quantum-physics/",
    "Software & Dev": "https://dev.to/feed",
    "Emerging Hardware": "https://spectrum.ieee.org/feeds/feed.rss"
}

# 4. Universal API Key Retrieval
api_key = os.environ.get("GROQ_API_KEY", "")

if not api_key:
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        pass

if not api_key:
    st.error("🔒 API Key Missing! Please configure `GROQ_API_KEY` in Environment Variables or Secrets.")
    st.stop()

# 5. Interactive Theme-Matched Sidebar
with st.sidebar:
    st.markdown('<h2 style="color:#38bdf8; font-size: 1.4rem; font-weight:800; margin-bottom: 20px;">⚙️ Your domain</h2>', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-card"><span style="color:#cbd5e1; font-weight:600;">🌐 Select Category</span>', unsafe_allow_html=True)
    selected_category = st.selectbox("Select Category", list(FEEDS.keys()), label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-card"><span style="color:#cbd5e1; font-weight:600;">📊 Select number of articles</span>', unsafe_allow_html=True)
    num_articles = st.slider("Select number of articles", 1, 5, 3, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="status-badge">🟢 you are good to go</div>', unsafe_allow_html=True)

# 6. Initialize Groq Client
client = Groq(api_key=api_key)

# Clean Text Function (Strips any raw markdown or codeblock tags from LLM response)
def clean_llm_text(text):
    text = re.sub(r'```[a-zA-Z]*', '', text)
    text = text.replace('```', '').strip()
    return text

# 7. Execution Loop
if st.button(f"🚀 Fetch Latest Breakthroughs from {selected_category}"):
    with st.spinner("⚡ Intercepting live satellite feeds..."):
        parsed_feed = feedparser.parse(FEEDS[selected_category])
        
        if not parsed_feed.entries:
            st.error("Unable to load feed items. Please check network connection.")
            st.stop()

        for idx, entry in enumerate(parsed_feed.entries[:num_articles]):
            snippet = entry.summary if 'summary' in entry else entry.title
            
            prompt = f"""
            You are a senior tech analyst. Summarize this snippet into 2 bullet points for an engineer:
            • Breakthrough: (1 concise sentence)
            • Impact: (1 concise sentence)

            Snippet: {snippet}
            """
            
            try:
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                )
                summary_text = clean_llm_text(chat_completion.choices[0].message.content)
                
                # Container Wrapper with Anchor for CSS Selection
                with st.container():
                    st.markdown('<div class="article-anchor"></div>', unsafe_allow_html=True)
                    
                    # Headline Header (Always Visible)
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #38bdf8; font-weight: bold; font-size: 0.85rem;">ARTICLE #{idx+1}</span>
                        <span style="color: #94a3b8; font-size: 0.8rem;">Hover to Reveal Details 💡</span>
                    </div>
                    <h3 style="color: #f8fafc; font-size: 1.25rem; margin: 8px 0 12px 0; font-weight: 700;">{entry.title}</h3>
                    """, unsafe_allow_html=True)
                    
                    # Slide-In Details Block (Triggers on Mouse Hover)
                    formatted_summary = summary_text.replace('\n', '<br>')
                    st.markdown(f"""
                    <div class="reveal-details">
                        <div style="margin-bottom: 12px;">
                            <a href="{entry.link}" target="_blank" style="color: #818cf8; text-decoration: none; font-size: 0.9rem; font-weight: 600;">
                                🔗 Read Full Source Article →
                            </a>
                        </div>
                        <div style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.6;">
                            {formatted_summary}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Groq Analysis Error: {e}")
