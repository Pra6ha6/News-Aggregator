import streamlit as st
from auth_manager import get_auth_manager, sync_user_to_supabase

def main():
    # Privacy: prevent indexing and hide menus
    st.set_page_config(
        page_title="Zen News | Privacy-First Aggregator",
        page_icon="📰",
        layout="wide",
        initial_sidebar_state="collapsed",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': "Zen News is a privacy-first, neutral news aggregator."
        }
    )

    # Apply Zen-mode styling
    st.markdown("""
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stApp {
                background-color: #0e1117;
                color: #ffffff;
            }
        </style>
    """, unsafe_allow_html=True)

    import os
    # Environment Check
    required_secrets = ["SUPABASE_URL", "SUPABASE_KEY", "NEWS_API_KEY", "GEMINI_API_KEY", "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"]
    missing = [s for s in required_secrets if not os.getenv(s)]
    
    if missing:
        st.error(f"Missing required Secrets/Environment Variables: {', '.join(missing)}")
        st.info("Check your .env file locally or the 'Secrets' tab on Streamlit Cloud.")
        st.stop()

    auth = get_auth_manager()
    
    # Check authentication or Guest Mode
    if not st.session_state.get("connected") and not st.session_state.get("guest_mode"):
        auth.check_authentification()

    # Main Dashboard Area
    if st.session_state.get("connected") or st.session_state.get("guest_mode"):
        user_info = st.session_state.get("user_info", {"name": "Guest", "sub": "guest_id"})
        if st.session_state.get("connected"):
            sync_user_to_supabase(user_info)
        
        # Dashboard Layout: [Main Feed (3) | Control Panel (1)]
        main_col, rhs_col = st.columns([3, 1], gap="large")
        
        with rhs_col:
            st.subheader("Topic Control")
            
            # Country and Category Selection (RHS Panel)
            countries = {"United States": "us", "India": "in", "United Kingdom": "gb", "Canada": "ca", "Australia": "au"}
            # Use session state for persistent defaults
            if "country" not in st.session_state: st.session_state.country = "us"
            if "category" not in st.session_state: st.session_state.category = "general"
            
            selected_country_name = st.selectbox("Switch Country", options=list(countries.keys()), 
                                               index=list(countries.values()).index(st.session_state.country))
            st.session_state.country = countries[selected_country_name]
            
            categories = ["general", "business", "entertainment", "health", "science", "sports", "technology"]
            selected_category = st.selectbox("Switch Category", options=categories, 
                                           index=categories.index(st.session_state.category))
            st.session_state.category = selected_category
            
            st.divider()
            source_transparency = st.toggle("Source Transparency", value=False)
            
            if st.button("Logout / Exit"):
                st.session_state.connected = False
                st.session_state.guest_mode = False
                auth.logout()
                st.rerun()

        with main_col:
            st.title("📰 Zen News")
            st.caption(f"Factual Digest for {st.session_state.country.upper()} • {st.session_state.category.capitalize()}")
            st.write("---")
            
            # Fetch and Cluster News
            from news_manager import fetch_top_stories
            from summarizer import cluster_stories, triangulate_cluster
            
            with st.spinner("Synthesizing multi-story factual core..."):
                all_articles = fetch_top_stories(country=st.session_state.country, category=st.session_state.category)
                story_clusters = cluster_stories(all_articles)
                
                if not story_clusters:
                    st.warning("No news stories matched the current filters.")
                else:
                    for cluster in story_clusters:
                        summary_data = triangulate_cluster(cluster)
                        if summary_data:
                            with st.container(border=True):
                                st.subheader(summary_data["title"])
                                st.write(summary_data["factual_core"])
                                
                                # Bias Meter (Heuristic)
                                score = summary_data["bias_score"]
                                cols = st.columns([1, 4])
                                with cols[0]: st.caption(f"Bias: {score}/100")
                                with cols[1]: st.progress(score / 100)
                                
                                if source_transparency:
                                    with st.expander("View 3+ Diverse Sources"):
                                        for art in summary_data["sources"][:5]:
                                            st.caption(f"[{art['source']['name']}]({art['url']}) - {art['title']}")
    
    else:
        # Zen Landing Page with Initial Interest Selection
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("📰 Zen News")
            st.write("A sanctuary for neutral, fact-based journalism.")
            st.write("---")
            
            # Interest Selection BEFORE Guest login
            st.subheader("Select Initial Interests")
            c_col, cat_col = st.columns(2)
            with c_col:
                initial_country = st.selectbox("Country", ["United States", "India", "UK"], index=0)
            with cat_col:
                initial_category = st.selectbox("Category", ["general", "technology", "politics", "sports"], index=0)
            
            st.markdown("---")
            
            # Login Buttons
            auth_col, guest_col = st.columns(2)
            with auth_col:
                auth.login()
            with guest_col:
                if st.button("Continue as Guest", use_container_width=True):
                    st.session_state.guest_mode = True
                    st.session_state.country = "us" if initial_country == "United States" else "in" if initial_country == "India" else "gb"
                    st.session_state.category = initial_category
                    st.rerun()

            st.markdown("""
                <style>
                div.stButton > button {
                    background-color: #ffffff !important;
                    color: #000000 !important;
                    height: 40px !important;
                    border-radius: 4px !important;
                    border: 1px solid #dadce0 !important;
                    font-size: 14px !important;
                    font-weight: 500 !important;
                    margin-top: 25px !important;
                }
                </style>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
