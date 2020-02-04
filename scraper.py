import re
from urllib.parse import urlparse
from lxml import etree, html
from io import *

def scraper(url, resp):
    links = extract_next_links(url, resp)
    # print([link for link in links if is_valid(link)])
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation requred.
    # print(type(resp))
    # if resp.raw_response == None:
    #     print(type(resp.status))
    #     print(url)
    final = []
    # if re.match(r".*\.php.*", url):
    #     return []
    if 200 == resp.status:
        print(url)
        html = resp.raw_response.content.decode('utf-8')
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(html), parser)
        root = tree.getroot()
        for i in root.xpath('/html')[0].getiterator('a'):
            # if 'href' in i.attrib:
            #     count += 1
            #     print(i.attrib['href'])
            #     print()
            url_dict = i.attrib
            if 'href' in url_dict:
                print(url_dict)
                curr_url = url_dict['href']
                print(curr_url)
                if len(curr_url) >= 2 and curr_url[0] == '/' and curr_url[1] != '/':
                    # print(url+curr_url)
                    if not re.match(r".*\.php.*", url):
                        final.append(url + curr_url)
                elif curr_url[0] != '/' and curr_url[0] != '#':
                    # print(curr_url)
                    final.append(curr_url)
        # print()
        # print('-------------------------------------------------------------------------------------------------------------------------------------------')
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