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
            
            from news_manager import COUNTRIES
            
            # Use session state for persistent defaults
            if "country" not in st.session_state: st.session_state.country = "us"
            if "category" not in st.session_state: st.session_state.category = "general"
            if "custom_interest" not in st.session_state: st.session_state.custom_interest = ""
            
            # Country selection (Full List)
            country_names = sorted(list(COUNTRIES.keys()))
            default_country_idx = country_names.index([k for k, v in COUNTRIES.items() if v == st.session_state.country][0])
            selected_country_name = st.selectbox("Switch Country", options=country_names, index=default_country_idx)
            st.session_state.country = COUNTRIES[selected_country_name]
            
            # Sync categories (Must match landing page)
            categories = ["general", "business", "entertainment", "health", "science", "sports", "technology"]
            cat_idx = categories.index(st.session_state.category) if st.session_state.category in categories else 0
            selected_category = st.selectbox("Switch Category", options=categories, index=cat_idx)
            st.session_state.category = selected_category
            
            st.markdown("---")
            st.write("Custom Interest")
            custom_q = st.text_input("Enter Topic (e.g. AI, Cricket)", value=st.session_state.custom_interest)
            if custom_q != st.session_state.custom_interest:
                st.session_state.custom_interest = custom_q
                st.rerun()
            
            st.divider()
            source_transparency = st.toggle("Source Transparency", value=False)
            
            if st.button("🔄 Force Digest Refresh", use_container_width=True):
                st.rerun()
                
            if st.button("Logout / Exit"):
                st.session_state.connected = False
                st.session_state.guest_mode = False
                auth.logout()
                st.rerun()

        with main_col:
            st.title("📰 Zen News")
            label = st.session_state.custom_interest if st.session_state.custom_interest else f"{st.session_state.country.upper()} • {st.session_state.category.capitalize()}"
            st.caption(f"Factual Digest for {label}")
            st.write("---")
            
            # TWO-STEP MULTI-MODAL PROCESS
            from news_manager import fetch_top_stories
            from summarizer import find_top_topics, triangulate_cluster
            
            with st.spinner("Scavenging news landscape for top events..."):
                # Step 1: General Scavenging
                general_articles = fetch_top_stories(
                    country=st.session_state.country, 
                    category=st.session_state.category,
                    query=st.session_state.custom_interest if st.session_state.custom_interest else None
                )
                
                # Step 2: Identify Top 4 Modal Topics
                top_topics = find_top_topics(general_articles, n=4)
                
                if not top_topics:
                    st.warning("No clear story patterns identified. Try broadening your interests.")
                else:
                    for topic in top_topics:
                        with st.status(f"Triangulating News: {topic.title()}...", expanded=False):
                            # Deep Fetch for the specific topic
                            topic_pool = fetch_top_stories(query=topic)
                            # Pass topic for relevance filtering
                            summary_data = triangulate_cluster(topic_pool, topic_query=topic)
                            
                        if summary_data:
                            with st.container(border=True):
                                # Header
                                h_col1, h_col2 = st.columns([4, 1])
                                # Use the specific topic as the title for clarity
                                with h_col1: st.subheader(topic.title())
                                with h_col2: st.caption(f"🛡️ {summary_data['depth']}")
                                
                                st.write(summary_data["factual_core"])
                                
                                # Source Attribution (Strictly Diverse)
                                st.write("**Perspective Diversity:**")
                                source_html = " ".join([f'<a href="{s["url"]}" target="_blank" style="text-decoration:none; color:#1f77b4; background-color:#f0f2f6; padding:2px 8px; border-radius:10px; font-size:12px; margin-right:5px;">{s["name"]}</a>' for s in summary_data["sources"][:5]])
                                st.markdown(source_html, unsafe_allow_html=True)
                                
                                st.divider()
                                # Bias Meter
                                score = summary_data["bias_score"]
                                b_cols = st.columns([1, 4])
                                with b_cols[0]: st.caption(f"Leaning Guard: {score}/100")
                                with b_cols[1]: st.progress(score / 100)
    
    else:
        # Zen Landing Page with Initial Interest Selection
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("📰 Zen News")
            st.write("A sanctuary for neutral, fact-based journalism.")
            st.write("---")
            
            # Interest Selection BEFORE Guest login
            st.subheader("Select Initial Interests")
            from news_manager import COUNTRIES
            c_col, cat_col = st.columns(2)
            with c_col:
                initial_country_name = st.selectbox("Country", sorted(list(COUNTRIES.keys())), index=sorted(list(COUNTRIES.keys())).index("United States"))
            with cat_col:
                initial_category = st.selectbox("Category", ["general", "business", "entertainment", "health", "science", "sports", "technology"], index=0)
            
            st.markdown("---")
            
            # Login Buttons
            auth_col, guest_col = st.columns(2)
            with auth_col:
                auth.login()
            with guest_col:
                if st.button("Continue as Guest", use_container_width=True):
                    st.session_state.guest_mode = True
                    st.session_state.country = COUNTRIES[initial_country_name]
                    st.session_state.category = initial_category
                    st.session_state.custom_interest = ""
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
