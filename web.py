import os
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time

class WebsiteDownloader:
    def __init__(self):
        self.visited_urls = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def create_folder(self, folder_name):
        """Create download folder if it doesn't exist"""
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        return folder_name
    
    def get_valid_filename(self, url):
        """Convert URL to valid filename"""
        parsed = urlparse(url)
        path = parsed.path
        
        if not path or path == '/':
            return 'index.html'
        
        # Remove leading slash and replace other slashes with underscores
        filename = path.lstrip('/').replace('/', '_')
        
        # If no extension, add .html
        if '.' not in filename:
            filename += '.html'
            
        return filename
    
    def download_file(self, url, folder_name):
        """Download individual file"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            filename = self.get_valid_filename(url)
            filepath = os.path.join(folder_name, filename)
            
            # Handle duplicate filenames
            counter = 1
            original_filepath = filepath
            while os.path.exists(filepath):
                name, ext = os.path.splitext(original_filepath)
                filepath = f"{name}_{counter}{ext}"
                counter += 1
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"✓ Downloaded: {filename}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to download {url}: {str(e)}")
            return False
    
    def extract_links(self, html_content, base_url):
        """Extract all relevant links from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        
        # Extract CSS links
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                links.append(urljoin(base_url, href))
        
        # Extract JavaScript files
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src:
                links.append(urljoin(base_url, src))
        
        # Extract PHP and HTML links
        for a in soup.find_all('a', href=True):
            href = a.get('href')
            if href and (href.endswith('.php') or href.endswith('.html') or href.endswith('.htm')):
                links.append(urljoin(base_url, href))
        
        # Extract images that might be in CSS
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            if src:
                links.append(urljoin(base_url, src))
        
        return list(set(links))  # Remove duplicates
    
    def download_website(self, url, folder_name):
        """Main function to download entire website"""
        print(f"🚀 Starting download from: {url}")
        print(f"📁 Saving to folder: {folder_name}")
        
        # Create download folder
        download_folder = self.create_folder(folder_name)
        
        # Download main page first
        print(f"\n📄 Downloading main page...")
        self.download_file(url, download_folder)
        
        # Get main page content to extract links
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # Extract all linked resources
            print(f"\n🔍 Extracting linked resources...")
            all_links = self.extract_links(response.content, url)
            
            print(f"📊 Found {len(all_links)} resources to download")
            
            # Download all linked resources
            successful_downloads = 0
            for link in all_links:
                if link not in self.visited_urls:
                    self.visited_urls.add(link)
                    if self.download_file(link, download_folder):
                        successful_downloads += 1
                    time.sleep(0.5)  # Be polite to the server
            
            print(f"\n✅ Download completed!")
            print(f"📊 Successfully downloaded: {successful_downloads + 1} files")
            print(f"💾 Location: {os.path.abspath(download_folder)}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def main():
    print("🌐 Website Downloader")
    print("=" * 50)
    
    # Get user input
    website_url = input("Enter website URL: ").strip()
    folder_name = input("Enter folder name to save files: ").strip()
    
    # Add http:// if missing
    if not website_url.startswith(('http://', 'https://')):
        website_url = 'https://' + website_url
    
    # Validate folder name
    if not folder_name:
        folder_name = "downloaded_website"
    
    # Create downloader and start
    downloader = WebsiteDownloader()
    downloader.download_website(website_url, folder_name)

if __name__ == "__main__":
    main()
