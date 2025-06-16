#!/usr/bin/env python3
"""
Demo script showing how to create a company profile and run legal analysis
"""

import sys
import os
from pathlib import Path
import pickle

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from database.db_manager import DatabaseManager
from models.text_analyzer import TextAnalyzer

def create_sample_company():
    """Create a sample company profile"""
    
    company_profile = {
        'company_name': 'TechCorp Solutions',
        'industry': 'Technology',
        'business_description': 'A technology company specializing in cloud-based software solutions, data analytics, and digital transformation services for enterprise clients.',
        'company_size': 'Medium (51-250 employees)',
        'location': 'Germany',
        'business_activities': 'Software development, cloud services, data processing, customer analytics, digital consulting',
        'compliance_areas': 'GDPR compliance, data protection, cybersecurity standards, financial data handling',
        'risk_profile': 'Medium'
    }
    
    return company_profile

def run_demo_analysis():
    """Run a complete demo analysis"""
    
    print("🚀 EU Legal Analyzer - Demo Analysis")
    print("=" * 50)
    
    # Initialize components
    print("📊 Initializing database and AI models...")
    db = DatabaseManager()
    analyzer = TextAnalyzer()
    
    # Create sample company
    print("\n🏢 Creating sample company profile...")
    company_profile = create_sample_company()
    
    # Generate embedding for company
    company_text = f"{company_profile['company_name']} {company_profile['industry']} {company_profile['business_description']} {company_profile['business_activities']} {company_profile['compliance_areas']}"
    company_embedding = analyzer.generate_embedding(company_text)
    company_profile['embedding'] = pickle.dumps(company_embedding)
    
    # Save company profile
    company_id = db.save_company_profile(company_profile)
    print(f"✅ Company profile created with ID: {company_id}")
    print(f"   Company: {company_profile['company_name']}")
    print(f"   Industry: {company_profile['industry']}")
    print(f"   Description: {company_profile['business_description'][:100]}...")
    
    # Get legal acts
    print("\n📋 Retrieving legal acts from database...")
    legal_acts = db.get_legal_acts()
    print(f"✅ Found {len(legal_acts)} legal acts in database")
    
    # Run analysis
    print("\n🔍 Running legal compliance analysis...")
    analysis_results = []
    
    for i, legal_act in enumerate(legal_acts):
        print(f"   Analyzing act {i+1}/{len(legal_acts)}: {legal_act['title'][:50]}...")
        
        # Analyze relevance
        analysis = analyzer.analyze_company_legal_relevance(company_profile, legal_act)
        
        # Save analysis result
        db.save_analysis_result(
            company_id,
            legal_act['id'],
            analysis['relevance_score'],
            analysis['reasoning']
        )
        
        analysis_results.append({
            'legal_act': legal_act,
            'analysis': analysis
        })
    
    # Sort by relevance score
    analysis_results.sort(key=lambda x: x['analysis']['relevance_score'], reverse=True)
    
    # Display top results
    print("\n🎯 Top 5 Most Relevant Legal Acts:")
    print("=" * 50)
    
    for i, result in enumerate(analysis_results[:5]):
        legal_act = result['legal_act']
        analysis = result['analysis']
        
        print(f"\n#{i+1} {legal_act['title']}")
        print(f"   CELEX: {legal_act.get('celex_number', 'N/A')}")
        print(f"   Type: {legal_act.get('document_type', 'N/A')}")
        print(f"   Relevance Score: {analysis['relevance_score']:.3f}")
        print(f"   Reasoning: {analysis['reasoning'][:200]}...")
        
        if legal_act.get('url'):
            print(f"   URL: {legal_act['url']}")
    
    print(f"\n✅ Analysis complete! Results saved to database.")
    print(f"📊 You can view detailed results in the Streamlit application at http://localhost:12000")

if __name__ == "__main__":
    run_demo_analysis()