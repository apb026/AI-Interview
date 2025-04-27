import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import logging
from typing import Dict, Optional, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScraper:
    """A class to scrape job descriptions from various job posting websites."""
    
    def __init__(self, headers: Optional[Dict[str, str]] = None):
        """Initialize the WebScraper with optional headers for requests.
        
        Args:
            headers: Custom headers for HTTP requests
        """
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Supported job sites and their specific scraping methods
        self.site_handlers = {
            'linkedin.com': self._scrape_linkedin,
            'indeed.com': self._scrape_indeed,
            'glassdoor.com': self._scrape_glassdoor,
            'monster.com': self._scrape_monster,
        }
    
    def scrape_job_description(self, url: str) -> Dict[str, str]:
        """Scrape job description from the provided URL.
        
        Args:
            url: URL of the job posting
        
        Returns:
            Dictionary containing job details including title, company, location, and description
        """
        try:
            domain = urlparse(url).netloc
            base_domain = '.'.join(domain.split('.')[-2:])
            
            # Check if we have a specific handler for this site
            for site, handler in self.site_handlers.items():
                if site in domain:
                    return handler(url)
            
            # If no specific handler, use generic scraper
            return self._generic_scraper(url)
            
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {str(e)}")
            return {
                "title": "",
                "company": "",
                "location": "",
                "description": f"Failed to scrape job description: {str(e)}",
                "error": True
            }
    
    def _generic_scraper(self, url: str) -> Dict[str, str]:
        """Generic scraper for websites without specific handlers.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary with job details
        """
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to extract job information using common patterns
        title = soup.find('h1')
        title = title.text.strip() if title else "Unknown Title"
        
        # Look for company name in meta tags or common elements
        company = ""
        company_elements = soup.select('meta[property="og:site_name"], .company-name, .employer, [itemprop="hiringOrganization"]')
        if company_elements:
            company = company_elements[0].get('content', '') or company_elements[0].text.strip()
        
        # Extract job description from the main content
        description = ""
        main_content = soup.select('main, article, .job-description, [itemprop="description"]')
        if main_content:
            description = main_content[0].get_text(separator='\n').strip()
        else:
            # Fallback: get the main body text
            body = soup.find('body')
            if body:
                # Remove script and style elements
                for script in body(["script", "style", "nav", "header", "footer"]):
                    script.extract()
                description = body.get_text(separator='\n').strip()
        
        return {
            "title": title,
            "company": company,
            "location": "Unknown",
            "description": description,
            "url": url,
            "source": "generic"
        }
    
    def _scrape_linkedin(self, url: str) -> Dict[str, str]:
        """Scrape job description from LinkedIn.
        
        Args:
            url: LinkedIn job posting URL
            
        Returns:
            Dictionary with job details
        """
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.select_one('.top-card-layout__title')
        title = title.text.strip() if title else "Unknown Title"
        
        company = soup.select_one('.top-card-layout__company-name')
        company = company.text.strip() if company else "Unknown Company"
        
        location = soup.select_one('.top-card-layout__footer-item')
        location = location.text.strip() if location else "Unknown Location"
        
        description = soup.select_one('.description__text')
        description = description.get_text(separator='\n').strip() if description else ""
        
        return {
            "title": title,
            "company": company,
            "location": location,
            "description": description,
            "url": url,
            "source": "linkedin"
        }
    
    def _scrape_indeed(self, url: str) -> Dict[str, str]:
        """Scrape job description from Indeed.
        
        Args:
            url: Indeed job posting URL
            
        Returns:
            Dictionary with job details
        """
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.select_one('.jobsearch-JobInfoHeader-title')
        title = title.text.strip() if title else "Unknown Title"
        
        company = soup.select_one('.jobsearch-InlineCompanyRating-companyHeader')
        company = company.text.strip() if company else "Unknown Company"
        
        location = soup.select_one('.jobsearch-JobInfoHeader-subtitle .jobsearch-JobInfoHeader-subitem')
        location = location.text.strip() if location else "Unknown Location"
        
        description = soup.select_one('#jobDescriptionText')
        description = description.get_text(separator='\n').strip() if description else ""
        
        return {
            "title": title,
            "company": company,
            "location": location,
            "description": description,
            "url": url,
            "source": "indeed"
        }
    
    def _scrape_glassdoor(self, url: str) -> Dict[str, str]:
        """Scrape job description from Glassdoor.
        
        Args:
            url: Glassdoor job posting URL
            
        Returns:
            Dictionary with job details
        """
        # Glassdoor requires additional handling due to anti-scraping measures
        # This is a simplified implementation
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.select_one('.job-title')
        title = title.text.strip() if title else "Unknown Title"
        
        company = soup.select_one('.employer-name')
        company = company.text.strip() if company else "Unknown Company"
        
        location = soup.select_one('.location')
        location = location.text.strip() if location else "Unknown Location"
        
        description = soup.select_one('.jobDescriptionContent')
        description = description.get_text(separator='\n').strip() if description else ""
        
        return {
            "title": title,
            "company": company,
            "location": location,
            "description": description,
            "url": url,
            "source": "glassdoor"
        }
    
    def _scrape_monster(self, url: str) -> Dict[str, str]:
        """Scrape job description from Monster.
        
        Args:
            url: Monster job posting URL
            
        Returns:
            Dictionary with job details
        """
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.select_one('.job-title')
        title = title.text.strip() if title else "Unknown Title"
        
        company = soup.select_one('.company-name')
        company = company.text.strip() if company else "Unknown Company"
        
        location = soup.select_one('.location')
        location = location.text.strip() if location else "Unknown Location"
        
        description = soup.select_one('#jobDescription')
        description = description.get_text(separator='\n').strip() if description else ""
        
        return {
            "title": title,
            "company": company,
            "location": location,
            "description": description,
            "url": url,
            "source": "monster"
        }
    
    def extract_skills_from_jd(self, jd_text: str) -> List[str]:
        """Extract key skills from job description text using regex patterns.
        
        Args:
            jd_text: Job description text
            
        Returns:
            List of identified skills
        """
        # Common skill-related phrases in job descriptions
        skill_patterns = [
            r'proficient in ([\w\s,]+)',
            r'experience with ([\w\s,]+)',
            r'knowledge of ([\w\s,]+)',
            r'familiarity with ([\w\s,]+)',
            r'skills:([\w\s,]+)',
            r'requirements:([\w\s,]+)',
            r'qualifications:([\w\s,]+)'
        ]
        
        # Common technical skills to look for directly
        tech_skills = [
            'Python', 'Java', 'JavaScript', 'C\+\+', 'SQL', 'React', 'Node\.js', 'AWS',
            'Docker', 'Kubernetes', 'Machine Learning', 'AI', 'Data Analysis',
            'Project Management', 'Agile', 'Scrum', 'Leadership'
        ]
        
        skills = set()
        
        # Extract skills from patterns
        for pattern in skill_patterns:
            matches = re.finditer(pattern, jd_text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) > 0:
                    # Split by common separators and clean up
                    for skill in re.split(r'[,;]', match.group(1)):
                        if skill.strip() and len(skill.strip()) > 2:
                            skills.add(skill.strip())
        
        # Look for direct mentions of technical skills
        for skill in tech_skills:
            if re.search(r'\b' + skill + r'\b', jd_text, re.IGNORECASE):
                skills.add(skill)
        
        return list(skills)