import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple, Optional
import logging
import pickle

class TextAnalyzer:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the text analyzer with sentence transformers and other models
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.logger = logging.getLogger(__name__)
        
        # Load sentence transformer for embeddings
        self.logger.info(f"Loading sentence transformer model: {model_name}")
        self.sentence_model = SentenceTransformer(model_name)
        
        # Load summarization pipeline
        self.logger.info("Loading summarization model...")
        self.summarizer = pipeline("summarization", 
                                 model="facebook/bart-large-cnn",
                                 device=0 if torch.cuda.is_available() else -1)
        
        # Load classification pipeline for legal domain classification
        self.logger.info("Loading classification model...")
        self.classifier = pipeline("zero-shot-classification",
                                 model="facebook/bart-large-mnli",
                                 device=0 if torch.cuda.is_available() else -1)
        
        # Legal domain categories
        self.legal_categories = [
            "Data Protection and Privacy",
            "Financial Services and Banking",
            "Environmental Law",
            "Competition and Antitrust",
            "Employment and Labor Law",
            "Consumer Protection",
            "Digital Services and Technology",
            "Healthcare and Pharmaceuticals",
            "Energy and Utilities",
            "Transportation and Logistics",
            "Agriculture and Food Safety",
            "Telecommunications",
            "Construction and Real Estate",
            "Manufacturing and Industry",
            "Trade and Customs",
            "Tax and Fiscal Policy",
            "Corporate Governance",
            "Intellectual Property",
            "Public Procurement",
            "State Aid and Subsidies"
        ]
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a given text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as numpy array
        """
        try:
            # Clean and truncate text if too long
            cleaned_text = self._clean_text(text)
            embedding = self.sentence_model.encode(cleaned_text)
            return embedding
        except Exception as e:
            self.logger.error(f"Error generating embedding: {e}")
            return np.zeros(self.sentence_model.get_sentence_embedding_dimension())
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            similarity = cosine_similarity([embedding1], [embedding2])[0][0]
            return float(similarity)
        except Exception as e:
            self.logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def analyze_company_legal_relevance(self, company_profile: Dict, legal_act: Dict) -> Dict:
        """
        Analyze the relevance of a legal act to a company profile
        
        Args:
            company_profile: Company profile dictionary
            legal_act: Legal act dictionary
            
        Returns:
            Analysis result with relevance score and reasoning
        """
        try:
            # Generate embeddings
            company_text = self._create_company_text(company_profile)
            legal_text = self._create_legal_text(legal_act)
            
            company_embedding = self.generate_embedding(company_text)
            legal_embedding = self.generate_embedding(legal_text)
            
            # Calculate base similarity
            base_similarity = self.calculate_similarity(company_embedding, legal_embedding)
            
            # Classify legal act into categories
            legal_categories = self._classify_legal_act(legal_text)
            
            # Analyze company industry relevance
            industry_relevance = self._analyze_industry_relevance(
                company_profile.get('industry', ''),
                legal_categories
            )
            
            # Calculate weighted relevance score
            relevance_score = self._calculate_weighted_relevance(
                base_similarity, industry_relevance, company_profile, legal_act
            )
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                company_profile, legal_act, legal_categories, 
                base_similarity, industry_relevance, relevance_score
            )
            
            return {
                'relevance_score': relevance_score,
                'base_similarity': base_similarity,
                'industry_relevance': industry_relevance,
                'legal_categories': legal_categories,
                'reasoning': reasoning
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing relevance: {e}")
            return {
                'relevance_score': 0.0,
                'reasoning': f"Error in analysis: {str(e)}"
            }
    
    def _create_company_text(self, company_profile: Dict) -> str:
        """Create a comprehensive text representation of the company"""
        parts = []
        
        if company_profile.get('company_name'):
            parts.append(f"Company: {company_profile['company_name']}")
        
        if company_profile.get('industry'):
            parts.append(f"Industry: {company_profile['industry']}")
        
        if company_profile.get('business_description'):
            parts.append(f"Business: {company_profile['business_description']}")
        
        if company_profile.get('business_activities'):
            parts.append(f"Activities: {company_profile['business_activities']}")
        
        if company_profile.get('compliance_areas'):
            parts.append(f"Compliance areas: {company_profile['compliance_areas']}")
        
        return " ".join(parts)
    
    def _create_legal_text(self, legal_act: Dict) -> str:
        """Create a comprehensive text representation of the legal act"""
        parts = []
        
        if legal_act.get('title'):
            parts.append(legal_act['title'])
        
        if legal_act.get('summary'):
            parts.append(legal_act['summary'])
        
        if legal_act.get('subject_matter'):
            parts.append(legal_act['subject_matter'])
        
        if legal_act.get('keywords'):
            parts.append(legal_act['keywords'])
        
        # Include a portion of the content if available
        if legal_act.get('content'):
            content = legal_act['content'][:2000]  # First 2000 characters
            parts.append(content)
        
        return " ".join(parts)
    
    def _classify_legal_act(self, legal_text: str) -> List[Dict]:
        """Classify legal act into relevant categories"""
        try:
            result = self.classifier(legal_text, self.legal_categories)
            
            # Return top 3 categories with scores
            categories = []
            for label, score in zip(result['labels'][:3], result['scores'][:3]):
                categories.append({
                    'category': label,
                    'confidence': float(score)
                })
            
            return categories
            
        except Exception as e:
            self.logger.error(f"Error classifying legal act: {e}")
            return []
    
    def _analyze_industry_relevance(self, company_industry: str, legal_categories: List[Dict]) -> float:
        """Analyze how relevant the legal categories are to the company's industry"""
        if not company_industry or not legal_categories:
            return 0.5  # Neutral relevance
        
        # Industry-category mapping (simplified)
        industry_mappings = {
            'technology': ['Data Protection and Privacy', 'Digital Services and Technology', 'Telecommunications'],
            'finance': ['Financial Services and Banking', 'Data Protection and Privacy'],
            'healthcare': ['Healthcare and Pharmaceuticals', 'Data Protection and Privacy'],
            'manufacturing': ['Manufacturing and Industry', 'Environmental Law', 'Employment and Labor Law'],
            'retail': ['Consumer Protection', 'Data Protection and Privacy'],
            'energy': ['Energy and Utilities', 'Environmental Law'],
            'transportation': ['Transportation and Logistics', 'Environmental Law'],
            'agriculture': ['Agriculture and Food Safety', 'Environmental Law'],
            'construction': ['Construction and Real Estate', 'Environmental Law', 'Employment and Labor Law']
        }
        
        company_industry_lower = company_industry.lower()
        relevant_categories = []
        
        for industry_key, categories in industry_mappings.items():
            if industry_key in company_industry_lower:
                relevant_categories.extend(categories)
        
        if not relevant_categories:
            return 0.5  # Neutral if no specific mapping found
        
        # Calculate relevance based on category matches
        total_relevance = 0.0
        for legal_cat in legal_categories:
            if legal_cat['category'] in relevant_categories:
                total_relevance += legal_cat['confidence']
        
        return min(total_relevance, 1.0)
    
    def _calculate_weighted_relevance(self, base_similarity: float, industry_relevance: float,
                                    company_profile: Dict, legal_act: Dict) -> float:
        """Calculate weighted relevance score"""
        # Base weights
        similarity_weight = 0.4
        industry_weight = 0.3
        content_weight = 0.2
        recency_weight = 0.1
        
        # Content relevance (based on keywords and compliance areas)
        content_relevance = self._calculate_content_relevance(company_profile, legal_act)
        
        # Recency relevance (newer acts might be more relevant)
        recency_relevance = self._calculate_recency_relevance(legal_act)
        
        # Calculate weighted score
        weighted_score = (
            base_similarity * similarity_weight +
            industry_relevance * industry_weight +
            content_relevance * content_weight +
            recency_relevance * recency_weight
        )
        
        return min(weighted_score, 1.0)
    
    def _calculate_content_relevance(self, company_profile: Dict, legal_act: Dict) -> float:
        """Calculate relevance based on content overlap"""
        company_keywords = set()
        legal_keywords = set()
        
        # Extract keywords from company profile
        for field in ['business_description', 'business_activities', 'compliance_areas']:
            if company_profile.get(field):
                company_keywords.update(company_profile[field].lower().split())
        
        # Extract keywords from legal act
        for field in ['title', 'summary', 'keywords', 'subject_matter']:
            if legal_act.get(field):
                legal_keywords.update(legal_act[field].lower().split())
        
        # Calculate Jaccard similarity
        if not company_keywords or not legal_keywords:
            return 0.5
        
        intersection = len(company_keywords.intersection(legal_keywords))
        union = len(company_keywords.union(legal_keywords))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_recency_relevance(self, legal_act: Dict) -> float:
        """Calculate relevance based on how recent the legal act is"""
        # This is a simplified implementation
        # In practice, you'd parse the actual dates
        return 0.7  # Default moderate recency score
    
    def _generate_reasoning(self, company_profile: Dict, legal_act: Dict, 
                          legal_categories: List[Dict], base_similarity: float,
                          industry_relevance: float, relevance_score: float) -> str:
        """Generate human-readable reasoning for the relevance score"""
        reasoning_parts = []
        
        # Overall assessment
        if relevance_score >= 0.8:
            reasoning_parts.append("This legal act is highly relevant to your company.")
        elif relevance_score >= 0.6:
            reasoning_parts.append("This legal act is moderately relevant to your company.")
        elif relevance_score >= 0.4:
            reasoning_parts.append("This legal act has some relevance to your company.")
        else:
            reasoning_parts.append("This legal act has limited relevance to your company.")
        
        # Industry relevance
        if industry_relevance >= 0.7:
            reasoning_parts.append(f"The act strongly aligns with your industry ({company_profile.get('industry', 'N/A')}).")
        elif industry_relevance >= 0.5:
            reasoning_parts.append(f"The act has moderate alignment with your industry ({company_profile.get('industry', 'N/A')}).")
        
        # Legal categories
        if legal_categories:
            top_category = legal_categories[0]['category']
            confidence = legal_categories[0]['confidence']
            reasoning_parts.append(f"The act primarily relates to {top_category} (confidence: {confidence:.2f}).")
        
        # Specific recommendations
        if relevance_score >= 0.7:
            reasoning_parts.append("We recommend reviewing this act for compliance requirements.")
        elif relevance_score >= 0.5:
            reasoning_parts.append("Consider reviewing this act to assess potential impact.")
        
        return " ".join(reasoning_parts)
    
    def _clean_text(self, text: str, max_length: int = 5000) -> str:
        """Clean and truncate text for processing"""
        if not text:
            return ""
        
        # Remove extra whitespace and truncate
        cleaned = " ".join(text.split())
        return cleaned[:max_length] if len(cleaned) > max_length else cleaned
    
    def summarize_legal_act(self, legal_act: Dict, max_length: int = 150) -> str:
        """Generate a summary of a legal act"""
        try:
            content = legal_act.get('content', '')
            if not content:
                return legal_act.get('summary', 'No summary available.')
            
            # Use the first part of content for summarization
            text_to_summarize = content[:1000]
            
            summary = self.summarizer(text_to_summarize, 
                                    max_length=max_length, 
                                    min_length=50, 
                                    do_sample=False)
            
            return summary[0]['summary_text']
            
        except Exception as e:
            self.logger.error(f"Error summarizing legal act: {e}")
            return legal_act.get('summary', 'Summary not available.')