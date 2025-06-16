import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import Dict, List, Optional
import re
from urllib.parse import urljoin, urlparse
import json
from datetime import datetime

class EURLexScraper:
    def __init__(self, delay: float = 1.0):
        self.base_url = "https://eur-lex.europa.eu"
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def search_legal_acts(self, query: str = "", document_types: List[str] = None, 
                         max_results: int = 100) -> List[Dict]:
        """
        Search for legal acts on EUR-Lex
        
        Args:
            query: Search query
            document_types: List of document types (e.g., ['REG', 'DIR', 'DEC'])
            max_results: Maximum number of results to return
        """
        if document_types is None:
            document_types = ['REG', 'DIR', 'DEC', 'REC']  # Regulations, Directives, Decisions, Recommendations
        
        results = []
        
        for doc_type in document_types:
            self.logger.info(f"Searching for {doc_type} documents...")
            
            # Build search URL
            search_url = f"{self.base_url}/search.html"
            params = {
                'scope': 'EURLEX',
                'type': 'quick',
                'lang': 'en',
                'text': query,
                'FM_CODED': doc_type,
                'qid': '1640995200000',
                'DTS_DOM': 'ALL',
                'sort': 'DATE_DOCU',
                'sortOrder': 'DESC'
            }
            
            try:
                response = self.session.get(search_url, params=params)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find search results
                result_items = soup.find_all('div', class_='SearchResult')
                
                for item in result_items[:max_results//len(document_types)]:
                    legal_act = self._parse_search_result(item)
                    if legal_act:
                        results.append(legal_act)
                
                time.sleep(self.delay)
                
            except Exception as e:
                self.logger.error(f"Error searching for {doc_type}: {e}")
                continue
        
        return results[:max_results]
    
    def _parse_search_result(self, result_item) -> Optional[Dict]:
        """Parse a single search result item"""
        try:
            legal_act = {}
            
            # Extract title and URL
            title_link = result_item.find('a', class_='title')
            if title_link:
                legal_act['title'] = title_link.get_text(strip=True)
                legal_act['url'] = urljoin(self.base_url, title_link.get('href', ''))
            
            # Extract CELEX number
            celex_elem = result_item.find('span', class_='celex')
            if celex_elem:
                legal_act['celex_number'] = celex_elem.get_text(strip=True)
            
            # Extract document type
            doc_type_elem = result_item.find('span', class_='documentType')
            if doc_type_elem:
                legal_act['document_type'] = doc_type_elem.get_text(strip=True)
            
            # Extract date
            date_elem = result_item.find('span', class_='date')
            if date_elem:
                legal_act['date_document'] = date_elem.get_text(strip=True)
            
            # Extract summary/description
            summary_elem = result_item.find('div', class_='summary')
            if summary_elem:
                legal_act['summary'] = summary_elem.get_text(strip=True)
            
            return legal_act
            
        except Exception as e:
            self.logger.error(f"Error parsing search result: {e}")
            return None
    
    def get_document_details(self, celex_number: str) -> Optional[Dict]:
        """
        Get detailed information about a specific document
        
        Args:
            celex_number: CELEX number of the document
        """
        try:
            # Build document URL
            doc_url = f"{self.base_url}/legal-content/EN/TXT/?uri=CELEX:{celex_number}"
            
            response = self.session.get(doc_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            document_details = {
                'celex_number': celex_number,
                'url': doc_url
            }
            
            # Extract title
            title_elem = soup.find('h1', class_='doc-ti')
            if title_elem:
                document_details['title'] = title_elem.get_text(strip=True)
            
            # Extract content
            content_elem = soup.find('div', {'id': 'text'})
            if content_elem:
                # Remove script and style elements
                for script in content_elem(["script", "style"]):
                    script.decompose()
                document_details['content'] = content_elem.get_text(strip=True)
            
            # Extract metadata
            metadata = self._extract_metadata(soup)
            document_details.update(metadata)
            
            time.sleep(self.delay)
            
            return document_details
            
        except Exception as e:
            self.logger.error(f"Error getting document details for {celex_number}: {e}")
            return None
    
    def _extract_metadata(self, soup) -> Dict:
        """Extract metadata from document page"""
        metadata = {}
        
        try:
            # Extract subject matter
            subject_elem = soup.find('dd', {'data-testid': 'subject-matter'})
            if subject_elem:
                metadata['subject_matter'] = subject_elem.get_text(strip=True)
            
            # Extract directory code
            directory_elem = soup.find('dd', {'data-testid': 'directory-code'})
            if directory_elem:
                metadata['directory_code'] = directory_elem.get_text(strip=True)
            
            # Extract dates
            date_force_elem = soup.find('dd', {'data-testid': 'date-force'})
            if date_force_elem:
                metadata['date_force'] = date_force_elem.get_text(strip=True)
            
            date_end_elem = soup.find('dd', {'data-testid': 'date-end-validity'})
            if date_end_elem:
                metadata['date_end_validity'] = date_end_elem.get_text(strip=True)
            
            # Extract keywords
            keywords_elem = soup.find('dd', {'data-testid': 'keywords'})
            if keywords_elem:
                metadata['keywords'] = keywords_elem.get_text(strip=True)
            
        except Exception as e:
            self.logger.error(f"Error extracting metadata: {e}")
        
        return metadata
    
    def scrape_recent_acts(self, days: int = 30, max_results: int = 100) -> List[Dict]:
        """
        Scrape recent legal acts from the last N days
        
        Args:
            days: Number of days to look back
            max_results: Maximum number of results
        """
        self.logger.info(f"Scraping legal acts from the last {days} days...")
        
        # Use the search functionality to get recent acts
        results = self.search_legal_acts(query="", max_results=max_results)
        
        # Get detailed information for each act
        detailed_results = []
        for result in results:
            if 'celex_number' in result:
                details = self.get_document_details(result['celex_number'])
                if details:
                    # Merge search result with detailed info
                    result.update(details)
                    detailed_results.append(result)
                
                if len(detailed_results) >= max_results:
                    break
        
        return detailed_results
    
    def scrape_by_subject(self, subject_areas: List[str], max_per_subject: int = 20) -> List[Dict]:
        """
        Scrape legal acts by subject areas
        
        Args:
            subject_areas: List of subject areas to search for
            max_per_subject: Maximum results per subject area
        """
        all_results = []
        
        for subject in subject_areas:
            self.logger.info(f"Scraping acts for subject: {subject}")
            results = self.search_legal_acts(query=subject, max_results=max_per_subject)
            
            for result in results:
                if 'celex_number' in result:
                    details = self.get_document_details(result['celex_number'])
                    if details:
                        result.update(details)
                        all_results.append(result)
        
        return all_results