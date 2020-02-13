import re
from urllib.parse import urlparse
from lxml import etree, html
from simhash import Simhash
from io import *
from collections import defaultdict
from string import punctuation

# largest page in crawl, in a list form
BIG_PAGE = [0, 0]

# dictionary of tokens
TOKENS = defaultdict(int)

# dictionary of all ics urls
ICS_DICT = defaultdict(int)

# set of punctuations that we will ignore for tokenizing
PUNC_SET = set(punctuation)
print(PUNC_SET)

# english stop words
STOP_WORDS = {'which', 'my', 'all', "when's", 'the', "you'd", 'from', 'be', 'down', 'until', 'by', 'only', "we're",
              "couldn't", 'your', 'her', 'should', 'but', 'at', 'having', 'ours', 'doing', "who's", 'during', "i've",
              'those', 'as', 'myself', 'than', 'himself', "i'm", 'very', 'this', "we'd", 'them', 'ourselves', "doesn't",
              'is', "we'll", "what's", 'had', 'there', "there's", 'a', 'yours', "he's", 'with', "you'll", 'these', 'does',
              'into', 'not', "that's", "hadn't", "hasn't", "it's", 'she', "why's", 'me', 'against', 'yourselves', 'it',
              "you're", "he'll", "here's", 'further', 'in', 'own', "i'll", "shouldn't", "they've", "aren't", 'do', 'itself',
              "wasn't", 'then', "shan't", 'again', 'i', 'were', 'why', 'through', 'more', 'when', "where's", 'once', 'being',
              'who', "she'll", 'under', 'no', "can't", 'other', "they'll", 'they', 'below', "won't", 'each', 'themselves',
              'would', 'on', 'both', 'while', 'hers', 'herself', 'cannot', "she's", 'nor', 'over', 'where', 'you', "you've",
              "how's", 'up', 'how', 'ought', "they'd", 'am', 'what', 'whom', 'above', "i'd", "let's", 'their', 'him', 'after',
              'was', 'before', 'for', 'did', 'few', "we've", "she'd", 'to', 'because', 'an', 'and', 'he', 'same', 'theirs',
              'yourself', 'too', "don't", 'could', "wouldn't", "mustn't", 'so', 'such', 'its', 'here', 'are', 'off', 'out',
              "didn't", 'have', 'his', 'or', "isn't", 'that', 'of', 'our', 'we', 'has', 'if', 'between', 'most', 'some',
              "they're", "weren't", 'about', 'any', "haven't", "he'd", 'been'}

# set of all simhash values
SIMHASH_URLS = {}

# blacklisting calendar types
BLACKLIST_RESP_TYPES = {'text/calendar'}


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


# returns all tokens
def get_all_tokens():
    return TOKENS


# adds token to global dictionary
def add_tokens(words):

    for w in words:
        if w is not '':
            TOKENS[w] += 1


def extract_next_links(url, resp):

    final = []

    try:
        # separate the url into important parts for parsing
        parsed = urlparse(url)
        resp_type = ''

        # finds the content type of the url
        if resp.raw_response is not None and resp.raw_response.headers['Content-Type'] is not None:
            resp_type = resp.raw_response.headers['Content-Type'].split(';')[0]
            with open('response_types.txt', 'a+') as f:
                f.write(resp_type + ' ' + url + '\n')

        print(resp.status)
        print(resp_type)
        # checks the resp.status and only goes through the if statement if the content type is an html
        if 200 <= resp.status <= 599 and resp_type == 'text/html' and resp.raw_response is not None:

            # gets the html root, library calls to parse through html
            html_value = resp.raw_response.content.decode('utf-8')
            parser = etree.HTMLParser()
            tree = etree.parse(StringIO(html_value), parser)
            root = tree.getroot()

            # creates a robots url for the parser
            # variables initialized for word and tag count, determining if pages are relevant or not
            dup = False
            word_count = 0
            word = []

            # loops through the HTML to obtain all the words, and puts it in a list
            for i in root.xpath('/html')[0].getiterator('*'):
                if i.tag not in {"script", "style"}:
                    if i.text is not None:
                        word.append(i.text)

            # keeps a variable of a string of all the words to create a Simhash value
            val = ''.join(word)
            temp_sim = Simhash(val)

            # checks if there are any duplicates or near duplicates in the Simhash set
            for i in SIMHASH_URLS:
                if i.distance(temp_sim) <= 4:
                    dup = True
                    print('SIM', SIMHASH_URLS[i])
                    break

            # if the file is not a duplicate then check the word count of the file, excluding stop words,
            # and add the tokens to a list to add to a global dictionary later.
            if not dup:
                unique_words = []
                for word in val.split():
                    temp = word.lower()
                    while len(temp) > 0 and temp[-1] in PUNC_SET:
                        temp = temp.strip(temp[-1])
                    if temp not in STOP_WORDS:
                        word_count += 1
                        unique_words.append(temp)
            print('WORD', word_count)
            # checks to see if the url is able to be fetched in within the domain, based on the robots.txt
            if word_count > 150 and not dup:

                # function that adds tokens into dict
                add_tokens(unique_words)

                # checks and changes the highest text volume page
                if len(unique_words) > BIG_PAGE[1]:
                    BIG_PAGE[0], BIG_PAGE[1] = [url, len(unique_words)]

                # adds count to ics dict
                if '.ics.uci.edu' in parsed.netloc:
                    ICS_DICT[parsed.netloc] += 1

                # SIMHASH_URLS.add(temp_sim)
                SIMHASH_URLS[temp_sim] = url

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
            f.write(str(type(e)) + ' ' + str(e) + ' ' + str(url) + '\n')
    finally:
        return final


def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        match_links = not re.match(r".*(share=|replytocom=).*", url)
        match_domains = re.match(
            r".*\.(ics|cs|informatics|stat)\.uci\.edu\/.*|today\.uci\.edu\/department\/information_computer_sciences\/.*$",
            url
        )
        # print(re.match(r".*(share=|replytocom=).*", 'https://evoke.ics.uci.edu/hollowing-i-in-the-authorship-of-letters-a-note-on-flusser-and-surveillance/?replytocom=38622'))
        # print(url, parsed.path)
        # print('MATCH_LINKS', match_links, url)
        # print('MATCH_DOMAINS', match_domains, url)
        return match_links and match_domains and not re.match(
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
