import requests as req
from bs4 import BeautifulSoup as bs

# class to load sqlite database with tweets
class GatherNews:
    def __init__(self, url):
        self.site = url
        self.html = req.get(url).text
        # TODO: expand this list. 
        # Should probably keep a set of all unique domains/domain extensions that ever appear on HN front page
        # Also should not be a class variable lol
        self.allowed_suffixes = ['.org', '.net', '.com', '.edu', '.tech', '.io']

    # would HN ever give an all cap or mixed case domain?
    # TODO: use an actual library to do this!
    def __valid_domain(self, url):
        # special cases
        if 'from?' in url or 'ycombinator.com' in url:
            return False
        for suffix in self.allowed_suffixes:
            if suffix in url:
                return True
        return False

    def scrape(self, debug=False):
        soup = bs(self.html, 'html.parser')
        breakpoint()
        for link in soup.find_all('a'):
            #if link.get('href')[-4:] != '.com':
            if not self.__valid_domain(link.get('href')):
                if debug:
                    print('skipping ' + link.get('href'))
                pass
            else:
                print('found ' + link.get('href'))
            #breakpoint()
        breakpoint()

if __name__ == '__main__':
    gn = GatherNews('http://news.ycombinator.com')
    gn.scrape()

