from newscatcher import describe_url
from newscatcher import Newscatcher
from newscatcher import urls
url = 'news.ycombinator.com'
url2 = 'ycombinator.com'
eng_lnx = urls(language='en')
nc = Newscatcher(website=url)
try:
    print("looking for " + url + "...")
    nc.get_news()
except Exception as e:
    print(repr(e))
describe_url(url)
print(url + ' in urls: ' + str(url in eng_lnx))
print(url2 + ' in urls: ' + str(url2 in eng_lnx))
nc2 = Newscatcher(website='ycombinator.com')
try:
    print("looking for " + url2 + "...")
    nc2.get_news()
except Exception as e:
    print(repr(e))
