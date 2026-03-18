# 📰 Zen News: Privacy-First Neutral News Aggregator

**FACTUAL • NEUTRAL • PRIVATE**

Zen News is a minimalist Streamlit-based news aggregator designed to strip away the sensationalism of modern journalism. By "triangulating" news from Neutral, Left, and Right perspectives using LLMs, it delivers a **Factual Core** summary free from loaded language.

## 🚀 Features

- **Google Authentication**: Secure user login via `streamlit-google-auth`.
- **Privacy First**: No external tracking and `noindex` headers.
- **LLM Triangulation**: Uses Gemini 1.5 Flash to synthesize factual summaries.
- **Bias Meter**: Visual indicator of source divergence.
- **Source Transparency**: One-click access to original sources.
- **Persistent Preferences**: Stored securely in Supabase.

## 🏁 Getting Started

1. **Environment Setup**: Copy `.env.example` to `.env` and add your keys.
2. **Database**: Create a `profiles` table in Supabase (see SQL in code).
3. **Run**: `pip install -r requirements.txt` then `streamlit run app.py`.
