import sqlite3 as sql
import requests as req
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
                                    '.io', '.co', '.so', '.info', '.fyi']
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

    # scrape front page of HN
    # store links in a dict of ints (inds) : tuples
    # then store them in sqlite
    # AskHN links arent included
    def scrape(self, debug=False):
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
            #if link.get('href')[-4:] != '.com':
            if not self.__valid_domain(link.get('href')):
                if debug: print('skipping ' + link.get('href'))
                pass
            else:
                if debug: print('found ' + link.get('href'))
                #data[ind] = (link.get_text(), link.get('href'))
                data.append((ind, link.get_text(), link.get('href'), tstamp))
                stmt = """insert into HNFP (rank, post_title, post_link, tstamp) values ({}, "{}", "{}", "{}")""".format(ind, link.get_text(), link.get('href'), tstamp)
                breakpoint()
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
    gn.scrape(debug=True)

# [1] https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not
