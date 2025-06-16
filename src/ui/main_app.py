import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import sys
import os
import pickle

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.db_manager import DatabaseManager
from scraper.eurlex_scraper import EURLexScraper
from models.text_analyzer import TextAnalyzer
from analysis.enhanced_legal_analyzer import EnhancedLegalAnalyzer
from ui.homepage import show_homepage

print("EU Regulation Analyser is starting (finally)...")
st.set_page_config(
    page_title="EU Regulation Analyzer",
    page_icon="🇪🇺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for blue/white/grey theme (temporary)
def load_css():
    dark_mode = st.session_state.get('dark_mode', False)
    
    css = f"""
    <style>

    .stApp {{
        background: #ffffff !important;
        background-image: none !important;
    }}
    
    header, footer, .reportview-container .main footer {{
    visibility: hidden;
}}

    
    .main-header {{
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #2c3e50;
    }}
    
    .metric-card {{
        background-color: #2c5aa0;
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        border: 1px solid #e9ecef;
    }}
    
    .relevance-high {{
        background-color: #2c5aa0;
        padding: 0.5rem;
        border-radius: 5px;
        color: white;
        font-weight: bold;
    }}
    
    .relevance-medium {{
        background-color: #6c757d;
        padding: 0.5rem;
        border-radius: 5px;
        color: white;
        font-weight: bold;
    }}
    
    .relevance-low {{
        background-color: #adb5bd;
        padding: 0.5rem;
        border-radius: 5px;
        color: white;
        font-weight: bold;
    }}
    
    .stSelectbox > div > div {{
        background-color: {'#2d3748' if dark_mode else '#ffffff'};
        border: 1px solid {'#4a5568' if dark_mode else '#e2e8f0'};
    }}
    
    .stTextInput > div > div > input {{
        background-color: {'#2d3748' if dark_mode else '#ffffff'};
        color: {'#ffffff' if dark_mode else '#2c3e50'};
        border: 1px solid {'#4a5568' if dark_mode else '#e2e8f0'};
    }}
    
    .stTextArea > div > div > textarea {{
        background-color: {'#2d3748' if dark_mode else '#ffffff'};
        color: {'#ffffff' if dark_mode else '#2c3e50'};
        border: 1px solid {'#4a5568' if dark_mode else '#e2e8f0'};
    }}
    
    .dark-mode {{
        background-color: #1e2a3a;
        color: #ffffff;
    }}
    
    .sidebar .sidebar-content {{
        background: linear-gradient(180deg, {'#1e2a3a' if dark_mode else '#f8f9fa'} 0%, {'#2d3748' if dark_mode else '#e9ecef'} 100%);
    }}
    
    /* Navigation styling */
    .css-1d391kg {{
        background-color: {'#1e2a3a' if dark_mode else '#ffffff'};
    }}
    
    /* Button styling */
    .stButton > button {{
        background-color: #2c5aa0;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }}
    
    .stButton > button:hover {{
        background-color: #2c5aa0;
    }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = DatabaseManager()
    if 'text_analyzer' not in st.session_state:
        st.session_state.text_analyzer = None  # Lazy load
    if 'enhanced_analyzer' not in st.session_state:
        st.session_state.enhanced_analyzer = None  # Lazy load
    if 'scraper' not in st.session_state:
        st.session_state.scraper = None  # Lazy load

def get_text_analyzer():
    """Lazy load text analyzer only when needed"""
    if st.session_state.text_analyzer is None:
        with st.spinner("Loading NLP models..."):
            st.session_state.text_analyzer = TextAnalyzer()
    return st.session_state.text_analyzer

def get_enhanced_analyzer():
    """Lazy load enhanced legal analyzer only when needed"""
    if st.session_state.enhanced_analyzer is None:
        with st.spinner("Loading the latest NLP models..."):
            st.session_state.enhanced_analyzer = EnhancedLegalAnalyzer()
    return st.session_state.enhanced_analyzer

def get_scraper():
    """Lazy load scraper only when needed"""
    if st.session_state.scraper is None:
        st.session_state.scraper = EURLexScraper()
    return st.session_state.scraper

def main():
    load_css()
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("EU Regulation Analyzer")
        
        # Dark mode toggle
        dark_mode = st.toggle("Dark Mode", value=st.session_state.dark_mode)
        if dark_mode != st.session_state.dark_mode:
            st.session_state.dark_mode = dark_mode
            st.rerun()
        
        # Navigation menu
        selected = option_menu(
            menu_title="Navigation",
            options=["Home", "Company Profile", "Compliance Analysis", "Regulations Database", "Settings"],
            icons=["house", "graph-up", "building", "search", "database", "gear"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "orange", "font-size": "25px"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "#02ab21"},
            }
        )
    
    # Check if assessment was completed and should redirect to analysis
    if st.session_state.get('show_analysis', False):
        st.session_state.show_analysis = False
        selected = "Legal Analysis"
    
    # Main content
    if selected == "Home":
        show_homepage()
    elif selected == "Company Profile":
        show_company_profile()
    elif selected == "Compliance Analysis":
        show_legal_analysis()
    elif selected == "Regulations Database":
        show_data_management()
    elif selected == "Settings":
        show_settings()

def show_company_profile():
    st.title("Company Profile Management")
    
    tab1, tab2 = st.tabs(["Create Profile", "Existing Profiles"])
    
    with tab1:
        st.subheader("Create New Company Profile")
        
        with st.form("company_profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                company_name = st.text_input("Company Name *", placeholder="Enter company name")
                industry = st.selectbox("Industry *", [
                    "Technology", "Automotive", "Finance", "Healthcare", "Manufacturing",
                    "Retail", "Energy", "Transportation", "Agriculture", 
                    "Construction", "Telecommunications", "Other"
                ])
                company_size = st.selectbox("Company Size", [
                    "Startup (1-10 employees)", "Small (11-50 employees)", 
                    "Medium (51-250 employees)", "Large (251-1000 employees)", 
                    "Enterprise (1000+ employees)"
                ])
                location = st.text_input("Primary Location", placeholder="Country/Region")
            
            with col2:
                business_description = st.text_area("Business Description *", 
                    placeholder="Describe your company's main business activities...", height=100)
                business_activities = st.text_area("Key Business Activities", 
                    placeholder="List main business activities, products, or services...", height=100)
                compliance_areas = st.text_area("Current Compliance Areas", 
                    placeholder="Areas where you currently ensure compliance (e.g., GDPR, financial regulations)...", height=100)
                risk_profile = st.selectbox("Risk Profile", ["Low", "Medium", "High"])
            
            submitted = st.form_submit_button("Create Profile", use_container_width=True)
            
            if submitted:
                if company_name and industry and business_description:
                    # Generate embedding for the profile
                    profile_text = f"{company_name} {industry} {business_description} {business_activities} {compliance_areas}"
                    embedding = get_text_analyzer().generate_embedding(profile_text)
                    
                    profile_data = {
                        'company_name': company_name,
                        'industry': industry,
                        'business_description': business_description,
                        'company_size': company_size,
                        'location': location,
                        'business_activities': business_activities,
                        'compliance_areas': compliance_areas,
                        'risk_profile': risk_profile,
                        'embedding': pickle.dumps(embedding)
                    }
                    
                    profile_id = st.session_state.db_manager.save_company_profile(profile_data)
                    st.success(f"Company profile created successfully! (ID: {profile_id})")
                else:
                    st.error("Please fill in all required fields marked with *")

def show_legal_analysis():
    st.title("Legal Compliance Analysis")
    
    # Company selection
    profiles = st.session_state.db_manager.get_company_profiles()
    
    if not profiles:
        st.warning("No company profiles found. Please create a company profile first.")
        if st.button("➕ Create Company Profile"):
            st.switch_page("Company Profile")
        return
    
    # Company selector
    company_options = {f"{p['company_name']} ({p['industry']})": p['id'] for p in profiles}
    selected_company_name = st.selectbox("Select Company for Analysis", list(company_options.keys()))
    selected_company_id = company_options[selected_company_name]
    
    # Get selected company profile
    selected_profile = next(p for p in profiles if p['id'] == selected_company_id)
    
    # Analysis controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        max_results = st.slider("Maximum Results", 5, 50, 20)
    
    with col2:
        min_relevance = st.slider("Minimum Relevance Score", 0.0, 1.0, 0.3, 0.1)
    
    with col3:
        if st.button("Run Analysis", use_container_width=True):
            run_legal_analysis(selected_profile, max_results, min_relevance)
    
    # Display existing analysis results
    st.subheader("Analysis Results")
    
    results = st.session_state.db_manager.get_analysis_results(selected_company_id, max_results)
    
    if results:
        # Filter by minimum relevance
        filtered_results = [r for r in results if r['relevance_score'] >= min_relevance]
        
        if filtered_results:
            display_analysis_results(filtered_results)
        else:
            st.info(f"No results found with relevance score >= {min_relevance}")
    else:
        st.info("No analysis results found. Run an analysis to see results.")

def run_legal_analysis(company_profile, max_results, min_relevance):
    """Run the enhanced legal analysis for a company"""
    
    with st.spinner("Matching regulations to your business..."):
        # Use the enhanced analyzer for comprehensive analysis
        enhanced_analyzer = get_enhanced_analyzer()
        
        # Get database stats
        stats = enhanced_analyzer.get_database_stats()
        st.info(f"Analyzing against {stats['total_legal_acts']} legal acts in database")
        
        # Run comprehensive analysis
        analysis_results = enhanced_analyzer.analyze_company_legal_requirements(
            company_profile, max_results=max_results
        )
        
        # Filter by minimum relevance
        filtered_results = [r for r in analysis_results if r['relevance_score'] >= min_relevance]
        
        # Save results to database
        saved_count = 0
        for result in filtered_results:
            try:
                st.session_state.db_manager.save_analysis_result(
                    company_profile['id'],
                    result['id'],
                    result['relevance_score'],
                    result['reasoning']
                )
                saved_count += 1
            except Exception as e:
                st.warning(f"Could not save result for {result.get('title', 'Unknown')}: {e}")
        
        st.success(f"Enhanced analysis complete! Found {len(filtered_results)} relevant legal acts (saved {saved_count} to database).")
        
        # Display immediate results
        if filtered_results:
            st.subheader("Top Relevant Legal Acts")
            display_enhanced_analysis_results(filtered_results[:10])  # Show top 10 immediately

def display_enhanced_analysis_results(results):

    for i, result in enumerate(results, 1):
        with st.expander(f"#{i} {result['title']} (Score: {result['relevance_score']:.3f})", expanded=i <= 3):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**CELEX:** {result.get('Celex ID', 'N/A')}")
                st.write(f"**Type:** {result.get('Act Type', 'N/A')}")
                st.write(f"**Subject:** {result.get('Topic', 'N/A')}")
                
                if result.get('summary'):
                    st.write(f"**Summary:** {result['summary'][:300]}...")
                
                st.write(f"**Reasoning:** {result['reasoning']}")
                
                # Show detailed scores
                if 'detailed_scores' in result:
                    scores = result['detailed_scores']
                    st.write("**Analysis Breakdown:**")
                    score_cols = st.columns(4)
                    with score_cols[0]:
                        st.metric("TF-IDF", f"{scores['tfidf']:.3f}")
                    with score_cols[1]:
                        st.metric("Keywords", f"{scores['Keywords']:.3f}")
                    with score_cols[2]:
                        st.metric("Industry", f"{scores['Industry']:.3f}")
                    with score_cols[3]:
                        st.metric("Characteristics", f"{scores['characteristics']:.3f}")
            
            with col2:
                # Risk level indicator
                risk_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                risk_level = result.get('risk_level', 'low')
                st.markdown(f"**Risk Level**  \n{risk_color.get(risk_level, '⚪')} {risk_level.title()}")
                
                # Relevance score
                st.metric("Relevance", f"{result['relevance_score']:.3f}")
                
                # Link to full document
                if result.get('url'):
                    st.markdown(f"[📄 View Document]({result['url']})")

def display_analysis_results(results):

    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        document_types = list(set([r.get('document_type', 'Unknown') for r in results]))
        selected_types = st.multiselect("Filter by Document Type", document_types, default=document_types)
    
    with col2:
        relevance_ranges = ["High (0.8-1.0)", "Medium (0.5-0.8)", "Low (0.3-0.5)"]
        selected_ranges = st.multiselect("Filter by Relevance", relevance_ranges, default=relevance_ranges)
    
    with col3:
        sort_by = st.selectbox("Sort by", ["Relevance Score", "Date", "Title"])
    
    # Filter results
    filtered_results = results.copy()
    
    if selected_types:
        filtered_results = [r for r in filtered_results if r.get('document_type', 'Unknown') in selected_types]
    
    # Apply relevance filter
    relevance_filters = []
    if "High (0.8-1.0)" in selected_ranges:
        relevance_filters.extend([r for r in filtered_results if r['relevance_score'] >= 0.8])
    if "Medium (0.5-0.8)" in selected_ranges:
        relevance_filters.extend([r for r in filtered_results if 0.5 <= r['relevance_score'] < 0.8])
    if "Low (0.3-0.5)" in selected_ranges:
        relevance_filters.extend([r for r in filtered_results if 0.3 <= r['relevance_score'] < 0.5])
    
    if relevance_filters:
        filtered_results = relevance_filters
    
    # Sort results
    if sort_by == "Relevance Score":
        filtered_results.sort(key=lambda x: x['relevance_score'], reverse=True)
    elif sort_by == "Title":
        filtered_results.sort(key=lambda x: x.get('Title', ''))
    
    # Display results
    for i, result in enumerate(filtered_results[:20]):  # Show top 20
        relevance_score = result['relevance_score']
        
        # Determine relevance class
        if relevance_score >= 0.8:
            relevance_class = "relevance-high"
            relevance_text = "HIGH"
        elif relevance_score >= 0.5:
            relevance_class = "relevance-medium"
            relevance_text = "MEDIUM"
        else:
            relevance_class = "relevance-low"
            relevance_text = "LOW"
        
        with st.expander(f"#{i+1} {result.get('title', 'Unknown Title')}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**CELEX Number:** {result.get('celex_number', 'N/A')}")
                st.markdown(f"**Document Type:** {result.get('document_type', 'N/A')}")
                st.markdown(f"**Subject Matter:** {result.get('subject_matter', 'N/A')}")
                
                if result.get('url'):
                    st.markdown(f"**[📄 View Full Document]({result['url']})**")
                
                st.markdown("**Reasoning:**")
                st.write(result.get('reasoning', 'No reasoning available.'))
            
            with col2:
                st.markdown(f'''
                <div class="{relevance_class}">
                    {relevance_text}<br>
                    {relevance_score:.2f}
                </div>
                ''', unsafe_allow_html=True)
                
                if st.button(f"Detailed Analysis", key=f"detail_{i}"):
                    show_detailed_analysis(result)

def show_detailed_analysis(result):
    """Show detailed analysis in a modal-like display"""
    st.subheader(f"Detailed Analysis: {result.get('title', 'Unknown')}")
    
    # Create tabs for different aspects
    tab1, tab2, tab3 = st.tabs(["Summary", "Compliance Impact", "Recommendations"])
    
    with tab1:
        st.write("**Document Summary:**")
        summary = get_text_analyzer().summarize_legal_act(result)
        st.write(summary)
        
        st.write("**Key Information:**")
        info_data = {
            'Field': ['CELEX Number', 'Document Type', 'Subject Matter', 'Relevance Score'],
            'Value': [
                result.get('celex_number', 'N/A'),
                result.get('document_type', 'N/A'),
                result.get('subject_matter', 'N/A'),
                f"{result['relevance_score']:.3f}"
            ]
        }
        st.table(pd.DataFrame(info_data))
    
    with tab2:
        st.write("**Potential Compliance Impact:**")
        st.write(result.get('reasoning', 'No detailed impact analysis available.'))
        
        # Risk assessment
        risk_level = "High" if result['relevance_score'] >= 0.8 else "Medium" if result['relevance_score'] >= 0.5 else "Low"
        st.metric("Risk Level", risk_level)
    
    with tab3:
        st.write("**Recommended Actions:**")
        
        if result['relevance_score'] >= 0.8:
            st.error("🚨 **Immediate Action Required**")
            st.write("- Review this regulation immediately")
            st.write("- Assess current compliance status")
            st.write("- Develop implementation plan")
            st.write("- Consult legal counsel if needed")
        elif result['relevance_score'] >= 0.5:
            st.warning("⚠️ **Review Recommended**")
            st.write("- Schedule review within 30 days")
            st.write("- Assess potential impact on operations")
            st.write("- Monitor for updates")
        else:
            st.info("ℹ️ **Monitor for Changes**")
            st.write("- Keep on watchlist")
            st.write("- Review quarterly")

def show_data_management():
    st.title("Data Management")
    
    tab1, tab2, tab3 = st.tabs(["Legal Acts Database", "Scraping Tools", "Export/Import"])
    
    with tab1:
        st.subheader("Legal Acts in Database")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_term = st.text_input("Search Legal Acts", placeholder="Enter keywords to search...")
        
        with col2:
            if st.button("Search", use_container_width=True):
                if search_term:
                    results = st.session_state.db_manager.search_legal_acts(search_term)
                    st.session_state.search_results = results
        
        # Display legal acts
        if hasattr(st.session_state, 'search_results'):
            results = st.session_state.search_results
        else:
            results = st.session_state.db_manager.get_legal_acts(limit=50)
        
        if results:
            df = pd.DataFrame(results)
            display_columns = ['celex_number', 'title', 'document_type', 'date_document', 'subject_matter']
            available_columns = [col for col in display_columns if col in df.columns]
            
            st.dataframe(df[available_columns], use_container_width=True, height=400)
        else:
            st.info("No legal acts found.")
    
    with tab2:
        st.subheader("EUR-Lex Scraping Tools")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Scrape Recent Acts**")
            days = st.number_input("Days to look back", min_value=1, max_value=365, value=30)
            max_recent = st.number_input("Max results", min_value=1, max_value=500, value=50)
            
            if st.button("Scrape Recent Acts"):
                scrape_recent_acts(days, max_recent)
        
        with col2:
            st.write("**Comprehensive Directory Scraping**")
            st.info("Use the enhanced scraper to populate the database with comprehensive legal acts")
            
            max_acts = st.number_input("Max acts to scrape", min_value=50, max_value=5000, value=500, step=50)
            
            if st.button("🇪🇺 Run Comprehensive Scraping", type="primary"):
                run_comprehensive_scraping(max_acts)
        
        st.divider()
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.write("**Scrape by Subject**")
            subjects = st.multiselect("Select subjects", [
                "Data Protection", "Financial Services", "Environmental Law",
                "Competition Law", "Employment Law", "Consumer Protection",
                "Digital Services", "Healthcare", "Energy", "Transportation"
            ])
            max_per_subject = st.number_input("Max per subject", min_value=1, max_value=100, value=20)
            
            if st.button("Scrape by Subject"):
                if subjects:
                    scrape_by_subjects(subjects, max_per_subject)
                else:
                    st.warning("Please select at least one subject.")
        
        with col4:
            st.write("**Database Statistics**")
            stats = get_enhanced_analyzer().get_database_stats()
            st.metric("Total Legal Acts", stats['total_legal_acts'])
            
            if stats['document_types']:
                st.write("**Document Types:**")
                for doc_type, count in stats['document_types'].items():
                    st.write(f"• {doc_type or 'Unknown'}: {count}")
            
            if st.button("Refresh Stats"):
                st.rerun()
    
    with tab3:
        st.subheader("Export/Import Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Export Data**")
            
            if st.button("Export Legal Acts to CSV"):
                legal_acts = st.session_state.db_manager.get_legal_acts()
                if legal_acts:
                    df = pd.DataFrame(legal_acts)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="legal_acts.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No data to export.")
        
        with col2:
            st.write("**Import Data**")
            uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
            
            if uploaded_file is not None:
                df = pd.read_csv(uploaded_file)
                st.write("Preview:")
                st.dataframe(df.head())
                
                if st.button("Import Data"):
                    # Implementation for importing data
                    st.success("Data import functionality would be implemented here.")

def run_comprehensive_scraping(max_acts):
    """Run comprehensive EUR-Lex directory scraping"""
    try:
        from scraper.directory_scraper import EURLexDirectoryScraper
        
        with st.spinner(f"🇪🇺 Running comprehensive scraping for up to {max_acts} legal acts..."):
            # Initialize the comprehensive scraper
            scraper = EURLexDirectoryScraper(delay=0.5, max_workers=2)
            
            # Show initial stats
            initial_stats = scraper.get_scraping_stats()
            st.info(f"Starting with {initial_stats['total_acts_in_db']} acts in database")
            
            # Create progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Run the comprehensive scraping
            scraped_count = scraper.scrape_comprehensive_legal_acts(max_acts=max_acts)
            
            # Show final stats
            final_stats = scraper.get_scraping_stats()
            
            progress_bar.progress(1.0)
            status_text.text("Scraping completed!")
            
            st.success(f"Comprehensive scraping completed!")
            st.info(f"Scraped {scraped_count} new legal acts")
            st.info(f"Total acts in database: {final_stats['total_acts_in_db']}")
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
        
    except Exception as e:
        st.error(f"Error during comprehensive scraping: {e}")
        st.info("Try reducing the number of acts or check your internet connection")

def scrape_recent_acts(days, max_results):
    """Scrape recent legal acts"""
    with st.spinner(f"Scraping legal acts from the last {days} days..."):
        try:
            scraper = get_scraper()
            new_acts = scraper.scrape_recent_acts(days=days, max_results=max_results)
            
            saved_count = 0
            for act in new_acts:
                try:
                    # Generate embedding
                    act_text = f"{act.get('title', '')} {act.get('summary', '')} {act.get('content', '')}"
                    embedding = get_text_analyzer().generate_embedding(act_text)
                    act['embedding'] = pickle.dumps(embedding)
                    
                    st.session_state.db_manager.save_legal_act(act)
                    saved_count += 1
                except Exception as e:
                    st.error(f"Error saving act {act.get('celex_number', 'Unknown')}: {e}")
            
            st.success(f"Successfully scraped and saved {saved_count} legal acts!")
            
        except Exception as e:
            st.error(f"Error during scraping: {e}")

def scrape_by_subjects(subjects, max_per_subject):
    """Scrape legal acts by subjects"""
    with st.spinner(f"Scraping legal acts for {len(subjects)} subjects..."):
        try:
            scraper = get_scraper()
            new_acts = scraper.scrape_by_subject(subjects, max_per_subject)
            
            saved_count = 0
            for act in new_acts:
                try:
                    # Generate embedding
                    act_text = f"{act.get('title', '')} {act.get('summary', '')} {act.get('content', '')}"
                    embedding = get_text_analyzer().generate_embedding(act_text)
                    act['embedding'] = pickle.dumps(embedding)
                    
                    st.session_state.db_manager.save_legal_act(act)
                    saved_count += 1
                except Exception as e:
                    st.error(f"Error saving act {act.get('celex_number', 'Unknown')}: {e}")
            
            st.success(f"Successfully scraped and saved {saved_count} legal acts!")
            
        except Exception as e:
            st.error(f"Error during scraping: {e}")

# this bit is for dark mode
def show_settings():
    st.title("Settings")
    
    tab1, tab2, tab3 = st.tabs(["General", "AI Models", "Regulations Database"])
    
    with tab1:
        st.subheader("General Settings")
        
        st.write("**Theme Settings**")
        dark_mode = st.checkbox("Dark Mode", value=st.session_state.dark_mode)
        if dark_mode != st.session_state.dark_mode:
            st.session_state.dark_mode = dark_mode

    
    with tab2:
        st.subheader("AI Model Settings")
        
        st.write("**Current Models**")
        st.info("Sentence Transformer: all-MiniLM-L6-v2")
        st.info("Summarization: TBA")
        st.info("Classification: TBA")
        
        st.write("**Model Performance**")

    
    with tab3:
        st.subheader("Regulations Database")
        

if __name__ == "__main__":
    main()