import streamlit as st
import pandas as pd
from typing import Dict, Any

def show_homepage():
    """Display the homepage with compliance assessment"""
    
    # Check for dark mode
    dark_mode = st.session_state.get('dark_mode', False)
    
    # Custom CSS for the homepage with blue/white/grey theme
    st.markdown(f"""
    <style>
    /* Blue/White/Grey Background */
    .main {{
        background: linear-gradient(135deg, 
            {'#1e2a3a' if dark_mode else '#f8f9fa'} 0%, 
            {'#2d3748' if dark_mode else '#e9ecef'} 50%, 
            {'#1e2a3a' if dark_mode else '#f8f9fa'} 100%);
        background-attachment: fixed;
        min-height: 100vh;
    }}
    
    .main-title {{
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        color: {'#ffffff' if dark_mode else '#2c5aa0'};
        margin-bottom: 1rem;
        line-height: 1.2;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        background: linear-gradient(45deg, #2c5aa0, #4a90e2, #2c5aa0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    .subtitle {{
        font-size: 1.3rem;
        text-align: center;
        color: {'#e2e8f0' if dark_mode else '#495057'};
        margin-bottom: 3rem;
        line-height: 1.5;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
        padding: 1.5rem;
        border-radius: 12px;
        background: {'rgba(45, 55, 72, 0.9)' if dark_mode else 'rgba(255, 255, 255, 0.9)'};
        border: 1px solid {'#4a5568' if dark_mode else '#e2e8f0'};
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }}
    
    .blue-elements {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
    }}
    
    .blue-dot {{
        position: absolute;
        color: {'#4a90e2' if not dark_mode else '#2c5aa0'};
        font-size: 1.5rem;
        animation: float 4s ease-in-out infinite;
        opacity: 0.3;
    }}
    
    @keyframes float {{
        0%, 100% {{ transform: translateY(0px); opacity: 0.2; }}
        50% {{ transform: translateY(-10px); opacity: 0.4; }}
    }}
    
    .assessment-container {{
        background: {'rgba(45, 55, 72, 0.95)' if dark_mode else 'rgba(255, 255, 255, 0.95)'};
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        border: 1px solid {'#4a5568' if dark_mode else '#e2e8f0'};
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }}
    
    .question-title {{
        font-size: 1.4rem;
        font-weight: 600;
        color: {'#ffffff' if dark_mode else '#2c5aa0'};
        margin-bottom: 1.5rem;
        padding: 0.5rem 0;
        border-bottom: 2px solid {'#4a5568' if dark_mode else '#e2e8f0'};
    }}
    
    .step-indicator {{
        text-align: center;
        color: {'#e2e8f0' if dark_mode else '#6c757d'};
        font-size: 0.9rem;
        margin-bottom: 1rem;
        background: {'rgba(45, 55, 72, 0.8)' if dark_mode else 'rgba(248, 249, 250, 0.9)'};
        padding: 0.75rem;
        border-radius: 20px;
        border: 1px solid {'#4a5568' if dark_mode else '#e2e8f0'};
        backdrop-filter: blur(5px);
    }}
    
    .feature-card {{
        background: {'rgba(45, 55, 72, 0.9)' if dark_mode else 'rgba(255, 255, 255, 0.9)'};
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid {'#4a5568' if dark_mode else '#e2e8f0'};
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }}
    
    .feature-card h3 {{
        color: {'#ffffff' if dark_mode else '#2c5aa0'};
        margin-bottom: 0.75rem;
    }}
    
    .feature-card p {{
        color: {'#e2e8f0' if dark_mode else '#495057'};
        line-height: 1.6;
    }}
    
    /* Dark mode specific styles */
    .stApp {{
        background: {'linear-gradient(135deg, #1e2a3a 0%, #2d3748 50%, #1e2a3a 100%)' if dark_mode else 'inherit'};
    }}
    
    /* Form input styling */
    .stSelectbox > div > div {{
        background-color: {'#2d3748' if dark_mode else '#ffffff'} !important;
        color: {'#ffffff' if dark_mode else '#2c3e50'} !important;
        border: 1px solid {'#4a5568' if dark_mode else '#e2e8f0'} !important;
        border-radius: 8px !important;
    }}
    
    .stTextInput > div > div > input {{
        background-color: {'#2d3748' if dark_mode else '#ffffff'} !important;
        color: {'#ffffff' if dark_mode else '#2c3e50'} !important;
        border: 1px solid {'#4a5568' if dark_mode else '#e2e8f0'} !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
    }}
    
    .stTextArea > div > div > textarea {{
        background-color: {'#2d3748' if dark_mode else '#ffffff'} !important;
        color: {'#ffffff' if dark_mode else '#2c3e50'} !important;
        border: 1px solid {'#4a5568' if dark_mode else '#e2e8f0'} !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
    }}
    
    /* Radio button styling */
    .stRadio > div {{
        background-color: {'rgba(45, 55, 72, 0.5)' if dark_mode else 'rgba(255, 255, 255, 0.8)'};
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid {'#4a5568' if dark_mode else '#e2e8f0'};
        margin: 0.5rem 0;
    }}
    
    .stRadio > div > label {{
        color: {'#ffffff' if dark_mode else '#2c3e50'} !important;
        font-weight: 500;
    }}
    
    /* Label styling */
    .stTextInput > label, .stSelectbox > label, .stTextArea > label, .stRadio > label {{
        color: {'#e2e8f0' if dark_mode else '#495057'} !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
    }}
    </style>
    
    <!-- Blue Elements Background -->
    <div class="blue-elements">
        <div class="blue-dot" style="top: 10%; left: 15%;">●</div>
        <div class="blue-dot" style="top: 20%; left: 85%; animation-delay: 1s;">●</div>
        <div class="blue-dot" style="top: 30%; left: 10%; animation-delay: 2s;">●</div>
        <div class="blue-dot" style="top: 40%; left: 90%; animation-delay: 0.5s;">●</div>
        <div class="blue-dot" style="top: 50%; left: 5%; animation-delay: 1.5s;">●</div>
        <div class="blue-dot" style="top: 60%; left: 95%; animation-delay: 2.5s;">●</div>
        <div class="blue-dot" style="top: 70%; left: 20%; animation-delay: 0.8s;">●</div>
        <div class="blue-dot" style="top: 80%; left: 80%; animation-delay: 1.8s;">●</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for the assessment
    if 'assessment_started' not in st.session_state:
        st.session_state.assessment_started = False
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    if 'assessment_data' not in st.session_state:
        st.session_state.assessment_data = {}
    
    # Show homepage or assessment based on state
    if not st.session_state.assessment_started:
        show_landing_page()
    else:
        show_assessment()

def show_landing_page():
    """Display the main landing page"""
    
    # Main title and subtitle
    st.markdown('<h1 class="main-title">Stay Compliant with EU Regulations</h1>', unsafe_allow_html=True)
    
    st.markdown('''
    <p class="subtitle">
    Track and manage EU regulatory compliance for your business. Get personalized insights, 
    deadlines, and action plans based on your company profile.
    </p>
    ''', unsafe_allow_html=True)
    
    # Start button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Compliance Assessment", 
                    type="primary", 
                    use_container_width=True,
                    help="Begin your personalized EU compliance assessment"):
            st.session_state.assessment_started = True
            st.session_state.current_step = 1
            st.rerun()
    
    # Feature highlights
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
        <h3>🎯 Personalized Analysis</h3>
        <p>Get tailored compliance recommendations based on your specific business profile and operations.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
        <h3>🤖 AI-Powered Insights</h3>
        <p>Advanced AI models analyze thousands of EU regulations to find what's most relevant to you.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
        <h3>📊 Interactive Dashboard</h3>
        <p>Track compliance status, deadlines, and action items in an intuitive, easy-to-use interface.</p>
        </div>
        """, unsafe_allow_html=True)

def show_assessment():
    """Display the multi-step assessment survey"""
    
    total_steps = 10
    current_step = st.session_state.current_step
    
    # Progress indicator
    st.markdown(f'<div class="step-indicator">Step {current_step} of {total_steps}</div>', unsafe_allow_html=True)
    
    # Progress bar
    progress = current_step / total_steps
    st.progress(progress)
    
    # Assessment container
    st.markdown('<div class="assessment-container">', unsafe_allow_html=True)
    
    # Route to appropriate question
    if current_step == 1:
        show_question_1()
    elif current_step == 2:
        show_question_2()
    elif current_step == 3:
        show_question_3()
    elif current_step == 4:
        show_question_4()
    elif current_step == 5:
        show_question_5()
    elif current_step == 6:
        show_question_6()
    elif current_step == 7:
        show_question_7()
    elif current_step == 8:
        show_question_8()
    elif current_step == 9:
        show_question_9()
    elif current_step == 10:
        show_question_10()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation buttons
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.assessment_started = False
            st.session_state.current_step = 1
            st.rerun()
    
    with col2:
        if current_step > 1:
            if st.button("← Previous", use_container_width=True):
                st.session_state.current_step -= 1
                st.rerun()
    
    with col4:
        if current_step < total_steps:
            if st.button("Next →", type="primary", use_container_width=True):
                st.session_state.current_step += 1
                st.rerun()
        else:
            if st.button("Complete Assessment", type="primary", use_container_width=True):
                complete_assessment()

def show_question_1():
    """Q1 - Company Information"""
    st.markdown('<div class="question-title">Company Information</div>', unsafe_allow_html=True)
    
    company_name = st.text_input(
        "Company Name *",
        value=st.session_state.assessment_data.get('company_name', ''),
        placeholder="Enter your company name"
    )
    st.session_state.assessment_data['company_name'] = company_name

def show_question_2():
    """Q2 - Location"""
    st.markdown('<div class="question-title">Location</div>', unsafe_allow_html=True)
    
    eu_countries = [
        "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic",
        "Denmark", "Estonia", "Finland", "France", "Germany", "Greece",
        "Hungary", "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg",
        "Malta", "Netherlands", "Poland", "Portugal", "Romania", "Slovakia",
        "Slovenia", "Spain", "Sweden"
    ]
    
    country = st.selectbox(
        "Country of Operations/HQ *",
        options=["Select your country..."] + eu_countries,
        index=0 if 'country' not in st.session_state.assessment_data else 
              eu_countries.index(st.session_state.assessment_data['country']) + 1
    )
    
    if country != "Select your country...":
        st.session_state.assessment_data['country'] = country

def show_question_3():
    """Q3 - Company Size"""
    st.markdown('<div class="question-title">Company Size</div>', unsafe_allow_html=True)
    
    size_options = [
        "Small (1-50 employees)",
        "Medium (51-250 employees)", 
        "Large (250+ employees)"
    ]
    
    company_size = st.radio(
        "Company Size *",
        options=size_options,
        index=size_options.index(st.session_state.assessment_data.get('company_size', size_options[0]))
    )
    st.session_state.assessment_data['company_size'] = company_size

def show_question_4():
    """Q4 - Legal Structure"""
    st.markdown('<div class="question-title">Legal Structure</div>', unsafe_allow_html=True)
    
    legal_forms = [
        "Limited Liability Company (LLC/Ltd)",
        "Public Limited Company (PLC)",
        "Partnership",
        "Sole Proprietorship",
        "Corporation",
        "Cooperative",
        "Non-profit Organization",
        "Other"
    ]
    
    legal_form = st.selectbox(
        "Legal Form *",
        options=["Select legal form..."] + legal_forms,
        index=0 if 'legal_form' not in st.session_state.assessment_data else 
              legal_forms.index(st.session_state.assessment_data['legal_form']) + 1
    )
    
    if legal_form != "Select legal form...":
        st.session_state.assessment_data['legal_form'] = legal_form

def show_question_5():
    """Q5 - International Trade"""
    st.markdown('<div class="question-title">International Trade</div>', unsafe_allow_html=True)
    
    trade_options = [
        "Yes, we import/export goods or services",
        "No, we operate domestically only"
    ]
    
    import_export = st.radio(
        "Import/Export Activity *",
        options=trade_options,
        index=trade_options.index(st.session_state.assessment_data.get('import_export', trade_options[1]))
    )
    st.session_state.assessment_data['import_export'] = import_export

def show_question_6():
    """Q6 - Industry"""
    st.markdown('<div class="question-title">Industry</div>', unsafe_allow_html=True)
    
    industries = [
        "Technology/Software", "Financial Services", "Healthcare/Pharmaceuticals",
        "Manufacturing", "Retail/E-commerce", "Energy/Utilities", "Transportation",
        "Telecommunications", "Food & Beverage", "Construction", "Education",
        "Media/Entertainment", "Professional Services", "Other"
    ]
    
    industry = st.selectbox(
        "Industry *",
        options=["Select your industry..."] + industries,
        index=0 if 'industry' not in st.session_state.assessment_data else 
              industries.index(st.session_state.assessment_data['industry']) + 1
    )
    
    if industry != "Select your industry...":
        st.session_state.assessment_data['industry'] = industry

def show_question_7():
    """Q7 - Products & Services"""
    st.markdown('<div class="question-title">Products & Services</div>', unsafe_allow_html=True)
    
    products_services = st.text_area(
        "Brief Description of Products/Services *",
        value=st.session_state.assessment_data.get('products_services', ''),
        placeholder="Describe your main products or services...",
        height=100
    )
    st.session_state.assessment_data['products_services'] = products_services

def show_question_8():
    """Q8 - AI Usage"""
    st.markdown('<div class="question-title">AI Usage</div>', unsafe_allow_html=True)
    
    ai_usage_options = [
        "Yes, we use AI in our business operations",
        "No, we don't currently use AI",
        "We're planning to implement AI"
    ]
    
    ai_usage = st.radio(
        "Use of AI *",
        options=ai_usage_options,
        index=ai_usage_options.index(st.session_state.assessment_data.get('ai_usage', ai_usage_options[1]))
    )
    st.session_state.assessment_data['ai_usage'] = ai_usage

def show_question_9():
    """Q9 - Business Model"""
    st.markdown('<div class="question-title">Business Model</div>', unsafe_allow_html=True)
    
    business_model_options = [
        "B2B (Business to Business)",
        "B2C (Business to Consumer)",
        "Both B2B and B2C"
    ]
    
    business_model = st.radio(
        "Business Model *",
        options=business_model_options,
        index=business_model_options.index(st.session_state.assessment_data.get('business_model', business_model_options[0]))
    )
    st.session_state.assessment_data['business_model'] = business_model

def show_question_10():
    """Q10 - ESG Reporting"""
    st.markdown('<div class="question-title">ESG Reporting</div>', unsafe_allow_html=True)
    
    esg_options = [
        "Yes, we currently do ESG reporting",
        "No, but we plan to implement it",
        "No plans for ESG reporting"
    ]
    
    esg_reporting = st.radio(
        "ESG Reporting Status *",
        options=esg_options,
        index=esg_options.index(st.session_state.assessment_data.get('esg_reporting', esg_options[2]))
    )
    st.session_state.assessment_data['esg_reporting'] = esg_reporting

def complete_assessment():
    """Complete the assessment and redirect to analysis"""
    
    # Save assessment data to session state for use in other parts of the app
    st.session_state.completed_assessment = st.session_state.assessment_data.copy()
    
    # Create a company profile from the assessment
    create_company_profile_from_assessment()
    
    # Show completion message
    st.success("🎉 Assessment completed successfully!")
    st.info("Redirecting to your personalized compliance analysis...")
    
    # Reset assessment state and redirect
    st.session_state.assessment_started = False
    st.session_state.current_step = 1
    st.session_state.show_analysis = True
    
    # Small delay then rerun to show analysis
    import time
    time.sleep(2)
    st.rerun()

def create_company_profile_from_assessment():
    """Create a company profile from assessment data"""
    
    data = st.session_state.assessment_data
    
    # Map assessment data to company profile format
    profile_data = {
        'company_name': data.get('company_name', ''),
        'industry': data.get('industry', ''),
        'company_size': data.get('company_size', ''),
        'country': data.get('country', ''),
        'legal_form': data.get('legal_form', ''),
        'description': generate_company_description(data),
        'business_activities': generate_business_activities(data),
        'compliance_areas': generate_compliance_areas(data),
        'risk_profile': determine_risk_profile(data)
    }
    
    # Store in session state for use by other components
    st.session_state.assessment_profile = profile_data

def generate_company_description(data: Dict[str, Any]) -> str:
    """Generate company description from assessment data"""
    
    company_name = data.get('company_name', 'Company')
    industry = data.get('industry', 'business')
    size = data.get('company_size', '').split('(')[0].strip().lower()
    country = data.get('country', 'EU')
    products_services = data.get('products_services', '')
    
    description = f"{company_name} is a {size} {industry.lower()} company based in {country}."
    
    if products_services:
        description += f" {products_services}"
    
    if data.get('import_export', '').startswith('Yes'):
        description += " The company engages in international trade activities."
    
    if data.get('ai_usage', '').startswith('Yes'):
        description += " We use AI technology in our business operations."
    
    business_model = data.get('business_model', '')
    if business_model:
        description += f" Our business model is {business_model.lower()}."
    
    return description

def generate_business_activities(data: Dict[str, Any]) -> str:
    """Generate business activities from assessment data"""
    
    activities = []
    
    industry = data.get('industry', '')
    if industry:
        activities.append(f"Primary industry: {industry}")
    
    products_services = data.get('products_services', '')
    if products_services:
        activities.append(f"Products/Services: {products_services}")
    
    if data.get('import_export', '').startswith('Yes'):
        activities.append("International import/export operations")
    
    if data.get('ai_usage', '').startswith('Yes'):
        activities.append("AI technology implementation")
    
    business_model = data.get('business_model', '')
    if business_model:
        activities.append(f"Business model: {business_model}")
    
    return "; ".join(activities)

def generate_compliance_areas(data: Dict[str, Any]) -> str:
    """Generate compliance areas from assessment data"""
    
    areas = []
    
    if data.get('ai_usage', '').startswith('Yes'):
        areas.append("AI Act Compliance")
    
    if data.get('esg_reporting', '').startswith('Yes'):
        areas.append("ESG and Sustainability Reporting")
    
    if data.get('import_export', '').startswith('Yes'):
        areas.append("Trade and Customs Regulations")
    
    # Business model specific compliance
    business_model = data.get('business_model', '')
    if 'B2C' in business_model:
        areas.append("Consumer Protection")
    
    # Industry specific compliance
    industry = data.get('industry', '')
    if 'Financial' in industry:
        areas.append("Financial Services Regulation")
    elif 'Healthcare' in industry:
        areas.append("Medical Device Regulation")
    elif 'Technology' in industry:
        areas.append("Digital Services Act")
    
    # Always include general areas
    areas.extend(["Data Protection (GDPR)", "Competition Law", "Employment Law"])
    
    return "; ".join(areas)

def determine_risk_profile(data: Dict[str, Any]) -> str:
    """Determine risk profile from assessment data"""
    
    risk_factors = 0
    
    # High-risk factors
    if data.get('ai_usage', '').startswith('Yes'):
        risk_factors += 2  # AI usage increases regulatory risk
    
    if data.get('esg_reporting', '').startswith('Yes'):
        risk_factors += 1  # ESG reporting indicates higher scrutiny
    
    if data.get('company_size', '').startswith('Large'):
        risk_factors += 2  # Large companies have more regulatory obligations
    elif data.get('company_size', '').startswith('Medium'):
        risk_factors += 1
    
    if data.get('import_export', '').startswith('Yes'):
        risk_factors += 1  # International trade adds complexity
    
    # Industry-specific risks
    industry = data.get('industry', '')
    if 'Financial' in industry:
        risk_factors += 2  # Highly regulated industry
    elif 'Healthcare' in industry:
        risk_factors += 2  # Highly regulated industry
    elif 'Technology' in industry:
        risk_factors += 1  # Moderate regulatory risk
    
    # Business model risks
    business_model = data.get('business_model', '')
    if 'B2C' in business_model:
        risk_factors += 1  # Consumer protection requirements
    
    if risk_factors >= 6:
        return "High"
    elif risk_factors >= 3:
        return "Medium"
    else:
        return "Low"