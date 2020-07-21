import sqlite3 as sql
import requests as req
from sys import exit
from datetime import datetime
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse

# TODO: detect AI/ML content
#       write to logs not just stdout
#       store in its own repo
#       set up mysql or pgsql remote db, to load automatically

# print list of tuples, one on each line
def print_tuple_list(tl):
    for l in tl:
        print(l)

# class to load sqlite database with HN posts
class GatherNews:
    def __init__(self, url):
        self.site = url
        self.html = req.get(url).text
        # TODO: expand this list. 
        # Should probably keep a set of all unique domains/domain extensions that ever appear on HN front page
        # Also should not be a class variable lol
        self.allowed_suffixes = ['.org', '.net', '.com', '.edu', '.tech', \
                                    '.io', '.co', '.so', '.info', '.fyi', \
                                    '.us', '.hr'
                                ]
        self.db = sql.connect('TechTweets.db')
        self.dbc = self.db.cursor()

    def __cre_tstamp(self):
        return str(datetime.now())[:-10]

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
                return link.get('href'), link.get_text().replace("\"", "'")
        raise ValueError('storylink not found')

    # this feels inelegant
    # construct sqlite insertion string
    def __gen_ins_stmt(self, rank, title, link, top_comments, tstamp):
        # even if we can perfectly scrape comments, lets account for the cases when there are 0 or 1 comments
        # case when more than one comment is found
        if len(top_comments) >= 2:
            return  """insert into HNFP (rank, post_title, post_link, cmnt1, cmnt1_age, cmnt1_author, cmnt2, cmnt2_age, cmnt2_author, tstamp) values ({}, "{}", "{}", "{}", "{}","{}", "{}", "{}", "{}", "{}")""".\
            format(rank, title, link, top_comments[0][0], top_comments[0][1],top_comments[0][2], top_comments[1][0], top_comments[1][1], top_comments[1][2], tstamp)
        # case when a single comment is found
        elif len(top_comments) == 1:
            return  """insert into HNFP (rank, post_title, post_link, cmnt1, cmnt1_age, cmnt1_author, tstamp) values ({}, "{}", "{}", "{}", "{}","{}", "{}")""".\
            format(rank, title, link, top_comments[0][0], top_comments[0][1],top_comments[0][2], tstamp)
        # case when no comments are found
        else:
            return  """insert into HNFP (rank, post_title, post_link, tstamp) values ({}, "{}", "{}", "{}")""".\
            format(rank, title, link, tstamp)
            
    # TODO: get all comments, store in some structure (eg graph)
    def get_comment(self, id, debug=False, only_one=True):
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
            # arbitrary boundary; my test page had tr: 659/td: 1316
            # TODO: record this number for posts of various ages
            if len(trs) > 5:
                if debug: print("comment block found")
                for tr in trs:
                    for x in tr.find_all('span'):
                        if x.get('class') is not None:
                            if x.get('class')[0] == 'commtext':
                                found = True
                                #if debug: print("found comment")
                                comment = x.get_text().replace("\"", "'")
                            elif x.get('class')[0] == 'age':
                                age = x.get_text()
                    for x in tr.find_all('a'):
                        if x.get('class') is not None:
                            if x.get('class')[0] == 'hnuser':
                                user = x.get_text()
                    if found:
                        if comment not in comment_set:
                            comments.append((comment, age, user))
                            comment_set.add(comment)
                            if only_one:
                                return comments
                    else:
                        pass
            else:
                pass
        if len(comments) == 0:
            print('no comments found for ' + url)
        return comments

    def scrape(self, insert=True, debug=False):
        soup = bs(self.html, 'html.parser')
        ind = 1
        valid_ind = 1
        tstamp = self.__cre_tstamp()
        for thing in soup.find_all('tr'):
        #for thing in soup.find_all('td'):
            trs = thing.find_all('tr')
            tds = thing.find_all('td')
            if len(trs) > 75:
                my_rank = 1
                for x in trs:
                    if x.get('class') is not None:
                        if x.get('class')[0] == 'athing':
                            rank = int(x.find('span').get_text().replace('.', ''))
                            if int(my_rank) != rank:
                                # do something
                                if debug: print("rank - my_rank mismatch")
                            link, title = self.__get_storylink(x)
                            top_comments = self.get_comment(x.get('id'))
                            if debug: print("found {} comments".format(len(top_comments)))
                            ind += 1
                            stmt = self.__gen_ins_stmt(rank, title, link, top_comments, tstamp)
                            if insert:
                                try:
                                    self.dbc.execute(stmt)
                                    self.db.commit()
                                except Exception as e:
                                    print("failed to execute: " + stmt)
                                    print(e)
                    
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
        tstamp = self.__cre_tstamp()
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
    #comments = gn.get_comment("23668918", debug=True)
    #gn.scrape(insert=False, debug=True)
    gn.scrape()

# [1] https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not
