import os
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

# 2. Techy Custom CSS & Keyframe Animations
st.markdown("""
<style>
    /* Global Page Styling */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #0f172a 0%, #020617 100%);
        color: #f8fafc;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* Animated Glowing Title */
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: pulseGlow 4s ease-in-out infinite alternate;
        letter-spacing: -0.025em;
    }

    @keyframes pulseGlow {
        0% { filter: drop-shadow(0 0 5px rgba(56, 189, 248, 0.2)); }
        100% { filter: drop-shadow(0 0 20px rgba(192, 132, 252, 0.6)); }
    }

    /* Subtitle Pulse */
    .sub-caption {
        font-size: 1.05rem;
        color: #94a3b8;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 1.5rem;
    }

    /* Interactive Hover News Cards */
    .tech-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
    }

    .tech-card:hover {
        transform: translateY(-8px) scale(1.01);
        border-color: #38bdf8;
        box-shadow: 0 12px 30px -10px rgba(56, 189, 248, 0.35);
        background: rgba(30, 41, 59, 0.9);
    }

    /* Hide Details until Mouse Hover */
    .card-details {
        max-height: 0;
        opacity: 0;
        overflow: hidden;
        transition: max-height 0.6s ease-in-out, opacity 0.4s ease-in-out;
    }

    .tech-card:hover .card-details {
        max-height: 800px;
        opacity: 1;
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px dashed rgba(255, 255, 255, 0.15);
    }

    /* Tech Bullet Points */
    .summary-text {
        color: #e2e8f0;
        line-height: 1.6;
        font-size: 0.98rem;
    }

    /* Custom Button Styling */
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
        background: linear-gradient(135deg, #1d4ed8 0%, #6d28d9 100%);
    }

    /* Sidebar Status Badge */
    .status-badge {
        background: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid rgba(74, 222, 128, 0.3);
        padding: 8px 12px;
        border-radius: 8px;
        font-weight: 600;
        text-align: center;
        letter-spacing: 0.05em;
        animation: blinkStatus 2s infinite;
    }

    @keyframes blinkStatus {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
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

# 5. Sidebar Controls with Updated Labels
with st.sidebar:
    st.markdown("### ⚙️ Your domain")
    selected_category = st.selectbox("Select Category", list(FEEDS.keys()), label_visibility="collapsed")
    
    st.write("")
    st.markdown("### 📊 Select number of articles")
    num_articles = st.slider("Select number of articles", 1, 5, 3, label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown('<div class="status-badge">🟢 you are good to go</div>', unsafe_allow_html=True)

# 6. Initialize Groq Client
client = Groq(api_key=api_key)

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
            You are a senior tech analyst. Summarize this news snippet for an engineer:
            • **Breakthrough:** (1 concise bullet point on what happened)
            • **Impact:** (1 concise bullet point on technical importance)
            
            Snippet: {snippet}
            """
            
            try:
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                )
                summary_text = chat_completion.choices[0].message.content
                
                # HTML Format Conversion for clean rendering inside CSS card
                formatted_summary = summary_text.replace('\n', '<br>').replace('**', '<b>').replace('**', '</b>')
                
                # Render Animated Hover Card
                card_html = f"""
                <div class="tech-card">
                    <div style="display: flex; justify-space-between; align-items: center;">
                        <span style="color: #38bdf8; font-weight: bold; font-size: 0.85rem; letter-spacing: 0.05em;">ARTICLE #{idx+1}</span>
                        <span style="color: #94a3b8; font-size: 0.8rem; float: right;">Hover for AI Insights 💡</span>
                    </div>
                    <h3 style="color: #f8fafc; font-size: 1.25rem; margin: 10px 0; font-weight: 700;">{entry.title}</h3>
                    <a href="{entry.link}" target="_blank" style="color: #818cf8; text-decoration: none; font-size: 0.9rem; font-weight: 600;">
                        🔗 Read Source Document →
                    </a>
                    
                    <div class="card-details">
                        <div class="summary-text">
                            {formatted_summary}
                        </div>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Groq Analysis Error: {e}")
