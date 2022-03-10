import multiprocessing
from bs4 import BeautifulSoup
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse
import requests
import time
  
    
class Crawler:
    #constructor to intialize the variables
    def __init__(self, intial_url):
        self.intial_url = intial_url
        self.root_url = '{}://{}'.format(urlparse(self.intial_url).scheme,
                                         urlparse(self.intial_url).netloc)
        self.pool = ThreadPoolExecutor(max_workers = 5 )
        self.scrap_page = set([])
        self.crawl_list= Queue()
        self.crawl_list.put(self.intial_url)
    
    #To parse the link , append it to the queue and print the webpages found within each page.
    def parse_links(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        A_Tags = soup.find_all('a', href=True)
        for link in A_Tags:
            url = link['href']
            if url.startswith('/') or url.startswith(self.root_url):
                url = urljoin(self.root_url, url)
                if url not in self.scrap_page:
                    self.crawl_list.put(url)
                    print("  "+ url)

    #To execute valid url and add threadpool             
    def scrape_callback(self, res):
        result = res.result()
        if result and result.status_code == 200:
            self.parse_links(result.text)
            
    #To check if the url is valid  
    def check_page(self, url):
        try:
            res = requests.get(url)
            return res
        except requests.RequestException:
            return

    #To create thread,scrap webpages and call callback fn
    def run_crawler(self):
        while True:
            try:
                target_url = self.crawl_list.get(timeout=60)
                if target_url not in self.scrap_page: 
                    print("{}".format(target_url))
                    self.current_url = "{}".format(target_url)
                    self.scrap_page.add(target_url)
                    job = self.pool.submit(self.check_page, target_url)
                    job.add_done_callback(self.scrape_callback)
                time.sleep(1.5)
            except Empty:
                return
            except Exception as e:
                print(e)
                continue

  
  
if __name__ == '__main__':
  
    url = input("Enter the url").strip()
    cc = Crawler(url)
    cc.run_crawler()
  