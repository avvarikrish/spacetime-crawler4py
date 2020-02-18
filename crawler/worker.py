from threading import Thread
from urllib.parse import urlparse
from utils.download import download
from utils import get_logger
from scraper import scraper, get_all_tokens, BIG_PAGE, ICS_DICT, IMPORTANT_URLS
from urllib.robotparser import RobotFileParser
import simhash
from io import *

from lxml import etree, html
import time


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.robots = {}
        self.TOTAL_URL_COUNT = 0
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
            print('TBD', tbd_url)
            # if tbd_url in ['https://www.ics.uci.edu','https://www.cs.uci.edu','https://www.informatics.uci.edu','https://www.stat.uci.edu','https://today.uci.edu/department/information_computer_sciences']:
            #     with open('Error_file.txt', 'a+') as f:
            #         f.write('\n\n\n\n\n\n' + 'SEED_URL : ' + str(tbd_url) + '\n')
            if not tbd_url:
                # print statements for report
                print('TOTAL URL:', self.TOTAL_URL_COUNT)
                print()
                print('IMPORTANT_URLS', IMPORTANT_URLS[0])
                print()
                print('BIG PAGE:', BIG_PAGE)
                print()
                print('TOKENS', sorted(get_all_tokens().items(), key=lambda x: -x[1])[0:50])
                print()
                print('ICS_DICT:', sorted(ICS_DICT.items(), key=lambda x: x[0]))
                print()
                print('LENGTH OF ICS_DICT', len(ICS_DICT))
                print()
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            try:
                # obtains url from frontier, then also adds the robots.txt of the domain.
                parsed = urlparse(tbd_url)
                base_url = parsed.scheme + '://' + parsed.netloc + '/robots.txt'

                print('BASE_URL', base_url)

                # function call that reads the robots.txt
                robot_parser = self.add_robot(base_url)

                # checks to see if the user agent is valid in the robots.txt, then downloads and scrapes
                # the url if it is allowed to
                if robot_parser.default_entry is None or (robot_parser.default_entry is not None and robot_parser.can_fetch('*', tbd_url)):

                    # downloads url
                    resp = download(tbd_url, self.config, self.logger)
                    self.logger.info(
                        f"Downloaded {tbd_url}, status <{resp.status}>, "
                        f"using cache {self.config.cache_server}.")

                    # function call to scraper that scrapes the url and obtains a list of valid links from the url
                    scraped_urls = scraper(tbd_url, resp)

                    # iterates through the list of scraped urls, and adds them to the frontier
                    for scraped_url in scraped_urls:
                        self.frontier.add_url(scraped_url)

                    # marks the url downloaded as completed, to prevent duplicates and infinite loops
                    self.frontier.mark_url_complete(tbd_url)
                    self.TOTAL_URL_COUNT += 1

                    # parses through the robots.txt to check if there is a crawl delay, and delays the crawl
                    # if there exists a delay.
                    crawl_delay = None
                    if robot_parser.default_entry is not None:
                        crawl_delay = robot_parser.crawl_delay('*')
                    if crawl_delay is not None:
                        print('crawl', crawl_delay)
                        time.sleep(crawl_delay)
                    time.sleep(self.config.time_delay)
            except Exception as e:
                print('ERROR OCCURED')
                # with open('Error_file.txt', 'a+') as f:
                #     f.write(str(type(e)) + ' ' + str(e) + ' ' + tbd_url + '\n')
