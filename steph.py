import subprocess
from lxml import etree, html
from io import *
from simhash import Simhash

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

proc = subprocess.Popen(["curl", "https://wics.ics.uci.edu/events/category/boothing/2020-01/?tribe_events_cat=boothing&tribe-bar-date=2020-01"], stdout=subprocess.PIPE)
(out, err) = proc.communicate()
html_value = out.decode('utf-8')
parser = etree.HTMLParser()
tree = etree.parse(StringIO(html_value), parser)
root = tree.getroot()
#
word = []
for i in root.xpath('/html')[0].getiterator('*'):
    if i.tag not in {"script", "style"}:
        if i.text is not None:
            word.append(i.text)

proc = subprocess.Popen(["curl", "https://wics.ics.uci.edu/events/category/boothing/2019-12/"], stdout=subprocess.PIPE)
(out, err) = proc.communicate()
html_value = out.decode('utf-8')
parser = etree.HTMLParser()
tree = etree.parse(StringIO(html_value), parser)
root = tree.getroot()
#
word2 = []
for i in root.xpath('/html')[0].getiterator('*'):
    if i.tag not in {"script", "style"}:
        if i.text is not None:
            word2.append(i.text)
# print(word)

# print(word)
# print(word)
# print(word)
# word = ['\r\n        \t', '\r\n\r\n\t\t        ', 'WICS is Invited to Western Digital – Women in Information and Computer Sciences', '\r\n\r\n        ', '\r\n                ', 'Skip to content', '\r\n            ', '\r\n                ', '\r\n                    ', '\r\n                        ', '\r\n                            ', '                      \r\n                  \r\n                        ', '\r\n                    ', '\r\n                        ', '\r\n                            ', '\r\n\t\t\t        ', '\r\n\t\t\t', 'Home', 'About', '\n\t', 'What We Do', 'Current Officers', 'Previous Officers', 'Awards and Accomplishments', 'History of WICS', 'Events', '\n\t', 'Events Calendar', 'Blogs', 'Conferences', '\n\t\t', 'CWIC Socal 2018', 'Init (Together)', 'Community Outreach', '\n\t', 'About Community Outreach', 'Bytes of Code', '\n\t\t', 'Bytes of Code 2019', 'Bytes of Code Summer 2018', '#innovate', '\n\t\t', '#innovate 2019', '#innovate Spring 2018', '#GirlsKnowCS 2018 Conference', 'ExploreICS', 'Join Us!', '\n\t', 'Membership Signup', 'Apply to WICS Committee', 'Mentorship Program', 'Contact Us', '\n\t', 'Contact Form', 'Support Us', '\r\n    \t', '\r\n\t\t', '\r\n\t\t\t', 'Blogs', '\r\n\t\t', '\r\n\t\t', '\r\n\t\t', '\r\n\t', '\r\n\t\t\t\t', '\r\n\t\t\t\t\t\t\t', '\r\n\t\t\t\t\t', '\r\n\t\t                ', '\r\n\t\t                    ', '\r\n\t\t\t\t\t\t\t\t', 'Tour', '\r\n\t\t                \t', 'WICS is Invited to Western Digital', '\r\n\t\t                \t', '04/14/2014', '04/14/2014', 'admin', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '\xa0« prev\xa0', ' 1 ', '\xa02 ', '\xa03 ', '\xa04 ', ' next » ', 'On April 4', 'th', 'After breakfast, the first thing on the to-do list was to break apart a hard drive, which was given to the attendees along with free swag to take home! As the hard drive was opened, everyone got to see what the inside looked like as the Western Digital speakers described the individual parts and their usage.', 'Before lunch was served, there was a tour of the Western Digital Shop (items were discounted for attendees), and the company in which we saw the employees in their natural habitat.', 'The tour concluded with a talk held by a panel of 10 women engineers that was provided just for WICS members. They described their work environment, gave school advice, and explained the benefits of working at Western Digital. It was definitely an informational and hands-on learning experience. WICS plans on having more future events with Western Digital so stay tuned!', '\n\t', 'Related', '\n\t\t', 'Post navigation', 'WICS First General Spring Quarter Meeting', 'WICS Attends CWIC SoCal!', '\r\n                            ', '\r\n                    ', '\r\n                        ', '\r\n\t\t\t                                                ', '\r\n\t\t\t\t\t                ', 'Upcoming Events', '\n\t\t\t\t\t', '\n\t\t\t\t\n\t\t\t\t\t\t\t\t', '\n\t\t\t\t\t', 'No Meeting', '\n\t\t\t\t\t', 'February 17 @ 6:30 pm', '8:00 pm', '\n\t\t\t\t\n\t\t\t\t\t\t\t\t', '\n\t\t\t\t\t', 'Negotiation / Imposter Syndrome Panel', '\n\t\t\t\t\t', 'February 24 @ 6:30 pm', '8:00 pm', '\n\t\t', 'View All Events', '\r\n\t\t\t\t\t                ', 'Contact', 'Contact Us', 'Facebook', 'Instagram', 'Twitter', '\r\n\t\t\t\t\t                ', 'Search', '\r\n    ', '\r\n        ', '\r\n            ', '\r\n                ', '\r\n                    ', '\r\n                        ', '\r\n                            ', '\r\n\t                                                                ', '\r\n\t\t\t                            © All right reserved                                    ', 'Portfolio Web by ', 'Acme Themes', '\r\n                            ', '\r\n            ', '\r\n                ', '\r\n                    ', '\r\n                        ', '×', 'Booking Table', '\n\t']
# word2 = ['\r\n        \t', '\r\n\r\n\t\t        ', 'Western Digital Tour & Luncheon with Female Engineers – Women in Information and Computer Sciences', '\r\n\r\n        ', '\r\n                ', 'Skip to content', '\r\n            ', '\r\n                ', '\r\n                    ', '\r\n                        ', '\r\n                            ', '                      \r\n                  \r\n                        ', '\r\n                    ', '\r\n                        ', '\r\n                            ', '\r\n\t\t\t        ', '\r\n\t\t\t', 'Home', 'About', '\n\t', 'What We Do', 'Current Officers', 'Previous Officers', 'Awards and Accomplishments', 'History of WICS', 'Events', '\n\t', 'Events Calendar', 'Blogs', 'Conferences', '\n\t\t', 'CWIC Socal 2018', 'Init (Together)', 'Community Outreach', '\n\t', 'About Community Outreach', 'Bytes of Code', '\n\t\t', 'Bytes of Code 2019', 'Bytes of Code Summer 2018', '#innovate', '\n\t\t', '#innovate 2019', '#innovate Spring 2018', '#GirlsKnowCS 2018 Conference', 'ExploreICS', 'Join Us!', '\n\t', 'Membership Signup', 'Apply to WICS Committee', 'Mentorship Program', 'Contact Us', '\n\t', 'Contact Form', 'Support Us', '\r\n    \t', '\r\n\t\t', '\r\n\t\t\t', 'Blogs', '\r\n\t\t', '\r\n\t\t', '\r\n\t\t', '\r\n\t', '\r\n\t\t\t\t', '\r\n\t\t\t\t\t\t\t', '\r\n\t\t\t\t\t', '\r\n\t\t                ', '\r\n\t\t                    ', '\r\n\t\t\t\t\t\t\t\t', 'Tour', '\r\n\t\t                \t', 'Western Digital Tour & Luncheon with Female Engineers', '\r\n\t\t                \t', '05/05/2013', '09/19/2013', 'admin', ' ', ' ', ' ', ' ', ' ', ' ', '\xa0« prev ', ' 1 ', '\xa02\xa0', '\xa03 ', ' next » ', 'Friday, May 3rd, WICS went to Western Digital for a luncheon with their female engineers and a tour of their work space. 14 female students were able to attend and have the opportunity to interact with and learn from many of Western Digital’s experienced female engineers. After a luncheon with them, the WICS members were taken on a tour to see the engineers at work! The discussions with the female engineers were extremely insightful and including the tour, the whole experience allowed the members to see what it was like to work at Western Digital as a female and have a general idea of what employers looked for in a good candidate. Everyone’s reviews on this tour were extremely positive and WICS plans on going again!', 'Share this:', 'Click to share on Twitter (Opens in new window)', 'Click to share on Facebook (Opens in new window)', 'Click to share on Google+ (Opens in new window)', '\n\t', 'Related', '\n\t\t', 'Post navigation', 'Init (Together) 2013', 'ICS Banquet', '\r\n                            ', '\r\n                    ', '\r\n                        ', '\r\n\t\t\t                                                ', '\r\n\t\t\t\t\t                ', 'Upcoming Events', '\n\t\t\t\t\t', '\n\t\t\t\t\n\t\t\t\t\t\t\t\t', '\n\t\t\t\t\t', 'No Meeting', '\n\t\t\t\t\t', 'February 17 @ 6:30 pm', '8:00 pm', '\n\t\t\t\t\n\t\t\t\t\t\t\t\t', '\n\t\t\t\t\t', 'Negotiation / Imposter Syndrome Panel', '\n\t\t\t\t\t', 'February 24 @ 6:30 pm', '8:00 pm', '\n\t\t', 'View All Events', '\r\n\t\t\t\t\t                ', 'Contact', 'Contact Us', 'Facebook', 'Instagram', 'Twitter', '\r\n\t\t\t\t\t                ', 'Search', '\r\n    ', '\r\n        ', '\r\n            ', '\r\n                ', '\r\n                    ', '\r\n                        ', '\r\n                            ', '\r\n\t                                                                ', '\r\n\t\t\t                            © All right reserved                                    ', 'Portfolio Web by ', 'Acme Themes', '\r\n                            ', '\r\n            ', '\r\n                ', '\r\n                    ', '\r\n                        ', '×', 'Booking Table', '\n\t']
val = ''.join(word)
val2 = ''.join(word2)
print(len(word))
# val = '› '
# print(val.split())
unique_words = []
for word in val.split():
    temp = word.lower()
    char_number = ord(temp[-1]) if len(temp) > 0 else 0
    # print('Main', temp)
    while len(temp) > 0 and not ((97 <= char_number <= 122) or (48 <= char_number <= 57)):
        temp = temp.strip(temp[-1])
        char_number = ord(temp[-1]) if len(temp) > 0 else 0
        # print(temp)
    char_number = ord(temp[0]) if len(temp) > 0 else 0
    while len(temp) > 0 and not ((97 <= char_number <= 122) or (48 <= char_number <= 57)):
        temp = temp.strip(temp[0])
        char_number = ord(temp[0]) if len(temp) > 0 else 0
        # print(temp)
    if temp not in STOP_WORDS and temp != '':
        unique_words.append(temp)



temp_sim = Simhash(val)
temp_sim2 = Simhash(val2)
print(temp_sim2.distance(temp_sim))

# print(unique_words)
# print(len(unique_words))
# print(unique_words)