import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import Dict, List, Optional, Set
import re
from urllib.parse import urljoin, urlparse, parse_qs
import json
from datetime import datetime
import concurrent.futures
from threading import Lock
import sqlite3
import os
import sys

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.db_manager import DatabaseManager

class EURLexDirectoryScraper:
    """
    Comprehensive scraper for EUR-Lex directory of legal acts
    Systematically scrapes the directory structure and populates the database
    """
    
    def __init__(self, delay: float = 1.0, max_workers: int = 5):
        self.base_url = "https://eur-lex.europa.eu"
        self.delay = delay
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Initialize database
        self.db = DatabaseManager()
        
        # Thread-safe set to track processed documents
        self.processed_celexes = set()
        self.lock = Lock()
        
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Load existing CELEX numbers to avoid duplicates
        self._load_existing_celexes()
    
    def _load_existing_celexes(self):
        """Load existing CELEX numbers from database to avoid duplicates"""
        try:
            existing_acts = self.db.get_legal_acts()
            self.processed_celexes = {act.get('celex_number') for act in existing_acts if act.get('celex_number')}
            self.logger.info(f"Loaded {len(self.processed_celexes)} existing CELEX numbers from database")
        except Exception as e:
            self.logger.error(f"Error loading existing CELEX numbers: {e}")
            self.processed_celexes = set()
    
    def scrape_directory_structure(self) -> List[Dict]:
        """
        Scrape the main directory structure to get all subject areas and categories
        """
        self.logger.info("Starting directory structure scraping...")
        
        directory_url = f"{self.base_url}/browse/directories/legislation.html"
        
        try:
            response = self.session.get(directory_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all directory categories
            categories = []
            
            # Look for directory links - these might be in different structures
            directory_links = soup.find_all('a', href=re.compile(r'/browse/directories/'))
            
            for link in directory_links:
                href = link.get('href')
                text = link.get_text(strip=True)
                
                if href and text and 'legislation' not in href.lower():
                    category = {
                        'name': text,
                        'url': urljoin(self.base_url, href),
                        'code': self._extract_directory_code(href)
                    }
                    categories.append(category)
            
            # Also try to find subject matter classifications
            subject_links = soup.find_all('a', href=re.compile(r'subject-matter'))
            for link in subject_links:
                href = link.get('href')
                text = link.get_text(strip=True)
                
                if href and text:
                    category = {
                        'name': text,
                        'url': urljoin(self.base_url, href),
                        'code': self._extract_subject_code(href)
                    }
                    categories.append(category)
            
            self.logger.info(f"Found {len(categories)} directory categories")
            return categories
            
        except Exception as e:
            self.logger.error(f"Error scraping directory structure: {e}")
            return []
    
    def _extract_directory_code(self, href: str) -> str:
        """Extract directory code from URL"""
        try:
            # Extract code from URL patterns like /browse/directories/01.html
            match = re.search(r'/directories/([^/]+)\.html', href)
            if match:
                return match.group(1)
            return ""
        except:
            return ""
    
    def _extract_subject_code(self, href: str) -> str:
        """Extract subject code from URL"""
        try:
            # Extract from query parameters or path
            parsed = urlparse(href)
            query_params = parse_qs(parsed.query)
            
            if 'subject' in query_params:
                return query_params['subject'][0]
            
            # Try to extract from path
            match = re.search(r'subject[_-]([^/&]+)', href)
            if match:
                return match.group(1)
            
            return ""
        except:
            return ""
    
    def scrape_comprehensive_legal_acts(self, max_acts: int = 5000) -> int:
        """
        Comprehensive scraping of EU legal acts using multiple approaches
        
        Args:
            max_acts: Maximum number of acts to scrape
            
        Returns:
            Number of acts successfully scraped and stored
        """
        self.logger.info(f"Starting comprehensive scraping of up to {max_acts} legal acts...")
        
        scraped_count = 0
        
        # Approach 1: Search by document types
        scraped_count += self._scrape_by_document_types(max_acts // 4)
        
        # Approach 2: Search by years (recent to older)
        scraped_count += self._scrape_by_years(max_acts // 4)
        
        # Approach 3: Search by subject areas
        scraped_count += self._scrape_by_subjects(max_acts // 4)
        
        # Approach 4: Browse recent legislation
        scraped_count += self._scrape_recent_legislation(max_acts // 4)
        
        self.logger.info(f"Comprehensive scraping completed. Total acts scraped: {scraped_count}")
        return scraped_count
    
    def _scrape_by_document_types(self, max_per_type: int = 500) -> int:
        """Scrape by different document types"""
        self.logger.info("Scraping by document types...")
        
        document_types = [
            ('REG', 'Regulation'),
            ('DIR', 'Directive'), 
            ('DEC', 'Decision'),
            ('REC', 'Recommendation'),
            ('OPI', 'Opinion'),
            ('RES', 'Resolution'),
            ('DEC_IMPL', 'Implementing Decision'),
            ('REG_IMPL', 'Implementing Regulation'),
            ('DIR_DELEG', 'Delegated Directive'),
            ('REG_DELEG', 'Delegated Regulation')
        ]
        
        total_scraped = 0
        
        for doc_code, doc_name in document_types:
            self.logger.info(f"Scraping {doc_name} documents...")
            
            try:
                acts = self._search_by_document_type(doc_code, max_per_type)
                saved_count = self._process_and_save_acts(acts)
                total_scraped += saved_count
                
                self.logger.info(f"Scraped {saved_count} {doc_name} documents")
                
                time.sleep(self.delay)
                
            except Exception as e:
                self.logger.error(f"Error scraping {doc_name}: {e}")
                continue
        
        return total_scraped
    
    def _scrape_by_years(self, max_per_year: int = 200) -> int:
        """Scrape by years from recent to older"""
        self.logger.info("Scraping by years...")
        
        current_year = datetime.now().year
        years = list(range(current_year, current_year - 10, -1))  # Last 10 years
        
        total_scraped = 0
        
        for year in years:
            self.logger.info(f"Scraping acts from year {year}...")
            
            try:
                acts = self._search_by_year(year, max_per_year)
                saved_count = self._process_and_save_acts(acts)
                total_scraped += saved_count
                
                self.logger.info(f"Scraped {saved_count} acts from {year}")
                
                time.sleep(self.delay)
                
            except Exception as e:
                self.logger.error(f"Error scraping year {year}: {e}")
                continue
        
        return total_scraped
    
    def _scrape_by_subjects(self, max_per_subject: int = 100) -> int:
        """Scrape by subject areas"""
        self.logger.info("Scraping by subject areas...")
        
        subjects = [
            'competition', 'environment', 'agriculture', 'transport', 'energy',
            'digital', 'health', 'consumer', 'employment', 'taxation',
            'trade', 'migration', 'security', 'justice', 'education',
            'research', 'fisheries', 'regional', 'budget', 'external'
        ]
        
        total_scraped = 0
        
        for subject in subjects:
            self.logger.info(f"Scraping acts for subject: {subject}...")
            
            try:
                acts = self._search_by_subject(subject, max_per_subject)
                saved_count = self._process_and_save_acts(acts)
                total_scraped += saved_count
                
                self.logger.info(f"Scraped {saved_count} acts for {subject}")
                
                time.sleep(self.delay)
                
            except Exception as e:
                self.logger.error(f"Error scraping subject {subject}: {e}")
                continue
        
        return total_scraped
    
    def _scrape_recent_legislation(self, max_acts: int = 500) -> int:
        """Scrape recent legislation"""
        self.logger.info("Scraping recent legislation...")
        
        try:
            # Use the recent legislation page
            recent_url = f"{self.base_url}/collection/eu-law/legal-acts/recent.html"
            
            response = self.session.get(recent_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all legal act links
            act_links = soup.find_all('a', href=re.compile(r'legal-content'))
            
            acts = []
            for link in act_links[:max_acts]:
                href = link.get('href')
                if href:
                    celex = self._extract_celex_from_url(href)
                    if celex and celex not in self.processed_celexes:
                        acts.append({'celex_number': celex, 'url': urljoin(self.base_url, href)})
            
            saved_count = self._process_and_save_acts(acts)
            self.logger.info(f"Scraped {saved_count} recent acts")
            
            return saved_count
            
        except Exception as e:
            self.logger.error(f"Error scraping recent legislation: {e}")
            return 0
    
    def _search_by_document_type(self, doc_type: str, max_results: int) -> List[Dict]:
        """Search for documents by type"""
        search_url = f"{self.base_url}/search.html"
        
        params = {
            'scope': 'EURLEX',
            'type': 'quick',
            'lang': 'en',
            'FM_CODED': doc_type,
            'qid': str(int(time.time() * 1000)),
            'DTS_DOM': 'ALL',
            'sort': 'DATE_DOCU',
            'sortOrder': 'DESC'
        }
        
        return self._perform_search(search_url, params, max_results)
    
    def _search_by_year(self, year: int, max_results: int) -> List[Dict]:
        """Search for documents by year"""
        search_url = f"{self.base_url}/search.html"
        
        params = {
            'scope': 'EURLEX',
            'type': 'quick',
            'lang': 'en',
            'DD_YEAR': str(year),
            'qid': str(int(time.time() * 1000)),
            'DTS_DOM': 'ALL',
            'sort': 'DATE_DOCU',
            'sortOrder': 'DESC'
        }
        
        return self._perform_search(search_url, params, max_results)
    
    def _search_by_subject(self, subject: str, max_results: int) -> List[Dict]:
        """Search for documents by subject"""
        search_url = f"{self.base_url}/search.html"
        
        params = {
            'scope': 'EURLEX',
            'type': 'quick',
            'lang': 'en',
            'text': subject,
            'qid': str(int(time.time() * 1000)),
            'DTS_DOM': 'ALL',
            'sort': 'DATE_DOCU',
            'sortOrder': 'DESC'
        }
        
        return self._perform_search(search_url, params, max_results)
    
    def _perform_search(self, search_url: str, params: Dict, max_results: int) -> List[Dict]:
        """Perform search and extract results"""
        acts = []
        page = 1
        
        while len(acts) < max_results:
            try:
                # Add pagination
                current_params = params.copy()
                current_params['page'] = page
                
                response = self.session.get(search_url, params=current_params)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find search results
                result_items = soup.find_all('div', class_='SearchResult')
                
                if not result_items:
                    # Try alternative selectors
                    result_items = soup.find_all('li', class_='result')
                    if not result_items:
                        result_items = soup.find_all('div', class_='result-item')
                
                if not result_items:
                    break
                
                page_acts = []
                for item in result_items:
                    act = self._parse_search_result_comprehensive(item)
                    if act and act.get('celex_number') not in self.processed_celexes:
                        page_acts.append(act)
                
                acts.extend(page_acts)
                
                if len(page_acts) == 0:
                    break
                
                page += 1
                time.sleep(self.delay)
                
            except Exception as e:
                self.logger.error(f"Error in search page {page}: {e}")
                break
        
        return acts[:max_results]
    
    def _parse_search_result_comprehensive(self, result_item) -> Optional[Dict]:
        """Parse search result with comprehensive data extraction"""
        try:
            act = {}
            
            # Extract title and URL
            title_selectors = [
                'a.title', 'a.result-title', '.title a', 'h3 a', '.document-title a'
            ]
            
            title_link = None
            for selector in title_selectors:
                title_link = result_item.select_one(selector)
                if title_link:
                    break
            
            if title_link:
                act['title'] = title_link.get_text(strip=True)
                href = title_link.get('href', '')
                act['url'] = urljoin(self.base_url, href)
                act['celex_number'] = self._extract_celex_from_url(href)
            
            # Extract document type
            doc_type_selectors = [
                '.documentType', '.doc-type', '.type', '[class*="type"]'
            ]
            
            for selector in doc_type_selectors:
                doc_type_elem = result_item.select_one(selector)
                if doc_type_elem:
                    act['document_type'] = doc_type_elem.get_text(strip=True)
                    break
            
            # Extract date
            date_selectors = [
                '.date', '.document-date', '.pub-date', '[class*="date"]'
            ]
            
            for selector in date_selectors:
                date_elem = result_item.select_one(selector)
                if date_elem:
                    act['date_document'] = date_elem.get_text(strip=True)
                    break
            
            # Extract summary
            summary_selectors = [
                '.summary', '.description', '.abstract', '.excerpt'
            ]
            
            for selector in summary_selectors:
                summary_elem = result_item.select_one(selector)
                if summary_elem:
                    act['summary'] = summary_elem.get_text(strip=True)
                    break
            
            # Extract CELEX if not found in URL
            if not act.get('celex_number'):
                celex_selectors = [
                    '.celex', '.document-number', '.reference'
                ]
                
                for selector in celex_selectors:
                    celex_elem = result_item.select_one(selector)
                    if celex_elem:
                        celex_text = celex_elem.get_text(strip=True)
                        celex = self._extract_celex_from_text(celex_text)
                        if celex:
                            act['celex_number'] = celex
                            break
            
            return act if act.get('celex_number') else None
            
        except Exception as e:
            self.logger.error(f"Error parsing search result: {e}")
            return None
    
    def _extract_celex_from_url(self, url: str) -> Optional[str]:
        """Extract CELEX number from URL"""
        try:
            # Pattern for CELEX in URL: CELEX:32021R0001 or uri=CELEX:32021R0001
            match = re.search(r'CELEX:?([0-9]{5}[A-Z][0-9]{4})', url, re.IGNORECASE)
            if match:
                return match.group(1)
            
            # Alternative patterns
            match = re.search(r'celex[=:]([^&/]+)', url, re.IGNORECASE)
            if match:
                return match.group(1)
            
            return None
        except:
            return None
    
    def _extract_celex_from_text(self, text: str) -> Optional[str]:
        """Extract CELEX number from text"""
        try:
            # Standard CELEX pattern: 32021R0001
            match = re.search(r'\b([0-9]{5}[A-Z][0-9]{4})\b', text)
            if match:
                return match.group(1)
            
            return None
        except:
            return None
    
    def _process_and_save_acts(self, acts: List[Dict]) -> int:
        """Process and save acts to database with detailed information"""
        saved_count = 0
        
        # Use thread pool for parallel processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_act = {
                executor.submit(self._get_detailed_act_info, act): act 
                for act in acts
            }
            
            for future in concurrent.futures.as_completed(future_to_act):
                try:
                    detailed_act = future.result()
                    if detailed_act:
                        # Save to database
                        self.db.save_legal_act(detailed_act)
                        
                        with self.lock:
                            self.processed_celexes.add(detailed_act.get('celex_number'))
                        
                        saved_count += 1
                        
                        if saved_count % 10 == 0:
                            self.logger.info(f"Saved {saved_count} acts so far...")
                
                except Exception as e:
                    self.logger.error(f"Error processing act: {e}")
                    continue
        
        return saved_count
    
    def _get_detailed_act_info(self, act: Dict) -> Optional[Dict]:
        """Get detailed information for a legal act"""
        try:
            celex = act.get('celex_number')
            if not celex:
                return None
            
            # Check if already processed
            with self.lock:
                if celex in self.processed_celexes:
                    return None
            
            # Get document details
            doc_url = f"{self.base_url}/legal-content/EN/TXT/?uri=CELEX:{celex}"
            
            response = self.session.get(doc_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Update act with detailed information
            detailed_act = act.copy()
            detailed_act['url'] = doc_url
            
            # Extract title if not present
            if not detailed_act.get('title'):
                title_selectors = ['h1.doc-ti', 'h1', '.document-title', '.title']
                for selector in title_selectors:
                    title_elem = soup.select_one(selector)
                    if title_elem:
                        detailed_act['title'] = title_elem.get_text(strip=True)
                        break
            
            # Extract content
            content_selectors = ['#text', '.document-content', '.content', 'main']
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Remove script and style elements
                    for script in content_elem(["script", "style"]):
                        script.decompose()
                    
                    content_text = content_elem.get_text(strip=True)
                    if len(content_text) > 100:  # Only save if substantial content
                        detailed_act['content'] = content_text[:10000]  # Limit content size
                        break
            
            # Extract metadata
            metadata = self._extract_comprehensive_metadata(soup)
            detailed_act.update(metadata)
            
            time.sleep(self.delay)
            
            return detailed_act
            
        except Exception as e:
            self.logger.error(f"Error getting detailed info for {act.get('celex_number', 'unknown')}: {e}")
            return None
    
    def _extract_comprehensive_metadata(self, soup) -> Dict:
        """Extract comprehensive metadata from document page"""
        metadata = {}
        
        try:
            # Define metadata mappings
            metadata_mappings = {
                'subject_matter': ['subject-matter', 'subject', 'subjects'],
                'directory_code': ['directory-code', 'directory', 'classification'],
                'date_force': ['date-force', 'entry-into-force', 'force-date'],
                'date_end_validity': ['date-end-validity', 'end-validity', 'validity-end'],
                'keywords': ['keywords', 'descriptors', 'terms'],
                'legal_basis': ['legal-basis', 'basis', 'legal-base'],
                'procedure': ['procedure', 'legislative-procedure'],
                'addressee': ['addressee', 'addressed-to']
            }
            
            # Extract using data-testid attributes
            for field, test_ids in metadata_mappings.items():
                for test_id in test_ids:
                    elem = soup.find('dd', {'data-testid': test_id})
                    if not elem:
                        elem = soup.find('span', {'data-testid': test_id})
                    if not elem:
                        elem = soup.find('div', {'data-testid': test_id})
                    
                    if elem:
                        metadata[field] = elem.get_text(strip=True)
                        break
            
            # Extract from metadata tables
            metadata_tables = soup.find_all('table', class_='metadata')
            for table in metadata_tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        
                        # Map common metadata fields
                        if 'subject' in key:
                            metadata['subject_matter'] = value
                        elif 'directory' in key or 'classification' in key:
                            metadata['directory_code'] = value
                        elif 'keyword' in key or 'descriptor' in key:
                            metadata['keywords'] = value
                        elif 'force' in key and 'date' in key:
                            metadata['date_force'] = value
                        elif 'validity' in key and 'end' in key:
                            metadata['date_end_validity'] = value
            
            # Extract from definition lists
            dts = soup.find_all('dt')
            for dt in dts:
                dd = dt.find_next_sibling('dd')
                if dd:
                    key = dt.get_text(strip=True).lower()
                    value = dd.get_text(strip=True)
                    
                    if 'subject' in key:
                        metadata['subject_matter'] = value
                    elif 'directory' in key:
                        metadata['directory_code'] = value
                    elif 'keyword' in key:
                        metadata['keywords'] = value
            
        except Exception as e:
            self.logger.error(f"Error extracting metadata: {e}")
        
        return metadata
    
    def get_scraping_stats(self) -> Dict:
        """Get current scraping statistics"""
        total_acts = self.db.get_legal_act_count()
        
        return {
            'total_acts_in_db': total_acts,
            'processed_celexes': len(self.processed_celexes),
            'timestamp': datetime.now().isoformat()
        }


def main():
    """Main function to run the comprehensive scraper"""
    scraper = EURLexDirectoryScraper(delay=1.0, max_workers=3)
    
    print("🇪🇺 Starting comprehensive EUR-Lex directory scraping...")
    print(f"📊 Current database stats: {scraper.get_scraping_stats()}")
    
    # Scrape comprehensive legal acts
    scraped_count = scraper.scrape_comprehensive_legal_acts(max_acts=2000)
    
    print(f"✅ Scraping completed! Scraped {scraped_count} legal acts")
    print(f"📊 Final database stats: {scraper.get_scraping_stats()}")


if __name__ == "__main__":
    main()