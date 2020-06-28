Twitter bot to post news about AI, ML, and computing in general.
Also includes a HN scraper - a bit of a toy project since you can probably use their API directly.
Future work could include 
    - a way to submit posts, though I haven't even done this manually before.
    - create graph or set of links found on comment pages

TODO
1) store constants securely, separately
2) save json output from tweepy
3) better error handling
4) dockerize
5) use mysql or postgresql; insert rows remotely
6) write scrapers for r/artifical and other sources
7) some safety mechanism to prevent repeat tweets (?)
8) convert HN "time stamps" to real time values; maybe compute time of original post/comment
