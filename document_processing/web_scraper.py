import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import os
from typing import Dict, List, Optional, Any
from app.config import SCRAPER_API_KEY

class WebScraper:
    """
    Class to scrape job descriptions from various job posting websites
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        # API key for scraper service (if used)
        self.scraper_api_key = SCRAPER_API_KEY
    
    def scrape_job_description(self, url: str) -> str:
        """
        Scrape job description from a URL
        
        Args:
            url: URL to the job posting
            
        Returns:
            Job description text
        """
        # Extract domain to determine which scraper to use
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        # Select appropriate scraper based on domain
        if 'linkedin.com' in domain:
            return self._scrape_linkedin(url)
        elif 'indeed.com' in domain:
            return self._scrape_indeed(url)
        elif 'glassdoor.com' in domain:
            return self._scrape_glassdoor(url)
        else:
            # Generic scraper for unknown sites
            return self._scrape_generic(url)
    
    def _get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """
        Get page content using requests or scraper API
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object of the page content
        """
        try:
            # If a scraper API key is provided, use it
            if self.scraper_api_key:
                scraper_url = f"http://api.scraperapi.com?api_key={self.scraper_api_key}&url={url}"
                response = requests.get(scraper_url, timeout=30)
            else:
                # Otherwise use direct requests
                response = requests.get(url, headers=self.headers, timeout=15)
            
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"Error fetching URL {url}: {e}")
            return None
    
    def _scrape_linkedin(self, url: str) -> str:
        """
        Scrape job description from LinkedIn
        
        Args:
            url: LinkedIn job posting URL
            
        Returns:
            Job description text
        """
        soup = self._get_page_content(url)
        if not soup:
            return ""
        
        job_description = ""
        
        # Try to get job description from LinkedIn
        try:
            # Look for job description container
            job_desc_divs = soup.select("div.description__text")
            if job_desc_divs:
                job_description = job_desc_divs[0].get_text(separator='\n', strip=True)
            else:
                # Alternative selectors
                job_desc_divs = soup.select(".job-view-layout")
                if job_desc_divs:
                    job_description = job_desc_divs[0].get_text(separator='\n', strip=True)
        except Exception as e:
            print(f"Error scraping LinkedIn: {e}")
        
        return job_description
    
    def _scrape_indeed(self, url: str) -> str:
        """
        Scrape job description from Indeed
        
        Args:
            url: Indeed job posting URL
            
        Returns:
            Job description text
        """
        soup = self._get_page_content(url)
        if not soup:
            return ""
        
        job_description = ""
        
        # Try to get job description from Indeed
        try:
            # Look for job description container
            job_desc_div = soup.select_one("#jobDescriptionText")
            if job_desc_div:
                job_description = job_desc_div.get_text(separator='\n', strip=True)
        except Exception as e:
            print(f"Error scraping Indeed: {e}")
        
        return job_description
    
    def _scrape_glassdoor(self, url: str) -> str:
        """
        Scrape job description from Glassdoor
        
        Args:
            url: Glassdoor job posting URL
            
        Returns:
            Job description text
        """
        soup = self._get_page_content(url)
        if not soup:
            return ""
        
        job_description = ""
        
        # Try to get job description from Glassdoor
        try:
            # Look for job description container
            job_desc_div = soup.select_one(".jobDescriptionContent")
            if job_desc_div:
                job_description = job_desc_div.get_text(separator='\n', strip=True)
        except Exception as e:
            print(f"Error scraping Glassdoor: {e}")
        
        return job_description
    
    def _scrape_generic(self, url: str) -> str:
        """
        Generic scraper for unknown sites
        
        Args:
            url: Job posting URL
            
        Returns:
            Job description text
        """
        soup = self._get_page_content(url)
        if not soup:
            return ""
        
        job_description = ""
        
        # Try to find job description content
        try:
            # Common selectors that might contain job descriptions
            potential_selectors = [
                "div.job-description",
                "div.description",
                "div.jobDescription",
                "div.job_description",
                "div#job-description",
                "div#jobDescription",
                "section.job-description",
                "div[data-testid='jobDescriptionText']",
                "div.details",
                "article"
            ]
        for selector in potential_selectors:
                desc_container = soup.select_one(selector)
                if desc_container:
                    job_description = desc_container.get_text(separator='\n', strip=True)
                    if len(job_description.split()) > 50:  # Heuristic: only keep if reasonably long
                        break
    except Exception as e:
        print(f"Error scraping generic site: {e}")
        
    return job_description
 
