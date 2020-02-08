import re
from urllib.parse import urlparse
from lxml import etree
from io import *

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation requred.
    final = []
    parsed = urlparse(url)
    if 200 <= resp.status <= 599:
        html = resp.raw_response.content.decode('utf-8')
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(html), parser)
        root = tree.getroot()
        for i in root.xpath('/html')[0].getiterator('a'):
            url_dict = i.attrib
            if 'href' in url_dict:
                curr_url = url_dict['href']
                final_url = ''
                if len(curr_url) >= 2 and curr_url[0] == '/' and curr_url[1] != '/':
                    final_url = parsed.scheme + '://' + parsed.netloc + curr_url
                elif curr_url[0] != '/' and curr_url[0] != '#':
                    final_url = curr_url
                if urlparse(final_url).fragment != '':
                    final.append(final_url.split('#')[0])
                else:
                    final.append(final_url)
    print(final)
    return final


def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        match_domains = re.match(
            r".*\.(ics|cs|informatics|stat)\.uci\.edu\/.*|today\.uci\.edu\/department\/information_computer_sciences\/.*$",
            url
        )
        # print(url, parsed.path)
        return match_domains and not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())
    except TypeError:
        print ("TypeError for ", parsed)
        raise