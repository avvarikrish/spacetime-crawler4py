import re
from urllib.parse import urlparse
from lxml import etree, html
from io import *



BLACKLIST_RESP_TYPES = {'text/calendar'}


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):

    # Implementation required.
    # print(url ,' ------------------------------------------- ')
    final = []

    try:
        # separate the url into important parts for parsing
        parsed = urlparse(url)

        # finds the content type of the url
        resp_type = resp.raw_response.headers['Content-Type'].split(';')[0]
        with open('response_types.txt', 'a+') as f:
            f.write(resp_type + ' ' + url + '\n')

        # checks the resp.status and only goes through the if statement if the content type is an html
        if 200 <= resp.status <= 599 and resp_type == 'text/html':

            # gets the html root, library calls to parse through html
            html_value = resp.raw_response.content.decode('utf-8')
            parser = etree.HTMLParser()
            tree = etree.parse(StringIO(html_value), parser)
            root = tree.getroot()

            # creates a robots url for the parser
            # variables initialized for word and tag count, determining if pages are relevant or not
            tag_count = 0
            text_tag_count = 0
            word_count = 0
            for i in root.xpath('/html')[0].getiterator('*'):
                # print(i.tag)
                if i.tag in {'a', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'b', 'br'}:
                    text_tag_count += 1
                    if i.text is not None:
                        word_count += len(i.text.split())
                tag_count += 1

            print(word_count)
            print(text_tag_count/tag_count)

            # checks to see if the url is able to be fetched in within the domain, based on the robots.txt

            # loops through all <a> tag
            # for i in root.xpath('/html')[0].getiterator('p'):
            #     print(i.text)
            # if word_count >= 200:
            # print(word_count, 'word count')
            # print(tag_count, 'tag count')
            # print((word_count+text_tag_count)/(tag_count+word_count))

            if word_count >= 150:
                for i in root.xpath('/html')[0].getiterator('a'):

                    url_dict = i.attrib

                    # gets the href of the <a> tag
                    if 'href' in url_dict:
                        curr_url = url_dict['href']
                        final_url = ''

                        # creates the url to put in the frontier
                        if len(curr_url) >= 2 and curr_url[0] == '/' and curr_url[1] == '/':
                            final_url = 'https:' + curr_url
                        elif len(curr_url) >= 2 and curr_url[0] == '/' and curr_url[1] != '/':
                            final_url = parsed.scheme + '://' + parsed.netloc + curr_url
                        elif len(curr_url) > 0 and curr_url[0] != '/' and curr_url[0] != '#':
                            final_url = curr_url

                        # removes the fragment from the url
                        split_value = final_url.split('#')[0]
                        if split_value != '':
                            final.append(split_value)

    except Exception as e:
        print('ERROR OCCURED')
        with open('Error_file.txt', 'a+') as f:
            f.write(str(type(e)) + ' ' + str(e) + '\n')
    finally:
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
        print("TypeError for ", parsed)
        raise
