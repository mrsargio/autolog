import os
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time

class WebsiteDownloader:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited_urls = set()
        self.downloaded_files = set()
        self.domain = urlparse(base_url).netloc
        
        # Create download directory
        self.download_dir = f"downloaded_website_{self.domain}"
        os.makedirs(self.download_dir, exist_ok=True)
        
    def download_file(self, url, filepath):
        """Download a single file"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            self.downloaded_files.add(url)
            print(f"✅ Downloaded: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Error downloading {url}: {str(e)}")
            return False
    
    def extract_assets(self, soup, page_url):
        """Extract all assets from HTML"""
        assets = []
        
        # CSS files
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                assets.append(urljoin(page_url, href))
        
        # JavaScript files
        for script in soup.find_all('script', src=True):
            assets.append(urljoin(page_url, script['src']))
        
        # Images
        for img in soup.find_all('img', src=True):
            assets.append(urljoin(page_url, img['src']))
        
        # Favicon
        for link in soup.find_all('link', rel='icon'):
            href = link.get('href')
            if href:
                assets.append(urljoin(page_url, href))
        
        # Background images in CSS
        for tag in soup.find_all(style=True):
            style = tag['style']
            # Simple extraction of url() from style
            if 'url(' in style:
                start = style.find('url(') + 4
                end = style.find(')', start)
                if start != -1 and end != -1:
                    url_content = style[start:end].strip('"\'')
                    assets.append(urljoin(page_url, url_content))
        
        return assets
    
    def save_html(self, url, content, filename):
        """Save HTML content and modify links for local viewing"""
        soup = BeautifulSoup(content, 'html.parser')
        
        # Update all links to point to local files
        for tag in soup.find_all(['link', 'script', 'img'], src=True):
            if tag.get('src'):
                original_src = tag['src']
                local_path = self.get_local_path(urljoin(url, original_src))
                tag['src'] = local_path
        
        for tag in soup.find_all('link', href=True):
            if tag.get('href'):
                original_href = tag['href']
                local_path = self.get_local_path(urljoin(url, original_href))
                tag['href'] = local_path
        
        # Save modified HTML
        filepath = os.path.join(self.download_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
        print(f"💾 Saved HTML: {filepath}")
        return soup
    
    def get_local_path(self, asset_url):
        """Convert URL to local file path"""
        parsed = urlparse(asset_url)
        path = parsed.path.lstrip('/')
        
        if not path:
            path = 'index.html'
        elif '.' not in os.path.basename(path):
            path = os.path.join(path, 'index.html')
        
        return path
    
    def download_asset(self, asset_url):
        """Download a single asset"""
        if asset_url in self.downloaded_files:
            return
        
        local_path = self.get_local_path(asset_url)
        full_path = os.path.join(self.download_dir, local_path)
        
        # Create directory if needed
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        self.download_file(asset_url, full_path)
    
    def download_website(self):
        """Main function to download the entire website"""
        print(f"🚀 Starting download of: {self.base_url}")
        print(f"📁 Saving to: {self.download_dir}")
        
        try:
            # Download main page
            response = requests.get(self.base_url, timeout=10)
            response.raise_for_status()
            
            # Save main HTML
            soup = self.save_html(self.base_url, response.content, 'index.html')
            
            # Extract and download assets
            assets = self.extract_assets(soup, self.base_url)
            
            print(f"📦 Found {len(assets)} assets to download...")
            
            # Download all assets
            for asset_url in assets:
                if asset_url not in self.downloaded_files:
                    self.download_asset(asset_url)
                    time.sleep(0.5)  # Be polite to the server
            
            print(f"\n🎉 Download completed!")
            print(f"📊 Total files downloaded: {len(self.downloaded_files)}")
            print(f"💾 Location: {os.path.abspath(self.download_dir)}")
            
        except Exception as e:
            print(f"💥 Error: {str(e)}")

def main():
    print("🌐 Website Downloader")
    print("=" * 40)
    
    # Get URL from user
    url = input("Enter website URL: ").strip()
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Download website
    downloader = WebsiteDownloader(url)
    downloader.download_website()

if __name__ == "__main__":
    main()