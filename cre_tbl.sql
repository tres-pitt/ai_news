# shell script to initialize the sqlite database used to record tweets.
# meant to show what I did rather than be used in production

create table tweets(
ID integer primary key autoincrement,
msg char(280) not null,
link text,
tweeted int default 0
);
