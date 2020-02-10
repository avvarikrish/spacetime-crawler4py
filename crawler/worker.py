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

    def add_robot(self, base_url):

        # Adds the robots.txt in a global dictionary, returning the read robot.txt
        if base_url not in self.robots:
            robots_file = RobotFileParser()
            robots_file.set_url(base_url)
            robots_file.read()
            self.robots[base_url] = robots_file

        return self.robots[base_url]
        
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            try:
                parsed = urlparse(tbd_url)
                base_url = parsed.scheme + '://' + parsed.netloc + '/robots.txt'
                robot_parser = self.add_robot(base_url)
                if robot_parser.can_fetch('*', tbd_url):
                    resp = download(tbd_url, self.config, self.logger)
                    self.logger.info(
                        f"Downloaded {tbd_url}, status <{resp.status}>, "
                        f"using cache {self.config.cache_server}.")
                    scraped_urls = scraper(tbd_url, resp)
                    for scraped_url in scraped_urls:
                        self.frontier.add_url(scraped_url)
                    self.frontier.mark_url_complete(tbd_url)
                    time.sleep(self.config.time_delay)
            except Exception as e:
                print('ERROR OCCURED')
                with open('Error_file.txt', 'a+') as f:
                    f.write(str(type(e)) + ' ' + str(e) + ' ' + tbd_url + '\n')
