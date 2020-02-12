from threading import Thread
from urllib.parse import urlparse
from utils.download import download
from utils import get_logger
from scraper import scraper
from urllib.robotparser import RobotFileParser
import time


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.robots = {}
        super().__init__(daemon=True)

    # def read_robot(self, text_file, content_type):


    def add_robot(self, base_url):

        resp = download(base_url,self.config, self.logger)

        if resp.raw_response is not None:
            robot_list = resp.raw_response.content.decode().split("\n")

        # Adds the robots.txt in a global dictionary, returning the read robot.txt
        if base_url not in self.robots:
            robots_file = RobotFileParser()
            if resp.raw_response is not None and resp.status != 404:
                robots_file.parse(robot_list)
            self.robots[base_url] = robots_file
            
        return self.robots[base_url]
        
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            print(tbd_url)
            if tbd_url in ['https://www.ics.uci.edu','https://www.cs.uci.edu','https://www.informatics.uci.edu','https://www.stat.uci.edu','https://today.uci.edu/department/information_computer_sciences']:
                print('sup')
                with open('Error_file.txt', 'a+') as f:
                    f.write('\n\n\n\n\n\n' + 'SEED_URL : ' + str(tbd_url) + '\n')
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            try:
                parsed = urlparse(tbd_url)
                base_url = parsed.scheme + '://' + parsed.netloc + '/robots.txt'
                print('BASE_URL', base_url)
                robot_parser = self.add_robot(base_url)
                if robot_parser.default_entry is None or (robot_parser.default_entry is not None and robot_parser.can_fetch('*', tbd_url)):
                    resp = download(tbd_url, self.config, self.logger)
                    self.logger.info(
                        f"Downloaded {tbd_url}, status <{resp.status}>, "
                        f"using cache {self.config.cache_server}.")
                    scraped_urls = scraper(tbd_url, resp)
                    for scraped_url in scraped_urls:
                        self.frontier.add_url(scraped_url)
                    self.frontier.mark_url_complete(tbd_url)
                    crawl_delay = None
                    if robot_parser.default_entry is not None:
                        crawl_delay = robot_parser.crawl_delay('*')
                    if crawl_delay is not None:
                        time.sleep(crawl_delay)
                    time.sleep(self.config.time_delay)
            except Exception as e:
                print('ERROR OCCURED')
                with open('Error_file.txt', 'a+') as f:
                    f.write(str(type(e)) + ' ' + str(e) + ' ' + tbd_url + '\n')
