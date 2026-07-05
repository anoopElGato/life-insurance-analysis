"""
Web scraping collector for company websites
"""

import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.collectors.base import BaseCollector
from src.utils.models import Document, SourceType
from src.utils.logger import get_logger
from src.utils.helpers import clean_text, extract_domain
from config.settings import PLAYWRIGHT_HEADLESS, REQUEST_TIMEOUT, MAX_RETRIES

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

logger = get_logger("collectors.web")


class WebCollector(BaseCollector):
    """Collector for company websites"""
    
    def __init__(self, company: str, website_url: str):
        super().__init__(company, SourceType.WEBSITE)
        self.website_url = website_url
        self.visited_urls = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def collect(self) -> List[Document]:
        """Collect data from website"""
        try:
            logger.info(f"Starting web collection for {self.company} from {self.website_url}")
            self._scrape_pages([self.website_url])
            logger.info(f"Collected {len(self.documents)} documents from {self.company} website")
            return self.documents
        except Exception as e:
            logger.error(f"Error collecting from {self.company} website: {str(e)}")
            return self.documents
    
    def _scrape_pages(self, urls: List[str], max_depth: int = 3, current_depth: int = 0) -> None:
        """Recursively scrape pages"""
        if current_depth >= max_depth:
            return
        
        for url in urls:
            if url in self.visited_urls or not self._is_valid_url(url):
                continue
            
            self.visited_urls.add(url)
            logger.info(f"Scraping: {url}")
            
            try:
                page_content = self._fetch_page(url)
                if page_content:
                    self._extract_content(url, page_content)
                    
                    # Find links for next level
                    next_urls = self._extract_links(url, page_content)
                    if next_urls and current_depth + 1 < max_depth:
                        self._scrape_pages(next_urls, max_depth, current_depth + 1)
                
                time.sleep(1)  # Be polite to the server
                
            except Exception as e:
                logger.warning(f"Error scraping {url}: {str(e)}")
    
    def _fetch_page(self, url: str, retries: int = MAX_RETRIES) -> Optional[str]:
        """Fetch page content with retry logic"""
        for attempt in range(retries):
            try:
                response = self.session.get(
                    url,
                    timeout=REQUEST_TIMEOUT,
                    allow_redirects=True
                )
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def _extract_content(self, url: str, html_content: str) -> None:
        """Extract meaningful content from HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract title
            title = soup.title.string if soup.title else extract_domain(url)
            
            # Extract main content
            main_content = ""
            
            # Try to find main content area
            main_tag = soup.find("main") or soup.find(class_=["content", "main", "article"])
            if main_tag:
                main_content = main_tag.get_text()
            else:
                # Fallback to body
                body = soup.find("body")
                if body:
                    main_content = body.get_text()
            
            # Extract meta description
            meta_description = ""
            meta_tag = soup.find("meta", attrs={"name": "description"})
            if meta_tag:
                meta_description = meta_tag.get("content", "")
            
            # Combine content
            full_content = f"{title}\n{meta_description}\n{main_content}"
            cleaned_content = clean_text(full_content)
            
            if len(cleaned_content) > 100:
                metadata = {
                    "domain": extract_domain(url),
                    "title": title,
                    "meta_description": meta_description
                }
                
                doc = self.create_document(
                    source_url=url,
                    document_name=f"{self.company}_{title}",
                    raw_text=cleaned_content,
                    metadata=metadata
                )
                self.add_document(doc)
        
        except Exception as e:
            logger.warning(f"Error extracting content from {url}: {str(e)}")
    
    def _extract_links(self, base_url: str, html_content: str) -> List[str]:
        """Extract links from page"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            links = []
            
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').strip()
                if href:
                    absolute_url = urljoin(base_url, href)
                    links.append(absolute_url)
            
            return links
        except Exception as e:
            logger.warning(f"Error extracting links from {base_url}: {str(e)}")
            return []
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and belongs to company domain"""
        try:
            parsed = urlparse(url)
            
            # Check if it's a valid URL
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Check if it belongs to company domain
            base_domain = extract_domain(self.website_url)
            current_domain = extract_domain(url)
            
            if base_domain not in current_domain and current_domain not in base_domain:
                return False
            
            # Skip common file types
            skip_extensions = ['.pdf', '.jpg', '.png', '.gif', '.zip', '.exe', '.mp4']
            if any(url.lower().endswith(ext) for ext in skip_extensions):
                return False
            
            return True
        except Exception:
            return False


__all__ = ["WebCollector"]
