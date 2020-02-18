import re
from urllib.parse import urlparse
from lxml import etree, html
from simhash import Simhash
from io import *
from collections import defaultdict
from string import punctuation

# CITATION FOR LMXL
# Copyright (c) 2004 Infrae. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 1.   Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
# 2.   Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in
#      the documentation and/or other materials provided with the
#      distribution.
#
# 3.   Neither the name of Infrae nor the names of its contributors may
#      be used to endorse or promote products derived from this software
#      without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL INFRAE OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# CITATION FOR SIMHASH
# The MIT License (MIT)
#
# Copyright (c) 2013 1e0n
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# largest page in crawl, in a list form
BIG_PAGE = [0, 0]

IMPORTANT_URLS = [0]

# dictionary of tokens
TOKENS = defaultdict(int)

# dictionary of all ics urls
ICS_DICT = defaultdict(int)

# set of punctuations that we will ignore for tokenizing
PUNC_SET = set(punctuation)
print(PUNC_SET)

# english stop words
# stop word list can be found here https://www.ranks.nl/stopwords
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

    # This method uses the lmxl library from Infrae. The original code can be found at https://github.com/lxml/lxml/
    # This method uses the simhash library from 1e0n. The original code can be found at https://github.com/leonsim/simhash

    final = []

    try:
        # separate the url into important parts for parsing
        parsed = urlparse(url)
        resp_type = ''

        # finds the content type of the url
        if resp.raw_response is not None and resp.raw_response.headers['Content-Type'] is not None:
            resp_type = resp.raw_response.headers['Content-Type'].split(';')[0]
            # with open('response_types.txt', 'a+') as f:
            #     f.write(resp_type + ' ' + url + '\n')

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
            unique_words = []

            # loops through the HTML to obtain all the words, and puts it in a list
            for i in root.xpath('/html')[0].getiterator('*'):
                if i.tag not in {"script", "style"}:
                    if i.text is not None:
                        word.append(i.text)

            # keeps a variable of a string of all the words to create a Simhash value
            val = ' '.join(word)
            temp_sim = Simhash(val)

            # checks if there are any duplicates or near duplicates in the Simhash set
            for i in SIMHASH_URLS:
                if i.distance(temp_sim) <= 3:
                    dup = True
                    print('SIM', SIMHASH_URLS[i])
                    break

            # if the file is not a duplicate then check the word count of the file, excluding stop words,
            # and add the tokens to a list to add to a global dictionary later.
            if not dup:
                for word in val.split():
                    temp = word.lower()
                    char_number = ord(temp[-1]) if len(temp) > 0 else 0
                    while len(temp) > 0 and not ((97 <= char_number <= 122) or (48 <= char_number <= 57)):
                        temp = temp.strip(temp[-1])
                        char_number = ord(temp[-1]) if len(temp) > 0 else 0
                    char_number = ord(temp[0]) if len(temp) > 0 else 0
                    while len(temp) > 0 and not ((97 <= char_number <= 122) or (48 <= char_number <= 57)):
                        temp = temp.strip(temp[0])
                        char_number = ord(temp[0]) if len(temp) > 0 else 0
                    if temp not in STOP_WORDS and temp != '':
                        word_count += 1
                        unique_words.append(temp)
            print('WORD', word_count)
            # checks to see if the url is able to be fetched in within the domain, based on the robots.txt
            if word_count > 150 and not dup:
                IMPORTANT_URLS[0] += 1
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
        # with open('Error_file.txt', 'a+') as f:
        #     f.write(str(type(e)) + ' ' + str(e) + ' ' + str(url) + '\n')
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
