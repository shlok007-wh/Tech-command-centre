
import streamlit as st
import feedparser
from groq import Groq

# 1. Page Configuration
st.set_page_config(page_title="Tech Frontier Radar", page_icon="⚡", layout="wide")

# 2. Dark Card UI Styling
st.markdown("""
<style>
    .news-card {
        background-color: #1E222A;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #2E3440;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ Personal Tech Command Center")
st.caption("Live Feed Aggregator powered by Groq (Llama 3.3)")

# 3. Active RSS Feeds
FEEDS = {
    "AI & Machine Learning": "https://rss.arxiv.org/rss/cs.AI",
    "Quantum Computing": "https://phys.org/rss-feed/physics-news/quantum-physics/",
    "Software & Dev": "https://dev.to/feed",
    "Emerging Hardware": "https://spectrum.ieee.org/feeds/feed.rss"
}

# 4. SILENT BACKEND API KEY RETRIEVAL (Never shown in UI)
api_key = st.secrets.get("GROQ_API_KEY", "")

if not api_key:
    st.error("🔒 API Key Missing! Please configure `GROQ_API_KEY` in `.streamlit/secrets.toml` or Streamlit Cloud Secrets.")
    st.stop()

# 5. Sidebar Configuration (Only user settings, NO key fields)
with st.sidebar:
    st.header("⚙️ Dashboard Settings")
    selected_category = st.selectbox("Select Domain Feed", list(FEEDS.keys()))
    num_articles = st.slider("Number of items to fetch", 1, 5, 3)
    st.markdown("---")
    st.caption("🟢 Backend API Status: Connected")

# 6. Initialize Groq Client
client = Groq(api_key=api_key)

# 7. Fetch & Summarize Loop
if st.button(f"🔍 Load Latest Updates from {selected_category}"):
    st.success(f"Fetching updates from {selected_category}...")
    parsed_feed = feedparser.parse(FEEDS[selected_category])
    
    if not parsed_feed.entries:
        st.error("Unable to load feed items. Please check your internet connection or feed URL.")
        st.stop()

    for entry in parsed_feed.entries[:num_articles]:
        with st.container():
            st.markdown("---")
            st.subheader(f"📌 {entry.title}")
            st.caption(f"🔗 [Read Source Article]({entry.link})")
            
            snippet = entry.summary if 'summary' in entry else entry.title
            
            prompt = f"""
            You are a senior tech analyst. Summarize this news snippet for an engineer:
            • **Breakthrough:** (1 concise bullet point on what happened)
            • **Impact:** (1 concise bullet point on technical importance)
            
            Snippet: {snippet}
            """
            
            try:
                with st.spinner("Analyzing article..."):
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile",
                    )
                    summary = chat_completion.choices[0].message.content
                    st.markdown(summary)
            except Exception as e:
                st.error(f"Groq API Error: {e}")