# 📰 Zen News: Privacy-First Neutral News Aggregator

Zen News is a minimalist, privacy-focused news aggregator that "triangulates" multiple perspectives to find the **Factual Core** of any story. It uses a local NLP pipeline (LexRank) to ensure neutral reporting without the bias of sensationalist headlines.

## 🚀 Key Features

- **Multi-Story Triangulation**: Automatically groups headlines into 3-4 major daily news events for a comprehensive digest.
- **Global reach**: Support for coverage in over 50+ countries (searchable via the RHS panel).
- **Custom Interests**: Type in any topic (e.g., "AI", "Cricket", "SpaceX") to get a multi-perspective factual core immediately.
- **Local NLP Engine**: Privacy-first summarization using `sumy` (LexRank), eliminating external LLM API dependencies for core features.
- **Zen UI**: Clean, distraction-free interface with a dedicated Right-Hand Side (RHS) control panel.
- **Guest Access**: Immediate access to neutral news without requiring a login.
- **Daily Digest**: (Coming Soon) Scheduled personalized neutral summaries via email/push.
- **Source Transparency**: A universal toggle to see the original diverse sources for every summary.

## 🛠️ Security & Privacy Audit

- ✅ **No Tracking**: Zero third-party scripts, analytic pixels, or CDNs.
- ✅ **Zero Indexing**: Configured to prevent search engine indexing.
- ✅ **Encrypted Preferences**: User settings stored securely in Supabase.
- ✅ **Privacy-First Backend**: Local NLP processing ensures your interests never leave the server.

## 📦 Setup & Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Pra6ha6/News-Aggregator.git
   cd News-Aggregator
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Secrets**:
   Create an `env_backup.txt` (or `.env` which is ignored) based on the following template (no real keys are included in the repo!):
   - `NEWS_API_KEY`: Get one from [newsapi.org](https://newsapi.org/)
   - `SUPABASE_URL` / `SUPABASE_KEY`: From your Supabase project.

4. **Run the App**:
   ```bash
   streamlit run app.py
   ```

## 📜 Methodology: Triangulation

Zen News fetches top headlines from three distinct categories:
1. **Neutral**: High-fact, low-bias wires (AP, Reuters).
2. **Left**: Reporting from a left-leaning perspective.
3. **Right**: Reporting from a right-leaning perspective.

The **Heuristic Clustering** identifies overlapping keywords to group these into stories. The **LexRank Summarizer** then extracts the sentences that appear most central to the combined reporting, resulting in a factual core that discards outlier bias.
