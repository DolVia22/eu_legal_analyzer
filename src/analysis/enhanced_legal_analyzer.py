import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
import re
import logging
from datetime import datetime
import pickle
import os
import sys

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from models.text_analyzer import TextAnalyzer

class EnhancedLegalAnalyzer:
    """
    Enhanced legal analyzer that uses the comprehensive EUR-Lex database
    for more accurate and extensive legal act matching
    """
    
    def __init__(self):
        self.db = DatabaseManager()
        self.text_analyzer = TextAnalyzer()
        
        # Initialize vectorizers
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 3),
            min_df=2,
            max_df=0.8
        )
        
        self.svd = TruncatedSVD(n_components=100, random_state=42)
        
        # Cache for legal acts and embeddings
        self._legal_acts_cache = None
        self._embeddings_cache = None
        self._last_cache_update = None
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Industry-specific legal area mappings
        self.industry_legal_mappings = {
            'Technology': ['data protection', 'digital services', 'artificial intelligence', 'cybersecurity', 'telecommunications'],
            'Finance': ['financial services', 'banking', 'insurance', 'payment services', 'anti-money laundering'],
            'Healthcare': ['medical devices', 'pharmaceuticals', 'clinical trials', 'health data', 'patient rights'],
            'Manufacturing': ['product safety', 'chemicals', 'environmental protection', 'worker safety', 'machinery'],
            'Agriculture': ['food safety', 'agricultural products', 'pesticides', 'animal welfare', 'organic farming'],
            'Transport': ['road transport', 'aviation', 'maritime', 'rail transport', 'vehicle safety'],
            'Energy': ['renewable energy', 'energy efficiency', 'electricity markets', 'gas markets', 'nuclear safety'],
            'Retail': ['consumer protection', 'product liability', 'e-commerce', 'unfair commercial practices'],
            'Construction': ['construction products', 'building standards', 'energy performance', 'public procurement'],
            'Education': ['recognition of qualifications', 'student mobility', 'vocational training', 'research'],
            'Media': ['audiovisual media', 'copyright', 'broadcasting', 'digital content', 'press freedom']
        }
        
        # Risk level mappings
        self.risk_keywords = {
            'high': ['prohibited', 'criminal', 'sanctions', 'penalties', 'infringement', 'violation', 'breach'],
            'medium': ['compliance', 'requirements', 'obligations', 'standards', 'procedures', 'notification'],
            'low': ['recommendations', 'guidelines', 'best practices', 'voluntary', 'encouraged']
        }
    
    def analyze_company_legal_requirements(self, company_profile: Dict, 
                                         max_results: int = 20) -> List[Dict]:
        """
        Analyze company profile and return most relevant legal acts
        
        Args:
            company_profile: Company profile data
            max_results: Maximum number of results to return
            
        Returns:
            List of relevant legal acts with relevance scores and reasoning
        """
        self.logger.info(f"Analyzing legal requirements for company: {company_profile.get('company_name', 'Unknown')}")
        
        # Load and prepare legal acts
        legal_acts = self._get_legal_acts_with_caching()
        
        if not legal_acts:
            self.logger.warning("No legal acts found in database")
            return []
        
        # Generate company profile text for analysis
        company_text = self._generate_company_analysis_text(company_profile)
        
        # Calculate relevance scores using multiple methods
        relevance_scores = self._calculate_comprehensive_relevance(company_text, company_profile, legal_acts)
        
        # Sort by relevance score
        sorted_results = sorted(relevance_scores, key=lambda x: x['relevance_score'], reverse=True)
        
        # Return top results with enhanced information
        return self._enhance_results_with_reasoning(sorted_results[:max_results], company_profile)
    
    def _get_legal_acts_with_caching(self) -> List[Dict]:
        """Get legal acts with intelligent caching"""
        current_time = datetime.now()
        
        # Check if cache needs refresh (every hour or if empty)
        if (self._legal_acts_cache is None or 
            self._last_cache_update is None or 
            (current_time - self._last_cache_update).seconds > 3600):
            
            self.logger.info("Refreshing legal acts cache...")
            self._legal_acts_cache = self.db.get_legal_acts()
            self._last_cache_update = current_time
            
            # Filter out acts without sufficient content
            self._legal_acts_cache = [
                act for act in self._legal_acts_cache 
                if act.get('title') and (act.get('content') or act.get('summary'))
            ]
            
            self.logger.info(f"Loaded {len(self._legal_acts_cache)} legal acts into cache")
        
        return self._legal_acts_cache
    
    def _generate_company_analysis_text(self, company_profile: Dict) -> str:
        """Generate comprehensive text representation of company for analysis"""
        text_parts = []
        
        # Basic company information
        if company_profile.get('company_name'):
            text_parts.append(f"Company: {company_profile['company_name']}")
        
        if company_profile.get('industry'):
            text_parts.append(f"Industry: {company_profile['industry']}")
            # Add industry-specific keywords
            industry_keywords = self.industry_legal_mappings.get(company_profile['industry'], [])
            if industry_keywords:
                text_parts.append(f"Industry areas: {' '.join(industry_keywords)}")
        
        if company_profile.get('business_description'):
            text_parts.append(f"Business: {company_profile['business_description']}")
        
        if company_profile.get('products_services'):
            text_parts.append(f"Products and services: {company_profile['products_services']}")
        
        if company_profile.get('business_activities'):
            text_parts.append(f"Activities: {company_profile['business_activities']}")
        
        # Location and trade information
        if company_profile.get('location'):
            text_parts.append(f"Location: {company_profile['location']}")
        
        if company_profile.get('international_trade') == 'Yes':
            text_parts.append("International trade import export cross-border")
        
        # AI usage
        if company_profile.get('ai_usage') in ['Yes', 'Planning']:
            text_parts.append("artificial intelligence AI machine learning automated decision-making")
        
        # ESG reporting
        if company_profile.get('esg_reporting') in ['Current', 'Planned']:
            text_parts.append("environmental social governance sustainability reporting")
        
        # Business model
        if company_profile.get('business_model'):
            if 'B2B' in company_profile['business_model']:
                text_parts.append("business-to-business B2B commercial")
            if 'B2C' in company_profile['business_model']:
                text_parts.append("business-to-consumer B2C consumer protection")
        
        # Company size implications
        company_size = company_profile.get('company_size', '')
        if 'Large' in company_size:
            text_parts.append("large enterprise corporate governance reporting obligations")
        elif 'Medium' in company_size:
            text_parts.append("medium enterprise SME")
        else:
            text_parts.append("small business SME startup")
        
        return ' '.join(text_parts)
    
    def _calculate_comprehensive_relevance(self, company_text: str, 
                                         company_profile: Dict, 
                                         legal_acts: List[Dict]) -> List[Dict]:
        """Calculate relevance using multiple sophisticated methods"""
        results = []
        
        # Prepare legal acts texts
        legal_texts = []
        for act in legal_acts:
            act_text = self._prepare_legal_act_text(act)
            legal_texts.append(act_text)
        
        if not legal_texts:
            return results
        
        # Method 1: TF-IDF + Cosine Similarity
        tfidf_scores = self._calculate_tfidf_similarity(company_text, legal_texts)
        
        # Method 2: Keyword-based scoring
        keyword_scores = self._calculate_keyword_relevance(company_text, company_profile, legal_acts)
        
        # Method 3: Industry-specific scoring
        industry_scores = self._calculate_industry_relevance(company_profile, legal_acts)
        
        # Method 4: Company characteristics scoring
        characteristics_scores = self._calculate_characteristics_relevance(company_profile, legal_acts)
        
        # Combine scores with weights
        for i, act in enumerate(legal_acts):
            combined_score = (
                0.35 * tfidf_scores[i] +
                0.25 * keyword_scores[i] +
                0.25 * industry_scores[i] +
                0.15 * characteristics_scores[i]
            )
            
            results.append({
                'legal_act': act,
                'relevance_score': combined_score,
                'tfidf_score': tfidf_scores[i],
                'keyword_score': keyword_scores[i],
                'industry_score': industry_scores[i],
                'characteristics_score': characteristics_scores[i]
            })
        
        return results
    
    def _prepare_legal_act_text(self, act: Dict) -> str:
        """Prepare legal act text for analysis"""
        text_parts = []
        
        title = act.get('title')
        if title:
            text_parts.append(str(title))
        
        summary = act.get('summary')
        if summary:
            text_parts.append(str(summary))
        
        subject_matter = act.get('subject_matter')
        if subject_matter:
            text_parts.append(str(subject_matter))
        
        keywords = act.get('keywords')
        if keywords:
            text_parts.append(str(keywords))
        
        # Include first part of content if available
        content = act.get('content')
        if content:
            content_str = str(content)[:2000]  # First 2000 characters
            text_parts.append(content_str)
        
        return ' '.join(text_parts)
    
    def _calculate_tfidf_similarity(self, company_text: str, legal_texts: List[str]) -> List[float]:
        """Calculate TF-IDF based similarity scores"""
        try:
            # Combine company text with legal texts for fitting
            all_texts = [company_text] + legal_texts
            
            # Fit TF-IDF vectorizer
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_texts)
            
            # Calculate cosine similarity
            company_vector = tfidf_matrix[0:1]
            legal_vectors = tfidf_matrix[1:]
            
            similarities = cosine_similarity(company_vector, legal_vectors)[0]
            
            return similarities.tolist()
            
        except Exception as e:
            self.logger.error(f"Error calculating TF-IDF similarity: {e}")
            return [0.0] * len(legal_texts)
    
    def _calculate_keyword_relevance(self, company_text: str, 
                                   company_profile: Dict, 
                                   legal_acts: List[Dict]) -> List[float]:
        """Calculate keyword-based relevance scores"""
        scores = []
        company_text_lower = company_text.lower()
        
        for act in legal_acts:
            score = 0.0
            act_text = self._prepare_legal_act_text(act).lower()
            
            # Industry-specific keywords
            industry = company_profile.get('industry', '')
            if industry in self.industry_legal_mappings:
                industry_keywords = self.industry_legal_mappings[industry]
                for keyword in industry_keywords:
                    if keyword.lower() in act_text:
                        score += 0.2
            
            # Business model keywords
            business_model = company_profile.get('business_model', '')
            if 'B2C' in business_model and any(term in act_text for term in ['consumer', 'customer', 'buyer']):
                score += 0.15
            if 'B2B' in business_model and any(term in act_text for term in ['business', 'commercial', 'enterprise']):
                score += 0.15
            
            # AI usage keywords
            if company_profile.get('ai_usage') in ['Yes', 'Planning']:
                ai_terms = ['artificial intelligence', 'ai', 'machine learning', 'automated', 'algorithm']
                for term in ai_terms:
                    if term in act_text:
                        score += 0.3
            
            # International trade keywords
            if company_profile.get('international_trade') == 'Yes':
                trade_terms = ['import', 'export', 'customs', 'trade', 'cross-border', 'international']
                for term in trade_terms:
                    if term in act_text:
                        score += 0.2
            
            # ESG keywords
            if company_profile.get('esg_reporting') in ['Current', 'Planned']:
                esg_terms = ['environmental', 'sustainability', 'governance', 'social', 'reporting', 'disclosure']
                for term in esg_terms:
                    if term in act_text:
                        score += 0.2
            
            scores.append(min(score, 1.0))  # Cap at 1.0
        
        return scores
    
    def _calculate_industry_relevance(self, company_profile: Dict, 
                                    legal_acts: List[Dict]) -> List[float]:
        """Calculate industry-specific relevance scores"""
        scores = []
        industry = company_profile.get('industry', '').lower()
        
        for act in legal_acts:
            score = 0.0
            
            # Check subject matter
            subject_matter = act.get('subject_matter') or ''
            subject_matter = subject_matter.lower()
            if industry in subject_matter:
                score += 0.5
            
            # Check directory code for industry relevance
            directory_code = act.get('directory_code') or ''
            directory_code = directory_code.lower()
            
            # Industry-specific directory mappings
            industry_directory_mappings = {
                'technology': ['digital', 'information', 'telecommunications', 'data'],
                'finance': ['financial', 'banking', 'insurance', 'monetary'],
                'healthcare': ['health', 'medical', 'pharmaceutical', 'clinical'],
                'agriculture': ['agriculture', 'food', 'rural', 'fisheries'],
                'transport': ['transport', 'aviation', 'maritime', 'road'],
                'energy': ['energy', 'electricity', 'gas', 'nuclear'],
                'manufacturing': ['industrial', 'manufacturing', 'chemicals', 'machinery']
            }
            
            if industry in industry_directory_mappings:
                for keyword in industry_directory_mappings[industry]:
                    if keyword in directory_code or keyword in subject_matter:
                        score += 0.3
            
            scores.append(min(score, 1.0))
        
        return scores
    
    def _calculate_characteristics_relevance(self, company_profile: Dict, 
                                           legal_acts: List[Dict]) -> List[float]:
        """Calculate relevance based on company characteristics"""
        scores = []
        
        for act in legal_acts:
            score = 0.0
            act_text = self._prepare_legal_act_text(act).lower()
            
            # Company size relevance
            company_size = company_profile.get('company_size', '')
            if 'Large' in company_size:
                if any(term in act_text for term in ['large', 'enterprise', 'corporate', 'listed', 'public']):
                    score += 0.2
            elif 'Small' in company_size:
                if any(term in act_text for term in ['sme', 'small', 'micro', 'startup']):
                    score += 0.2
            
            # Legal structure relevance
            legal_structure = company_profile.get('legal_structure') or ''
            legal_structure = legal_structure.lower()
            if 'limited' in legal_structure and 'limited' in act_text:
                score += 0.1
            
            # Location relevance (EU-specific)
            location = company_profile.get('location') or ''
            location = location.lower()
            if any(eu_term in location for eu_term in ['eu', 'european', 'europe']):
                if any(term in act_text for term in ['member state', 'european union', 'eu']):
                    score += 0.15
            
            scores.append(min(score, 1.0))
        
        return scores
    
    def _enhance_results_with_reasoning(self, results: List[Dict], 
                                      company_profile: Dict) -> List[Dict]:
        """Enhance results with detailed reasoning"""
        enhanced_results = []
        
        for result in results:
            act = result['legal_act']
            
            # Generate reasoning
            reasoning_parts = []
            
            # Industry relevance
            if result['industry_score'] > 0.3:
                reasoning_parts.append(f"High industry relevance for {company_profile.get('industry', 'your sector')}")
            
            # AI relevance
            if company_profile.get('ai_usage') in ['Yes', 'Planning']:
                act_text = self._prepare_legal_act_text(act).lower()
                if any(ai_term in act_text for ai_term in ['artificial intelligence', 'ai', 'automated']):
                    reasoning_parts.append("Relevant for AI usage and automated decision-making")
            
            # Trade relevance
            if company_profile.get('international_trade') == 'Yes':
                act_text = self._prepare_legal_act_text(act).lower()
                if any(trade_term in act_text for trade_term in ['import', 'export', 'trade', 'customs']):
                    reasoning_parts.append("Important for international trade operations")
            
            # ESG relevance
            if company_profile.get('esg_reporting') in ['Current', 'Planned']:
                act_text = self._prepare_legal_act_text(act).lower()
                if any(esg_term in act_text for esg_term in ['environmental', 'sustainability', 'governance']):
                    reasoning_parts.append("Relevant for ESG reporting and sustainability compliance")
            
            # Company size relevance
            company_size = company_profile.get('company_size', '')
            if 'Large' in company_size and result['characteristics_score'] > 0.1:
                reasoning_parts.append("Specific obligations for large enterprises")
            
            # Risk assessment
            risk_level = self._assess_risk_level(act)
            if risk_level == 'high':
                reasoning_parts.append("⚠️ High compliance risk - mandatory requirements")
            elif risk_level == 'medium':
                reasoning_parts.append("⚡ Medium compliance risk - important standards")
            else:
                reasoning_parts.append("ℹ️ Low risk - guidelines and recommendations")
            
            # Default reasoning if none found
            if not reasoning_parts:
                reasoning_parts.append("General relevance based on business profile analysis")
            
            enhanced_result = {
                'id': act.get('id'),
                'celex_number': act.get('celex_number'),
                'title': act.get('title'),
                'document_type': act.get('document_type'),
                'subject_matter': act.get('subject_matter'),
                'date_document': act.get('date_document'),
                'summary': act.get('summary'),
                'url': act.get('url'),
                'relevance_score': round(result['relevance_score'], 3),
                'reasoning': '; '.join(reasoning_parts),
                'risk_level': risk_level,
                'detailed_scores': {
                    'tfidf': round(result['tfidf_score'], 3),
                    'keyword': round(result['keyword_score'], 3),
                    'industry': round(result['industry_score'], 3),
                    'characteristics': round(result['characteristics_score'], 3)
                }
            }
            
            enhanced_results.append(enhanced_result)
        
        return enhanced_results
    
    def _assess_risk_level(self, act: Dict) -> str:
        """Assess the compliance risk level of a legal act"""
        act_text = self._prepare_legal_act_text(act).lower()
        
        # Check for high-risk keywords
        high_risk_count = sum(1 for keyword in self.risk_keywords['high'] if keyword in act_text)
        medium_risk_count = sum(1 for keyword in self.risk_keywords['medium'] if keyword in act_text)
        low_risk_count = sum(1 for keyword in self.risk_keywords['low'] if keyword in act_text)
        
        # Document type risk assessment
        doc_type = act.get('document_type') or ''
        doc_type = doc_type.lower()
        if 'regulation' in doc_type:
            base_risk = 'high'  # Regulations are directly applicable
        elif 'directive' in doc_type:
            base_risk = 'medium'  # Directives need transposition
        else:
            base_risk = 'low'
        
        # Combine keyword and document type assessment
        if high_risk_count > 0 or base_risk == 'high':
            return 'high'
        elif medium_risk_count > 0 or base_risk == 'medium':
            return 'medium'
        else:
            return 'low'
    
    def get_database_stats(self) -> Dict:
        """Get current database statistics"""
        total_acts = self.db.get_legal_act_count()
        
        # Get breakdown by document type
        legal_acts = self.db.get_legal_acts()
        doc_types = {}
        for act in legal_acts:
            doc_type = act.get('document_type', 'Unknown')
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        return {
            'total_legal_acts': total_acts,
            'document_types': doc_types,
            'last_updated': datetime.now().isoformat()
        }


def main():
    """Test the enhanced legal analyzer"""
    analyzer = EnhancedLegalAnalyzer()
    
    # Test company profile
    test_profile = {
        'company_name': 'TechCorp AI Solutions',
        'industry': 'Technology',
        'business_description': 'AI-powered software solutions for businesses',
        'company_size': 'Medium (51-250 employees)',
        'location': 'Germany (EU)',
        'international_trade': 'Yes',
        'ai_usage': 'Yes',
        'business_model': 'B2B',
        'esg_reporting': 'Planned'
    }
    
    print("🔍 Testing Enhanced Legal Analyzer")
    print("=" * 50)
    
    # Get database stats
    stats = analyzer.get_database_stats()
    print(f"📊 Database Statistics:")
    print(f"   Total legal acts: {stats['total_legal_acts']}")
    print(f"   Document types: {stats['document_types']}")
    print()
    
    # Analyze company
    print(f"🏢 Analyzing: {test_profile['company_name']}")
    results = analyzer.analyze_company_legal_requirements(test_profile, max_results=10)
    
    print(f"\n📋 Top {len(results)} Relevant Legal Acts:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   CELEX: {result['celex_number']}")
        print(f"   Type: {result['document_type']}")
        print(f"   Relevance: {result['relevance_score']:.3f}")
        print(f"   Risk: {result['risk_level']}")
        print(f"   Reasoning: {result['reasoning']}")


if __name__ == "__main__":
    main()