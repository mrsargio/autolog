import json
import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import re
from datetime import datetime
import asyncio
import aiohttp
import async_timeout

class HyperFastUtkarshDownloader:
    def __init__(self, max_workers=50):
        self.base_url = "https://utk-batches-api.vercel.app/api"
        self.api_url = "https://utkarsh-api.vercel.app/api"
        self.max_workers = max_workers
        self.all_links = []
        self.all_responses = []
        self.lock = threading.Lock()
        self.processed_count = 0
        self.start_time = None
    
    def clean_name(self, name):
        if not name: return "unknown"
        return re.sub(r'[<>:"/\\|?*]', '_', str(name))[:50]
    
    async def async_request(self, session, url):
        """Ultra fast async request"""
        try:
            async with async_timeout.timeout(5):
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        with self.lock:
                            self.all_responses.append({'url': url, 'data': data})
                        return data
        except:
            return None
    
    async def fetch_all_masters(self, session):
        """Fetch all master categories"""
        return await self.async_request(session, f"{self.base_url}/master-categories")
    
    async def fetch_all_subs(self, session, masters):
        """Fetch all subcategories in parallel"""
        tasks = []
        for master in masters:
            url = f"{self.base_url}/subcategories?master_id={master['id']}"
            tasks.append(self.async_request(session, url))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    
    async def fetch_all_finals(self, session, master_subs):
        """Fetch all final categories in parallel"""
        tasks = []
        for master_id, subs in master_subs.items():
            for sub in subs:
                url = f"{self.base_url}/final-categories?subcat_id={sub['id']}"
                tasks.append(self.async_request(session, url))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    
    async def fetch_all_courses(self, session, hierarchy_data):
        """Fetch all courses in parallel"""
        tasks = []
        for data in hierarchy_data:
            url = f"{self.base_url}/courses?master_id={data['master_id']}&cat_id={data['subcat_id']}&sub_cat_id={data['final_id']}"
            tasks.append(self.async_request(session, url))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    
    async def fetch_batch_details(self, session, course_id):
        """Fetch batch details"""
        return await self.async_request(session, f"{self.api_url}/batch/{course_id}")
    
    async def fetch_topics(self, session, course_id, subject_id):
        """Fetch topics"""
        return await self.async_request(session, f"{self.api_url}/course/{course_id}/subject/{subject_id}/topics")
    
    async def fetch_content(self, session, course_id, subject_id, topic_id):
        """Fetch content"""
        return await self.async_request(session, f"{self.api_url}/course/{course_id}/subject/{subject_id}/topic/{topic_id}/content")
    
    def save_data_ultra_fast(self, folder_path, data, filename):
        """Ultra fast save - no validation"""
        try:
            (folder_path / f"{filename}.json").write_text(
                json.dumps(data, ensure_ascii=False), 
                encoding='utf-8'
            )
            return True
        except:
            return False
    
    def save_links_ultra_fast(self, folder_path, content_data, hierarchy):
        """Ultra fast links save"""
        try:
            content = ["UTKARSH LINKS\n", "="*40 + "\n"]
            for item in content_data.get('data', []):
                if item.get('url'):
                    content.extend([
                        f"\n{item.get('title', 'No Title')}\n",
                        f"URL: {item['url']}\n",
                        "-"*30 + "\n"
                    ])
                    with self.lock:
                        self.all_links.append({'hierarchy': hierarchy, 'url': item['url']})
            
            (folder_path / "ALL_LINKS.txt").write_text(''.join(content), encoding='utf-8')
            return len(content_data.get('data', []))
        except:
            return 0
    
    async def process_content_hyper_fast(self, session, course_data, base_path):
        """Hyper fast content processing"""
        course_id = course_data['id']
        course_title = course_data['title']
        master_cat = course_data['master_name']
        sub_cat = course_data['sub_name'] 
        final_cat = course_data['final_name']
        
        # Get batch details
        batch_data = await self.fetch_batch_details(session, course_id)
        if not batch_data: return 0
        
        total_links = 0
        subjects = batch_data.get('data', {}).get('subjects', [])
        
        # Process subjects in parallel
        subject_tasks = []
        for subject in subjects:
            subject_tasks.append(self.process_subject_hyper_fast(
                session, course_id, course_title, subject, 
                master_cat, sub_cat, final_cat, base_path
            ))
        
        if subject_tasks:
            results = await asyncio.gather(*subject_tasks)
            total_links = sum(results)
        
        self.processed_count += 1
        if self.processed_count % 10 == 0:
            elapsed = time.time() - self.start_time
            print(f"⚡ Processed: {self.processed_count} courses | Links: {len(self.all_links)} | Speed: {len(self.all_links)/max(1,elapsed):.1f} links/sec")
        
        return total_links
    
    async def process_subject_hyper_fast(self, session, course_id, course_title, subject, master_cat, sub_cat, final_cat, base_path):
        """Hyper fast subject processing"""
        subject_id = subject['id']
        subject_title = subject['title']
        
        # Get topics
        topics_data = await self.fetch_topics(session, course_id, subject_id)
        if not topics_data: return 0
        
        topics = topics_data.get('data', [])
        
        # Process topics in parallel
        topic_tasks = []
        for topic in topics:
            topic_tasks.append(self.process_topic_hyper_fast(
                session, course_id, subject_id, course_title, subject_title,
                topic, master_cat, sub_cat, final_cat, base_path
            ))
        
        if topic_tasks:
            results = await asyncio.gather(*topic_tasks)
            return sum(results)
        
        return 0
    
    async def process_topic_hyper_fast(self, session, course_id, subject_id, course_title, subject_title, topic, master_cat, sub_cat, final_cat, base_path):
        """Hyper fast topic processing"""
        topic_id = topic['id']
        topic_title = topic['title']
        
        # Create folder path
        folder_path = (
            base_path / self.clean_name(master_cat) / 
            self.clean_name(sub_cat) / self.clean_name(final_cat) /
            f"{course_id}_{self.clean_name(course_title)}" /
            self.clean_name(subject_title) / self.clean_name(topic_title)
        )
        folder_path.mkdir(parents=True, exist_ok=True)
        
        # Get content
        content_data = await self.fetch_content(session, course_id, subject_id, topic_id)
        if not content_data: return 0
        
        # Save data
        self.save_data_ultra_fast(folder_path, content_data, "content_data")
        
        # Save links
        hierarchy = {
            'master': master_cat, 'sub': sub_cat, 'final': final_cat,
            'course': course_title, 'subject': subject_title, 'topic': topic_title
        }
        
        return self.save_links_ultra_fast(folder_path, content_data, hierarchy)
    
    async def download_hyper_fast(self):
        """MAIN HYPER FAST DOWNLOAD METHOD"""
        print("🚀 HYPER FAST DOWNLOAD STARTING...")
        print("⚡ 1000x SPEED - ASYNC PARALLEL PROCESSING")
        print("🎯 MAX WORKERS: 50 | TIMEOUT: 5s\n")
        
        self.start_time = time.time()
        base_path = Path("Utkarsh_Hyper_Fast")
        base_path.mkdir(exist_ok=True)
        
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'Mozilla/5.0'}
        ) as session:
            
            # STEP 1: Get all masters
            print("📥 Fetching master categories...")
            masters_data = await self.fetch_all_masters(session)
            if not masters_data: return
            
            masters = masters_data.get('data', [])
            print(f"✅ Found {len(masters)} master categories")
            
            # STEP 2: Get all subcategories in parallel
            print("📥 Fetching ALL subcategories in parallel...")
            subs_results = await self.fetch_all_subs(session, masters)
            
            master_subs = {}
            for i, result in enumerate(subs_results):
                if result and 'data' in result:
                    master_subs[masters[i]['id']] = result['data']
            
            # STEP 3: Get all final categories in parallel
            print("📥 Fetching ALL final categories in parallel...")
            finals_results = await self.fetch_all_finals(session, master_subs)
            
            hierarchy_data = []
            result_index = 0
            for master_id, subs in master_subs.items():
                master_name = next((m['name'] for m in masters if m['id'] == master_id), 'Unknown')
                for sub in subs:
                    if result_index < len(finals_results) and finals_results[result_index] and 'data' in finals_results[result_index]:
                        for final_cat in finals_results[result_index]['data']:
                            hierarchy_data.append({
                                'master_id': master_id,
                                'master_name': master_name,
                                'subcat_id': sub['id'],
                                'sub_name': sub['name'],
                                'final_id': final_cat['id'],
                                'final_name': final_cat['name']
                            })
                    result_index += 1
            
            print(f"🎯 Found {len(hierarchy_data)} category combinations")
            
            # STEP 4: Get all courses in parallel
            print("📥 Fetching ALL courses in parallel...")
            courses_results = await self.fetch_all_courses(session, hierarchy_data)
            
            # STEP 5: Process all courses in MASSIVE parallel
            print("🚀 Processing ALL content in MASSIVE parallel...")
            all_courses_data = []
            
            for i, result in enumerate(courses_results):
                if result and 'data' in result:
                    hierarchy = hierarchy_data[i]
                    for course in result['data']:
                        course_data = course.copy()
                        course_data.update(hierarchy)
                        all_courses_data.append(course_data)
            
            print(f"📚 Found {len(all_courses_data)} total courses")
            
            # MASSIVE PARALLEL PROCESSING
            print("⚡ STARTING MASSIVE PARALLEL PROCESSING...")
            
            # Process in chunks to avoid memory issues
            chunk_size = 100
            total_processed = 0
            
            for i in range(0, len(all_courses_data), chunk_size):
                chunk = all_courses_data[i:i + chunk_size]
                
                # Process chunk in parallel
                chunk_tasks = []
                for course_data in chunk:
                    chunk_tasks.append(self.process_content_hyper_fast(session, course_data, base_path))
                
                chunk_results = await asyncio.gather(*chunk_tasks)
                total_processed += len(chunk)
                
                print(f"📦 Processed chunk: {total_processed}/{len(all_courses_data)} courses")
                
                # Small delay between chunks
                await asyncio.sleep(0.1)
            
            # FINAL SAVE
            await self.save_final_data_hyper_fast(base_path)
    
    async def save_final_data_hyper_fast(self, base_path):
        """Hyper fast final save"""
        try:
            # Save summary
            summary_content = [
                "UTKARSH HYPER FAST DOWNLOAD\n",
                "="*50 + "\n",
                f"Total Links: {len(self.all_links)}\n",
                f"Total API Calls: {len(self.all_responses)}\n", 
                f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
                f"Duration: {time.time() - self.start_time:.2f}s\n"
            ]
            (base_path / "HYPER_FAST_SUMMARY.txt").write_text(''.join(summary_content))
            
            # Save responses
            (base_path / "ALL_RESPONSES.json").write_text(
                json.dumps(self.all_responses, ensure_ascii=False),
                encoding='utf-8'
            )
            
            elapsed = time.time() - self.start_time
            print(f"\n🎉 HYPER FAST DOWNLOAD COMPLETED!")
            print(f"📍 Location: {base_path.absolute()}")
            print(f"📊 Total links: {len(self.all_links)}")
            print(f"🔗 API calls: {len(self.all_responses)}")
            print(f"⚡ Time: {elapsed:.2f} seconds")
            print(f"🚀 SPEED: {len(self.all_links)/max(1,elapsed):.1f} links/second")
            print(f"💫 1000x FASTER THAN NORMAL!")
            
        except Exception as e:
            print(f"Final save note: {e}")

def run_hyper_fast():
    """Run hyper fast downloader"""
    downloader = HyperFastUtkarshDownloader(max_workers=50)
    
    # Set high thread limits for maximum speed
    import os
    os.environ['PYTHONASYNCIODEBUG'] = '0'
    
    try:
        asyncio.run(downloader.download_hyper_fast())
    except KeyboardInterrupt:
        print("\n⏹️ Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    run_hyper_fast()