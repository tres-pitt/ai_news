import requests as req
from bs4 import BeautifulSoup as bs

# class to load sqlite database with tweets
class GatherNews:
    def __init__(self, url):
        self.site = url
        self.html = req.get(url).text
        self.allowed_suffixes = ['.org', '.net', '.com', '.edu'

    def scrape(self):
        soup = bs(self.html, 'html.parser')
        breakpoint()
        for link in soup.find_all('a'):
            if link.get('href')[-4:] != '.com':
                print('skipping ' + link.get('href'))
            else:
                print('found ' + link.get('href'))
            #breakpoint()
        breakpoint()

if __name__ == '__main__':
    gn = GatherNews('http://news.ycombinator.com')
    gn.scrape()

