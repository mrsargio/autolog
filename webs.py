import requests
import os
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import concurrent.futures
import re
import json

class UltimateWebsiteDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.downloaded_files = set()
        self.folder_name = ""
        self.base_url = ""
        self.domain = ""
        self.visited_urls = set()
    
    def get_user_input(self):
        """यूजर से URL और फोल्डर नाम लें"""
        print("🌐 अल्टीमेट वेबसाइट डाउनलोडर")
        print("=" * 50)
        print("किसी भी वेबसाइट की सभी फाइल्स डाउनलोड करें")
        print("=" * 50)
        
        website_url = input("वेबसाइट का पूरा URL डालें: ").strip()
        if not website_url:
            print("❌ URL जरूरी है!")
            return None, None
        
        if not website_url.startswith(('http://', 'https://')):
            website_url = 'https://' + website_url
        
        folder_name = input("सेव करने के लिए फोल्डर नाम डालें: ").strip()
        if not folder_name:
            folder_name = urlparse(website_url).netloc.replace('www.', '') + "_website"
        
        return website_url, folder_name
    
    def download_complete_website(self, website_url, folder_name):
        """पूरी वेबसाइट डाउनलोड करें"""
        self.base_url = website_url
        self.domain = urlparse(website_url).netloc
        self.folder_name = folder_name
        
        print(f"\n🚀 डाउनलोड शुरू: {website_url}")
        print(f"📁 फोल्डर: {folder_name}")
        print("=" * 60)
        
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        
        # स्टेप 1: मुख्य पेज डाउनलोड करें और सभी लिंक्स ढूंढें
        print("📄 मुख्य पेज डाउनलोड कर रहा हूँ...")
        all_urls = self.recursive_crawl(website_url, max_depth=3)
        
        # स्टेप 2: सभी फाइल्स डाउनलोड करें
        self.download_all_resources(all_urls)
        
        print(f"\n✅ डाउनलोड पूरा! कुल {len(self.downloaded_files)} फाइल्स")
        self.show_report()
    
    def recursive_crawl(self, start_url, max_depth=3):
        """Recursive तरीके से पूरी वेबसाइट क्रॉल करें"""
        print(f"🕸️ Recursive crawling शुरू (max depth: {max_depth})...")
        
        all_urls = set()
        to_crawl = [(start_url, 0)]  # (url, depth)
        
        while to_crawl:
            current_url, depth = to_crawl.pop(0)
            
            if current_url in self.visited_urls or depth > max_depth:
                continue
                
            self.visited_urls.add(current_url)
            print(f"   🔍 Depth {depth}: {self.get_display_url(current_url)}")
            
            try:
                # URL डाउनलोड करें
                response = self.session.get(current_url, timeout=15)
                if response.status_code == 200:
                    # फाइल सेव करें
                    self.save_file(current_url, response.content, response.headers.get('content-type', ''))
                    
                    # HTML पेज है तो लिंक्स निकालें
                    if 'text/html' in response.headers.get('content-type', ''):
                        new_urls = self.extract_all_links_from_content(response.text, current_url)
                        
                        # नए URLs जोड़ें
                        for url in new_urls:
                            if url not in self.visited_urls and url not in [u for u, d in to_crawl]:
                                if self.should_crawl(url, depth):
                                    to_crawl.append((url, depth + 1))
                                all_urls.add(url)
                    
                    all_urls.add(current_url)
                    
            except Exception as e:
                print(f"   ❌ क्रॉल त्रुटि: {e}")
            
            time.sleep(0.3)  # सर्वर को ओवरलोड न करें
        
        print(f"   📊 कुल {len(all_urls)} URLs मिले")
        return all_urls
    
    def extract_all_links_from_content(self, content, base_url):
        """कंटेंट से सभी लिंक्स निकालें (HTML + JavaScript)"""
        urls = set()
        
        # HTML लिंक्स
        soup = BeautifulSoup(content, 'html.parser')
        
        # सभी HTML टैग्स
        html_tags = [
            ('a', 'href'),
            ('link', 'href'),
            ('script', 'src'),
            ('img', 'src'),
            ('source', 'src'),
            ('audio', 'src'),
            ('video', 'src'),
            ('iframe', 'src'),
            ('form', 'action'),
            ('meta', 'content')
        ]
        
        for tag_name, attr in html_tags:
            for tag in soup.find_all(tag_name, {attr: True}):
                url = tag.get(attr)
                if url:
                    full_url = self.normalize_url(url, base_url)
                    if self.is_same_domain(full_url):
                        urls.add(full_url)
        
        # CSS में URLs
        css_urls = re.findall(r'url\([\'"]?([^\'")]+)[\'"]?\)', content)
        for css_url in css_urls:
            full_url = self.normalize_url(css_url, base_url)
            if self.is_same_domain(full_url):
                urls.add(full_url)
        
        # JavaScript में URLs - एडवांस्ड डिटेक्शन
        js_urls = self.extract_urls_from_javascript(content, base_url)
        urls.update(js_urls)
        
        return list(urls)
    
    def extract_urls_from_javascript(self, content, base_url):
        """JavaScript कोड से URLs निकालें"""
        urls = set()
        
        # fetch() और XMLHttpRequest calls
        fetch_patterns = [
            r'fetch\([\'"]([^\'"]+)[\'"]\)',
            r'\.open\([\'"]GET[\'"],\s*[\'"]([^\'"]+)[\'"]\)',
            r'\.open\([\'"]POST[\'"],\s*[\'"]([^\'"]+)[\'"]\)',
            r'axios\.(?:get|post)\([\'"]([^\'"]+)[\'"]\)',
            r'\.get\([\'"]([^\'"]+)[\'"]\)',
            r'\.post\([\'"]([^\'"]+)[\'"]\)',
        ]
        
        for pattern in fetch_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                full_url = self.normalize_url(match, base_url)
                if self.is_same_domain(full_url):
                    urls.add(full_url)
        
        # URL strings in JavaScript
        url_patterns = [
            r'[\'\"](/[^\'\"\s]+\.(?:html|css|js|json|txt|xml))[\'\"]',
            r'[\'\"](\./[^\'\"\s]+\.(?:html|css|js|json|txt|xml))[\'\"]',
            r'[\'\"](\.\.[^\'\"\s]+\.(?:html|css|js|json|txt|xml))[\'\"]',
            r'[\'\"]([^\'\"\s]+/[\w\-]+\.(?:html|css|js|json|txt|xml))[\'\"]',
        ]
        
        for pattern in url_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                full_url = self.normalize_url(match, base_url)
                if self.is_same_domain(full_url):
                    urls.add(full_url)
        
        # JSON data में URLs
        json_patterns = [
            r'[\'"]url[\'"]\s*:\s*[\'"]([^\'"]+)[\'"]',
            r'[\'"]src[\'"]\s*:\s*[\'"]([^\'"]+)[\'"]',
            r'[\'"]href[\'"]\s*:\s*[\'"]([^\'"]+)[\'"]',
            r'[\'"]file[\'"]\s*:\s*[\'"]([^\'"]+)[\'"]',
            r'[\'"]path[\'"]\s*:\s*[\'"]([^\'"]+)[\'"]',
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                full_url = self.normalize_url(match, base_url)
                if self.is_same_domain(full_url):
                    urls.add(full_url)
        
        # Array में URLs (जैसे batch files)
        array_patterns = [
            r'=\s*\[(.*?)\]',
            r'const\s+\w+\s*=\s*\[(.*?)\]',
            r'let\s+\w+\s*=\s*\[(.*?)\]',
            r'var\s+\w+\s*=\s*\[(.*?)\]',
        ]
        
        for pattern in array_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                # Array items निकालें
                items = re.findall(r'[\'"]([^\'"]+)[\'"]', match)
                for item in items:
                    if any(ext in item for ext in ['.html', '.css', '.js', '.txt', '.json', '.xml']):
                        full_url = self.normalize_url(item, base_url)
                        if self.is_same_domain(full_url):
                            urls.add(full_url)
        
        return list(urls)
    
    def should_crawl(self, url, depth):
        """चेक करें कि URL को क्रॉल करना चाहिए"""
        # सिर्फ same domain
        if not self.is_same_domain(url):
            return False
        
        # सिर्फ HTML पेजेस को क्रॉल करें (और कुछ specific फाइल टाइप्स)
        if url.endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', 
                        '.pdf', '.zip', '.mp4', '.mp3', '.woff', '.woff2', '.ttf')):
            return False
        
        # पैरामीटर्स वाले URLs को सीमित करें
        if '?' in url and depth > 1:
            return False
        
        return True
    
    def should_download(self, url):
        """चेक करें कि फाइल डाउनलोड करनी चाहिए"""
        # सिर्फ same domain की फाइल्स
        if not self.is_same_domain(url):
            return False
        
        # बहुत बड़ी फाइल्स को स्किप करें
        if any(ext in url.lower() for ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']):
            return False
        
        return True
    
    def download_all_resources(self, urls):
        """सभी रिसोर्सेज डाउनलोड करें"""
        # फिल्टर URLs
        download_urls = [url for url in urls if self.should_download(url) and url not in self.downloaded_files]
        
        if not download_urls:
            print("ℹ️ डाउनलोड के लिए कोई नई फाइल्स नहीं मिलीं")
            return
        
        print(f"\n📥 {len(download_urls)} फाइल्स डाउनलोड कर रहा हूँ...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = []
            for url in download_urls:
                future = executor.submit(self.download_single_file, url)
                futures.append(future)
            
            completed = 0
            total = len(futures)
            
            for future in concurrent.futures.as_completed(futures):
                completed += 1
                if completed % 10 == 0 or completed == total:
                    print(f"   📊 {completed}/{total} डाउनलोड हो चुके...")
    
    def download_single_file(self, url):
        """सिंगल फाइल डाउनलोड करें"""
        try:
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                self.save_file(url, response.content, response.headers.get('content-type', ''))
                self.downloaded_files.add(url)
            elif response.status_code == 404:
                print(f"   ❌ {self.get_filename(url)} - नहीं मिली (404)")
            else:
                print(f"   ⚠️ {self.get_filename(url)} - स्टेटस: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {self.get_filename(url)} - त्रुटि: {e}")
    
    def save_file(self, url, content, content_type=""):
        """फाइल को सेव करें"""
        try:
            file_path = self.get_local_path(url)
            
            # फोल्डर बनाएं
            file_dir = os.path.dirname(file_path)
            if file_dir and not os.path.exists(file_dir):
                os.makedirs(file_dir, exist_ok=True)
            
            # कॉन्टेंट टाइप के अनुसार सेव करें
            if isinstance(content, str):
                content = content.encode('utf-8')
            
            # टेक्स्ट फाइल्स के लिए UTF-8 encoding
            if any(ct in content_type for ct in ['text/', 'application/javascript', 'application/json']) or \
               url.endswith(('.html', '.htm', '.css', '.js', '.txt', '.json', '.xml')):
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content.decode('utf-8'))
                except:
                    with open(file_path, 'wb') as f:
                        f.write(content)
            else:
                with open(file_path, 'wb') as f:
                    f.write(content)
            
            file_size = len(content)
            display_path = os.path.relpath(file_path, self.folder_name)
            print(f"     ✅ {display_path} ({file_size} bytes)")
            
        except Exception as e:
            print(f"     ❌ सेव करने में त्रुटि: {self.get_filename(url)} - {e}")
    
    def get_local_path(self, url):
        """URL को लोकल फाइल पाथ में कन्वर्ट करें"""
        parsed = urlparse(url)
        path = parsed.path
        
        if not path or path == '/':
            return os.path.join(self.folder_name, "index.html")
        
        # रूट पाथ को साफ करें
        path = path.lstrip('/')
        
        # डायरेक्टरी के लिए index.html एड करें
        if not path or path.endswith('/'):
            path = os.path.join(path, "index.html")
        elif '.' not in os.path.basename(path):
            path += ".html"
        
        return os.path.join(self.folder_name, path)
    
    def normalize_url(self, url, base_url):
        """URL को पूरा URL में कन्वर्ट करें"""
        if url.startswith('//'):
            return 'https:' + url
        elif url.startswith('/'):
            return urljoin(self.base_url, url)
        elif url.startswith('./'):
            return urljoin(base_url, url)
        elif url.startswith('../'):
            return urljoin(base_url, url)
        elif not url.startswith('http'):
            return urljoin(base_url, url)
        else:
            return url
    
    def is_same_domain(self, url):
        """चेक करें कि URL same domain का है"""
        try:
            return urlparse(url).netloc == self.domain
        except:
            return False
    
    def get_display_url(self, url):
        """डिस्प्ले के लिए छोटा URL बनाएं"""
        return url.replace(self.base_url, '') or '/'
    
    def get_filename(self, url):
        """URL से फाइलनाम निकालें"""
        return os.path.basename(urlparse(url).path) or "index.html"
    
    def show_report(self):
        """डाउनलोड रिपोर्ट दिखाएं"""
        print("\n" + "=" * 60)
        print("📊 अल्टीमेट वेबसाइट डाउनलोड रिपोर्ट")
        print("=" * 60)
        
        if not os.path.exists(self.folder_name):
            print("❌ फोल्डर नहीं बना!")
            return
        
        file_count = 0
        total_size = 0
        file_types = {}
        
        for root, dirs, files in os.walk(self.folder_name):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower() or 'no-ext'
                file_size = os.path.getsize(file_path)
                
                file_types[file_ext] = file_types.get(file_ext, 0) + 1
                total_size += file_size
                file_count += 1
        
        print(f"🌐 वेबसाइट: {self.base_url}")
        print(f"📁 फोल्डर: {self.folder_name}")
        print(f"📄 कुल फाइल्स: {file_count}")
        print(f"💾 कुल साइज: {total_size / 1024 / 1024:.2f} MB")
        
        print("\n📋 फाइल टाइप्स:")
        for ext, count in sorted(file_types.items()):
            if count > 0:
                print(f"   {ext or 'no-ext'}: {count} फाइल्स")
        
        # मुख्य फाइल्स की लिस्ट
        main_files = []
        for root, dirs, files in os.walk(self.folder_name):
            for file in files:
                if file in ['index.html', 'main.html', 'app.html', 'home.html']:
                    main_files.append(os.path.join(root, file))
        
        if main_files:
            print(f"\n🏠 मुख्य फाइल्स:")
            for main_file in main_files:
                rel_path = os.path.relpath(main_file, self.folder_name)
                print(f"   📄 {rel_path}")
        
        print(f"\n✅ डाउनलोड पूरा हो गया!")
        print(f"📍 लोकेशन: {os.path.abspath(self.folder_name)}")
        
        # ओपन करने का सुझाव
        index_path = os.path.join(self.folder_name, "index.html")
        if os.path.exists(index_path):
            print(f"🌐 वेबसाइट देखने के लिए: file://{os.path.abspath(index_path)}")

def main():
    downloader = UltimateWebsiteDownloader()
    
    try:
        website_url, folder_name = downloader.get_user_input()
        
        if website_url and folder_name:
            print(f"\n⚡ प्रोसेस शुरू कर रहा हूँ...")
            downloader.download_complete_website(website_url, folder_name)
        else:
            print("❌ इनपुट वैध नहीं है!")
            
    except KeyboardInterrupt:
        print("\n⏹️ डाउनलोड रोक दिया गया")
    except Exception as e:
        print(f"\n❌ त्रुटि: {e}")

if __name__ == "__main__":
    # लाइब्रेरीज चेक करें
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("❌ जरूरी लाइब्रेरीज इंस्टॉल नहीं हैं!")
        print("इंस्टॉल करें: pip install requests beautifulsoup4")
        exit(1)
    
    main()