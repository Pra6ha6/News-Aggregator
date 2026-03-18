# 📰 Zen News: Privacy-First Neutral News Aggregator

Zen News is a state-of-the-art, privacy-focused news aggregator that "triangulates" multiple perspectives to find the **Factual Core** of any story. It uses a custom Multi-Modal NLP pipeline to ensure high-accuracy, neutral reporting with zero data leakage.

## 🚀 Key Features

- **Multi-Modal Triangulation**: A two-step process that scavenges the general news landscape, identifies top "modal" topics, and performs deep-dive multi-source searches for each event.
- **Universal Translation**: Automatic language detection and translation (🌐) for non-English sources, enabling a global factual core from anywhere in the world.
- **Point-by-Point Synthesis**: Summaries are structured into scannable bullet points for clarity and speed.
- **Dedicated Fact Extraction**: Each story includes a "**📍 Key Facts & Entities**" section pulling names, locations, and data points directly from the triangulation pool.
- **Maximum Perspective Diversity**: Strict **1-Article-per-Source** rule ensures every digest reflects 4-5 unique providers.
- **Global reach**: Support for over 50+ countries with automatic fallback for regional news availability.
- **Custom Interests**: Real-time factual core generation for any user-input topic.
- **Zen UI**: Minimalist, high-performance dashboard with a dedicated Topic Control panel.

## 🛠️ Security & Privacy Audit

- ✅ **No Tracking**: Zero third-party scripts, analytic pixels, or CDNs.
- ✅ **Zero Indexing**: Configured to prevent search engine indexing.
- ✅ **Encrypted Preferences**: User settings stored securely in Supabase.
- ✅ **Secure Git**: Sanitized repository history with all secrets excluded.

## 📦 Setup & Installation

1. **Clone & Install**:
   ```bash
   git clone https://github.com/Pra6ha6/News-Aggregator.git
   cd News-Aggregator
   pip install -r requirements.txt
   ```

2. **Run the App**:
   ```bash
   streamlit run app.py
   ```

## 📜 Methodology: The Neutrality Engine

Zen News operates on a recursive scavenging loop:
1. **Scavenge**: Fetch 100+ headlines for the selected region/category.
2. **Detect**: Identify the most prominent "Modal Topics" via keyword-pair frequency.
3. **Deep Search**: For each topic, perform a dedicated multi-source query.
4. **Translate**: Convert all native-language articles to English.
5. **Triangulate**: Extract the overlapping factual core using LexRank across diverse sources and structure it into scannable points.
