import sqlite3 as sql
import requests as req
from sys import exit
from datetime import datetime
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse

# TODO: detect AI/ML content (possible rabbit hole)
#       write to logs not just stdout
#       store in its own repo
#       set up mysql or pgsql remote db, to load automatically
#       load top comment into string or blob field
#           condition ^ on x hours elapsed

# print list of tuples, one on each line
def print_tuple_list(tl):
    for l in tl:
        print(l)

# class to load sqlite database with tweets
# HN-only for now
class GatherNews:
    def __init__(self, url):
        self.site = url
        self.html = req.get(url).text
        # TODO: expand this list. 
        # Should probably keep a set of all unique domains/domain extensions that ever appear on HN front page
        # Also should not be a class variable lol
        self.allowed_suffixes = ['.org', '.net', '.com', '.edu', '.tech', \
                                    '.io', '.co', '.so', '.info', '.fyi', \
                                    '.us'
                                ]
        self.db = sql.connect('TechTweets.db')
        self.dbc = self.db.cursor()

    # would HN ever give an all cap or mixed case domain?
    # TODO: use an actual library to do this!
    def __valid_domain(self, url):
        # special cases
        if 'from?' in url or 'ycombinator.com' in url or \
            url == 'https://github.com/HackerNews/API':
            return False
        # this is accepted answer on SO, but fails to find all 30 links
        #try:
        #    result = urlparse(url)
        #    return all([result.scheme, result.netloc, result.path])
        #except:
        #    return False
        for suffix in self.allowed_suffixes:
            if suffix in url:
                return True
        return False

    def __contains_valid_link(self, thing, debug):
        for link in thing.find_all('a'):
            if self.__valid_domain(link.get('href')):
                if debug: print("VALID: " + link.get('href'))
                return True
            else:
                if debug: print('invalid: ' + link.get('href'))
        return False

    def __get_storylink(self, html):
        for link in html.find_all('a'):
            if link.get('class') is None:
                continue
            if link.get('class')[0] == 'storylink':
                return link.get('href'), link.get_text()
        raise ValueError('storylink not found')

    # TODO: get all comments, store in some structure (eg graph)
    def get_comment(self, id, debug=False):
        breakpoint()
        url = "https://news.ycombinator.com/item?id=" + id
        html = req.get(url).text
        soup = bs(html, 'html.parser')
        comment = None
        age = None
        user = None
        found = False
        comments = []
        comment_set = set()
        for thing in soup.find_all('tr'):
            trs = thing.find_all('tr')
            tds = thing.find_all('td')
            found = False
            if debug:
                print('')
                print('len tr: ' + str(len(trs)))
                print('len td: ' + str(len(tds)))
                print(thing)
                print('')
            # arbitrary boundary; my test page had tr: 659/td: 1316
            # TODO: record this number for posts of various ages
            if len(trs) > 200:
                if debug: print("comment block found")
                for tr in trs:
                    for x in tr.find_all('span'):
                        if x.get('class') is not None:
                            if x.get('class')[0] == 'commtext':
                                found = True
                                if debug: print("found comment")
                                comment = x.get_text()
                            elif x.get('class')[0] == 'age':
                                age = x.get_text()
                    for x in tr.find_all('a'):
                        if x.get('class') is not None:
                            if x.get('class')[0] == 'hnuser':
                                user = x.get_text()
                    if found and comment not in comment_set:
                        comments.append((comment, age, user))
                        comment_set.add(comment)
                    else:
                        if debug: print("no comment found")
        return comments

    def scrape2(self, debug=False):
        soup = bs(self.html, 'html.parser')
        ind = 0
        valid_ind = 1
        for thing in soup.find_all('tr'):
        #for thing in soup.find_all('td'):
            trs = thing.find_all('tr')
            tds = thing.find_all('td')
            #if debug:
            #    print('')
            #    print('LEN: ' + str(len(thing)))
            #    print('LEN, TR: ' + str(len(trs)))
            #    print('LEN, TD: ' + str(len(tds)))
            #    print(thing)
            #    print('')
            if len(trs) > 75:
                my_rank = 1
                for x in trs:
                    if x.get('class')[0] == 'athing':
                        if debug:
                            print('')
                            print(x)
                            print('')
                        rank = x.find('span').get_text().replace('.', '')
                        link, title = self.__get_storylink(x)
                        top_comments = self.get_comment(x.get('id'))
                        breakpoint()
                    

        #    valid_link = False
        #    #print(ind)
        #    ind += 1
        #    if not self.__contains_valid_link(thing, debug):
        #        continue
        #    print("post found (" + str(valid_ind) + ")")
        #    valid_ind += 1

    # scrape front page of HN
    # store links in a dict of ints (inds) : tuples
    # then store them in sqlite
    # AskHN links arent included
    def scrape_links(self, debug=False, insert=True):
        soup = bs(self.html, 'html.parser')
        # lets see if we can match the number of links on HN
        #   if you get <30, you probably need to add new domain to allowed_suffixes class var
        # HN front page is 1-indexed 
        ind = 1
        #data = {}
        data = []
        tstamp = str(datetime.now())[:-10]
        # currently, I cant executemany (bulk insert a posteriori) with autoincrement sakey column
        #   I'll still populate data for now
        print("..........beginning 'a' traversal..........")
        for link in soup.find_all('a'):
            # dont all a's have href's?
            try:
                hr = link.get('href')
            except:
                print('couldnt get href')
                #exit()
                continue
            if not self.__valid_domain(hr):
                if debug: print('skipping ' + hr)
                pass
            else:
                if debug: print('found ' + hr)
                #data[ind] = (link.get_text(), link.get('href'))
                data.append((ind, link.get_text(), hr, tstamp))
                if insert:
                    stmt = """insert into HNFP (rank, post_title, post_link, tstamp) values ({}, "{}", "{}", "{}")""".format(ind, link.get_text(), hr, tstamp)
                    try:
                        self.dbc.execute(stmt)
                    except Exception as e:
                        print("failed to execute: " + stmt)
                ind += 1
        print("..........completed 'a' traversal..........")
        if debug: print("found " + str(ind) + " links")
        self.db.commit()
        #if len(data) > 28 and len(data) <= 30:
        #    if debug: print("inserting...")
        #    stmt = "insert into HNFP values (?,?,?,?)"
        #    self.dbc.executemany(stmt, data)
        #else:
        #    if debug:
        #        print("found " + str(len(data)) + " links. Aborting insert.")

if __name__ == '__main__':
    gn = GatherNews('http://news.ycombinator.com')
    #gn.scrape(debug=True, insert=False)
    #comments = gn.get_comment("23654188", debug=True)
    gn.scrape2()

# [1] https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not
